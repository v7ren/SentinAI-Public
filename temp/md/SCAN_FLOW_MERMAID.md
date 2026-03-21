# Sentinel AI Scan Flow: Backend + Worker

This document describes how a security scan flows from the Flask backend (`backend/main_integrated.py`) to the FastAPI worker (`backend/worker/core/main.py`) and back.

---

## 1. High-Level Architecture

```mermaid
flowchart LR
    subgraph Client
        Browser[Browser / Frontend]
    end

    subgraph Backend["Backend (Flask :5001)"]
        API["/api/scan/start\n/api/scan/events\n/api/scan/status"]
        ScanLoop["_run_scan_events"]
        WorkerCall["send_to_worker"]
        Index["index_project_on_workers\nindex_project_deepwiki"]
        DB[(SQLite / JSON)]
    end

    subgraph Worker["Worker (FastAPI :5002)"]
        ScanEP["POST /scan"]
        IndexEP["POST /index_project\nPOST /index_project_deepwiki"]
        PocEP["POST /poc"]
        Redis[(Redis)]
    end

    Browser -->|POST multipart| API
    API --> ScanLoop
    ScanLoop --> Index
    Index -->|files + scan_id| IndexEP
    IndexEP --> Redis
    ScanLoop -->|per file| WorkerCall
    WorkerCall -->|filename, content, scan_id, scan_type| ScanEP
    ScanEP --> Redis
    ScanLoop --> DB
```

---

## 2. Backend: Scan Lifecycle (main_integrated.py)

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as /api/scan/start
    participant BG as Background Thread
    participant Events as _run_scan_events
    participant Index as index_project / DeepWiki
    participant Worker as send_to_worker
    participant W as Worker :5002
    participant DB as DB / File

    FE->>+API: POST files, project_name, scan_type
    API->>API: Auth (get_current_user_email)
    API->>API: temp_dir, _save_uploaded_files_secure
    API->>API: scan_id = scan_{email}_{timestamp}
    API->>BG: _run_scan_background_async(...)
    API-->>-FE: { scan_id }

    FE->>API: GET /api/scan/events/<scan_id> (SSE)
    Note over FE,API: SSE stream replays event_log

    BG->>+Events: _run_scan_events(...)
    Events-->>FE: SSE: start, log
    alt scan_type 2, 3, or 4
        Events->>Index: analyze_project_structure(temp_dir)
        Events->>Index: index_project_on_workers(temp_dir, scan_id)
        Events->>Index: index_project_deepwiki_on_workers(temp_dir, scan_id)
    else scan_type 1
        Events->>Index: index_project_on_workers only
    end
    Index->>W: POST /index_project, POST /index_project_deepwiki
    Events-->>FE: SSE: log "Scanning files..."

    loop For each valid file
        Events-->>FE: SSE: file_start
        Events->>Worker: send_to_worker(filename, content, scan_id, scan_type)
        Worker->>W: POST /scan (x-secret, x-scan-id, x-scan-type)
        W-->>Worker: { status, findings, logs }
        Worker-->>Events: data
        alt status VULNERABLE
            Events-->>FE: SSE: vuln_found, progress
        else SAFE / no data
            Events-->>FE: SSE: file_safe, progress
        end
    end

    Events->>DB: save_scan_result, save_scan_result_to_file
    Events-->>FE: SSE: complete, _final
    Events-->>-BG: done
```

---

## 3. Backend: _run_scan_events Flow (Simplified)

```mermaid
flowchart TB
    Start([Start _run_scan_events]) --> Init["Emit: start, log 'Initializing...'"]
    Init --> NeedIndex{"scan_type 2, 3 or 4?"}
    NeedIndex -->|Yes| Analyze["analyze_project_structure(temp_dir)"]
    NeedIndex -->|No| IndexAll
    Analyze --> IndexAll["index_project_on_workers(temp_dir, scan_id)"]
    IndexAll --> NeedDeepWiki{"scan_type 2, 3 or 4?"}
    NeedDeepWiki -->|Yes| DeepWiki["index_project_deepwiki_on_workers(temp_dir, scan_id)"]
    NeedDeepWiki -->|No| ScanFiles
    DeepWiki --> ScanFiles["Emit: log 'Scanning files...'"]

    ScanFiles --> Filter["For each file: filter by VALID_EXTENSIONS,\nignore IGNORE_DIRS, max 1MB"]
    Filter --> Submit["executor.submit(send_to_worker, ...)\nThreadPoolExecutor max_workers=MAX_WORKERS"]
    Submit --> Collect["as_completed(future_map)"]
    Collect --> Result{Worker response}
    Result -->|data present| Parse["Parse findings, build structured_issues"]
    Result -->|null / error| Safe["Emit: file_safe, progress"]
    Parse --> Vuln["Emit: vuln_found, progress\nAppend to results"]
    Vuln --> More{More files?}
    Safe --> More
    More -->|Yes| Collect
    More -->|No| Final["Build final_scan_data\nsave_scan_result()\nsave_scan_result_to_file()"]
    Final --> EmitComplete["Emit: complete, _final"]
    EmitComplete --> End([End])
```

---

## 4. Worker: POST /scan Pipeline (main.py)

```mermaid
flowchart TB
    Scan([POST /scan]) --> Auth["Check x-secret == WORKER_SECRET"]
    Auth --> Ctx["Load context from Redis:\n- ProjectIndexer (regex/symbol)\n- DeepWiki project_ir → build_security_context"]
    Ctx --> Kw["check_keywords(content)"]
    Kw --> Compact{Context compaction enabled\nand file large and tier 2/3/4?}
    Compact -->|Yes| CompactFn["compact_security_context()\n→ content_for_advanced"]
    Compact -->|No| Tier1
    CompactFn --> Tier1["scan_tier_1_basic (CHEAP_MODEL)\nAlways runs for every request"]

    Tier1 --> Status["status = triage_result.status\n(VULNERABLE or SAFE)"]

    Status --> Type4{x_scan_type == '4'\nor use_llm_centric?}
    Type4 -->|Yes| LLMCentric["llm_centric_scan()\nSingle-pass detection + filter"]
    LLMCentric --> LLMResult{Has findings?}
    LLMResult -->|Yes| Enrich4["Enrich (line, code_context, fingerprint)\nReturn VULNERABLE"]
    LLMResult -->|No| Fallback1["Fallback: use Tier 1 results if any\nelse return SAFE"]
    Fallback1 --> Tier1Path

    Type4 -->|No| Tier1Path{x_scan_type == '1'?}
    Tier1Path -->|Yes| T1Filter["Two-phase FP filter:\nPhase 1: FindingsFilter (hard exclusions)\nPhase 2: apply_two_phase_validation (LLM)"]
    T1Filter --> Cap["Cap Phase 2 at FREE_TIER_PHASE2_MAX_FINDINGS"]
    Cap --> ReturnT1["Enrich, return triage_result"]

    Tier1Path -->|No| SafePath{status == SAFE?}
    SafePath -->|Yes| Escalate{"ENABLE_TIER23_SAFE_ESCALATION\nand keywords >= N?"}
    Escalate -->|Yes| ForceVuln["Treat as VULNERABLE, continue to Tier 2/3"]
    Escalate -->|No| ReturnSafe["Return SAFE (skip Tier 2/3 provider)"]
    SafePath -->|No| ForceVuln

    ForceVuln --> Tier23{x_scan_type == '2' or '3'?}
    Tier23 -->|2| T2["scan_tier_2_standard\n(SMART_MODEL, CWE/confidence)"]
    Tier23 -->|3| T3["scan_tier_3_advanced\n(SMART_MODEL stream, CVSS/remediation)"]
    T2 --> Large{File > 20k chars?}
    T3 --> Large
    Large -->|Yes| Focus["tier1_result passed:\nbuild_focused_code_bundle()\n→ only suspicious snippets"]
    Large -->|No| Full["Full file content"]
    Focus --> T2
    Full --> T2

    T2 --> Fallback2{Tier 2/3 failed\nbut Tier 1 said VULNERABLE?}
    T3 --> Fallback2
    Fallback2 -->|Yes| ReturnT1Fallback["Return Tier 1 result + note"]
    Fallback2 -->|No| Enrich["Enrich: keywords_detected, code_context, fingerprint"]
    Enrich --> Phase1["Phase 1: FindingsFilter (hard exclusions)"]
    Phase1 --> Phase2["Phase 2: apply_two_phase_validation (LLM)"]
    Phase2 --> ReturnT23["Return final_result"]

    ReturnT1 --> End([Response])
    ReturnT4 --> End
    ReturnSafe --> End
    ReturnT1Fallback --> End
    ReturnT23 --> End
    Enrich4 --> End
```

---

## 5. Worker: Tier Summary

| Tier | Name        | Model        | Purpose |
|------|-------------|-------------|---------|
| 1    | Basic       | CHEAP_MODEL | High-recall triage; two-phase FP filter (hard exclusions + capped LLM validation) |
| 2    | Standard    | SMART_MODEL   | CWE, confidence; focused bundle for large files |
| 3    | Advanced    | SMART_MODEL   | CVSS, remediation, consequences; focused bundle for large files |
| 4    | LLM-Centric | SMART_MODEL   | Single-pass detection + filtering; fallback to Tier 1 if 0 findings |

---

## 6. Worker Endpoints Used by Backend

```mermaid
flowchart LR
    subgraph Backend
        B1["index_project_on_workers"]
        B2["index_project_deepwiki_on_workers"]
        B3["analyze_project_structure"]
        B4["send_to_worker"]
        B5["request_pocs_from_worker"]
        B6["get_scan_docs"]
    end

    subgraph Worker
        W1["POST /index_project"]
        W2["POST /index_project_deepwiki"]
        W3["POST /analyze"]
        W4["POST /scan"]
        W5["POST /poc"]
        W6["GET /deepwiki_docs"]
    end

    B1 --> W1
    B2 --> W2
    B3 --> W3
    B4 --> W4
    B5 --> W5
    B6 --> W6
```

---

## 7. Data Flow: Index → Scan

```mermaid
flowchart TB
    subgraph Backend
        Upload["Upload files → temp_dir"]
        Walk["Walk tree, filter VALID_EXTENSIONS"]
        Payload["Build files_payload: filename + content"]
    end

    subgraph Worker
        IndexProject["/index_project\nProjectIndexer.index_file()\n→ to_json()"]
        IndexDeepWiki["/index_project_deepwiki\nLLMProjectIndexer.build_index()\nWikiGenerator.generate_all()"]
        Redis[(Redis)]
    end

    subgraph ScanTime
        GetIndex["redis_client.get(scan_id)"]
        GetDeepWiki["redis_client.get(scan_id:deepwiki_index)"]
        Ctx["indexer.get_context_for_code()\nbuild_security_context(project_ir)"]
        Scan["/scan uses context + content"]
    end

    Upload --> Walk --> Payload
    Payload --> IndexProject
    Payload --> IndexDeepWiki
    IndexProject --> Redis
    IndexDeepWiki --> Redis
    Redis --> GetIndex
    Redis --> GetDeepWiki
    GetIndex --> Ctx
    GetDeepWiki --> Ctx
    Ctx --> Scan
```

---

## 8. SSE Events (Frontend ↔ Backend)

| Event Type   | Direction   | Meaning |
|-------------|-------------|---------|
| `start`     | Backend→FE  | Scan phase started; `msg` describes phase |
| `log`       | Backend→FE  | Log line; `filename`, `msg` |
| `file_start`| Backend→FE  | Started scanning a file |
| `vuln_found`| Backend→FE  | File has issues; `filename`, `count`, `issues` |
| `file_safe` | Backend→FE  | File has no (remaining) findings |
| `progress`  | Backend→FE  | `files_scanned`, `total_files` |
| `complete`  | Backend→FE  | Scan done; `scan_id` |
| `_final`    | Internal    | Not sent to client; carries final `data` or `error` |

---

## 9. send_to_worker (Backend → Worker)

```mermaid
flowchart LR
    A["send_to_worker(filename, content, scan_id, scan_type)"] --> B["Round-robin: _next_worker_node()"]
    B --> C["Headers: x-secret, x-scan-id, x-scan-type"]
    C --> D["POST {node}/scan\nbody: filename, content"]
    D --> E{HTTP 200?}
    E -->|Yes| F["Parse JSON, return data"]
    E -->|429| G["Try next node or sleep retry"]
    E -->|Other| G
    G --> D
```

- Retries: up to 3 global attempts; on 429, rotate nodes and optionally sleep.
- Response: `{ status, findings, logs }` or `null` on failure.

---

*Generated from `backend/main_integrated.py` and `backend/worker/core/main.py`.*
