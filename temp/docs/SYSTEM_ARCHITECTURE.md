# SentinAI SAST System Architecture

## Overview

This document shows how all components work together in the SentinAI vulnerability scanning system.

## System Flow Diagram

```mermaid
flowchart TB
    subgraph Client["Client / Frontend"]
        A[User uploads code]
        B[Scan Request]
    end

    subgraph API["Main API (main4.py)"]
        C[POST /scan endpoint]
        D{Scan Type?}
    end

    subgraph Worker["Worker Service (main.py)"]
        E[Scan Handler]
        F{Decision Logic}
    end

    subgraph Context["Context Building"]
        G[Project Indexer]
        H[DeepWiki Generator]
        I[Redis Cache]
    end

    subgraph ScanTypes["Scan Types"]
        T1[Tier 1: Basic]
        T2[Tier 2: Standard]
        T3[Tier 3: Advanced]
        T4[Tier 4: LLM-Centric]
    end

    subgraph CoreDetection["Detection Engine"]
        Keywords[Keyword Scanner]
        Tier1[ai_tier1.py<br/>CHEAP_MODEL]
        Tier2[ai_tier2.py<br/>SMART_MODEL]
        Tier3[ai_tier3.py<br/>SMART_MODEL]
        LLMCent[llm_centric_detector.py<br/>SMART_MODEL]
    end

    subgraph Filtering["Filtering Engine"]
        HardRules[findings_filter.py<br/>Hard Exclusions]
        Validator[findings_validator.py<br/>Two-Phase Validation]
        SmartFilter[llm_centric_detector.py<br/>Smart LLM Filter]
    end

    subgraph Output["Output Generation"]
        Enrich[Context Enrichment]
        PoC[poc.py<br/>PoC Generation]
        Results[Results JSON]
    end

    A --> B
    B --> C
    C --> D
    D -->|X-Scan-Type: 1| T1
    D -->|X-Scan-Type: 2| T2
    D -->|X-Scan-Type: 3| T3
    D -->|X-Scan-Type: 4| T4

    T1 & T2 & T3 & T4 --> E
    E --> F

    F -->|Build Context| G
    G --> H
    H --> I

    I -->|Context Available| CoreDetection

    T1 -.->|Uses| Tier1
    T2 -.->|Uses| Tier2
    T3 -.->|Uses| Tier3
    T4 -.->|Uses| LLMCent

    Tier1 -.->|Initial Triage| Keywords
    Tier2 -.->|Detailed Analysis| Tier1
    Tier3 -.->|Deep Analysis| Tier2

    CoreDetection -->|Raw Findings| Filtering

    Filtering -->|Phase 1| HardRules
    HardRules -->|Phase 2| Validator
    Validator -->|Optional| SmartFilter

    Filtering -->|Filtered Findings| Enrich
    Enrich -->|Add fingerprints| PoC
    PoC -->|Generate PoC scripts| Results

    Results -->|Return| Client
```

## File Interaction Diagram

```mermaid
flowchart LR
    subgraph Entry["Entry Points"]
        Main4[main4.py<br/>Main API]
        Worker[worker/core/main.py<br/>Worker Service]
    end

    subgraph Models["Data Models"]
        ModelsPy[models.py<br/>Pydantic Schemas]
    end

    subgraph Config["Configuration"]
        ConfigPy[config.py<br/>Settings & Keys]
    end

    subgraph Detection["Detection Layer"]
        Tier1[ai_tier1.py<br/>Basic Detection]
        Tier2[ai_tier2.py<br/>Standard Detection]
        Tier3[ai_tier3.py<br/>Advanced Detection]
        LLMDet[llm_centric_detector.py<br/>LLM Detection]
        Keywords[keywords.py<br/>Keyword Database]
    end

    subgraph Filtering["Filtering Layer"]
        Filter[findings_filter.py<br/>Hard Exclusions]
        Validator[findings_validator.py<br/>Two-Phase Validator]
    end

    subgraph Utils["Utilities"]
        UtilsPy[utils.py<br/>Helpers]
        Redis[redis_client.py<br/>Caching]
        Indexer[project_indexer.py<br/>Project Analysis]
        DeepWiki[deepwiki_utils.py<br/>Wiki Generation]
    end

    subgraph Output["Output Layer"]
        PoC[poc.py<br/>PoC Generator]
    end

    subgraph External["External Services"]
        ORouter[OpenRouter<br/>LLM Models]
        RedisDB[Redis<br/>Cache/Queue]
    end

    Main4 -->|Uses| Worker
    Worker -->|Validates| ModelsPy
    Worker -->|Reads| ConfigPy

    Worker -->|Calls| Tier1
    Worker -->|Calls| Tier2
    Worker -->|Calls| Tier3
    Worker -->|Calls| LLMDet

    Tier1 & Tier2 & Tier3 -->|Uses| Keywords
    Tier1 & Tier2 & Tier3 & LLMDet -->|Calls| ORouter

    Worker -->|Filters| Filter
    Worker -->|Validates| Validator

    Filter -->|Uses| UtilsPy
    Validator -->|Uses| UtilsPy
    Indexer -->|Uses| Redis
    DeepWiki -->|Uses| Redis

    Worker -->|Indexes| Indexer
    Worker -->|Generates| DeepWiki

    Worker -->|Generates| PoC

    Redis -->|Connects| RedisDB
```

## Detailed Scan Type Flows

### Tier 1 Flow (Basic)

```mermaid
sequenceDiagram
    participant C as Client
    participant M as main.py
    participant T1 as ai_tier1.py
    participant F as findings_filter.py
    participant V as findings_validator.py
    participant D as ORouter

    C->>M: POST /scan (X-Scan-Type: 1)
    M->>M: Build context (Redis/DeepWiki)
    M->>T1: scan_tier_1_basic()
    T1->>D: CHEAP_MODEL API Call
    D-->>T1: Raw Findings
    T1-->>M: Triage Result
    
    alt If Vulnerable
        M->>F: Phase 1: Hard Exclusions
        F-->>M: Filtered Findings
        
        opt If ≤5 findings
            M->>V: Phase 2: Parallel Validation
            V->>D: Validate each finding
            D-->>V: Confidence Scores
            V-->>M: Validated Findings
        end
    end
    
    M-->>C: Results
```

### Tier 2/3 Flow (Standard/Advanced)

```mermaid
sequenceDiagram
    participant C as Client
    participant M as main.py
    participant T1 as ai_tier1.py
    participant T2 as ai_tier2.py
    participant T3 as ai_tier3.py
    participant F as findings_filter.py
    participant V as findings_validator.py
    participant D as ORouter

    C->>M: POST /scan (X-Scan-Type: 2/3)
    M->>M: Build context
    M->>T1: Tier 1 Triage
    T1->>D: CHEAP_MODEL
    D-->>T1: Initial Findings
    T1-->>M: Vulnerable? → Continue
    
    alt Tier 2
        M->>T2: scan_tier_2_standard()
        T2->>D: SMART_MODEL
        D-->>T2: Standard Analysis
    else Tier 3
        M->>T3: scan_tier_3_advanced()
        T3->>D: SMART_MODEL (Streaming)
        D-->>T3: Advanced Analysis
    end
    
    M->>F: Phase 1: Hard Exclusions
    F-->>M: Phase 1 Results
    
    M->>V: Phase 2: Full Parallel Validation
    loop For each finding
        V->>D: Validate finding
        D-->>V: Judgment
    end
    V-->>M: Final Filtered
    
    M->>M: Enrich (fingerprints, context)
    M-->>C: Final Results
```

### Tier 4 Flow (LLM-Centric)

```mermaid
sequenceDiagram
    participant C as Client
    participant M as main.py
    participant LLM as llm_centric_detector.py
    participant D as ORouter

    C->>M: POST /scan (X-Scan-Type: 4)
    Note over C,M: OR use_llm_centric: true
    
    M->>M: Build context
    M->>LLM: llm_centric_scan()
    
    Note over LLM: Single intelligent pass
    LLM->>D: SMART_MODEL
    D-->>LLM: Detection + Self-Filtering
    
    opt Optional Smart Filter
        LLM->>LLM: Batch validation
        LLM->>D: Re-validate batch
        D-->>LLM: Final judgments
    end
    
    LLM-->>M: High-confidence findings
    M->>M: Enrich & fingerprint
    M-->>C: Results with reasoning
```

## Data Flow Through Files

```mermaid
flowchart TB
    subgraph Input["Input"]
        File[File Content]
        Headers[X-Scan-Type<br/>X-Scan-ID<br/>X-Secret]
    end

    subgraph Processing["Processing Pipeline"]
        direction TB
        
        Step1["main.py<br/>Receives request"]
        Step2["Build context<br/>project_indexer.py<br/>deepwiki_utils.py"]
        Step3["Cache check<br/>redis_client.py"]
        
        Step4{"Scan Type?"}
        
        Step1 --> Step2 --> Step3 --> Step4
    end

    subgraph Tier1Flow["Tier 1 Path"]
        T1a["ai_tier1.py<br/>Chunk large files"]
        T1b["CHEAP_MODEL<br/>Parallel chunk scanning"]
        T1c["Merge findings"]
        T1a --> T1b --> T1c
    end

    subgraph Tier2Flow["Tier 2/3 Path"]
        T23a["ai_tier2.py / ai_tier3.py"]
        T23b["SMART_MODEL<br/>Focused analysis"]
        T23c["Streaming (T3)"]
        T23a --> T23b --> T23c
    end

    subgraph Tier4Flow["Tier 4 Path"]
        T4a["llm_centric_detector.py"]
        T4b["LLM Detection + Filtering<br/>Single pass"]
        T4c["Smart batch validation"]
        T4a --> T4b --> T4c
    end

    subgraph Filtering["Filtering"]
        F1["findings_filter.py<br/>Hard exclusions"]
        F2["findings_validator.py<br/>Two-phase validation"]
        F1 --> F2
    end

    subgraph Enrichment["Enrichment"]
        E1["utils.py<br/>get_code_context"]
        E2["utils.py<br/>get_fingerprint"]
        E3["utils.py<br/>find_keywords"]
        E1 --> E2 --> E3
    end

    subgraph Output["Output"]
        O1["poc.py<br/>Generate PoC"]
        O2["JSON Response"]
        O1 --> O2
    end

    File --> Processing
    Headers --> Processing
    
    Step4 -->|Type 1| Tier1Flow
    Step4 -->|Type 2/3| Tier2Flow
    Step4 -->|Type 4| Tier4Flow
    
    Tier1Flow --> Filtering
    Tier2Flow --> Filtering
    Tier4Flow -->|Minimal| Filtering
    
    Filtering --> Enrichment
    Enrichment --> Output
```

## Component Responsibilities

### Core Detection Files

| File | Responsibility | Model Used |
|------|---------------|------------|
| `ai_tier1.py` | Initial triage, file chunking, quick detection | CHEAP_MODEL |
| `ai_tier2.py` | Standard analysis with context | SMART_MODEL |
| `ai_tier3.py` | Deep analysis with streaming, CVSS, remediation | SMART_MODEL |
| `llm_centric_detector.py` | Intelligent detection + filtering | SMART_MODEL |

### Filtering Files

| File | Responsibility | Approach |
|------|---------------|----------|
| `findings_filter.py` | Hard exclusion rules | Regex patterns |
| `findings_validator.py` | Two-phase validation | LLM per-finding |
| `llm_centric_detector.py` | Smart batch filtering | LLM batch judge |

### Utility Files

| File | Responsibility |
|------|---------------|
| `utils.py` | Code context, fingerprints, line finding |
| `keywords.py` | Vulnerability keyword database |
| `config.py` | API keys, model settings |
| `redis_client.py` | Caching and queue management |
| `project_indexer.py` | Project structure analysis |
| `deepwiki_utils.py` | Wiki generation and context |
| `poc.py` | Proof-of-concept generation |

## Request Lifecycle

```mermaid
flowchart LR
    subgraph Request["1. Request"]
        A[Client sends file<br/>+ Scan Type header]
    end

    subgraph Context["2. Context Building"]
        B[Load from Redis<br/>if cached]
        C[Generate DeepWiki<br/>if new]
        D[Build security<br/>context graph]
    end

    subgraph Detection["3. Detection"]
        E{Scan Type?}
        F[T1: Quick triage]
        G[T2: Standard]
        H[T3: Deep analysis]
        I[T4: LLM-centric]
    end

    subgraph Validation["4. Validation"]
        J[Hard exclusions]
        K[LLM validation<br/>if needed]
        L[Confidence<br/>threshold]
    end

    subgraph Enrich["5. Enrichment"]
        M[Add fingerprints]
        N[Code context]
        O[Keyword matches]
    end

    subgraph Response["6. Response"]
        P[Generate PoC<br/>if requested]
        Q[Return JSON<br/>with metadata]
    end

    Request --> Context --> Detection --> Validation --> Enrich --> Response

    E -->|1| F
    E -->|2| G
    E -->|3| H
    E -->|4| I
```

## Key Design Decisions

### Why Multiple Tiers?

```mermaid
flowchart LR
    subgraph Cost["Cost Optimization"]
        T1["Tier 1<br/>Cheap model<br/>Fast<br/>Low accuracy"]
        T2["Tier 2<br/>Smart model<br/>Medium cost<br/>Good accuracy"]
        T3["Tier 3<br/>Smart model + stream<br/>Higher cost<br/>Best accuracy"]
        T4["Tier 4<br/>Pure LLM<br/>Highest cost<br/>Intelligent filtering"]
    end

    T1 -->|Escalate if vulnerable| T2
    T2 -->|Escalate for deep analysis| T3
    T1 -->|Skip if budget allows| T4
```

### Two-Phase Filtering Strategy

```mermaid
flowchart TB
    subgraph Phase1["Phase 1: Fast Rules"]
        A[findings_filter.py<br/>Hard exclusions<br/>~10ms per finding<br/>Catches obvious FPs]
    end

    subgraph Phase2["Phase 2: LLM Validation"]
        B[findings_validator.py<br/>Parallel validation<br/>~500ms per finding<br/>Catches nuanced FPs]
    end

    subgraph Smart["Alternative: LLM-Centric"]
        C[llm_centric_detector.py<br/>Detection + Filtering<br/>Single LLM pass<br/>~2s per file<br/>Best accuracy]
    end

    Raw[Raw Findings] --> Phase1 -->|Surviving findings| Phase2 -->|High confidence| Results
    
    Raw -->|Direct to| Smart --> Results
```

## File Call Graph

```
main.py (entry point)
├── ai_tier1.py
│   └── config.py (OPENROUTER_API_KEY, CHEAP_MODEL)
│   └── utils.py (find_line_number, clean_json_response)
│   └── OpenRouter
├── ai_tier2.py
│   └── config.py (OPENROUTER_API_KEY, SMART_MODEL)
│   └── utils.py (build_focused_code_bundle, etc.)
│   └── OpenRouter
├── ai_tier3.py
│   └── config.py (OPENROUTER_API_KEY, SMART_MODEL)
│   └── utils.py (streaming helpers)
│   └── OpenRouter
├── llm_centric_detector.py (NEW)
│   └── config.py (OPENROUTER_API_KEY, SMART_MODEL)
│   └── OpenRouter
├── findings_filter.py
│   └── (self-contained, regex patterns)
├── findings_validator.py
│   └── config.py (OPENROUTER_API_KEY, SMART_MODEL)
│   └── OpenRouter
├── project_indexer.py
│   └── redis_client.py
├── deepwiki_utils.py
│   └── redis_client.py
├── poc.py
│   └── config.py
│   └── OpenRouter
└── utils.py (shared utilities)
    └── (line finding, fingerprinting, snippets)
```

## Summary

The system is designed as a **modular pipeline**:

1. **Entry**: `main.py` receives requests
2. **Context**: Redis + DeepWiki provide project context
3. **Detection**: Multiple tiers for cost/accuracy trade-off
4. **Filtering**: Two-phase (rules + LLM) or pure LLM
5. **Enrichment**: Add fingerprints and context
6. **Output**: JSON with findings and metadata

The **LLM-centric approach** (Tier 4) simplifies this by doing detection and filtering in a single intelligent LLM pass, trading cost for accuracy.
