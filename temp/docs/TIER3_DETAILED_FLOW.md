# Tier 3 Scan - Detailed Flow

## Overview

This document shows the complete flow of a Tier 3 scan, from user input to final output, including which files are called at each step.

## High-Level Flow

```mermaid
flowchart TB
    subgraph UserInput["1. User Input"]
        A[User selects Tier 3 scan]
        B[Uploads code file]
    end

    subgraph API["2. Main API (main4.py)"]
        C[POST /scan endpoint]
        D{Validate headers}
        E[Queue scan job]
    end

    subgraph Worker["3. Worker Service (main.py)"]
        F[scan_code() function]
        G[Build context]
        H{Decision Logic}
    end

    subgraph Tier1["4. Tier 1 Triage (ai_tier1.py)"]
        I[scan_tier_1_basic()]
        J[CHEAP_MODEL]
    end

    subgraph Tier3["5. Tier 3 Deep Analysis (ai_tier3.py)"]
        K[scan_tier_3_advanced()]
        L[Build focused code bundle]
        M[Streaming LLM call]
        N[Parse JSON stream]
        O[Repair if truncated]
    end

    subgraph Filtering["6. Two-Phase Filtering"]
        P[findings_filter.py<br/>Hard exclusions]
        Q[findings_validator.py<br/>Parallel LLM validation]
    end

    subgraph Enrich["7. Enrichment (utils.py)"]
        R[find_line_number()]
        S[get_bounded_snippet()]
        T[get_code_context_and_fingerprint()]
        U[find_keywords_with_lines()]
    end

    subgraph Output["8. Output Generation"]
        V[Format results]
        W[Return JSON]
    end

    A --> B --> C
    C --> D --> E --> F
    F --> G --> H
    H -->|X-Scan-Type: 3| Tier1
    Tier1 -->|Vulnerable| K
    K --> L --> M --> N --> O
    O --> P --> Q
    Q --> R --> S --> T --> U --> V --> W
```

## Detailed Step-by-Step Flow

```mermaid
sequenceDiagram
    participant User as User
    participant Client as Frontend Client
    participant MainAPI as main4.py<br/>POST /scan
    participant Worker as main.py<br/>Worker Service
    participant Redis as Redis Cache
    participant ProjectIndexer as project_indexer.py
    participant Tier1 as ai_tier1.py<br/>scan_tier_1_basic()
    participant OR1 as OpenRouter<br/>CHEAP_MODEL
    participant Tier3 as ai_tier3.py<br/>scan_tier_3_advanced()
    participant Utils as utils.py<br/>Helpers
    participant OR3 as OpenRouter<br/>SMART_MODEL
    participant Filter as findings_filter.py
    participant Validator as findings_validator.py
    participant Output as Output JSON

    %% Step 1: User Input
    User->>Client: Select "Tier 3 Deep Scan"
    User->>Client: Upload code file (e.g., app.py)
    Client->>MainAPI: POST /scan with headers:<br/>X-Scan-Type: 3<br/>X-Scan-ID: scan_123<br/>X-Secret: secret_key
    Note over MainAPI: Request body:<br/>{filename: "app.py", content: "..."}

    %% Step 2: API Validation
    MainAPI->>MainAPI: Check X-Secret == WORKER_SECRET
    MainAPI->>MainAPI: Parse ScanRequest model
    MainAPI->>Worker: Forward to worker service

    %% Step 3: Worker Setup
    Worker->>Worker: scan_code() function entry
    Worker->>Worker: logger.info("Scanning File: app.py | Plan: Tier 3")

    %% Step 4: Context Building
    Worker->>Redis: Check for existing context (x_scan_id)
    alt Context exists in Redis
        Redis-->>Worker: Return cached project_ir
    else No context
        Worker->>ProjectIndexer: ProjectIndexer.from_json()
        ProjectIndexer->>ProjectIndexer: build_index()
        ProjectIndexer->>Redis: Store in cache (SCAN_TTL)
    end

    Worker->>Worker: external_context = indexer.get_context_for_code()
    Worker->>Worker: deepwiki_context = build_security_context()
    Note over Worker: combined_context = external + deepwiki

    %% Step 5: Step 1 - Always Run Tier 1 First
    Worker->>Tier1: scan_tier_1_basic(session, filename, content, context_info)

    %% Tier 1 Execution
    Tier1->>Tier1: _build_system_prompt()
    Note over Tier1: Creates JSON schema for findings

    alt File > 12KB
        Tier1->>Tier1: _chunk_content(content)<br/>Split into overlapping chunks
        loop For each chunk
            Tier1->>Tier1: _scan_chunk()<br/>Add line numbers
            Tier1->>OR1: POST /chat/completions<br/>Model: CHEAP_MODEL
            OR1-->>Tier1: JSON with findings
            Tier1->>Tier1: Deduplicate with fingerprint
        end
    else Small file
        Tier1->>OR1: Single API call
        OR1-->>Tier1: findings[]
    end

    Tier1->>Tier1: Merge all findings
    Tier1-->>Worker: triage_result = {status, findings[]}

    %% Step 6: Decision Logic
    Worker->>Worker: Check if triage_result.status == "VULNERABLE"

    alt Status == SAFE
        Worker-->>Output: Return SAFE result (skip Tier 3)
    else Status == VULNERABLE
        Worker->>Worker: logger.warning("Escalating to Tier 3...")

        %% Step 7: Tier 3 Deep Analysis
        Worker->>Tier3: scan_tier_3_advanced(session, filename, content, context_info, tier1_result)

        %% Tier 3 Execution
        Tier3->>Tier3: _build_system_prompt()<br/>Enhanced prompt with:<br/>- CVSS scoring<br/>- Fix complexity<br/>- CWE mapping

        Tier3->>Utils: build_focused_code_bundle()<br/>Extract code around Tier 1 findings
        Note over Utils: max_findings=10, window=15 lines

        Tier3->>Tier3: _build_user_content()<br/>Combine context + focused code

        %% Streaming LLM Call
        Tier3->>OR3: POST /chat/completions<br/>Model: SMART_MODEL<br/>stream: true<br/>max_tokens: 16384

        loop Streaming chunks
            OR3-->>Tier3: data: {delta: {content: "..."}}
            Tier3->>Tier3: collected_content += delta.content
        end

        OR3-->>Tier3: data: [DONE]

        %% JSON Processing
        Tier3->>Tier3: clean_json_response()

        alt JSON valid
            Tier3->>Tier3: json.loads(content)
        else JSON truncated
            Tier3->>Utils: repair_or_complete_tier3_json()<br/>Ask LLM to complete
            Utils->>OR3: Repair API call
            OR3-->>Utils: Completed JSON
            Utils-->>Tier3: repaired_data
        end

        Tier3->>Tier3: For each finding:<br/>- find_line_number()<br/>- get_bounded_snippet()<br/>- Add line numbers

        Tier3-->>Worker: final_result = {status, findings[], ...}
    end

    %% Step 8: Enrichment
    Worker->>Utils: find_keywords_with_lines()<br/>Pattern matching for keywords
    loop For each finding
        Worker->>Utils: get_code_context_and_fingerprint()<br/>Generate unique hash
        Utils-->>Worker: {code_context, fingerprint}
        Worker->>Worker: finding.keywords_detected = [...]
        Worker->>Worker: finding.code_context = {...}
        Worker->>Worker: finding.fingerprint = "..."
    end

    %% Step 9: Two-Phase Filtering
    Worker->>Filter: FindingsFilter(use_hard_exclusions=True)<br/>Phase 1: Hard exclusions
    Filter->>Filter: _apply_hard_rules()<br/>- Regex exclusions<br/>- Confidence threshold
    Filter-->>Worker: phase1_filtered[]

    Worker->>Validator: apply_two_phase_validation()<br/>Phase 2: LLM validation
    loop For each finding (parallel, max 5)
        Validator->>Validator: _validate_single_finding()
        Validator->>OR3: Confidence judgment
        OR3-->>Validator: {confidence, keep}
    end
    Validator-->>Worker: phase2_kept[]

    %% Step 10: Final Output
    Worker->>Worker: Build _two_phase_summary<br/>with metadata

    Worker-->>Output: Return final_result

    Output-->>Client: JSON Response
    Client-->>User: Display vulnerabilities
```

## File Call Chain for Tier 3

```mermaid
flowchart LR
    subgraph Entry["Entry Point"]
        A[main4.py<br/>POST /scan]
    end

    subgraph Worker["Worker"]
        B[main.py<br/>scan_code()]
        C[models.py<br/>ScanRequest]
    end

    subgraph Context["Context Building"]
        D[redis_client.py<br/>Cache check]
        E[project_indexer.py<br/>Build index]
        F[deepwiki_utils.py<br/>Security context]
    end

    subgraph Detection["Detection Layer"]
        G[ai_tier1.py<br/>Quick triage]
        H[ai_tier3.py<br/>Deep analysis]
    end

    subgraph Utils["Utility Functions"]
        I[utils.py<br/>build_focused_code_bundle]
        J[utils.py<br/>find_line_number]
        K[utils.py<br/>get_bounded_snippet]
        L[utils.py<br/>get_code_context_and_fingerprint]
        M[utils.py<br/>find_keywords_with_lines]
        N[utils.py<br/>clean_json_response]
        O[utils.py<br/>repair_or_complete_tier3_json]
    end

    subgraph Filtering["Filtering Layer"]
        P[findings_filter.py<br/>Hard exclusions]
        Q[findings_validator.py<br/>LLM validation]
    end

    subgraph External["External Services"]
        R[OpenRouter<br/>CHEAP_MODEL]
        S[OpenRouter<br/>SMART_MODEL]
        T[Redis Server]
    end

    A -->|HTTP POST| B
    B -->|Validates| C

    B -->|Checks| D
    D -->|If miss| E
    E -->|Stores| D
    D -->|Connects| T
    E -->|Generates| F

    B -->|Calls| G
    G -->|Uses| N
    G -->|Chunks via| I
    G -->|API calls| R

    B -->|If vulnerable| H
    H -->|Uses| I
    H -->|Uses| N
    H -->|On failure| O
    H -->|API calls| S

    H -->|Line finding| J
    H -->|Snippet| K

    B -->|Filtering| P
    P -->|Validates| Q
    Q -->|API calls| S

    B -->|Enrichment| L
    B -->|Keywords| M
    M -->|Uses| keywords.py

    L -->|Helpers| I
    L -->|Helpers| J
    L -->|Helpers| K
```

## Function Call Hierarchy

```
main4.py
└── POST /scan endpoint
    └── Forwards to Worker Service

main.py
└── scan_code()
    ├── Step 1: Context Building
    │   ├── redis_client.get(x_scan_id)
    │   ├── ProjectIndexer.from_json()
    │   ├── indexer.get_context_for_code()
    │   └── build_security_context()
    │
    ├── Step 2: Tier 1 Triage (Always runs)
    │   └── ai_tier1.scan_tier_1_basic()
    │       ├── _build_system_prompt()
    │       ├── _chunk_content() [if large file]
    │       ├── _scan_chunk() [for each chunk]
    │       │   ├── _build_numbered_content()
    │       │   └── OpenRouter Call (CHEAP_MODEL)
    │       ├── find_line_number()
    │       └── Merge findings
    │
    ├── Step 3: Decision Logic
    │   └── If Vulnerable → Continue to Tier 3
    │
    ├── Step 4: Tier 3 Deep Analysis
    │   └── ai_tier3.scan_tier_3_advanced()
    │       ├── _build_system_prompt()
    │       ├── build_focused_code_bundle()
    │       │   └── utils.get_function_or_window()
    │       ├── _build_user_content()
    │       ├── OpenRouter Call (SMART_MODEL, streaming)
    │       ├── clean_json_response()
    │       ├── json.loads() [or repair]
    │       ├── repair_or_complete_tier3_json() [if needed]
    │       ├── find_line_number()
    │       ├── get_bounded_snippet()
    │       └── Return detailed findings
    │
    ├── Step 5: Enrichment
    │   ├── find_keywords_with_lines()
    │   │   └── keywords.py (ALL_KEYWORDS)
    │   └── For each finding:
    │       ├── get_code_context_and_fingerprint()
    │       │   ├── get_bounded_snippet()
    │       │   └── get_function_or_window()
    │       └── Add to finding object
    │
    ├── Step 6: Two-Phase Filtering
    │   ├── Phase 1: findings_filter.py
    │   │   └── FindingsFilter.filter_findings()
    │   │       └── _apply_hard_rules()
    │   └── Phase 2: findings_validator.py
    │       └── apply_two_phase_validation()
    │           └── _validate_single_finding() [parallel]
    │               └── OpenRouter Call (SMART_MODEL)
    │
    └── Step 7: Output
        └── Return JSON with metadata
```

## Data Transformations at Each Step

```mermaid
flowchart TB
    subgraph Input["Input Data"]
        A["File: app.py<br/>Content: raw code<br/>Headers: X-Scan-Type=3"]
    end

    subgraph Step1["Step 1: Context"]
        B["+ Project context<br/>+ Code graph<br/>+ Security context"]
    end

    subgraph Step2["Step 2: Tier 1"]
        C["Findings: [{type, severity, line, code}]<br/>Status: VULNERABLE/SAFE"]
    end

    subgraph Step3["Step 3: Tier 3"]
        D["Detailed Findings: [{<br/>type, severity, confidence,<br/>cwe_id, cvss_score,<br/>fix_complexity, remediation<br/>}]"]
    end

    subgraph Step4["Step 4: Enrichment"]
        E["+ fingerprints<br/>+ code_context<br/>+ keywords_detected<br/>+ surrounding_code"]
    end

    subgraph Step5["Step 5: Filtering"]
        F["Filtered: [{...<br/>_validation: {confidence, phase}<br/>}]<br/>Excluded: [{...<br/>_exclusion_reason<br/>}]"]
    end

    subgraph Output["Output"]
        G["JSON: {<br/>status, findings[],<br/>_two_phase_summary,<br/>_confidence_stats<br/>}"]
    end

    A -->|Build context| B
    B -->|Quick triage| C
    C -->|If vulnerable| D
    D -->|Add context| E
    E -->|Validate| F
    F -->|Format| G
```

## API Calls Made During Tier 3 Scan

| Step | File | API Call | Model | Purpose |
|------|------|----------|-------|---------|
| 1 | ai_tier1.py | OpenRouter /chat/completions | CHEAP_MODEL | Quick triage |
| 2 | ai_tier3.py | DeepInfra /chat/completions (stream) | SMART_MODEL | Deep analysis |
| 3 | utils.py (repair) | OpenRouter /chat/completions | SMART_MODEL | JSON repair (if truncated) |
| 4 | findings_validator.py | OpenRouter /chat/completions | SMART_MODEL | Per-finding validation (parallel) |

## Time Estimates

| Step | Duration | File(s) |
|------|----------|---------|
| Context building | 50-100ms | main.py, redis_client.py |
| Tier 1 scan | 2-5 seconds | ai_tier1.py |
| Tier 3 scan | 5-15 seconds | ai_tier3.py (streaming) |
| JSON repair (if needed) | +2-5 seconds | utils.py |
| Enrichment | 10-50ms | utils.py |
| Two-phase filtering | 2-10 seconds | findings_filter.py + findings_validator.py |
| **Total** | **10-35 seconds** | All files |

## Error Handling Flow

```mermaid
flowchart TD
    A[Start Tier 3]

    B{Tier 1 fails?}
    B -->|Yes| C[Return Tier 1 error]
    B -->|No| D{Status = VULNERABLE?}

    D -->|No| E[Return SAFE result]
    D -->|Yes| F[Start Tier 3]

    G{Tier 3 API error?}
    G -->|Yes| H{Has Tier 1 findings?}
    H -->|Yes| I[Return Tier 1 as fallback]
    H -->|No| J[Return ERROR status]

    G -->|No| K{JSON truncated?}
    K -->|Yes| L[Call repair_or_complete_tier3_json]
    L -->|Success| M[Continue]
    L -->|Failure| N[Return partial results]

    K -->|No| M

    M --> O{Validation fails?}
    O -->|Yes| P[Use hard filter results]
    O -->|No| Q[Return final results]

    C --> R[End]
    E --> R
    I --> R
    J --> R
    N --> R
    P --> R
    Q --> R
```

## Summary

**Tier 3 scan uses these files in order:**

1. **main4.py** - Entry point, validates request
2. **main.py** - Orchestrates the flow
3. **models.py** - Validates ScanRequest
4. **redis_client.py** - Checks cache
5. **project_indexer.py** - Builds project context
6. **deepwiki_utils.py** - Security context
7. **ai_tier1.py** - Quick triage (always runs)
8. **ai_tier3.py** - Deep analysis (if vulnerable)
9. **utils.py** - Code context, line finding, snippets, JSON repair
10. **keywords.py** - Pattern matching
11. **findings_filter.py** - Phase 1 hard exclusions
12. **findings_validator.py** - Phase 2 LLM validation
13. **config.py** - API keys, model settings

**External calls:**
- OpenRouter (CHEAP_MODEL for Tier 1)
- OpenRouter (SMART_MODEL for Tier 3 and validation)
- Redis (caching)
