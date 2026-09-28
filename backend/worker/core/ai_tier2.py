# app/ai_tier2.py
import json
import sys
import asyncio
import aiohttp
from .config import OPENROUTER_API_KEY, OPENROUTER_API_URL, TIER2_MODEL, DETECTOR_MIN_CONFIDENCE, logger
from .deepseek_client import bridge_healthy, complete_json, llm_configured
from .utils import (
    build_focused_code_bundle,
    find_line_number,
    clean_json_response,
    get_function_or_window,
    find_keywords_with_lines,
    parse_json_with_fallbacks,
)
from .keywords import RECALL_KEYWORDS
from typing import Optional


def _filter_low_confidence(findings: list, threshold: float = DETECTOR_MIN_CONFIDENCE) -> list:
    """Drop Tier 2 findings below the confidence threshold before escalation."""
    kept = []
    for f in findings:
        score = f.get("confidence_score")
        if score is None:
            logger.warning(f"[TIER 2] Missing confidence_score: {f.get('type')} — defaulting to 5.0")
            score = 5.0
        try:
            score = float(score)
        except (TypeError, ValueError):
            logger.warning(f"[TIER 2] Unparseable confidence_score — defaulting to 5.0")
            score = 5.0
        if score >= threshold:
            kept.append(f)
        else:
            logger.debug(
                f"[TIER 2] Dropping low-confidence finding (score={score}): "
                f"{f.get('type')} in {f.get('function_name')}"
            )
    return kept


async def scan_tier_2_standard(
    session,
    filename,
    content,
    context_info: str = "",
    tier1_result: Optional[dict] = None,
    compacted_context: str = "",
):
    """
    Uses OpenRouter `TIER2_MODEL` (see `config.py`).
    Goal: Accurate classification with Confidence & CWE.
    NOW: Focuses on suspicious regions as indicated by Tier 1 (`CHEAP_MODEL`),
    instead of sending the entire file.
    """
    url = OPENROUTER_API_URL
    
    # ENHANCED SCHEMA with adversarial validation fields
    schema = {
        "status": "VULNERABLE or SAFE",
        "findings": [{
            "type": "Vulnerability Type",
            "subtype": "Specific Variant (e.g. Union-based SQLi)",
            "severity": "CRITICAL/HIGH/MEDIUM/LOW",
            "confidence_score": "Integer 1-10 (10 is certain)",
            "cwe_id": "CWE ID (e.g., CWE-89)",
            "function_name": "Name of the function containing the bug",
            "vulnerable_code": "Exact code snippet",
            "surrounding_code": "The 3 lines of code before and after the vulnerable line",
            "reason": "Technical explanation",
            "impact_summary": "One sentence on what the attacker can do",
            "tier1_was_correct": "Boolean - was Tier 1's finding actually correct?",
            "rejection_reason": "String or null - if rejected, explain why",
            "cvss_score": "Estimated numeric CVSS score (0.0-10.0) or null",
            "remediation": "Specific code change to fix, not generic prose"
        }],
        "rejections": [{
            "tier1_finding_type": "What Tier 1 flagged",
            "location": "function or line",
            "reason": "Why this is not a vulnerability",
            "pattern_matched": "Which safe pattern applies"
        }]
    }

    # Build focused input from Tier 1, or fall back to full content if missing
    if tier1_result:
        # Add keyword-driven snippets so Tier 2 sees code Tier 1 might have missed (recall)
        kw_hits = find_keywords_with_lines(content, RECALL_KEYWORDS, max_hits=30)
        extra_line_numbers = [h["line"] for h in kw_hits] if kw_hits else None
        focused_code = build_focused_code_bundle(
            filename,
            content,
            tier1_result,
            max_findings=15,
            window=15,
            extra_line_numbers=extra_line_numbers,
        )
    else:
        focused_code = (
            "Tier 1 context not available; falling back to full file content.\n\n"
            + content
        )

    # UPDATED PROMPT: model sees a focused bundle and must re-verify
    system_prompt = (
        "You are a Senior Security Engineer performing independent code review. "
        "You are given code snippets that a Tier 1 model flagged as potentially vulnerable.\n\n"
        "YOUR PRIMARY TASK: VERIFY each finding independently. Be THOROUGH.\n"
        "Your job is to:\n"
        "  1. Examine the code snippet carefully and independently\n"
        "  2. Determine if a real, exploitable vulnerability exists - not just a suspicious pattern\n"
        "  3. Confirm a concrete attack path (how would an attacker actually exploit this?)\n"
        "  4. If you cannot confirm the exploit path with high confidence, do not report it\n\n"
        "Tier 1 is a high-recall model with a HIGH false positive rate.\n"
        "Treat its output as a hint, not a verdict.\n"
        "Your job: confirm what's real, reject what's not, find what Tier 1 missed.\n"
        "Weight your own code analysis over Tier 1's label in all cases.\n\n"
        f"Return strictly valid JSON: {json.dumps(schema)}\n"
        "Requirements:\n"
        f"1. Assign a 'confidence_score' (1-10). Only include findings with score >= {int(DETECTOR_MIN_CONFIDENCE)}.\n"
        "2. Map the vulnerability to a specific 'cwe_id'.\n"
        "3. Extract the 'surrounding_code' context accurately from the snippets.\n"
        "4. If Tier 1 flagged something that is NOT a real vulnerability, omit it from your response.\n"
        "5. REQUIRED NEW FIELDS:\n"
        "   - 'tier1_was_correct' (bool): Was Tier 1's finding actually correct?\n"
        "   - 'rejection_reason' (string or null): If you rejected Tier 1's finding, explain why\n"
        "   - 'cross_file_taint' (bool): True if vulnerability spans multiple files\n"
        "   - 'severity' must be one of CRITICAL/HIGH/MEDIUM/LOW\n"
        "   - 'cvss_score' (number or null): estimated numeric CVSS v3.1 score\n"
        "   - 'cvss_vector' (string or null): e.g. 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'\n"
        "   - 'remediation' (string): Specific code change to fix, not generic prose\n\n"
        "6. CVSS v3.1 DECISION TREE:\n"
        "AV: N=network exploitable, A=adjacent, L=local, P=physical\n"
        "AC: L=no special conditions, H=requires specific config\n"
        "PR: N=unauthenticated, L=any login, H=admin required\n"
        "UI: N=no victim interaction, R=victim must act\n\n"
        "REFERENCE ANCHORS (stay within 0.5 unless you justify deviation):\n"
        "  SQLi unauth              = 9.8  (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)\n"
        "  SQLi behind auth         = 8.8  (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)\n"
        "  Command injection        = 8.8  (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)\n"
        "  XXE                      = 7.5  (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)\n"
        "  Read IDOR                = 6.5  (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)\n"
        "  Write IDOR               = 8.1  (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)\n"
        "  Write IDOR + priv esc    = 8.8  (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)\n"
        "  Stored XSS               = 5.4  (AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)\n"
        "  Reflected XSS            = 6.1  (AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)\n"
        "  Hardcoded secret         = 7.4  (AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)\n"
        "  Hardcoded secret exposed = 9.1  (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)\n"
        "  Path traversal read      = 7.5  (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)\n"
        "  Plaintext passwords      = 7.5  (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)\n\n"
        "================================================================================\n"
        "PRECEDENTS - These patterns are NOT vulnerabilities:\n"
        "================================================================================\n"
        "1. JSON.parse() / response.json() is NOT insecure deserialization - it's safe standard parsing\n"
        "2. Hardcoded localhost/127.0.0.1 URLs are NOT hardcoded secrets - they're dev endpoints\n"
        "3. UUIDs are unguessable and do NOT need validation\n"
        "4. Environment variables and CLI flags are TRUSTED in secure environments\n"
        "5. React setState with server data is NOT XSS - React auto-escapes by default\n"
        "6. router.push(HARDCODED_PATH) is safe. "
        "router.push(userInput) or window.location.href = req.query.redirect IS an open redirect — report it.\n"
        "7. window.open() is NOT insecure cryptography\n"
        "8. localStorage.setItem with JSON.stringify is NOT insecure deserialization\n"
        "9. Client-side auth checks are NOT vulnerabilities - backend MUST validate\n"
        "10. React/Angular are secure against XSS unless using dangerouslySetInnerHTML\n"
        "11. Plaintext passwords in DB seed/init data IS 'Hardcoded Credentials', NOT 'Insecure Deserialization'\n"
        "12. Logging non-PII data (URLs, IDs) is NOT a vulnerability - only secrets/passwords/PII\n"
        "13. try/catch logging error.message is NOT sensitive exposure unless it logs passwords/tokens\n"
        "14. HTTP URLs for internal private-network service calls are NOT insecure transport\n"
        "15. console.log(url, id, timestamp) is NOT a vulnerability — only flag if logging credentials/PII\n"
        "16. Rate limiting middleware in Flask uses flask_limiter / @limiter.limit() — absence is only flaggable on credential-handling endpoints\n"
        "17. CSRF protection in Flask uses flask_wtf.csrf.CSRFProtect — absence on state-changing POST routes IS reportable\n\n"
        "================================================================================\n"
        "SIGNAL QUALITY CRITERIA - Apply confidence scoring (1-10):\n"
        "================================================================================\n"
        f"9-10: Certain exploit path identified, tested if possible (score ≥ {int(DETECTOR_MIN_CONFIDENCE)} = report)\n"
        f"7-8:  High confidence - clear vulnerability with known exploit (score ≥ {int(DETECTOR_MIN_CONFIDENCE)} = report)\n"
        f"{int(DETECTOR_MIN_CONFIDENCE)}-6: Borderline - only report if exploit path is absolutely clear\n"
        f"Below {int(DETECTOR_MIN_CONFIDENCE)}: Do NOT report (filtered as likely false positive)\n\n"
        "EXCLUSIONS - DO NOT report findings for these categories:\n"
        "- DoS / resource exhaustion / rate limiting\n"
        "- Log spoofing\n"
        "- Memory safety issues in Python/JS (impossible)\n"
        "- Race conditions unless concretely exploitable\n"
        "- Outdated libraries (handled by separate dependency scanner)\n"
        "Report with MEDIUM/LOW when clearly exploitable: Open redirect, ReDoS (catastrophic backtracking with user input), "
        "Prototype pollution (clear security impact).\n\n"
        "RECALL — MUST CHECK (do not skip):\n"
        "- Open Redirect: RedirectResponse(redirect_url), redirect(user_input), location.href = userInput, navigate(searchParams.get('next')). Flag if target is user-controlled with no allowlist.\n"
        "- JWT algorithm confusion: jwt.decode(..., algorithms=[algo]) where algo is user-controlled. Report as HIGH (auth bypass).\n"
        "- ReDoS: re.match(pattern, text) or re.search(pattern, text) where pattern is user-controlled. Report as MEDIUM/HIGH.\n"
        "- Information disclosure: endpoints returning os.environ, SECRET_KEY, or full tracebacks. Flag /api/debug, /debug/env, error handlers exposing stack.\n"
        "- Host header injection: response URL or redirect built from X-Forwarded-Host or request headers without validation.\n"
        "- Unrestricted file upload: UploadFile/save() without checking file extension or size; allowlist extensions.\n"
        "- CSV formula injection: csv.writer, writerow(), or to_csv writing user-controlled cell content without sanitizing leading =, +, -, @.\n"
        "- SSTI (Jinja2, Template) and XXE: report as HIGH severity (not INFORMATIONAL). CVSS 8+ for RCE/read arbitrary files.\n"
        "- Plaintext password storage: flag if passwords are stored or compared without hashing. "
        "Look for SELECT WHERE password=?, direct string comparison in login, "
        "or absence of bcrypt/argon2/hashlib/pbkdf2 in the authentication call path. "
        "CWE-256 / CWE-916. CVSS 7.5+\n"
        "- Missing CSRF protection (Flask): flag state-changing POST/PUT/DELETE routes with no flask_wtf.csrf.CSRFProtect or equivalent token validation. CWE-352.\n"
        "- Missing rate limiting on credential endpoints (Flask): flag /login, /reset-password, /verify-otp routes with no flask_limiter / @limiter.limit() decorator visible. CWE-307.\n"
    )


    user_content = (
        f"High-level context (project + code graph):\n{context_info[:4000]}\n\n"
        + (
            f"Compacted high-signal lines for recall (large-file prefilter):\n{compacted_context[:5000]}\n\n"
            if compacted_context
            else ""
        )
        + 
        f"File: {filename}\n\n"
        f"FOCUSED CODE SNIPPETS (with line numbers):\n\n{focused_code}"
    )

    payload = {
        "model": TIER2_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "stream": False,  # Non-streaming often faster; heartbeat shows progress
    }

    timeout = aiohttp.ClientTimeout(total=300, sock_read=240)

    try:
        sys.stdout.write("\n[Tier 2] calling model")
        sys.stdout.flush()

        async def _heartbeat():
            elapsed = 0
            while True:
                await asyncio.sleep(5)
                elapsed += 5
                sys.stdout.write(f" ({elapsed}s)")
                sys.stdout.flush()

        heartbeat_task = asyncio.create_task(_heartbeat())
        try:
            async with session.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                timeout=timeout
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"OpenRouter API Error ({resp.status}): {error_text}")
                    return {"status": "UNKNOWN", "details": f"OpenRouter Error: {resp.status}"}

                result = await resp.json()
                raw_content = (result.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        finally:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
        sys.stdout.write("\n")
        sys.stdout.flush()

        if not raw_content:
            return {"status": "UNKNOWN", "details": "Empty response from OpenRouter"}

        logger.info(
            f"\n========== [TIER 2 RAW] ({filename}) ==========\n"
            f"{raw_content}\n"
            f"========================================================"
        )

        clean_content = clean_json_response(raw_content)
        ok, parsed = parse_json_with_fallbacks(clean_content, "Tier 2 response")
        if not ok:
            return {"status": "UNKNOWN", "details": "Invalid JSON from Tier 2 model"}
        data = parsed

        # Drop obviously low-confidence / explanatory-only findings before downstream filtering.
        if data.get("findings"):
            data["findings"] = _filter_low_confidence(data["findings"])

        if data.get("findings"):
            data["status"] = "VULNERABLE"
            for f in data["findings"]:
                severity = str(f.get("severity", "MEDIUM")).upper()
                if severity not in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
                    severity = "MEDIUM"
                f["severity"] = severity
                try:
                    if f.get("cvss_score") is not None:
                        f["cvss_score"] = float(f["cvss_score"])
                except (TypeError, ValueError):
                    f["cvss_score"] = None
                line_num = find_line_number(
                    content,
                    f.get("vulnerable_code", ""),
                    f.get("surrounding_code", ""),
                    f.get("function_name", "")
                )
                f["line"] = line_num
                snippet = get_function_or_window(content, line_num, filename, window=5)
                f["vulnerable_code"] = snippet
                lines = content.splitlines()
                start = max(0, line_num - 1 - 5)
                end = min(len(lines), line_num - 1 + 5 + 1)
                f["surrounding_code"] = "\n".join(lines[start:end])
            return data

        data.setdefault("status", "SAFE")
        return data

    except Exception as e:
        logger.exception(f"Tier 2 Unexpected Error: {str(e)}")
        return {"status": "UNKNOWN", "details": str(e)}
