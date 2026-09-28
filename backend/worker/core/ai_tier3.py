import json
import sys
import asyncio
import aiohttp
from .config import OPENROUTER_API_KEY, OPENROUTER_API_URL, SMART_MODEL, DETECTOR_MIN_CONFIDENCE, logger
from .deepseek_client import bridge_healthy, complete_json, llm_configured
from .utils import (
    build_focused_code_bundle,
    find_line_number,
    clean_json_response,
    get_function_or_window,
    get_bounded_snippet,
    repair_or_complete_tier3_json,
    find_keywords_with_lines,
    normalize_openrouter_message_content,
)
from .keywords import RECALL_KEYWORDS
from typing import Optional


def _filter_low_confidence(findings: list, threshold: float = DETECTOR_MIN_CONFIDENCE) -> list:
    """Drop Tier 3 findings below the confidence threshold before downstream filtering/validation."""
    kept = []
    for f in findings:
        if not isinstance(f, dict):
            logger.warning("[TIER 3] Skipping non-dict finding entry: %r", f)
            continue
        score = f.get("confidence_score")
        if score is None:
            # BUG FIX: Missing confidence should default to mid-range (5.0), not max (10.0)
            logger.warning(
                f"[TIER 3] Missing confidence_score on finding: {f.get('type')} — defaulting to 5.0"
            )
            score = 5.0
        try:
            score = float(score)
        except (TypeError, ValueError):
            # BUG FIX: Unparseable confidence should default to mid-range, not max
            logger.warning(
                f"[TIER 3] Unparseable confidence_score '{score}' — defaulting to 5.0"
            )
            score = 5.0
        if score >= threshold:
            kept.append(f)
        else:
            logger.debug(
                f"[TIER 3] Dropping low-confidence finding (score={score}): "
                f"{f.get('type')} in {f.get('function_name')}"
            )
    return kept

# Total attempts: attempt 0 = stream, attempt 1 = non-stream fallback
MAX_TIER3_ATTEMPTS = 2

async def scan_tier_3_advanced(
    session,
    filename,
    content,
    context_info: str = "",
    tier1_result: Optional[dict] = None,
    compacted_context: str = "",
):
    """
    Uses OpenRouter `SMART_MODEL` with streaming (see `config.py`).
    Goal: Detailed Remediation, CVSS, Complexity (no PoC script here).
    NOW: Focuses on suspicious regions as indicated by Tier 1 (`CHEAP_MODEL`),
    instead of scanning the full file.
    """
    url = OPENROUTER_API_URL
    
    # ENHANCED SCHEMA - JSON-serializable for prompt embedding (no Python type objects)
    schema = {
        "status": "VULNERABLE | SAFE",
        "findings": [{
            "type": "string (vulnerability type)",
            "subtype": "string",
            "severity": "HIGH | MEDIUM | LOW",
            "confidence_score": "integer 1-10",
            "cwe_id": "string",
            "cvss_score": "float 0.0-10.0",
            "cvss_vector": "string e.g. CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            "fix_complexity": "LOW | MEDIUM | HIGH",
            "function_name": "string",
            "vulnerable_code": "string (exact vulnerable code)",
            "surrounding_code": "string",
            "reason": "string",
            "impact_summary": "string",
            "consequences": "string",
            "remediation": "string (specific code change)",
            "references": "array of strings",
            "tier1_was_correct": "boolean",
            "rejection_reason": "string or null",
            "cross_file_taint": "boolean (true if spans multiple files)",
            "exploit_proof": "One sentence: exactly how an attacker triggers this. Format: '[Method] [endpoint] with [param]=[payload] causes [outcome].' If you cannot write this, set confidence_score to 3 or below."
        }]
    }

    # Build focused input from Tier 1, or fallback
    if tier1_result:
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

    system_prompt = (
        "You are an Elite Penetration Tester and Secure Code Auditor performing GROUND TRUTH analysis.\n\n"
        "TIER 1 RELATIONSHIP:\n"
        "Tier 1 is a fast model with a HIGH false positive rate — treat it as a map, not a verdict.\n"
        "You are the ground truth layer. Your job:\n"
        "  - Confirm findings Tier 1 got right\n"
        "  - Reject findings Tier 1 got wrong (and log in 'rejections') — rejection requires explicit justification in rejection_reason\n"
        "  - Find findings Tier 1 MISSED that are visible in the provided snippets\n"
        "Weight your own code analysis over Tier 1's label in all cases.\n"
        "Do NOT dismiss a Tier 1 finding without independent analysis. Rejection requires explicit justification in rejection_reason.\n\n"
        "You are given focused code snippets around suspicious locations. "
        "Analyze deeply, refine the findings, and provide actionable remediation, CVSS, and CWE.\n"
        f"Return strictly valid JSON ONLY, exactly matching this schema: {json.dumps(schema)}\n"
        "Do NOT wrap the JSON in markdown code fences. Do NOT add any extra text.\n\n"
        "REASONING PROTOCOL — follow this exact order before outputting JSON:\n"
        "1. TRACE: For each suspicious location, trace the data flow. "
        "Where does input come from? Where does it go? Is it sanitized?\n"
        "2. EXPLOIT: Write a one-sentence proof of exploit. "
        "If you cannot write one, the finding is not reportable.\n"
        "3. REJECT: List what you considered but rejected and why.\n"
        "4. SCORE: Only after steps 1-3, assign confidence_score.\n"
        "5. OUTPUT: Emit the JSON.\n"
        "The JSON must reflect your reasoning, not precede it.\n\n"
        "EXPLOIT PROOF RULE:\n"
        "Every finding MUST have an exploit_proof.\n"
        "Format: '[HTTP method] [endpoint] with [parameter]=[payload] causes [outcome].'\n"
        "If exploit requires conditions you cannot verify, state them and reduce confidence_score by 2.\n"
        "If you cannot write any exploit_proof, do not report the finding.\n\n"
        "Requirements:\n"
        "1. INDEPENDENT ANALYSIS: Determine ground truth. Reject Tier 1 if the finding is not exploitable.\n"
        "2. CVSS v3.1 DECISION TREE:\n"
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
        "  Plaintext passwords      = 7.5  (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)\n"
        "3. Provide 'cvss_vector' (e.g., 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H').\n"
        "4. Assess 'fix_complexity' (LOW/MEDIUM/HIGH).\n"
        "5. Explicitly identify the function name and surrounding context.\n"
        "6. 'confidence_score' must be 1-10 (10 = certain exploit exists). See confidence scale below.\n"
        "7. 'remediation' must be a specific code change string (e.g., \"db.query('SELECT * FROM users WHERE email = $1', [email])\"), not a list of steps.\n"
        "8. REQUIRED FIELDS:\n"
        "   - 'tier1_was_correct' (bool): Was Tier 1's finding actually correct?\n"
        "   - 'rejection_reason' (string or null): If you rejected Tier 1's finding, explain why\n"
        "   - 'cross_file_taint' (bool): True if vulnerability spans multiple files (source in one, sink in another)\n"
        "9. Provide specific CWE IDs: CWE-89 (SQLi), CWE-78 (OS Command Injection), "
        "CWE-79 (XSS), CWE-918 (SSRF), CWE-22 (Path Traversal), CWE-502 (Deserialization), "
        "CWE-94 (Code Injection), CWE-798 (Hardcoded Credentials), CWE-327 (Weak Crypto), "
        "CWE-639 (IDOR), CWE-352 (CSRF), CWE-256 (Plaintext Password Storage), "
        "CWE-916 (Insufficient Password Hashing).\n\n"
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
        "FRONTEND VULNERABILITY PATTERNS:\n"
        "================================================================================\n"
        "XSS — VULNERABLE:\n"
        "  dangerouslySetInnerHTML={{ __html: userContent }}\n"
        "  element.innerHTML = userInput\n"
        "  document.write(userInput)\n"
        "XSS — SAFE:\n"
        "  <div>{variable}</div>  ← React auto-escapes\n"
        "  element.textContent = userInput\n\n"
        "Sensitive Storage — VULNERABLE:\n"
        "  localStorage.setItem('token', jwt)\n"
        "  localStorage.setItem('user', JSON.stringify(userWithRole))\n"
        "  Reason: readable by any JS on page, XSS pivot\n\n"
        "Open Redirect — VULNERABLE:\n"
        "  window.location.href = searchParams.get('redirect')\n"
        "  router.push(req.query.next)\n"
        "Open Redirect — SAFE:\n"
        "  router.push('/dashboard')\n"
        "  router.push(ALLOWED_ROUTES[key])\n\n"
        "================================================================================\n"
        "CROSS-FILE TAINT:\n"
        "================================================================================\n"
        "If you see a SINK (exec, query, eval, innerHTML) receiving a variable "
        "you cannot trace to its origin in the shown code — flag it with "
        "confidence_score 6 and cross_file_taint: true.\n"
        "If you see a SOURCE (req.body, req.query) flowing into a function "
        "whose implementation is not shown — flag it with confidence_score 6 "
        "and cross_file_taint: true.\n"
        "Do NOT drop cross-file findings. DO reduce confidence by 2 vs same-file findings.\n\n"
        "================================================================================\n"
        "CONFIDENCE SCALE - Be precise with your scoring:\n"
        "================================================================================\n"
        f"9-10: Certain exploit path identified, can demonstrate exploitation (score ≥ {int(DETECTOR_MIN_CONFIDENCE)} = report)\n"
        f"7-8: High confidence - clear vulnerability with known exploit (score ≥ {int(DETECTOR_MIN_CONFIDENCE)} = report)\n"
        f"{int(DETECTOR_MIN_CONFIDENCE)}-6: Borderline - only report if exploit path is absolutely clear\n"
        f"Below {int(DETECTOR_MIN_CONFIDENCE)}: Do NOT report (filtered as likely false positive)\n\n"
        "================================================================================\n"
        "DEPRIORITIZE — require confidence ≥ 8 to report (not full exclusion):\n"
        "================================================================================\n"
        "- Prototype pollution: only if __proto__ or constructor reachable from user input\n"
        "- Open redirect: only if redirect target is user-controlled with no origin validation\n"
        "- Path traversal: only if path comes from user input AND reaches outside intended directory\n\n"
        "FULL EXCLUSIONS — never report:\n"
        "- DoS / resource exhaustion / rate limiting\n"
        "- Log spoofing\n"
        "- Memory safety issues in Python/JS (impossible)\n"
        "- Race conditions unless concretely exploitable\n"
        "- Outdated libraries (handled by separate dependency scanner)\n\n"
        "RECALL — MUST CHECK (do not skip):\n"
        "- Open Redirect: RedirectResponse(redirect_url), redirect(user_input), location.href = userInput, navigate(searchParams.get('next')). Flag if target is user-controlled with no allowlist.\n"
        "- JWT algorithm confusion: jwt.decode(..., algorithms=[algo]) where algo is user-controlled. Report as HIGH (auth bypass).\n"
        "- ReDoS: re.match(pattern, text) or re.search(pattern, text) where pattern is user-controlled. Report as MEDIUM/HIGH (denial of service).\n"
        "- Information disclosure: endpoints returning os.environ, SECRET_KEY, or full tracebacks. Flag /api/debug, /debug/env, error handlers exposing stack.\n"
        "- Host header injection: response URL or redirect built from X-Forwarded-Host or request headers without validation.\n"
        "- Unrestricted file upload: UploadFile/save() without checking file extension or size; allowlist extensions.\n"
        "- CSV formula injection: csv.writer, writerow(), or to_csv writing user-controlled cell content without sanitizing leading =, +, -, @.\n"
        "- SSTI (Jinja2, Template) and XXE: report as HIGH severity (not INFORMATIONAL). CVSS 8+ for RCE/read arbitrary files.\n"
        "- Plaintext password storage: flag if passwords are stored or compared without hashing. "
        "Look for SELECT WHERE password=?, direct string comparison, or absence of bcrypt/argon2/hashlib/pbkdf2 in the authentication call path. "
        "CWE-256 / CWE-916. CVSS 7.5+\n"
        "- Missing CSRF protection (Flask): flag state-changing POST/PUT/DELETE routes with no flask_wtf.csrf.CSRFProtect or equivalent token validation. CWE-352.\n"
        "- Missing rate limiting on credential endpoints (Flask): flag /login, /reset-password, /verify-otp routes with no flask_limiter / @limiter.limit() decorator visible. CWE-307.\n\n"
        "================================================================================\n"
        "CROSS-FILE VULNERABILITIES:\n"
        "================================================================================\n"
        "If you identify a vulnerability where the source (user input) and sink (dangerous function) "
        "are in different files, report it with the evidence you have and set 'cross_file_taint': true. "
        "Do not drop it just because you can't see both sides.\n\n"
        "================================================================================\n"
        "SECONDARY VULNERABILITY CHECKLIST:\n"
        "================================================================================\n"
        "After your primary analysis, explicitly check for each of these:\n\n"
        "[ ] PREDICTABLE TOKENS\n"
        "    Flag if reset/session tokens use: Date.now(), Math.random(),\n"
        "    sequential IDs, username+timestamp, or any non-CSPRNG source.\n"
        "    Safe pattern: crypto.randomBytes(32), uuid v4, secrets.token_hex()\n\n"
        "[ ] MISSING RATE LIMITING\n"
        "    Flag auth endpoints (login, reset-password, verify-otp) with no\n"
        "    rate limiting middleware visible in the route definition or controller.\n"
        "    Python/Flask: flask_limiter, @limiter.limit()\n"
        "    Node.js: express-rate-limit, slowDown, ratelimiter, @RateLimit\n"
        "    Only flag if the endpoint handles credentials or tokens.\n\n"
        "[ ] STACK TRACE / DEBUG EXPOSURE\n"
        "    Flag error handlers that return error.stack, error.message, or\n"
        "    full exception objects in HTTP responses.\n"
        "    Safe pattern: generic message only, stack logged server-side.\n\n"
        "[ ] SENSITIVE DATA IN DATABASE\n"
        "    Flag refresh tokens, password reset tokens, or session tokens\n"
        "    stored as plaintext strings in DB models/schemas.\n"
        "    Safe pattern: hashed with bcrypt/argon2 before storage.\n\n"
        "[ ] PLAINTEXT PASSWORD STORAGE\n"
        "    Flag if passwords are stored or compared without hashing.\n"
        "    Look for: SELECT WHERE password=?, direct string comparison in login,\n"
        "    INSERT INTO users VALUES (..., plaintext_password, ...),\n"
        "    or absence of bcrypt/argon2/hashlib.pbkdf2 anywhere in the auth flow.\n"
        "    Safe pattern: bcrypt.checkpw(), argon2.verify(), pbkdf2_hmac()\n"
        "    CWE-256 / CWE-916. CVSS 7.5+\n\n"
        "[ ] INCOMPLETE IDOR COVERAGE\n"
        "    If you flag an IDOR on one operation (e.g. getOne), check ALL\n"
        "    operations on the same resource: create, update, delete, list.\n"
        "    Report each unprotected operation as a separate finding.\n"
        "    Distinguish read IDOR (CVSS 6.5) from write IDOR (CVSS 8.1)\n"
        "    and write IDOR with privilege escalation (CVSS 8.8).\n\n"
        "[ ] HARDCODED SECRETS IN FRONTEND\n"
        "    Flag API keys, analytics tokens, tracking IDs hardcoded in\n"
        "    .js/.jsx/.ts/.tsx files that ship to the browser.\n"
        "    These are exposed to all users regardless of auth.\n\n"
        "[ ] INSECURE API CLIENT CONFIG\n"
        "    Flag axios/fetch clients configured with:\n"
        "    - HTTP (not HTTPS) base URLs in production config\n"
        "    - withCredentials: false on authenticated endpoints\n"
        "    - No CSRF token header on state-changing requests\n\n"
        "[ ] MISSING CSRF PROTECTION\n"
        "    Flag state-changing POST/PUT/DELETE routes with no CSRF token validation.\n"
        "    Flask: check for flask_wtf.csrf.CSRFProtect(app) or per-route @csrf.exempt absence.\n"
        "    Node.js: check for csurf middleware or equivalent.\n"
        "    Only flag if the route modifies server state and uses cookie-based sessions.\n"
        "    CWE-352. CVSS 6.5+\n"
    )


    # BUG FIX: Add truncation indicators when context is sliced
    context_truncated = len(context_info) > 4000
    context_preview = context_info[:4000]
    if context_truncated:
        context_preview += "\n... [context truncated]"

    compacted_truncated = len(compacted_context) > 5000
    compacted_preview = compacted_context[:5000]
    if compacted_truncated:
        compacted_preview += "\n... [compacted context truncated]"

    user_content = (
        f"High-level context (project + code graph):\n{context_preview}\n\n"
        + (
            f"Compacted high-signal lines for recall (large-file prefilter):\n{compacted_preview}\n\n"
            if compacted_context
            else ""
        )
        +
        f"File: {filename}\n\n"
        f"FOCUSED CODE SNIPPETS (with line numbers):\n\n{focused_code}"
    )

    payload = {
        "model": SMART_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "stream": True,  # STREAM ENABLED
        "max_tokens": 16384,  # reduce stream truncation (unterminated JSON)
    }

    # Slow providers + many parallel /scan calls: 240s sock_read caused spurious timeouts between chunks.
    timeout = aiohttp.ClientTimeout(total=900, connect=60, sock_connect=60, sock_read=600)
    non_stream_timeout = aiohttp.ClientTimeout(total=900, connect=60, sock_connect=60, sock_read=900)

    data = None
    clean_content = ""
    use_stream = True  # First attempt: stream. Retry: non-stream for complete response.

    for attempt in range(MAX_TIER3_ATTEMPTS):
        try:
            req_payload = {**payload, "stream": use_stream}
            if not use_stream:
                # Non-stream retry: allow more tokens to reduce truncation
                req_payload = {**req_payload, "max_tokens": 24576}
            request_timeout = non_stream_timeout if not use_stream else timeout
            async with session.post(
                url,
                json=req_payload,
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                timeout=request_timeout
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    logger.error(f"OpenRouter Tier 3 Stream Error {resp.status}: {error}")
                    return {"status": "ERROR", "details": f"OpenRouter Error: {resp.status}"}

                collected_content = ""
                if use_stream:
                    sys.stdout.write("\n[Tier 3] waiting for model")
                    sys.stdout.flush()

                    async def _heartbeat():
                        await asyncio.sleep(1)
                        while True:
                            sys.stdout.write(".")
                            sys.stdout.flush()
                            await asyncio.sleep(2)

                    heartbeat_task = asyncio.create_task(_heartbeat())
                    first_chunk = True  # BUG FIX: Track first chunk for heartbeat cancellation
                    try:
                        async for raw_line in resp.content:
                            # BUG FIX: Only cancel heartbeat on first chunk, not every chunk
                            if first_chunk and heartbeat_task:
                                heartbeat_task.cancel()
                                try:
                                    await heartbeat_task
                                except asyncio.CancelledError:
                                    pass
                                heartbeat_task = None
                                first_chunk = False

                            try:
                                line = raw_line.decode("utf-8").strip()
                            except Exception:
                                continue

                            if not line.startswith("data:"):
                                continue
                            if line == "data: [DONE]":
                                break

                            json_str = line[5:].strip()
                            if not json_str:
                                continue

                            try:
                                chunk = json.loads(json_str)
                            except json.JSONDecodeError:
                                continue

                            if not isinstance(chunk, dict):
                                continue
                            choices = chunk.get("choices") or []
                            if not choices:
                                continue
                            try:
                                delta = (choices[0] or {}).get("delta") or {}
                            except (IndexError, TypeError, AttributeError):
                                continue
                            if delta.get("content"):
                                chunk_text = delta["content"]
                                if not collected_content:
                                    sys.stdout.write("\n  ")
                                collected_content += chunk_text
                                sys.stdout.write(chunk_text)
                                sys.stdout.flush()
                    finally:
                        if heartbeat_task:
                            heartbeat_task.cancel()
                            try:
                                await heartbeat_task
                            except asyncio.CancelledError:
                                pass
                else:
                    # Non-stream retry: get full JSON response (more reliable when stream was cut off)
                    logger.info("[TIER 3] Non-stream request in progress, waiting for full response...")
                    result = await resp.json()
                    choices = result.get("choices", [])
                    if choices:
                        msg = choices[0].get("message") or {}
                        collected_content = normalize_openrouter_message_content(msg) or ""
                    if not collected_content and choices:
                        logger.warning(
                            "[TIER 3] Non-stream empty body after normalize; finish_reason=%r",
                            choices[0].get("finish_reason"),
                        )
                    logger.info("[TIER 3] Non-stream response received (%s chars)", len(collected_content))
                    sys.stdout.write("\n[Tier 3] non-stream retry complete\n")
                    sys.stdout.flush()

                sys.stdout.write("\n")
                sys.stdout.flush()

                logger.info(
                    f"\n========== [TIER 3 STREAM COMPLETE] ({filename}) (attempt {attempt + 1}) ==========\n"
                    f"{collected_content[:500]}...\n"
                    f"===========================================================\n"
                )

                clean_content = clean_json_response(collected_content)

                try:
                    data = json.loads(clean_content)
                    break
                except json.JSONDecodeError as e:
                    if attempt < MAX_TIER3_ATTEMPTS - 1:
                        logger.warning(
                            "Tier 3 JSON parse failed (stream cut off?), retrying with non-stream (attempt %s/%s): %s",
                            attempt + 1, MAX_TIER3_ATTEMPTS, e,
                        )
                        logger.info(
                            "[TIER 3] Switching to non-stream request for full response; this may take several minutes..."
                        )
                        use_stream = False  # Retry with non-stream for complete response
                        continue
                    logger.error(
                        f"Tier 3 JSON Parse Error (stream cut off?): {e}\n"
                        f"Streamed content (first 1000 chars): {clean_content[:1000]}..."
                    )

                    logger.info("Tier 3 stream truncated, calling repair to complete JSON...")
                    data = await repair_or_complete_tier3_json(session, clean_content)
                    if not data:
                        return {
                            "status": "ERROR",
                            "details": "Invalid JSON from Tier 3 model (stream) and repair failed"
                        }
                    break
        except Exception as e:
            if attempt < MAX_TIER3_ATTEMPTS - 1:
                logger.warning(
                    "Tier 3 stream exception, retrying (attempt %s/%s): %s: %r",
                    attempt + 1, MAX_TIER3_ATTEMPTS, type(e).__name__, e,
                )
                continue
            logger.exception(f"Tier 3 Stream Exception: {type(e).__name__}: {repr(e)}")

            # Fallback: one non-stream completion attempt to recover from stream timeouts.
            try:
                non_stream_payload = {
                    **payload,
                    "stream": False,
                    # Smaller completion target reduces timeout risk on fallback.
                    "max_tokens": 8192,
                }
                async with session.post(
                    url,
                    json=non_stream_payload,
                    headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                    timeout=aiohttp.ClientTimeout(total=600, connect=60, sock_connect=60, sock_read=600),
                ) as resp2:
                    if resp2.status != 200:
                        err2 = await resp2.text()
                        return {"status": "ERROR", "details": f"Tier 3 fallback failed ({resp2.status}): {err2[:300]}"}

                    result2 = await resp2.json()
                    choices2 = result2.get("choices", [])
                    if not choices2:
                        return {"status": "ERROR", "details": "Tier 3 fallback returned empty choices"}
                    content2 = normalize_openrouter_message_content(choices2[0].get("message") or {}) or ""
                    clean2 = clean_json_response(content2 or "")
                    try:
                        data = json.loads(clean2)
                    except json.JSONDecodeError:
                        data = await repair_or_complete_tier3_json(session, clean2)
                        if not data:
                            return {"status": "ERROR", "details": "Tier 3 stream timeout and fallback parse failed"}
            except Exception as e2:
                return {"status": "ERROR", "details": f"Tier 3 stream exception + fallback exception: {type(e2).__name__}"}
            break

    if data is None:
        return {"status": "ERROR", "details": "Tier 3 failed after retries"}

    # Models sometimes return a bare JSON array of findings despite json_object mode.
    if isinstance(data, list):
        if not data:
            data = {"findings": []}
        elif all(isinstance(x, dict) for x in data):
            data = {"findings": data}
        else:
            logger.warning(
                "[TIER 3] Parsed JSON is a non-object array (truncated/garbled output); "
                "attempting repair for %s",
                filename,
            )
            repaired = await repair_or_complete_tier3_json(session, clean_content)
            if repaired is None:
                return {
                    "status": "ERROR",
                    "details": "Tier 3 returned invalid JSON (non-object array) and repair failed",
                }
            if isinstance(repaired, list):
                if not repaired:
                    data = {"findings": [], "status": "SAFE"}
                elif all(isinstance(x, dict) for x in repaired):
                    data = {"findings": repaired}
                else:
                    return {
                        "status": "ERROR",
                        "details": "Tier 3 repair still returned a non-object array",
                    }
            elif isinstance(repaired, dict):
                data = repaired
            else:
                return {
                    "status": "ERROR",
                    "details": f"Tier 3 repair returned unexpected type: {type(repaired).__name__}",
                }
    elif not isinstance(data, dict):
        return {
            "status": "ERROR",
            "details": f"Tier 3 returned unexpected JSON type: {type(data).__name__}",
        }

    raw_findings = data.get("findings")
    if raw_findings is None:
        data["findings"] = []
    elif not isinstance(raw_findings, list):
        logger.warning("[TIER 3] findings is not a list; resetting to empty")
        data["findings"] = []
    else:
        dict_only = [x for x in raw_findings if isinstance(x, dict)]
        if len(dict_only) != len(raw_findings):
            logger.warning(
                "[TIER 3] Dropped %d non-dict entries from findings",
                len(raw_findings) - len(dict_only),
            )
        data["findings"] = dict_only

    # First pass: drop obviously low-confidence / explanatory-only findings.
    if data.get("findings"):
        data["findings"] = _filter_low_confidence(data["findings"])

    if data.get("findings"):
        data["status"] = "VULNERABLE"
        for f in data["findings"]:
            f["_model_vulnerable_code"] = f.get("vulnerable_code", "")

            line_num = find_line_number(
                content,
                f["_model_vulnerable_code"],
                f.get("surrounding_code", ""),
                f.get("function_name", "")
            )
            f["line"] = line_num

            # Only the relevant part: minimal snippet (vulnerable line + a bit), not whole function/file
            snippet = get_bounded_snippet(content, line_num, before=1, after=2)
            f["vulnerable_code"] = snippet or f["_model_vulnerable_code"]

            # Surrounding context: 3 lines before and after (bounded)
            f["surrounding_code"] = get_bounded_snippet(content, line_num, before=3, after=3)
    else:
        data.setdefault("status", "SAFE")

    return data
