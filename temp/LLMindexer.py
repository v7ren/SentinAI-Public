import os
import sys
import json
import time
import textwrap
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import requests

load_dotenv()


DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
DEEPINFRA_MODEL = os.environ.get("DEEPINFRA_MODEL", "openai/gpt-oss-120b")

# Chunking / indexing
MAX_FILE_CHARS = 24000
CHUNK_LINES = 120

INDEXER_CHAT_MAX_RETRIES = int(os.environ.get("LLM_INDEXER_CHAT_RETRIES", "3"))
INDEXER_CHAT_BACKOFF_SEC = float(os.environ.get("LLM_INDEXER_CHAT_BACKOFF", "2"))

CODE_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rb",
    ".php",
    ".rs",
    ".cs",
)

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".idea",
    ".vscode",
}

MAX_WORKERS = int(os.environ.get("LLM_INDEXER_THREADS", "10"))
WIKI_MAX_WORKERS = int(os.environ.get("WIKI_THREADS", "5"))

###############################################################################
# DeepInfra client
###############################################################################

class DeepInfraClient:
    """
    Minimal OpenAI-compatible client for DeepInfra.
    """

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise RuntimeError("DEEPINFRA_API_KEY is not set")
        self.api_key = api_key
        self.model = model
        self.url = "https://api.deepinfra.com/v1/openai/chat/completions"

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.1,
        json_mode: bool = False,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        resp = requests.post(self.url, headers=headers, json=payload, timeout=120)
        if resp.status_code != 200:
            raise RuntimeError(f"DeepInfra error: {resp.status_code} {resp.text}")

        data = resp.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Unexpected DeepInfra response: {data}") from e
        return content

    def chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """
        Call DeepInfra and parse JSON response, with a simple repair heuristic.
        """
        raw = self.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=True,
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            cleaned = raw.strip()
            if "{" in cleaned and "}" in cleaned:
                cleaned = cleaned[cleaned.index("{") : cleaned.rindex("}") + 1]
                return json.loads(cleaned)
            raise

###############################################################################
# Indexer
###############################################################################

class LLMProjectIndexer:
    """
    Folder-based, threaded indexer.

    Produces:
    project_ir = {
        "root_path": "...",
        "files": {
          "path/to/file.py": {
            "language": "...",
            "file_summary": "...",
            "main_concerns": [...],
            "suspected_entrypoints": [...],
            "chunks": [
              {
                "chunk_id": "file.py:1-120",
                "start_line": 1,
                "end_line": 120,
                "summary": "...",
                "tags": [...],
                "http_endpoint": {...},
                "ws_handler": {...}
              },
              ...
            ]
          }
        }
    }
    """

    def __init__(self, root_path: str, client: DeepInfraClient):
        self.root_path = os.path.abspath(root_path)
        self.client = client
        self.project_ir: Dict[str, Any] = {
            "root_path": self.root_path,
            "files": {},
        }

    # --------------------- discovery & basic utilities ---------------------

    def _is_code_file(self, rel_path: str) -> bool:
        return rel_path.endswith(CODE_EXTENSIONS)

    def discover_files(self) -> List[str]:
        files: List[str] = []
        for root, dirs, filenames in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in filenames:
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, self.root_path)
                if self._is_code_file(rel):
                    files.append(rel)
        return sorted(files)

    def _read_file(self, rel_path: str) -> str:
        full = os.path.join(self.root_path, rel_path)
        with open(full, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def detect_language(self, rel_path: str) -> str:
        lower = rel_path.lower()
        if lower.endswith(".py"):
            return "python"
        if lower.endswith((".js", ".jsx", ".ts", ".tsx")):
            return "javascript"
        if lower.endswith(".java"):
            return "java"
        if lower.endswith(".go"):
            return "go"
        if lower.endswith(".rb"):
            return "ruby"
        if lower.endswith(".php"):
            return "php"
        if lower.endswith(".rs"):
            return "rust"
        if lower.endswith(".cs"):
            return "csharp"
        return "text"

    def chunk_file(self, content: str, max_lines: int = CHUNK_LINES) -> List[Dict[str, Any]]:
        lines = content.splitlines()
        chunks: List[Dict[str, Any]] = []
        start = 0
        while start < len(lines):
            end = min(start + max_lines, len(lines))
            chunk_text = "\n".join(lines[start:end])
            chunks.append(
                {
                    "start_line": start + 1,
                    "end_line": end,
                    "text": chunk_text,
                }
            )
            start = end
        return chunks

    # ----------------------------- prompts --------------------------------

    def _file_summary_prompt(self, rel_path: str, language: str, content: str) -> str:
        trimmed = content[:MAX_FILE_CHARS]
        return textwrap.dedent(
            f"""
            You are a code comprehension assistant.

            You are given the full contents of a single source file from a codebase.
            Your job is to produce a JSON description of what this file does.

            Rules:
            - Only describe behavior that is clearly present in the code.
            - If you are unsure about something, omit it or mark it as null.
            - DO NOT invent endpoints or functions that are not present.
            - Output valid JSON ONLY, no comments or extra text.

            Return JSON with this exact structure:

            {{
              "file_summary": "short paragraph describing this file's purpose",
              "main_concerns": [
                "auth / login / session / jwt / oauth / permissions if applicable",
                "database querying / orm models if applicable",
                "external http calls (apis, webhooks, etc) if applicable",
                "filesystem operations if applicable",
                "message queues, redis, kafka, websockets if applicable"
              ],
              "suspected_entrypoints": [
                {{
                  "kind": "http_endpoint | ws_handler | cli | main | library",
                  "name": "symbol name or description",
                  "details": "short explanation"
                }}
              ]
            }}

            File path: {rel_path}
            Language: {language}

            Code:
            {trimmed}
            """
        ).strip()

    def _chunk_summary_prompt(
        self,
        rel_path: str,
        language: str,
        chunk_text: str,
        start_line: int,
        end_line: int,
    ) -> str:
        return textwrap.dedent(
            f"""
            You are a code indexing assistant.

            You are given a contiguous chunk of code from a single file.
            Your task is to produce a JSON description of this chunk that can be used
            for building a project index map.

            Rules:
            - Only talk about behavior that appears in THIS chunk.
            - DO NOT invent functions, routes, or behavior that is not in this code.
            - If you see HTTP routes, websockets, or other clear entrypoints, describe them.
            - If unsure, use null or empty lists.
            - Output valid JSON ONLY, no comments or extra text.

            Return JSON with this exact structure:

            {{
              "chunk_id": "unique identifier for this chunk (e.g. '{rel_path}:{start_line}-{end_line}')",
              "start_line": {start_line},
              "end_line": {end_line},
              "summary": "one short paragraph explaining what this chunk does",
              "tags": [
                "auth",
                "db",
                "network",
                "file_io",
                "crypto",
                "process",
                "config",
                "testing",
                "logging",
                "ws",
                "security",
                "other"
              ],
              "http_endpoint": {{
                "method": "GET|POST|PUT|DELETE|PATCH|WS|null",
                "path": "string or null",
                "framework": "flask|fastapi|express|django|aiohttp|other|unknown|null",
                "notes": "short explanation or null"
              }},
              "ws_handler": {{
                "path": "string or null",
                "expects_auth": "boolean or null",
                "message_types": ["string", "..."]
              }}
            }}

            Fill fields as accurately as you can based ONLY on the code below.

            File: {rel_path}
            Language: {language}
            Lines: {start_line}-{end_line}

            Code chunk:
            {chunk_text}
            """
        ).strip()

    # ------------------------- per-file indexing --------------------------

    def _chat_json_with_retry(self, system_prompt: str, user_prompt: str, label: str = "") -> Dict[str, Any]:
        """Call client.chat_json with retries on connection errors."""
        last_err = None
        for attempt in range(INDEXER_CHAT_MAX_RETRIES):
            try:
                return self.client.chat_json(system_prompt, user_prompt)
            except Exception as e:
                last_err = e
                if attempt < INDEXER_CHAT_MAX_RETRIES - 1:
                    wait = INDEXER_CHAT_BACKOFF_SEC * (attempt + 1)
                    print(f"[!] {label or 'LLM'} attempt {attempt + 1}/{INDEXER_CHAT_MAX_RETRIES} failed: {e}. Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    raise
        raise last_err

    def index_file(self, rel_path: str) -> Dict[str, Any]:
        """
        Index a single file and return its IR.
        """
        content = self._read_file(rel_path)
        language = self.detect_language(rel_path)
        system_prompt = (
            "You are a careful code analysis model. "
            "Always return STRICTLY valid JSON that matches the requested schema."
        )

        print(f"[+] Indexing file: {rel_path}")

        # File-level
        file_prompt = self._file_summary_prompt(rel_path, language, content)
        try:
            file_json = self._chat_json_with_retry(system_prompt, file_prompt, label=f"File-level {rel_path}")
        except Exception as e:
            print(f"[!] File-level summary failed for {rel_path}: {e}")
            file_json = {
                "file_summary": "",
                "main_concerns": [],
                "suspected_entrypoints": [],
            }

        # Chunk-level
        chunks = self.chunk_file(content)
        chunk_entries: List[Dict[str, Any]] = []

        for ch in chunks:
            start_line = ch["start_line"]
            end_line = ch["end_line"]
            chunk_text = ch["text"]

            chunk_prompt = self._chunk_summary_prompt(
                rel_path, language, chunk_text, start_line, end_line
            )

            try:
                chunk_json = self._chat_json_with_retry(
                    system_prompt, chunk_prompt,
                    label=f"Chunk {rel_path}:{start_line}-{end_line}"
                )
                if not chunk_json.get("chunk_id"):
                    chunk_json["chunk_id"] = f"{rel_path}:{start_line}-{end_line}"
                if "start_line" not in chunk_json:
                    chunk_json["start_line"] = start_line
                if "end_line" not in chunk_json:
                    chunk_json["end_line"] = end_line
            except Exception as e:
                print(
                    f"[!] Chunk-level summary failed for {rel_path}:{start_line}-{end_line}: {e}"
                )
                chunk_json = {
                    "chunk_id": f"{rel_path}:{start_line}-{end_line}",
                    "start_line": start_line,
                    "end_line": end_line,
                    "summary": "",
                    "tags": [],
                    "http_endpoint": {
                        "method": None,
                        "path": None,
                        "framework": None,
                        "notes": None,
                    },
                    "ws_handler": {
                        "path": None,
                        "expects_auth": None,
                        "message_types": [],
                    },
                }

            chunk_entries.append(chunk_json)
            # Per-thread pacing
            time.sleep(0.2)

        file_ir = {
            "language": language,
            "file_summary": file_json.get("file_summary", ""),
            "main_concerns": file_json.get("main_concerns", []),
            "suspected_entrypoints": file_json.get("suspected_entrypoints", []),
            "chunks": chunk_entries,
        }
        return file_ir

    # ------------------------ project-wide indexing -----------------------

    def build_index(self) -> None:
        files = self.discover_files()
        print(f"[+] Found {len(files)} code files under {self.root_path}")
        if not files:
            return

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_file = {
                executor.submit(self.index_file, rel): rel for rel in files
            }

            for future in as_completed(future_to_file):
                rel_path = future_to_file[future]
                try:
                    file_ir = future.result()
                    self.project_ir["files"][rel_path] = file_ir
                except Exception as e:
                    print(f"[!] Failed to index {rel_path}: {e}")

    def to_json(self) -> str:
        return json.dumps(self.project_ir, indent=2)

###############################################################################
# Wiki generation (DeepWiki-style synthesis)
###############################################################################

class WikiGenerator:
    """
    Takes the project_ir and produces a set of markdown wiki pages.

    Pages:
    - wiki_overview.md
    - wiki_architecture.md
    - wiki_<dynamic_section_id>.md (0-4 extra sections)
    """

    def __init__(self, client: DeepInfraClient, project_ir: Dict[str, Any]):
        self.client = client
        self.project_ir = project_ir

    def _collect_snippets(self) -> Dict[str, str]:
        """
        Generic: collapse all file+chunk summaries into one big text blob.
        The LLM will decide how to structure documentation based on this.
        """
        files = self.project_ir.get("files", {})
        snippets: List[str] = []

        for path, info in files.items():
            summary = info.get("file_summary", "")
            main_concerns = info.get("main_concerns", [])
            suspected = info.get("suspected_entrypoints", [])
            chunks = info.get("chunks", [])

            chunk_summaries = [
                f"{c.get('chunk_id')}: {c.get('summary', '')} [tags={c.get('tags', [])}]"
                for c in chunks
            ]

            combined = "\n".join(
                [
                    f"FILE: {path}",
                    f"SUMMARY: {summary}",
                    f"MAIN_CONCERNS: {main_concerns}",
                    f"ENTRYPOINTS: {suspected}",
                    "CHUNKS:",
                    *chunk_summaries,
                    "",
                ]
            )
            snippets.append(combined)

        return {"all": "\n".join(snippets)}

    def _generate_toc(self, raw_index_text: str) -> Dict[str, Any]:
        """
        Ask the LLM to propose documentation sections based on the index.

        Returns JSON like:
        {
          "sections": [
            {"id": "overview", "title": "Overview", "description": "..."},
            {"id": "architecture", "title": "Architecture", "description": "..."},
            {"id": "key_components", "title": "Key Components", "description": "..."},
            ...
          ]
        }
        """
        system_prompt = (
            "You are designing a documentation structure for a codebase, based on a project index. "
            "You MUST output STRICT JSON, no markdown, no explanations."
        )

        user_prompt = textwrap.dedent(
            f"""
            You are given an LLM-derived project index (file summaries, entrypoints, chunk summaries).

            1. Propose a small table of contents for technical documentation.
            2. You MUST include at least these two sections:
               - A high-level "Overview"
               - An "Architecture" style section about how the system is structured and how data/requests flow
            3. You may add up to 4 more sections whose names make sense for THIS project
               (e.g. "Key Components", "Gameplay Systems", "Data Layer", "Frontend", "API Reference").
            4. Section IDs must be simple lowercase identifiers with underscores, e.g. "overview", "architecture", "key_components".
            5. Titles should be human-readable.

            IMPORTANT:
            - Do NOT assume this is a web server; infer the domain from the index.
            - Only propose sections that are justified by the provided index.
            - Total sections: minimum 2 (overview, architecture), maximum 6.

            Return JSON ONLY in this format:

            {{
              "sections": [
                {{
                  "id": "overview",
                  "title": "Overview",
                  "description": "Short sentence about what this section will cover"
                }},
                {{
                  "id": "architecture",
                  "title": "Architecture and Data Flow",
                  "description": "..."
                }}
              ]
            }}

            Here is the project index:

            {raw_index_text}
            """
        ).strip()

        raw = self.client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=1024,
            temperature=0.2,
            json_mode=True,
        )

        try:
            toc = json.loads(raw)
        except json.JSONDecodeError:
            cleaned = raw.strip()
            if "{" in cleaned and "}" in cleaned:
                cleaned = cleaned[cleaned.index("{"): cleaned.rindex("}") + 1]
                toc = json.loads(cleaned)
            else:
                raise

        # Ensure overview + architecture are present
        ids = {s.get("id") for s in toc.get("sections", []) if isinstance(s, dict)}

        def ensure_section(sec_id, title, desc):
            nonlocal toc, ids
            if sec_id not in ids:
                toc.setdefault("sections", []).insert(0, {
                    "id": sec_id,
                    "title": title,
                    "description": desc,
                })
                ids.add(sec_id)

        ensure_section(
            "overview",
            "Overview",
            "High-level overview of what the project is and what it does."
        )
        ensure_section(
            "architecture",
            "Architecture",
            "How the project is structured internally and how data/requests flow."
        )

        # De-duplicate by id while preserving order, and enforce max 6 sections
        seen = set()
        cleaned_sections = []
        for s in toc.get("sections", []):
            sec_id = s.get("id")
            if not sec_id or sec_id in seen:
                continue
            seen.add(sec_id)
            cleaned_sections.append(s)
        toc["sections"] = cleaned_sections[:6]

        return toc

    def _wiki_prompt(self, section_id: str, title: str, description: str, raw_snippets: str) -> str:
        """
        Build the prompt for a single wiki section, using generic instructions,
        with special treatment for overview/architecture.
        """
        base_intro = textwrap.dedent(
            """
            You are generating high-level documentation for a codebase.
            You are given an LLM-derived project index: per-file summaries, entrypoints,
            and chunk summaries (with tags).

            Your task is to write a clear, opinionated markdown document for ONE section
            of the documentation. You must:
            - Base your answers ONLY on the provided summaries.
            - Be concrete and map concepts back to file names and key entities/functions.
            - Avoid hallucinating technologies or components that are not mentioned.
            - Use headings, bullet lists, and short paragraphs.
            - Explain flows and interactions between components, not just listing files.
            """
        ).strip()

        if section_id == "overview":
            extra = textwrap.dedent(
                """
                This is the high-level Overview section. Explain:
                - What the project is and what problem it solves.
                - The main components or modules at a very high level.
                - A typical usage or runtime scenario in broad strokes.
                - Where to look next (other sections) for deeper details.
                """
            ).strip()
        elif section_id == "architecture":
            extra = textwrap.dedent(
                """
                This is the Architecture section. Explain:
                - The main architectural components (modules, services, subsystems).
                - How data and control flow between them.
                - Any important patterns (e.g., MVC, event-driven, layered, client/server).
                - Reference specific files and important functions or classes where relevant.
                """
            ).strip()
        else:
            extra = textwrap.dedent(
                f"""
                This section is titled "{title}". Use the description below as guidance:
                "{description}"

                Focus on this theme specifically, and organize content with clear headings.
                """
            ).strip()

        return (
            f"{base_intro}\n\n"
            f"Section ID: {section_id}\n"
            f"Section Title: {title}\n\n"
            f"{extra}\n\n"
            f"Here is the project index subset for this section:\n\n{raw_snippets}"
        )

    def generate_section(self, section_id: str, title: str, description: str, raw_snippets: str) -> str:
        if not raw_snippets.strip():
            return f"# {title}\n\n_No relevant information found in index._\n"

        system_prompt = (
            "You are a senior engineer turning a project index into clear documentation. "
            "Write high-quality markdown with headings and lists. Do not hallucinate APIs."
        )
        user_prompt = self._wiki_prompt(section_id, title, description, raw_snippets)
        md = self.client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=4096,
            temperature=0.2,
            json_mode=False,
        )
        return md

    def generate_all(self, out_dir: str) -> List[str]:
        os.makedirs(out_dir, exist_ok=True)
        snippets = self._collect_snippets()
        all_text = snippets.get("all", "")

        # 1) Ask LLM to propose sections (TOC)
        # 'sections' contains the logical order: [Overview, Architecture, Security...]
        print("[+] Generating dynamic table of contents...")
        toc = self._generate_toc(all_text)
        sections = toc.get("sections", [])
        print(f"[+] Sections chosen by LLM: {[s.get('id') for s in sections]}")

        if not sections:
            print("[!] No sections returned from TOC generation, aborting wiki generation.")
            return []

        # 2) Generate each section in parallel
        def generate_one_section(section: Dict[str, Any]) -> None:
            sec_id = section.get("id")
            title = section.get("title", sec_id.title() if sec_id else "Section")
            desc = section.get("description", "")
            filename = f"wiki_{sec_id}.md" if sec_id else "wiki_section.md"

            print(f"[+] Generating wiki section: {sec_id} ({title})")
            md = self.generate_section(sec_id, title, desc, all_text)
            out_path = os.path.join(out_dir, filename)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"[+] Wrote {out_path}")

        # Execute in parallel (Order of completion is random, and that's fine)
        max_workers = min(len(sections), WIKI_MAX_WORKERS or 1)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(generate_one_section, s) for s in sections]
            
            # Wait for ALL to finish
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"[!] A section failed to generate: {e}")

        # 3) Construct the return list based on the ORIGINAL TOC ORDER
        # This ensures Overview is first, Architecture is second, etc.
        ordered_files = []
        for section in sections:
            sec_id = section.get("id")
            if sec_id:
                filename = f"wiki_{sec_id}.md"
                # Verify file exists before adding (in case a thread failed)
                if os.path.exists(os.path.join(out_dir, filename)):
                    ordered_files.append(filename)

        return ordered_files


###############################################################################
# CLI
###############################################################################

def main():
    if len(sys.argv) < 4:
        print(
            "Usage:\n"
            "  python deepwiki_like_indexer.py /path/to/project index.json wiki_out_dir/\n\n"
            "Env:\n"
            "  DEEPINFRA_API_KEY       (required)\n"
            "  DEEPINFRA_MODEL         (optional, default=openai/gpt-oss-120b)\n"
            "  LLM_INDEXER_THREADS     (optional, default=4)\n"
        )
        sys.exit(1)

    folder_path = sys.argv[1]
    index_path = sys.argv[2]
    wiki_dir = sys.argv[3]

    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a directory")
        sys.exit(1)

    if not DEEPINFRA_API_KEY:
        print("Error: DEEPINFRA_API_KEY is not set")
        sys.exit(1)

    print(f"[+] Using model: {DEEPINFRA_MODEL}")
    print(f"[+] Using up to {MAX_WORKERS} threads for indexing")

    client = DeepInfraClient(DEEPINFRA_API_KEY, DEEPINFRA_MODEL)

    # Phase 1: Index
    indexer = LLMProjectIndexer(folder_path, client)
    indexer.build_index()

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(indexer.to_json())
    print(f"[+] Index written to {index_path}")

    # Phase 2: Wiki generation
    project_ir = indexer.project_ir
    wiki = WikiGenerator(client, project_ir)
    wiki.generate_all(wiki_dir)
    print(f"[+] Wiki pages written to {wiki_dir}")

if __name__ == "__main__":
    main()
