"""
Unit tests for LogicAnalyst.
"""

import json
import pytest

from backend.worker.core.agents.specialists.logic_analyst import LogicAnalyst
from backend.worker.core.llm_client import MockLLMClient
from backend.worker.tests.agents.fixtures import make_context


def test_detects_idor_missing_ownership_check():
    finding = json.dumps({"findings": [{"file_path": "api/user.py", "line_start": 20, "line_end": 25, "function_name": "get_user", "vulnerability_class": "IDOR", "cwe_id": "CWE-639", "severity": "high", "confidence": 0.9, "exploitability": "confirmed", "vulnerable_code": "User.get(request.args['id'])", "reasoning": "No ownership check", "false_positive_indicators": [], "remediation_hint": "Verify user owns resource"}]})
    client = MockLLMClient(responses=[finding])
    agent = LogicAnalyst(llm_client=client)
    result = agent.run(make_context())
    assert len(result.findings) == 1
    assert result.findings[0].cwe_id == "CWE-639"


def test_detects_race_condition_check_then_act():
    finding = json.dumps({"findings": [{"file_path": "orders/place.py", "line_start": 10, "line_end": 20, "function_name": "place_order", "vulnerability_class": "Race Condition", "cwe_id": "CWE-362", "severity": "medium", "confidence": 0.8, "exploitability": "likely", "vulnerable_code": "if balance >= amount: ... deduct()", "reasoning": "Check-then-act", "false_positive_indicators": [], "remediation_hint": "Use atomic operation"}]})
    client = MockLLMClient(responses=[finding])
    agent = LogicAnalyst(llm_client=client)
    result = agent.run(make_context())
    assert len(result.findings) == 1


def test_detects_mass_assignment_orm():
    finding = json.dumps({"findings": [{"file_path": "models/user.py", "line_start": 5, "line_end": 10, "function_name": "update", "vulnerability_class": "Mass Assignment", "cwe_id": "CWE-915", "severity": "high", "confidence": 0.85, "exploitability": "likely", "vulnerable_code": "User(**request.json)", "reasoning": "All fields from request", "false_positive_indicators": [], "remediation_hint": "Whitelist fields"}]})
    client = MockLLMClient(responses=[finding])
    agent = LogicAnalyst(llm_client=client)
    result = agent.run(make_context())
    assert len(result.findings) == 1


def test_detects_skippable_workflow_step():
    finding = json.dumps({"findings": [{"file_path": "checkout/flow.py", "line_start": 1, "line_end": 30, "function_name": "complete", "vulnerability_class": "Business Logic Bypass", "cwe_id": "CWE-840", "severity": "medium", "confidence": 0.75, "exploitability": "possible", "vulnerable_code": "step = request.json.get('step')", "reasoning": "Step can be skipped", "false_positive_indicators": [], "remediation_hint": "Enforce order"}]})
    client = MockLLMClient(responses=[finding])
    agent = LogicAnalyst(llm_client=client)
    result = agent.run(make_context())
    assert len(result.findings) == 1


def test_does_not_flag_ownership_verified_access():
    client = MockLLMClient(responses=[json.dumps({"findings": []})])
    agent = LogicAnalyst(llm_client=client)
    context = make_context(file_contents={"api/safe.py": "if resource.owner_id != current_user.id: return 403"})
    result = agent.run(context)
    assert len(result.findings) == 0


def test_prompt_includes_business_logic_reasoning_instructions():
    client = MockLLMClient(responses=[json.dumps({"findings": []})])
    agent = LogicAnalyst(llm_client=client)
    agent.run(make_context())
    prompt = client.last_prompt or ""
    assert "ownership check" in prompt.lower()
    assert "workflow" in prompt.lower() or "step" in prompt.lower()
    assert "IDOR" in prompt or "CWE-639" in prompt
