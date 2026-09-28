"""
Unit tests for CryptoSpecialist.
"""

import json
import pytest

from backend.worker.core.agents.specialists.crypto_specialist import CryptoSpecialist
from backend.worker.core.llm_client import MockLLMClient
from backend.worker.tests.agents.fixtures import make_context


def test_detects_md5_for_password_hashing():
    finding = json.dumps({"findings": [{"file_path": "auth/hash.py", "line_start": 1, "line_end": 5, "function_name": "hash_pw", "vulnerability_class": "Weak Algorithm", "cwe_id": "CWE-327", "severity": "high", "confidence": 0.9, "exploitability": "confirmed", "vulnerable_code": "hashlib.md5()", "reasoning": "MD5 for password", "false_positive_indicators": [], "remediation_hint": "Use bcrypt"}]})
    client = MockLLMClient(responses=[finding])
    agent = CryptoSpecialist(llm_client=client)
    result = agent.run(make_context(file_contents={"auth/hash.py": "hashlib.md5()"}))
    assert len(result.findings) == 1
    assert "CWE-327" in result.findings[0].cwe_id


def test_detects_hardcoded_api_key():
    finding = json.dumps({"findings": [{"file_path": "config.py", "line_start": 10, "line_end": 10, "function_name": "", "vulnerability_class": "Hardcoded Secret", "cwe_id": "CWE-798", "severity": "high", "confidence": 0.95, "exploitability": "confirmed", "vulnerable_code": "API_KEY = 'sk-xxx'", "reasoning": "API key in source", "false_positive_indicators": [], "remediation_hint": "Use env var"}]})
    client = MockLLMClient(responses=[finding])
    agent = CryptoSpecialist(llm_client=client)
    result = agent.run(make_context())
    assert len(result.findings) == 1


def test_detects_math_random_for_token_generation():
    finding = json.dumps({"findings": [{"file_path": "utils/token.js", "line_start": 5, "line_end": 7, "function_name": "genToken", "vulnerability_class": "Insufficient Randomness", "cwe_id": "CWE-338", "severity": "medium", "confidence": 0.85, "exploitability": "likely", "vulnerable_code": "Math.random()", "reasoning": "Used for token", "false_positive_indicators": [], "remediation_hint": "Use crypto.randomBytes"}]})
    client = MockLLMClient(responses=[finding])
    agent = CryptoSpecialist(llm_client=client)
    result = agent.run(make_context())
    assert len(result.findings) == 1


def test_detects_disabled_tls_verification():
    finding = json.dumps({"findings": [{"file_path": "http/client.py", "line_start": 20, "line_end": 22, "function_name": "request", "vulnerability_class": "TLS Verification Disabled", "cwe_id": "CWE-295", "severity": "high", "confidence": 0.9, "exploitability": "confirmed", "vulnerable_code": "verify=False", "reasoning": "SSL verify disabled", "false_positive_indicators": [], "remediation_hint": "Enable verify"}]})
    client = MockLLMClient(responses=[finding])
    agent = CryptoSpecialist(llm_client=client)
    result = agent.run(make_context())
    assert len(result.findings) == 1


def test_entropy_calculation_high_entropy_string():
    agent = CryptoSpecialist(llm_client=MockLLMClient())
    h = agent._calculate_entropy("a" * 10 + "b" * 10)
    assert h > 0
    # High entropy: random-looking string
    high = agent._calculate_entropy("x7Kp2mN9qL4vR8sT1wY0zA3bC5dE6fG")
    assert high > 4.0


def test_entropy_calculation_low_entropy_string():
    agent = CryptoSpecialist(llm_client=MockLLMClient())
    low = agent._calculate_entropy("aaaaaaaaaa")
    assert low < 1.0


def test_is_likely_secret_true_for_real_key():
    agent = CryptoSpecialist(llm_client=MockLLMClient())
    assert agent._is_likely_secret("x7Kp2mN9qL4vR8sT1wY0zA3bC5dE6fG") is True


def test_is_likely_secret_false_for_placeholder():
    agent = CryptoSpecialist(llm_client=MockLLMClient())
    assert agent._is_likely_secret("changeme") is False
    assert agent._is_likely_secret("your_api_key") is False


def test_scans_config_files_not_just_source():
    client = MockLLMClient(responses=[json.dumps({"findings": []})])
    agent = CryptoSpecialist(llm_client=client)
    context = make_context(file_contents={
        "app.py": "# code",
        "config.yaml": "api_key: secret",
        ".env": "DB_PASSWORD=xxx",
    })
    agent.run(context)
    assert "config.yaml" in (client.last_prompt or "")
    assert ".env" in (client.last_prompt or "")
