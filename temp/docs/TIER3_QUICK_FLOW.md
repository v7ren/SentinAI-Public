# Tier 3 Quick Flow

## Simple Flow Diagram

```mermaid
flowchart TB
    User([User uploads file])
    Main4[main4.py]
    Worker[main.py - scan_code]
    Redis[redis_client.py]
    ProjectIndexer[project_indexer.py + deepwiki_utils.py]
    Tier1[ai_tier1.py - CHEAP_MODEL]
    Tier3[ai_tier3.py - SMART_MODEL]
    Utils1[utils.py - code bundling]
    Utils2[utils.py - JSON repair]
    Filter1[findings_filter.py]
    Filter2[findings_validator.py]
    Utils3[utils.py - enrichment]
    Keywords[keywords.py]
    Output([Return JSON])

    User -->|POST /scan X-Scan-Type: 3| Main4
    Main4 -->|Forward| Worker
    
    Worker -->|Check cache| Redis
    Worker -->|Build context| ProjectIndexer
    
    Worker -->|Always run| Tier1
    
    Tier1 -->|If VULNERABLE| Tier3
    Tier3 -->|Uses| Utils1
    Tier3 -->|If truncated| Utils2
    
    Tier3 --> Filter1
    Filter1 -->|Phase 1: Hard rules| Filter2
    Filter2 -->|Phase 2: LLM validation| Utils3
    
    Utils3 -->|Pattern matching| Keywords
    Utils3 -->|Add fingerprints| Output
```

## File Call Order

```mermaid
sequenceDiagram
    participant U as User
    participant M4 as main4.py
    participant W as main.py
    participant R as redis_client
    participant PI as project_indexer
    participant T1 as ai_tier1.py
    participant D1 as OpenRouter CHEAP_MODEL
    participant T3 as ai_tier3.py
    participant D3 as OpenRouter SMART_MODEL
    participant UF as utils.py
    participant FF as findings_filter.py
    participant FV as findings_validator.py
    participant K as keywords.py
    participant O as Output

    U->>M4: POST /scan (X-Scan-Type: 3)
    M4->>W: Forward request
    
    W->>R: Check Redis cache
    W->>PI: Build project context
    
    W->>T1: scan_tier_1_basic()
    T1->>D1: API call (CHEAP_MODEL)
    D1-->>T1: findings[]
    T1-->>W: triage_result
    
    Note over W: If status == VULNERABLE
    
    W->>T3: scan_tier_3_advanced()
    T3->>UF: build_focused_code_bundle()
    T3->>D3: Streaming API (SMART_MODEL)
    D3-->>T3: streamed JSON
    T3->>UF: repair_or_complete_tier3_json() [if needed]
    T3-->>W: detailed_findings[]
    
    W->>FF: Phase 1: Hard exclusions
    FF-->>W: phase1_filtered[]
    
    W->>FV: Phase 2: LLM validation
    FV->>D3: Validate each finding
    D3-->>FV: confidence scores
    FV-->>W: phase2_kept[]
    
    W->>UF: Enrichment
    W->>K: find_keywords_with_lines()
    UF-->>W: fingerprints, context
    
    W->>O: Return final JSON
    O-->>U: Results
```

## Files Used in Order

| Step | File | Key Function | Purpose |
|------|------|--------------|---------|
| 1 | **main4.py** | POST /scan | Entry point, validate headers |
| 2 | **main.py** | scan_code() | Orchestrate the flow |
| 3 | **models.py** | ScanRequest | Validate input |
| 4 | **redis_client.py** | get() | Check cached context |
| 5 | **project_indexer.py** | build_index() | Build project structure |
| 6 | **deepwiki_utils.py** | build_security_context() | Security context |
| 7 | **ai_tier1.py** | scan_tier_1_basic() | Quick triage (CHEAP_MODEL) |
| 8 | **ai_tier3.py** | scan_tier_3_advanced() | Deep analysis (SMART_MODEL) |
| 9 | **utils.py** | build_focused_code_bundle() | Extract code snippets |
| 10 | **utils.py** | repair_or_complete_tier3_json() | Fix truncated JSON |
| 11 | **findings_filter.py** | filter_findings() | Phase 1: Hard rules |
| 12 | **findings_validator.py** | validate_findings_parallel() | Phase 2: LLM validation |
| 13 | **utils.py** | find_keywords_with_lines() | Pattern matching |
| 14 | **utils.py** | get_code_context_and_fingerprint() | Add context |
| 15 | **keywords.py** | ALL_KEYWORDS | Keyword database |

## API Calls

```mermaid
graph LR
    subgraph Tier1["Tier 1"]
        A[ai_tier1.py] -->|CHEAP_MODEL| B[OpenRouter]
    end

    subgraph Tier3["Tier 3"]
        C[ai_tier3.py] -->|SMART_MODEL Streaming| D[OpenRouter]
    end

    subgraph Repair["Repair (if needed)"]
        E[utils.py] -->|SMART_MODEL| F[OpenRouter]
    end

    subgraph Validation["Validation"]
        G[findings_validator.py] -->|SMART_MODEL Parallel| H[OpenRouter]
    end

    B -.->|If vulnerable| C
    D -.->|If truncated| E
    D -.->|After analysis| G
```

## Data Flow

```mermaid
graph LR
    A[File Content] -->|+ Context| B[Tier 1]
    B -->|Findings| C{Status?}
    C -->|SAFE| D[Return SAFE]
    C -->|VULNERABLE| E[Tier 3]
    E -->|Detailed Findings| F[Filtering]
    F -->|Phase 1| G[Hard Rules]
    G -->|Phase 2| H[LLM Validation]
    H -->|Kept Findings| I[Enrichment]
    I -->|+ Fingerprints<br/>+ Context<br/>+ Keywords| J[Final Output]
```

## Visual Summary

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   main4.py   │────▶│   main.py    │────▶│    Redis     │
│   (Entry)    │     │ (Orchestrate)│     │    Cache     │
└──────────────┘     └──────────────┘     └──────────────┘
                             │
                             ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  ai_tier1.py │────▶│  ai_tier3.py │────▶│ findings_    │
│  (CHEAP_MODEL -     │     │ (SMART_MODEL -      │     │ filter.py    │
│   Triage)    │     │  Deep)       │     │ (Hard Rules) │
└──────────────┘     └──────────────┘     └──────────────┘
                             │                    │
                             ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   utils.py   │◀────│ findings_    │◀────│  utils.py    │
│ (Bundling)   │     │ validator.py │     │ (Keywords)   │
└──────────────┘     │(LLM Filter)  │     └──────────────┘
                             │
                             ▼
┌──────────────┐
│  keywords.py │
│(Pattern Match)│
└──────────────┘
```
