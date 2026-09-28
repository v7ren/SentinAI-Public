"""
Unit tests for BaseAgent.
"""

import pytest

from backend.worker.core.agents.base_agent import BaseAgent
from backend.worker.core.agents.models import AgentContext, AgentFinding


class MockAgent(BaseAgent):
    """Test agent that implements abstract methods."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt_called = False
        self.response_data = None

    def build_prompt(self, context: AgentContext) -> str:
        """Build mock prompt."""
        self.prompt_called = True
        return f"Prompt for {self.name}\n\nContext: scan_id={context.scan_id}"

    def parse_response(self, response: str) -> list[AgentFinding]:
        """Parse mock response."""
        if self.response_data:
            return [AgentFinding.from_dict(self.response_data)]
        return []


class TestBaseAgent:
    """Tests for BaseAgent class."""

    @pytest.fixture
    def mock_agent(self):
        """Create a MockAgent instance."""
        return MockAgent(name="MockAgent", llm_client=None, max_retries=3, timeout_seconds=120)

    @pytest.fixture
    def mock_context(self):
        """Create an AgentContext for testing."""
        return AgentContext(
            scan_id="test-scan",
            repo_path="/test/repo",
            language="python",
            framework="flask",
        )

    def test_base_agent_init(self):
        """Test BaseAgent initialization."""
        agent = MockAgent(
            name="TestAgent",
            llm_client=None,
            max_retries=5,
            timeout_seconds=300,
        )

        assert agent.name == "TestAgent"
        assert agent.max_retries == 5
        assert agent.timeout_seconds == 300

    def test_build_prompt(self, mock_agent, mock_context):
        """Test that build_prompt is called."""
        prompt = mock_agent.build_prompt(mock_context)

        assert mock_agent.prompt_called is True
        assert "Prompt for MockAgent" in prompt
        assert "test-scan" in prompt

    def test_run_with_mock_response(self, mock_agent, mock_context):
        """Test agent run with mock response."""
        mock_agent.response_data = {
            "finding_id": "test-uuid",
            "agent_source": "MockAgent",
            "file_path": "test.py",
            "line_start": 1,
            "line_end": 10,
            "vulnerability_class": "Test",
        }

        result = mock_agent.run(mock_context)

        assert len(result.findings) == 1
        assert result.findings[0].finding_id == "test-uuid"
        assert result.errors == []

    def test_run_with_empty_findings(self, mock_agent, mock_context):
        """Test agent run with no findings."""
        mock_agent.response_data = None

        result = mock_agent.run(mock_context)

        assert len(result.findings) == 0
        assert result.agent_name == "MockAgent"

    def test_validate_finding_valid(self, mock_agent):
        """Test validate_finding with valid finding."""
        finding = AgentFinding(
            finding_id="test-uuid",
            agent_source="TestAgent",
            file_path="test.py",
            line_start=1,
            line_end=10,
            vulnerability_class="Test",
        )

        assert mock_agent.validate_finding(finding) is True

    def test_validate_finding_missing_required(self, mock_agent):
        """Test validate_finding with missing required field."""
        finding = AgentFinding(
            finding_id="",  # Missing required field
            agent_source="TestAgent",
            file_path="test.py",
            line_start=1,
            line_end=10,
            vulnerability_class="Test",
        )

        assert mock_agent.validate_finding(finding) is False

    def test_adjust_confidence_increase(self, mock_agent):
        """Test adjusting confidence upward."""
        finding = AgentFinding(
            finding_id="test-uuid",
            agent_source="TestAgent",
            file_path="test.py",
            line_start=1,
            line_end=10,
            vulnerability_class="Test",
            confidence=0.5,
        )

        mock_agent.adjust_confidence(finding, 0.3)

        assert finding.confidence == 0.8

    def test_adjust_confidence_clamp_max(self, mock_agent):
        """Test that confidence is clamped at 1.0."""
        finding = AgentFinding(
            finding_id="test-uuid",
            agent_source="TestAgent",
            file_path="test.py",
            line_start=1,
            line_end=10,
            vulnerability_class="Test",
            confidence=0.9,
        )

        mock_agent.adjust_confidence(finding, 0.3)

        assert finding.confidence == 1.0  # Clamped at 1.0

    def test_adjust_confidence_clamp_min(self, mock_agent):
        """Test that confidence is clamped at 0.0."""
        finding = AgentFinding(
            finding_id="test-uuid",
            agent_source="TestAgent",
            file_path="test.py",
            line_start=1,
            line_end=10,
            vulnerability_class="Test",
            confidence=0.1,
        )

        mock_agent.adjust_confidence(finding, -0.3)

        assert finding.confidence == 0.0  # Clamped at 0.0


class TestBaseAgentLLMIntegration:
    """Tests for BaseAgent LLM client integration."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client."""

        class MockClient:
            def complete(self, prompt: str, timeout: int) -> str:
                return '{"finding_id": "mock-uuid", "agent_source": "TestAgent", "file_path": "test.py", "line_start": 1, "line_end": 10, "vulnerability_class": "Mock"}'

        return MockClient()

    @pytest.fixture
    def agent_with_llm(self, mock_llm_client):
        """Create an agent with mock LLM client."""

        class TestAgent(BaseAgent):
            def build_prompt(self, context):
                return "test prompt"

            def parse_response(self, response):
                import json
                data = json.loads(response)
                return [AgentFinding.from_dict(data)]

        return TestAgent(
            name="TestAgent",
            llm_client=mock_llm_client,
            max_retries=0,
            timeout_seconds=30,
        )

    def test_llm_call_success(self, agent_with_llm):
        """Test successful LLM call."""
        context = AgentContext(
            scan_id="test-scan",
            repo_path="/test",
            language="python",
            framework="flask",
        )

        result = agent_with_llm.run(context)

        assert len(result.findings) == 1
        assert result.findings[0].finding_id == "mock-uuid"
        assert result.errors == []

    def test_llm_call_failure_no_retries(self, agent_with_llm):
        """Test LLM call failure with no retries."""

        class FailingClient:
            def complete(self, prompt: str, timeout: int) -> str:
                raise ConnectionError("LLM service unavailable")

        agent_with_llm.llm_client = FailingClient()
        agent_with_llm.max_retries = 0

        context = AgentContext(
            scan_id="test-scan",
            repo_path="/test",
            language="python",
            framework="flask",
        )

        result = agent_with_llm.run(context)

        assert len(result.findings) == 0
        assert len(result.errors) == 1
        assert "FailingClient" in result.errors[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
