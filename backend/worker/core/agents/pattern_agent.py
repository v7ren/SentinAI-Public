"""
PatternAgent — Identifies architectural patterns in the codebase.

Purpose:
Identifies architectural patterns so downstream agents can apply framework-specific
vulnerability knowledge rather than generic rules.

What It Detects:
- MVC pattern: Models, views, controllers and their relationships
- Middleware chains: Middleware execution order — critical for auth bypass detection
- Service layer patterns: Service classes that mediate between controllers and data
- Repository pattern: Data access objects — the taint sinks
- Dependency injection containers: How dependencies are wired
- ORM usage: SQLAlchemy, Prisma, Hibernate — affects SQLi detection
- Template engines: Jinja2, Handlebars, Pug — affects SSTI detection
- Authentication middleware: Which auth middleware and where applied
- CORS configuration: How CORS is configured
"""

import re
from typing import Any

from .base_agent import BaseAgent
from .models import AgentContext, AgentFinding, ArchPattern, CORSConfig


class PatternAgent(BaseAgent):
    """
    Pattern detection agent that identifies architectural patterns.
    """

    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        "python": {
            "flask": [r'from\s+flask\s+import', r'Flask\s*\('],
            "fastapi": [r'from\s+fastapi\s+import', r'FastAPI\s*\('],
            "django": [r'from\s+django\s+import', r'Django', r'class\s+\w+\s*\(models\.Model\)'],
            "sqlalchemy": [r'from\s+sqlalchemy\s+import', r'SessionLocal'],
            "pydantic": [r'from\s+pydantic\s+import', r'class\s+\w+\s*\(BaseModel\)'],
        },
        "javascript": {
            "express": [r'from\s+["\']express["\']', r'require\s*\(\s*["\']express["\']'],
            "nextjs": [r'from\s+["\']next["\']', r'getServerSideProps'],
            "prisma": [r'from\s+@prisma\/client', r'new\s+PrismaClient'],
            "sequelize": [r'from\s+sequelize', r'Sequence\.define'],
        },
        "java": {
            "spring": [r'@SpringBootApplication', r'@RestController', r'springframework'],
            "hibernate": [r'@Entity', r'@Table', r'jakarta\.persisten'],
        },
    }

    # Middleware detection patterns
    MIDDLEWARE_PATTERNS = {
        "express": [
            r'app\.use\s*\(\s*(?:\/\*.*?\*\/\s*)?(?:cors|auth|jsonwebtoken|express\.json|express\.urlencoded)',
            r'app\.use\s*\(\s*(?:authentication|authorize|isAdmin)',
        ],
        "flask": [
            r'@app\.before_request',
            r'@app\.teardown_request',
            r'flask\.g\.',
        ],
        "fastapi": [
            r'@app\.middleware\(http\)',
            r'app\.add_middleware',
        ],
    }

    # ORM detection
    ORM_PATTERNS = {
        "sqlalchemy": [
            r'class\s+\w+\s*\(Base\)',
            r'self\.\w+\s*=\s*Column',
            r'SeessionLocal\(\)',
        ],
        "prisma": [
            r'prisma\.\w+',
            r'PrismaClient',
        ],
        "sequelize": [
            r'Sequence\.define',
            r'sequlize\.define',
        ],
    }

    def __init__(self, *args, **kwargs):
        """Initialize PatternAgent."""
        name = kwargs.pop("name", "PatternAgent")
        super().__init__(name=name, *args, **kwargs)

    def build_prompt(self, context: AgentContext, include_file_contents: bool = True) -> str:
        """
        Build prompt for PatternAgent.

        Instructs LLM to detect:
        - MVC vs microservice patterns
        - Middleware chains and order
        - ORM and template engine usage
        - Authentication middleware location
        - CORS configuration
        """
        return f"""You are an architecture analyst tasked with identifying patterns in this codebase.

## Instructions

Identify the following architectural patterns:

1. **Architecture Pattern**: "MVC", "microservice", "monolith", "serverless"

2. **Middleware Chain** (if applicable):
   - List middleware functions in EXECUTION ORDER
   - Note which files contain auth middleware

3. **ORM Usage**:
   - sqlalchemy, prisma, sequelize, hibernate, etc.
   - Or null if no ORM detected

4. **Template Engine** (if applicable):
   - jinja2, handlebars, pug, react, vue, etc.
   - Or null if no template engine

5. **CORS Configuration**:
   - allow_origin, allow_methods, allow_headers
   - Whether credentials are allowed

6. **Service Layer**: Files containing service classes

7. **Repository Layer**: Files containing repository/data access classes

8. **Dependency Injection**: Any DI container detected (e.g., "inversify", "hilt")

## Output Format

Return a JSON object matching ArchPattern:
{{
  "pattern_type": "MVC",
  "middleware_order": ["cors", "auth", "logging"],
  "auth_middleware_files": ["middleware/auth.py"],
  "orm_type": "sqlalchemy",
  "template_engine": "jinja2",
  "cors_config": {{
    "allow_origin": "*",
    "allow_methods": ["GET", "POST"],
    "allow_headers": ["Content-Type"],
    "expose_headers": [],
    "max_age": 3600,
    "allow_credentials": false
  }},
  "service_layer_files": ["services/user_service.py"],
  "repository_files": ["repositories/user_repo.py"],
  "di_container": null
}}

## Context

Language: {context.language}
Framework: {context.framework}
"""

    def parse_response(self, response: str) -> list[AgentFinding]:
        """
        Parse LLM response and create ArchPattern.

        Returns AgentFindings that represent detected patterns.
        """
        import json

        findings = []

        try:
            data = json.loads(response)

            arch_pattern = ArchPattern(
                pattern_type=data.get("pattern_type", "unknown"),
                middleware_order=data.get("middleware_order", []),
                auth_middleware_files=data.get("auth_middleware_files", []),
                orm_type=data.get("orm_type"),
                template_engine=data.get("template_engine"),
                cors_config=data.get("cors_config"),
                service_layer_files=data.get("service_layer_files", []),
                repository_files=data.get("repository_files", []),
                di_container=data.get("di_container"),
            )

            # Create findings for each detected pattern
            finding = AgentFinding(
                finding_id=f"PATTERN-{self._generate_finding_id(data)}",
                agent_source=self.name,
                file_path="",  # Pattern spans multiple files
                line_start=0,
                line_end=0,
                function_name="",
                vulnerability_class="Architecture Pattern",
                cwe_id="",
                severity="info",
                reasoning=f"Detected architecture pattern: {arch_pattern.pattern_type}",
                metadata={"arch_pattern": arch_pattern.__dict__},
            )
            findings.append(finding)

        except json.JSONDecodeError:
            pass

        return findings

    def _generate_finding_id(self, data: dict) -> str:
        """Generate deterministic ID from pattern data."""
        import hashlib

        key = data.get("pattern_type", "unknown")
        return hashlib.md5(key.encode()).hexdigest()[:8]

    def detect_patterns_from_patterns(self, context: AgentContext) -> ArchPattern | None:
        """
        Pattern-based detection (fallback when LLM fails).

        Scans files for framework and pattern signatures.
        """
        patterns_found: dict[str, list[str]] = {}

        for file_path, content in context.file_contents.items():
            # Check framework patterns
            for lang, frameworks in self.FRAMEWORK_PATTERNS.items():
                for fw_name, fw_patterns in frameworks.items():
                    for pattern in fw_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            key = f"{lang}:{fw_name}"
                            if key not in patterns_found:
                                patterns_found[key] = []
                            patterns_found[key].append(file_path)

        # Build ArchPattern from detected patterns
        if "python:flask" in patterns_found:
            orm_type = "none"
            for pattern_list in self.ORM_PATTERNS.values():
                for pattern in pattern_list:
                    for file_path, content in context.file_contents.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            orm_type = list(self.ORM_PATTERNS.keys())[
                                list(self.ORM_PATTERNS.values()).index(pattern_list)
                            ]
                            break

            return ArchPattern(
                pattern_type="MVC",
                middleware_order=["cors", "auth"],  # Default order
                auth_middleware_files=[],  # Would need deeper analysis
                orm_type=orm_type if orm_type != "none" else None,
                template_engine="jinja2",  # Flask default
                cors_config=None,
                service_layer_files=[],
                repository_files=[],
                di_container=None,
            )

        return None

    def extract_middleware_order(self, context: AgentContext) -> list[str]:
        """
        Extract middleware execution order from code.

        Analyzes files to determine middleware chain order.
        """
        middleware_order = []

        if context.language == "javascript" and context.framework == "express":
            for file_path, content in context.file_contents.items():
                for pattern in self.MIDDLEWARE_PATTERNS["express"]:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        # Extract middleware name
                        middleware_name = self._extract_middleware_name(match.group(0))
                        if middleware_name and middleware_name not in middleware_order:
                            middleware_order.append(middleware_name)

        return middleware_order

    def _extract_middleware_name(self, match_text: str) -> str | None:
        """Extract middleware name from regex match."""
        # Common middleware names
        patterns = [
            r'cors',
            r'auth',
            r'jsonwebtoken',
            r'express\.json',
            r'express\.urlencoded',
            r'logging',
            r'rateLimit',
        ]

        for pattern in patterns:
            if re.search(pattern, match_text, re.IGNORECASE):
                return pattern

        return None


class CORSConfig:
    """Helper class to parse CORS configuration."""

    def __init__(self, allow_origin: str = "*", allow_methods: list[str] | None = None):
        self.allow_origin = allow_origin
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE"]
        self.allow_headers = ["Content-Type", "Authorization"]
        self.expose_headers: list[str] = []
        self.max_age: int | None = None
        self.allow_credentials = False

    @classmethod
    def from_config(cls, config: dict) -> "CORSConfig":
        """Create CORSConfig from configuration dictionary."""
        return cls(
            allow_origin=config.get("allow_origin", "*"),
            allow_methods=config.get("allow_methods"),
        )
