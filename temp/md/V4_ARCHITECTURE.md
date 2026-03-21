# SentinAI v4 Architecture

## Overview

SentinAI v4 is an advanced AI-powered SAST (Static Application Security Testing) tool featuring a **multi-agent security analysis system**, **layered detection pipeline**, and **adaptive tiered scanning**. It combines keyword heuristics, regex-based indexing, deep semantic analysis via DeepWiki, and a sophisticated multi-agent system for vulnerability detection and validation.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Browser (Next.js :5000)                      │
└───────────────────────────┓─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Flask API Gateway (:5001)                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Auth & Sessions  │  Subscriptions  │  File Uploads         │   │
│  │  CSRF Protection  │  Project Mgmt   │  SSE Streaming        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────────────────┳─────────────────────────────────────────┘
                            │ HTTP + Worker Secret Auth
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  FastAPI Worker Nodes (:5002)                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  SCANNING PIPELINE                                           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │  │
│  │  │   Tier 1    │→ │   Tier 2/3  │→ │    Tier 4   │          │  │
│  │  │ (CHEAP_MODEL)│  │ (SMART_MODEL)│  │ (LLM-Centric)│         │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │  MULTI-AGENT SYSTEM (OpenRouter/Minimax-powered)     │   │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌────────────────────┐   │   │  │
│  │  │  │ Recon    │ │ Pattern  │ │ Specialists (5)    │   │   │  │
│  │  │  │ Agent    │ │ Agent    │ │ - Injection        │   │   │  │
│  │  │  └──────────┘ └──────────┘ │ - Auth             │   │   │  │
│  │  │                            │ - Crypto           │   │   │  │
│  │  │                            │ - Logic Analyst    │   │   │  │
│  │  │                            │ - Config Hunter    │   │   │  │
│  │  │  ┌────────────────────────────────────────────┐ │   │  │
│  │  │  │ Post-Scan Synthesis                        │ │   │  │
│  │  │  │ - Deduplication → Chain → Attack Path →   │ │   │  │
│  │  │  │   Consensus → Skeptic → Remediation       │ │   │  │
│  │  │  └────────────────────────────────────────────┘ │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │  LAYERED ANALYSIS PIPELINE                           │   │  │
│  │  │  Layer 0: Hard Detection Rules (deterministic)       │   │  │
│  │  │  Layer 1: Project Indexing (regex/symbol table)      │   │  │
│  │  │  Layer 2: Context Enrichment (taint/risk analysis)   │   │  │
│  │  │  Layer 3: Tiered LLM Detection                       │   │  │
│  │  │  Layer 4: Post-Scan Validation (SkepticPass)         │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  STORAGE LAYER                                             │    │
│  │  Redis (Symbol Table, Call Graph, DeepWiki Index, State)  │    │
│  │  SQLite (Scans, Auth, Subscriptions, Payments)            │    │
│  │  DeepWiki Docs (Generated markdown documentation)         │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Flask API Gateway (`backend/mainflask.py`)

**Port:** 5001

**Responsibilities:**
- File upload handling with security validation
- User authentication & session management
- Subscription & payment processing
- Scan orchestration & progress streaming
- Result aggregation and storage
- Cross-file consistency coordination

**Key Features:**
- **Custom Auth System:** Replaced Clerk with custom session-based auth
- **CSRF Protection:** Token-based CSRF for all state-changing requests
- **SSE Streaming:** Real-time scan progress via Server-Sent Events
- **Worker Load Balancing:** Round-robin distribution across worker nodes
- **ZIP Extraction:** Automatic extraction and scanning of uploaded archives
- **Multi-format Output:** JSON, SARIF 2.1, and Markdown findings reports

**API Routes:**
```python
POST /auth/register          # User registration
POST /auth/login             # User login
POST /auth/logout            # User logout
GET  /api/csrf-token         # Get CSRF token
POST /api/scan/start         # Async scan with SSE
GET  /api/scan/events/<id>   # SSE stream for scan progress
GET  /api/scan/status/<id>   # Polling fallback
POST /api/scan               # Blocking scan
GET  /api/projects           # List user projects
GET  /api/scan/by-id/<id>    # Get scan by ID
POST /api/scan/pocs          # Generate PoCs (Tier 4)
GET  /api/poc/<scan>/<fp>    # Download PoC script
GET  /api/admin/worker-activity  # Admin monitoring
GET  /api/health             # Health check
```

---

### 2. FastAPI Worker (`backend/worker/core/main.py`)

**Port:** 5002

**Core Scanning Pipeline:**

#### **Stage 0: Hard Detection Rules**
```python
apply_hard_detection_rules()
```
- Deterministic regex-based vulnerability detection
- Catches known patterns (CWE-798 hardcoded secrets, etc.)
- Provides baseline coverage before LLM analysis

#### **Stage 1: Context Enrichment (Layer 2)**
```python
DataflowHintExtractor.extract()      # Taint sources, entry points
FileRiskRanker.rank_one()            # File risk scoring
SanitizerRegistry.build()            # Custom sanitizer detection
DeadCodeDetector.build()             # Dead/test function identification
ContextSlicer.slice_for_scan()       # Cross-file context slicing
```

#### **Stage 2: Tiered LLM Detection**

**Tier 1 (Free):** CHEAP_MODEL default (OpenRouter)
- High-recall triage scan
- Two-phase FP filtering (hard exclusions + parallel LLM validation)
- Max 8 findings for Phase 2 (cost control)

**Tier 2 (Paid):** `TIER2_MODEL` (OpenRouter, default aligns with `SMART_MODEL`)
- Standard CWE/confidence validation
- Focused mode for large files (>20k chars)
- Risk-based tier escalation

**Tier 3 (Premium):** SMART_MODEL streaming
- CVSS scoring + remediation guidance
- Full-file analysis with DeepWiki context
- Advanced contextual understanding

**Tier 4 (LLM-Centric):** Pure LLM detection
- Single-pass intelligent detection + filtering
- Agentic validation (tool-using per-finding validator)
- Maximum accuracy, maximum cost

#### **Stage 3: Two-Phase False Positive Filtering**
```python
Phase 1: FindingsFilter.filter_findings()  # Hard exclusions
Phase 2: apply_two_phase_validation()      # Parallel LLM validation
```

#### **Stage 4: Post-Scan Validation (Layer 4)**
```python
SkepticPass.run()            # Adversarial review for high-CVSS findings
MultiSignalConfidenceScorer.score_all()  # Multi-signal confidence scoring
```

---

### 3. Multi-Agent System (`backend/worker/core/agents/`)

**Requires:** appropriate provider API keys for the configured scan/agent paths

**Execution Flow:**

#### **Pre-Scan Phase (Sequential - Context Enrichment)**
```python
1. ReconAgent           → Maps entry points (public functions, API routes)
2. PatternAgent         → Detects architecture patterns (MVC, layered, etc.)
3. ThreatModelAgent     → Builds framework-specific threat model
```

#### **Detection Phase (Parallel - All Specialists)**
```python
1. InjectionSpecialist   → SQLi, XSS, command injection, etc.
2. AuthSpecialist       → Authentication/authorization flaws
3. CryptoSpecialist     → Weak crypto, hardcoded keys, etc.
4. LogicAnalyst         → Business logic vulnerabilities
5. ConfigHunter         → Misconfigurations, insecure settings
```

#### **Synthesis Phase (Sequential - Mandatory Order)**
```python
1. DeduplicationEngine  → Removes duplicate findings
2. ChainCombiner        → Links related findings into chains
3. AttackPathSimulator  → Simulates exploit paths from chains
4. ConsensusScorer      → Adjusts confidence based on agent agreement
```

#### **Validation + Output Phase (Sequential)**
```python
1. SkepticAgent         → Adversarial review of findings
2. RemediationAgent     → Fix suggestions + test generation
3. Final Report         → Attack narratives + prioritized findings
```

---

### 4. Indexing Pipeline (`backend/worker/core/indexers/`)

#### **Project Indexer**
- Regex-based symbol table construction
- Call graph extraction
- Stores in Redis per scan_id

#### **DeepWiki Indexer** (`LLMindexer.py`)
- LLM-powered semantic indexing
- Generates `project_ir` (intermediate representation)
- Creates structured documentation sections

#### **Extended Indexers (Layer 1)**
```python
FileDependencyMapper      → File-to-file dependency mapping
FunctionCallMapper        → Detailed call graph with entry points
SanitizerRegistry         → Custom input sanitizer detection
DeadCodeDetector          → Dead and test-only function identification
```

---

### 5. Enrichment Modules (`backend/worker/core/enrichment/`)

```python
FileRiskRanker            → Risk scoring per file
DataflowHintExtractor     → Taint analysis (sources, sinks, propagators)
ContextSlicer             → Cross-file context extraction
```

---

### 6. Validation Modules (`backend/worker/core/validation/`)

```python
SkepticPass               → Adversarial validation of high-severity findings
CrossFileConsistencyChecker → Validates cross-file taint chains
MultiSignalConfidenceScorer → Multi-signal confidence aggregation
```

---

### 7. Output Generators

#### **SARIF Emitter** (`backend/worker/core/output/sarif_emitter.py`)
- Generates SARIF 2.1 format for CI/CD integration
- Compatible with GitHub Issues, Azure DevOps, etc.

#### **Findings Markdown Generator** (`backend/findings_md_generator.py`)
- Human-readable findings report
- Includes code snippets, remediation guidance, and PoC references

---

## Tiered Scanning Logic

```python
┌─────────────────────────────────────────────────────────────┐
│                    File Received                            │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
        ┌─────────────────────────────────────┐
        │  Stage 0: Hard Detection Rules      │
        │  (Deterministic regex-based)        │
        └───────────────┬─────────────────────┘
                        ▼
        ┌─────────────────────────────────────┐
        │  Stage 1: Context Enrichment        │
        │  - Taint analysis                   │
        │  - Risk ranking                     │
        │  - Sanitizer registry               │
        └───────────────┬─────────────────────┘
                        ▼
        ┌─────────────────────────────────────┐
        │  Stage 2: Tier 1 (CHEAP_MODEL)         │
        │  - High-recall triage               │
        │  - SAFE → Skip to end (optimization)│
        │  - VULNERABLE → Escalate            │
        └───────────────┬─────────────────────┘
                        ▼
           ┌────────────┴────────────┐
           │                         │
           ▼                         ▼
   ┌──────────────┐          ┌──────────────┐
   │   Tier 1     │          │   Tier 2/3   │
   │   (Free)     │          │   (Paid)     │
   └──────┬───────┘          └──────┬───────┘
          │                         │
          ▼                         ▼
   ┌──────────────┐          ┌──────────────┐
   │  Phase 1:    │          │  Phase 1:    │
   │  Hard FP     │          │  Hard FP     │
   │  Filter      │          │  Filter      │
   └──────┬───────┘          └──────┬───────┘
          │                         │
          ▼                         ▼
   ┌──────────────┐          ┌──────────────┐
   │  Phase 2:    │          │  Phase 2:    │
   │  Parallel    │          │  Parallel    │
   │  LLM Val     │          │  LLM Val     │
   │  (max 8)     │          │  Agentic Val │
   └──────┬───────┘          └──────┬───────┘
          │                         │
          └────────────┬────────────┘
                       ▼
        ┌─────────────────────────────────────┐
        │  Stage 3: Post-Scan Validation      │
        │  - SkepticPass (CVSS ≥ 7.0)         │
        │  - Multi-signal Confidence Scoring  │
        └───────────────┬─────────────────────┘
                        ▼
        ┌─────────────────────────────────────┐
        │  Tier 4 (Optional): LLM-Centric     │
        │  - Pure LLM detection + filtering   │
        │  - Agentic validation               │
        └───────────────┬─────────────────────┘
                        ▼
        ┌─────────────────────────────────────┐
        │  Output: Findings + PoCs + Report   │
        └─────────────────────────────────────┘
```

---

## Configuration

### Environment Variables (`backend/worker/core/config.py`)

```python
# LLM API Keys
OPENROUTER_API_KEY     # Required for all tiers + agents (see `AGENT_MODEL` / `MINIMAX_MODEL`)

# Worker Configuration
WORKER_SECRET          # Shared secret between gateway and worker
REDIS_HOST             # Redis host (default: localhost)
REDIS_PORT             # Redis port (default: 6379)

# Model Selection
CHEAP_MODEL            # e.g. qwen/qwen3.5-9b (Tier 1)
SMART_MODEL            # e.g. z-ai/glm-5 (Tier 2/3; `OPENROUTER_TIER2_MODEL` overrides Tier 2 only)

# Tier 2/3 Settings
ENABLE_TIER23_SAFE_ESCALATION    # Enable SAFE file escalation (default: true)
TIER23_SAFE_ESCALATION_KEYWORD_COUNT  # Keyword threshold (default: 3)

# Context Compaction (for large files >20k chars)
ENABLE_CONTEXT_COMPACTION         # Enable compaction (default: true)
COMPACTION_MIN_CHARS              # Minimum chars for compaction (default: 20000)
COMPACTION_MAX_DROP_RATIO         # Maximum content drop ratio (default: 0.35)

# Two-Phase Filtering
PHASE1_CONFIDENCE_THRESHOLD       # Phase 1 threshold (default: 6.0)
PHASE2_CONFIDENCE_THRESHOLD       # Phase 2 threshold (default: 6.0)
FREE_TIER_PHASE2_MAX_FINDINGS     # Max Phase 2 for Tier 1 (default: 8)

# Agentic Validation
AGENTIC_CONFIDENCE_CEILING                # Confidence ceiling for agent scoring (default: 8.5)
AGENTIC_TIER3_MAX_TOOL_CALLS_PER_FINDING  # Max tool calls per finding (default: 3)
AGENTIC_TIER3_MAX_TOOL_CALLS_PER_SCAN     # Max total tool calls per scan (default: 60)
AGENTIC_TIER4_MAX_TOOL_CALLS_PER_FINDING  # Tier 4 max per finding (default: 5)
AGENTIC_TIER4_MAX_TOOL_CALLS_PER_SCAN     # Tier 4 max per scan (default: 120)
TIER4_AGENTIC_CONFIDENCE_FLOOR            # Confidence floor for Tier 4 (default: 7.0)

# SkepticPass (Post-Scan Validation)
SKEPTIC_PASS_ENABLED                # Enable SkepticPass (default: true)
SKEPTIC_CVSS_THRESHOLD              # CVSS threshold for Skeptic (default: 7.0)
SKEPTIC_MAX_PARALLEL                # Max parallel Skeptic tasks (default: 6)

# Multi-Agent System
AGENT_SCAN_ENABLED                  # Enable multi-agent scanning (default: true)
AGENT_PARALLEL_TIMEOUT_SECONDS      # Parallel agent timeout (default: 120)
AGENT_MAX_FILE_TOKENS               # Max tokens per file for agents (default: 50000)

# Caching
SCAN_TTL                    # Scan data TTL in Redis (default: 3600)
PROJECT_CACHE_TTL          # Project index cache TTL (default: 21600)
```

---

## Data Flow

### File Upload → Scan → Result

```
1. Browser uploads file(s) via multipart/form-data
   │
   ▼
2. Flask Gateway validates files (path traversal, size, extension)
   │
   ▼
3. Gateway generates scan_id and stores in Redis
   │
   ▼
4. Gateway distributes files to worker nodes (round-robin)
   │
   ▼
5. Worker executes multi-stage scanning pipeline
   │
   ▼
6. Worker stores progress in Redis (SSE streaming)
   │
   ▼
7. Worker stores final results in SQLite + Redis
   │
   ▼
8. Worker generates SARIF + Markdown reports
   │
   ▼
9. Gateway streams results to frontend via SSE
   │
   ▼
10. Frontend displays findings in dashboard
```

### Multi-Agent Scan Flow

```
1. Pre-scan indexing (project-wide)
   │
   ▼
2. AgentContext creation (call graph, dependencies, file contents)
   │
   ▼
3. Pre-scan agents (sequential):
   - ReconAgent → entry_points
   - PatternAgent → architecture_patterns
   - ThreatModelAgent → threat_model
   │
   ▼
4. Specialist agents (parallel):
   - All 5 specialists receive enriched context
   - Each agent runs independently
   │
   ▼
5. Merge all specialist findings
   │
   ▼
6. Post-scan synthesis (sequential):
   - DeduplicationEngine
   - ChainCombiner
   - AttackPathSimulator
   - ConsensusScorer
   │
   ▼
7. Validation + output:
   - SkepticAgent
   - RemediationAgent
   │
   ▼
8. Store agent findings in Redis
   │
   ▼
9. Merge agent findings with main scan results
```

---

## Security Features

### Input Validation
- Path traversal protection
- ZIP extraction safety
- File size limits (1MB default)
- Allowed extension whitelist

### Authentication & Authorization
- Session-based auth with CSRF tokens
- Secure cookies (HTTPOnly, SameSite, Secure)
- Worker authentication via shared secret header
- Admin-only endpoints protected by email whitelist

### Data Protection
- Redis TTL for scan data (auto-expiry)
- Temp directory cleanup after scan
- Secure temp file handling
- No secrets in logs

### Output Sanitization
- SARIF format for CI/CD safety
- Markdown escaping in reports
- PoC script download with validation

---

## Extensibility

### Adding New Agents
1. Inherit from `BaseAgent` in `agents/base_agent.py`
2. Implement `run()` method
3. Register in `AgentCoordinator`

### Adding New Specialists
1. Create new specialist in `agents/specialists/`
2. Implement detection logic
3. Add to coordinator's specialist list

### Adding New Tier
1. Create new tier module in `backend/worker/core/ai_tierX.py`
2. Add routing logic in `main.py` `/scan` endpoint
3. Configure tier parameters in `config.py`

---

## Performance Optimization

### Context Compaction
- Reduces token usage for large files (>20k chars)
- Preserves security-relevant code sections
- Drops non-essential code (comments, blank lines)

### Incremental Indexing
- File digests for change detection
- Reuses cached project index
- Only re-indexes changed files

### Parallel Processing
- ThreadPoolExecutor for file scanning
- asyncio for LLM validation
- Parallel specialist agents

### Risk-Based Escalation
- File risk scoring before Tier 1
- Auto-escalate high-risk files to higher tiers
- Skip low-risk files after Tier 1

---

## Testing

### Unit Tests
- `backend/worker/tests/agents/` - Agent tests
- `backend/worker/tests/benchmarks/` - Benchmark suite
- `backend/worker/tests/test_llm_client.py` - LLM client tests

### Integration Tests
- `backend/test_scan.py` - End-to-end scan test
- `backend/test_vulnerabilities.py` - Vulnerability detection test

### Benchmark Targets
- `vulnerable-server/` - Intentionally vulnerable Python app
- `vulnerable-server-bank/` - Fullstack vulnerable app
- `vulnerable-server-sast-test/` - SAST-specific test target

---

## Deployment

### Development
```bash
# Frontend
npm run dev  # localhost:5000

# Backend Gateway
cd backend
python mainflask.py  # localhost:5001

# Worker Node
cd backend/worker/core
python main.py  # localhost:5002

# Redis (optional)
redis-server
```

### Production
```bash
# Use gunicorn/uwsgi for Flask
gunicorn -w 4 -b 0.0.0.0:5001 mainflask:app

# Use uvicorn for FastAPI
uvicorn main:app --host 0.0.0.0 --port 5002 --workers 4

# Enable HTTPS, reverse proxy (nginx/caddy)
# Set WORKER_SECRET, ADMIN_EMAILS, SESSION_COOKIE_DOMAIN
```

### Horizontal Scaling
```python
# Set multiple worker nodes
WORKER_NODES=http://127.0.0.1:5002,http://127.0.0.1:5003,http://127.0.0.1:5004

# Gateway distributes scans via round-robin
# Redis for shared state
```

---

## File Structure

```
sentinai-v4/
├── backend/
│   ├── mainflask.py              # Flask API Gateway
│   ├── user_db.py                # Auth database initialization
│   ├── auth.py                   # Auth blueprint (login/register/logout)
│   ├── pay_routes.py             # Payment/subscription routes
│   ├── auth_helpers.py           # Auth utility functions
│   ├── cors_helpers.py           # CORS middleware
│   ├── csrf_helpers.py           # CSRF protection
│   ├── subscription_config.py    # Tier configuration
│   ├── findings_md_generator.py  # Markdown report generation
│   ├── database/
│   │   ├── __init__.py           # Database initialization
│   │   └── operations.py         # SQL operations
│   ├── worker/
│   │   └── core/
│   │       ├── main.py           # FastAPI worker (scan endpoint)
│   │       ├── config.py         # Configuration constants
│   │       ├── models.py         # Pydantic models
│   │       ├── redis_client.py   # Redis connection
│   │       ├── keywords.py       # Keyword definitions
│   │       ├── utils.py          # Utility functions
│   │       ├── LLMindexer.py     # DeepWiki indexing
│   │       ├── project_indexer.py # Regex/symbol indexing
│   │       ├── deepwiki_utils.py # DeepWiki utilities
│   │       ├── context_compactor.py # Context compression
│   │       ├── llm_centric_detector.py # Tier 4 detection
│   │       ├── poc.py            # PoC generation
│   │       ├── ai_tier1.py       # Tier 1 scanning
│   │       ├── ai_tier2.py       # Tier 2 scanning
│   │       ├── ai_tier3.py       # Tier 3 scanning
│   │       ├── findings_filter.py # FP filtering
│   │       ├── findings_validator.py # Validation
│   │       └── agents/           # Multi-agent system
│   │           ├── coordinator.py        # Agent orchestrator
│   │           ├── base_agent.py         # Base agent class
│   │           ├── models.py             # Agent data models
│   │           ├── recon_agent.py        # Reconnaissance agent
│   │           ├── pattern_agent.py      # Pattern detection agent
│   │           ├── threat_model_agent.py # Threat modeling agent
│   │           ├── deduplication_engine.py # Deduplication
│   │           ├── chain_combiner.py     # Chain building
│   │           ├── attack_path_simulator.py # Attack path simulation
│   │           ├── consensus_scorer.py   # Consensus scoring
│   │           ├── skeptic_agent.py      # Skeptic validation
│   │           ├── remediation_agent.py  # Fix suggestions
│   │           ├── learning_agent.py     # Learning from scans
│   │           └── specialists/          # Detection specialists
│   │               ├── injection_specialist.py
│   │               ├── auth_specialist.py
│   │               ├── crypto_specialist.py
│   │               ├── logic_analyst.py
│   │               └── config_hunter.py
│   │       └── indexers/             # Extended indexers
│   │           ├── file_dependency_mapper.py
│   │           ├── function_call_mapper.py
│   │           ├── sanitizer_registry.py
│   │           └── dead_code_detector.py
│   │       └── enrichment/           # Pre-scan enrichment
│   │           ├── file_risk_ranker.py
│   │           ├── dataflow_hint_extractor.py
│   │           └── context_slicer.py
│   │       └── validation/           # Post-scan validation
│   │           ├── skeptic_pass.py
│   │           ├── cross_file_consistency.py
│   │           └── confidence_scorer.py
│   │       └── output/               # Output generators
│   │           └── sarif_emitter.py
│   ├── scan_results/               # Generated reports
│   ├── deepwiki_docs/              # DeepWiki documentation
│   └── data/learning/              # Learning data
├── frontend/                       # Next.js app
│   ├── src/
│   │   ├── app/                    # Next.js pages
│   │   ├── components/             # React components
│   │   └── context/                # React contexts
│   └── package.json
├── benchmark/                      # Benchmark suite
│   └── servers/                    # Vulnerable test apps
└── md/                             # Documentation
    ├── V4_ARCHITECTURE.md          # This file
    └── ARCHITECTURE_AND_FLOWS.md   # V3 documentation (legacy)
```

---

## Version Comparison

### V3 → V4 Key Changes

| Feature | V3 | V4 |
|---------|-----|-----|
| **Detection** | Keyword + Tiered LLM | + Hard rules + Multi-agent |
| **Context** | Regex symbol table | + DeepWiki + Call graph + Taint analysis |
| **Architecture** | Monolithic worker | Layered pipeline + Agent system |
| **FP Filtering** | Phase 1 + Phase 2 | + SkepticPass + Consensus scoring |
| **Output** | JSON + Markdown | + SARIF 2.1 |
| **Auth** | Clerk | Custom session-based |
| **Indexing** | Basic regex | Extended indexers (deps, sanitizers, dead code) |
| **Validation** | Cross-file consistency | + Cross-file chains + Multi-signal confidence |
| **Scanning Modes** | Tier 1-3 | + Tier 4 (LLM-Centric) + Agent Scan |

---

## Glossary

- **DeepWiki**: LLM-powered semantic project documentation generator
- **Tier**: Scanning depth level (1 = basic, 4 = LLM-centric)
- **Taint Analysis**: Tracking user input through code to detect injection flaws
- **Call Graph**: Mapping of function-to-function calls in the codebase
- **Sanitizer**: Input validation/encoding function that mitigates injection
- **SkepticPass**: Adversarial validation step that reviews high-severity findings
- **Agent**: Autonomous LLM-driven component with specific security analysis role
- **PoC**: Proof of Concept script demonstrating vulnerability exploitation
- **SARIF**: Static Analysis Results Interchange Format (CI/CD standard)

---

## License & Credits

SentinAI v4 is an AI-powered SAST tool under development. Built with:
- **Flask** (API Gateway)
- **FastAPI** (Worker Node)
- **Next.js** (Frontend)
- **CHEAP_MODEL** (Tier 1 LLM)
- **`SMART_MODEL`** (Tier 2/3 LLM, default `z-ai/glm-5`)
- **Minimax M2.5** (Multi-agent system via OpenRouter)
- **Redis** (Caching & State)
- **SQLite** (Database)

---

*Last Updated: March 10, 2026*
*Version: 4.0.0*
