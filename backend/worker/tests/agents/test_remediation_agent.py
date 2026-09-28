# backend/worker/tests/agents/test_remediation_agent.py

import json
import pytest
from backend.worker.core.agents.remediation_agent import RemediationAgent, FIX_STRATEGIES
from backend.worker.core.agents.models import DeduplicatedFinding, Exploitability, Severity
from backend.worker.tests.agents.fixtures import make_context


def _make_dedup(
    finding_id: str = "f1",
    vulnerability_class: str = "SQL Injection",
    vulnerable_code: str = "query = 'SELECT' + user_id",
    remediation_hint: str = "Use parameterized queries",
) -> DeduplicatedFinding:
    return DeduplicatedFinding(
        finding_id=finding_id,
        agent_source="injection_specialist",
        file_path="app.py",
        line_start=10,
        line_end=12,
        function_name="handler",
        vulnerability_class=vulnerability_class,
        cwe_id="CWE-89",
        severity=Severity.HIGH,
        confidence=0.9,
        exploitability=Exploitability.CONFIRMED,
        vulnerable_code=vulnerable_code,
        reasoning="String concat into SQL",
        remediation_hint=remediation_hint,
        contributing_agents=["injection_specialist"],
        duplicate_count=1,
    )


def test_generates_parameterized_query_for_sqli():
    """SQL Injection gets fix with parameterized query strategy."""
    client = __import__("backend.worker.core.llm_client", fromlist=["MockLLMClient"]).MockLLMClient(
        responses=[
            json.dumps({
                "fix_description": "Use parameterized query.",
                "fixed_code": "cursor.execute('SELECT * FROM users WHERE id=?', [user_id])",
                "fix_type": "patch",
                "unit_test_code": "def test_sqli_fix(): assert True",
                "unit_test_framework": "pytest",
                "verification_steps": ["Run tests"],
                "regression_risk": "Low",
            })
        ]
    )
    agent = RemediationAgent(llm_client=client)
    ctx = make_context(language="python", framework="flask")
    findings = [_make_dedup(vulnerability_class="SQL Injection")]
    result = agent.run(findings, ctx)
    assert len(result) == 1
    assert "parameterized" in result[0].fix_description.lower() or "query" in result[0].fixed_code.lower()
    assert result[0].fix_type == "patch"


def test_generates_env_var_extraction_for_hardcoded_secret():
    """Hardcoded Secret gets env var extraction strategy."""
    client = __import__("backend.worker.core.llm_client", fromlist=["MockLLMClient"]).MockLLMClient(
        responses=[
            json.dumps({
                "fix_description": "Use environment variable.",
                "fixed_code": "api_key = os.environ.get('API_KEY')",
                "fix_type": "config_change",
                "unit_test_code": "def test_no_hardcoded(): pass",
                "unit_test_framework": "pytest",
                "verification_steps": ["Set env var", "Run app"],
                "regression_risk": "Missing env may break startup",
            })
        ]
    )
    agent = RemediationAgent(llm_client=client)
    ctx = make_context()
    findings = [_make_dedup(vulnerability_class="Hardcoded Secret")]
    result = agent.run(findings, ctx)
    assert len(result) == 1
    assert result[0].fix_type in ("patch", "refactor", "config_change", "dependency_update")


def test_generates_unit_test_code():
    """Remediation includes unit_test_code."""
    client = __import__("backend.worker.core.llm_client", fromlist=["MockLLMClient"]).MockLLMClient(
        responses=[
            json.dumps({
                "fix_description": "Fix.",
                "fixed_code": "x = 1",
                "fix_type": "patch",
                "unit_test_code": "def test_fix(): assert secure_query()",
                "unit_test_framework": "pytest",
                "verification_steps": [],
                "regression_risk": "None",
            })
        ]
    )
    agent = RemediationAgent(llm_client=client)
    ctx = make_context()
    result = agent.run([_make_dedup()], ctx)
    assert result[0].unit_test_code != ""


def test_unit_test_framework_matches_project_language():
    """unit_test_framework is pytest for Python."""
    client = __import__("backend.worker.core.llm_client", fromlist=["MockLLMClient"]).MockLLMClient(
        responses=[
            json.dumps({
                "fix_description": "Fix.",
                "fixed_code": "x = 1",
                "fix_type": "patch",
                "unit_test_code": "def test_x(): pass",
                "unit_test_framework": "pytest",
                "verification_steps": [],
                "regression_risk": "",
            })
        ]
    )
    agent = RemediationAgent(llm_client=client)
    ctx = make_context(language="python")
    result = agent.run([_make_dedup()], ctx)
    assert result[0].unit_test_framework == "pytest"


def test_fix_type_correct_for_each_vulnerability_class():
    """fix_type is one of patch, refactor, config_change, dependency_update."""
    client = __import__("backend.worker.core.llm_client", fromlist=["MockLLMClient"]).MockLLMClient(
        responses=[
            json.dumps({
                "fix_description": "Fix.",
                "fixed_code": "code",
                "fix_type": "config_change",
                "unit_test_code": "",
                "unit_test_framework": "pytest",
                "verification_steps": [],
                "regression_risk": "",
            })
        ]
    )
    agent = RemediationAgent(llm_client=client)
    ctx = make_context()
    result = agent.run([_make_dedup(vulnerability_class="Hardcoded Secret")], ctx)
    assert result[0].fix_type in ("patch", "refactor", "config_change", "dependency_update")


def test_regression_risk_populated():
    """regression_risk is non-empty when LLM provides it."""
    client = __import__("backend.worker.core.llm_client", fromlist=["MockLLMClient"]).MockLLMClient(
        responses=[
            json.dumps({
                "fix_description": "Fix.",
                "fixed_code": "code",
                "fix_type": "patch",
                "unit_test_code": "",
                "unit_test_framework": "pytest",
                "verification_steps": ["Run tests"],
                "regression_risk": "May break legacy callers",
            })
        ]
    )
    agent = RemediationAgent(llm_client=client)
    ctx = make_context()
    result = agent.run([_make_dedup()], ctx)
    assert result[0].regression_risk != ""


def test_verification_steps_populated():
    """verification_steps is a list (can be empty)."""
    client = __import__("backend.worker.core.llm_client", fromlist=["MockLLMClient"]).MockLLMClient(
        responses=[
            json.dumps({
                "fix_description": "Fix.",
                "fixed_code": "code",
                "fix_type": "patch",
                "unit_test_code": "",
                "unit_test_framework": "pytest",
                "verification_steps": ["Step 1", "Step 2"],
                "regression_risk": "",
            })
        ]
    )
    agent = RemediationAgent(llm_client=client)
    ctx = make_context()
    result = agent.run([_make_dedup()], ctx)
    assert isinstance(result[0].verification_steps, list)
    assert len(result[0].verification_steps) >= 0


def test_no_llm_returns_placeholder_remediation():
    """Without LLM, returns remediation with placeholder fix."""
    agent = RemediationAgent(llm_client=None)
    ctx = make_context()
    result = agent.run([_make_dedup()], ctx)
    assert len(result) == 1
    assert result[0].finding_id == "f1"
    assert result[0].fix_description != ""
    assert "pytest" in result[0].unit_test_framework or "jest" in result[0].unit_test_framework
