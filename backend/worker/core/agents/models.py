"""
Agent Interface Contracts

This module defines the core data structures for the multi-agent security analysis framework.
These interfaces must be locked before specialist agents are built.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ScanMode(str, Enum):
    """Scan mode identifier."""

    FULL = "full"
    DIFF = "diff"


class Severity(str, Enum):
    """Vulnerability severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Exploitability(str, Enum):
    """Exploitability likelihood levels."""

    CONFIRMED = "confirmed"
    LIKELY = "likely"
    POSSIBLE = "possible"
    UNLIKELY = "unlikely"


# =============================================================================
# ENTRY POINTS AND ARCHITECTURE (Pre-scan context)
# =============================================================================


@dataclass
class EntryPoint:
    """
    Represents a location where untrusted external data enters the application.
    Created by Recon Agent.
    """

    entry_type: str  # "http", "cli", "mq", "file", "env", "ipc", "webhook"
    file_path: str
    line_number: int
    function_name: str
    handler_function: str
    parameters: list[str] = field(default_factory=list)
    authentication_required: bool = False
    authorization_required: bool = False
    rate_limited: bool = False
    framework: str = ""  # "express", "flask", "fastapi", etc.


@dataclass
class EntryParameter:
    """Parameter of an entry point."""

    name: str
    location: str  # "body", "query", "header", "path", "cookie"
    type_: str = "string"


@dataclass
class ArchPattern:
    """
    Architectural patterns detected in the codebase.
    Created by Pattern Agent.
    """

    pattern_type: str  # "MVC", "microservice", "monolith", etc.
    middleware_order: list[str] = field(default_factory=list)
    auth_middleware_files: list[str] = field(default_factory=list)
    orm_type: str | None = None  # "sqlalchemy", "prisma", "hibernate", etc.
    template_engine: str | None = None  # "jinja2", "handlebars", etc.
    cors_config: dict[str, Any] | None = None
    service_layer_files: list[str] = field(default_factory=list)
    repository_files: list[str] = field(default_factory=list)
    di_container: str | None = None


@dataclass
class CORSConfig:
    """CORS configuration details."""

    allow_origin: str
    allow_methods: list[str]
    allow_headers: list[str]
    expose_headers: list[str]
    max_age: int | None = None
    allow_credentials: bool = False


@dataclass
class ThreatScenario:
    """A specific threat scenario for the detected stack."""

    description: str
    priority: float  # 0.0 - 1.0
    cwe_ids: list[str] = field(default_factory=list)


@dataclass
class ThreatModel:
    """
    Framework-specific threat model.
    Created by Threat Model Agent.
    """

    stack_summary: str  # "Node.js/Express/Sequelize/JWT"
    high_priority_threats: list[ThreatScenario] = field(default_factory=list)
    framework_specific_sinks: list[str] = field(default_factory=list)
    framework_specific_sources: list[str] = field(default_factory=list)
    known_cve_patterns: list[str] = field(default_factory=list)


# =============================================================================
# DATA STRUCTURES FROM V3 (Read-only from project_indexer)
# =============================================================================


@dataclass
class SanitizerInfo:
    """Information about a sanitization function."""

    function_name: str
    file_path: str
    sanitizes: list[str]  # What it sanitizes (e.g., ["html", "sql", "shell"])


@dataclass
class DeadCodeRegion:
    """Region of unreachable code."""

    file_path: str
    line_start: int
    line_end: int
    reason: str


# =============================================================================
# AGENT CONTEXT (What every agent receives)
# =============================================================================


@dataclass
class AgentContext:
    """
    Context passed to every agent. This is the most critical interface contract.
    All agents read from this; pre-scan agents (Recon, Pattern, ThreatModel) write to it.
    """

    # Project intelligence from existing v3 indexer (read-only for specialists)
    call_graph: dict[str, list[str]] = field(default_factory=dict)
    dependency_map: dict[str, list[str]] = field(default_factory=dict)
    sanitizer_registry: dict[str, SanitizerInfo] = field(default_factory=dict)
    dead_code_map: dict[str, DeadCodeRegion] = field(default_factory=dict)

    # New context added by pre-scan agents
    entry_points: list[EntryPoint] = field(default_factory=list)
    architecture_patterns: ArchPattern | None = None
    threat_model: ThreatModel | None = None

    # File content (read-only)
    file_contents: dict[str, str] = field(default_factory=dict)
    file_asts: dict[str, Any] = field(default_factory=dict)

    # Scan metadata
    scan_id: str = ""
    repo_path: str = ""
    language: str = ""
    framework: str = ""
    scan_mode: ScanMode = ScanMode.FULL
    changed_files: list[str] = field(default_factory=list)


# =============================================================================
# AGENT FINDING (What every agent returns)
# =============================================================================


@dataclass
class AgentFinding:
    """
    A vulnerability finding produced by an agent. This is the canonical finding format.
    All agents must produce findings matching this schema.
    """

    # Identity
    finding_id: str  # UUID, generated by agent
    agent_source: str  # Which agent produced this (e.g., "InjectionSpecialist")

    # Location
    file_path: str
    line_start: int
    line_end: int
    function_name: str = ""

    # Classification
    vulnerability_class: str = ""  # CWE-aligned class name (e.g., "SQL Injection")
    cwe_id: str = ""  # e.g., "CWE-89"
    owasp_category: str = ""  # e.g., "A03:2021"

    # Severity
    severity: Severity = Severity.MEDIUM
    confidence: float = 0.0  # 0.0 - 1.0, agent's own confidence
    exploitability: Exploitability = Exploitability.POSSIBLE

    # Evidence
    vulnerable_code: str = ""  # The actual vulnerable snippet
    taint_source: str | None = None  # Where untrusted data enters
    taint_sink: str | None = None  # Where untrusted data is used dangerously
    taint_path: list[str] | None = None  # Steps between source and sink

    # Chain metadata (populated by Chain Combiner, not by specialist)
    chain_id: str | None = None  # Set if part of a chain
    chain_position: int | None = None  # Position in chain (1 = entry)

    # Reasoning
    reasoning: str = ""  # Agent's explanation of why this is vulnerable
    false_positive_indicators: list[str] = field(default_factory=list)

    # Remediation hint (basic, detailed remediation done by Remediation Agent)
    remediation_hint: str = ""

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "finding_id": self.finding_id,
            "agent_source": self.agent_source,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "function_name": self.function_name,
            "vulnerability_class": self.vulnerability_class,
            "cwe_id": self.cwe_id,
            "owasp_category": self.owasp_category,
            "severity": self.severity.value if isinstance(self.severity, Severity) else self.severity,
            "confidence": self.confidence,
            "exploitability": self.exploitability.value if isinstance(self.exploitability, Exploitability) else self.exploitability,
            "vulnerable_code": self.vulnerable_code,
            "taint_source": self.taint_source,
            "taint_sink": self.taint_sink,
            "taint_path": self.taint_path,
            "chain_id": self.chain_id,
            "chain_position": self.chain_position,
            "reasoning": self.reasoning,
            "false_positive_indicators": self.false_positive_indicators,
            "remediation_hint": self.remediation_hint,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentFinding":
        """Create AgentFinding from dictionary."""
        # Convert string severity/exploitability to enums if needed
        severity = data.get("severity")
        if isinstance(severity, str):
            try:
                severity = Severity(severity)
            except ValueError:
                severity = Severity.MEDIUM

        exploitability = data.get("exploitability")
        if isinstance(exploitability, str):
            try:
                exploitability = Exploitability(exploitability)
            except ValueError:
                exploitability = Exploitability.POSSIBLE

        return cls(
            finding_id=data.get("finding_id", ""),
            agent_source=data.get("agent_source", ""),
            file_path=data.get("file_path", ""),
            line_start=data.get("line_start", 0),
            line_end=data.get("line_end", 0),
            function_name=data.get("function_name", ""),
            vulnerability_class=data.get("vulnerability_class", ""),
            cwe_id=data.get("cwe_id", ""),
            owasp_category=data.get("owasp_category", ""),
            severity=severity,
            confidence=data.get("confidence", 0.0),
            exploitability=exploitability,
            vulnerable_code=data.get("vulnerable_code", ""),
            taint_source=data.get("taint_source"),
            taint_sink=data.get("taint_sink"),
            taint_path=data.get("taint_path"),
            chain_id=data.get("chain_id"),
            chain_position=data.get("chain_position"),
            reasoning=data.get("reasoning", ""),
            false_positive_indicators=data.get("false_positive_indicators", []),
            remediation_hint=data.get("remediation_hint", ""),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# AGENT RESULT (Wrapper returned by every agent)
# =============================================================================


@dataclass
class AgentResult:
    """
    Wrapper returned by every agent's run() method.
    Contains findings plus execution metadata.
    """

    agent_name: str
    findings: list[AgentFinding] = field(default_factory=list)
    execution_time_ms: int = 0
    token_usage: int = 0
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "agent_name": self.agent_name,
            "findings": [f.to_dict() for f in self.findings],
            "execution_time_ms": self.execution_time_ms,
            "token_usage": self.token_usage,
            "errors": self.errors,
            "metadata": self.metadata,
        }


# =============================================================================
# POST-PROCESSING RESULTS (Produced by synthesis agents)
# =============================================================================


@dataclass
class DeduplicatedFinding:
    """
    A finding after deduplication: same fields as AgentFinding plus
    contributing_agents and duplicate_count. Used by Chain Combiner and downstream.
    """

    finding_id: str
    agent_source: str
    file_path: str
    line_start: int
    line_end: int
    function_name: str = ""
    vulnerability_class: str = ""
    cwe_id: str = ""
    owasp_category: str = ""
    severity: Severity = Severity.MEDIUM
    confidence: float = 0.0
    exploitability: Exploitability = Exploitability.POSSIBLE
    vulnerable_code: str = ""
    taint_source: str | None = None
    taint_sink: str | None = None
    taint_path: list[str] | None = None
    chain_id: str | None = None
    chain_position: int | None = None
    reasoning: str = ""
    false_positive_indicators: list[str] = field(default_factory=list)
    remediation_hint: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    # Deduplication-specific
    contributing_agents: list[str] = field(default_factory=list)
    duplicate_count: int = 1

    def to_agent_finding(self) -> AgentFinding:
        """Convert to AgentFinding for pipelines that expect it."""
        return AgentFinding(
            finding_id=self.finding_id,
            agent_source=self.agent_source,
            file_path=self.file_path,
            line_start=self.line_start,
            line_end=self.line_end,
            function_name=self.function_name,
            vulnerability_class=self.vulnerability_class,
            cwe_id=self.cwe_id,
            owasp_category=self.owasp_category,
            severity=self.severity,
            confidence=self.confidence,
            exploitability=self.exploitability,
            vulnerable_code=self.vulnerable_code,
            taint_source=self.taint_source,
            taint_sink=self.taint_sink,
            taint_path=self.taint_path,
            chain_id=self.chain_id,
            chain_position=self.chain_position,
            reasoning=self.reasoning,
            false_positive_indicators=self.false_positive_indicators,
            remediation_hint=self.remediation_hint,
            metadata=self.metadata,
        )


@dataclass
class VulnerabilityChain:
    """
    Multi-hop attack chain linking individual findings.
    Created by Chain Combiner.
    """

    chain_id: str
    chain_name: str
    findings: list["DeduplicatedFinding"]  # Ordered list in chain
    entry_point: EntryPoint | None
    impact: str
    exploitability: str
    attack_narrative: str
    chain_length: int = 0


@dataclass
class AttackStep:
    """A single step in an attack path."""

    step_number: int
    action: str  # What the attacker does
    target_endpoint: str  # Which endpoint/function is targeted
    payload_type: str  # What kind of payload is used
    expected_response: str  # What the attacker expects to see
    finding_reference: str  # Which finding this step exploits


@dataclass
class AttackPath:
    """
    Concrete exploitation path from entry point to final impact.
    Created by Attack Path Simulator.
    """

    path_id: str
    entry_point: EntryPoint | None
    chains_involved: list[VulnerabilityChain]
    steps: list[AttackStep]
    final_impact: str  # "Full database read", "RCE", "Account takeover"
    attacker_prerequisites: list[str] = field(default_factory=list)
    estimated_complexity: str = "unknown"  # "trivial", "low", "medium", "high"
    proof_of_concept_outline: str = ""


@dataclass
class SkepticVerdict:
    """
    Verdict from Skeptic Agent's adversarial review.
    """

    finding_id: str
    verdict: str  # "confirmed", "downgraded", "rejected"
    confidence_adjustment: float  # Positive or negative adjustment
    skeptic_reasoning: str
    surviving_risk: str | None = None


@dataclass
class Remediation:
    """
    Remediation plan for a confirmed finding.
    Created by Remediation Agent.
    """

    finding_id: str
    fix_description: str  # Plain English explanation
    fixed_code: str  # The actual fixed code snippet
    fix_type: str  # "patch", "refactor", "config_change", "dependency_update"
    unit_test_code: str = ""  # A unit test that passes with the fix
    unit_test_framework: str = ""  # "pytest", "jest", "junit", etc.
    verification_steps: list[str] = field(default_factory=list)
    regression_risk: str = ""


@dataclass
class FuzzingHint:
    """
    Fuzzing hints for an attack path.
    Created by Fuzzing Hint Generator.
    """

    attack_path_id: str
    entry_point: str
    http_method: str
    required_parameters: list[str] = field(default_factory=list)
    injection_points: list[str] = field(default_factory=list)
    payload_templates: list[str] = field(default_factory=list)
    boundary_values: list[str] = field(default_factory=list)
    authentication_required: bool = False
    auth_setup_steps: list[str] = field(default_factory=list)
