"""
ReconAgent — Maps entry points where untrusted data enters the application.

Purpose:
Maps every location where untrusted external data can enter the application.
This is the foundation for taint analysis — if you don't know where data enters,
you can't trace where it goes.

What It Detects:
- HTTP route handlers: Express routes, Flask routes, FastAPI endpoints, Django views, Spring controllers
- API endpoints: REST, GraphQL resolvers, gRPC handlers
- CLI argument parsers: argparse, click, cobra, clap
- Message queue consumers: Kafka consumers, RabbitMQ handlers, SQS listeners
- File readers: Any code that reads from disk where the path is externally influenced
- Environment variable readers: os.environ, process.env
- Database query results used as control flow: Second-order injection sources
- Webhook handlers: Incoming webhook processors
- IPC handlers: Unix socket readers, named pipe readers
"""

import re
from typing import Any

from .base_agent import BaseAgent
from .models import AgentContext, AgentFinding, EntryPoint, EntryParameter


class ReconAgent(BaseAgent):
    """
    Reconnaissance agent that maps all entry points in the application.
    """

    # Framework-specific route patterns
    FRAMEWORK_PATTERNS = {
        "python": {
            "flask": [
                r'@\w+\s*\(\s*["\']([^"\']+)["\']\s*\)',  # @app.route('/path')
                r'def\s+(\w+)\s*\([^)]*request[^)]*\)',  # def view(request):
            ],
            "fastapi": [
                r'@(\w+)\s*\(\s*["\']([^"\']+)["\']\s*\)',  # @app.get('/path')
                r'async\s+def\s+(\w+)\s*\([^)]*request[^)]*\)',  # async def view(request):
                r'def\s+(\w+)\s*\([^)]*request[^)]*\)',  # def view(request):
            ],
            "django": [
                r'def\s+(\w+)\s*\([^)]*request[^)]*\)',  # def view(request):
                r'@(?:method_decorator|require_\w+)\s*\(',  # @require_http_methods
            ],
            "python_generic": [
                r'request\.(args|form|json|data|cookies|headers)\[',  # request['param']
                r'request\.(args|form|json|data|cookies|headers)\.get\(',  # request.get('param')
            ],
        },
        "javascript": {
            "express": [
                r'app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']\s*,',  # app.get('/path', handler)
                r'r\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']\s*,',  # router.get('/path', handler)
                r'async\s*\(?\s*req\s*,?\s*res\s*\)?\s*=>',  # async (req, res) =>
                r'function\s*\(\s*req\s*,?\s*res\s*\)',  # function(req, res)
            ],
            "fastify": [
                r'server\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']\s*,',
                r'fastify\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']\s*,',
            ],
            "node_generic": [
                r'req\.(body|params|query|headers|cookies|file)\[',
                r'req\.(body|params|query|headers|cookies|file)\.get\(',
            ],
        },
        "java": {
            "spring": [
                r'@(?:GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\s*\(\s*["\']([^"\']+)["\']',
                r'public\s+(?:async\s+)?\w+\s+(\w+)\s*\([^)]*HttpServletRequest',
            ],
        },
        "go": {
            "gorilla": [
                r'mux\.NewRouter\(\)\.([A-Za-z]+)\s*\(\s*["\']([^"\']+)["\']\s*,',
                r'func\s+(\w+)\s*\(\s*w\s+http\.ResponseWriter,\s*r\s*\*http\.Request',
            ],
        },
    }

    # Entry point type detection patterns
    ENTRY_TYPE_PATTERNS = {
        "http": [
            r'request\.(body|params|query|headers|cookies|args|form|json)',
            r'req\.(body|params|query|headers|cookies)',
        ],
        "cli": [
            r'argparse\.ArgumentParser',
            r'click\.\(.*@click\.command',
            r'cobra\.Command',
            r'parser\.add_argument',
        ],
        "mq": [
            r'kafka\.Consumer',
            r'RabbitMQ',
            r'pika\.BasicConsumer',
            r'sqs\.receive_message',
            r'@\.subscribe',  # Firebase, etc.
        ],
        "file": [
            r'open\s*\([^)]*\+',  # open(filename + user_input)
            r'os\.path\.(join|join)\s*\([^)]*\+',
            r'pathlib\.Path\s*\([^)]*\+',
        ],
        "env": [
            r'os\.environ\[[\'"]',
            r'os\.getenv\s*\(',
            r'process\.env\.',
        ],
        "webhook": [
            r'webhook',
            r'callback',
            r'webhook_handler',
        ],
    }

    def __init__(self, *args, **kwargs):
        """Initialize ReconAgent."""
        name = kwargs.pop("name", "ReconAgent")
        super().__init__(name=name, *args, **kwargs)

    def build_prompt(self, context: AgentContext, include_file_contents: bool = True) -> str:
        """
        Build prompt for ReconAgent.

        Instructs LLM to:
        - Act as a penetration tester mapping the attack surface
        - Look specifically for all locations where request.*, req.*, ctx.*, args.* are accessed
        - Flag any entry point that lacks authentication as high-priority
        """
        return f"""You are a penetration tester tasked with mapping the attack surface of this application.
Your job is to identify every location where untrusted external data can enter the system.

## Instructions

1. Identify all ENTRY POINTS where external data enters:
   - HTTP routes (REST APIs, GraphQL endpoints, web hooks)
   - CLI argument parsers
   - Message queue consumers (Kafka, RabbitMQ, SQS)
   - File path readers (where path comes from user input)
   - Environment variable readers (os.environ, process.env)
   - IPC handlers

2. For each entry point, determine:
   - entry_type: "http", "cli", "mq", "file", "env", "ipc", "webhook"
   - file_path: Source file where entry point is defined
   - line_number: Line number of the route/handler definition
   - function_name: Name of the handler function
   - handler_function: The actual function that processes the request
   - parameters: List of parameter names that accept external data
   - authentication_required: True if auth middleware is applied BEFORE this route
   - authorization_required: True if permission checks exist
   - rate_limited: True if rate limiting is configured
   - framework: Detected framework (express, flask, fastapi, django, spring, etc.)

3. Pay special attention to:
   - Routes WITHOUT authentication (flag as HIGH priority)
   - Request parameters from user-controlled sources (req.body, req.params, query strings)
   - Indirect data sources (environment variables, config files, message queues)

## Output Format

Return a JSON array of EntryPoint objects:
[
  {{
    "entry_type": "http",
    "file_path": "routes/api.py",
    "line_number": 42,
    "function_name": "login",
    "handler_function": "handle_login",
    "parameters": ["username", "password"],
    "authentication_required": false,
    "authorization_required": false,
    "rate_limited": true,
    "framework": "flask"
  }}
]

## Context

Language: {context.language}
Framework: {context.framework}

Files analyzed: {list(context.file_contents.keys())[:10]}...

Scan mode: {context.scan_mode.value}
"""

    def parse_response(self, response: str) -> list[AgentFinding]:
        """
        Parse LLM response into AgentFinding objects.

        Converts EntryPoint objects to AgentFindings with entry point metadata.
        """
        import json

        findings = []

        try:
            data = json.loads(response)

            # Handle both direct list and wrapped response
            if isinstance(data, dict) and "entry_points" in data:
                entry_points = data["entry_points"]
            elif isinstance(data, list):
                entry_points = data
            else:
                return findings

            for ep_data in entry_points:
                # Convert EntryPoint to AgentFinding
                finding = AgentFinding(
                    finding_id=f"RECON-{self._generate_finding_id(ep_data)}",
                    agent_source=self.name,
                    file_path=ep_data.get("file_path", ""),
                    line_start=ep_data.get("line_number", 0),
                    line_end=ep_data.get("line_number", 0) + 1,
                    function_name=ep_data.get("function_name", ""),
                    vulnerability_class="Entry Point",
                    cwe_id="CWE-200" if not ep_data.get("authentication_required", True) else "",
                    severity="high" if not ep_data.get("authentication_required", True) else "info",
                    reasoning=f"Entry point detected: {ep_data.get('entry_type', 'unknown')}",
                    taint_source=self._identify_taint_source(ep_data),
                    metadata={
                        "entry_point": {
                            "entry_type": ep_data.get("entry_type"),
                            "parameters": ep_data.get("parameters", []),
                            "authentication_required": ep_data.get("authentication_required", False),
                            "authorization_required": ep_data.get("authorization_required", False),
                        }
                    },
                )
                findings.append(finding)

        except json.JSONDecodeError as e:
            # Return empty list on parse failure
            pass

        return findings

    def run(self, context: AgentContext) -> Any:
        """
        Override run() to return EntryPoint list in addition to AgentResult.

        Returns a tuple: (AgentResult, list[EntryPoint])
        """
        result = super().run(context)

        # Extract entry points from findings
        entry_points = []
        for finding in result.findings:
            if "entry_point" in finding.metadata:
                ep_data = finding.metadata["entry_point"]
                ep = EntryPoint(
                    entry_type=ep_data.get("entry_type", "unknown"),
                    file_path=finding.file_path,
                    line_number=finding.line_start,
                    function_name=finding.function_name,
                    handler_function=finding.function_name,
                    parameters=ep_data.get("parameters", []),
                    authentication_required=ep_data.get("authentication_required", False),
                    authorization_required=ep_data.get("authorization_required", False),
                    rate_limited=ep_data.get("rate_limited", False),
                    framework=context.framework,
                )
                entry_points.append(ep)

        return result, entry_points

    def _generate_finding_id(self, ep_data: dict) -> str:
        """Generate deterministic finding ID from entry point data."""
        import hashlib

        key = f"{ep_data.get('file_path', '')}:{ep_data.get('line_number', 0)}:{ep_data.get('function_name', '')}"
        return hashlib.md5(key.encode()).hexdigest()[:8]

    def _identify_taint_source(self, ep_data: dict) -> str | None:
        """Identify the taint source for this entry point."""
        params = ep_data.get("parameters", [])
        if not params:
            return None

        entry_type = ep_data.get("entry_type", "http")

        # Map entry type to parameter location
        location_map = {
            "http": "req.{}".format(params[0] if params else "body"),
            "cli": "args.{}".format(params[0] if params else "input"),
            "mq": "message.body.{}".format(params[0] if params else "data"),
            "file": "user_provided_path",
            "env": "os.environ.{}".format(params[0] if params else "VAR"),
        }

        return location_map.get(entry_type, "unknown_source")

    def detect_entry_points_from_patterns(self, context: AgentContext) -> list[EntryPoint]:
        """
        Pattern-based entry point detection (fallback when LLM fails).

        Scans all files in context for framework-specific patterns.
        """
        entry_points = []

        for file_path, content in context.file_contents.items():
            detected = self._scan_file_for_entry_points(file_path, content, context)
            entry_points.extend(detected)

        return entry_points

    def _scan_file_for_entry_points(
        self, file_path: str, content: str, context: AgentContext
    ) -> list[EntryPoint]:
        """Scan a single file for entry point patterns."""
        entry_points = []
        lines = content.split("\n")

        # Get language-specific patterns
        lang = context.language
        patterns = self.FRAMEWORK_PATTERNS.get(lang, {}).get(
            context.framework, self.FRAMEWORK_PATTERNS.get(lang, {}).get("generic", [])
        )

        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Extract function name if available
                    function_name = match.group(1) if match.lastindex and match.lastindex >= 1 else f"handler_{line_num}"

                    entry_point = EntryPoint(
                        entry_type="http",
                        file_path=file_path,
                        line_number=line_num,
                        function_name=function_name,
                        handler_function=function_name,
                        parameters=[],
                        authentication_required=False,
                        authorization_required=False,
                        rate_limited=False,
                        framework=context.framework,
                    )
                    entry_points.append(entry_point)
                    break  # One entry point per line

        return entry_points
