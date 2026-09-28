# app/utils.py
import hashlib
import json
import re
from typing import List, Tuple, Set, Dict, Any, Optional
import aiohttp
from .keywords import ALL_KEYWORDS
from .config import OPENROUTER_API_KEY, OPENROUTER_API_URL, SMART_MODEL, logger

def build_security_context(project_ir: dict, max_files: int = 25) -> str:
    """
    Turn DeepWiki project_ir into a compact, human-readable security overview.

    Expected project_ir shape:
      {
        "files": {
          "path/to/file.py": {
            "file_summary": str,
            "main_concerns": [str | None, ...],
            "suspected_entrypoints": [
              {"kind": str, "name": str, "details": str}, ...
            ]
          },
          ...
        }
      }
    """
    files = project_ir.get("files", {})
    if not files:
        return "No project security overview available."

    all_concerns: list[str] = []
    all_entrypoints: list[dict] = []

    # Collect global concerns & entrypoints
    for _path, info in files.items():
        mc = info.get("main_concerns") or []
        se = info.get("suspected_entrypoints") or []
        # filter Nones / empties
        all_concerns.extend([str(c).strip() for c in mc if c])
        all_entrypoints.extend(se)

    # Dedup & clean
    concerns_clean = sorted(set(c for c in all_concerns if c))
    # Entry points as plaintext "kind name – details"
    def fmt_entry(ep: dict) -> str:
        kind = (ep.get("kind") or "").strip()
        name = (ep.get("name") or "").strip()
        details = (ep.get("details") or "").strip()
        label = ""
        if kind and name:
            label = f"[{kind}] {name}"
        elif name:
            label = name
        elif kind:
            label = f"[{kind}]"
        return f"{label} – {details}" if details and label else (label or details or "").strip()

    entrypoints_clean = [fmt_entry(ep) for ep in all_entrypoints]
    entrypoints_clean = [e for e in entrypoints_clean if e]  # drop empties

    lines: list[str] = []

    # === PROJECT SECURITY OVERVIEW ===
    lines.append("=== PROJECT SECURITY OVERVIEW ===")
    lines.append("")

    if concerns_clean:
        lines.append("Main concerns (deduped):")
        for c in concerns_clean[:12]:
            lines.append(f"  - {c}")
        lines.append("")

    if entrypoints_clean:
        lines.append("Sample suspected entrypoints (truncated):")
        for ep in entrypoints_clean[:10]:
            lines.append(f"  - {ep}")
        lines.append("")

    # === FILE SUMMARIES ===
    lines.append("=== FILE SUMMARIES (TRUNCATED) ===")

    for path, info in list(files.items())[:max_files]:
        lines.append(f"FILE: {path}")

        fs = (info.get("file_summary") or "").strip()
        if len(fs) > 400:
            fs = fs[:400].rstrip() + "..."
        lines.append(f"SUMMARY: {fs}")

        mc = [str(c).strip() for c in (info.get("main_concerns") or []) if c]
        if mc:
            lines.append("MAIN_CONCERNS:")
            for c in mc:
                lines.append(f"  - {c}")
        else:
            lines.append("MAIN_CONCERNS: (none detected)")

        se_list = info.get("suspected_entrypoints") or []
        if se_list:
            lines.append("ENTRYPOINTS:")
            for ep in se_list:
                ep_line = fmt_entry(ep)
                if ep_line:
                    lines.append(f"  - {ep_line}")
        else:
            lines.append("ENTRYPOINTS: (none detected)")

        lines.append("")  # blank line between files

    return "\n".join(lines)



_FRONTEND_EXTENSIONS = {'.jsx', '.tsx', '.vue', '.svelte', '.html', '.js', '.ts'}
_BACKEND_LANG_MAP = {
    '.py': 'Python', '.java': 'Java', '.go': 'Go', '.php': 'PHP',
    '.rb': 'Ruby', '.cs': 'C#', '.rs': 'Rust', '.c': 'C', '.cpp': 'C++',
}

def detect_language(filename: str) -> tuple:
    """
    Returns (language_name: str, is_frontend: bool).
    Used by all tiers to tailor prompts to the file's language.
    """
    ext = ''
    if '.' in filename:
        ext = '.' + filename.rsplit('.', 1)[-1].lower()

    if ext in {'.tsx', '.jsx'}:
        return 'TypeScript/React (JSX)', True
    if ext in {'.ts', '.js'}:
        return 'TypeScript/JavaScript', True
    if ext in {'.vue'}:
        return 'Vue.js', True
    if ext in {'.svelte'}:
        return 'Svelte', True
    if ext in {'.html'}:
        return 'HTML', True
    lang = _BACKEND_LANG_MAP.get(ext)
    if lang:
        return lang, False
    return 'Unknown', False


def _line_of_compact_snippet(clean_file_lines: List[str], snippet_clean: str) -> Optional[int]:
    """Return 1-based start line of a whitespace-collapsed snippet, or None."""
    if not snippet_clean:
        return None
    compact_lines = ["".join(line.split()) for line in clean_file_lines]
    starts: List[int] = []
    pos = 0
    for compact in compact_lines:
        starts.append(pos)
        pos += len(compact)
    joined = "".join(compact_lines)
    if joined.count(snippet_clean) != 1:
        return None
    idx = joined.find(snippet_clean)
    for i in range(len(starts) - 1, -1, -1):
        if starts[i] <= idx:
            return i + 1
    return None


# --- UTILS ---
def find_line_number(content: str, snippet: str, surrounding_code: str = "", function_name: str = "") -> int:
    """
    Smart Line Finder with Context Matching:
    1. Tries to match the 'surrounding_code' block (Highest Accuracy).
    2. Tries to find the full 'snippet' (multiline before first-line).
    3. Tries to find the function definition.
    """
    if not content:
        return 1

    file_lines = content.splitlines()
    clean_file_lines = [line.strip() for line in file_lines]

    # Positional callers sometimes pass function_name as surrounding_code.
    if (
        surrounding_code
        and "\n" not in surrounding_code
        and surrounding_code.strip().isidentifier()
    ):
        if not function_name:
            function_name = surrounding_code.strip()
        surrounding_code = ""

    # --- STRATEGY 1: Context Block Match (The "Fingerprint" Method) ---
    if surrounding_code and len(surrounding_code) > 10:
        context_lines = [line.strip() for line in surrounding_code.splitlines() if line.strip()]

        if context_lines:
            window_size = len(context_lines)
            for i in range(len(clean_file_lines) - window_size + 1):
                file_chunk = clean_file_lines[i : i + window_size]
                if file_chunk == context_lines:
                    vuln_clean = snippet.strip()
                    for offset, line in enumerate(context_lines):
                        if vuln_clean in line:
                            return i + offset + 1
                    return i + (window_size // 2) + 1

    # --- STRATEGY 2: Full snippet, then unique first line ---
    if snippet and len(snippet.strip()) > 3:
        snippet_lines = [ln.strip() for ln in snippet.splitlines() if ln.strip()]
        if snippet_lines:
            window_size = len(snippet_lines)
            if window_size > 1:
                for i in range(len(clean_file_lines) - window_size + 1):
                    if clean_file_lines[i : i + window_size] == snippet_lines:
                        return i + 1

            snippet_clean = "".join(snippet.split())
            compact_hit = _line_of_compact_snippet(clean_file_lines, snippet_clean)
            if compact_hit is not None:
                return compact_hit

            distinctive = max(snippet_lines, key=len)
            if len(distinctive) > 12:
                distinctive_compact = "".join(distinctive.split())
                hits = [
                    i
                    for i, line in enumerate(file_lines)
                    if distinctive in line or distinctive_compact in "".join(line.split())
                ]
                if len(hits) == 1:
                    return hits[0] + 1

            first_line = snippet_lines[0]
            hits = [i for i, line in enumerate(file_lines) if first_line in line]
            if len(hits) == 1:
                return hits[0] + 1

    # --- STRATEGY 3: Function Name Fallback ---
    if function_name:
        def_pat = re.compile(
            rf"^\s*(async\s+)?def\s+{re.escape(function_name)}\s*\("
        )
        js_pat = re.compile(rf"\bfunction\s+{re.escape(function_name)}\s*\(")
        for i, line in enumerate(file_lines):
            if def_pat.search(line) or js_pat.search(line):
                return i + 1
        call_pat = re.compile(rf"\b{re.escape(function_name)}\s*\(")
        for i, line in enumerate(file_lines):
            if call_pat.search(line):
                return i + 1

    return 1

def get_function_or_window(content: str, line_num: int, filename: str, window: int = 5) -> str:
    """
    Return either:
      - the full enclosing Python function (if filename ends with .py and we can detect it), OR
      - a window of `window` lines above and below the given line.

    This is what we will send back as `vulnerable_code`, so Node never gets the whole file.
    """
    lines = content.splitlines()
    total_lines = len(lines)
    if total_lines == 0:
        return ""

    # Normalize line_num to be within the file
    if line_num < 1:
        line_num = 1
    if line_num > total_lines:
        line_num = total_lines

    # --- Case A: Python function extraction ---
    if filename.endswith(".py"):
        # Walk upward to find the def line
        def_line_idx = None
        for i in range(line_num - 1, -1, -1):
            stripped = lines[i].lstrip()
            # Simple heuristic: a def line
            if stripped.startswith("def ") and "(" in stripped and stripped.rstrip().endswith(":"):
                def_line_idx = i
                break

        if def_line_idx is not None:
            # Determine indentation of the def line
            def_indent = len(lines[def_line_idx]) - len(lines[def_line_idx].lstrip())
            end_idx = def_line_idx + 1

            # Walk downward until indentation goes back to <= def_indent (and line is not blank)
            while end_idx < total_lines:
                line = lines[end_idx]
                if line.strip() == "":
                    end_idx += 1
                    continue
                indent = len(line) - len(line.lstrip())
                if indent <= def_indent:
                    break
                end_idx += 1

            # Return the function block
            return "\n".join(lines[def_line_idx:end_idx])

    # --- Case B: generic line window (for non‑Python or no def found) ---
    start = max(0, line_num - 1 - window)
    end = min(total_lines, line_num - 1 + window + 1)
    return "\n".join(lines[start:end])


def get_bounded_snippet(content: str, line_num: int, before: int = 3, after: int = 3) -> str:
    """
    Return only a small window of lines around the given line (no full function).
    Use this in Tier 3 results so we send only the relevant part, not the entire file or function.
    """
    lines = content.splitlines()
    total_lines = len(lines)
    if total_lines == 0:
        return ""
    if line_num < 1:
        line_num = 1
    if line_num > total_lines:
        line_num = total_lines
    start = max(0, line_num - 1 - before)
    end = min(total_lines, line_num - 1 + after + 1)
    return "\n".join(lines[start:end])

def build_focused_code_bundle(
    filename: str,
    full_content: str,
    tier1_result: dict,
    max_findings: int = 5,
    window: int = 20,
    extra_line_numbers: Optional[List[int]] = None,
) -> str:
    """
    Build a compact, high-context code bundle for Tier 2/3 based on Tier 1 (`CHEAP_MODEL`) findings:
    - Includes up to `max_findings` findings.
    - For each finding, include the enclosing function or a +/- `window` line window.
    - Also includes a small file header section for global context.
    - Returns a plain-text description + code slices.
    """

    findings = tier1_result.get("findings") or []
    lines = full_content.splitlines()
    total_lines = len(lines)

    # If Tier 1 found nothing, say so and encourage a broader scan decision upstream
    if not findings:
        header_preview = "\n".join(lines[: min(total_lines, 150)])
        return (
            f"Tier 1 found no specific findings in {filename}.\n"
            "The following is a header preview of the file for context:\n\n"
            f"=== FILE HEADER ({filename}:1-{min(total_lines, 150)}) ===\n"
            f"{header_preview}"
        )

    snippets: List[str] = []
    seen_snippets: Set[str] = set()

    # --- FILE HEADER CONTEXT (imports, config, routes) ---
    # Keep header small to leave room for actual findings
    header_lines = min(total_lines, 50)
    if header_lines > 0:
        header_block = "\n".join(lines[:header_lines])
        snippets.append(
            f"=== FILE HEADER ({filename}:1-{header_lines}) ===\n"
            f"{header_block}\n"
        )

    # --- EXTRA SNIPPETS FROM KEYWORD LINES (recall: include code Tier 1 might have missed) ---
    if extra_line_numbers:
        for line_num in sorted(set(extra_line_numbers))[:25]:  # cap at 25 extra regions
            if line_num < 1 or line_num > total_lines:
                continue
            snippet_body = get_function_or_window(full_content, line_num, filename, window=window)
            snippet_body = (snippet_body or "").rstrip("\n")
            if not snippet_body or snippet_body in seen_snippets:
                continue
            seen_snippets.add(snippet_body)
            snippets.append(
                f"=== SNIPPET (line {line_num}, keyword-triggered for recall) ===\n"
                f"{snippet_body}\n"
            )

    # --- FOCUSED SNIPPETS FROM TIER 1 FINDINGS ---
    for f in findings[:max_findings]:
        vuln = (f.get("vulnerable_code") or "").strip()
        func = (f.get("function_name") or "").strip()
        line_num = f.get("line")

        # If no line in Tier 1 result, try to locate it
        if not isinstance(line_num, int) or line_num <= 0:
            line_num = find_line_number(full_content, vuln, function_name=func)

        # Bound the line number
        if line_num < 1:
            line_num = 1
        if line_num > total_lines:
            line_num = total_lines

        # Use higher-context extraction: enclosing function OR +/- window lines
        snippet_body = get_function_or_window(full_content, line_num, filename, window=window)
        snippet_body = snippet_body.rstrip("\n")

        if not snippet_body:
            continue

        # De-duplicate exact snippets to avoid repeated blocks
        if snippet_body in seen_snippets:
            continue
        seen_snippets.add(snippet_body)

        snippets.append(
            f"=== SNIPPET (approx line {line_num}) for finding: {f.get('type', 'Unknown Type')} ===\n"
            f"{snippet_body}\n"
        )

    if not snippets:
        # fallback: show header only
        header_preview = "\n".join(lines[: min(total_lines, 200)])
        return (
            f"Tier 1 findings could not be mapped to concrete code ranges in {filename}.\n"
            "The following is a header preview of the file for context:\n\n"
            f"=== FILE HEADER ({filename}:1-{min(total_lines, 200)}) ===\n"
            f"{header_preview}"
        )

    meta = (
        f"Focused Tier 2/3 input for file: {filename}\n"
        f"Based on Tier 1 findings (up to {max_findings}).\n"
        f"Each snippet is either the enclosing function or a +/-{window} line window around the suspicious line.\n\n"
    )

    return meta + "\n".join(snippets)


def find_best_line_match(content: str, vulnerable_code: str, surrounding_code: str, function_name: str) -> int:
    """
    Finds the line number using a hierarchy of accuracy:
    1. Exact match of 'surrounding_code' block (Highest Confidence).
    2. Exact match of 'vulnerable_code'.
    3. Fuzzy match of 'vulnerable_code'.
    4. Function definition line.
    """
    if not content: return 1
    
    file_lines = content.splitlines()
    clean_file_lines = [line.strip() for line in file_lines] # Cache stripped lines for speed

    # --- STRATEGY 1: Context Block Match (The "Fingerprint" Method) ---
    if surrounding_code and len(surrounding_code) > 10:
        # Split LLM's context into lines and strip whitespace
        context_lines = [line.strip() for line in surrounding_code.splitlines() if line.strip()]
        
        if context_lines:
            # Sliding window search: Look for this sequence of lines in the file
            window_size = len(context_lines)
            for i in range(len(clean_file_lines) - window_size + 1):
                # Grab a chunk of the file
                file_chunk = clean_file_lines[i : i + window_size]
                
                # If the chunk matches the context lines exactly
                if file_chunk == context_lines:
                    # We found the block!
                    # Now, try to pinpoint the specific vulnerable line *inside* this block
                    vuln_clean = vulnerable_code.strip()
                    for offset, line in enumerate(context_lines):
                        if vuln_clean in line:
                            return i + offset + 1
                    
                    # If we can't find the specific line in the block, return the middle of the block
                    return i + (window_size // 2) + 1

    # --- STRATEGY 2: Exact Vulnerable Code Match ---
    if vulnerable_code and len(vulnerable_code) > 3:
        vuln_clean = vulnerable_code.strip()
        for i, line in enumerate(clean_file_lines):
            if vuln_clean == line: # Exact line match
                return i + 1
            if vuln_clean in line: # Substring match
                return i + 1

    # --- STRATEGY 3: Function Name Fallback ---
    if function_name:
        for i, line in enumerate(file_lines):
            if f"def {function_name}" in line or f"function {function_name}" in line:
                return i + 1

    return 1


def check_keywords(content: str):
    """Prefer Rust sentinai_index when built; else Python ALL_KEYWORDS scan."""
    try:
        from backend.worker.core.native_index import check_keywords as _native_check

        return _native_check(content)
    except Exception:
        content_lower = content.lower()
        found = [kw for kw in ALL_KEYWORDS if kw in content_lower]
        return found[:10]
def find_keywords_with_lines(content: str, keywords: List[str], max_hits=50):
    """Finds exact line numbers for keywords."""
    results = []
    lines = content.splitlines()
    seen = set()
    keywords_lower = [k.lower() for k in keywords]
    
    for i, line in enumerate(lines, start=1):
        line_lower = line.lower()
        if not line.strip() or line.strip().startswith(('#', '//')): continue
        
        for kw in keywords_lower:
            if kw in line_lower:
                key = (kw, i)
                if key not in seen:
                    seen.add(key)
                    results.append({"keyword": kw, "line": i, "context": line.strip()[:200]})
                    if len(results) >= max_hits: return results
    return results

def get_code_context_and_fingerprint(content: str, filename: str, line_num: int, snippet: str):
    """Extracts code window and generates a stable hash ID."""
    lines = content.splitlines()
    start = max(0, line_num - 3)
    end = min(len(lines), line_num + 2)
    
    context = {
        "before": lines[start:line_num-1],
        "target": lines[line_num-1] if line_num > 0 else "",
        "after": lines[line_num:end]
    }
    
    # Generate a short hash ID for this finding
    raw = f"{filename}:{line_num}:{snippet.strip()}".encode()
    fp = hashlib.sha1(raw).hexdigest()[:12]
    return context, fp

def normalize_openrouter_message_content(msg: Any) -> Optional[str]:
    """
    OpenAI-compatible chat completions: content may be str, null, list of {type,text},
    or absent with reasoning_* fields (OpenRouter / reasoning models).
    """
    if not isinstance(msg, dict):
        return None
    c = msg.get("content")
    if isinstance(c, str) and c.strip():
        return c
    if isinstance(c, list):
        parts: List[str] = []
        for block in c:
            if isinstance(block, dict):
                t = block.get("text")
                if isinstance(t, str) and t:
                    parts.append(t)
                elif block.get("type") == "text" and isinstance(block.get("content"), str):
                    parts.append(block["content"])
            elif isinstance(block, str):
                parts.append(block)
        if parts:
            return "".join(parts)
    for key in ("reasoning", "reasoning_content", "thinking"):
        v = msg.get(key)
        if isinstance(v, str) and v.strip():
            return v
    if c is not None and not isinstance(c, list):
        s = str(c).strip()
        return s if s else None
    return None


def clean_json_response(response_content: Optional[str]) -> str:
    """Removes markdown code blocks if present."""
    import re
    if response_content is None:
        return ""
    if not isinstance(response_content, str):
        response_content = str(response_content)
    if "```" in response_content:
        pattern = r"```(?:json)?\n?(.*?)```"
        match = re.search(pattern, response_content, re.DOTALL)
        if match:
            return match.group(1).strip()
    return response_content.strip()


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from mixed model output.
    Mirrors Claude review parser behavior:
    - Try fenced code blocks first
    - Then scan for first balanced object
    """
    try:
        json_matches = [
            re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL),
            re.search(r"```\s*(\{.*?\})\s*```", text, re.DOTALL),
        ]

        for json_match in json_matches:
            if json_match:
                try:
                    parsed = json.loads(json_match.group(1))
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    continue

        brace_count = 0
        json_start = -1
        for i, char in enumerate(text):
            if char == "{":
                if brace_count == 0:
                    json_start = i
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0 and json_start != -1:
                    candidate = text[json_start : i + 1]
                    try:
                        parsed = json.loads(candidate)
                        if isinstance(parsed, dict):
                            return parsed
                    except json.JSONDecodeError:
                        continue
    except Exception:
        return None

    return None


def parse_json_with_fallbacks(text: str, error_context: str = "") -> Tuple[bool, Dict[str, Any]]:
    """
    Parse JSON with Claude-style fallbacks.
    Returns (success, parsed_or_error_dict).
    """
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return True, parsed
    except json.JSONDecodeError:
        pass

    extracted = extract_json_from_text(text)
    if extracted is not None:
        return True, extracted

    error_msg = "Failed to parse JSON"
    if error_context:
        error_msg = f"{error_context}: {error_msg}"
    logger.error(f"{error_msg}. Raw output: {repr(text)}")
    return False, {"error": f"Invalid JSON response -- raw output: {repr(text)}"}


def _try_parse_tier3_closed(partial: str, closing: str) -> Optional[dict]:
    """Try to parse partial JSON with a given closing suffix."""
    try:
        s = partial.rstrip()
        if s.endswith(","):
            s = s[:-1].rstrip()
        return json.loads(s + closing)
    except json.JSONDecodeError:
        return None


def salvage_truncated_tier3_json(partial_json_text: str) -> Optional[dict]:
    """
    Try to recover valid Tier 3 JSON from a truncated stream by finding the last
    complete finding and closing the JSON. Avoids an extra repair LLM call when
    the stream was cut mid-response (e.g. unterminated string).
    """
    import re
    s = partial_json_text.strip()
    if not s or not s.startswith("{"):
        return None

    # Prefer: last "},\n    \"" (end of one finding, start of next)
    for pattern, closing in [
        (r"\}\s*,\s*\n\s*\"", "}]}"),   # multiple findings
        (r"\}\s*\n\s*\]", "}"),         # single finding, end of array
    ]:
        matches = list(re.finditer(pattern, s))
        if matches:
            last = matches[-1]
            if pattern == r"\}\s*,\s*\n\s*\"":
                end = last.start() + 1
            else:
                end = last.end()
            out = _try_parse_tier3_closed(s[:end], closing)
            if out is not None and isinstance(out.get("findings"), list):
                logger.info("Tier 3 salvaged valid JSON from truncated stream (no repair call).")
                return out

    # Fallback: try truncating from the end and adding "]}" until parse works
    closing = "}]}"
    for i in range(len(s), max(0, len(s) - 2000), -1):
        out = _try_parse_tier3_closed(s[:i], closing)
        if out is not None and isinstance(out.get("findings"), list):
            logger.info("Tier 3 salvaged valid JSON by truncating from end (no repair call).")
            return out
    return None

async def call_openrouter_smart_json(session, system_prompt: str, user_prompt: str):
    """
    Non-streaming JSON repair/completion (`SMART_MODEL` / deepseek-flash via bridge).
    """
    from .deepseek_client import bridge_healthy, complete, llm_configured

    if llm_configured() and await bridge_healthy(session):
        text, _model = await complete(session, "repair", system_prompt, user_prompt)
        return text

    url = OPENROUTER_API_URL
    payload = {
        "model": SMART_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "stream": False
    }
    timeout = aiohttp.ClientTimeout(total=300)

    async with session.post(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        timeout=timeout,
    ) as resp:
        if resp.status != 200:
            error = await resp.text()
            logger.error(f"OpenRouter repair call error {resp.status}: {error}")
            raise RuntimeError(f"OpenRouter repair API error {resp.status}")
        result = await resp.json()
        return result["choices"][0]["message"]["content"]


async def repair_or_complete_tier3_json(session, partial_json_text: str) -> Optional[dict]:
    """
    Given partial / invalid JSON from the streaming Tier 3 call,
    first try to salvage by truncating to the last complete finding;
        if that fails, ask `SMART_MODEL` (OpenRouter) to fix and complete it.
    Returns parsed dict or None.
    """
    salvaged = salvage_truncated_tier3_json(partial_json_text)
    if salvaged is not None:
        return salvaged

    repair_system = (
        "You are a JSON repair engine.\n"
        "You will be given a possibly truncated or invalid JSON fragment "
        "produced by another model.\n"
        "Your job is to output a SINGLE valid JSON object ONLY.\n"
        "No explanations, no markdown, no code fences.\n"
        "The schema is:\n"
        "{\n"
        "  \"status\": \"VULNERABLE or SAFE\",\n"
        "  \"findings\": [\n"
        "    {\n"
        "      \"type\": \"Vulnerability Type\",\n"
        "      \"subtype\": \"Specific Variant\",\n"
        "      \"severity\": \"HIGH/MEDIUM/LOW\",\n"
        "      \"confidence_score\": \"Integer 1-10\",\n"
        "      \"cwe_id\": \"CWE ID\",\n"
        "      \"cvss_score\": \"Float 0.0-10.0 (Estimated)\",\n"
        "      \"fix_complexity\": \"LOW/MEDIUM/HIGH\",\n"
        "      \"function_name\": \"Name of the function\",\n"
        "      \"vulnerable_code\": \"Exact code snippet\",\n"
        "      \"surrounding_code\": \"The 3 lines of code before and after\",\n"
        "      \"reason\": \"Technical explanation\",\n"
        "      \"impact_summary\": \"One sentence summary\",\n"
        "      \"consequences\": \"Detailed impact\",\n"
        "      \"remediation\": [\"Step 1\", \"Step 2\"],\n"
        "      \"references\": [\"URLs or references\"]\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "If some fields are missing, fill them with reasonable defaults "
        "and still output valid JSON."
    )

    repair_user = (
        "The previous streaming response from the model produced invalid/truncated JSON.\n"
        "Here is the raw content exactly as received (may be truncated):\n\n"
        f"{partial_json_text[:12000]}\n\n"
        "Fix and COMPLETE this into a single valid JSON object matching the schema.\n"
        "Output ONLY the JSON object, nothing else."
    )

    try:
        repaired_raw = await call_openrouter_smart_json(session, repair_system, repair_user)
    except Exception as e:
        logger.error(f"Tier 3 repair call failed: {e}")
        return None

    repaired_clean = clean_json_response(repaired_raw)
    try:
        return json.loads(repaired_clean)
    except json.JSONDecodeError as e:
        logger.error(
            f"Tier 3 repaired JSON still invalid: {e}\n"
            f"Repaired content (first 1000 chars): {repaired_clean[:1000]}..."
        )
        return None


def is_only_hardcoded_secret(triage_result: dict) -> bool:
    """
    Returns True if:
    - status is VULNERABLE (from Tier 1)
    - all findings are about hardcoded secrets (no other vuln types)
    """
    if triage_result.get("status") != "VULNERABLE":
        return False

    findings = triage_result.get("findings") or []
    if not findings:
        return False

    for f in findings:
        t = (f.get("type") or "").lower()
        # Be lenient: match either exact label or any type that clearly indicates hardcoded secrets
        if "hardcoded" not in t and "secret" not in t and "credential" not in t:
            return False

    return True
