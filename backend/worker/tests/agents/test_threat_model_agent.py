"""
Unit tests for ThreatModelAgent.
"""

import pytest

from backend.worker.core.agents.models import AgentContext, ThreatModel, ThreatScenario
from backend.worker.core.agents.threat_model_agent import ThreatModelAgent


class TestThreatModelAgent:
    """Tests for ThreatModelAgent class."""

    @pytest.fixture
    def threat_agent(self):
        """Create a ThreatModelAgent instance."""
        return ThreatModelAgent(name="ThreatModelAgent", llm_client=None, max_retries=3, timeout_seconds=120)

    @pytest.fixture
    def flask_context(self):
        """Create an AgentContext for Flask app."""
        return AgentContext(
            scan_id="test-scan",
            repo_path="/test/repo",
            language="python",
            framework="flask",
            file_contents={},
        )

    @pytest.fixture
    def express_context(self):
        """Create an AgentContext for Express app."""
        return AgentContext(
            scan_id="test-scan",
            repo_path="/test/repo",
            language="javascript",
            framework="express",
            file_contents={},
        )

    def test_threat_model_agent_init(self):
        """Test ThreatModelAgent initialization."""
        agent = ThreatModelAgent(name="TestThreat", llm_client=None)
        assert agent.name == "TestThreat"

    def test_build_prompt_flask(self, threat_agent, flask_context):
        """Test prompt generation for Flask."""
        prompt = threat_agent.build_prompt(flask_context)

        assert "security architect" in prompt.lower()
        assert "Python/Flask" in prompt
        assert "high-priority" in prompt.lower()

    def test_build_prompt_express(self, threat_agent, express_context):
        """Test prompt generation for Express."""
        prompt = threat_agent.build_prompt(express_context)

        assert "Node.js/Express" in prompt

    def test_generate_threat_model_flask(self, threat_agent, flask_context):
        """Test threat model generation for Flask."""
        threat_model = threat_agent.generate_threat_model(flask_context)

        assert threat_model is not None
        assert threat_model.stack_summary == "Python/Flask"
        assert len(threat_model.high_priority_threats) > 0

    def test_generate_threat_model_express(self, threat_agent, express_context):
        """Test threat model generation for Express."""
        threat_model = threat_agent.generate_threat_model(express_context)

        assert threat_model is not None
        assert threat_model.stack_summary == "Node.js/Express"
        assert len(threat_model.high_priority_threats) > 0

    def test_generate_threat_model_unknown_framework(self, threat_agent):
        """Test threat model generation with unknown framework."""
        context = AgentContext(
            scan_id="test-scan",
            repo_path="/test/repo",
            language="unknown",
            framework="unknown",
            file_contents={},
        )

        threat_model = threat_agent.generate_threat_model(context)

        assert threat_model is None

    def test_get_priority_weights(self, threat_agent, flask_context):
        """Test priority weights calculation."""
        threat_model = ThreatModel(
            stack_summary="Python/Flask",
            high_priority_threats=[
                ThreatScenario(description="SQL injection priority test", priority=0.95, cwe_ids=["CWE-89"]),
            ],
        )
        flask_context.threat_model = threat_model

        weights = threat_agent.get_priority_weights(flask_context)

        assert "SQL Injection" in weights
        assert weights["SQL Injection"] >= 0.9

    def test_analyze_entry_points_for_threats(self, threat_agent):
        """Test entry point threat analysis."""
        from backend.worker.core.agents.models import EntryPoint

        entry_points = [
            EntryPoint(
                entry_type="http",
                file_path="routes/api.py",
                line_number=42,
                function_name="login",
                handler_function="handle_login",
                parameters=["username", "password"],
                authentication_required=False,
                authorization_required=False,
                rate_limited=False,
                framework="flask",
            ),
        ]

        threats = threat_agent.analyze_entry_points_for_threats(
            flask_context, entry_points
        )

        assert len(threats) > 0
        assert any("Unauthenticated" in t.description for t in threats)


class TestThreatModel:
    """Tests for ThreatModel dataclass."""

    def test_create_threat_model(self):
        """Test creating a threat model."""
        model = ThreatModel(
            stack_summary="Python/Flask",
            high_priority_threats=[
                ThreatScenario(
                    description="SQL injection in raw queries",
                    priority=0.9,
                    cwe_ids=["CWE-89"],
                ),
            ],
            framework_specific_sinks=["execute()", "cursor.execute()"],
            framework_specific_sources=["request.args", "request.form"],
            known_cve_patterns=["CVE-2018-1000656"],
        )

        assert model.stack_summary == "Python/Flask"
        assert len(model.high_priority_threats) == 1
        assert model.high_priority_threats[0].description == "SQL injection in raw queries"

    def test_create_empty_threat_model(self):
        """Test creating threat model with empty threats."""
        model = ThreatModel(
            stack_summary="Python/Flask",
            high_priority_threats=[],
            framework_specific_sinks=[],
            framework_specific_sources=[],
            known_cve_patterns=[],
        )

        assert model.stack_summary == "Python/Flask"
        assert len(model.high_priority_threats) == 0


class TestThreatScenario:
    """Tests for ThreatScenario dataclass."""

    def test_create_threat_scenario(self):
        """Test creating a threat scenario."""
        scenario = ThreatScenario(
            description="SQL injection vulnerability",
            priority=0.85,
            cwe_ids=["CWE-89"],
        )

        assert scenario.description == "SQL injection vulnerability"
        assert scenario.priority == 0.85
        assert scenario.cwe_ids == ["CWE-89"]

    def test_create_threat_scenario_no_cwe(self):
        """Test creating threat scenario without CWE IDs."""
        scenario = ThreatScenario(
            description="General security concern",
            priority=0.7,
            cwe_ids=[],
        )

        assert scenario.cwe_ids == []


class TestThreatModelAgentFrameworkThreats:
    """Tests for framework-specific threat patterns."""

    @pytest.fixture
    def threat_agent(self):
        return ThreatModelAgent(name="ThreatModelAgent", llm_client=None)

    def test_flask_threats(self, threat_agent):
        """Test Flask-specific threats are defined."""
        flask_threats = threat_agent.STACK_THREATS["python"]["flask"]

        assert len(flask_threats) > 0
        assert any("SQL" in t.description for t in flask_threats)

    def test_express_threats(self, threat_agent):
        """Test Express-specific threats are defined."""
        express_threats = threat_agent.STACK_THREATS["javascript"]["express"]

        assert len(express_threats) > 0
        assert any("NoSQL" in t.description for t in express_threats)

    def test_spring_threats(self, threat_agent):
        """Test Spring-specific threats are defined."""
        spring_threats = threat_agent.STACK_THREATS["java"]["spring"]

        assert len(spring_threats) > 0
        assert any("SQL" in t.description for t in spring_threats)

    def test_framework_sinks(self, threat_agent):
        """Test framework-specific sinks are defined."""
        sinks = threat_agent.FRAMEWORK_SINKS["python"]["flask"]

        assert "execute()" in sinks

    def test_framework_sources(self, threat_agent):
        """Test framework-specific sources are defined."""
        sources = threat_agent.FRAMEWORK_SOURCES["python"]["flask"]

        assert "request.args" in sources
        assert "request.form" in sources

    def test_cve_patterns(self, threat_agent):
        """Test CVE patterns are defined for frameworks."""
        cves = threat_agent.CVE_PATTERNS["python"]["flask"]

        assert len(cves) > 0
        assert "CVE-2018-1000656" in cves


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
