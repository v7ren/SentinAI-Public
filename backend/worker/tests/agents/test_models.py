"""
Unit tests for agent models.
"""

import json
from datetime import datetime

import pytest

from backend.worker.core.agents.models import (
    AgentContext,
    AgentFinding,
    AgentResult,
    ArchPattern,
    EntryParameter,
    EntryPoint,
    Exploitability,
    Severity,
    ThreatModel,
)


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_values(self):
        """Test severity enum values."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"


class TestExploitability:
    """Tests for Exploitability enum."""

    def test_exploitability_values(self):
        """Test exploitability enum values."""
        assert Exploitability.CONFIRMED.value == "confirmed"
        assert Exploitability.LIKELY.value == "likely"
        assert Exploitability.POSSIBLE.value == "possible"
        assert Exploitability.UNLIKELY.value == "unlikely"


class TestEntryPoint:
    """Tests for EntryPoint dataclass."""

    def test_entry_point_creation(self):
        """Test creating an entry point."""
        ep = EntryPoint(
            entry_type="http",
            file_path="routes/api.py",
            line_number=42,
            function_name="login",
            handler_function="handle_login",
            parameters=["username", "password"],
            authentication_required=False,
            authorization_required=False,
            rate_limited=True,
            framework="flask",
        )

        assert ep.entry_type == "http"
        assert ep.file_path == "routes/api.py"
        assert ep.line_number == 42
        assert ep.function_name == "login"
        assert ep.framework == "flask"


class TestEntryParameter:
    """Tests for EntryParameter dataclass."""

    def test_entry_parameter_creation(self):
        """Test creating an entry parameter."""
        param = EntryParameter(
            name="username",
            location="body",
            type_="string",
        )

        assert param.name == "username"
        assert param.location == "body"
        assert param.type_ == "string"


class TestArchPattern:
    """Tests for ArchPattern dataclass."""

    def test_arch_pattern_creation(self):
        """Test creating an architecture pattern."""
        pattern = ArchPattern(
            pattern_type="MVC",
            middleware_order=["cors", "auth", "logging"],
            auth_middleware_files=["middleware/auth.py"],
            orm_type="sqlalchemy",
            template_engine="jinja2",
        )

        assert pattern.pattern_type == "MVC"
        assert pattern.middleware_order == ["cors", "auth", "logging"]
        assert pattern.orm_type == "sqlalchemy"


class TestThreatModel:
    """Tests for ThreatModel dataclass."""

    def test_threat_model_creation(self):
        """Test creating a threat model."""
        threat = ThreatModel(
            stack_summary="Node.js/Express/Sequelize/JWT",
            high_priority_threats=[],
            framework_specific_sinks=["sequelize.query()"],
            framework_specific_sources=["req.body", "req.params"],
        )

        assert threat.stack_summary == "Node.js/Express/Sequelize/JWT"
        assert threat.framework_specific_sinks == ["sequelize.query()"]


class TestAgentFinding:
    """Tests for AgentFinding dataclass."""

    def test_agent_finding_creation(self):
        """Test creating an agent finding."""
        finding = AgentFinding(
            finding_id="test-uuid-123",
            agent_source="InjectionSpecialist",
            file_path="routes/api.py",
            line_start=42,
            line_end=45,
            function_name="login",
            vulnerability_class="SQL Injection",
            cwe_id="CWE-89",
            owasp_category="A03:2021",
            severity=Severity.HIGH,
            confidence=0.85,
            exploitability=Exploitability.LIKELY,
            vulnerable_code="db.query(f'SELECT * FROM users WHERE id={user_id}')",
            taint_source="req.params.user_id",
            taint_sink="db.query()",
            taint_path=["req.params.user_id", "login()", "db.query()"],
            reasoning="User input from URL parameter directly interpolated into SQL query",
            false_positive_indicators=["User input may be sanitized upstream"],
            remediation_hint="Use parameterized query instead of string interpolation",
        )

        assert finding.finding_id == "test-uuid-123"
        assert finding.agent_source == "InjectionSpecialist"
        assert finding.vulnerability_class == "SQL Injection"
        assert finding.confidence == 0.85
        assert finding.severity == Severity.HIGH

    def test_agent_finding_to_dict(self):
        """Test converting AgentFinding to dictionary."""
        finding = AgentFinding(
            finding_id="test-uuid-123",
            agent_source="TestAgent",
            file_path="test.py",
            line_start=1,
            line_end=10,
            vulnerability_class="Test",
            severity=Severity.MEDIUM,
            confidence=0.7,
            exploitability=Exploitability.POSSIBLE,
        )

        finding_dict = finding.to_dict()

        assert finding_dict["finding_id"] == "test-uuid-123"
        assert finding_dict["severity"] == "medium"
        assert finding_dict["exploitability"] == "possible"

    def test_agent_finding_from_dict(self):
        """Test creating AgentFinding from dictionary."""
        data = {
            "finding_id": "test-uuid-123",
            "agent_source": "TestAgent",
            "file_path": "test.py",
            "line_start": 1,
            "line_end": 10,
            "vulnerability_class": "Test",
            "severity": "high",
            "confidence": 0.9,
            "exploitability": "confirmed",
        }

        finding = AgentFinding.from_dict(data)

        assert finding.finding_id == "test-uuid-123"
        assert finding.severity == Severity.HIGH
        assert finding.exploitability == Exploitability.CONFIRMED

    def test_agent_finding_required_fields(self):
        """Test that required fields are validated."""
        # Minimal valid finding
        finding = AgentFinding(
            finding_id="test-uuid",
            agent_source="TestAgent",
            file_path="test.py",
            line_start=1,
            line_end=10,
            vulnerability_class="Test",
        )

        assert finding.finding_id == "test-uuid"
        assert finding.function_name == ""  # Default value


class TestAgentResult:
    """Tests for AgentResult dataclass."""

    def test_agent_result_creation(self):
        """Test creating an agent result."""
        finding = AgentFinding(
            finding_id="test-uuid",
            agent_source="TestAgent",
            file_path="test.py",
            line_start=1,
            line_end=10,
            vulnerability_class="Test",
        )

        result = AgentResult(
            agent_name="TestAgent",
            findings=[finding],
            execution_time_ms=1500,
            token_usage=5000,
            errors=[],
            metadata={"scan_id": "scan-123"},
        )

        assert result.agent_name == "TestAgent"
        assert len(result.findings) == 1
        assert result.execution_time_ms == 1500
        assert result.token_usage == 5000

    def test_agent_result_to_dict(self):
        """Test converting AgentResult to dictionary."""
        result = AgentResult(
            agent_name="TestAgent",
            findings=[],
            execution_time_ms=100,
            token_usage=1000,
        )

        result_dict = result.to_dict()

        assert result_dict["agent_name"] == "TestAgent"
        assert result_dict["execution_time_ms"] == 100
        assert "findings" in result_dict


class TestAgentContext:
    """Tests for AgentContext dataclass."""

    def test_agent_context_default_values(self):
        """Test that AgentContext has correct default values."""
        context = AgentContext(
            scan_id="scan-123",
            repo_path="/path/to/repo",
            language="python",
            framework="flask",
        )

        assert context.scan_id == "scan-123"
        assert context.repo_path == "/path/to/repo"
        assert context.language == "python"
        assert context.framework == "flask"
        assert context.call_graph == {}
        assert context.entry_points == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
