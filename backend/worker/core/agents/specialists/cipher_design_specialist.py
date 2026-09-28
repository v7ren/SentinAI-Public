# backend/worker/core/agents/specialists/cipher_design_specialist.py

from __future__ import annotations

import json
import uuid
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


class CipherDesignSpecialist(BaseAgent):
    """
    Dedicated pass for symmetric crypto construction flaws that generic crypto checks often under-report:
    padding-oracle surfaces, ECB/CBC pitfalls, encrypt-without-MAC, and nonce/IV reuse.
    """

    name = "cipher_design_specialist"

    def __init__(self, llm_client: LLMClient):
        super().__init__(name="cipher_design_specialist", llm_client=llm_client)
        self._parse_error: str | None = None

    def run(self, context: AgentContext) -> AgentResult:
        self._parse_error = None
        result = super().run(context)
        if self._parse_error is not None:
            result.errors.append(self._parse_error)
        return result

    def build_prompt(self, context: AgentContext, include_file_contents: bool = True) -> str:
        files_summary = format_context_metadata(context) if not include_file_contents else self._format_files(context.file_contents)
        return f"""
You are analyzing a {context.language} application for symmetric-cipher *construction* and *protocol* flaws
(AES and similar block ciphers, modes, padding, and integrity).

## FILES TO SCAN
{files_summary}

## VULNERABILITY CLASSES (prioritize concrete code evidence)
1. **Padding oracle (CBC / PKCS#7)** — Decryption or token validation branches on padding validity, returns
   different HTTP status/body/timing for "bad padding" vs "bad plaintext", or logs distinguish padding errors.
   Classic: AES-CBC + homegrown "unpad" without constant-time compare or without MAC first.
2. **Unauthenticated encryption** — Confidentiality-only modes (AES-CBC, AES-CTR) protecting tokens, cookies,
   or messages with **no** HMAC / AEAD (AES-GCM, ChaCha20-Poly1305). Especially dangerous when attacker can
   flip ciphertext (bit-flipping / malleability).
3. **ECB for structured data** — AES-ECB on more than one block of repeating or guessable plaintext.
4. **IV / nonce misuse** — Fixed or static IV with CBC; IV reused with the same key; GCM nonce reuse;
   deriving IV from predictable values only; using the same (key, nonce) pair twice in CTR/GCM.
5. **Wrong MAC order or custom "encrypt-then-MAC"** — MAC-then-encrypt, encrypt-then-MAC without covering all
   fields, or comparing MACs with non-constant-time comparison when timing matters.
6. **Homemade crypto** — Custom "AES + XOR + base64" schemes, manual padding, or "secret" permutation of blocks.

## FALSE POSITIVES TO AVOID
- High-level APIs that already use AEAD (e.g. Fernet, NaCl secretbox, `crypto.createCipheriv` with GCM **and**
  documented auth tag verification) unless the code clearly skips tag check or uses unsafe options.
- Hashing (SHA-256) or KDF usage mislabeled as "padding oracle".
- TLS/HTTPS configuration issues (leave those as lower priority unless code disables verification explicitly).

## OUTPUT FORMAT
Return JSON: {{ "findings": [ {{ "file_path", "line_start", "line_end", "function_name", "vulnerability_class", "cwe_id", "owasp_category", "severity", "confidence", "exploitability", "vulnerable_code", "taint_source", "taint_sink", "taint_path", "reasoning", "false_positive_indicators", "remediation_hint" }} ] }}
Use cwe_id such as CWE-327, CWE-326, or CWE-347 where applicable; cite padding-oracle patterns explicitly in reasoning.
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
            self._parse_error = f"CipherDesignSpecialist parse failed: {e}"
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
