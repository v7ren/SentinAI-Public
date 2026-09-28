"""
Unit tests for LLM client abstraction.
"""

import pytest

from backend.worker.core.llm_client import LLMResponse, MockLLMClient


class TestMockLLMClient:
    """Tests for MockLLMClient."""

    def test_returns_scripted_responses_in_order(self):
        """MockLLMClient returns scripted responses in order."""
        client = MockLLMClient(responses=['{"findings": [{"id": "1"}]}', '{"findings": [{"id": "2"}]}'])
        r1 = client.complete("prompt1")
        r2 = client.complete("prompt2")
        assert r1.content == '{"findings": [{"id": "1"}]}'
        assert r2.content == '{"findings": [{"id": "2"}]}'

    def test_returns_empty_findings_json_when_responses_exhausted(self):
        """MockLLMClient returns empty findings JSON when responses exhausted."""
        client = MockLLMClient(responses=['{"findings": [{"id": "1"}]}'])
        client.complete("prompt1")
        r2 = client.complete("prompt2")
        assert r2.content == '{"findings": []}'

    def test_records_last_prompt_correctly(self):
        """MockLLMClient records last_prompt correctly."""
        client = MockLLMClient(responses=["ok"])
        client.complete("my prompt here")
        assert client.last_prompt == "my prompt here"
        client.complete("second prompt")
        assert client.last_prompt == "second prompt"

    def test_increments_call_count_correctly(self):
        """MockLLMClient increments call_count correctly."""
        client = MockLLMClient(responses=["a", "b", "c"])
        assert client.call_count == 0
        client.complete("p1")
        assert client.call_count == 1
        client.complete("p2")
        assert client.call_count == 2
        client.complete("p3")
        assert client.call_count == 3
        client.complete("p4")
        assert client.call_count == 4

    def test_records_last_system_prompt(self):
        """MockLLMClient records last_system_prompt when provided."""
        client = MockLLMClient(responses=["ok"])
        client.complete("user prompt", system_prompt="system prompt")
        assert client.last_system_prompt == "system prompt"

    def test_returns_llm_response_type(self):
        """MockLLMClient returns LLMResponse with all fields."""
        client = MockLLMClient(responses=["content"])
        r = client.complete("p")
        assert isinstance(r, LLMResponse)
        assert r.content == "content"
        assert r.input_tokens == 100
        assert r.output_tokens == 50
        assert r.total_tokens == 150
        assert r.model == "mock"
        assert r.latency_ms == 0

    def test_count_tokens(self):
        """MockLLMClient count_tokens returns approximate count."""
        client = MockLLMClient()
        assert client.count_tokens("hello") == 1
        assert client.count_tokens("x" * 40) == 10
