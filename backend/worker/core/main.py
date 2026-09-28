# app/main.py
import asyncio
import hashlib
import os
import re
import sys
import tempfile
import time
import traceback
from typing import Any, Dict, List, Optional
import aiohttp
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import PlainTextResponse
import json

# Add project root to path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.worker.core.config import (
    WORKER_SECRET, OPENROUTER_API_KEY, DEEPSEEK_API_KEY, INDEXER_MODEL, CHEAP_MODEL,
    DEEPWIKI_DOCS_DIR, SCAN_TTL, logger,
    ENABLE_CONTEXT_COMPACTION, COMPACTION_MIN_CHARS,
    PHASE1_CONFIDENCE_THRESHOLD, PHASE2_CONFIDENCE_THRESHOLD,
    FREE_TIER_PHASE2_MAX_FINDINGS, ENABLE_TIER23_SAFE_ESCALATION,
    TIER23_SAFE_ESCALATION_KEYWORD_COUNT,
    SKEPTIC_PASS_ENABLED, SKEPTIC_CVSS_THRESHOLD, SKEPTIC_MAX_PARALLEL,
    AGENTIC_CONFIDENCE_CEILING,
    AGENTIC_TIER3_MAX_TOOL_CALLS_PER_FINDING,
    AGENTIC_TIER3_MAX_TOOL_CALLS_PER_SCAN,
    AGENTIC_TIER4_MAX_TOOL_CALLS_PER_FINDING,
    AGENTIC_TIER4_MAX_TOOL_CALLS_PER_SCAN,
    TIER4_AGENTIC_CONFIDENCE_FLOOR,
    PROJECT_CACHE_TTL,
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
    AGENT_MODEL,
    AGENT_SCAN_ENABLED,
    AGENT_MAX_FILE_TOKENS,
    AGENT_CHAIN_COMBINER_ENABLED,
    AGENT_ATTACK_PATH_SIMULATOR_ENABLED,
    AGENT_REMEDIATION_ENABLED,
    AGENT_LLM_SECURITY_ENABLED,
    DEPENDENCY_SCANNER_ENABLED,
)
from backend.worker.core.redis_client import redis_client, REDIS_AVAILABLE
from backend.worker.core.models import (
    ScanRequest, FileData, IndexRequest, DeepWikiIndexRequest,
    AnalyzeRequest, PocRequest, CrossFileConsistencyRequest
)
from backend.worker.core.project_indexer import ProjectIndexer
from backend.worker.core.deepwiki_utils import build_security_context
from backend.worker.core.utils import (
    check_keywords, find_keywords_with_lines,
    get_code_context_and_fingerprint, find_line_number
)
from backend.worker.core.ai_tier1 import scan_tier_1_basic
from backend.worker.core.ai_tier2 import scan_tier_2_standard
from backend.worker.core.ai_tier3 import scan_tier_3_advanced
from backend.worker.core.poc import generate_poc_for_finding
from backend.worker.core.keywords import ALL_KEYWORDS
from backend.worker.core.findings_validator import apply_two_phase_validation
from backend.worker.core.findings_validator import AgenticValidationConfig
from backend.worker.core.llm_centric_detector import llm_centric_scan
from backend.worker.core.context_compactor import compact_security_context
from backend.worker.core.native_index import (
    build_deepwiki_project_ir,
    index_project_on_disk,
    persist_extended_index,
)
from backend.worker.core.deepseek_client import bridge_healthy, llm_configured
from backend.worker.core.deepseek_scan import deepseek_single_file_scan, maybe_summarize_project

# Enrichment modules for pre-scan context extraction
from backend.worker.core.enrichment import (
    FileRiskRanker,
    DataflowHintExtractor,
    ContextSlicer,
)

# Validation modules for post-scan quality assurance
from backend.worker.core.validation import (
    SkepticPass,
    CrossFileConsistencyChecker,
    MultiSignalConfidenceScorer,
)
from backend.worker.core.agents.agent_logger import AgentLogger, set_logger, clear_logger, get_logger


async def run_agent_scan(
    call_graph: Dict[str, Any],
    dependency_map: Dict[str, Any],
    sanitizer_registry: Dict[str, Any],
    dead_code_map: Dict[str, Any],
    file_contents: Dict[str, str],
    file_asts: Dict[str, Any],
    scan_id: str,
    repo_path: str,
    language: str,
    framework: str,
    scan_mode: str = "full",
    changed_files: Optional[List[str]] = None,
    display_file_count: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Runs the multi-agent scan pipeline.
    Called after existing v3 project indexing completes.
    Returns list of finding dicts (compatible with existing pipeline).
    """
    if not AGENT_SCAN_ENABLED:
        return []

    # Determine which LLM to use for agents
    # OpenRouter (Minimax) only. Claude/Anthropic support intentionally removed.
    llm_client = None
    agent_model = "minimax"

    if DEEPSEEK_API_KEY or OPENROUTER_API_KEY:
        from backend.worker.core.llm_client import MinimaxClient

        llm_client = MinimaxClient(
            api_key=DEEPSEEK_API_KEY or OPENROUTER_API_KEY,
            model=AGENT_MODEL,
        )
        agent_model = AGENT_MODEL
        logger.info(f"[{scan_id}] Using agent model ({AGENT_MODEL}) via OpenCode bridge")
    else:
        logger.warning(f"[{scan_id}] No LLM available for agents - DEEPSEEK_API_KEY missing")
        return []

    try:
        from backend.worker.core.agents.coordinator import AgentCoordinator
        from backend.worker.core.agents.models import AgentContext, ScanMode
        from backend.worker.core.agents.recon_agent import ReconAgent
        from backend.worker.core.agents.pattern_agent import PatternAgent
        from backend.worker.core.agents.threat_model_agent import ThreatModelAgent
        from backend.worker.core.agents.specialists.injection_specialist import InjectionSpecialist
        from backend.worker.core.agents.specialists.auth_specialist import AuthSpecialist
        from backend.worker.core.agents.specialists.crypto_specialist import CryptoSpecialist
        from backend.worker.core.agents.specialists.cipher_design_specialist import CipherDesignSpecialist
        from backend.worker.core.agents.specialists.logic_analyst import LogicAnalyst
        from backend.worker.core.agents.specialists.config_hunter import ConfigHunter

        # Set logger so agent events are pushed to log server (LOG_SERVER_URL)
        file_count = len(file_contents) if isinstance(file_contents, dict) else 0
        if display_file_count is not None and file_count == 0:
            file_count = display_file_count  # so admin UI shows correct "Scan start · N files"
        agent_logger = AgentLogger(scan_id, file_count=file_count, language=language or "", framework=framework or "")
        set_logger(agent_logger)
        agent_finalized = False
        try:
            mode = ScanMode.DIFF if scan_mode == "diff" else ScanMode.FULL
            context = AgentContext(
                call_graph=_call_graph_to_list(call_graph),
                dependency_map=_dep_map_to_list(dependency_map),
                sanitizer_registry=sanitizer_registry if isinstance(sanitizer_registry, dict) else {},
                dead_code_map=dead_code_map if isinstance(dead_code_map, dict) else {},
                entry_points=[],
                architecture_patterns=None,
                threat_model=None,
                file_contents=file_contents,
                file_asts=file_asts,
                scan_id=scan_id,
                repo_path=repo_path,
                language=language,
                framework=framework,
                scan_mode=mode,
                changed_files=changed_files or [],
            )
            recon_agent = ReconAgent(name="ReconAgent", llm_client=llm_client)
            pattern_agent = PatternAgent(name="PatternAgent", llm_client=llm_client)
            threat_model_agent = ThreatModelAgent(name="ThreatModelAgent", llm_client=llm_client)
            specialists = [
                InjectionSpecialist(llm_client=llm_client),
                AuthSpecialist(llm_client=llm_client),
                CryptoSpecialist(llm_client=llm_client),
                CipherDesignSpecialist(llm_client=llm_client),
                LogicAnalyst(llm_client=llm_client),
                ConfigHunter(llm_client=llm_client),
            ]
            if AGENT_LLM_SECURITY_ENABLED:
                from backend.worker.core.agents.specialists.llm_security_agent import LLMSecurityAgent
                specialists.append(LLMSecurityAgent(llm_client=llm_client))
            coordinator = AgentCoordinator(
                recon_agent=recon_agent,
                pattern_agent=pattern_agent,
                threat_model_agent=threat_model_agent,
                specialist_agents=specialists,
            )
            result, context = await coordinator.run_scan(context)
            # Phase 2/3: Deduplication -> Consensus -> Skeptic for high-accuracy output
            from backend.worker.core.agents.deduplication_engine import DeduplicationEngine
            from backend.worker.core.agents.consensus_scorer import ConsensusScorer
            from backend.worker.core.agents.skeptic_agent import SkepticAgent

            dedup_engine = DeduplicationEngine()
            dedup_list = dedup_engine.run(result.findings)
            agent_log = get_logger()
            if agent_log:
                agent_log.log_deduplication(
                    len(result.findings), len(dedup_list),
                    len(result.findings) - len(dedup_list), [],
                )
            consensus_scorer = ConsensusScorer()
            scored_list = consensus_scorer.score_all(dedup_list, context)
            if agent_log:
                agent_log.log_consensus_scoring(len(dedup_list), [])
            skeptic_agent = SkepticAgent(llm_client=llm_client)
            skeptic_list = skeptic_agent.run(scored_list, context)
            if agent_log and len(scored_list) > 0:
                rejection_rate = (len(scored_list) - len(skeptic_list)) / len(scored_list) * 100.0
                agent_log.log_skeptic_review(len(scored_list), [], float(rejection_rate))

            # Tag findings that survived SkepticAgent so they are not re-reviewed by SkepticPass
            for _sf in skeptic_list:
                if hasattr(_sf, '__dict__'):
                    _sf._skeptic_reviewed = True
                    _sf._skeptic_reviewed_at = "agent_pipeline"
                    _sf._skeptic_confidence = getattr(_sf, 'confidence', 0.5) * 10

            # Optional: Chain combiner -> attack path simulator -> remediation (configurable)
            final_findings: list = list(skeptic_list)
            chains_serialized: list = []
            attack_paths_serialized: list = []
            remediations_serialized: list = []

            if AGENT_CHAIN_COMBINER_ENABLED and skeptic_list:
                try:
                    from backend.worker.core.agents.chain_combiner import ChainCombiner
                    chain_combiner = ChainCombiner(llm_client=llm_client)
                    chains, unchained = chain_combiner.run(skeptic_list, context)
                    # Final findings = unchained + all findings that appear in chains (dedupe by finding_id)
                    seen_ids: set = set()
                    final_findings = []
                    for d in unchained:
                        if d.finding_id not in seen_ids:
                            seen_ids.add(d.finding_id)
                            final_findings.append(d)
                    for c in chains:
                        for f in c.findings:
                            if f.finding_id not in seen_ids:
                                seen_ids.add(f.finding_id)
                                final_findings.append(f)
                    chains_serialized = [_vulnerability_chain_to_dict(c) for c in chains]
                    logger.info(f"[{scan_id}] Agent chains: {len(chains)} chains, {len(unchained)} unchained")
                    if agent_log:
                        agent_log.log_chain_combiner(len(chains), len(unchained), chains_serialized)

                    if AGENT_ATTACK_PATH_SIMULATOR_ENABLED and chains:
                        from backend.worker.core.agents.attack_path_simulator import AttackPathSimulator
                        path_sim = AttackPathSimulator()
                        paths = path_sim.run(chains, context)
                        attack_paths_serialized = [_attack_path_to_dict(p) for p in paths]
                        logger.info(f"[{scan_id}] Agent attack paths: {len(paths)} paths")
                        if agent_log:
                            agent_log.log_attack_paths(len(paths), attack_paths_serialized)
                except Exception as chain_err:
                    logger.warning(f"[{scan_id}] Chain combiner / attack path failed: {chain_err}")

            if AGENT_REMEDIATION_ENABLED and skeptic_list:
                try:
                    from backend.worker.core.agents.remediation_agent import RemediationAgent
                    rem_agent = RemediationAgent(llm_client=llm_client)
                    remediations = rem_agent.run(skeptic_list, context)
                    remediations_serialized = [_remediation_to_dict(r) for r in remediations]
                    logger.info(f"[{scan_id}] Agent remediations: {len(remediations)}")
                    if agent_log:
                        agent_log.log_remediation(len(remediations), remediations_serialized)
                except Exception as rem_err:
                    logger.warning(f"[{scan_id}] Remediation agent failed: {rem_err}")

            # Store optional outputs in Redis for UI / downstream
            if REDIS_AVAILABLE and (chains_serialized or attack_paths_serialized or remediations_serialized):
                try:
                    if chains_serialized:
                        redis_client.setex(f"{scan_id}:agent_chains", SCAN_TTL, json.dumps(chains_serialized))
                    if attack_paths_serialized:
                        redis_client.setex(f"{scan_id}:agent_attack_paths", SCAN_TTL, json.dumps(attack_paths_serialized))
                    if remediations_serialized:
                        redis_client.setex(f"{scan_id}:agent_remediations", SCAN_TTL, json.dumps(remediations_serialized))
                except Exception as redis_err:
                    logger.debug(f"[{scan_id}] Redis store chains/paths/remediations: {redis_err}")

            # Finalize agent log so admin UI gets scan_complete (coordinator no longer "stuck at running")
            agent_finalized = False
            try:
                al = get_logger()
                if al:
                    al.finalize({"total_findings": len(final_findings)})
                    agent_finalized = True
            except Exception:
                pass
            return [_agent_finding_to_dict(d.to_agent_finding()) for d in final_findings]
        except Exception as e:
            logger.warning(f"[{scan_id}] Agent scan failed: {e}")
            return []
        finally:
            # If we never finalized (e.g. exception), send scan_complete so admin UI does not stay "Running"
            if not agent_finalized:
                try:
                    al = get_logger()
                    if al:
                        al.finalize({"total_findings": 0})
                except Exception:
                    pass
            clear_logger()
    except Exception as e:
        logger.warning(f"[{scan_id}] Agent scan failed: {e}")
        return []


def _call_graph_to_list(cg: Dict[str, Any]) -> Dict[str, list]:
    out = {}
    for k, v in cg.items():
        if isinstance(v, list):
            out[k] = v
        elif isinstance(v, dict) and "callees" in v:
            out[k] = v["callees"]
        else:
            out[k] = []
    return out


def _dep_map_to_list(dm: Dict[str, Any]) -> Dict[str, list]:
    if not dm:
        return {}
    out = {}
    for k, v in dm.items():
        out[k] = v if isinstance(v, list) else list(v) if hasattr(v, "__iter__") and not isinstance(v, (str, dict)) else []
    return out


def _agent_finding_to_dict(finding: Any) -> Dict[str, Any]:
    d = finding.to_dict() if hasattr(finding, "to_dict") else {}
    result = {
        "type": d.get("vulnerability_class", "Vulnerability"),
        "severity": (d.get("severity") or "MEDIUM").upper(),
        "confidence_score": int((d.get("confidence") or 0.5) * 10),
        "cwe_id": d.get("cwe_id", ""),
        "function_name": d.get("function_name", ""),
        "line": d.get("line_start", 0),
        "description": d.get("reasoning", ""),
        "reason": d.get("reasoning", ""),
        "vulnerable_code": d.get("vulnerable_code", ""),
        "agent_source": d.get("agent_source", ""),
    }
    # Propagate skeptic review metadata from agent pipeline
    if getattr(finding, '_skeptic_reviewed', False):
        result["_skeptic_reviewed"] = True
        result["_skeptic_reviewed_at"] = getattr(finding, '_skeptic_reviewed_at', 'agent_pipeline')
        result["_skeptic_confidence"] = getattr(finding, '_skeptic_confidence', result["confidence_score"])
    return result


def _entry_point_to_dict(ep: Any) -> Dict[str, Any]:
    if ep is None:
        return {}
    return {
        "entry_type": getattr(ep, "entry_type", ""),
        "file_path": getattr(ep, "file_path", ""),
        "line_number": getattr(ep, "line_number", 0),
        "function_name": getattr(ep, "function_name", ""),
        "handler_function": getattr(ep, "handler_function", ""),
        "authentication_required": getattr(ep, "authentication_required", False),
        "authorization_required": getattr(ep, "authorization_required", False),
        "rate_limited": getattr(ep, "rate_limited", False),
        "framework": getattr(ep, "framework", ""),
    }


def _vulnerability_chain_to_dict(c: Any) -> Dict[str, Any]:
    """Serialize VulnerabilityChain for Redis/API."""
    findings = getattr(c, "findings", [])
    finding_dicts = [_agent_finding_to_dict(f.to_agent_finding()) for f in findings]
    return {
        "chain_id": getattr(c, "chain_id", ""),
        "chain_name": getattr(c, "chain_name", ""),
        "findings": finding_dicts,
        "entry_point": _entry_point_to_dict(getattr(c, "entry_point", None)),
        "impact": getattr(c, "impact", ""),
        "exploitability": getattr(c, "exploitability", ""),
        "attack_narrative": getattr(c, "attack_narrative", ""),
        "chain_length": getattr(c, "chain_length", 0),
    }


def _attack_step_to_dict(s: Any) -> Dict[str, Any]:
    return {
        "step_number": getattr(s, "step_number", 0),
        "action": getattr(s, "action", ""),
        "target_endpoint": getattr(s, "target_endpoint", ""),
        "payload_type": getattr(s, "payload_type", ""),
        "expected_response": getattr(s, "expected_response", ""),
        "finding_reference": getattr(s, "finding_reference", ""),
    }


def _attack_path_to_dict(p: Any) -> Dict[str, Any]:
    """Serialize AttackPath for Redis/API."""
    return {
        "path_id": getattr(p, "path_id", ""),
        "entry_point": _entry_point_to_dict(getattr(p, "entry_point", None)),
        "chains_involved": [getattr(c, "chain_id", "") for c in getattr(p, "chains_involved", [])],
        "steps": [_attack_step_to_dict(s) for s in getattr(p, "steps", [])],
        "final_impact": getattr(p, "final_impact", ""),
        "attacker_prerequisites": getattr(p, "attacker_prerequisites", []),
        "estimated_complexity": getattr(p, "estimated_complexity", "unknown"),
        "proof_of_concept_outline": getattr(p, "proof_of_concept_outline", ""),
    }


def _remediation_to_dict(r: Any) -> Dict[str, Any]:
    """Serialize Remediation for Redis/API."""
    return {
        "finding_id": getattr(r, "finding_id", ""),
        "fix_description": getattr(r, "fix_description", ""),
        "fixed_code": getattr(r, "fixed_code", ""),
        "fix_type": getattr(r, "fix_type", "patch"),
        "unit_test_code": getattr(r, "unit_test_code", ""),
        "unit_test_framework": getattr(r, "unit_test_framework", ""),
        "verification_steps": getattr(r, "verification_steps", []),
        "regression_risk": getattr(r, "regression_risk", ""),
    }

def _asyncio_exception_handler(loop, context):
    """Suppress ConnectionResetError during HTTP connection cleanup (Windows ProactorEventLoop)."""
    exc = context.get("exception")
    if exc is not None and isinstance(exc, ConnectionResetError):
        return  # Client closed connection; suppress noisy traceback
    loop.default_exception_handler(context)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Suppress ConnectionResetError on Windows when client closes connection after long requests
    try:
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(_asyncio_exception_handler)
    except RuntimeError:
        pass

    # Redis connectivity was checked at import (redis_client.py). Log status.
    if REDIS_AVAILABLE:
        logger.info("Redis: OK (enrichment pipeline enabled)")
    else:
        logger.error(
            "Redis: UNAVAILABLE — using MockRedis. file_deps, call_graph, sanitizer_registry, "
            "dead_code_map will NOT persist. /scan enrichment pipeline is BLIND."
        )
    app.state.session = aiohttp.ClientSession()
    yield
    await app.state.session.close()

app = FastAPI(lifespan=lifespan)


def _stream_progress(scan_id: str, msg: str, **extra: Any) -> None:
    """Push a progress message to Redis for live SSE streaming (Flask consumes via BLPOP)."""
    if not scan_id or not REDIS_AVAILABLE:
        return
    try:
        r = redis_client
        if getattr(r, "rpush", None):
            payload = {"msg": msg, **extra}
            r.rpush(f"{scan_id}:progress", json.dumps(payload))
    except Exception as e:
        logger.debug(f"Stream progress skip: {e}")


CACHE_CHOICE_WAIT_TIMEOUT = 120  # seconds to wait for user cache choice


def _wait_cache_choice(scan_id: str) -> bool:
    """Block until gateway sets scan_id:cache_choice; return True to use cache, False to rescan from 0."""
    if not scan_id or not REDIS_AVAILABLE:
        return False
    key = f"{scan_id}:cache_choice"
    deadline = time.time() + CACHE_CHOICE_WAIT_TIMEOUT
    while time.time() < deadline:
        try:
            raw = redis_client.blpop(key, timeout=2)
            if raw:
                _, value = raw
                s = (value.decode("utf-8") if isinstance(value, bytes) else value).strip().lower()
                if s in ("1", "true", "use", "yes"):
                    return True
                return False
        except Exception as e:
            logger.debug(f"Cache choice wait: {e}")
    logger.warning(f"[{scan_id}] Cache choice timeout; rescanning from 0")
    return False


def _redis_set_json(key: str, value: Any, ttl: int = SCAN_TTL) -> None:
    """
    Best-effort JSON write to Redis.

    Note: we intentionally attempt this even when REDIS_AVAILABLE is False because
    the codebase may be running with a MockRedis that still supports setex/get,
    and some features (agentic file tools) depend on `{scan_id}:file_store`.
    """
    r = redis_client
    if not getattr(r, "setex", None):
        return
    try:
        r.setex(key, ttl, json.dumps(value))
    except Exception as e:
        # Don't crash scans on Redis connectivity issues
        logger.debug(f"Redis setex failed for key={key!r}: {type(e).__name__}: {e}")


def _redis_get_json(key: str, default: Any = None) -> Any:
    """
    Best-effort JSON read from Redis.

    Works with real Redis as well as MockRedis (when present), and fails closed
    to `default` if the key is missing or data is invalid.
    """
    r = redis_client
    if not getattr(r, "get", None):
        return default
    try:
        raw = r.get(key)
    except Exception as e:
        logger.debug(f"Redis get failed for key={key!r}: {type(e).__name__}: {e}")
        return default
    if not raw:
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default


def _build_file_store(files: List[FileData]) -> Dict[str, str]:
    return {f.filename: f.content for f in files}


def _normalize_file_digests(files: List[FileData]) -> Dict[str, str]:
    digests = {}
    for f in files:
        digest = f.sha1 or hashlib.sha1(f.content.encode("utf-8", errors="ignore")).hexdigest()
        digests[f.filename] = digest
    return digests


def _compute_incremental_delta(
    current_files: Dict[str, str],
    cached_digests: Optional[Dict[str, str]],
) -> Dict[str, List[str]]:
    cached_digests = cached_digests or {}
    current_paths = set(current_files.keys())
    cached_paths = set(cached_digests.keys())
    changed = [
        path for path, digest in current_files.items()
        if cached_digests.get(path) != digest
    ]
    removed = sorted(cached_paths - current_paths)
    unchanged = sorted(current_paths - set(changed))
    return {
        "changed": sorted(changed),
        "removed": removed,
        "unchanged": unchanged,
    }


def _flatten_project_findings(vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    flattened = []
    for file_idx, vuln in enumerate(vulnerabilities):
        filename = vuln.get("filename", "unknown")
        for issue_idx, issue in enumerate(vuln.get("issues", [])):
            finding = dict(issue)
            finding.setdefault("filename", filename)
            finding.setdefault("file", filename)
            finding["_location"] = {"file_idx": file_idx, "issue_idx": issue_idx}
            flattened.append(finding)
    return flattened


def _rebuild_project_findings(
    vulnerabilities: List[Dict[str, Any]],
    findings: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    rebuilt = []
    for vuln in vulnerabilities:
        cloned = dict(vuln)
        cloned["issues"] = []
        rebuilt.append(cloned)

    for finding in findings:
        location = finding.pop("_location", None)
        if not location:
            continue
        file_idx = location.get("file_idx")
        if file_idx is None or file_idx >= len(rebuilt):
            continue
        rebuilt[file_idx]["issues"].append(finding)

    output = []
    for vuln in rebuilt:
        if vuln.get("issues"):
            vuln["count"] = len(vuln["issues"])
            output.append(vuln)
    return output


def _upsert_cross_file_chains(scan_id: str, filepath: str, chains: List[Dict[str, Any]]) -> None:
    if not scan_id or not chains:
        return
    existing = _redis_get_json(f"{scan_id}:cross_file_taint_chains", default={}) or {}
    existing[filepath] = chains
    _redis_set_json(f"{scan_id}:cross_file_taint_chains", existing)


def _distance_to_entry_point(
    function_key: Optional[str],
    call_graph: Dict[str, Dict[str, Any]],
) -> Optional[int]:
    if not function_key or function_key not in call_graph:
        return None
    queue = [(function_key, 0)]
    visited = set()
    while queue:
        current, distance = queue.pop(0)
        if current in visited or current not in call_graph:
            continue
        visited.add(current)
        current_data = call_graph[current]
        if current_data.get("is_entry_point"):
            return distance
        for caller in current_data.get("called_by", []):
            queue.append((caller, distance + 1))
    return None


def _annotate_findings_with_graph_context(
    findings: List[Dict[str, Any]],
    filename: str,
    dead_code_map: Dict[str, Dict[str, Any]],
    call_graph: Dict[str, Dict[str, Any]],
) -> None:
    for finding in findings:
        function_name = finding.get("function_name") or finding.get("trigger")
        if not function_name:
            continue
        function_key = f"{filename}::{function_name}"
        dead_info = dead_code_map.get(function_key, {})
        if dead_info:
            finding["is_dead"] = dead_info.get("is_dead", False)
            finding["is_test_only"] = dead_info.get("is_test_only", False)
            finding["distance_to_entry_point"] = _distance_to_entry_point(function_key, call_graph)


@app.post("/index_project")
async def index_project(
    req_data: IndexRequest,
    x_secret: str = Header(None),
    x_scan_id: str = Header(None),
):
    """Build regex/symbol index (ProjectIndexer) and store in Redis for scan context."""
    if x_secret != WORKER_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    if not x_scan_id:
        raise HTTPException(status_code=400, detail="Missing scan_id")

    project_key = (req_data.project_key or "").strip() or None
    digest_map = _normalize_file_digests(req_data.files)
    cache_key = f"{project_key}:regex_index" if project_key else None
    digest_key = f"{project_key}:file_digests" if project_key else None

    logger.info(f"[{x_scan_id}] Building regex/symbol index...")
    indexer = ProjectIndexer()
    incremental_meta = {
        "project_key": project_key,
        "changed_files": len(req_data.files),
        "unchanged_files": 0,
        "removed_files": 0,
        "used_cache": False,
    }

    if cache_key and digest_key:
        cached_index = _redis_get_json(cache_key)
        cached_digests = _redis_get_json(digest_key, default={}) or {}
        delta = _compute_incremental_delta(digest_map, cached_digests)
        if cached_index:
            indexer = ProjectIndexer.from_json(json.dumps(cached_index))
            for removed_path in delta["removed"]:
                indexer.remove_file(removed_path)
            incremental_meta.update({
                "changed_files": len(delta["changed"]),
                "unchanged_files": len(delta["unchanged"]),
                "removed_files": len(delta["removed"]),
                "used_cache": True,
            })
            files_to_index = [f for f in req_data.files if f.filename in set(delta["changed"])]
        else:
            files_to_index = list(req_data.files)
    else:
        files_to_index = list(req_data.files)

    n = len(req_data.files)
    _stream_progress(x_scan_id, f"Indexing project ({n} files)…" if n else "Indexing project…")
    for i, f in enumerate(files_to_index):
        indexer.index_file(f.filename, f.content)
        _stream_progress(x_scan_id, f"Indexed {f.filename}" + (f" ({i + 1}/{n})" if n > 1 else ""))

    index_json = indexer.to_json()
    if len(files_to_index) == len(req_data.files) and req_data.files:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                for f in req_data.files:
                    file_path = os.path.join(tmp, f.filename)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "w", encoding="utf-8", errors="ignore") as fh:
                        fh.write(f.content)
                native_data = index_project_on_disk(tmp)
                sym = native_data.get("symbol_index")
                if sym:
                    index_json = json.dumps(sym)
        except Exception as e:
            logger.warning(f"[{x_scan_id}] Native symbol index fallback to ProjectIndexer: {e}")
    try:
        redis_client.setex(x_scan_id, SCAN_TTL, index_json)
        _redis_set_json(f"{x_scan_id}:indexing_meta", {"regex": incremental_meta})
        if cache_key and digest_key:
            redis_client.setex(cache_key, PROJECT_CACHE_TTL, index_json)
            _redis_set_json(digest_key, digest_map, PROJECT_CACHE_TTL)
        logger.info(f"[{x_scan_id}] Regex index stored in Redis.")
    except Exception as e:
        logger.error(f"[{x_scan_id}] Failed to store index in Redis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok", "scan_id": x_scan_id, "incremental": incremental_meta}


@app.post("/index_project_deepwiki")
async def index_project_deepwiki(
    req_data: DeepWikiIndexRequest,
    x_secret: str = Header(None),
    x_scan_id: str = Header(None),
):
    if x_secret != WORKER_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    if not x_scan_id:
        raise HTTPException(status_code=400, detail="Missing scan_id")

    project_key = (req_data.project_key or "").strip() or None
    file_store = _build_file_store(req_data.files)
    digest_map = _normalize_file_digests(req_data.files)
    cache_prefix = f"{project_key}:" if project_key else None
    docs_cache_key = f"{cache_prefix}deepwiki_docs" if cache_prefix else None
    deepwiki_cache_key = f"{cache_prefix}deepwiki_index" if cache_prefix else None
    file_deps_cache_key = f"{cache_prefix}file_deps" if cache_prefix else None
    call_graph_cache_key = f"{cache_prefix}call_graph" if cache_prefix else None
    sanitizer_cache_key = f"{cache_prefix}sanitizer_registry" if cache_prefix else None
    dead_code_cache_key = f"{cache_prefix}dead_code_map" if cache_prefix else None
    api_surface_cache_key = f"{cache_prefix}api_surface" if cache_prefix else None
    file_store_cache_key = f"{cache_prefix}file_store" if cache_prefix else None
    digest_key = f"{cache_prefix}deepwiki_file_digests" if cache_prefix else None

    logger.info(f"[{x_scan_id}] Starting DeepWiki index build...")
    _stream_progress(x_scan_id, "Building project index…")

    _redis_set_json(f"{x_scan_id}:file_store", file_store)

    incremental_meta = {
        "project_key": project_key,
        "changed_files": len(req_data.files),
        "unchanged_files": 0,
        "removed_files": 0,
        "used_cache": False,
    }
    if digest_key:
        cached_digests = _redis_get_json(digest_key, default={}) or {}
        delta = _compute_incremental_delta(digest_map, cached_digests)
        incremental_meta.update({
            "changed_files": len(delta["changed"]),
            "unchanged_files": len(delta["unchanged"]),
            "removed_files": len(delta["removed"]),
        })

        if len(delta["changed"]) == 0 and len(delta["removed"]) == 0:
            cached_sets = {
                "deepwiki_index": _redis_get_json(deepwiki_cache_key),
                "file_deps": _redis_get_json(file_deps_cache_key),
                "call_graph": _redis_get_json(call_graph_cache_key),
                "sanitizer_registry": _redis_get_json(sanitizer_cache_key),
                "dead_code_map": _redis_get_json(dead_code_cache_key),
                "api_surface": _redis_get_json(api_surface_cache_key, default=[]),
                "file_store": _redis_get_json(file_store_cache_key, default=file_store),
            }
            cached_docs = _redis_get_json(docs_cache_key)
            if (
                cached_sets["deepwiki_index"] is not None
                and cached_sets["file_deps"] is not None
                and cached_sets["call_graph"] is not None
                and cached_sets["sanitizer_registry"] is not None
                and cached_sets["dead_code_map"] is not None
                and cached_sets["file_store"] is not None
                and cached_docs is not None
            ):
                # Ask user: use cache or rescan from 0 (push cache_detected, then wait for choice)
                _stream_progress(
                    x_scan_id,
                    "Cached project data found. Use it or rescan from scratch?",
                    cache_detected=True,
                )
                use_cache = _wait_cache_choice(x_scan_id)
                if use_cache:
                    for suffix, value in cached_sets.items():
                        _redis_set_json(f"{x_scan_id}:{suffix}" if suffix != "deepwiki_index" else f"{x_scan_id}:deepwiki_index", value)
                    combined_path = os.path.join(DEEPWIKI_DOCS_DIR, f"{x_scan_id}.md")
                    with open(combined_path, "w", encoding="utf-8") as md_file:
                        md_file.write(cached_docs)
                    incremental_meta["used_cache"] = True
                    existing_meta = _redis_get_json(f"{x_scan_id}:indexing_meta", default={}) or {}
                    existing_meta["deepwiki"] = incremental_meta
                    _redis_set_json(f"{x_scan_id}:indexing_meta", existing_meta)
                    logger.info(f"[{x_scan_id}] Reused cached DeepWiki + extended index state")
                    # Set deepwiki_complete so per-file /scan can merge agent findings (same as full path)
                    if getattr(redis_client, "setex", None):
                        try:
                            redis_client.setex(f"{x_scan_id}:deepwiki_complete", SCAN_TTL, "1")
                        except Exception as e:
                            logger.debug(f"Redis setex deepwiki_complete (cache path) failed: {type(e).__name__}: {e}")
                    return {"status": "ok", "scan_id": x_scan_id, "incremental": incremental_meta}
                logger.info(f"[{x_scan_id}] User chose rescan from 0; rebuilding DeepWiki index")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 1) Write all files to a temporary folder
        for f in req_data.files:
            file_path = os.path.join(tmpdir, f.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8", errors="ignore") as fh:
                fh.write(f.content)

        # 2) Native project index (symbol + extended sets); optional Flash summary
        _stream_progress(x_scan_id, "Building native project index…")
        t0 = time.time()
        index_data = index_project_on_disk(tmpdir)
        persist_extended_index(x_scan_id, index_data)
        file_dep_map = index_data.get("file_deps") or {}
        call_graph = index_data.get("call_graph") or {}
        sanitizer_registry = index_data.get("sanitizer_registry") or {}
        dead_code_map = index_data.get("dead_code_map") or {}
        api_surface = index_data.get("api_surface") or []
        if file_deps_cache_key:
            _redis_set_json(file_deps_cache_key, file_dep_map, PROJECT_CACHE_TTL)
        if call_graph_cache_key:
            _redis_set_json(call_graph_cache_key, call_graph, PROJECT_CACHE_TTL)
        if sanitizer_cache_key:
            _redis_set_json(sanitizer_cache_key, sanitizer_registry, PROJECT_CACHE_TTL)
        if dead_code_cache_key:
            _redis_set_json(dead_code_cache_key, dead_code_map, PROJECT_CACHE_TTL)
        if api_surface_cache_key:
            _redis_set_json(api_surface_cache_key, api_surface, PROJECT_CACHE_TTL)
        logger.info(f"[{x_scan_id}] Native index: {time.time()-t0:.2f}s")

        project_ir = build_deepwiki_project_ir(index_data)
        summary = None
        if llm_configured():
            try:
                async with aiohttp.ClientSession() as bridge_session:
                    summary = await maybe_summarize_project(bridge_session, x_scan_id, project_ir)
            except Exception as e:
                logger.warning(f"[{x_scan_id}] Project Flash summary skipped: {e}")
        if summary:
            project_ir["flash_summary"] = summary

        index_json = json.dumps(project_ir)
        try:
            redis_client.setex(f"{x_scan_id}:deepwiki_index", SCAN_TTL, index_json)
            if deepwiki_cache_key:
                redis_client.setex(deepwiki_cache_key, PROJECT_CACHE_TTL, index_json)
            logger.info(f"[{x_scan_id}] Project context stored in Redis (native index).")
        except Exception as e:
            logger.error(f"[{x_scan_id}] Failed to store project index in Redis: {e}")

        combined_text = summary or json.dumps(project_ir, indent=2)[:50000]
        combined_path = os.path.join(DEEPWIKI_DOCS_DIR, f"{x_scan_id}.md")
        try:
            with open(combined_path, "w", encoding="utf-8") as md_file:
                md_file.write(combined_text)
            if docs_cache_key:
                _redis_set_json(docs_cache_key, combined_text, PROJECT_CACHE_TTL)
        except Exception as e:
            logger.error(f"[{x_scan_id}] Failed to write project docs: {e}")
        _stream_progress(x_scan_id, "Project index ready.")

        # Multi-agent scan (if enabled, after project indexing)
        if AGENT_SCAN_ENABLED and (DEEPSEEK_API_KEY or OPENROUTER_API_KEY):
            try:
                file_contents = {}
                for root, _, files in os.walk(tmpdir):
                    for name in files:
                        path = os.path.join(root, name)
                        rel = os.path.relpath(path, tmpdir).replace("\\", "/")
                        try:
                            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                                file_contents[rel] = f.read()
                        except Exception:
                            pass
                agent_findings = await run_agent_scan(
                    call_graph=call_graph,
                    dependency_map=file_dep_map,
                    sanitizer_registry=sanitizer_registry if isinstance(sanitizer_registry, dict) else {},
                    dead_code_map=dead_code_map if isinstance(dead_code_map, dict) else {},
                    file_contents=file_contents,
                    file_asts={},
                    scan_id=x_scan_id,
                    repo_path=tmpdir,
                    language="python",
                    framework="flask",
                    scan_mode="full",
                    changed_files=[],
                    display_file_count=len(req_data.files),
                )
                if agent_findings and REDIS_AVAILABLE:
                    redis_client.setex(f"{x_scan_id}:agent_findings", SCAN_TTL, json.dumps(agent_findings))
                    logger.info(f"[{x_scan_id}] Agent scan: {len(agent_findings)} findings stored.")
            except Exception as e:
                logger.warning(f"[{x_scan_id}] Agent scan failed: {e}")

    if file_store_cache_key:
        _redis_set_json(file_store_cache_key, file_store, PROJECT_CACHE_TTL)
    if digest_key:
        _redis_set_json(digest_key, digest_map, PROJECT_CACHE_TTL)
    existing_meta = _redis_get_json(f"{x_scan_id}:indexing_meta", default={}) or {}
    existing_meta["deepwiki"] = incremental_meta
    _redis_set_json(f"{x_scan_id}:indexing_meta", existing_meta)

    # Signal that the entire deepwiki phase (indexers + agent scan) is complete.
    # Per-file /scan handlers use this flag to decide whether to merge agent findings.
    # Gateway also waits for this before starting per-file scans; use best-effort write
    # so it gets set even when REDIS_AVAILABLE was false at import (e.g. MockRedis).
    if getattr(redis_client, "setex", None):
        try:
            redis_client.setex(f"{x_scan_id}:deepwiki_complete", SCAN_TTL, "1")
        except Exception as e:
            logger.debug(f"Redis setex deepwiki_complete failed: {type(e).__name__}: {e}")
    logger.info(f"[{x_scan_id}] DeepWiki index + extended indexing complete.")
    return {"status": "ok", "scan_id": x_scan_id, "incremental": incremental_meta}

@app.post("/poc")
async def generate_pocs(
    poc_req: PocRequest,
    req: Request,
    x_secret: str = Header(None),
):
    if x_secret != WORKER_SECRET:
        raise HTTPException(403, "Invalid secret")

    session = req.app.state.session
    filename = poc_req.filename
    content = poc_req.content
    findings = poc_req.findings or []
    max_pocs = poc_req.max_pocs

    # Cap number of PoCs per call for safety
    findings = findings[:max_pocs]

    enriched_findings = []

    for f in findings:
        poc = await generate_poc_for_finding(
            session,
            filename,
            content,
            f
        )
        f_out = dict(f)
        if poc.get("status") == "OK":
            f_out["poc"] = poc
        else:
            f_out["poc_error"] = poc.get("details", "PoC generation failed")
        enriched_findings.append(f_out)

    return {
        "status": "OK",
        "findings": enriched_findings
    }


@app.post("/analyze")
async def analyze_project(
    analyze_req: AnalyzeRequest,
    req: Request, 
    x_secret: str = Header(None)
):
    if x_secret != WORKER_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    session = req.app.state.session
    url = OPENROUTER_API_URL

    payload = {
        "model": CHEAP_MODEL,
        "messages": [
            {"role": "system", "content": analyze_req.system_prompt},
            {"role": "user", "content": analyze_req.project_structure}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }
    
    try:
        async with session.post(url, json=payload, headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"}) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=500, detail="Analysis API failed")
            result = await resp.json()
            return json.loads(result['choices'][0]['message']['content'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cross_file_consistency")
async def cross_file_consistency(
    consistency_req: CrossFileConsistencyRequest,
    req: Request,
    x_secret: str = Header(None),
):
    if x_secret != WORKER_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    session = req.app.state.session
    scan_id = consistency_req.scan_id
    vulnerabilities = consistency_req.vulnerabilities or []
    flattened = _flatten_project_findings(vulnerabilities)

    for finding in flattened:
        if "reason" not in finding and finding.get("description"):
            finding["reason"] = finding["description"]
        if "function_name" not in finding and finding.get("trigger"):
            finding["function_name"] = finding["trigger"]

    sanitizer_registry = _redis_get_json(f"{scan_id}:sanitizer_registry", default={}) or {}
    chain_map = _redis_get_json(f"{scan_id}:cross_file_taint_chains", default={}) or {}
    checker = CrossFileConsistencyChecker()
    corrections = await checker.check(
        all_findings=flattened,
        sanitizer_registry=sanitizer_registry,
        session=session,
        scan_id=scan_id,
    )
    corrected = checker.apply_corrections(flattened, corrections, scan_id=scan_id)

    file_index_by_name = {
        vuln.get("filename"): idx for idx, vuln in enumerate(vulnerabilities)
    }
    chain_findings = []
    corroborated_keys = set()
    seen_chain_paths = set()
    for filename, chains in chain_map.items():
        entry_idx = file_index_by_name.get(filename)
        if entry_idx is None:
            continue
        for chain in chains or []:
            full_chain = chain.get("full_chain") or []
            chain_path = " -> ".join(full_chain)
            if not chain_path or chain_path in seen_chain_paths:
                continue
            seen_chain_paths.add(chain_path)
            for finding in corrected:
                fn_name = finding.get("function_name") or finding.get("trigger")
                if fn_name and any(fn_name == hop.split("::", 1)[-1] for hop in full_chain):
                    corroborated_keys.add(finding.get("fingerprint") or f"{finding.get('type')}:{finding.get('line')}")
                    finding["cross_file_taint"] = True
                    finding["cross_file_chain"] = chain_path
                    score = finding.get("confidence_score", 0)
                    try:
                        score = float(score)
                    except Exception:
                        score = 0.0
                    if score <= 10:
                        finding["confidence_score"] = min(10, round(score + 1))
                    else:
                        finding["confidence_score"] = min(100, round(score + 10))
                    if finding.get("severity") not in {"CRITICAL", "HIGH"}:
                        finding["severity"] = "HIGH"

            chain_finding = {
                "_location": {"file_idx": entry_idx},
                "severity": "HIGH",
                "type": "Cross-File Taint Chain",
                "trigger": chain.get("entry_point", filename),
                "function_name": chain.get("entry_point", filename),
                "line": chain.get("sink_line", 1),
                "description": (
                    f"User-controlled input crosses files before reaching {chain.get('final_sink')} via "
                    f"{chain_path}."
                ),
                "reason": (
                    f"Cross-file taint chain corroborated by dependency and call-graph analysis: {chain_path}"
                ),
                "vulnerable_code": chain.get("sink_content", ""),
                "confidence_score": 9,
                "cross_file_taint": True,
                "cross_file_chain": chain_path,
                "chain_depth": chain.get("chain_depth", len(full_chain)),
                "tainted_args": chain.get("tainted_args", []),
                "files_involved": sorted({
                    hop.split("::", 1)[0] for hop in full_chain if "::" in hop
                }),
            }
            chain_findings.append(chain_finding)

    corrected.extend(chain_findings)
    rebuilt = _rebuild_project_findings(vulnerabilities, corrected)

    # Build cross_file_consistency section from checker results
    removed_findings_detail = []
    for rf in getattr(checker, '_last_removed_findings', []):
        removed_findings_detail.append({
            "type": rf.get("type"),
            "file": rf.get("filename") or rf.get("file"),
            "line": rf.get("line"),
            "_removal_reason": rf.get("_removal_reason"),
        })

    return {
        "status": "ok",
        "scan_id": scan_id,
        "vulnerabilities": rebuilt,
        "summary": {
            "original_findings": len(flattened),
            "final_findings": sum(len(v.get("issues", [])) for v in rebuilt),
            "removed": len(corrections.get("remove", [])),
            "upgraded": len(corrections.get("upgrade", [])),
            "chain_findings_added": len(chain_findings),
            "corroborated_findings": len(corroborated_keys),
        },
        "cross_file_consistency": {
            "removed_count": len(corrections.get("remove", [])),
            "upgraded_count": len(corrections.get("upgrade", [])),
            "removed_findings": removed_findings_detail,
        },
    }


async def scan_code_pipeline(
    scan_req: ScanRequest,
    req: Request,
    x_scan_id: Optional[str],
    x_scan_type: str,
) -> Dict[str, Any]:
    """Per-file scan implementation (shared by HTTP ``/scan`` and local in-process runners)."""
    session = req.app.state.session

    # LOG: Start
    display_name = os.path.basename(scan_req.filename)
    logger.info(f"[{x_scan_id}] Scanning File: {display_name} | Plan: Tier {x_scan_type}")

    # --- STEP 1: Context & Keywords (All Tiers) ---
    external_context = ""
    if x_scan_id:
        try:
            raw_data = redis_client.get(x_scan_id)
            if raw_data:
                indexer = ProjectIndexer.from_json(raw_data)
                external_context = indexer.get_context_for_code(scan_req.content)
        except:
            pass

    # NEW: DeepWiki project-wide context (if available)
    deepwiki_context = ""
    if x_scan_id:
        try:
            deepwiki_raw = redis_client.get(f"{x_scan_id}:deepwiki_index")
            if deepwiki_raw:
                project_ir = json.loads(deepwiki_raw)
                deepwiki_context = build_security_context(project_ir)
        except Exception as e:
            logger.error(f"[{x_scan_id}] Failed to load DeepWiki index: {e}")
            deepwiki_context = ""

    found_keywords = check_keywords(scan_req.content)
    if found_keywords:
        logger.info(f"[{x_scan_id}] Keywords found: {found_keywords}")

    # Stage 0: Optional context compaction for large files before expensive LLM validation passes.
    content_for_advanced = scan_req.content
    compaction_meta = {}
    if (
        ENABLE_CONTEXT_COMPACTION
        and len(scan_req.content) >= COMPACTION_MIN_CHARS
        and (x_scan_type in ["2", "3", "4"] or scan_req.use_llm_centric)
    ):
        try:
            content_for_advanced, compaction_meta = await compact_security_context(
                session=session,
                filename=scan_req.filename,
                content=scan_req.content,
                recall_keywords=found_keywords,
            )
            logger.info(
                f"[{x_scan_id}] Context compaction: kept {compaction_meta.get('kept_lines')}/"
                f"{compaction_meta.get('total_lines')} lines (drop_ratio={compaction_meta.get('drop_ratio')})"
            )
        except Exception as e:
            logger.warning(f"[{x_scan_id}] Context compaction failed, continuing with original content: {e}")
            content_for_advanced = scan_req.content
            compaction_meta = {"enabled": True, "error": str(e)}

    # --- NEW: Pre-scan enrichment (Layer 2) ---
    # Extract taint sources, risk score, and load sanitizer/dead-code data
    taint_hints = {"tainted_variables": [], "has_user_input": False, "entry_points": []}
    risk_ranking = {"risk_score": 0.5, "recommended_tier": int(x_scan_type), "skip": False}
    sanitizer_registry = {}
    api_surface = []
    call_graph = {}
    dead_code_map = {}
    dead_code_list = []
    context_slice = {}  # Context slice from ContextSlicer
    hard_rule_findings = []  # Hard detection rule findings (MISS 1-4 fix)

    try:
        # 0. Apply hard detection rules FIRST (deterministic vulnerability detection)
        from backend.worker.core.findings_filter import apply_hard_detection_rules
        hard_rule_findings = apply_hard_detection_rules(
            filepath=scan_req.filename,
            content=scan_req.content,
            language="python"  # Auto-detect based on extension in the function
        )
        if hard_rule_findings:
            logger.info(f"[{x_scan_id}] Hard detection rules found {len(hard_rule_findings)} vulnerabilities")
            for f in hard_rule_findings:
                logger.info(f"  - {f['type']} at line {f['line']}: {f['description'][:60]}...")

        # 1. Extract taint hints
        dfe = DataflowHintExtractor()
        taint_hints = dfe.extract(scan_req.filename, scan_req.content, scan_id=x_scan_id)
        if x_scan_id and REDIS_AVAILABLE:
            api_surface = _redis_get_json(f"{x_scan_id}:api_surface", default=[]) or []
            public_entry_names = {
                item.get("name") for item in api_surface if item.get("file") == scan_req.filename
            }
            if public_entry_names:
                taint_hints["public_entry_points"] = sorted(
                    set(taint_hints.get("entry_points", [])) & public_entry_names
                )
                for variable in taint_hints.get("tainted_variables", []):
                    variable["source_is_public_entry"] = bool(taint_hints["public_entry_points"])
        if taint_hints.get("has_user_input"):
            logger.info(f"[{x_scan_id}] Taint sources found: {len(taint_hints['tainted_variables'])}")

        for secret in taint_hints.get("secrets", []):
            hard_rule_findings.append({
                "type": "Hardcoded Secret",
                "severity": "HIGH",
                "confidence_score": 9,
                "cwe_id": "CWE-798",
                "function_name": "module_scope",
                "line": secret.get("line", 1),
                "description": f"Hardcoded {secret.get('secret_type', 'secret')} detected in source.",
                "reason": f"Hardcoded {secret.get('secret_type', 'secret')} detected in source.",
                "vulnerable_code": secret.get("line_content", ""),
                "tainted_variable": secret.get("variable"),
                "sanitizers_checked": False,
            })

        # 2. Risk rank this file
        frr = FileRiskRanker()
        risk_ranking = frr.rank_one(scan_req.filename, scan_req.content)
        logger.info(f"[{x_scan_id}] Risk score: {risk_ranking['risk_score']}, recommended tier: {risk_ranking['recommended_tier']}")

        # Override scan_type if risk score pushes it higher
        if risk_ranking["recommended_tier"] > int(x_scan_type):
            x_scan_type = str(risk_ranking["recommended_tier"])
            logger.info(f"[{x_scan_id}] Risk-based tier override: now Tier {x_scan_type}")

        # 3. Load sanitizer registry from Redis
        if x_scan_id and REDIS_AVAILABLE:
            try:
                sanitizer_data = redis_client.get(f"{x_scan_id}:sanitizer_registry")
                if sanitizer_data:
                    sanitizer_registry = json.loads(sanitizer_data)
                    logger.info(f"[{x_scan_id}] Loaded sanitizer registry: {len(sanitizer_registry.get('custom_sanitizers', []))} custom sanitizers")
            except Exception as e:
                logger.warning(f"[{x_scan_id}] Failed to load sanitizer registry: {e}")

            try:
                call_graph_data = redis_client.get(f"{x_scan_id}:call_graph")
                if call_graph_data:
                    call_graph = json.loads(call_graph_data)
            except Exception as e:
                logger.warning(f"[{x_scan_id}] Failed to load call graph: {e}")

            # 4. Load dead code map from Redis
            try:
                dead_code_data = redis_client.get(f"{x_scan_id}:dead_code_map")
                if dead_code_data:
                    dead_code_map = json.loads(dead_code_data)
                    dead_code_list = [k for k, v in dead_code_map.items() if v.get("is_dead") or v.get("is_test_only")]
                    logger.info(f"[{x_scan_id}] Loaded dead code map: {len(dead_code_list)} dead/test functions")
            except Exception as e:
                logger.warning(f"[{x_scan_id}] Failed to load dead code map: {e}")

            # 5. Build context slice (if scan_id available)
            try:
                # Get first function name from file to slice for
                func_name = None
                if taint_hints.get("entry_points"):
                    func_name = taint_hints["entry_points"][0]
                if func_name and x_scan_id:
                    slicer = ContextSlicer()
                    context_slice = slicer.slice_for_scan(
                        filepath=scan_req.filename,
                        function_name=func_name,
                        scan_id=x_scan_id,
                        project_path="",
                        tainted_variables=taint_hints.get("tainted_variables", [])  # Pass tainted vars for MISS 4
                    )
                    if context_slice.get("callers") or context_slice.get("security_callees"):
                        logger.info(f"[{x_scan_id}] Context slice built: {len(context_slice.get('callers', []))} callers, {len(context_slice.get('security_callees', []))} callees")
                    # Log cross-file taint chains (MISS 4 fix)
                    if context_slice.get("cross_file_taint_chains"):
                        chains = context_slice["cross_file_taint_chains"]
                        _upsert_cross_file_chains(x_scan_id, scan_req.filename, chains)
                        logger.info(f"[{x_scan_id}] Cross-file taint chains detected: {len(chains)}")
                        for chain in chains:
                            logger.info(f"  - {chain['entry_point']} -> {chain['intermediate_function']} -> {chain['final_sink']}")
            except Exception as e:
                logger.warning(f"[{x_scan_id}] Context slicing failed: {e}")

        if hard_rule_findings:
            detailed_keywords = find_keywords_with_lines(scan_req.content, ALL_KEYWORDS)
            for finding in hard_rule_findings:
                finding.setdefault("keywords_detected", detailed_keywords)
                ctx, fp = get_code_context_and_fingerprint(
                    scan_req.content,
                    scan_req.filename,
                    finding.get("line", 1),
                    finding.get("vulnerable_code", ""),
                )
                finding.setdefault("code_context", ctx)
                finding.setdefault("fingerprint", fp)
                finding["source_is_public_entry"] = bool(taint_hints.get("public_entry_points"))

    except re.error as e:
        bad_pattern = getattr(e, "pattern", None) or getattr(e, "msg", str(e))
        logger.warning(
            "[%s] Enrichment regex error in %s: %s (pattern preview: %s). Continuing without enrichment for this file.",
            x_scan_id, scan_req.filename, e, repr(bad_pattern)[:200] if bad_pattern else "n/a",
        )
    except Exception as e:
        logger.error(f"[{x_scan_id}] Enrichment failed: {e}")

    # Skip low-risk files - but mark as NOT_SCANNED instead of SAFE
    # This is a cost-control optimization: low-risk files don't reach LLM
    # but shouldn't claim "SAFE" since there was no security analysis.
    if risk_ranking.get("skip"):
        logger.info(f"[{x_scan_id}] Skipping low-risk file (score < 0.05)")
        return {
            "status": "NOT_SCANNED",
            "risk_score": risk_ranking["risk_score"],
            "skipped": True,
            "skip_reason": f"Risk score {risk_ranking['risk_score']:.2f} below threshold 0.05 (cost optimization)",
        }

    flash_enriched = ""
    if external_context:
        flash_enriched = external_context[:2000]
    elif deepwiki_context:
        flash_enriched = deepwiki_context[:2000]
    if taint_hints.get("has_user_input"):
        flash_enriched += "\n\nTainted variables:\n" + "\n".join(
            f"  - {v['variable']} from {v['source']} (line {v['line']})"
            for v in taint_hints["tainted_variables"]
        )
    if context_slice and (context_slice.get("callers") or context_slice.get("security_callees")):
        flash_enriched += "\n\n" + ContextSlicer().format_for_prompt(context_slice)[:1500]

    use_flash_path = (
        llm_configured()
        and x_scan_type not in ("4",)
        and not scan_req.use_llm_centric
    )
    if use_flash_path:
        try:
            if await bridge_healthy(session):
                logger.info(f"[{x_scan_id}] Single deepseek-flash scan for {display_name}")
                slice_text = ContextSlicer().format_for_prompt(context_slice) if context_slice else ""
                flash_result = await deepseek_single_file_scan(
                    session,
                    x_scan_id,
                    scan_req.filename,
                    scan_req.content,
                    enriched_context=flash_enriched,
                    context_slice_text=slice_text,
                )
                if flash_result.get("findings") or flash_result.get("status") == "SAFE":
                    findings = list(flash_result.get("findings") or [])
                    if hard_rule_findings:
                        seen = {f.get("fingerprint") for f in findings}
                        for hr in hard_rule_findings:
                            if hr.get("fingerprint") not in seen:
                                findings.append(hr)
                    detailed_keywords = find_keywords_with_lines(scan_req.content, ALL_KEYWORDS)
                    for finding in findings:
                        finding.setdefault("keywords_detected", detailed_keywords)
                        ctx, fp = get_code_context_and_fingerprint(
                            scan_req.content,
                            scan_req.filename,
                            finding.get("line", 1),
                            finding.get("vulnerable_code", ""),
                        )
                        finding.setdefault("code_context", ctx)
                        finding.setdefault("fingerprint", fp)
                    _annotate_findings_with_graph_context(
                        findings,
                        filename=scan_req.filename,
                        dead_code_map=dead_code_map,
                        call_graph=call_graph,
                    )
                    if findings:
                        return {
                            "status": "VULNERABLE",
                            "findings": findings,
                            "scan_type": flash_result.get("scan_type", "deepseek-flash"),
                            "keywords_found": [k[:100] for k in found_keywords] if found_keywords else [],
                        }
                    return {
                        "status": "SAFE",
                        "scan_type": flash_result.get("scan_type", "deepseek-flash"),
                    }
        except Exception as e:
            logger.warning(f"[{x_scan_id}] deepseek-flash path failed, using tier ladder: {e}")

    # --- STEP 2: Run Tier 1 (`CHEAP_MODEL`) ---
    # We run this for EVERYONE.
    logger.info(f"[{x_scan_id}] Running Tier 1 scan (CHEAP_MODEL)...")

    # Build a light context specifically for Tier 1 to keep it cheap:
    # Prefer local graph context; if missing, fall back to a trimmed DeepWiki summary.
    light_context = ""
    if external_context:
        light_context = external_context[:2000]
    elif deepwiki_context:
        light_context = deepwiki_context[:2000]

    # NEW: Build enriched context with taint hints and sanitizer info
    enriched_context = light_context
    if taint_hints.get("has_user_input"):
        taint_summary = "Tainted variables:\n" + "\n".join(
            f"  - {v['variable']} from {v['source']} (line {v['line']})"
            for v in taint_hints["tainted_variables"]
        )
        enriched_context = f"{enriched_context}\n\n{taint_summary}"

    if sanitizer_registry.get("custom_sanitizers"):
        sanitizer_summary = "Confirmed sanitizers in project:\n" + "\n".join(
            f"  - {s}"
            for s in sanitizer_registry["custom_sanitizers"]
        )
        enriched_context = f"{enriched_context}\n\n{sanitizer_summary}"

    if api_surface:
        surface_summary = "Public entry points in project:\n" + "\n".join(
            f"  - {item.get('file')}::{item.get('name')} (line {item.get('line')})"
            for item in api_surface[:12]
        )
        enriched_context = f"{enriched_context}\n\n{surface_summary}"

    if dead_code_list:
        dead_summary = "Dead/test functions (downgrade confidence):\n" + "\n".join(
            f"  - {f}"
            for f in dead_code_list[:10]  # Limit to first 10
        )
        enriched_context = f"{enriched_context}\n\n{dead_summary}"

    # Add context slice if available
    if context_slice and (context_slice.get("callers") or context_slice.get("security_callees")):
        slicer = ContextSlicer()
        context_text = slicer.format_for_prompt(context_slice)
        enriched_context = f"{enriched_context}\n\n{context_text[:1500]}"  # Cap size

    triage_result = await scan_tier_1_basic(
        session,
        scan_req.filename,
        scan_req.content,
        enriched_context
    )
    
    status = triage_result.get("status", "UNKNOWN")
    logger.info(f"[{x_scan_id}] Tier 1 verdict: {status}")


    # --- STEP 3: Decision Logic ---
    
    tier4_fallback = False  # True when Tier 4 failed/empty and we use Tier 1 results without re-filtering
    
    # CASE LLM-CENTRIC: Pure LLM-based detection (NEW - most intelligent, most expensive)
    # This uses LLM for both detection AND filtering, minimal hard-coded rules
    if x_scan_type == "4" or scan_req.use_llm_centric:
        logger.info(f"[{x_scan_id}] 🧠 LLM-CENTRIC MODE: Using LLM as primary detection engine")
        
        try:
            # Combine contexts
            combined_context = ""
            if deepwiki_context:
                combined_context += deepwiki_context[:2000] + "\n\n"
            if external_context:
                combined_context += external_context[:1000]
            if api_surface:
                combined_context += "\n\nPublic entry points:\n" + "\n".join(
                    f"- {item.get('file')}::{item.get('name')}"
                    for item in api_surface[:10]
                )
            if context_slice.get("cross_file_taint_chains"):
                combined_context += "\n\nCross-file taint chains:\n" + "\n".join(
                    f"- {' -> '.join(chain.get('full_chain', []))}"
                    for chain in context_slice.get("cross_file_taint_chains", [])[:5]
                )
            
            # Single intelligent LLM pass (detection + filtering together)
            llm_findings, llm_meta = await llm_centric_scan(
                session=session,
                filename=scan_req.filename,
                content=content_for_advanced,
                context_info=combined_context,
                use_smart_filter=True,  # Double-check with smart filter
            )
            
            if llm_findings:
                # Add enrichment
                detailed_keywords = find_keywords_with_lines(scan_req.content, ALL_KEYWORDS)
                for finding in llm_findings:
                    # Re-anchor line numbers against original file when compaction changed line offsets.
                    finding["line"] = find_line_number(
                        scan_req.content,
                        finding.get("vulnerable_code", ""),
                        function_name=finding.get("function_name", ""),
                    )
                    # Normalize: backend expects "reason"; LLM-centric prompt uses "reasoning"
                    if "reason" not in finding and finding.get("reasoning"):
                        finding["reason"] = finding["reasoning"]
                    finding["keywords_detected"] = detailed_keywords
                    ctx, fp = get_code_context_and_fingerprint(
                        scan_req.content,
                        scan_req.filename,
                        finding.get("line", 1),
                        finding.get("vulnerable_code", "")
                    )
                    finding["code_context"] = ctx
                    finding["fingerprint"] = fp
                _annotate_findings_with_graph_context(
                    llm_findings,
                    filename=scan_req.filename,
                    dead_code_map=dead_code_map,
                    call_graph=call_graph,
                )
                for finding in llm_findings:
                    finding["source_is_public_entry"] = bool(taint_hints.get("public_entry_points"))

                borderline_findings = []
                high_confidence_findings = []
                for finding in llm_findings:
                    score = finding.get("confidence_score", finding.get("confidence", 0)) or 0
                    try:
                        score = float(score)
                    except Exception:
                        score = 0.0
                    if score < TIER4_AGENTIC_CONFIDENCE_FLOOR:
                        borderline_findings.append(finding)
                    else:
                        high_confidence_findings.append(finding)

                phase2_summary = None
                if borderline_findings and x_scan_id:
                    agentic_config = AgenticValidationConfig(
                        max_tool_calls_per_finding=AGENTIC_TIER4_MAX_TOOL_CALLS_PER_FINDING,
                        max_total_tool_calls_per_scan=AGENTIC_TIER4_MAX_TOOL_CALLS_PER_SCAN,
                        agentic_confidence_ceiling=AGENTIC_CONFIDENCE_CEILING,
                    )
                    tier4_kept, phase2_summary = await apply_two_phase_validation(
                        session=app.state.session,
                        findings=borderline_findings,
                        filename=scan_req.filename,
                        file_content=scan_req.content,
                        context_info=combined_context,
                        confidence_threshold=PHASE2_CONFIDENCE_THRESHOLD,
                        agentic_config=agentic_config,
                        scan_id=x_scan_id,
                        file_store=_redis_get_json(f"{x_scan_id}:file_store", default={}) or {},
                        redis_client=redis_client,
                    )
                    llm_findings = high_confidence_findings + tier4_kept
                
                final_result = {
                    "status": "VULNERABLE",
                    "findings": llm_findings,
                    "_llm_centric_meta": llm_meta,
                    "scan_type": "4 (LLM-Centric)",
                }
                if phase2_summary:
                    final_result["_two_phase_summary"] = {
                        "phase": "tier4_agentic_validation",
                        "phase2": phase2_summary,
                    }
                if compaction_meta:
                    final_result["_compaction"] = compaction_meta
                logger.info(f"[{x_scan_id}] ✅ LLM-Centric Complete: {len(llm_findings)} high-confidence findings")
                return final_result
            else:
                # Tier 4 returned 0: fall back to Tier 1 results if we have any so user doesn't get 0
                if triage_result.get("status") == "VULNERABLE" and triage_result.get("findings"):
                    logger.info(f"[{x_scan_id}] Tier 4 returned 0 findings; using Tier 1 results ({len(triage_result['findings'])} findings)")
                    tier4_fallback = True
                    x_scan_type = "1"  # Fall through to Tier 1 path below
                else:
                    if hard_rule_findings:
                        return {
                            "status": "VULNERABLE",
                            "findings": hard_rule_findings,
                            "_llm_centric_meta": llm_meta,
                            "scan_type": "4 (LLM-Centric)",
                        }
                    return {
                        "status": "SAFE",
                        "_llm_centric_meta": llm_meta,
                        "scan_type": "4 (LLM-Centric)",
                    }
                
        except Exception as e:
            logger.exception(f"[{x_scan_id}] LLM-Centric failed: {e}")
            # Fall back to Tier 1 if LLM-centric fails
            logger.info(f"[{x_scan_id}] Falling back to Tier 1...")
            tier4_fallback = True
            x_scan_type = "1"  # Continue to Tier 1 logic
    
    # CASE A: User is Tier 1 (Free)
    if x_scan_type == "1":
        # Tier 4 fallback: return Tier 1 findings without Phase 1/2 filtering (they were already triaged)
        if tier4_fallback and triage_result.get("status") == "VULNERABLE" and triage_result.get("findings"):
            logger.info(f"[{x_scan_id}] Tier 4 fallback: returning {len(triage_result['findings'])} Tier 1 findings (no extra filtering)")
            detailed_keywords = find_keywords_with_lines(scan_req.content, ALL_KEYWORDS)
            for finding in triage_result["findings"]:
                finding["keywords_detected"] = detailed_keywords
                ctx, fp = get_code_context_and_fingerprint(
                    scan_req.content,
                    scan_req.filename,
                    finding.get("line", 1),
                    finding.get("vulnerable_code", "")
                )
                finding["code_context"] = ctx
                finding["fingerprint"] = fp
            triage_result["scan_type"] = "4 (fallback Tier 1)"
            if found_keywords:
                triage_result["keywords_found"] = [k[:100] for k in found_keywords]
            return triage_result

        # Apply two-phase false positive filtering to Tier 1 results
        if triage_result.get("status") == "VULNERABLE" and triage_result.get("findings"):
            from backend.worker.core.findings_filter import FindingsFilter

            # Phase 1: Hard exclusions
            logger.info(f"[{x_scan_id}] Tier 1 - Phase 1: Hard exclusion filtering...")
            fp_filter = FindingsFilter(
                use_hard_exclusions=True,
                use_llm_filtering=False,
                confidence_threshold=PHASE1_CONFIDENCE_THRESHOLD
            )
            success, filter_results, stats = fp_filter.filter_findings(
                triage_result["findings"],
                context={"filename": scan_req.filename, "scan_id": x_scan_id}
            )

            if success:
                phase1_filtered = filter_results.get("filtered_findings", [])
                phase1_excluded = len(filter_results.get("excluded_findings", []))

                logger.info(f"[{x_scan_id}] Tier 1 - Phase 1: {len(phase1_filtered)}/{len(triage_result['findings'])} passed")

                # Phase 2: Parallel LLM validation for Tier 1 (limited to avoid credit drain)
                # Only validate if we have findings and not too many
                if phase1_filtered and len(phase1_filtered) <= FREE_TIER_PHASE2_MAX_FINDINGS:
                    logger.info(f"[{x_scan_id}] Tier 1 - Phase 2: Parallel validation...")
                    try:
                        phase2_kept, phase2_summary = await apply_two_phase_validation(
                            session=app.state.session,
                            findings=phase1_filtered,
                            filename=scan_req.filename,
                            file_content=scan_req.content,
                            context_info=deepwiki_context or "",
                            confidence_threshold=PHASE2_CONFIDENCE_THRESHOLD,
                        )

                        if not phase2_kept:
                            triage_result["status"] = "SAFE"
                            triage_result["findings"] = []
                        else:
                            triage_result["findings"] = phase2_kept
                            triage_result["_two_phase_summary"] = {
                                "phase1_excluded": phase1_excluded,
                                "phase2": phase2_summary,
                            }
                        logger.info(f"[{x_scan_id}] Tier 1 - Phase 2: Kept {len(phase2_kept)}/{len(phase1_filtered)}")
                    except Exception as e:
                        logger.warning(f"[{x_scan_id}] Tier 1 Phase 2 failed: {e}")
                        triage_result["findings"] = phase1_filtered
                else:
                    # Skip Phase 2 for Tier 1 if too many findings (cost control)
                    if len(phase1_filtered) > FREE_TIER_PHASE2_MAX_FINDINGS:
                        logger.info(
                            f"[{x_scan_id}] Tier 1: Skipping Phase 2 (>{FREE_TIER_PHASE2_MAX_FINDINGS} findings, cost control)"
                        )
                    triage_result["findings"] = phase1_filtered
                    triage_result["_filtering_summary"] = filter_results.get("analysis_summary", {})

        # Merge hard rule findings with AI findings
        if hard_rule_findings:
            if triage_result.get("status") != "VULNERABLE":
                triage_result["status"] = "VULNERABLE"
                triage_result["findings"] = []

            # Add hard rule findings to the findings list
            existing_lines = {f.get("line") for f in triage_result.get("findings", [])}
            for hr_finding in hard_rule_findings:
                # Avoid duplicates (same line)
                if hr_finding.get("line") not in existing_lines:
                    triage_result["findings"].append(hr_finding)
                    existing_lines.add(hr_finding.get("line"))

            logger.info(f"[{x_scan_id}] Merged {len(hard_rule_findings)} hard-rule findings into Tier 1 results")

        logger.info(f"[{x_scan_id}] ✅ Tier 1 Complete.")
        if found_keywords: triage_result["keywords_found"] = [k[:100] for k in found_keywords]
        return triage_result

    # CASE B: User is Tier 2/3 (Paid), but file is SAFE
    if status == "SAFE":
        should_escalate_safe = (
            ENABLE_TIER23_SAFE_ESCALATION
            and x_scan_type in ["2", "3"]
            and len(scan_req.content) > COMPACTION_MIN_CHARS
            and len(found_keywords or []) >= TIER23_SAFE_ESCALATION_KEYWORD_COUNT
        )
        if should_escalate_safe:
            logger.warning(
                f"[{x_scan_id}] SAFE escalation enabled: escalating Tier {x_scan_type} due to high-risk keyword density "
                f"({len(found_keywords)} keywords)"
            )
            status = "VULNERABLE"
            triage_result.setdefault("findings", [])
            triage_result["_safe_escalation_reason"] = (
                f"Tier1 SAFE but high-risk keyword count={len(found_keywords)}"
            )
        else:
            logger.info(f"[{x_scan_id}] File is Safe. Skipping Tier 2/3 escalation to save credits.")
            if hard_rule_findings:
                triage_result["status"] = "VULNERABLE"
                triage_result["findings"] = list(hard_rule_findings)
            triage_result["scan_type"] = f"{x_scan_type} (Optimized)"
            if found_keywords: triage_result["keywords_found"] = [k[:100] for k in found_keywords]
            if compaction_meta:
                triage_result["_compaction"] = compaction_meta
            return triage_result

    # CASE C: User is Tier 2/3 AND file is VULNERABLE
    logger.warning(f"[{x_scan_id}] 🚨 Escalating to Tier {x_scan_type} (SMART_MODEL / TIER2_MODEL)...")

    # Combine project-wide DeepWiki context + local regex context
    combined_context = ""
    if deepwiki_context:
        combined_context += "Project-wide security context:\n" + deepwiki_context + "\n\n"
    if external_context:
        combined_context += "Local code graph context:\n" + external_context
    if api_surface:
        combined_context += "\n\nAPI surface:\n" + "\n".join(
            f"- {item.get('file')}::{item.get('name')} (line {item.get('line')})"
            for item in api_surface[:15]
        )
    if context_slice.get("cross_file_taint_chains"):
        combined_context += "\n\nCross-file taint chains:\n" + "\n".join(
            f"- {' -> '.join(chain.get('full_chain', []))}"
            for chain in context_slice.get("cross_file_taint_chains", [])[:5]
        )

    final_result = {}

    # Decide whether to use focused mode (large file) or full-file mode (small file)
    content_len = len(scan_req.content)
    # You can tune this threshold; e.g., 20k chars ~ 300–400 lines typical
    is_large_file = content_len > 20000

    tier1_for_escalation = triage_result if is_large_file else None

    if x_scan_type == "2":
        final_result = await scan_tier_2_standard(
            session,
            scan_req.filename,
            scan_req.content,
            combined_context or external_context,   # context_info
            tier1_result=tier1_for_escalation,        # None for small files → full-file
            compacted_context=content_for_advanced if content_for_advanced != scan_req.content else "",
        )
    elif x_scan_type == "3":
        final_result = await scan_tier_3_advanced(
            session,
            scan_req.filename,
            scan_req.content,
            combined_context or external_context,   # context_info
            tier1_result=tier1_for_escalation,        # None for small files → full-file
            compacted_context=content_for_advanced if content_for_advanced != scan_req.content else "",
        )




    # --- FALLBACK LOGIC ---
    # If Tier 2/3 failed (ERROR/UNKNOWN) but Tier 1 said VULNERABLE, return Tier 1 result
    # with a note attached.
    if final_result.get("status") in ["ERROR", "UNKNOWN"] and status == "VULNERABLE":
        logger.error(f"[{x_scan_id}] Tier {x_scan_type} Failed. Falling back to Tier 1 result.")
        triage_result["scan_type"] = f"Tier 1 (Fallback from {x_scan_type})"
        triage_result["note"] = "Advanced analysis failed due to provider timeout. Basic results shown."
        if found_keywords: triage_result["keywords_found"] = [k[:100] for k in found_keywords]
        return triage_result

    # --- STEP 4: Enrichment (Highlighting) ---
    if final_result.get("status") == "VULNERABLE" and final_result.get("findings"):
        detailed_keywords = find_keywords_with_lines(scan_req.content, ALL_KEYWORDS)
        for finding in final_result["findings"]:
            finding["keywords_detected"] = detailed_keywords
            ctx, fp = get_code_context_and_fingerprint(
                scan_req.content,
                scan_req.filename,
                finding.get("line", 1),
                finding.get("vulnerable_code", "")
            )
            finding["code_context"] = ctx
            finding["fingerprint"] = fp
        _annotate_findings_with_graph_context(
            final_result["findings"],
            filename=scan_req.filename,
            dead_code_map=dead_code_map,
            call_graph=call_graph,
        )
        for finding in final_result["findings"]:
            finding["source_is_public_entry"] = bool(taint_hints.get("public_entry_points"))

    # Merge agent findings from index-time multi-agent scan (if any)
    if x_scan_id and REDIS_AVAILABLE:
        try:
            # Check deepwiki_complete flag to avoid race with incomplete deepwiki indexing
            deepwiki_done = redis_client.get(f"{x_scan_id}:deepwiki_complete")
            if not deepwiki_done:
                logger.warning(
                    f"[{x_scan_id}] deepwiki_complete flag not set yet — skipping agent findings "
                    f"merge for file={scan_req.filename}. This may indicate a race condition."
                )
            else:
                raw = redis_client.get(f"{x_scan_id}:agent_findings")
                if raw:
                    agent_findings = json.loads(raw)
                    if agent_findings and isinstance(agent_findings, list):
                        final_result.setdefault("findings", []).extend(agent_findings)
                        if final_result.get("status") != "VULNERABLE":
                            final_result["status"] = "VULNERABLE"
                        logger.info(f"[{x_scan_id}] Merged {len(agent_findings)} agent findings into scan result.")
        except Exception as e:
            logger.warning(f"[{x_scan_id}] Failed to load agent findings: {e}")

    # --- STEP 5: Two-Phase False Positive Filtering (Anthropic-Style) ---
    # Phase 1: Hard exclusion rules (fast, regex-based)
    # Phase 2: Parallel LLM validation (each finding validated individually)
    if final_result.get("status") == "VULNERABLE" and final_result.get("findings"):
        from backend.worker.core.findings_filter import FindingsFilter

        # Phase 1: Hard exclusions (fast rule-based filtering)
        logger.info(f"[{x_scan_id}] Phase 1: Applying hard exclusion rules...")
        findings_filter = FindingsFilter(
            use_hard_exclusions=True,
            use_llm_filtering=False,
            confidence_threshold=PHASE1_CONFIDENCE_THRESHOLD
        )

        original_findings = final_result["findings"]
        success, filter_results, stats = findings_filter.filter_findings(
            original_findings,
            context={"filename": scan_req.filename, "scan_id": x_scan_id}
        )

        if success:
            phase1_filtered = filter_results.get("filtered_findings", [])
            phase1_excluded = len(filter_results.get("excluded_findings", []))

            logger.info(f"[{x_scan_id}] Phase 1 complete: {len(phase1_filtered)}/{len(original_findings)} findings passed hard filters")

            # Phase 2: Anthropic-style parallel LLM validation (if findings remain)
            if phase1_filtered and len(phase1_filtered) > 0:
                logger.info(f"[{x_scan_id}] Phase 2: Starting parallel LLM validation (Anthropic-style)...")

                try:
                    # Get context for validation
                    combined_context = ""
                    if deepwiki_context:
                        combined_context += "Project context:\n" + deepwiki_context[:2000] + "\n\n"

                    validation_kwargs = {}
                    if x_scan_type == "3" and x_scan_id:
                        validation_kwargs = {
                            "agentic_config": AgenticValidationConfig(
                                max_tool_calls_per_finding=AGENTIC_TIER3_MAX_TOOL_CALLS_PER_FINDING,
                                max_total_tool_calls_per_scan=AGENTIC_TIER3_MAX_TOOL_CALLS_PER_SCAN,
                                agentic_confidence_ceiling=AGENTIC_CONFIDENCE_CEILING,
                            ),
                            "scan_id": x_scan_id,
                            "file_store": _redis_get_json(f"{x_scan_id}:file_store", default={}) or {},
                            "redis_client": redis_client,
                        }
                        # Set logger so agentic tool_call/tool_result are pushed to log server
                        set_logger(AgentLogger(x_scan_id))
                    try:
                        # Run two-phase validation
                        phase2_kept, phase2_summary = await apply_two_phase_validation(
                            session=app.state.session,
                            findings=phase1_filtered,
                            filename=scan_req.filename,
                            file_content=scan_req.content,
                            context_info=combined_context,
                            confidence_threshold=PHASE2_CONFIDENCE_THRESHOLD,
                            **validation_kwargs,
                        )

                        # Update final result
                        if not phase2_kept:
                            final_result["status"] = "SAFE"
                            final_result["findings"] = []
                            final_result["_filter_note"] = (
                                f"All findings filtered in Phase 2 (confidence < {PHASE2_CONFIDENCE_THRESHOLD})"
                            )
                            logger.info(f"[{x_scan_id}] Phase 2: All findings filtered by parallel validation")
                        else:
                            final_result["findings"] = phase2_kept
                            final_result["_two_phase_summary"] = {
                                "phase1": {
                                    "original_count": len(original_findings),
                                    "passed": len(phase1_filtered),
                                    "excluded": phase1_excluded,
                                },
                                "phase2": phase2_summary,
                            }
                            final_result["_total_filtered"] = len(original_findings) - len(phase2_kept)
                            logger.info(f"[{x_scan_id}] Phase 2 complete: Kept {len(phase2_kept)}/{len(phase1_filtered)} findings")
                            logger.info(f"[{x_scan_id}] Overall: {len(phase2_kept)}/{len(original_findings)} findings after both phases")
                    finally:
                        if x_scan_type == "3" and x_scan_id:
                            clear_logger()

                except Exception as e:
                    logger.error(f"[{x_scan_id}] Phase 2 validation failed: {e}")
                    # Fall back to Phase 1 results
                    final_result["findings"] = phase1_filtered
                    final_result["_filter_note"] = f"Phase 2 failed, using Phase 1 results: {str(e)}"
            else:
                # Phase 1 filtered everything
                final_result["status"] = "SAFE"
                final_result["findings"] = []
                final_result["_filter_note"] = "All findings filtered in Phase 1 (hard exclusions)"

    # --- NEW: Post-Scan Validation (Layer 4) ---
    if final_result.get("status") == "VULNERABLE" and final_result.get("findings"):
        logger.info(f"[{x_scan_id}] Running post-scan validation...")

        # 1. SkepticPass for high-severity findings (optional, configurable)
        skeptic_stats = {"total": 0, "validated": 0, "unvalidated": 0, "skeptic_failed": 0, "skipped_agent_reviewed": 0}

        def should_run_skeptic_pass(finding: Dict[str, Any]) -> bool:
            """Return False for agent findings already skeptic-reviewed, unless confidence drifted."""
            if not finding.get("_skeptic_reviewed"):
                return True
            # Re-review if confidence_score drifted more than 2.0 from agent pipeline value
            agent_conf = finding.get("_skeptic_confidence", 0)
            current_conf = finding.get("confidence_score", 0)
            try:
                drift = float(agent_conf) - float(current_conf)
            except (TypeError, ValueError):
                return True  # can't compare, be safe and re-review
            if drift > 2.0:
                logger.info(
                    f"[{x_scan_id}] Re-reviewing agent finding (confidence drifted "
                    f"{agent_conf} -> {current_conf}, delta={drift:.1f})"
                )
                return True
            return False

        try:
            if SKEPTIC_PASS_ENABLED:
                skeptic = SkepticPass(scan_id=x_scan_id, redis_client=redis_client if REDIS_AVAILABLE else None)
                semaphore = asyncio.Semaphore(SKEPTIC_MAX_PARALLEL)
                findings_list = final_result["findings"]
                # Index -> finding for high-severity (need skeptic); others get validated inline
                high_severity_indices = []
                for i, finding in enumerate(findings_list):
                    if finding.get("cvss_score", 0) >= SKEPTIC_CVSS_THRESHOLD:
                        if not should_run_skeptic_pass(finding):
                            # Already reviewed by agent SkepticAgent — skip
                            finding["skeptic_passed"] = True
                            finding["skeptic_note"] = "Skipped: already reviewed by agent SkepticAgent"
                            finding["validation_status"] = "validated"
                            skeptic_stats["skipped_agent_reviewed"] += 1
                            continue
                        if not finding.get("filename") and not finding.get("file"):
                            finding["filename"] = scan_req.filename
                        high_severity_indices.append(i)
                    else:
                        finding["skeptic_passed"] = True
                        finding["skeptic_note"] = None
                        finding["validation_status"] = "validated"

                async def run_skeptic_for_finding(idx: int):
                    finding = findings_list[idx]
                    ctx, _ = get_code_context_and_fingerprint(
                        scan_req.content,
                        scan_req.filename,
                        finding.get("line", 1),
                        finding.get("vulnerable_code", ""),
                    )
                    try:
                        async with semaphore:
                            return idx, await skeptic.run(
                                finding=finding,
                                code_context=ctx,
                                sanitizer_registry=sanitizer_registry,
                                session=session,
                            )
                    except Exception as e:
                        logger.error(f"[{x_scan_id}] SkepticPass task failed for finding {idx}: {e}")
                        finding["validation_status"] = "unvalidated"
                        finding["skeptic_note"] = f"SkepticPass error: {str(e)}"
                        finding["skeptic_passed"] = True  # fail-open
                        return idx, finding

                if high_severity_indices:
                    skeptic_stats["total"] = len(high_severity_indices)
                    tasks = [run_skeptic_for_finding(i) for i in high_severity_indices]
                    results = await asyncio.gather(*tasks)
                    result_by_idx = {}
                    for idx, finding in results:
                        result_by_idx[idx] = finding
                        status = finding.get("validation_status", "unvalidated")
                        if status == "validated":
                            skeptic_stats["validated"] += 1
                        elif status == "skeptic_failed":
                            skeptic_stats["skeptic_failed"] += 1
                        else:
                            skeptic_stats["unvalidated"] += 1
                else:
                    result_by_idx = {}

                findings_with_skeptic = []
                for i, finding in enumerate(findings_list):
                    findings_with_skeptic.append(result_by_idx.get(i, finding))
                final_result["findings"] = findings_with_skeptic
                logger.info(
                    f"[{x_scan_id}] ✅ SkepticPass completed successfully: "
                    f"{skeptic_stats['total']} high-severity findings reviewed, "
                    f"{skeptic_stats['validated']} validated, "
                    f"{skeptic_stats['skeptic_failed']} flagged, "
                    f"{skeptic_stats['unvalidated']} unvalidated"
                )
            else:
                # SkepticPass disabled: mark all findings as validated so downstream is consistent
                for finding in final_result["findings"]:
                    finding["skeptic_passed"] = True
                    finding["skeptic_note"] = None
                    finding["validation_status"] = "validated"
                logger.info(f"[{x_scan_id}] SkepticPass disabled (SKEPTIC_PASS_ENABLED=false), all findings marked validated")
            final_result["_skeptic_stats"] = skeptic_stats
        except Exception as e:
            logger.error(f"[{x_scan_id}] SkepticPass failed: {e}")
            logger.error(f"[{x_scan_id}] SkepticPass traceback: {traceback.format_exc()}")
            # Mark all high-severity findings as unvalidated
            for finding in final_result["findings"]:
                if finding.get("cvss_score", 0) >= SKEPTIC_CVSS_THRESHOLD:
                    finding["validation_status"] = "unvalidated"
                    finding["skeptic_note"] = f"SkepticPass crashed: {str(e)}"

        # 2. Multi-signal confidence scoring
        try:
            scorer = MultiSignalConfidenceScorer()
            final_result["findings"] = scorer.score_all(final_result["findings"])
            logger.info(f"[{x_scan_id}] Confidence scoring complete")
        except Exception as e:
            logger.error(f"[{x_scan_id}] Confidence scoring failed: {e}")

    final_result["scan_type"] = x_scan_type
    # Merge hard rule findings with AI findings for Tier 2/3
    if hard_rule_findings:
        if final_result.get("status") != "VULNERABLE":
            final_result["status"] = "VULNERABLE"
            final_result["findings"] = []

        # Add hard rule findings to the findings list
        existing_lines = {f.get("line") for f in final_result.get("findings", [])}
        for hr_finding in hard_rule_findings:
            # Avoid duplicates (same line)
            if hr_finding.get("line") not in existing_lines:
                final_result["findings"].append(hr_finding)
                existing_lines.add(hr_finding.get("line"))

        logger.info(f"[{x_scan_id}] Merged {len(hard_rule_findings)} hard-rule findings into Tier {x_scan_type} results")

    if compaction_meta:
        final_result["_compaction"] = compaction_meta

    # Record DeepWiki availability / fallback metadata for this scan so callers
    # can see when project-wide docs were missing.
    deepwiki_meta = {
        "available": bool(deepwiki_context),
        "fallback": "deepwiki+regex_index" if deepwiki_context else "regex_index_only",
    }
    final_result.setdefault("_context", {})["deepwiki"] = deepwiki_meta
    if not deepwiki_context:
        final_result.setdefault("warnings", []).append(
            "DeepWiki documentation unavailable for this scan (regex_index_only). "
            "Cross-file context quality may be reduced. "
            "Re-run indexing with: POST /index_project_deepwiki"
        )

    # --- Coverage metadata: dependency scan visibility ---
    dep_scan_notice = None
    dep_files_checked = 0
    if not DEPENDENCY_SCANNER_ENABLED:
        dep_scan_notice = (
            "Dependency scanning was not run. Known CVEs in package.json / "
            "requirements.txt / go.mod / Cargo.toml were not checked. "
            "Enable DEPENDENCY_SCANNER_ENABLED for SCA coverage."
        )
    else:
        # Count dependency files in this scan (heuristic: count files with dependency-related names)
        _dep_file_names = {"package.json", "requirements.txt", "go.mod", "Cargo.toml", "pyproject.toml", "pom.xml", "build.gradle"}
        if x_scan_id and REDIS_AVAILABLE:
            try:
                _fs = _redis_get_json(f"{x_scan_id}:file_store", default={}) or {}
                dep_files_checked = sum(1 for p in _fs if any(p.endswith(n) for n in _dep_file_names))
            except Exception:
                pass
    final_result["coverage"] = {
        "dependency_scan": {
            "enabled": DEPENDENCY_SCANNER_ENABLED,
            "notice": dep_scan_notice,
            "files_checked": dep_files_checked,
        }
    }

    logger.info(f"[{x_scan_id}] ✅ Tier {x_scan_type} Scan Complete.")
    return final_result


@app.post("/scan")
async def scan_code(
    scan_req: ScanRequest,
    req: Request,
    x_secret: str = Header(None),
    x_scan_id: str = Header(None),
    x_scan_type: str = Header("1"),
):
    if x_secret != WORKER_SECRET:
        raise HTTPException(403, "Invalid secret")
    from backend.worker.core.deepseek_client import (
        reset_request_llm_api_key,
        set_request_llm_api_key_from_request,
    )

    key_token = set_request_llm_api_key_from_request(req)
    try:
        return await scan_code_pipeline(scan_req, req, x_scan_id, x_scan_type)
    finally:
        reset_request_llm_api_key(key_token)


@app.get("/deepwiki_docs", response_class=PlainTextResponse)
async def deepwiki_docs(
    x_secret: str = Header(None),
    x_scan_id: str = Header(None),
):
    if x_secret != WORKER_SECRET:
        raise HTTPException(403, "Invalid secret")
    if not x_scan_id:
        raise HTTPException(400, "Missing x_scan_id")

    md_path = os.path.join(DEEPWIKI_DOCS_DIR, f"{x_scan_id}.md")
    if not os.path.exists(md_path):
        # Optionally: fallback to Redis + build_security_context if file missing
        logger.warning(f"[{x_scan_id}] DeepWiki docs file not found at {md_path}")
        raise HTTPException(404, "DeepWiki docs file not found for this scan_id")

    try:
        with open(md_path, "r", encoding="utf-8") as f:
            docs = f.read()
    except Exception as e:
        logger.error(f"[{x_scan_id}] Failed to read DeepWiki docs file: {e}")
        raise HTTPException(500, "Failed to read DeepWiki docs file")

    return docs or "No DeepWiki security overview available for this project."

@app.get("/health")
def health():
    return {"status": "ok", "redis": REDIS_AVAILABLE, "engine": "Smart Regex (Py3.14)"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002, reload=False)
