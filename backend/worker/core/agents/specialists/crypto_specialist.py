# backend/worker/core/agents/specialists/crypto_specialist.py

from __future__ import annotations

import json
import math
import uuid
from collections import Counter
from typing import Any

from backend.worker.core.agents.base_agent import BaseAgent, format_files_for_prompt, format_context_metadata
from backend.worker.core.agents.models import (
    AgentContext,
    AgentFinding,
    AgentResult,
    Exploitability,
    Severity,
)
from backend.worker.core.llm_client import LLMClient


SYSTEM_PROMPT = """You are a senior penetration tester specializing in cryptographic weaknesses.
Detect weak algorithms, hardcoded secrets, insufficient randomness, and TLS misconfigurations.
You output ONLY valid JSON. No prose. No markdown."""


class CryptoSpecialist(BaseAgent):
    name = "crypto_specialist"

    def __init__(self, llm_client: LLMClient):
        super().__init__(name="crypto_specialist", llm_client=llm_client)
        self._parse_error: str | None = None

    def run(self, context: AgentContext) -> AgentResult:
        self._parse_error = None
        result = super().run(context)
        if self._parse_error is not None:
            result.errors.append(self._parse_error)
        return result

    def _calculate_entropy(self, text: str) -> float:
        if not text:
            return 0.0
        counts = Counter(text)
        length = len(text)
        return -sum(
            (count / length) * math.log2(count / length)
            for count in counts.values()
        )

    def _is_likely_secret(self, value: str) -> bool:
        placeholders = {"your_api_key", "changeme", "secret", "password", "xxx", "todo"}
        if value.lower() in placeholders:
            return False
        return len(value) > 16 and self._calculate_entropy(value) > 4.5

    def build_prompt(self, context: AgentContext, include_file_contents: bool = True) -> str:
        files_summary = format_context_metadata(context) if not include_file_contents else self._format_files(context.file_contents)
        return f"""
You are analyzing a {context.language} application for cryptographic vulnerabilities.

## FILES TO SCAN (include ALL: source, .env, config.yaml, config.json, settings.py, application.properties, docker-compose.yml, Dockerfile, kubernetes/*.yaml, .github/workflows/*.yml)
{files_summary}

## VULNERABILITY CLASSES
1. Weak algorithms (CWE-327): MD5/SHA1 for security, DES/3DES/RC4, ECB mode
2. Insufficient key length: RSA < 2048, AES < 128, weak ECDSA curves
3. Improper key management (CWE-321): hardcoded keys, keys from predictable values
4. Insufficient randomness (CWE-338): Math.random()/random.random() for security tokens
5. Hardcoded secrets (CWE-798): API keys, DB passwords, private keys in source
6. TLS weaknesses: cert validation disabled, old TLS versions, weak cipher suites

## OUTPUT FORMAT
Return JSON: {{ "findings": [ {{ "file_path", "line_start", "line_end", "function_name", "vulnerability_class", "cwe_id", "severity", "confidence", "exploitability", "vulnerable_code", "reasoning", "false_positive_indicators", "remediation_hint" }} ] }}
If no findings: {{ "findings": [] }}
"""

    def parse_response(self, response: str) -> list[AgentFinding]:
        try:
            data = json.loads(response.strip())
            findings = []
            for raw in data.get("findings", []):
                severity = self._parse_severity(raw.get("severity", "medium"))
                exploitability = self._parse_exploitability(raw.get("exploitability", "possible"))
                finding = AgentFinding(
                    finding_id=str(uuid.uuid4()),
                    agent_source=self.name,
                    file_path=raw.get("file_path", ""),
                    line_start=int(raw.get("line_start", 0)),
                    line_end=int(raw.get("line_end", 0)),
                    function_name=raw.get("function_name", ""),
                    vulnerability_class=raw.get("vulnerability_class", ""),
                    cwe_id=raw.get("cwe_id", ""),
                    owasp_category=raw.get("owasp_category", ""),
                    severity=severity,
                    confidence=self._parse_confidence(raw.get("confidence", 0.5)),
                    exploitability=exploitability,
                    vulnerable_code=raw.get("vulnerable_code", ""),
                    taint_source=raw.get("taint_source"),
                    taint_sink=raw.get("taint_sink"),
                    taint_path=raw.get("taint_path"),
                    chain_id=None,
                    chain_position=None,
                    reasoning=raw.get("reasoning", ""),
                    false_positive_indicators=raw.get("false_positive_indicators", []),
                    remediation_hint=raw.get("remediation_hint", ""),
                )
                findings.append(finding)
            return findings
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self._parse_error = f"CryptoSpecialist parse failed: {e}"
            return []

    def _format_files(self, file_contents: dict[str, str]) -> str:
        return format_files_for_prompt(file_contents)

    def _parse_confidence(self, value: str | int | float | Any) -> float:
        if value is None:
            return 0.5
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return {"high": 0.9, "medium": 0.6, "low": 0.3, "critical": 0.95}.get(
                value.lower(), 0.5
            )
        return 0.5

    def _parse_severity(self, value: str | Any) -> Severity:
        if isinstance(value, Severity):
            return value
        try:
            return Severity(value.lower())
        except ValueError:
            return Severity.MEDIUM

    def _parse_exploitability(self, value: str | Any) -> Exploitability:
        if isinstance(value, Exploitability):
            return value
        try:
            return Exploitability(value.lower())
        except ValueError:
            return Exploitability.POSSIBLE
