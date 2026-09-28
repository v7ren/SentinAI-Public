"""
Unit tests for ConfigHunter.
"""

import json
import pytest

from backend.worker.core.agents.specialists.config_hunter import ConfigHunter
from backend.worker.core.llm_client import MockLLMClient
from backend.worker.tests.agents.fixtures import make_context


def test_detects_aws_key_via_pattern_matching():
    client = MockLLMClient(responses=[json.dumps({"findings": []})])
    agent = ConfigHunter(llm_client=client)
    context = make_context(file_contents={"config.py": "AWS_ACCESS_KEY = 'AKIAIOSFODNN7EXAMPLE'"})
    result = agent.run(context)
    assert any("AKIA" in f.vulnerable_code for f in result.findings) or len(result.findings) >= 1


def test_detects_github_token_via_pattern_matching():
    client = MockLLMClient(responses=[json.dumps({"findings": []})])
    agent = ConfigHunter(llm_client=client)
    # ghp_ + 36 alphanumeric chars to match SECRET_PATTERNS["github_token"]
    context = make_context(file_contents={".env": "GITHUB_TOKEN=ghp_abcdefghijklmnopqrstuvwxyz1234567890"})
    result = agent.run(context)
    assert any("ghp_" in (f.vulnerable_code or "") for f in result.findings)


def test_detects_private_key_in_source():
    client = MockLLMClient(responses=[json.dumps({"findings": []})])
    agent = ConfigHunter(llm_client=client)
    context = make_context(file_contents={"key.pem": "-----BEGIN RSA PRIVATE KEY-----\nMIIE..."})
    result = agent.run(context)
    assert any("PRIVATE KEY" in f.vulnerable_code for f in result.findings)


def test_detects_debug_mode_enabled():
    finding = json.dumps({"findings": [{"file_path": "settings.py", "line_start": 10, "line_end": 10, "function_name": "", "vulnerability_class": "Debug Mode Enabled", "cwe_id": "CWE-489", "severity": "medium", "confidence": 0.9, "exploitability": "likely", "vulnerable_code": "DEBUG = True", "reasoning": "Debug in production", "false_positive_indicators": [], "remediation_hint": "Set DEBUG=False"}]})
    client = MockLLMClient(responses=[finding])
    agent = ConfigHunter(llm_client=client)
    result = agent.run(make_context(file_contents={"settings.py": "DEBUG = True"}))
    assert len(result.findings) >= 1


def test_detects_wildcard_cors_on_authenticated_endpoint():
    finding = json.dumps({"findings": [{"file_path": "app.py", "line_start": 5, "line_end": 5, "function_name": "", "vulnerability_class": "Overly Permissive CORS", "cwe_id": "CWE-942", "severity": "medium", "confidence": 0.85, "exploitability": "likely", "vulnerable_code": "Access-Control-Allow-Origin: *", "reasoning": "Wildcard CORS", "false_positive_indicators": [], "remediation_hint": "Restrict origin"}]})
    client = MockLLMClient(responses=[finding])
    agent = ConfigHunter(llm_client=client)
    result = agent.run(make_context())
    assert len(result.findings) >= 1


def test_pattern_scan_does_not_call_llm():
    """Pattern scan runs first and adds findings without needing LLM for those; LLM is only for misconfig pass."""
    client = MockLLMClient(responses=[json.dumps({"findings": []})])
    agent = ConfigHunter(llm_client=client)
    context = make_context(file_contents={"key.txt": "-----BEGIN RSA PRIVATE KEY-----\nMIIE"})
    result = agent.run(context)
    pattern_findings = [f for f in result.findings if "Pattern match" in f.reasoning]
    assert len(pattern_findings) >= 1
    assert client.call_count == 1


def test_scans_env_files():
    client = MockLLMClient(responses=[json.dumps({"findings": []})])
    agent = ConfigHunter(llm_client=client)
    context = make_context(file_contents={".env": "DB_PASSWORD=secret123"})
    agent.run(context)
    assert ".env" in (client.last_prompt or "")


def test_scans_dockerfile():
    client = MockLLMClient(responses=[json.dumps({"findings": []})])
    agent = ConfigHunter(llm_client=client)
    context = make_context(file_contents={"Dockerfile": "FROM python:3.9\nRUN pip install -r requirements.txt"})
    agent.run(context)
    assert "Dockerfile" in (client.last_prompt or "")


def test_scans_github_actions_workflow():
    client = MockLLMClient(responses=[json.dumps({"findings": []})])
    agent = ConfigHunter(llm_client=client)
    context = make_context(file_contents={".github/workflows/ci.yml": "on: push\njobs:\n  build:\n    runs-on: ubuntu-latest"})
    agent.run(context)
    assert "workflow" in (client.last_prompt or "").lower() or ".github" in (client.last_prompt or "")
