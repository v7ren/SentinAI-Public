"""
Unit tests for ReconAgent.
"""

import pytest

from backend.worker.core.agents.models import AgentContext, EntryParameter, EntryPoint
from backend.worker.core.agents.recon_agent import ReconAgent


class TestReconAgent:
    """Tests for ReconAgent class."""

    @pytest.fixture
    def recon_agent(self):
        """Create a ReconAgent instance."""
        return ReconAgent(name="ReconAgent", llm_client=None, max_retries=3, timeout_seconds=120)

    @pytest.fixture
    def mock_context(self):
        """Create an AgentContext for testing."""
        return AgentContext(
            scan_id="test-scan",
            repo_path="/test/repo",
            language="python",
            framework="flask",
            file_contents={
                "routes/api.py": """
from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    return authenticate(username, password)

@app.route('/users/<int:user_id>')
def get_user(user_id):
    return fetch_user(user_id)
""",
            },
        )

    def test_recon_agent_init(self):
        """Test ReconAgent initialization."""
        agent = ReconAgent(name="TestRecon", llm_client=None)
        assert agent.name == "TestRecon"

    def test_build_prompt(self, recon_agent, mock_context):
        """Test prompt generation."""
        prompt = recon_agent.build_prompt(mock_context)

        assert "penetration tester" in prompt.lower()
        assert "entry point" in prompt.lower()
        assert "python" in prompt
        assert "flask" in prompt

    def test_detect_entry_points_from_patterns(self, recon_agent, mock_context):
        """Test pattern-based entry point detection."""
        entry_points = recon_agent.detect_entry_points_from_patterns(mock_context)

        assert len(entry_points) >= 1

    def test_scan_file_for_entry_points(self, recon_agent):
        """Test scanning a file for entry points."""
        content = """
from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    return username
"""

        entry_points = recon_agent._scan_file_for_entry_points(
            "routes/api.py", content, mock_context
        )

        assert len(entry_points) >= 1
        assert entry_points[0].entry_type == "http"
        assert entry_points[0].function_name == "login"

    def test_identify_taint_source(self, recon_agent):
        """Test taint source identification."""
        ep_data = {
            "entry_type": "http",
            "parameters": ["username", "password"],
        }

        source = recon_agent._identify_taint_source(ep_data)

        assert source == "req.username"

    def test_entry_point_with_no_params(self, recon_agent):
        """Test entry point detection with no parameters."""
        ep_data = {
            "entry_type": "http",
            "parameters": [],
        }

        source = recon_agent._identify_taint_source(ep_data)

        assert source == "req.body"


class TestReconAgentEntryPoints:
    """Tests for EntryPoint creation."""

    def test_create_http_entry_point(self):
        """Test creating an HTTP entry point."""
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
        assert ep.authentication_required is False
        assert ep.rate_limited is True

    def test_create_cli_entry_point(self):
        """Test creating a CLI entry point."""
        ep = EntryPoint(
            entry_type="cli",
            file_path="cli/commands.py",
            line_number=10,
            function_name="main",
            handler_function="process_command",
            parameters=["command", "args"],
            authentication_required=False,
            authorization_required=False,
            rate_limited=False,
            framework="click",
        )

        assert ep.entry_type == "cli"
        assert ep.function_name == "main"

    def test_create_webhook_entry_point(self):
        """Test creating a webhook entry point."""
        ep = EntryPoint(
            entry_type="webhook",
            file_path="webhooks/paypal.py",
            line_number=25,
            function_name="handle_webhook",
            handler_function="process_paypal_webhook",
            parameters=["webhook_id", "data"],
            authentication_required=True,
            authorization_required=False,
            rate_limited=True,
            framework="flask",
        )

        assert ep.entry_type == "webhook"
        assert ep.authentication_required is True


class TestReconAgentFrameworkDetection:
    """Tests for framework detection patterns."""

    @pytest.fixture
    def recon_agent(self):
        return ReconAgent(name="ReconAgent", llm_client=None)

    def test_flask_patterns(self, recon_agent):
        """Test Flask route pattern detection."""
        content = '@app.route("/login")'
        matches = recon_agent.FRAMEWORK_PATTERNS["python"]["flask"][0]
        import re

        result = re.search(matches, content, re.IGNORECASE)
        assert result is not None

    def test_express_patterns(self, recon_agent):
        """Test Express route pattern detection."""
        content = "app.get('/login', handler)"
        matches = recon_agent.FRAMEWORK_PATTERNS["javascript"]["express"][0]
        import re

        result = re.search(matches, content, re.IGNORECASE)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
