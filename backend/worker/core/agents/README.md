# Multi-Agent Security Analysis Framework

This directory contains the core multi-agent infrastructure for SentinAI v3's expansion.

## Architecture Overview

The multi-agent system follows a strict execution order:

```
PRE-SCAN (sequential — each enriches context)
├── ReconAgent           → populates entry_points
├── PatternAgent         → populates architecture_patterns
└── ThreatModelAgent     → populates threat_model

DETECTION (parallel — all receive same enriched context)
├── InjectionSpecialist
├── AuthSpecialist
├── CryptoSpecialist
├── CipherDesignSpecialist
├── LogicAnalyst
└── ConfigHunter

SYNTHESIS (sequential — order is mandatory)
├── DeduplicationEngine  → clean finding set
├── ChainCombiner        → build chains from findings
├── AttackPathSimulator  → simulate paths from validated chains
└── ConsensusScorer      → adjust confidence based on agent agreement

VALIDATION + OUTPUT (sequential)
├── SkepticAgent         → adversarial review
├── RemediationAgent     → fix + test generation
└── Final Report         → attack narratives + prioritized findings
```

## Core Components

### 1. Interface Contracts (`models.py`)

Defines the canonical data structures that all agents use:

- **AgentContext**: What every agent receives (project intelligence, file contents, scan metadata)
- **AgentFinding**: What every agent returns (vulnerability finding with standard schema)
- **AgentResult**: Wrapper containing findings plus execution metadata

**CRITICAL**: These interfaces are LOCKED. Do not modify after specialists are built.

### 2. Base Agent (`base_agent.py`)

Abstract base class that all agents inherit from. Provides:

- Shared execution logic (retries, timeouts, token tracking)
- Abstract methods: `build_prompt()`, `parse_response()`
- Confidence adjustment utilities

### 3. Pre-Scan Agents

#### ReconAgent (`recon_agent.py`)
Maps every entry point where untrusted data enters the application:
- HTTP routes, API endpoints, CLI parsers
- Message queue consumers, file readers, environment variables
- Webhook handlers, IPC handlers

Output: `entry_points` list in AgentContext

#### PatternAgent (`pattern_agent.py`)
Identifies architectural patterns:
- MVC, microservice, monolith patterns
- Middleware chains and execution order
- ORM usage (SQLAlchemy, Prisma, etc.)
- Template engines, DI containers, service/repo layers

Output: `architecture_patterns` in AgentContext

#### ThreatModelAgent (`threat_model_agent.py`)
Generates framework-specific threat models:
- Stack summary (e.g., "Python/Flask")
- High-priority threat scenarios with weights
- Framework-specific dangerous sinks and sources
- Known CVE patterns for the stack

Output: `threat_model` in AgentContext

### 4. Specialist Agents (Specialists Directory)

Specialist agents detect specific vulnerability classes. To be implemented:

- **InjectionSpecialist**: SQLi, XSS, Command Injection, etc.
- **AuthSpecialist**: Broken auth, session issues, JWT weaknesses
- **CryptoSpecialist**: Weak crypto, hardcoded secrets, TLS issues
- **CipherDesignSpecialist**: AES/CBC misuse, padding oracles, missing MAC/AEAD, IV/nonce reuse
- **LogicAnalyst**: IDOR, race conditions, business logic flaws
- **ConfigHunter**: Misconfigurations, secrets in config files

### 5. Coordinator (`coordinator.py`)

Central orchestrator that:
- Manages agent execution order
- Runs pre-scan agents sequentially
- Dispatches specialists in parallel (asyncio.gather)
- Merges findings from all agents
- Creates AgentContext from existing v3 indexer output

## Usage Example

```python
from backend.worker.core.agents import AgentCoordinator, AgentContext
from backend.worker.core.agents.recon_agent import ReconAgent
from backend.worker.core.agents.pattern_agent import PatternAgent
from backend.worker.core.agents.threat_model_agent import ThreatModelAgent

# Initialize agents
recon_agent = ReconAgent(name="ReconAgent", llm_client=llm_client)
pattern_agent = PatternAgent(name="PatternAgent", llm_client=llm_client)
threat_agent = ThreatModelAgent(name="ThreatModelAgent", llm_client=llm_client)

# Initialize coordinator
coordinator = AgentCoordinator(
    recon_agent=recon_agent,
    pattern_agent=pattern_agent,
    threat_model_agent=threat_agent,
    specialist_agents=[],  # Add specialists here
)

# Create context from existing v3 indexer
context = coordinator.create_context_from_indexer(
    indexer_output=indexer_output,
    repo_path="/path/to/repo",
    language="python",
    framework="flask",
    scan_mode=ScanMode.FULL,
)

# Run scan
result, enriched_context = await coordinator.run_scan(context)

# Get findings
for finding in result.findings:
    print(f"Found: {finding.vulnerability_class} in {finding.file_path}")
```

## Testing

Unit tests are located in `backend/worker/tests/agents/`:

```bash
pytest backend/worker/tests/agents/ -v
```

### Test Coverage

- `test_models.py`: AgentContext, AgentFinding, AgentResult
- `test_base_agent.py`: BaseAgent abstract class
- `test_recon_agent.py`: Entry point detection
- `test_pattern_agent.py`: Architecture pattern detection
- `test_threat_model_agent.py`: Threat model generation
- `test_coordinator.py`: Agent orchestration

## Adding New Agents

To add a new agent:

1. Inherit from `BaseAgent`
2. Implement `build_prompt()` with role definition and output format
3. Implement `parse_response()` to convert LLM output to `AgentFinding` objects
4. Add to coordinator's agent list

Example:

```python
from backend.worker.core.agents.base_agent import BaseAgent
from backend.worker.core.agents.models import AgentContext, AgentFinding

class MyAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(name="MyAgent", *args, **kwargs)
    
    def build_prompt(self, context: AgentContext) -> str:
        return f"""You are a my agent. Look for X, Y, Z.
        
Output format:
[
  {{
    "finding_id": "unique-id",
    "agent_source": "MyAgent",
    "file_path": "file.py",
    "line_start": 1,
    "line_end": 10,
    "vulnerability_class": "MyVulnerability",
    "reasoning": "Why this is a vulnerability"
  }}
]"""
    
    def parse_response(self, response: str) -> list[AgentFinding]:
        import json
        data = json.loads(response)
        return [AgentFinding.from_dict(item) for item in data]
```

## Integration with v3

The new agent system integrates with existing v3 components:

- **Reads from**: `project_indexer.py` output (call_graph, dependency_map, sanitizer_registry)
- **Writes to**: Existing findings pipeline via `findings_filter.py`
- **Main entry point**: `main.py` (Task 11 in implementation plan)

## File Structure

```
backend/worker/core/agents/
├── __init__.py              # Public exports
├── models.py                # Core data structures (LOCKED INTERFACE)
├── base_agent.py            # Abstract base class
├── coordinator.py           # Agent orchestration
├── recon_agent.py           # Entry point mapping
├── pattern_agent.py         # Architecture detection
├── threat_model_agent.py    # Threat modeling
└── specialists/
    ├── __init__.py
    ├── injection_specialist.py     # TODO: Implement
    ├── auth_specialist.py          # TODO: Implement
    ├── crypto_specialist.py        # TODO: Implement
    ├── cipher_design_specialist.py # AES/CBC, padding oracle, AEAD/MAC design
    ├── logic_analyst.py            # TODO: Implement
    └── config_hunter.py            # TODO: Implement
```

## Next Steps

See `backend/worker/tests/benchmarks/` for Phase 0 evaluation framework.

See improvement plan for remaining phases (Attack Chain Synthesis, Validation, Efficiency, Emerging Threats).
