import json
import aiohttp
from typing import Dict
from .config import OPENROUTER_API_KEY, OPENROUTER_API_URL, SMART_MODEL, logger
from .deepseek_client import bridge_healthy, complete_json, llm_configured
from .utils import clean_json_response

async def generate_poc_for_finding(session, filename: str, content: str, finding: dict):
    """
    Generate a SMALL Python PoC for a single finding.
    Called internally after Tier 3, when should_generate_poc == true.
    """
    url = OPENROUTER_API_URL

    schema = {
        "language": "python",
        "script_type": "standalone_exploit",
        "instructions": "Short Windows-focused run instructions",
        "script": "Complete Python3 script, no markdown fences",
        "expected_outcome": "What proves the exploit worked"
    }

    system_prompt = (
        "You are an expert exploit developer.\n"
        "Given one confirmed vulnerability finding and relevant code, "
        "generate a SMALL, WORKING Python PoC script.\n"
        f"Return strictly valid JSON ONLY, exactly matching this schema: {json.dumps(schema)}\n"
        "Rules:\n"
        "- language must be 'python'.\n"
        "- the script must default to assume the target server is in windows system, but include one or two variation exploits for linux/mac"
        "- script_type must be 'standalone_exploit'.\n"
        "- script must be a short (<= 60 lines) Python 3 script with NO markdown fences.\n"
        "- Define TARGET_URL or BASE_URL, defaulting to 'http://127.0.0.1:5000'.\n"
        "- Use 'requests' for HTTP if applicable; mention 'pip install requests' in instructions.\n"
        "- Include if __name__ == \"__main__\": main().\n"
        "- Print clear SUCCESS/FAILURE output.\n"
        "- Escape quotes/newlines properly so the JSON is valid.\n"
    )

    user_content = (
        f"File: {filename}\n\n"
        f"Vulnerability finding (JSON):\n{json.dumps(finding, indent=2)}\n\n"
        "Relevant code:\n"
        f"{content[:6000]}"
    )

    payload = {
        "model": SMART_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
        "stream": False
    }

    timeout = aiohttp.ClientTimeout(total=120, sock_read=120)

    try:
        if llm_configured() and await bridge_healthy(session):
            poc_data = await complete_json(session, filename, system_prompt, user_content, timeout_seconds=120)
            if isinstance(poc_data, dict):
                return {"status": "OK", "poc": poc_data}

        async with session.post(
            url, json=payload,
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            timeout=timeout
        ) as resp:
            if resp.status != 200:
                error = await resp.text()
                logger.error(f"OpenRouter PoC Error {resp.status}: {error}")
                return {"status": "ERROR", "details": f"PoC Error: {resp.status}"}

            result = await resp.json()
            raw_content = result["choices"][0]["message"]["content"]
            logger.info(f"\n========== [POC RAW - SMART_MODEL] ({filename}) ==========\n{raw_content}\n============================================")

            clean_content = clean_json_response(raw_content)
            try:
                poc_data = json.loads(clean_content)
            except json.JSONDecodeError as e:
                logger.error(f"PoC JSON Parse Error: {e}\nContent: {clean_content[:1000]}...")
                return {"status": "ERROR", "details": "Invalid JSON from PoC generator"}

            poc_data["status"] = "OK"
            return poc_data

    except Exception as e:
        logger.exception(f"PoC Generation Exception: {str(e)}")
        return {"status": "ERROR", "details": str(e)}
