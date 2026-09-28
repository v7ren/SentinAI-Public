# backend/worker/core/agents/remediation_agent.py
"""
RemediationAgent — For each confirmed finding, generates a specific fix and unit test.
"""

import json
import logging
from typing import Any

from .models import AgentContext, DeduplicatedFinding, Remediation

logger = logging.getLogger(__name__)

FIX_STRATEGIES = {
    "SQL Injection": "Generate parameterized query replacement. Show before/after code.",
    "Command Injection": "Generate subprocess with list args, shell=False. No shell=True.",
    "Hardcoded Secret": "Generate environment variable extraction (os.environ or config).",
    "Weak Cryptography": "Generate algorithm replacement with secure implementation.",
    "Missing Auth": "Generate middleware application at correct chain position.",
    "IDOR": "Generate ownership verification query before data access.",
    "SSTI": "Generate static template with context variables. No user-controlled template string.",
    "Session Fixation": "Generate session.regenerate() or equivalent after login.",
}

SYSTEM_PROMPT = """You are a senior security engineer. For the given vulnerability finding, output a concrete remediation.
Output ONLY valid JSON with this exact structure:
{
  "fix_description": "1-2 sentence plain English description",
  "fixed_code": "code snippet showing the fix (same language as the project)",
  "fix_type": "patch" | "refactor" | "config_change" | "dependency_update",
  "unit_test_code": "a unit test that verifies the fix (use project's test framework)",
  "unit_test_framework": "pytest" | "jest" | "junit" | "unittest" etc.,
  "verification_steps": ["step1", "step2"],
  "regression_risk": "Brief description of what could break"
}"""


class RemediationAgent:
    """
    Generates fix + unit test for each confirmed finding.
    """

    name = "remediation_agent"

    def __init__(self, llm_client: Any | None = None):
        self.llm_client = llm_client

    def run(
        self,
        findings: list[DeduplicatedFinding],
        context: AgentContext,
    ) -> list[Remediation]:
        """For each finding, generate Remediation. Returns list of Remediation."""
        if not findings:
            return []

        language = getattr(context, "language", None) or "python"
        framework = getattr(context, "framework", None) or ""

        results: list[Remediation] = []
        for f in findings:
            strategy = self._strategy_for_class(f.vulnerability_class)
            prompt = self._build_prompt(f, strategy, language, framework)

            if not self.llm_client:
                results.append(
                    Remediation(
                        finding_id=f.finding_id,
                        fix_description=f.remediation_hint or "Apply secure coding practice.",
                        fixed_code="# Fix: " + (f.vulnerable_code or ""),
                        fix_type="patch",
                        unit_test_code="# Unit test placeholder",
                        unit_test_framework="pytest" if "python" in language.lower() else "jest",
                        verification_steps=["Run tests", "Manual verification"],
                        regression_risk="Low",
                    )
                )
                continue

            try:
                resp = self.llm_client.complete(prompt=prompt, system_prompt=SYSTEM_PROMPT)
                text = getattr(resp, "content", resp) if hasattr(resp, "content") else str(resp)
                data = json.loads(self._extract_json(text))
                results.append(
                    Remediation(
                        finding_id=f.finding_id,
                        fix_description=data.get("fix_description", "")[:1000],
                        fixed_code=data.get("fixed_code", "")[:5000],
                        fix_type=data.get("fix_type", "patch"),
                        unit_test_code=data.get("unit_test_code", "")[:5000],
                        unit_test_framework=data.get("unit_test_framework", "pytest"),
                        verification_steps=data.get("verification_steps", []),
                        regression_risk=data.get("regression_risk", "")[:500],
                    )
                )
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.debug("Remediation parse error for %s: %s", f.finding_id, e)
                results.append(
                    Remediation(
                        finding_id=f.finding_id,
                        fix_description=f.remediation_hint or "See remediation hint.",
                        fixed_code=f.vulnerable_code or "",
                        fix_type="patch",
                        unit_test_code="",
                        unit_test_framework="pytest",
                        verification_steps=[],
                        regression_risk="Unknown",
                    )
                )

        return results

    def _strategy_for_class(self, vuln_class: str) -> str:
        for key, strategy in FIX_STRATEGIES.items():
            if key.lower() in (vuln_class or "").lower():
                return strategy
        return "Apply secure coding best practice. Remove or validate user input."

    def _build_prompt(
        self,
        finding: DeduplicatedFinding,
        strategy: str,
        language: str,
        framework: str,
    ) -> str:
        return f"""Vulnerability: {finding.vulnerability_class}
File: {finding.file_path} lines {finding.line_start}-{finding.line_end}
Vulnerable code:
```
{finding.vulnerable_code or "N/A"}
```
Reasoning: {finding.reasoning[:500]}

Strategy: {strategy}

Project: {language}, {framework}.

Output JSON only."""

    def _extract_json(self, text: str) -> str:
        text = text.strip()
        if "```" in text:
            for part in text.split("```"):
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    return part
        return text


def _remediation_agent_run(context: AgentContext, findings: list[DeduplicatedFinding], llm_client: Any | None = None) -> list[Remediation]:
    """Convenience: run RemediationAgent on findings."""
    agent = RemediationAgent(llm_client=llm_client)
    return agent.run(findings, context)
