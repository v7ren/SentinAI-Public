"""
AgentLogger — Comprehensive logging system for multi-agent pipeline.

Logs every agent's:
- Input (context, prompts, configuration)
- Execution (timing, retries, errors)
- Output (findings, verdicts, scores)
- State transitions (pre-scan → detection → synthesis → validation)

Log files are written to: backend/worker/data/agent_logs/

When LOG_SERVER_URL is set (e.g. http://127.0.0.1:5003), each entry is also
POSTed to the live log server for real-time WebSocket streaming.
"""

import json
import os
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import asdict, is_dataclass


class AgentLogger:
    """
    Centralized logger for all agent activities in the multi-agent pipeline.

    Each scan gets its own log file: agent_log_{scan_id}_{timestamp}.jsonl
    """

    # Windows-compatible path: backend/worker/data/agent_logs/
    LOG_DIR = Path(__file__).parent.parent.parent.parent / "worker" / "data" / "agent_logs"

    def __init__(
        self,
        scan_id: str,
        file_count: int = 0,
        language: str = "",
        framework: str = "",
    ):
        """
        Initialize logger for a specific scan.

        Args:
            scan_id: Unique scan identifier
            file_count: Number of files in this scan (for admin UI)
            language: Project language (e.g. python)
            framework: Project framework (e.g. flask)
        """
        self.scan_id = scan_id
        self.start_time = time.time()
        self.log_id = f"{scan_id}_{int(self.start_time)}"

        # Ensure log directory exists
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

        self.log_file = self.LOG_DIR / f"agent_log_{self.log_id}.jsonl"
        self.summary_file = self.LOG_DIR / f"agent_summary_{self.log_id}.json"

        # In-memory log buffer for quick access
        self.entries: List[Dict[str, Any]] = []

        # Write initial entry (admin UI shows "Scan start · N files")
        self._write_entry({
            "event_type": "scan_start",
            "agent_name": "coordinator",
            "timestamp": datetime.utcnow().isoformat(),
            "scan_id": scan_id,
            "log_version": "1.0",
            "file_count": file_count,
            "language": language or "",
            "framework": framework or "",
        })

    def _serialize_value(self, value: Any) -> Any:
        """Serialize a value to JSON-compatible format."""
        if is_dataclass(value):
            return asdict(value)
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, (str, int, float, bool, type(None))):
            return value
        else:
            return str(value)

    def _push_to_log_server(self, entry: Dict[str, Any]) -> None:
        """Push entry to live log server (fire-and-forget, non-blocking)."""
        try:
            from backend.worker.core.config import LOG_SERVER_URL
            if not LOG_SERVER_URL:
                return
            url = f"{LOG_SERVER_URL}/api/broadcast"
            payload = {
                "event_type": entry.get("event_type", "event"),
                "agent_name": entry.get("agent_name", ""),
                "scan_id": self.scan_id,
                "data": entry,
            }
            if "timestamp" not in payload["data"]:
                payload["data"] = dict(payload["data"], timestamp=datetime.utcnow().isoformat())
            body = json.dumps(payload, default=str).encode("utf-8")
            try:
                from urllib.request import Request, urlopen
                req = Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
                urlopen(req, timeout=2)
            except Exception:
                pass  # Do not fail scan if log server is down
        except Exception:
            pass

    def _write_entry(self, entry: Dict[str, Any]):
        """Write a log entry to file and buffer."""
        # Add sequence number and timestamp
        entry["seq"] = len(self.entries)
        entry["elapsed_ms"] = int((time.time() - self.start_time) * 1000)
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.utcnow().isoformat()

        self.entries.append(entry)

        # Append to JSONL file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")

        # Push to live log server in background (worker and log server are separate processes)
        try:
            from backend.worker.core.config import LOG_SERVER_URL
            if LOG_SERVER_URL:
                threading.Thread(
                    target=self._push_to_log_server,
                    args=(dict(entry),),
                    daemon=True,
                ).start()
        except Exception:
            pass

    def log_agent_start(
        self,
        agent_name: str,
        agent_type: str,
        context: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Log when an agent starts execution.

        Args:
            agent_name: Name of the agent (e.g., "InjectionSpecialist")
            agent_type: Type of agent (e.g., "specialist", "pre-scan", "synthesis")
            context: The AgentContext or relevant context data
            config: Agent-specific configuration
        """
        entry = {
            "event_type": "agent_start",
            "agent_name": agent_name,
            "agent_type": agent_type,
            "context_summary": self._summarize_context(context),
            "context_full": self._serialize_value(context),
            "config": config or {},
        }
        self._write_entry(entry)

    def log_agent_prompt(
        self,
        agent_name: str,
        prompt: str,
        prompt_tokens: Optional[int] = None,
    ):
        """
        Log the prompt sent to the LLM.

        Args:
            agent_name: Name of the agent
            prompt: The full prompt text
            prompt_tokens: Token count (if available)
        """
        entry = {
            "event_type": "agent_prompt",
            "agent_name": agent_name,
            "prompt_length": len(prompt),
            "prompt_tokens": prompt_tokens,
            "prompt_preview": prompt[:2000] + "..." if len(prompt) > 2000 else prompt,
            "prompt_full": prompt,  # Store full prompt for debugging
        }
        self._write_entry(entry)

    def log_agent_response(
        self,
        agent_name: str,
        response: str,
        response_tokens: Optional[int] = None,
        latency_ms: Optional[int] = None,
    ):
        """
        Log the raw response from the LLM.

        Args:
            agent_name: Name of the agent
            response: The raw LLM response
            response_tokens: Token count (if available)
            latency_ms: Response time in milliseconds
        """
        entry = {
            "event_type": "agent_response",
            "agent_name": agent_name,
            "response_length": len(response),
            "response_tokens": response_tokens,
            "latency_ms": latency_ms,
            "response_preview": response[:2000] + "..." if len(response) > 2000 else response,
            "response_full": response,  # Store full response
        }
        self._write_entry(entry)

    def log_agent_findings(
        self,
        agent_name: str,
        findings: List[Dict[str, Any]],
        parsing_errors: Optional[List[str]] = None,
    ):
        """
        Log the findings produced by an agent.

        Args:
            agent_name: Name of the agent
            findings: List of finding dictionaries
            parsing_errors: Any errors during response parsing
        """
        entry = {
            "event_type": "agent_findings",
            "agent_name": agent_name,
            "findings_count": len(findings),
            "findings": [self._serialize_value(f) for f in findings],
            "parsing_errors": parsing_errors or [],
        }
        self._write_entry(entry)

    def log_agent_complete(
        self,
        agent_name: str,
        execution_time_ms: int,
        token_usage: int,
        errors: List[str],
        findings_count: int,
    ):
        """
        Log when an agent completes execution.

        Args:
            agent_name: Name of the agent
            execution_time_ms: Total execution time
            token_usage: Total tokens used
            errors: Any errors encountered
            findings_count: Number of findings produced
        """
        entry = {
            "event_type": "agent_complete",
            "agent_name": agent_name,
            "execution_time_ms": execution_time_ms,
            "token_usage": token_usage,
            "errors": errors,
            "findings_count": findings_count,
        }
        self._write_entry(entry)

    def log_deduplication(
        self,
        input_findings: int,
        output_findings: int,
        duplicates_found: int,
        merged_groups: List[Dict[str, Any]],
    ):
        """
        Log deduplication engine activity.

        Args:
            input_findings: Number of findings before dedup
            output_findings: Number after dedup
            duplicates_found: Number of duplicates identified
            merged_groups: Groups of merged findings
        """
        entry = {
            "event_type": "deduplication",
            "agent_name": "DeduplicationEngine",
            "input_findings": input_findings,
            "output_findings": output_findings,
            "duplicates_found": duplicates_found,
            "deduplication_ratio": round((1 - output_findings / input_findings) * 100, 2) if input_findings > 0 else 0,
            "merged_groups": merged_groups,
        }
        self._write_entry(entry)

    def log_consensus_scoring(
        self,
        findings_scored: int,
        confidence_adjustments: List[Dict[str, Any]],
    ):
        """
        Log consensus scorer activity.

        Args:
            findings_scored: Number of findings processed
            confidence_adjustments: List of adjustments made
        """
        entry = {
            "event_type": "consensus_scoring",
            "agent_name": "ConsensusScorer",
            "findings_scored": findings_scored,
            "adjustments": confidence_adjustments,
        }
        self._write_entry(entry)

    def log_skeptic_review(
        self,
        findings_reviewed: int,
        verdicts: List[Dict[str, Any]],
        rejection_rate: float,
    ):
        """
        Log SkepticAgent review results.

        Args:
            findings_reviewed: Total findings reviewed
            verdicts: List of verdicts (confirmed/downgraded/rejected)
            rejection_rate: Percentage of findings rejected
        """
        entry = {
            "event_type": "skeptic_review",
            "agent_name": "SkepticAgent",
            "findings_reviewed": findings_reviewed,
            "verdicts": verdicts,
            "rejection_rate": rejection_rate,
            "confirmed": sum(1 for v in verdicts if v.get("verdict") == "confirmed"),
            "downgraded": sum(1 for v in verdicts if v.get("verdict") == "downgraded"),
            "rejected": sum(1 for v in verdicts if v.get("verdict") == "rejected"),
        }
        self._write_entry(entry)

    def log_tool_call(self, agent_name: str, tool_name: str, tool_args: Dict[str, Any], filename: str = ""):
        """Log a tool call (e.g. from Tier 3 agentic validation) for live dashboard."""
        entry = {
            "event_type": "tool_call",
            "agent_name": agent_name,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "filename": filename,
        }
        self._write_entry(entry)

    def log_tool_result(self, agent_name: str, tool_name: str, tool_result: Any, filename: str = ""):
        """Log a tool result for live dashboard."""
        result_str = str(tool_result) if not isinstance(tool_result, str) else tool_result
        entry = {
            "event_type": "tool_result",
            "agent_name": agent_name,
            "tool_name": tool_name,
            "result_preview": result_str[:500] + "..." if len(result_str) > 500 else result_str,
            "filename": filename,
        }
        self._write_entry(entry)

    def log_chain_combiner(
        self,
        chains_created: int,
        unchained_findings: int,
        chains: List[Dict[str, Any]],
    ):
        """
        Log ChainCombiner results.

        Args:
            chains_created: Number of vulnerability chains created
            unchained_findings: Findings not part of any chain
            chains: The created chains
        """
        entry = {
            "event_type": "chain_combiner",
            "agent_name": "ChainCombiner",
            "chains_created": chains_created,
            "unchained_findings": unchained_findings,
            "chains": chains,
        }
        self._write_entry(entry)

    def log_attack_paths(
        self,
        paths_simulated: int,
        paths: List[Dict[str, Any]],
    ):
        """
        Log AttackPathSimulator results.

        Args:
            paths_simulated: Number of attack paths generated
            paths: The generated paths
        """
        entry = {
            "event_type": "attack_paths",
            "agent_name": "AttackPathSimulator",
            "paths_simulated": paths_simulated,
            "paths": paths,
        }
        self._write_entry(entry)

    def log_remediation(
        self,
        remediations_generated: int,
        remediations: List[Dict[str, Any]],
    ):
        """
        Log RemediationAgent results.

        Args:
            remediations_generated: Number of remediations created
            remediations: The remediation plans
        """
        entry = {
            "event_type": "remediation",
            "agent_name": "RemediationAgent",
            "remediations_generated": remediations_generated,
            "remediations": remediations,
        }
        self._write_entry(entry)

    def log_error(
        self,
        agent_name: str,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
    ):
        """
        Log an error during agent execution.

        Args:
            agent_name: Name of the agent (or "system")
            error_type: Type of error
            error_message: Error description
            stack_trace: Full stack trace if available
        """
        entry = {
            "event_type": "error",
            "agent_name": agent_name,
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
        }
        self._write_entry(entry)

    def log_phase_transition(
        self,
        from_phase: str,
        to_phase: str,
        phase_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Log pipeline phase transitions.

        Args:
            from_phase: Previous phase name
            to_phase: New phase name
            phase_data: Additional phase information
        """
        entry = {
            "event_type": "phase_transition",
            "agent_name": "coordinator",
            "from_phase": from_phase,
            "to_phase": to_phase,
            "phase_data": phase_data or {},
        }
        self._write_entry(entry)

    def finalize(self, final_stats: Optional[Dict[str, Any]] = None):
        """
        Finalize logging and write summary.

        Args:
            final_stats: Final scan statistics
        """
        total_time_ms = int((time.time() - self.start_time) * 1000)
        stats = final_stats or {}
        total_findings = stats.get("total_findings", 0)

        # Write final entry (admin UI expects total_findings, total_time_ms)
        self._write_entry({
            "event_type": "scan_complete",
            "agent_name": "coordinator",
            "total_time_ms": total_time_ms,
            "total_findings": total_findings,
            "final_stats": stats,
        })

        # Write summary JSON
        summary = {
            "scan_id": self.scan_id,
            "log_id": self.log_id,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "total_time_ms": total_time_ms,
            "total_entries": len(self.entries),
            "log_file": str(self.log_file),
            "event_counts": self._count_events(),
            "agent_summary": self._summarize_agents(),
            "final_stats": final_stats or {},
        }

        with open(self.summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)

        return summary

    def _summarize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of context for logging."""
        summary = {}

        # Count files
        if "file_contents" in context:
            summary["file_count"] = len(context["file_contents"])

        # Count entry points
        if "entry_points" in context:
            summary["entry_points_count"] = len(context["entry_points"])

        # Count call graph nodes
        if "call_graph" in context:
            summary["call_graph_nodes"] = len(context["call_graph"])

        # Language/framework
        summary["language"] = context.get("language", "unknown")
        summary["framework"] = context.get("framework", "unknown")
        summary["scan_mode"] = context.get("scan_mode", "unknown")

        return summary

    def _count_events(self) -> Dict[str, int]:
        """Count events by type."""
        counts = {}
        for entry in self.entries:
            event_type = entry.get("event_type", "unknown")
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts

    def _summarize_agents(self) -> Dict[str, Dict[str, Any]]:
        """Summarize agent executions."""
        agents = {}

        for entry in self.entries:
            if entry.get("event_type") == "agent_complete":
                agent_name = entry.get("agent_name", "unknown")
                agents[agent_name] = {
                    "execution_time_ms": entry.get("execution_time_ms"),
                    "token_usage": entry.get("token_usage"),
                    "findings_count": entry.get("findings_count"),
                    "errors": entry.get("errors", []),
                }

        return agents

    def get_log_file_path(self) -> str:
        """Get the path to the log file."""
        return str(self.log_file)

    def get_summary_file_path(self) -> str:
        """Get the path to the summary file."""
        return str(self.summary_file)


# Global logger instance (set per-scan)
_current_logger: Optional[AgentLogger] = None


def set_logger(logger: AgentLogger):
    """Set the current global logger."""
    global _current_logger
    _current_logger = logger


def get_logger() -> Optional[AgentLogger]:
    """Get the current global logger."""
    return _current_logger


def clear_logger():
    """Clear the current global logger."""
    global _current_logger
    _current_logger = None


def push_event_to_log_server(
    scan_id: str,
    event_type: str,
    agent_name: str,
    data: Dict[str, Any],
) -> None:
    """
    Push a single event to the log server (fire-and-forget).
    Use from code paths that may not have AgentLogger set (e.g. Tier3 agentic validation during /scan).
    When LOG_SERVER_URL is set, events appear on the admin agent activity page.
    """
    try:
        from backend.worker.core.config import LOG_SERVER_URL
        if not LOG_SERVER_URL:
            return
        entry = dict(data)
        entry.setdefault("timestamp", datetime.utcnow().isoformat())
        payload = {
            "event_type": event_type,
            "agent_name": agent_name,
            "scan_id": scan_id,
            "data": entry,
        }
        body = json.dumps(payload, default=str).encode("utf-8")
        import threading
        def _post():
            try:
                from urllib.request import Request, urlopen
                req = Request(
                    f"{LOG_SERVER_URL}/api/broadcast",
                    data=body,
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                urlopen(req, timeout=2)
            except Exception:
                pass
        threading.Thread(target=_post, daemon=True).start()
    except Exception:
        pass
