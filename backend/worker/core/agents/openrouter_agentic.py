"""
OpenRouter tool-calling loop — same pattern as Tier 3 validator.
Use this so pipeline agents get tool results back to the LLM (tools in request, tool_calls in response, execute and append, repeat).
When the model returns [TOOL_CALL]...[/TOOL_CALL] in content instead of API tool_calls, we parse and execute those too so tool results are fed back.
Optional callbacks allow the caller to log tool_call/tool_result for the admin dashboard (like Tier3Validator).
"""

import asyncio
import json
import logging
from typing import Callable

import aiohttp

from backend.worker.core.deepseek_client import bridge_healthy, complete, llm_configured

logger = logging.getLogger(__name__)


async def run_openrouter_agentic_loop(
    messages: list[dict],
    tools: list[dict],
    execute_tool: Callable[[str, dict], str],
    *,
    model: str,
    api_key: str,
    api_url: str,
    max_rounds: int = 10,
    timeout_seconds: int = 120,
    parse_text_tool_calls: Callable[[str], list[tuple[str, dict]]] | None = None,
    on_tool_call: Callable[[str, dict], None] | None = None,
    on_tool_result: Callable[[str, dict, str], None] | None = None,
) -> tuple[str, int]:
    """
    Run the same tool-calling loop as the validator: POST to OpenRouter with tools,
    on tool_calls execute via execute_tool(name, args), append assistant + tool messages, repeat.
    If the API returns no tool_calls but content contains [TOOL_CALL]...[/TOOL_CALL], use
    parse_text_tool_calls(content) to get (name, args) list, execute tools, append results as user message, continue.
    Returns (final_content, total_tokens_approx).
    execute_tool is sync (e.g. PipelineToolExecutor.execute); we run it in a thread.
    """
    total_tokens = 0
    last_content = ""
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    if llm_configured():
        async with aiohttp.ClientSession() as bridge_session:
            if await bridge_healthy(bridge_session):
                system_parts = []
                user_parts = []
                for m in messages:
                    role = m.get("role", "user")
                    text = m.get("content") or ""
                    if role == "system":
                        system_parts.append(text)
                    else:
                        user_parts.append(f"[{role}]\n{text}")
                system_prompt = "\n".join(system_parts)
                user_prompt = "\n".join(user_parts)
                user_prompt += (
                    "\n\n[Policy] No shell or file-edit tools. Respond with your final answer as text."
                )
                text, _model = await complete(
                    bridge_session,
                    "agentic",
                    system_prompt,
                    user_prompt,
                    timeout_seconds=timeout_seconds,
                )
                return text, total_tokens

    for round_num in range(max_rounds):
        payload = {
            "model": model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": 0.1,
            "max_tokens": 4096,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sentinai.io",
            "X-Title": "SentinAI",
        }

        data = None
        last_err: Exception | None = None
        for attempt in range(2):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        api_url,
                        json=payload,
                        headers=headers,
                        timeout=timeout,
                    ) as resp:
                        if resp.status != 200:
                            err = await resp.text()
                            raise RuntimeError(f"OpenRouter error {resp.status}: {err[:500] or resp.reason}")
                        data = await resp.json()
                if attempt > 0:
                    logger.info(
                        "OpenRouter request succeeded on attempt %s/2 after retry.",
                        attempt + 1,
                    )
                break
            except (asyncio.TimeoutError, TimeoutError) as e:
                last_err = e
                logger.warning(
                    "OpenRouter request timeout (attempt %s/2, %ss); retrying once.",
                    attempt + 1, timeout_seconds,
                )
                if attempt == 1:
                    raise RuntimeError(f"OpenRouter request timed out after {timeout_seconds}s (2 attempts)") from e
            except Exception as e:
                logger.warning("OpenRouter request failed: %s", e)
                raise RuntimeError(f"OpenRouter request failed: {e!r}") from e

        if data is None:
            raise RuntimeError("OpenRouter returned no data") from last_err

        if "choices" not in data or not data["choices"]:
            raise RuntimeError("OpenRouter returned no choices")

        choice = data["choices"][0]
        message = choice.get("message") or {}
        content = (message.get("content") or "").strip()
        last_content = content
        usage = data.get("usage", {})
        total_tokens += usage.get("total_tokens", 0) or usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)

        raw_tool_calls = message.get("tool_calls") or []
        text_tool_calls: list[tuple[str, dict]] = []
        if not raw_tool_calls and parse_text_tool_calls:
            text_tool_calls = parse_text_tool_calls(content)

        if raw_tool_calls:
            assistant_message = {"role": "assistant", "content": content, "tool_calls": raw_tool_calls}
            messages.append(assistant_message)
            loop = asyncio.get_event_loop()
            for tc in raw_tool_calls:
                fn = tc.get("function") or {}
                name = (fn.get("name") or "").strip()
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except json.JSONDecodeError:
                    args = {}
                if on_tool_call:
                    try:
                        on_tool_call(name, args)
                    except Exception:
                        pass
                tool_result = await loop.run_in_executor(
                    None,
                    (lambda n=name, a=args: execute_tool(n, a)),
                )
                if on_tool_result:
                    try:
                        on_tool_result(name, args, tool_result)
                    except Exception:
                        pass
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "content": tool_result,
                })
            continue

        if text_tool_calls:
            messages.append({"role": "assistant", "content": content})
            loop = asyncio.get_event_loop()
            results: list[str] = []
            for name, args in text_tool_calls:
                if on_tool_call:
                    try:
                        on_tool_call(name, args)
                    except Exception:
                        pass
                result = await loop.run_in_executor(
                    None,
                    (lambda n=name, a=args: execute_tool(n, a)),
                )
                if on_tool_result:
                    try:
                        on_tool_result(name, args, result)
                    except Exception:
                        pass
                results.append(f"[{name}]\n{result}")
            follow_up = "Tool results:\n\n" + "\n\n".join(results)
            follow_up += "\n\nUse the above to complete your analysis. Respond with ONLY your final JSON (e.g. {\"findings\": [...]}), no other text or tool calls."
            messages.append({"role": "user", "content": follow_up})
            continue

        break

    return last_content, total_tokens
