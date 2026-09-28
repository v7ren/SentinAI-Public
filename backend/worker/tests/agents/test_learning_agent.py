# backend/worker/tests/agents/test_learning_agent.py

import json
import os
import tempfile
import pytest
from backend.worker.core.agents.learning_agent import (
    FeedbackRecord,
    LearningAgent,
)


def test_records_feedback_to_jsonl():
    """record_feedback appends one line to JSONL."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "feedback.jsonl")
        agent = LearningAgent(feedback_path=path)
        rec = FeedbackRecord(
            finding_id="f1",
            scan_id="s1",
            analyst_verdict="true_positive",
            analyst_notes="Good catch",
            codebase_fingerprint="fp-abc",
            agent_source="injection_specialist",
            vulnerability_class="SQL Injection",
            timestamp="2025-01-01T12:00:00Z",
        )
        agent.record_feedback(rec)
        agent.record_feedback(rec)  # append again
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) == 2
        data = json.loads(lines[0])
        assert data["finding_id"] == "f1"
        assert data["analyst_verdict"] == "true_positive"


def test_feedback_records_are_append_only():
    """Appending does not overwrite previous lines."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "feedback.jsonl")
        agent = LearningAgent(feedback_path=path)
        agent.record_feedback(
            FeedbackRecord("f1", "s1", "fp", "n1", "fp-x", "agent1", "SQL", "t1")
        )
        agent.record_feedback(
            FeedbackRecord("f2", "s1", "tp", "n2", "fp-x", "agent2", "XSS", "t2")
        )
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert "f1" in lines[0]
        assert "f2" in lines[1]


def test_rebuild_patterns_not_called_automatically():
    """rebuild_patterns is only called when explicitly invoked."""
    with tempfile.TemporaryDirectory() as tmp:
        feedback_path = os.path.join(tmp, "feedback.jsonl")
        suppression_path = os.path.join(tmp, "suppression.json")
        calibration_path = os.path.join(tmp, "calibration.json")
        agent = LearningAgent(
            feedback_path=feedback_path,
            suppression_path=suppression_path,
            calibration_path=calibration_path,
        )
        agent.record_feedback(
            FeedbackRecord("f1", "s1", "false_positive", "notes", "finger-1", "inj", "SQL Injection", "t1")
        )
        assert not os.path.isfile(suppression_path)
        agent.rebuild_patterns()
        assert os.path.isfile(suppression_path)


def test_suppression_patterns_returned_for_fingerprint():
    """get_suppression_patterns returns list for known fingerprint after rebuild."""
    with tempfile.TemporaryDirectory() as tmp:
        feedback_path = os.path.join(tmp, "feedback.jsonl")
        suppression_path = os.path.join(tmp, "suppression.json")
        calibration_path = os.path.join(tmp, "calibration.json")
        agent = LearningAgent(
            feedback_path=feedback_path,
            suppression_path=suppression_path,
            calibration_path=calibration_path,
        )
        for _ in range(4):
            agent.record_feedback(
                FeedbackRecord("f", "s1", "false_positive", "n", "my-fp", "injection_specialist", "SQL Injection", "t")
            )
        agent.rebuild_patterns()
        patterns = agent.get_suppression_patterns("my-fp")
        assert isinstance(patterns, list)
        assert len(patterns) >= 1


def test_calibration_factor_returned_for_agent_vuln_combo():
    """get_confidence_calibration returns float (1.0 or 0.9) after rebuild."""
    with tempfile.TemporaryDirectory() as tmp:
        feedback_path = os.path.join(tmp, "feedback.jsonl")
        suppression_path = os.path.join(tmp, "suppression.json")
        calibration_path = os.path.join(tmp, "calibration.json")
        agent = LearningAgent(
            feedback_path=feedback_path,
            suppression_path=suppression_path,
            calibration_path=calibration_path,
        )
        agent.rebuild_patterns()
        factor = agent.get_confidence_calibration("injection_specialist", "SQL Injection")
        assert factor >= 0.0
        assert factor <= 2.0


def test_unknown_fingerprint_returns_empty_suppressions():
    """Unknown fingerprint returns empty list."""
    with tempfile.TemporaryDirectory() as tmp:
        suppression_path = os.path.join(tmp, "suppression.json")
        with open(suppression_path, "w", encoding="utf-8") as f:
            json.dump({"known-fp": ["pattern1"]}, f)
        agent = LearningAgent(
            feedback_path=os.path.join(tmp, "f.jsonl"),
            suppression_path=suppression_path,
            calibration_path=os.path.join(tmp, "c.json"),
        )
        assert agent.get_suppression_patterns("unknown-fp") == []


def test_unknown_agent_vuln_returns_1_0():
    """Unknown agent:vuln_class returns 1.0."""
    with tempfile.TemporaryDirectory() as tmp:
        calibration_path = os.path.join(tmp, "calibration.json")
        with open(calibration_path, "w", encoding="utf-8") as f:
            json.dump({"other:Other": 0.9}, f)
        agent = LearningAgent(
            feedback_path=os.path.join(tmp, "f.jsonl"),
            suppression_path=os.path.join(tmp, "s.json"),
            calibration_path=calibration_path,
        )
        assert agent.get_confidence_calibration("unknown_agent", "Unknown Vuln") == 1.0
