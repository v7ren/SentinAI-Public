# backend/worker/core/llm_client.py
# LLM client abstraction layer.
# Agents never import provider SDKs directly — they always use this module.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import time


@dataclass(slots=True)
class ToolRoundResponse:
    """Response from one round of a tool-calling completion (for agentic loop)."""
    content: str
    tool_calls: list[dict]
    message: dict
    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass(slots=True)
class LLMResponse:
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    latency_ms: int
    cached: bool = False


class LLMClient(ABC):
    def __init__(
        self,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.1,
        timeout_seconds: int = 120,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds

    @abstractmethod
    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        timeout_seconds: int | None = None,
    ) -> LLMResponse:
        """Send completion request. All agents call this."""

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Estimate token count before sending."""


class MinimaxClient(LLMClient):
    """Minimax M2.5 client via OpenRouter. Used for agentic scanning."""

    def __init__(
        self,
        api_key: str,
        model: str = "minimax/minimax-m2.7",
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        import aiohttp

        self._api_key = api_key
        self._base_url = base_url
        super().__init__(model=model)

    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        timeout_seconds: int | None = None,
    ) -> LLMResponse:
        import aiohttp
        import asyncio

        timeout = timeout_seconds if timeout_seconds is not None else self.timeout_seconds

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sentinai.io",
            "X-Title": "SentinAI",
        }

        start = time.time()

        # complete() is sync but is often called from async context (e.g. agent.run() from
        # coordinator.run_scan()). get_running_loop() only works inside a coroutine, so from
        # sync code we cannot safely use run_until_complete on the main loop. Always run the
        # async _make_request in a thread with its own event loop.
        def _run_in_thread():
            return asyncio.run(self._make_request(payload, headers, timeout))

        try:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                response = pool.submit(_run_in_thread).result()
            latency = int((time.time() - start) * 1000)
            return LLMResponse(
                content=response["content"],
                input_tokens=response.get("input_tokens", 0),
                output_tokens=response.get("output_tokens", 0),
                total_tokens=response.get("total_tokens", 0),
                model=self.model,
                latency_ms=latency,
            )
        except Exception as e:
            raise RuntimeError(f"Minimax API error: {e}")

    async def _make_request(
        self, payload: dict, headers: dict, timeout: int
    ) -> dict:
        import aiohttp

        from backend.worker.core.deepseek_client import bridge_healthy, complete, llm_configured

        messages = payload.get("messages") or []
        system_prompt = None
        user_prompt = ""
        for m in messages:
            if m.get("role") == "system":
                system_prompt = m.get("content")
            elif m.get("role") == "user":
                user_prompt = m.get("content") or ""

        async with aiohttp.ClientSession() as session:
            if llm_configured() and await bridge_healthy(session):
                text, model = await complete(
                    session,
                    "agent",
                    system_prompt or "",
                    user_prompt,
                    timeout_seconds=timeout,
                )
                return {
                    "content": text,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "model": model,
                }

            async with session.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"OpenRouter error {resp.status}: {error_text}")

                data = await resp.json()

                if "choices" not in data or not data["choices"]:
                    raise RuntimeError("No choices in response")

                content = data["choices"][0]["message"].get("content", "")
                usage = data.get("usage", {})

                return {
                    "content": content,
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }

    def complete_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict],
        timeout_seconds: int | None = None,
    ) -> ToolRoundResponse:
        """
        One round of completion with tools. For agentic loop: append assistant message
        and tool results to messages and call again until no tool_calls.
        """
        import asyncio
        import concurrent.futures
        import json

        timeout = timeout_seconds if timeout_seconds is not None else self.timeout_seconds
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sentinai.io",
            "X-Title": "SentinAI",
        }

        async def _request() -> dict:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as resp:
                    if resp.status != 200:
                        err = await resp.text()
                        raise RuntimeError(f"OpenRouter error {resp.status}: {err}")
                    data = await resp.json()
            if "choices" not in data or not data["choices"]:
                raise RuntimeError("No choices in response")
            msg = data["choices"][0].get("message", {}) or {}
            content = msg.get("content", "") or ""
            raw_tool_calls = msg.get("tool_calls") or []
            tool_calls = []
            for tc in raw_tool_calls:
                fn = tc.get("function") or {}
                tool_calls.append({
                    "id": tc.get("id", ""),
                    "name": fn.get("name", ""),
                    "arguments": fn.get("arguments", "{}"),
                })
            usage = data.get("usage", {})
            assistant_message = {"role": "assistant", "content": content}
            if raw_tool_calls:
                assistant_message["tool_calls"] = raw_tool_calls
            return {
                "content": content,
                "tool_calls": tool_calls,
                "message": assistant_message,
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            }

        def _run():
            return asyncio.run(_request())

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            out = pool.submit(_run).result()

        return ToolRoundResponse(
            content=out["content"],
            tool_calls=out["tool_calls"],
            message=out["message"],
            input_tokens=out["input_tokens"],
            output_tokens=out["output_tokens"],
            total_tokens=out["total_tokens"],
        )

    def count_tokens(self, text: str) -> int:
        return len(text) // 4


class MockLLMClient(LLMClient):
    """
    Test client. Returns scripted responses. Never calls real LLM.
    Inject this in ALL unit tests.
    """

    def __init__(self, responses: list[str] | None = None):
        super().__init__(model="mock")
        self.responses: list[str] = responses or []
        self.call_count: int = 0
        self.last_prompt: str | None = None
        self.last_system_prompt: str | None = None

    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        timeout_seconds: int | None = None,
    ) -> LLMResponse:
        self.last_prompt = prompt
        self.last_system_prompt = system_prompt
        if self.call_count < len(self.responses):
            content = self.responses[self.call_count]
        else:
            content = '{"findings": []}'
        self.call_count += 1
        return LLMResponse(
            content=content,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            model="mock",
            latency_ms=0,
        )

    def complete_with_tools(
        self,
        messages: list,
        tools: list,
        timeout_seconds: int | None = None,
    ) -> ToolRoundResponse:
        """Mock: return a single round with no tool calls (findings JSON)."""
        content = '{"findings": []}'
        if self.responses and self.call_count < len(self.responses):
            content = self.responses[self.call_count]
        self.call_count += 1
        return ToolRoundResponse(
            content=content,
            tool_calls=[],
            message={"role": "assistant", "content": content},
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        )

    def count_tokens(self, text: str) -> int:
        return len(text) // 4
