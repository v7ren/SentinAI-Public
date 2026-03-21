# SentinAI v4 Multi-Agent Architecture

This document provides a comprehensive deep-dive into the multi-agent security analysis framework, including detailed mermaid diagrams of the agentic loop and how all components work together.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [The Agentic Loop](#the-agentic-loop)
4. [Phase 1: Pre-Scan Agents](#phase-1-pre-scan-agents)
5. [Phase 2: Specialist Detection](#phase-2-specialist-detection)
6. [Phase 3: Synthesis Pipeline](#phase-3-synthesis-pipeline)
7. [Phase 4: Validation & Output](#phase-4-validation--output)
8. [Data Models & Interface Contracts](#data-models--interface-contracts)
9. [Logging & Observability](#logging--observability)
10. [Learning & Feedback](#learning--feedback)

---

## Executive Summary

SentinAI v4 implements a **multi-agent security analysis pipeline** that combines:

- **Context Building**: Pre-scan agents (Recon, Pattern, ThreatModel) enrich context before detection
- **Parallel Detection**: Five specialist agents run concurrently for different vulnerability classes
- **Chain Synthesis**: Findings are linked into multi-hop attack chains
- **Adversarial Validation**: SkepticAgent plays devil's advocate to reduce false positives
- **Remediation**: Concrete fixes with unit tests for confirmed vulnerabilities

The key innovation is the **sequential context enrichment** pattern: each pre-scan agent adds intelligence that downstream agents use, enabling framework-specific detection rather than generic rules.

---

## Architecture Overview

```mermaid
graph TB
    subgraph Input["📥 Input Layer"]
        FILES[Project Files]
        INDEXER[Project Indexer]
    end

    subgraph Context["🔍 Context Building"]
        CG[Call Graph]
        DM[Dependency Map]
        SR[Sanitizer Registry]
        DCM[Dead Code Map]
    end

    subgraph PreScan["📊 Pre-Scan Phase (Sequential)"]
        RECON[ReconAgent<br/>Entry Point Mapping]
        PATTERN[PatternAgent<br/>Architecture Detection]
        THREAT[ThreatModelAgent<br/>Framework Threats]
    end

    subgraph Specialist["🔎 Specialist Detection (Parallel)"]
        INJ[InjectionSpecialist<br/>SQLi, CMD, SSTI]
        AUTH[AuthSpecialist<br/>Auth, Session, JWT]
        CRYPTO[CryptoSpecialist<br/>Weak Crypto, Secrets]
        LOGIC[LogicAnalyst<br/>IDOR, Race Conditions]
        CONFIG[ConfigHunter<br/>Misconfigurations]
    end

    subgraph Synthesis["🔗 Synthesis Phase (Sequential)"]
        DEDUP[DeduplicationEngine]
        CHAIN[ChainCombiner]
        ATTACK[AttackPathSimulator]
        CONSENSUS[ConsensusScorer]
    end

    subgraph Validation["✅ Validation Phase (Sequential)"]
        SKEPTIC[SkepticAgent<br/>Adversarial Review]
        REMED[RemediationAgent<br/>Fix + Test Generation]
    end

    subgraph Output["📤 Output Layer"]
        REPORT[Security Report]
        ATTACK_PATHS[Attack Narratives]
        FIXES[Remediation Plans]
    end

    FILES --> INDEXER
    INDEXER --> CG & DM & SR & DCM
    CG & DM & SR & DCM --> RECON
    RECON --> |entry_points| PATTERN
    PATTERN --> |architecture_patterns| THREAT
    THREAT --> |threat_model| INJ & AUTH & CRYPTO & LOGIC & CONFIG

    INJ & AUTH & CRYPTO & LOGIC & CONFIG --> DEDUP
    DEDUP --> CHAIN
    CHAIN --> ATTACK
    ATTACK --> CONSENSUS
    CONSENSUS --> SKEPTIC
    SKEPTIC --> REMED
    REMED --> REPORT & ATTACK_PATHS & FIXES

    style RECON fill:#3498db,color:#fff
    style PATTERN fill:#3498db,color:#fff
    style THREAT fill:#3498db,color:#fff
    style INJ fill:#e74c3c,color:#fff
    style AUTH fill:#e74c3c,color:#fff
    style CRYPTO fill:#e74c3c,color:#fff
    style LOGIC fill:#e74c3c,color:#fff
    style CONFIG fill:#e74c3c,color:#fff
    style SKEPTIC fill:#9b59b6,color:#fff
```

---

## The Agentic Loop

The core "agentic loop" refers to how each agent processes input through the LLM and produces structured output. This is the fundamental building block of the entire system.

### Single Agent Execution Flow

```mermaid
sequenceDiagram
    participant C as Coordinator
    participant A as BaseAgent
    participant L as AgentLogger
    participant LLM as LLM Client
    participant P as Parser

    C->>A: run(context: AgentContext)
    A->>L: log_agent_start()

    Note over A: Build specialized prompt
    A->>A: build_prompt(context)
    A->>L: log_agent_prompt(prompt)

    loop Retry with Exponential Backoff
        A->>LLM: complete(prompt, timeout)
        LLM-->>A: response
    end

    A->>L: log_agent_response(response, latency_ms)

    Note over A: Parse LLM output
    A->>P: parse_response(response)
    P-->>A: list[AgentFinding]

    A->>L: log_agent_findings(findings)
    A->>L: log_agent_complete()

    A-->>C: AgentResult(findings, metadata)
```

### Agent Execution State Machine

```mermaid
stateDiagram-v2
    [*] --> Initializing: run(context)

    Initializing --> BuildingPrompt: Logger initialized
    BuildingPrompt --> CallingLLM: prompt = build_prompt()

    state CallingLLM {
        [*] --> Attempt
        Attempt --> Success: response received
        Attempt --> Retry: exception & attempts < max_retries
        Retry --> Attempt: backoff(2^attempt)
        Retry --> Failed: attempts exhausted
        Success --> [*]
        Failed --> [*]
    }

    CallingLLM --> ParsingResponse: response content
    ParsingResponse --> ValidatingFindings: findings = parse_response()
    ValidatingFindings --> Completed: validation passed
    ValidatingFindings --> CompletedWithErrors: validation failed

    Completed --> [*]: return AgentResult
    CompletedWithErrors --> [*]: return AgentResult with errors
```

### BaseAgent Class Diagram

```mermaid
classDiagram
    class BaseAgent {
        <<abstract>>
        +name: str
        +llm_client: LLMClient
        +max_retries: int
        +timeout_seconds: int

        +build_prompt(context: AgentContext)* str
        +parse_response(response: str)* list~AgentFinding~
        +run(context: AgentContext) AgentResult

        #_call_llm_with_retry(prompt, context) str
        #_generate_mock_response(prompt) str
        #validate_finding(finding) bool
        #adjust_confidence(finding, adjustment) AgentFinding
        #_get_agent_type() str
    }

    class ReconAgent {
        +FRAMEWORK_PATTERNS: dict
        +ENTRY_TYPE_PATTERNS: dict

        +build_prompt(context) str
        +parse_response(response) list~AgentFinding~
        +run(context) tuple~AgentResult, list~EntryPoint~~
        +detect_entry_points_from_patterns(context) list~EntryPoint~
    }

    class PatternAgent {
        +FRAMEWORK_PATTERNS: dict
        +MIDDLEWARE_PATTERNS: dict
        +ORM_PATTERNS: dict

        +build_prompt(context) str
        +parse_response(response) list~AgentFinding~
        +detect_patterns_from_patterns(context) ArchPattern
        +extract_middleware_order(context) list~str~
    }

    class ThreatModelAgent {
        +build_prompt(context) str
        +parse_response(response) list~AgentFinding~
    }

    class InjectionSpecialist {
        +name: str
        +build_prompt(context) str
        +parse_response(response) list~AgentFinding~
        -_format_entry_points() str
        -_format_sanitizers() str
        -_format_call_graph() str
    }

    class AuthSpecialist {
        +name: str
        +build_prompt(context) str
        +parse_response(response) list~AgentFinding~
        -_check_middleware_chain() str
    }

    class CryptoSpecialist {
        +name: str
        +build_prompt(context) str
        +parse_response(response) list~AgentFinding~
        -_calculate_entropy(text) float
        -_is_likely_secret(value) bool
    }

    BaseAgent <|-- ReconAgent
    BaseAgent <|-- PatternAgent
    BaseAgent <|-- ThreatModelAgent
    BaseAgent <|-- InjectionSpecialist
    BaseAgent <|-- AuthSpecialist
    BaseAgent <|-- CryptoSpecialist
```

---

## Phase 1: Pre-Scan Agents

Pre-scan agents run **sequentially** because each one enriches the context for downstream agents. The order is mandatory.

### Execution Order & Data Flow

```mermaid
flowchart LR
    subgraph S1["Step 1: ReconAgent"]
        R_IN[File Contents] --> R_LLM[LLM Analysis]
        R_LLM --> R_OUT[entry_points]
    end

    subgraph S2["Step 2: PatternAgent"]
        P_IN[entry_points + Files] --> P_LLM[LLM Analysis]
        P_LLM --> P_OUT[architecture_patterns]
    end

    subgraph S3["Step 3: ThreatModelAgent"]
        T_IN[patterns + Files] --> T_LLM[LLM Analysis]
        T_LLM --> T_OUT[threat_model]
    end

    S1 --> S2 --> S3

    style S1 fill:#3498db20
    style S2 fill:#3498db20
    style S3 fill:#3498db20
```

### ReconAgent: Entry Point Mapping

```mermaid
graph TB
    subgraph Input
        FILES[Source Files]
        FW[Framework Info]
    end

    subgraph Detection
        HTTP[HTTP Routes<br/>Express, Flask, FastAPI, Django]
        CLI[CLI Parsers<br/>argparse, click, cobra]
        MQ[Message Queue Consumers<br/>Kafka, RabbitMQ, SQS]
        FILE[File Readers<br/>path injection detection]
        ENV[Environment Variables<br/>os.environ, process.env]
        WEBHOOK[Webhook Handlers]
    end

    subgraph Output
        EP[EntryPoint Objects]
        EP_DET{Entry Point Details}
        TYPE[entry_type]
        AUTH[authentication_required]
        PARAMS[parameters list]
        LOC[file_path:line_number]
    end

    FILES --> HTTP & CLI & MQ & FILE & ENV & WEBHOOK
    HTTP & CLI & MQ & FILE & ENV & WEBHOOK --> EP
    EP --> EP_DET
    EP_DET --> TYPE & AUTH & PARAMS & LOC

    style HTTP fill:#e74c3c,color:#fff
    style CLI fill:#e74c3c,color:#fff
    style MQ fill:#e74c3c,color:#fff
```

**What ReconAgent Detects:**

| Entry Type | Examples | Security Relevance |
|------------|----------|-------------------|
| HTTP | `@app.route('/api/users')`, `app.get('/users')` | Unauthenticated routes are high priority |
| CLI | `argparse.ArgumentParser()`, `click.command()` | Command injection vectors |
| MQ | `kafka.Consumer()`, `@rabbitmq.handler` | Message injection, deserialization |
| File | `open(user_path)`, `Path(user_input)` | Path traversal |
| Env | `os.environ['API_KEY']`, `process.env.DB_PASS` | Secret exposure |
| Webhook | `@webhook('/stripe')` | SSRF, signature bypass |

### PatternAgent: Architecture Detection

```mermaid
graph LR
    subgraph Detection
        ARCH[Architecture Pattern<br/>MVC, Microservice, Monolith]
        MW[Middleware Chain<br/>Execution Order]
        ORM[ORM Detection<br/>SQLAlchemy, Prisma, Hibernate]
        TMPL[Template Engine<br/>Jinja2, Handlebars, React]
        CORS[CORS Configuration]
        DI[Dependency Injection<br/>Container Detection]
    end

    subgraph Security_Implications["Security Implications"]
        AUTH_MW[Auth Middleware Position<br/>Before or After Routes?]
        ORM_SAFE[ORM Safety<br/>Parameterized by Default?]
        SSTI_RISK[Template Injection Risk<br/>Server-Side Rendering?]
        CORS_RISK[CORS Misconfiguration<br/>allow_origin: * ?]
    end

    ARCH --> AUTH_MW
    MW --> AUTH_MW
    ORM --> ORM_SAFE
    TMPL --> SSTI_RISK
    CORS --> CORS_RISK

    style AUTH_MW fill:#e74c3c,color:#fff
    style SSTI_RISK fill:#e74c3c,color:#fff
```

### ThreatModelAgent: Framework-Specific Threats

```mermaid
mindmap
  root((Threat Model))
    Stack Summary
      Language
      Framework
      Database
      Auth System
    High Priority Threats
      SQL Injection
        Priority: 0.9
        CWE-89
      Broken Auth
        Priority: 0.85
        CWE-287
      XSS
        Priority: 0.7
        CWE-79
    Framework Sinks
      Dangerous Functions
        eval(), exec()
        db.execute()
        render_template_string()
      Framework-Specific
        Flask: session, g
        Express: req.body
        Django: request.GET
    Known CVE Patterns
      CVE-2023-XXXXX
      Framework-specific
      Dependency-related
```

---

## Phase 2: Specialist Detection

Five specialist agents run **in parallel** using `asyncio.gather()`. All receive the same enriched context from pre-scan.

### Parallel Execution Architecture

```mermaid
flowchart TB
    CTX[Enriched Context<br/>entry_points + architecture + threat_model]

    subgraph Parallel["Parallel Execution (asyncio.gather)"]
        INJ[InjectionSpecialist]
        AUTH[AuthSpecialist]
        CRYPTO[CryptoSpecialist]
        LOGIC[LogicAnalyst]
        CONFIG[ConfigHunter]
    end

    subgraph Findings["Findings Output"]
        F1[SQLi, CMD, SSTI<br/>LDAP, XPath, NoSQL]
        F2[Broken Auth, JWT<br/>Session, OAuth, IDOR]
        F3[Weak Crypto, Hardcoded<br/>Secrets, TLS Issues]
        F4[Race Conditions<br/>Business Logic Flaws]
        F5[Misconfigurations<br/>Exposed Configs]
    end

    CTX --> INJ & AUTH & CRYPTO & LOGIC & CONFIG
    INJ --> F1
    AUTH --> F2
    CRYPTO --> F3
    LOGIC --> F4
    CONFIG --> F5

    F1 & F2 & F3 & F4 & F5 --> MERGE[Merge All Findings]

    style INJ fill:#e74c3c,color:#fff
    style AUTH fill:#e74c3c,color:#fff
    style CRYPTO fill:#e74c3c,color:#fff
    style LOGIC fill:#e74c3c,color:#fff
    style CONFIG fill:#e74c3c,color:#fff
```

### Specialist Agent Coverage Matrix

```mermaid
graph LR
    subgraph Vulnerability_Classes
        V1[SQL Injection - CWE-89]
        V2[Command Injection - CWE-78]
        V3[SSTI - CWE-94]
        V4[LDAP Injection - CWE-90]
        V5[XSS - CWE-79]
        V6[Broken Auth - CWE-287]
        V7[Session Fixation - CWE-384]
        V8[JWT Weaknesses]
        V9[Weak Crypto - CWE-327]
        V10[Hardcoded Secrets - CWE-798]
        V11[Insufficient Randomness - CWE-338]
        V12[IDOR - CWE-639]
        V13[Race Conditions - CWE-362]
        V14[Security Misconfig - CWE-16]
    end

    subgraph Specialists
        INJ[InjectionSpecialist]
        AUTH[AuthSpecialist]
        CRYPTO[CryptoSpecialist]
        LOGIC[LogicAnalyst]
        CONFIG[ConfigHunter]
    end

    V1 & V2 & V3 & V4 & V5 --> INJ
    V6 & V7 & V8 --> AUTH
    V9 & V10 & V11 --> CRYPTO
    V12 & V13 --> LOGIC
    V14 --> CONFIG

    style V1 fill:#e74c3c,color:#fff
    style V6 fill:#e74c3c,color:#fff
    style V9 fill:#e74c3c,color:#fff
    style V12 fill:#e74c3c,color:#fff
    style V14 fill:#e74c3c,color:#fff
```

### Taint Analysis Flow (InjectionSpecialist)

```mermaid
flowchart TB
    subgraph Source["Taint Source"]
        REQ[request.args.get]
        BODY[req.body]
        PARAMS[req.params]
    end

    subgraph Propagation["Taint Propagation"]
        F1[Function Call 1]
        F2[Function Call 2]
        F3[Function Call 3]
    end

    subgraph Sink["Dangerous Sink"]
        DB[db.execute]
        EXEC[os.system]
        EVAL[eval]
        RENDER[render_template_string]
    end

    subgraph Checks["Sanity Checks"]
        SAN{Sanitizer Applied?}
        DEAD{Dead Code?}
        VALID{Input Validated?}
    end

    REQ --> F1 --> F2 --> F3
    BODY --> F1
    PARAMS --> F1

    F3 --> SAN
    SAN -->|No| DEAD
    SAN -->|Yes| SKIP[Skip Finding]
    DEAD -->|No| VALID
    DEAD -->|Yes| SKIP
    VALID -->|No| DB & EXEC & EVAL & RENDER
    VALID -->|Yes| LOW[Lower Confidence]

    DB --> FINDING[Vulnerability Finding]
    EXEC --> FINDING
    EVAL --> FINDING
    RENDER --> FINDING

    style FINDING fill:#e74c3c,color:#fff
```

---

## Phase 3: Synthesis Pipeline

After specialists produce findings, the synthesis pipeline runs **sequentially** to process, link, and score findings.

### Synthesis Flow

```mermaid
flowchart LR
    subgraph Input
        RAW[Raw Findings<br/>From Specialists]
    end

    subgraph Step1["Step 1: Deduplication"]
        DEDUP[DeduplicationEngine]
        DEDUP_OUT[DeduplicatedFindings]
    end

    subgraph Step2["Step 2: Chain Building"]
        CHAIN[ChainCombiner]
        CHAINS[VulnerabilityChains]
    end

    subgraph Step3["Step 3: Path Simulation"]
        PATH[AttackPathSimulator]
        PATHS[AttackPaths]
    end

    subgraph Step4["Step 4: Consensus Scoring"]
        SCORE[ConsensusScorer]
        SCORED[Scored Findings]
    end

    RAW --> DEDUP
    DEDUP --> DEDUP_OUT
    DEDUP_OUT --> CHAIN
    CHAIN --> CHAINS
    CHAINS --> PATH
    PATH --> PATHS
    PATHS --> SCORE
    SCORE --> SCORED

    style DEDUP fill:#f39c12,color:#fff
    style CHAIN fill:#f39c12,color:#fff
    style PATH fill:#f39c12,color:#fff
    style SCORE fill:#f39c12,color:#fff
```

### Deduplication Logic

```mermaid
flowchart TB
    START[All Findings]
    GROUP[Group by<br/>file_path + vulnerability_class]
    OVERLAP{Line Range<br/>Overlap?}
    MERGE[Merge Findings]
    SINK{Same Taint Sink?}
    SINK_MERGE[Merge by Sink]
    FINAL[Deduplicated Findings]

    START --> GROUP
    GROUP --> OVERLAP
    OVERLAP -->|Yes| MERGE
    OVERLAP -->|No| SINK
    MERGE --> SINK
    SINK -->|Yes| SINK_MERGE
    SINK -->|No| FINAL
    SINK_MERGE --> FINAL

    subgraph Merge_Rules["Merge Rules"]
        M1[confidence: max]
        M2[taint_path: longest]
        M3[severity: highest]
        M4[contributing_agents: all]
        M5[duplicate_count: increment]
    end

    MERGE -.-> M1 & M2 & M3 & M4 & M5
```

### Chain Building Heuristics

```mermaid
graph LR
    subgraph Chainable_Rules["Chainable(A, B) Rules"]
        R1[A.taint_sink == B.taint_source]
        R2[A is auth_bypass<br/>AND B requires_auth]
        R3[A is info_disclosure<br/>AND B is exploitation]
    end

    subgraph Examples["Chain Examples"]
        E1[Auth Bypass → IDOR]
        E2[SQLi → Privilege Escalation]
        E3[Info Leak → Account Takeover]
    end

    R1 --> E2
    R2 --> E1
    R3 --> E3
```

### Consensus Scoring Formula

```mermaid
graph TB
    subgraph Inputs
        BASE[Base Confidence<br/>from Agent]
        AGENTS[Number of<br/>Contributing Agents]
        CHAIN[Chain Membership]
        DEAD[Dead Code Location]
    end

    subgraph Calculation
        MULT[Multiplier Calculation]
        AGENT_MULT[Agent Count Multiplier<br/>1 agent: 1.0<br/>2 agents: 1.25<br/>3 agents: 1.50<br/>4+ agents: 1.75]
        CHAIN_BONUS[Chain Bonus<br/>+0.15]
        DEAD_PENALTY[Dead Code Penalty<br/>-0.40]
    end

    subgraph Output
        FINAL[Final Confidence<br/>min(base * multiplier, 1.0)]
    end

    BASE --> FINAL
    AGENTS --> AGENT_MULT --> MULT
    CHAIN --> CHAIN_BONUS --> MULT
    DEAD --> DEAD_PENALTY --> MULT
    MULT --> FINAL
```

---

## Phase 4: Validation & Output

### SkepticAgent: Adversarial Review

The SkepticAgent acts as a devil's advocate, challenging each finding to reduce false positives.

```mermaid
flowchart TB
    FINDING[Finding to Review]

    subgraph Skeptic_Checks["Skeptic Checks"]
        C1[1. Sanitization<br/>Is there a sanitizer<br/>between source and sink?]
        C2[2. Dead Code<br/>Is this code reachable?]
        C3[3. Framework Protection<br/>Does framework<br/>automatically mitigate?]
        C4[4. Upstream Validation<br/>Is input validated<br/>before this point?]
        C5[5. Authentication Gate<br/>Is endpoint protected?]
        C6[6. Type Constraint<br/>Does type system<br/>prevent attack?]
        C7[7. Context Constraint<br/>Is attack impossible<br/>in this context?]
    end

    subgraph Verdicts["Possible Verdicts"]
        CONFIRMED[CONFIRMED<br/>confidence += 0.1]
        DOWNGRADED[DOWNGRADED<br/>severity -1 level]
        REJECTED[REJECTED<br/>removed from report]
    end

    FINDING --> C1 & C2 & C3 & C4 & C5 & C6 & C7

    C1 & C2 & C3 & C4 & C5 & C6 & C7 --> DECISION{Verdict}

    DECISION -->|No mitigations| CONFIRMED
    DECISION -->|Some mitigations<br/>risk remains| DOWNGRADED
    DECISION -->|Clear false positive| REJECTED

    style REJECTED fill:#27ae60,color:#fff
    style CONFIRMED fill:#e74c3c,color:#fff
    style DOWNGRADED fill:#f39c12,color:#fff
```

### RemediationAgent: Fix Generation

```mermaid
flowchart LR
    subgraph Input
        CF[Confirmed Finding]
        LANG[Language]
        FW[Framework]
    end

    subgraph Strategies["Fix Strategies by Class"]
        S1[SQL Injection:<br/>Parameterized queries]
        S2[Command Injection:<br/>subprocess list args, shell=False]
        S3[Hardcoded Secret:<br/>Environment variables]
        S4[Weak Crypto:<br/>Algorithm replacement]
        S5[Missing Auth:<br/>Middleware application]
        S6[IDOR:<br/>Ownership verification]
        S7[SSTI:<br/>Static templates]
    end

    subgraph Output
        FIX[Fixed Code Snippet]
        TEST[Unit Test Code]
        STEPS[Verification Steps]
        RISK[Regression Risk]
    end

    CF --> S1 & S2 & S3 & S4 & S5 & S6 & S7
    LANG --> Output
    FW --> Output
    S1 & S2 & S3 & S4 & S5 & S6 & S7 --> FIX & TEST
    FIX --> STEPS --> RISK
```

---

## Data Models & Interface Contracts

### Core Data Structures

```mermaid
classDiagram
    class AgentContext {
        +scan_id: str
        +repo_path: str
        +language: str
        +framework: str
        +scan_mode: ScanMode

        +call_graph: dict
        +dependency_map: dict
        +sanitizer_registry: dict
        +dead_code_map: dict

        +entry_points: list~EntryPoint~
        +architecture_patterns: ArchPattern
        +threat_model: ThreatModel

        +file_contents: dict
        +file_asts: dict
    }

    class EntryPoint {
        +entry_type: str
        +file_path: str
        +line_number: int
        +function_name: str
        +handler_function: str
        +parameters: list~str~
        +authentication_required: bool
        +authorization_required: bool
        +rate_limited: bool
        +framework: str
    }

    class ArchPattern {
        +pattern_type: str
        +middleware_order: list~str~
        +auth_middleware_files: list~str~
        +orm_type: str
        +template_engine: str
        +cors_config: dict
        +service_layer_files: list~str~
        +repository_files: list~str~
        +di_container: str
    }

    class ThreatModel {
        +stack_summary: str
        +high_priority_threats: list~ThreatScenario~
        +framework_specific_sinks: list~str~
        +framework_specific_sources: list~str~
        +known_cve_patterns: list~str~
    }

    class AgentFinding {
        +finding_id: str
        +agent_source: str
        +file_path: str
        +line_start: int
        +line_end: int
        +vulnerability_class: str
        +cwe_id: str
        +severity: Severity
        +confidence: float
        +exploitability: Exploitability
        +vulnerable_code: str
        +taint_source: str
        +taint_sink: str
        +taint_path: list~str~
        +chain_id: str
        +reasoning: str
        +false_positive_indicators: list~str~
        +remediation_hint: str
        +to_dict() dict
        +from_dict(data) AgentFinding
    }

    class AgentResult {
        +agent_name: str
        +findings: list~AgentFinding~
        +execution_time_ms: int
        +token_usage: int
        +errors: list~str~
        +metadata: dict
    }

    class DeduplicatedFinding {
        +All AgentFinding fields
        +contributing_agents: list~str~
        +duplicate_count: int
        +to_agent_finding() AgentFinding
    }

    class VulnerabilityChain {
        +chain_id: str
        +chain_name: str
        +findings: list~DeduplicatedFinding~
        +entry_point: EntryPoint
        +impact: str
        +exploitability: str
        +attack_narrative: str
        +chain_length: int
    }

    class AttackPath {
        +path_id: str
        +entry_point: EntryPoint
        +chains_involved: list~VulnerabilityChain~
        +steps: list~AttackStep~
        +final_impact: str
        +attacker_prerequisites: list~str~
        +estimated_complexity: str
        +proof_of_concept_outline: str
    }

    AgentContext "1" --> "*" EntryPoint
    AgentContext --> "0..1" ArchPattern
    AgentContext --> "0..1" ThreatModel
    VulnerabilityChain "1" --> "*" DeduplicatedFinding
    AttackPath "1" --> "*" VulnerabilityChain
    AttackPath "1" --> "*" AttackStep
```

### Data Flow Through Pipeline

```mermaid
flowchart TB
    subgraph Phase1["Phase 1: Context Building"]
        CTX[AgentContext]
    end

    subgraph Phase2["Phase 2: Detection"]
        AF[AgentFinding]
        AR[AgentResult]
    end

    subgraph Phase3["Phase 3: Synthesis"]
        DF[DeduplicatedFinding]
        VC[VulnerabilityChain]
        AP[AttackPath]
    end

    subgraph Phase4["Phase 4: Validation"]
        SV[SkepticVerdict]
        RM[Remediation]
    end

    CTX --> AF
    AF --> AR
    AR --> DF
    DF --> VC
    VC --> AP
    DF --> SV
    SV --> RM

    style CTX fill:#3498db,color:#fff
    style AF fill:#e74c3c,color:#fff
    style DF fill:#f39c12,color:#fff
    style SV fill:#9b59b6,color:#fff
```

---

## Logging & Observability

### AgentLogger Event Types

```mermaid
graph TB
    subgraph Events["Log Event Types"]
        E1[scan_start]
        E2[agent_start]
        E3[agent_prompt]
        E4[agent_response]
        E5[agent_findings]
        E6[agent_complete]
        E7[phase_transition]
        E8[deduplication]
        E9[consensus_scoring]
        E10[skeptic_review]
        E11[chain_combiner]
        E12[attack_paths]
        E13[remediation]
        E14[error]
        E15[scan_complete]
    end

    subgraph Outputs["Output Files"]
        JSONL[agent_log_scanid_timestamp.jsonl]
        SUMMARY[agent_summary_scanid_timestamp.json]
    end

    E1 & E2 & E3 & E4 & E5 & E6 --> JSONL
    E7 & E8 & E9 & E10 & E11 & E12 & E13 --> JSONL
    E14 & E15 --> JSONL
    JSONL --> SUMMARY
```

### Log Entry Structure

```
{
  "event_type": "agent_start",
  "seq": 5,
  "elapsed_ms": 1234,
  "agent_name": "InjectionSpecialist",
  "agent_type": "specialist",
  "context_summary": {
    "file_count": 42,
    "entry_points_count": 15,
    "language": "python",
    "framework": "flask"
  },
  "context_full": { ... },
  "config": {
    "max_retries": 3,
    "timeout_seconds": 120
  }
}
```

---

## Learning & Feedback

### LearningAgent Flow

```mermaid
flowchart LR
    subgraph Input["Analyst Feedback"]
        FB[Feedback Record]
        TP[True Positive]
        FP[False Positive]
        WF[Won't Fix]
    end

    subgraph Storage["Persistent Storage"]
        RECORDS[feedback_records.jsonl]
        SUPPRESS[suppression_patterns.json]
        CALIB[confidence_calibration.json]
    end

    subgraph Application["Applied in Future Scans"]
        SUPP[Suppress Known FP Patterns]
        ADJ[Adjust Confidence<br/>for Agent+VulnClass]
    end

    FB --> TP & FP & WF
    TP & FP & WF --> RECORDS
    RECORDS --> |rebuild_patterns| SUPPRESS & CALIB
    SUPPRESS --> SUPP
    CALIB --> ADJ

    style FP fill:#e74c3c,color:#fff
    style TP fill:#27ae60,color:#fff
```

### Feedback Record Structure

```json
{
  "finding_id": "RECON-abc12345",
  "scan_id": "scan-xyz",
  "analyst_verdict": "false_positive",
  "analyst_notes": "This is a test route, not production code",
  "codebase_fingerprint": "sha256:abc123...",
  "agent_source": "InjectionSpecialist",
  "vulnerability_class": "SQL Injection",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Summary

The SentinAI v4 multi-agent architecture provides:

| Feature | Implementation |
|---------|---------------|
| **Context Enrichment** | Pre-scan agents build intelligence before detection |
| **Parallel Detection** | Five specialists run concurrently for speed |
| **Cross-File Analysis** | Call graphs and dependency maps enable taint tracking |
| **Chain Detection** | Findings linked into multi-hop attack scenarios |
| **False Positive Reduction** | SkepticAgent adversarial review + consensus scoring |
| **Actionable Output** | Remediation with fixed code and unit tests |
| **Observability** | Comprehensive logging of every agent interaction |
| **Continuous Learning** | Analyst feedback improves future scans |

The agentic loop — `build_prompt → LLM call → parse_response → validate` — is the foundation that enables consistent, structured output from every agent in the pipeline.
