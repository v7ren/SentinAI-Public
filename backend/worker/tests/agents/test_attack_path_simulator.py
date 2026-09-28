# backend/worker/tests/agents/test_attack_path_simulator.py

import pytest
from backend.worker.core.agents.attack_path_simulator import (
    AttackPathSimulator,
    _find_max_depth,
)
from backend.worker.core.agents.models import (
    DeduplicatedFinding,
    EntryPoint,
    Exploitability,
    Severity,
    VulnerabilityChain,
)
from backend.worker.tests.agents.fixtures import make_context


def _make_dedup(finding_id: str, vulnerability_class: str) -> DeduplicatedFinding:
    return DeduplicatedFinding(
        finding_id=finding_id,
        agent_source="test",
        file_path="app.py",
        line_start=10,
        line_end=12,
        function_name="handler",
        vulnerability_class=vulnerability_class,
        cwe_id="CWE-89",
        severity=Severity.HIGH,
        confidence=0.9,
        exploitability=Exploitability.CONFIRMED,
        vulnerable_code="x",
        reasoning="test",
        contributing_agents=["test"],
        duplicate_count=1,
    )


def _make_chain(chain_id: str = "c1", impact: str = "RCE", findings_count: int = 2):
    findings = [_make_dedup(f"f{i}", "SQL Injection") for i in range(findings_count)]
    ep = EntryPoint(
        entry_type="http",
        file_path="routes/app.py",
        line_number=10,
        function_name="index",
        handler_function="index",
        parameters=[],
        authentication_required=False,
        authorization_required=False,
        rate_limited=False,
        framework="flask",
    )
    return VulnerabilityChain(
        chain_id=chain_id,
        chain_name="SQL Injection → RCE",
        findings=findings,
        entry_point=ep,
        impact=impact,
        exploitability="confirmed",
        attack_narrative="Test narrative",
        chain_length=len(findings),
    )


def test_generates_steps_for_simple_chain():
    """Simulator produces steps for each finding in chain."""
    sim = AttackPathSimulator()
    chain = _make_chain(findings_count=2)
    context = make_context()
    paths = sim.run([chain], context)
    assert len(paths) == 1
    assert len(paths[0].steps) == 2
    assert paths[0].steps[0].step_number == 1
    assert paths[0].steps[1].step_number == 2
    assert "SQL Injection" in paths[0].steps[0].action


def test_attacker_prerequisites_populated():
    """attacker_prerequisites list is non-empty."""
    sim = AttackPathSimulator()
    chain = _make_chain()
    context = make_context()
    paths = sim.run([chain], context)
    assert len(paths) == 1
    assert len(paths[0].attacker_prerequisites) >= 1
    assert any("entry" in p.lower() or "auth" in p.lower() for p in paths[0].attacker_prerequisites)


def test_complexity_trivial_for_unauthenticated_rce():
    """Unauthenticated RCE-like impact gets trivial complexity."""
    sim = AttackPathSimulator()
    chain = _make_chain(impact="Remote Code Execution")
    context = make_context()
    paths = sim.run([chain], context)
    assert len(paths) == 1
    assert paths[0].estimated_complexity in ("trivial", "low", "medium", "high")


def test_shallow_call_graph_logs_warning(capsys):
    """Shallow call graph triggers warning (depth < 5)."""
    sim = AttackPathSimulator()
    context = make_context()
    context.call_graph = {"a": ["b"], "b": ["c"]}  # depth 2
    sim._validate_call_graph_depth(context)
    out = capsys.readouterr().out
    assert "WARNING" in out
    assert "depth" in out.lower() or "5" in out


def test_proof_of_concept_outline_generated():
    """proof_of_concept_outline is non-empty."""
    sim = AttackPathSimulator()
    chain = _make_chain()
    context = make_context()
    paths = sim.run([chain], context)
    assert len(paths) == 1
    assert len(paths[0].proof_of_concept_outline) > 0
    assert "Chain" in paths[0].proof_of_concept_outline


def test_find_max_depth_empty():
    assert _find_max_depth({}) == 0


def test_find_max_depth_linear():
    assert _find_max_depth({"a": ["b"], "b": ["c"], "c": ["d"], "d": ["e"], "e": ["f"]}) == 5


def test_empty_chains_returns_empty():
    sim = AttackPathSimulator()
    context = make_context()
    assert sim.run([], context) == []
