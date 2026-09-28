# backend/worker/core/agents/specialists/injection_specialist.py

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


SYSTEM_PROMPT = """You are a senior penetration tester specializing in injection vulnerabilities.
Your job is to find injection flaws in source code with full taint tracing.
You must trace data from its entry point (where it enters the application) to its sink
(where it is used dangerously), even across function call boundaries.
You must check the sanitizer registry before flagging — if a registered sanitizer
is applied between source and sink, do not flag it.
You output ONLY valid JSON. No prose. No markdown. No explanation outside the JSON."""


class InjectionSpecialist(BaseAgent):
    name = "injection_specialist"

    def __init__(self, llm_client: LLMClient):
        super().__init__(name="injection_specialist", llm_client=llm_client)
        self._parse_error: str | None = None

    def run(self, context: AgentContext) -> AgentResult:
        self._parse_error = None
        result = super().run(context)
        if self._parse_error is not None:
            result.errors.append(self._parse_error)
        return result

    def build_prompt(self, context: AgentContext, include_file_contents: bool = True) -> str:
        entry_points_summary = self._format_entry_points(context.entry_points)
        sanitizers_summary = self._format_sanitizers(context.sanitizer_registry)
        files_summary = format_context_metadata(context) if not include_file_contents else self._format_files(context.file_contents)
        call_graph_summary = self._format_call_graph(context.call_graph)

        return f"""
You are analyzing a {context.language} application using the {context.framework} framework
for injection vulnerabilities.

## ENTRY POINTS (where untrusted data enters)
{entry_points_summary}

## REGISTERED SANITIZERS (do NOT flag if these are applied between source and sink)
{sanitizers_summary}

## CALL GRAPH (use this to trace data across function boundaries)
{call_graph_summary}

## SOURCE FILES / CONTEXT
{files_summary}

## YOUR TASK
Find all injection vulnerabilities in the above code. For each finding:
1. Identify the taint source (where untrusted data enters)
2. Trace the data through all function calls using the call graph
3. Identify the taint sink (where the data reaches a dangerous function)
4. Check if any registered sanitizer is applied — if yes, skip this finding
5. Record every step of the taint path

## INJECTION CLASSES TO FIND
- SQL Injection (CWE-89): string concatenation in queries, f-string queries, raw ORM queries
- Command Injection (CWE-78): exec/spawn/system/popen/subprocess with user input, shell=True
- SSTI (CWE-94): render_template_string, compile, eval with user-controlled template strings
- LDAP Injection (CWE-90): LDAP filter construction with unsanitized input
- XPath Injection (CWE-643): XPath query strings built with user input
- NoSQL Injection (CWE-943): MongoDB $where, operator injection via parsed JSON body

## OUTPUT FORMAT
Return a JSON object with this exact structure. No other text.
{{
  "findings": [
    {{
      "file_path": "path/to/file.py",
      "line_start": 42,
      "line_end": 44,
      "function_name": "login",
      "vulnerability_class": "SQL Injection",
      "cwe_id": "CWE-89",
      "owasp_category": "A03:2021",
      "severity": "critical",
      "confidence": 0.95,
      "exploitability": "confirmed",
      "vulnerable_code": "query = 'SELECT * FROM users WHERE id=' + user_id",
      "taint_source": "request.args.get('user_id') in routes/auth.py:15",
      "taint_sink": "db.execute(query) in models/user.py:42",
      "taint_path": [
        "routes/auth.py:15 — user_id = request.args.get('user_id')",
        "routes/auth.py:18 — result = get_user(user_id)",
        "models/user.py:42 — query = 'SELECT...' + user_id"
      ],
      "reasoning": "user_id flows from request.args without sanitization into raw SQL string concatenation",
      "false_positive_indicators": ["no parameterized query used", "no sanitizer in call path"],
      "remediation_hint": "Use parameterized queries: db.execute('SELECT * FROM users WHERE id=?', [user_id])"
    }}
  ]
}}

If no injection vulnerabilities are found, return: {{"findings": []}}
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
                    file_path=raw["file_path"],
                    line_start=int(raw["line_start"]),
                    line_end=int(raw["line_end"]),
                    function_name=raw.get("function_name", "unknown"),
                    vulnerability_class=raw["vulnerability_class"],
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
            self._parse_error = f"InjectionSpecialist parse failed: {e}"
            print(f"[InjectionSpecialist] Failed to parse response: {e}")
            return []

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

    def _format_entry_points(self, entry_points: list) -> str:
        if not entry_points:
            return "No entry points detected."
        lines = []
        for ep in entry_points:
            lines.append(
                f"- {ep.entry_type.upper()} | {ep.file_path}:{ep.line_number} "
                f"| handler: {ep.handler_function} "
                f"| auth_required: {ep.authentication_required}"
            )
        return "\n".join(lines)

    def _format_sanitizers(self, sanitizer_registry: dict) -> str:
        if not sanitizer_registry:
            return "No sanitizers registered."
        lines = []
        for name, info in sanitizer_registry.items():
            lines.append(f"- {name}: {info}")
        return "\n".join(lines)

    def _format_files(self, file_contents: dict[str, str]) -> str:
        return format_files_for_prompt(file_contents)

    def _format_call_graph(self, call_graph: dict) -> str:
        if not call_graph:
            return "No call graph available."
        lines = []
        for caller, callees in call_graph.items():
            if isinstance(callees, list):
                for callee in callees:
                    lines.append(f"  {caller} → {callee}")
            else:
                lines.append(f"  {caller} → {callees}")
        return "\n".join(lines[:200])
