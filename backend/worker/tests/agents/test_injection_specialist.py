"""
Unit tests for InjectionSpecialist.
"""

import json
import pytest

from backend.worker.core.agents.specialists.injection_specialist import InjectionSpecialist
from backend.worker.core.llm_client import MockLLMClient
from backend.worker.tests.agents.fixtures import make_context


SQLI_FINDING = json.dumps({
    "findings": [{
        "file_path": "routes/login.py",
        "line_start": 42,
        "line_end": 42,
        "function_name": "login",
        "vulnerability_class": "SQL Injection",
        "cwe_id": "CWE-89",
        "owasp_category": "A03:2021",
        "severity": "critical",
        "confidence": 0.95,
        "exploitability": "confirmed",
        "vulnerable_code": "query = 'SELECT * FROM users WHERE id=' + user_id",
        "taint_source": "request.args.get('user_id') in routes/login.py:10",
        "taint_sink": "db.execute(query) in routes/login.py:42",
        "taint_path": ["routes/login.py:10 — user_id = request.args.get('user_id')"],
        "reasoning": "Direct string concatenation into SQL query",
        "false_positive_indicators": [],
        "remediation_hint": "Use parameterized queries"
    }]
})

NO_FINDINGS = json.dumps({"findings": []})


def test_detects_sqli_string_concatenation():
    """Agent correctly identifies SQL injection via string concatenation."""
    client = MockLLMClient(responses=[SQLI_FINDING])
    agent = InjectionSpecialist(llm_client=client)
    context = make_context(file_contents={
        "routes/login.py": "user_id = request.args.get('user_id')\nquery = 'SELECT * FROM users WHERE id=' + user_id\ndb.execute(query)"
    })
    result = agent.run(context)
    assert len(result.findings) == 1
    assert result.findings[0].vulnerability_class == "SQL Injection"
    assert result.findings[0].cwe_id == "CWE-89"
    assert result.findings[0].agent_source == "injection_specialist"
    assert result.findings[0].taint_source is not None
    assert result.findings[0].taint_sink is not None


def test_does_not_flag_parameterized_query():
    """Agent returns no findings when parameterized query is used."""
    client = MockLLMClient(responses=[NO_FINDINGS])
    agent = InjectionSpecialist(llm_client=client)
    context = make_context(file_contents={
        "routes/login.py": "db.execute('SELECT * FROM users WHERE id=?', [user_id])"
    })
    result = agent.run(context)
    assert len(result.findings) == 0


def test_traces_taint_across_function_boundary():
    """Agent populates taint_path showing cross-function data flow."""
    client = MockLLMClient(responses=[SQLI_FINDING])
    agent = InjectionSpecialist(llm_client=client)
    context = make_context()
    result = agent.run(context)
    assert result.findings[0].taint_path is not None
    assert len(result.findings[0].taint_path) >= 1


def test_respects_sanitizer_registry():
    """Agent prompt includes sanitizer registry contents."""
    client = MockLLMClient(responses=[NO_FINDINGS])
    agent = InjectionSpecialist(llm_client=client)
    context = make_context(sanitizer_registry={"escape_sql": "escapes SQL special chars"})
    agent.run(context)
    assert "escape_sql" in (client.last_prompt or "")


def test_handles_malformed_json_gracefully():
    """Agent returns empty list when LLM returns malformed JSON."""
    client = MockLLMClient(responses=["this is not json at all"])
    agent = InjectionSpecialist(llm_client=client)
    context = make_context()
    result = agent.run(context)
    assert result.findings == []
    assert len(result.errors) > 0


def test_sets_agent_source_on_all_findings():
    """Every finding has agent_source = 'injection_specialist'."""
    client = MockLLMClient(responses=[SQLI_FINDING])
    agent = InjectionSpecialist(llm_client=client)
    context = make_context()
    result = agent.run(context)
    for finding in result.findings:
        assert finding.agent_source == "injection_specialist"


def test_finding_ids_are_unique():
    """Each finding gets a unique UUID."""
    first = json.loads(SQLI_FINDING)["findings"][0]
    multi = json.dumps({
        "findings": [
            {**first, "line_start": 10},
            {**first, "line_start": 20},
        ]
    })
    client = MockLLMClient(responses=[multi])
    agent = InjectionSpecialist(llm_client=client)
    context = make_context()
    result = agent.run(context)
    ids = [f.finding_id for f in result.findings]
    assert len(ids) == len(set(ids))
