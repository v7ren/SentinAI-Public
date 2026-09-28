"""
Unit tests for PatternAgent.
"""

import pytest

from backend.worker.core.agents.models import AgentContext, ArchPattern, CORSConfig
from backend.worker.core.agents.pattern_agent import PatternAgent


class TestPatternAgent:
    """Tests for PatternAgent class."""

    @pytest.fixture
    def pattern_agent(self):
        """Create a PatternAgent instance."""
        return PatternAgent(name="PatternAgent", llm_client=None, max_retries=3, timeout_seconds=120)

    @pytest.fixture
    def mock_context(self):
        """Create an AgentContext for testing."""
        return AgentContext(
            scan_id="test-scan",
            repo_path="/test/repo",
            language="python",
            framework="flask",
            file_contents={
                "app.py": """
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api')
def api():
    return {}
""",
                "models.py": """
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
""",
            },
        )

    def test_pattern_agent_init(self):
        """Test PatternAgent initialization."""
        agent = PatternAgent(name="TestPattern", llm_client=None)
        assert agent.name == "TestPattern"

    def test_build_prompt(self, pattern_agent, mock_context):
        """Test prompt generation."""
        prompt = pattern_agent.build_prompt(mock_context)

        assert "architecture analyst" in prompt.lower()
        assert "pattern" in prompt.lower()
        assert "python" in prompt
        assert "flask" in prompt

    def test_detect_patterns_from_patterns(self, pattern_agent, mock_context):
        """Test pattern detection from code patterns."""
        pattern = pattern_agent.detect_patterns_from_patterns(mock_context)

        assert pattern is not None
        assert pattern.pattern_type in ["MVC", "unknown"]
        assert pattern.orm_type in ["sqlalchemy", "none", None]

    def test_extract_middleware_order(self, pattern_agent):
        """Test middleware order extraction."""
        context = AgentContext(
            scan_id="test-scan",
            repo_path="/test",
            language="javascript",
            framework="express",
            file_contents={
                "app.js": """
const express = require('express');
const cors = require('cors');
const auth = require('./middleware/auth');

const app = express();
app.use(cors());
app.use(auth);
""",
            },
        )

        middleware_order = pattern_agent.extract_middleware_order(context)

        assert "cors" in middleware_order
        assert "auth" in middleware_order

    def test_extract_middleware_name(self, pattern_agent):
        """Test middleware name extraction from regex match."""
        match_text = "app.use(cors())"
        name = pattern_agent._extract_middleware_name(match_text)

        assert name == "cors"


class TestArchPattern:
    """Tests for ArchPattern dataclass."""

    def test_create_mvc_pattern(self):
        """Test creating an MVC architecture pattern."""
        pattern = ArchPattern(
            pattern_type="MVC",
            middleware_order=["cors", "auth", "logging"],
            auth_middleware_files=["middleware/auth.py"],
            orm_type="sqlalchemy",
            template_engine="jinja2",
            cors_config={
                "allow_origin": "*",
                "allow_methods": ["GET", "POST"],
                "allow_headers": ["Content-Type"],
            },
            service_layer_files=["services/user_service.py"],
            repository_files=["repositories/user_repo.py"],
            di_container=None,
        )

        assert pattern.pattern_type == "MVC"
        assert pattern.middleware_order == ["cors", "auth", "logging"]
        assert pattern.orm_type == "sqlalchemy"


class TestCORSConfig:
    """Tests for CORSConfig helper class."""

    def test_create_default_cors(self):
        """Test creating CORS config with defaults."""
        cors = CORSConfig()

        assert cors.allow_origin == "*"
        assert "GET" in cors.allow_methods
        assert "POST" in cors.allow_methods

    def test_create_custom_cors(self):
        """Test creating CORS config with custom values."""
        cors = CORSConfig(
            allow_origin="https://example.com",
            allow_methods=["GET", "POST"],
        )

        assert cors.allow_origin == "https://example.com"
        assert cors.allow_credentials is False

    def test_from_config(self):
        """Test creating CORSConfig from dictionary."""
        config = {
            "allow_origin": "https://trusted.com",
            "allow_methods": ["GET", "POST", "PUT"],
            "allow_credentials": True,
        }

        cors = CORSConfig.from_config(config)

        assert cors.allow_origin == "https://trusted.com"
        assert cors.allow_credentials is True


class TestPatternAgentFrameworkDetection:
    """Tests for framework detection patterns."""

    @pytest.fixture
    def pattern_agent(self):
        return PatternAgent(name="PatternAgent", llm_client=None)

    def test_flask_detection(self, pattern_agent):
        """Test Flask framework detection."""
        content = "from flask import Flask"
        patterns = pattern_agent.FRAMEWORK_PATTERNS["python"]["flask"]

        import re

        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return

        pytest.fail("Flask not detected")

    def test_fastapi_detection(self, pattern_agent):
        """Test FastAPI framework detection."""
        content = "from fastapi import FastAPI"
        patterns = pattern_agent.FRAMEWORK_PATTERNS["python"]["fastapi"]

        import re

        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return

        pytest.fail("FastAPI not detected")

    def test_express_detection(self, pattern_agent):
        """Test Express framework detection."""
        content = "const express = require('express')"
        patterns = pattern_agent.FRAMEWORK_PATTERNS["javascript"]["express"]

        import re

        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return

        pytest.fail("Express not detected")

    def test_sqlalchemy_detection(self, pattern_agent):
        """Test SQLAlchemy ORM detection."""
        content = "from sqlalchemy import Column"
        patterns = pattern_agent.ORM_PATTERNS["sqlalchemy"]

        import re

        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return

        pytest.fail("SQLAlchemy not detected")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
