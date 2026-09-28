# backend/worker/core/agents/consensus_scorer.py
"""
ConsensusScorer — Adjusts confidence based on multi-agent agreement and context.
"""

from .models import AgentContext, DeduplicatedFinding


class ConsensusScorer:
    """
    Adjusts confidence scores based on:
    - Number of agents that found the same issue (agreement boost)
    - Chain membership (boost)
    - Dead code location (penalty)
    """

    AGENT_COUNT_MULTIPLIERS = {1: 1.0, 2: 1.25, 3: 1.50}
    AGENT_COUNT_MAX_MULTIPLIER = 1.75  # for 4+ agents
    CHAIN_MEMBERSHIP_BOOST = 0.15
    DEAD_CODE_PENALTY = 0.40

    def score(
        self,
        finding: DeduplicatedFinding,
        context: AgentContext,
    ) -> float:
        """
        Compute adjusted confidence in [0, 1].
        """
        base = finding.confidence
        agent_count = len(finding.contributing_agents)

        multiplier = self.AGENT_COUNT_MULTIPLIERS.get(
            agent_count,
            self.AGENT_COUNT_MAX_MULTIPLIER,
        )

        if finding.chain_id:
            multiplier += self.CHAIN_MEMBERSHIP_BOOST

        if self._is_dead_code(finding, context):
            multiplier -= self.DEAD_CODE_PENALTY

        return min(base * multiplier, 1.0)

    def _is_dead_code(self, finding: DeduplicatedFinding, context: AgentContext) -> bool:
        """True if finding location is in dead code map from project indexer."""
        dead_map = getattr(context, "dead_code_map", None) or {}
        region = dead_map.get(finding.file_path)
        if region is None:
            return False
        line_start = getattr(region, "line_start", None) or (region.get("line_start") if isinstance(region, dict) else None)
        line_end = getattr(region, "line_end", None) or (region.get("line_end") if isinstance(region, dict) else None)
        if line_start is None or line_end is None:
            return True  # whole file dead
        return not (finding.line_end < line_start or line_end < finding.line_start)

    def score_all(
        self,
        findings: list[DeduplicatedFinding],
        context: AgentContext,
    ) -> list[DeduplicatedFinding]:
        """Return new list of findings with confidence replaced by consensus score."""
        result = []
        for f in findings:
            new_conf = self.score(f, context)
            result.append(
                DeduplicatedFinding(
                    finding_id=f.finding_id,
                    agent_source=f.agent_source,
                    file_path=f.file_path,
                    line_start=f.line_start,
                    line_end=f.line_end,
                    function_name=f.function_name,
                    vulnerability_class=f.vulnerability_class,
                    cwe_id=f.cwe_id,
                    owasp_category=f.owasp_category,
                    severity=f.severity,
                    confidence=new_conf,
                    exploitability=f.exploitability,
                    vulnerable_code=f.vulnerable_code,
                    taint_source=f.taint_source,
                    taint_sink=f.taint_sink,
                    taint_path=f.taint_path,
                    chain_id=f.chain_id,
                    chain_position=f.chain_position,
                    reasoning=f.reasoning,
                    false_positive_indicators=f.false_positive_indicators,
                    remediation_hint=f.remediation_hint,
                    metadata=f.metadata,
                    contributing_agents=f.contributing_agents,
                    duplicate_count=f.duplicate_count,
                )
            )
        return result
