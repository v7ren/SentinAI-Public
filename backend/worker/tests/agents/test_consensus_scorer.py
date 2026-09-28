# backend/worker/tests/agents/test_consensus_scorer.py

import pytest
from backend.worker.core.agents.consensus_scorer import ConsensusScorer
from backend.worker.core.agents.models import (
    DeduplicatedFinding,
    Exploitability,
    Severity,
)
from backend.worker.tests.agents.fixtures import make_context


def _make_dedup(
    finding_id: str = "f1",
    confidence: float = 0.8,
    contributing_agents: list[str] | None = None,
    chain_id: str | None = None,
    file_path: str = "app.py",
    line_start: int = 10,
    line_end: int = 12,
) -> DeduplicatedFinding:
    return DeduplicatedFinding(
        finding_id=finding_id,
        agent_source="test",
        file_path=file_path,
        line_start=line_start,
        line_end=line_end,
        function_name="h",
        vulnerability_class="SQL Injection",
        cwe_id="CWE-89",
        severity=Severity.HIGH,
        confidence=confidence,
        exploitability=Exploitability.CONFIRMED,
        vulnerable_code="x",
        reasoning="test",
        contributing_agents=contributing_agents or ["test"],
        duplicate_count=len(contributing_agents) if contributing_agents else 1,
        chain_id=chain_id,
    )


def test_single_agent_no_boost():
    """Single agent: multiplier 1.0, score = base."""
    scorer = ConsensusScorer()
    f = _make_dedup(confidence=0.8, contributing_agents=["a"])
    ctx = make_context()
    assert scorer.score(f, ctx) == 0.8


def test_two_agents_25_percent_boost():
    """Two agents: multiplier 1.25."""
    scorer = ConsensusScorer()
    f = _make_dedup(confidence=0.8, contributing_agents=["a", "b"])
    ctx = make_context()
    assert scorer.score(f, ctx) == pytest.approx(0.8 * 1.25, rel=1e-5)
    assert scorer.score(f, ctx) == 1.0  # 0.8 * 1.25 = 1.0


def test_three_agents_50_percent_boost():
    """Three agents: multiplier 1.50."""
    scorer = ConsensusScorer()
    f = _make_dedup(confidence=0.6, contributing_agents=["a", "b", "c"])
    ctx = make_context()
    assert scorer.score(f, ctx) == pytest.approx(0.9, rel=1e-5)


def test_four_agents_75_percent_boost():
    """Four+ agents: multiplier 1.75."""
    scorer = ConsensusScorer()
    f = _make_dedup(confidence=0.5, contributing_agents=["a", "b", "c", "d"])
    ctx = make_context()
    assert scorer.score(f, ctx) == pytest.approx(0.5 * 1.75, rel=1e-5)
    assert scorer.score(f, ctx) == 0.875


def test_chain_membership_adds_boost():
    """chain_id set adds CHAIN_MEMBERSHIP_BOOST."""
    scorer = ConsensusScorer()
    f = _make_dedup(confidence=0.5, contributing_agents=["a"], chain_id="chain-1")
    ctx = make_context()
    # 0.5 * (1.0 + 0.15) = 0.575
    assert scorer.score(f, ctx) == pytest.approx(0.5 * 1.15, rel=1e-5)


def test_dead_code_applies_penalty():
    """Finding in dead code: multiplier reduced by DEAD_CODE_PENALTY."""
    scorer = ConsensusScorer()
    f = _make_dedup(confidence=0.8, file_path="dead.py", line_start=15, line_end=20)
    ctx = make_context()
    from backend.worker.core.agents.models import DeadCodeRegion
    ctx.dead_code_map = {"dead.py": DeadCodeRegion("dead.py", 10, 30, "unreachable")}
    # 0.8 * (1.0 - 0.40) = 0.48
    assert scorer.score(f, ctx) == pytest.approx(0.48, rel=1e-5)


def test_score_capped_at_1_0():
    """Score never exceeds 1.0."""
    scorer = ConsensusScorer()
    f = _make_dedup(confidence=0.9, contributing_agents=["a", "b", "c", "d"], chain_id="c1")
    ctx = make_context()
    s = scorer.score(f, ctx)
    assert s <= 1.0


def test_dead_code_and_chain_combined():
    """Dead code penalty and chain boost both apply."""
    scorer = ConsensusScorer()
    f = _make_dedup(confidence=0.8, contributing_agents=["a", "b"], chain_id="c1")
    ctx = make_context()
    from backend.worker.core.agents.models import DeadCodeRegion
    ctx.dead_code_map = {f.file_path: DeadCodeRegion(f.file_path, 1, 50, "dead")}
    # 0.8 * (1.25 + 0.15 - 0.40) = 0.8 * 1.0 = 0.8
    assert scorer.score(f, ctx) == pytest.approx(0.8, rel=1e-5)


def test_score_all_returns_new_findings_with_updated_confidence():
    """score_all returns list of findings with consensus confidence."""
    scorer = ConsensusScorer()
    f1 = _make_dedup("f1", confidence=0.8, contributing_agents=["a"])
    f2 = _make_dedup("f2", confidence=0.6, contributing_agents=["a", "b"])
    ctx = make_context()
    result = scorer.score_all([f1, f2], ctx)
    assert len(result) == 2
    assert result[0].confidence == 0.8
    assert result[1].confidence == pytest.approx(0.6 * 1.25, rel=1e-5)
