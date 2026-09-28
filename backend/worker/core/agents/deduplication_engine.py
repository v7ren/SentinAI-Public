# backend/worker/core/agents/deduplication_engine.py
"""
DeduplicationEngine — Merges duplicate findings from multiple agents.
MUST run before Chain Combiner. Never build chains from duplicate findings.
"""

from dataclasses import dataclass

from .models import AgentFinding, DeduplicatedFinding, Severity, Exploitability


def _finding_to_dedup(f: AgentFinding) -> DeduplicatedFinding:
    """Convert AgentFinding to DeduplicatedFinding with single contributor."""
    sev = f.severity if isinstance(f.severity, Severity) else Severity(f.severity) if isinstance(f.severity, str) else Severity.MEDIUM
    exp = f.exploitability if isinstance(f.exploitability, Exploitability) else Exploitability(f.exploitability) if isinstance(f.exploitability, str) else Exploitability.POSSIBLE
    return DeduplicatedFinding(
        finding_id=f.finding_id,
        agent_source=f.agent_source,
        file_path=f.file_path,
        line_start=f.line_start,
        line_end=f.line_end,
        function_name=f.function_name,
        vulnerability_class=f.vulnerability_class,
        cwe_id=f.cwe_id,
        owasp_category=f.owasp_category,
        severity=sev,
        confidence=f.confidence,
        exploitability=exp,
        vulnerable_code=f.vulnerable_code,
        taint_source=f.taint_source,
        taint_sink=f.taint_sink,
        taint_path=f.taint_path,
        chain_id=f.chain_id,
        chain_position=f.chain_position,
        reasoning=f.reasoning,
        false_positive_indicators=list(f.false_positive_indicators),
        remediation_hint=f.remediation_hint,
        metadata=dict(f.metadata),
        contributing_agents=[f.agent_source],
        duplicate_count=1,
    )


def _lines_overlap(f1: AgentFinding | DeduplicatedFinding, f2: AgentFinding | DeduplicatedFinding) -> bool:
    """True if two findings' line ranges overlap."""
    return not (f1.line_end < f2.line_start or f2.line_end < f1.line_start)


_SEVERITY_ORDER = {
    Severity.CRITICAL: 4,
    Severity.HIGH: 3,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
    Severity.INFO: 0,
}


def _highest_severity(severities: list[Severity]) -> Severity:
    """Return highest severity from list."""
    for s in (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO):
        if s in severities:
            return s
    return Severity.MEDIUM


def _merge(group: list[DeduplicatedFinding]) -> DeduplicatedFinding:
    """
    Merge a group of duplicate findings into one.
    - confidence: max across group
    - taint_path: longest across group
    - false_positive_indicators: union
    - contributing_agents: all unique agent_source
    - severity: highest across group
    """
    if not group:
        raise ValueError("Cannot merge empty group")
    if len(group) == 1:
        return group[0]

    first = group[0]
    all_agents: list[str] = []
    for d in group:
        all_agents.extend(d.contributing_agents)
    contributing_agents = list(dict.fromkeys(all_agents))

    max_conf = max(d.confidence for d in group)
    longest_path = max(((d.taint_path or []) for d in group), key=len)
    fp_union: list[str] = []
    seen_fp: set[str] = set()
    for d in group:
        for x in d.false_positive_indicators or []:
            if x not in seen_fp:
                seen_fp.add(x)
                fp_union.append(x)

    severities = [d.severity for d in group]
    highest_sev = _highest_severity(severities)

    return DeduplicatedFinding(
        finding_id=first.finding_id,
        agent_source=first.agent_source,
        file_path=first.file_path,
        line_start=min(d.line_start for d in group),
        line_end=max(d.line_end for d in group),
        function_name=first.function_name,
        vulnerability_class=first.vulnerability_class,
        cwe_id=first.cwe_id,
        owasp_category=first.owasp_category,
        severity=highest_sev,
        confidence=max_conf,
        exploitability=first.exploitability,
        vulnerable_code=first.vulnerable_code,
        taint_source=first.taint_source,
        taint_sink=first.taint_sink,
        taint_path=longest_path if longest_path else None,
        chain_id=first.chain_id,
        chain_position=first.chain_position,
        reasoning=first.reasoning,
        false_positive_indicators=fp_union,
        remediation_hint=first.remediation_hint,
        metadata=dict(first.metadata),
        contributing_agents=contributing_agents,
        duplicate_count=len(group),
    )


class DeduplicationEngine:
    """
    Merges findings that describe the same underlying vulnerability.
    Rules (in order): exact match (file + overlapping lines + same vuln class), sink match.
    """

    def run(self, findings: list[AgentFinding]) -> list[DeduplicatedFinding]:
        """
        1. Convert all to DeduplicatedFinding.
        2. Group by (file_path, vulnerability_class).
        3. Within each group, merge those with overlapping line ranges.
        4. Optionally merge by same taint_sink across groups (sink match).
        5. Return deduplicated list.
        """
        if not findings:
            return []

        dedup_list = [_finding_to_dedup(f) for f in findings]

        # Group by (file_path, vulnerability_class)
        groups: dict[tuple[str, str], list[DeduplicatedFinding]] = {}
        for d in dedup_list:
            key = (d.file_path, d.vulnerability_class)
            groups.setdefault(key, []).append(d)

        # Within each group, merge overlapping line ranges
        merged: list[DeduplicatedFinding] = []
        for key, group in groups.items():
            used = [False] * len(group)
            for i, a in enumerate(group):
                if used[i]:
                    continue
                cluster = [a]
                used[i] = True
                for j, b in enumerate(group):
                    if i == j or used[j]:
                        continue
                    if _lines_overlap(a, b):
                        cluster.append(b)
                        used[j] = True
                merged.append(_merge(cluster))

        # Sink match: merge findings with same taint_sink
        with_sink = [d for d in merged if (d.taint_sink or "").strip()]
        without_sink = [d for d in merged if not (d.taint_sink or "").strip()]

        sink_groups: dict[str, list[DeduplicatedFinding]] = {}
        for d in with_sink:
            sink = (d.taint_sink or "").strip()
            sink_groups.setdefault(sink, []).append(d)

        final: list[DeduplicatedFinding] = list(without_sink)
        for sink, group in sink_groups.items():
            if len(group) > 1:
                final.append(_merge(group))
            else:
                final.append(group[0])

        return final
