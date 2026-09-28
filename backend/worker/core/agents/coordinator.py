"""
AgentCoordinator — Orchestrates multi-agent security analysis.

This is the central orchestrator that coordinates all agents in the pipeline:
1. Pre-scan agents (sequential, enrich context)
2. Specialist agents (parallel, all receive same enriched context)
3. Post-scan synthesis (sequential, order is mandatory)
"""

import asyncio
from typing import Any

from .base_agent import BaseAgent
from .models import AgentContext, AgentFinding, AgentResult, ScanMode
from .agent_logger import get_logger


class AgentCoordinator:
    """
    Coordinates all security analysis agents.

    Execution Order (Mandatory):
    1. Pre-Scan (sequential — each enriches context):
       - ReconAgent → populates entry_points
       - PatternAgent → populates architecture_patterns
       - ThreatModelAgent → populates threat_model

    2. Detection (parallel — all receive same enriched context):
       - InjectionSpecialist
       - AuthSpecialist
       - CryptoSpecialist
       - CipherDesignSpecialist (AES/CBC, padding oracle, unauthenticated encryption, IV/nonce misuse)
       - LogicAnalyst
       - ConfigHunter

    3. Synthesis (sequential — order is mandatory):
       - DeduplicationEngine → clean finding set
       - ChainCombiner → build chains from findings
       - AttackPathSimulator → simulate paths from chains
       - ConsensusScorer → adjust confidence based on agreement

    4. Validation + Output (sequential):
       - SkepticAgent → adversarial review
       - RemediationAgent → fix + test generation
       - Final Report → attack narratives + prioritized findings
    """

    def __init__(
        self,
        recon_agent: BaseAgent,
        pattern_agent: BaseAgent,
        threat_model_agent: BaseAgent,
        specialist_agents: list[BaseAgent],
        post_scan_agents: list[BaseAgent] | None = None,
    ):
        """
        Initialize coordinator with all agents.

        Args:
            recon_agent: Reconnaissance agent for entry point mapping
            pattern_agent: Pattern detection agent for architecture analysis
            threat_model_agent: Threat modeling agent for framework-specific threats
            specialist_agents: List of specialist vulnerability detection agents
            post_scan_agents: Optional post-scan agents (dedup, chain, etc.)
        """
        self.recon_agent = recon_agent
        self.pattern_agent = pattern_agent
        self.threat_model_agent = threat_model_agent
        self.specialist_agents = specialist_agents
        self.post_scan_agents = post_scan_agents or []

    async def run_scan(self, context: AgentContext) -> tuple[AgentResult, AgentContext]:
        """
        Run the complete multi-agent scan pipeline.

        Args:
            context: Initial AgentContext with file contents and scan metadata

        Returns:
            Tuple of (AgentResult with all findings, enriched AgentContext)
        """
        logger = get_logger()

        # Step 1: Pre-scan agents (sequential)
        if logger:
            logger.log_phase_transition("start", "pre-scan", {"context": context.__dict__})
        context = await self._run_pre_scan_agents(context)

        # Step 2: Specialist agents (parallel)
        if logger:
            logger.log_phase_transition("pre-scan", "specialist-detection", {"entry_points": len(context.entry_points)})
        specialist_results = await self._run_specialist_agents_parallel(context)

        # Step 3: Collect and merge all findings
        all_findings = self._merge_specialist_results(specialist_results)

        # Step 4: Post-scan synthesis (sequential)
        if logger:
            logger.log_phase_transition("specialist-detection", "post-scan-synthesis", {"findings_count": len(all_findings)})
        synthesized_result = await self._run_post_scan_synthesis(all_findings, context)

        if logger:
            logger.log_phase_transition("post-scan-synthesis", "complete", {"final_findings": len(synthesized_result.findings)})

        return synthesized_result, context

    async def _run_pre_scan_agents(self, context: AgentContext) -> AgentContext:
        """
        Run pre-scan agents to enrich context.

        Recon and Pattern only need the initial context (file contents, graph, etc.),
        so they run in parallel; ThreatModelAgent runs after both complete.
        """
        recon_task = asyncio.to_thread(self.recon_agent.run, context)
        pattern_task = asyncio.to_thread(self.pattern_agent.run, context)
        recon_out, pattern_result = await asyncio.gather(recon_task, pattern_task)
        _recon_result, entry_points = recon_out
        context.entry_points = entry_points

        if pattern_result.findings:
            pattern_data = pattern_result.findings[0].metadata.get("arch_pattern", {})
            context.architecture_patterns = self._dict_to_arch_pattern(pattern_data)

        threat_result = await asyncio.to_thread(self.threat_model_agent.run, context)
        if threat_result.findings:
            # Extract threat model from findings
            threat_model = self._build_threat_model_from_findings(threat_result.findings)
            context.threat_model = threat_model

        return context

    def _dict_to_arch_pattern(self, data: dict) -> Any:
        """Convert dictionary to ArchPattern object."""
        from .models import ArchPattern

        return ArchPattern(
            pattern_type=data.get("pattern_type", "unknown"),
            middleware_order=data.get("middleware_order", []),
            auth_middleware_files=data.get("auth_middleware_files", []),
            orm_type=data.get("orm_type"),
            template_engine=data.get("template_engine"),
            cors_config=data.get("cors_config"),
            service_layer_files=data.get("service_layer_files", []),
            repository_files=data.get("repository_files", []),
            di_container=data.get("di_container"),
        )

    def _build_threat_model_from_findings(self, findings: list[AgentFinding]) -> Any:
        """Build ThreatModel from agent findings."""
        from .models import ThreatModel, ThreatScenario

        threats = [
            ThreatScenario(
                description=f.finding_id,
                priority=0.7,
                cwe_ids=[f.cwe_id] if f.cwe_id else [],
            )
            for f in findings
        ]

        return ThreatModel(
            stack_summary="Detected Stack",
            high_priority_threats=threats,
            framework_specific_sinks=[],
            framework_specific_sources=[],
            known_cve_patterns=[],
        )

    async def _run_specialist_agents_parallel(
        self, context: AgentContext
    ) -> list[AgentResult]:
        """
        Run all specialist agents in parallel.

        All specialists receive the same enriched context from pre-scan agents.
        agent.run() is synchronous (LLM calls), so we run each in a thread and
        gather so they don't block each other.
        """
        if not self.specialist_agents:
            return []

        # Run each agent.run(context) in a thread so they execute in parallel
        tasks = [asyncio.to_thread(agent.run, context) for agent in self.specialist_agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, AgentResult):
                valid_results.append(result)
            else:
                # Handle exception case
                valid_results.append(
                    AgentResult(
                        agent_name=str(result.__class__.__name__) if hasattr(result, "__class__") else "Unknown",
                        findings=[],
                        errors=[str(result)],
                    )
                )

        return valid_results

    def _merge_specialist_results(self, results: list[AgentResult]) -> list[AgentFinding]:
        """Merge all specialist findings into a single list."""
        all_findings: list[AgentFinding] = []

        for result in results:
            if isinstance(result, AgentResult):
                all_findings.extend(result.findings)

        return all_findings

    async def _run_post_scan_synthesis(
        self, findings: list[AgentFinding], context: AgentContext
    ) -> AgentResult:
        """
        Run post-scan synthesis agents sequentially.

        Order is mandatory:
        1. Deduplication
        2. Chain combination
        3. Attack path simulation
        4. Consensus scoring
        5. Skeptic validation
        6. Remediation
        """
        current_findings = findings

        for agent in self.post_scan_agents:
            result = agent.run(
                AgentContext(
                    scan_id=context.scan_id,
                    repo_path=context.repo_path,
                    language=context.language,
                    framework=context.framework,
                    file_contents=context.file_contents,
                    entry_points=context.entry_points,
                    architecture_patterns=context.architecture_patterns,
                    threat_model=context.threat_model,
                    call_graph=context.call_graph,
                    dependency_map=context.dependency_map,
                    sanitizer_registry=context.sanitizer_registry,
                    dead_code_map=context.dead_code_map,
                )
            )
            # Update findings with processed results
            current_findings = result.findings

        return AgentResult(
            agent_name="Coordinator",
            findings=current_findings,
            metadata={
                "total_specialist_agents": len(self.specialist_agents),
                "pre_scan_agents": ["ReconAgent", "PatternAgent", "ThreatModelAgent"],
                "post_scan_agents": [a.name for a in self.post_scan_agents],
            },
        )

    def create_context_from_indexer(
        self,
        indexer_output: dict,
        repo_path: str,
        language: str,
        framework: str,
        scan_mode: ScanMode = ScanMode.FULL,
    ) -> AgentContext:
        """
        Create AgentContext from existing v3 indexer output.

        Args:
            indexer_output: Output from ProjectIndexer (call_graph, file_symbols, etc.)
            repo_path: Path to the repository being scanned
            language: Programming language (python, javascript, etc.)
            framework: Framework name (flask, express, django, etc.)
            scan_mode: Full or diff scan mode

        Returns:
            AgentContext ready for multi-agent analysis
        """
        context = AgentContext(
            scan_id=indexer_output.get("scan_id", ""),
            repo_path=repo_path,
            language=language,
            framework=framework,
            scan_mode=scan_mode,
            call_graph=indexer_output.get("call_graph", {}),
            dependency_map=indexer_output.get("dependency_map", {}),
            file_contents=indexer_output.get("file_contents", {}),
        )

        return context


class ScanResult:
    """Result of a complete multi-agent scan."""

    def __init__(
        self,
        findings: list[AgentFinding],
        context: AgentContext,
        execution_time_ms: int = 0,
        total_tokens_used: int = 0,
    ):
        self.findings = findings
        self.context = context
        self.execution_time_ms = execution_time_ms
        self.total_tokens_used = total_tokens_used

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "findings_count": len(self.findings),
            "findings": [f.to_dict() for f in self.findings],
            "execution_time_ms": self.execution_time_ms,
            "total_tokens_used": self.total_tokens_used,
            "context": {
                "scan_id": self.context.scan_id,
                "language": self.context.language,
                "framework": self.context.framework,
                "entry_points_count": len(self.context.entry_points),
                "threat_model": self.context.threat_model is not None,
            },
        }
