# SentinAI v4 — Agent Logging System

This document describes the comprehensive logging system for the multi-agent pipeline, which tracks all agent inputs, outputs, and execution states.

---

## Overview

The Agent Logging System provides detailed, structured logging for every agent in the multi-agent pipeline. It logs:

- **Agent starts** — Which agent, what context, what configuration
- **Agent prompts** — The exact prompt sent to the LLM
- **Agent responses** — The raw LLM response and latency
- **Agent findings** — What vulnerabilities were detected
- **Agent completions** — Timing, token usage, errors
- **Phase transitions** — When pipeline moves between phases
- **Post-processing** — Deduplication, consensus, skeptic review
- **Errors** — Exceptions, stack traces, failure points

All logs are stored in JSONL format (one JSON object per line) for easy parsing and analysis.

---

## Log File Locations (Windows)

```
C:\Users\Ren-pc\Desktop\main\sentinai-v4\backend\worker\data\agent_logs\
├── agent_log_{scan_id}_{timestamp}.jsonl        # Detailed event log
└── agent_summary_{scan_id}_{timestamp}.json    # Summary statistics
```

**Note:** The logger automatically creates this directory if it doesn't exist.

---

## Log Structure

### Event Types

Every log entry has an `event_type` field indicating what happened:

| Event Type | Description |
|-----------|-------------|
| `scan_start` | Scan initialized |
| `agent_start` | Agent begins execution |
| `agent_prompt` | Prompt sent to LLM |
| `agent_response` | LLM response received |
| `agent_findings` | Findings parsed from response |
| `agent_complete` | Agent finished |
| `phase_transition` | Pipeline phase changed |
| `deduplication` | Deduplication results |
| `consensus_scoring` | Consensus scoring results |
| `skeptic_review` | Skeptic verdicts |
| `chain_combiner` | Vulnerability chains created |
| `attack_paths` | Attack paths simulated |
| `remediation` | Remediation plans generated |
| `error` | Error occurred |
| `scan_complete` | Scan finished |

---

## Sample Log Entries

### 1. Scan Start

```json
{
  "event_type": "scan_start",
  "timestamp": "2026-03-12T10:30:00.000Z",
  "scan_id": "scan_user123_1710237600",
  "log_version": "1.0",
  "seq": 0,
  "elapsed_ms": 0
}
```

### 2. Agent Start

```json
{
  "event_type": "agent_start",
  "agent_name": "InjectionSpecialist",
  "agent_type": "specialist",
  "context_summary": {
    "file_count": 42,
    "entry_points_count": 15,
    "call_graph_nodes": 127,
    "language": "python",
    "framework": "flask",
    "scan_mode": "full"
  },
  "context_full": {
    "scan_id": "scan_user123_1710237600",
    "repo_path": "/tmp/project_abc123",
    "language": "python",
    "framework": "flask",
    "file_contents": { ... },
    "call_graph": { ... },
    "entry_points": [ ... ]
  },
  "config": {
    "max_retries": 3,
    "timeout_seconds": 120
  },
  "seq": 5,
  "elapsed_ms": 850
}
```

### 3. Agent Prompt

```json
{
  "event_type": "agent_prompt",
  "agent_name": "InjectionSpecialist",
  "prompt_length": 8456,
  "prompt_tokens": 2114,
  "prompt_preview": "You are a security specialist focused on injection vulnerabilities...",
  "prompt_full": "You are a security specialist focused on injection vulnerabilities...",
  "seq": 6,
  "elapsed_ms": 875
}
```

### 4. Agent Response

```json
{
  "event_type": "agent_response",
  "agent_name": "InjectionSpecialist",
  "response_length": 2341,
  "response_tokens": 585,
  "latency_ms": 3420,
  "response_preview": "{\"findings\": [{\"finding_id\": \"INJ-001\", \"vulnerability_class\": \"SQL Injection\"...",
  "response_full": "{\"findings\": [{\"finding_id\": \"INJ-001\", \"vulnerability_class\": \"SQL Injection\"...",
  "seq": 7,
  "elapsed_ms": 4295
}
```

### 5. Agent Findings

```json
{
  "event_type": "agent_findings",
  "agent_name": "InjectionSpecialist",
  "findings_count": 3,
  "findings": [
    {
      "finding_id": "INJ-001",
      "agent_source": "InjectionSpecialist",
      "file_path": "app.py",
      "line_start": 45,
      "line_end": 48,
      "vulnerability_class": "SQL Injection",
      "cwe_id": "CWE-89",
      "severity": "high",
      "confidence": 0.92,
      "reasoning": "User input from request.args.get('id') flows directly into SQL query without sanitization..."
    },
    ...
  ],
  "parsing_errors": [],
  "seq": 8,
  "elapsed_ms": 4310
}
```

### 6. Agent Complete

```json
{
  "event_type": "agent_complete",
  "agent_name": "InjectionSpecialist",
  "execution_time_ms": 3460,
  "token_usage": 2699,
  "errors": [],
  "findings_count": 3,
  "seq": 9,
  "elapsed_ms": 4320
}
```

### 7. Phase Transition

```json
{
  "event_type": "phase_transition",
  "from_phase": "pre-scan",
  "to_phase": "specialist-detection",
  "phase_data": {
    "entry_points": 15
  },
  "seq": 12,
  "elapsed_ms": 5000
}
```

### 8. Deduplication

```json
{
  "event_type": "deduplication",
  "input_findings": 23,
  "output_findings": 18,
  "duplicates_found": 5,
  "deduplication_ratio": 21.74,
  "merged_groups": [
    {
      "merged_finding_id": "MERGE-001",
      "contributing_findings": ["INJ-001", "INJ-003"],
      "reason": "Same file, overlapping lines, same vulnerability class"
    },
    ...
  ],
  "seq": 20,
  "elapsed_ms": 8500
}
```

### 9. Consensus Scoring

```json
{
  "event_type": "consensus_scoring",
  "findings_scored": 18,
  "adjustments": [
    {
      "finding_id": "INJ-001",
      "original_confidence": 0.92,
      "adjustment": 0.125,
      "reason": "2 agents agree (base + 0.125)",
      "new_confidence": 1.0
    },
    ...
  ],
  "seq": 21,
  "elapsed_ms": 8650
}
```

### 10. Skeptic Review

```json
{
  "event_type": "skeptic_review",
  "findings_reviewed": 18,
  "verdicts": [
    {
      "finding_id": "INJ-001",
      "verdict": "confirmed",
      "confidence_adjustment": 0.1
    },
    {
      "finding_id": "AUTH-007",
      "verdict": "downgraded",
      "confidence_adjustment": -0.15
    },
    {
      "finding_id": "CONFIG-012",
      "verdict": "rejected"
    }
  ],
  "rejection_rate": 0.06,
  "confirmed": 15,
  "downgraded": 2,
  "rejected": 1,
  "seq": 22,
  "elapsed_ms": 9200
}
```

### 11. Chain Combiner

```json
{
  "event_type": "chain_combiner",
  "chains_created": 2,
  "unchained_findings": 12,
  "chains": [
    {
      "chain_id": "CHAIN-001",
      "chain_name": "Auth Bypass → IDOR → Data Exfiltration",
      "findings": ["AUTH-007", "IDOR-003", "INJ-015"],
      "entry_point": {
        "entry_type": "http",
        "file_path": "routes/auth.py",
        "line_number": 42,
        "function_name": "login"
      },
      "impact": "Full database read access",
      "exploitability": "medium",
      "chain_length": 3
    },
    ...
  ],
  "seq": 23,
  "elapsed_ms": 9350
}
```

### 12. Attack Paths

```json
{
  "event_type": "attack_paths",
  "paths_simulated": 2,
  "paths": [
    {
      "path_id": "PATH-001",
      "entry_point": { ... },
      "chains_involved": ["CHAIN-001"],
      "steps": [
        {
          "step_number": 1,
          "action": "Exploit authentication bypass",
          "target_endpoint": "/auth/login",
          "payload_type": "SQL injection",
          "expected_response": "Admin session token",
          "finding_reference": "AUTH-007"
        },
        {
          "step_number": 2,
          "action": "Use admin session to access user list",
          "target_endpoint": "/api/users",
          "payload_type": "None",
          "expected_response": "List of all users",
          "finding_reference": "IDOR-003"
        }
      ],
      "final_impact": "Full database read",
      "attacker_prerequisites": ["Valid user account"],
      "estimated_complexity": "medium"
    }
  ],
  "seq": 24,
  "elapsed_ms": 9500
}
```

### 13. Remediation

```json
{
  "event_type": "remediation",
  "remediations_generated": 15,
  "remediations": [
    {
      "finding_id": "INJ-001",
      "fix_description": "Use parameterized queries instead of string concatenation",
      "fixed_code": "cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
      "fix_type": "patch",
      "unit_test_code": "def test_sql_injection():\n    response = client.get('/api/users?id=1 OR 1=1')\n    assert response.status_code == 400",
      "unit_test_framework": "pytest",
      "verification_steps": [
        "Run unit test: pytest test_sql_injection.py",
        "Verify no SQL errors in logs",
        "Run integration test with malicious input"
      ],
      "regression_risk": "low"
    }
  ],
  "seq": 25,
  "elapsed_ms": 10500
}
```

### 14. Error

```json
{
  "event_type": "error",
  "agent_name": "ChainCombiner",
  "error_type": "ValueError",
  "error_message": "Invalid finding format: missing taint_path",
  "stack_trace": "Traceback (most recent call last):\n  File ...",
  "seq": 26,
  "elapsed_ms": 10600
}
```

### 15. Scan Complete

```json
{
  "event_type": "scan_complete",
  "total_time_ms": 10500,
  "final_stats": {
    "total_findings": 15,
    "agent_model": "minimax",
    "scan_mode": "full"
  },
  "seq": 27,
  "elapsed_ms": 10500
}
```

---

## Summary File

The summary file (`agent_summary_{scan_id}_{timestamp}.json`) contains aggregated statistics:

```json
{
  "scan_id": "scan_user123_1710237600",
  "log_id": "scan_user123_1710237600_1710237600",
  "start_time": "2026-03-12T10:30:00.000Z",
  "end_time": "2026-03-12T10:30:10.500Z",
  "total_time_ms": 10500,
  "total_entries": 27,
  "log_file": "/path/to/agent_log_scan_user123_1710237600_1710237600.jsonl",
  "event_counts": {
    "scan_start": 1,
    "agent_start": 8,
    "agent_prompt": 8,
    "agent_response": 8,
    "agent_findings": 8,
    "agent_complete": 8,
    "phase_transition": 6,
    "deduplication": 1,
    "consensus_scoring": 1,
    "skeptic_review": 1,
    "chain_combiner": 1,
    "attack_paths": 1,
    "remediation": 1,
    "scan_complete": 1
  },
  "agent_summary": {
    "ReconAgent": {
      "execution_time_ms": 850,
      "token_usage": 1200,
      "findings_count": 15,
      "errors": []
    },
    "PatternAgent": {
      "execution_time_ms": 720,
      "token_usage": 980,
      "findings_count": 1,
      "errors": []
    },
    "ThreatModelAgent": {
      "execution_time_ms": 1150,
      "token_usage": 1800,
      "findings_count": 4,
      "errors": []
    },
    "InjectionSpecialist": {
      "execution_time_ms": 3460,
      "token_usage": 2699,
      "findings_count": 3,
      "errors": []
    },
    "AuthSpecialist": {
      "execution_time_ms": 2890,
      "token_usage": 2150,
      "findings_count": 2,
      "errors": []
    },
    "CryptoSpecialist": {
      "execution_time_ms": 1650,
      "token_usage": 1300,
      "findings_count": 1,
      "errors": []
    },
    "LogicAnalyst": {
      "execution_time_ms": 2100,
      "token_usage": 1750,
      "findings_count": 0,
      "errors": []
    },
    "ConfigHunter": {
      "execution_time_ms": 1430,
      "token_usage": 1100,
      "findings_count": 2,
      "errors": []
    }
  },
  "final_stats": {
    "total_findings": 15,
    "agent_model": "minimax",
    "scan_mode": "full"
  }
}
```

---

## Using the Log Viewer (Windows)

We've included a Windows-friendly Python script to view and analyze logs:

### View All Logs

```powershell
cd C:\Users\Ren-pc\Desktop\main\sentinai-v4\backend\worker\core
python view_agent_logs.py list
```

### View Summary

```powershell
python view_agent_logs.py summary scan_user123_1710237600
```

### View Timeline

```powershell
python view_agent_logs.py timeline scan_user123_1710237600
```

### View Errors

```powershell
python view_agent_logs.py errors scan_user123_1710237600
```

### View Agent Performance

```powershell
python view_agent_logs.py agents scan_user123_1710237600
```

### View All Findings

```powershell
python view_agent_logs.py findings scan_user123_1710237600
```

---

## Using the Logger

### In Code

```python
from backend.worker.core.agents.agent_logger import AgentLogger, set_logger, get_logger

# Initialize logger for a scan
logger = AgentLogger(scan_id="scan_user123_1710237600")
set_logger(logger)

# Log agent start
logger.log_agent_start(
    agent_name="InjectionSpecialist",
    agent_type="specialist",
    context={
        "file_count": 42,
        "language": "python",
        ...
    },
    config={
        "max_retries": 3,
        "timeout_seconds": 120,
    },
)

# Log agent findings
logger.log_agent_findings(
    agent_name="InjectionSpecialist",
    findings=[{...}, {...}],
)

# Log phase transition
logger.log_phase_transition(
    from_phase="pre-scan",
    to_phase="specialist-detection",
    phase_data={"entry_points": 15},
)

# Finalize and get summary
summary = logger.finalize(final_stats={
    "total_findings": 15,
    "agent_model": "minimax",
})

# Clear logger when done
from backend.worker.core.agents.agent_logger import clear_logger
clear_logger()
```

### Automatic Logging

The `BaseAgent.run()` method automatically logs:
- Agent start (with context summary)
- Agent prompt
- Agent response
- Agent findings
- Agent complete

The `AgentCoordinator` automatically logs:
- Phase transitions between stages
- Post-processing results (dedup, consensus, skeptic)

---

## Log Analysis (Windows)

### Query Logs with PowerShell

```powershell
# Get all findings for a specific agent
Get-Content agent_log_*.jsonl | ConvertFrom-Json | Where-Object { $_.event_type -eq "agent_findings" -and $_.agent_name -eq "InjectionSpecialist" }

# Get all errors
Get-Content agent_log_*.jsonl | ConvertFrom-Json | Where-Object { $_.event_type -eq "error" }

# Get agent execution times
Get-Content agent_log_*.jsonl | ConvertFrom-Json | Where-Object { $_.event_type -eq "agent_complete" } | Select-Object agent_name, execution_time_ms

# Count findings per agent
Get-Content agent_log_*.jsonl | ConvertFrom-Json | Where-Object { $_.event_type -eq "agent_complete" } | Group-Object agent_name | Select-Object Name, Count
```

### Query Logs with Python (Cross-platform)

```python
import json
from pathlib import Path

log_dir = Path("C:/Users/Ren-pc/Desktop/main/sentinai-v4/backend/worker/data/agent_logs")

# Get all findings for a specific agent
for log_file in log_dir.glob("agent_log_*.jsonl"):
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("event_type") == "agent_findings" and entry.get("agent_name") == "InjectionSpecialist":
                print(f"Found {entry['findings_count']} findings")

# Get all errors
for log_file in log_dir.glob("agent_log_*.jsonl"):
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("event_type") == "error":
                print(f"{entry['agent_name']}: {entry['error_message']}")

# Get agent execution times
import matplotlib.pyplot as plt

agent_times = {}
for log_file in log_dir.glob("agent_log_*.jsonl"):
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("event_type") == "agent_complete":
                agent_times[entry["agent_name"]] = entry["execution_time_ms"]

# Plot
plt.bar(agent_times.keys(), agent_times.values())
plt.xlabel("Agent")
plt.ylabel("Execution Time (ms)")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("agent_times.png")
plt.show()
```

### Visualize Timeline

```python
import json
import matplotlib.pyplot as plt

# Load log entries
entries = []
with open("agent_log_scan_user123_1710237600.jsonl", "r") as f:
    for line in f:
        entries.append(json.loads(line))

# Extract timing for each agent
agent_times = {}
for entry in entries:
    if entry["event_type"] == "agent_complete":
        agent_times[entry["agent_name"]] = entry["execution_time_ms"]

# Plot
plt.bar(agent_times.keys(), agent_times.values())
plt.xlabel("Agent")
plt.ylabel("Execution Time (ms)")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("agent_times.png")
```

---

## Log Retention (Windows)

Logs are stored in `C:\Users\Ren-pc\Desktop\main\sentinai-v4\backend\worker\data\agent_logs\`. You should implement a log rotation policy:

```python
# Example: Delete logs older than 30 days (Windows)
import os
import time
from pathlib import Path

log_dir = Path("C:/Users/Ren-pc/Desktop/main/sentinai-v4/backend/worker/data/agent_logs")
now = time.time()
max_age_days = 30

for log_file in log_dir.glob("*.jsonl"):
    if (now - log_file.stat().st_mtime) > (max_age_days * 86400):
        log_file.unlink()

for summary_file in log_dir.glob("*.json"):
    if (now - summary_file.stat().st_mtime) > (max_age_days * 86400):
        summary_file.unlink()
```

### Or use PowerShell:

```powershell
# Delete logs older than 30 days
$logDir = "C:\Users\Ren-pc\Desktop\main\sentinai-v4\backend\worker\data\agent_logs"
$cutoffDate = (Get-Date).AddDays(-30)

Get-ChildItem $logDir -Filter "*.jsonl" | Where-Object { $_.LastWriteTime -lt $cutoffDate } | Remove-Item
Get-ChildItem $logDir -Filter "*.json" | Where-Object { $_.LastWriteTime -lt $cutoffDate } | Remove-Item
```

---

## Performance Impact

- **Minimal overhead**: Logging adds ~1-5ms per operation
- **Async writes**: File I/O happens in background thread
- **Bounded memory**: Log buffer cleared after each scan
- **Compressed storage**: JSONL format is highly compressible

---

## Future Enhancements

1. **Log compression** — Gzip old logs automatically
2. **Log aggregation** — Send logs to centralized logging service
3. **Real-time dashboard** — WebSocket streaming to UI
4. **Log search API** — Query logs from API
5. **Anomaly detection** — Alert on unusual agent behavior

---

*Last updated: 2026-03-12*