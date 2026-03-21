# Agent Log Server

Real-time WebSocket server for monitoring AI agent activities during security scans.

## Quick Start

```bash
# Start the log server
python -m backend.worker.core.start_log_server

# Or with custom port
python -m backend.worker.core.start_log_server --port 5004

# Or directly
python backend/worker/core/log_server.py
```

## Access Points

| Endpoint | Description |
|----------|-------------|
| `http://localhost:5003/` | Live dashboard UI |
| `ws://localhost:5003/ws/logs` | WebSocket stream |
| `http://localhost:5003/api/state` | Current state (REST) |
| `http://localhost:5003/api/history` | Event history (REST) |

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Agent Code    │────▶│   LogBridge      │────▶│   LogServer     │
│  (main.py)      │     │   (log_bridge.py)│     │  (log_server.py)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │   AgentLogger    │     │   WebSocket     │
                        │   (file-based)   │     │   Clients       │
                        └──────────────────┘     └─────────────────┘
```

## Event Types

| Event Type | Description | Color |
|------------|-------------|-------|
| `scan_start` | Scan initiated | Blue |
| `agent_start` | Agent begins execution | Blue |
| `agent_prompt` | Prompt sent to LLM | Purple |
| `agent_response` | Response from LLM | Green |
| `tool_call` | Tool/function called | Orange |
| `tool_result` | Tool returned result | Yellow |
| `agent_findings` | Vulnerabilities found | Red |
| `agent_complete` | Agent finished | Cyan |
| `phase_transition` | Pipeline phase change | Cyan |
| `error` | Error occurred | Red |
| `scan_complete` | Scan finished | Green |

## Integration in Agent Code

### Method 1: Using LogBridge (Recommended)

```python
from backend.worker.core.log_bridge import create_log_bridge, get_log_bridge

# At scan start
bridge = create_log_bridge(scan_id="scan-123")
bridge.start_scan(language="python", framework="flask", file_count=42)

# During agent execution
bridge.log_agent_start("InjectionSpecialist", "specialist", config={...})
bridge.log_agent_prompt("InjectionSpecialist", prompt, tokens=500)
bridge.log_agent_response("InjectionSpecialist", response, tokens=1200, latency_ms=3500)
bridge.log_agent_findings("InjectionSpecialist", findings_list)
bridge.log_agent_complete("InjectionSpecialist", exec_time_ms=5000, tokens=1700, errors=[], count=3)

# For tool calls (agentic agents)
bridge.log_tool_call("InjectionSpecialist", "read_file", {"path": "app.py"})
bridge.log_tool_result("InjectionSpecialist", "read_file", file_content)

# At scan end
bridge.end_scan(total_findings=12, total_time_ms=45000)
```

### Method 2: Convenience Functions

```python
from backend.worker.core.log_bridge import log_tool_call, log_tool_result

# Quick logging without bridge reference
log_tool_call("MyAgent", "search_code", {"query": "sql query"})
log_tool_result("MyAgent", "search_code", "Found 3 matches")
```

### Method 3: Direct Server Interface

```python
from backend.worker.core.log_server import log_interface

# Direct broadcast to WebSocket clients
log_interface.log_agent_prompt(
    agent_name="MyAgent",
    prompt="Analyze this code...",
    prompt_tokens=500,
    scan_id="scan-123",
)
```

## Dashboard Features

### Live Stream Tab
- Real-time event stream
- Filter by event type
- Text search filter
- Auto-scroll to latest events

### Prompts Tab
- All LLM prompts and responses
- Token counts and latency
- Expandable full content

### Findings Tab
- Vulnerability findings from all agents
- File location and severity
- Reasoning excerpts

## WebSocket Protocol

### Client → Server
No client messages required. Server pushes events.

### Server → Client Messages

```json
// State update (on connect)
{
  "type": "state",
  "data": {
    "current_scan_id": "scan-abc123",
    "active_agent": "InjectionSpecialist",
    "active_phase": "specialist-detection",
    "events_count": 42,
    "subscribers_count": 2
  }
}

// Historical events (on connect)
{
  "type": "history",
  "data": { /* AgentLogEvent */ }
}

// Live events
{
  "type": "event",
  "data": {
    "event_type": "agent_prompt",
    "agent_name": "InjectionSpecialist",
    "timestamp": "2024-01-15T10:30:00Z",
    "scan_id": "scan-abc123",
    "data": {
      "prompt_length": 2345,
      "prompt_tokens": 500,
      "prompt_preview": "..."
    }
  }
}

// Heartbeat (every 30s)
{
  "type": "heartbeat"
}
```

## REST API

### GET /api/state

Returns current server state.

```json
{
  "current_scan_id": "scan-abc123",
  "active_agent": "InjectionSpecialist",
  "active_phase": "specialist-detection",
  "events_count": 42,
  "subscribers_count": 2
}
```

### GET /api/history?limit=100

Returns recent event history.

```json
{
  "events": [ /* AgentLogEvent[] */ ],
  "count": 100
}
```

### POST /api/broadcast

Manually broadcast an event (for testing).

```json
// Request
{
  "event_type": "manual",
  "agent_name": "test",
  "scan_id": "test-scan",
  "data": { "message": "Hello" }
}

// Response
{
  "status": "ok",
  "event": { /* AgentLogEvent */ }
}
```

## Running Alongside Main Worker

The log server runs on a **different port** (5003) from the main worker (5002). To see agent events in the dashboard, the worker must send events to the log server.

### 1. Start the log server first

```bash
python -m backend.worker.core.start_log_server  # Runs on port 5003
```

### 2. Start the worker with `LOG_SERVER_URL` set

```bash
# Terminal 1: Log server
python -m backend.worker.core.start_log_server

# Terminal 2: Main worker — set LOG_SERVER_URL so it pushes events to the log server
cd backend/worker/core
set LOG_SERVER_URL=http://127.0.0.1:5003
python main.py  # Runs on port 5002
```

On Linux/macOS:

```bash
LOG_SERVER_URL=http://127.0.0.1:5003 python main.py
```

### 3. Open the dashboard

Open **http://localhost:5003/** in your browser. You should see agent_start, agent_prompt, agent_response, agent_findings, and phase_transition events in real time.

If `LOG_SERVER_URL` is not set, the worker still logs to files under `backend/worker/data/agent_logs/` but does not push to the dashboard.

## Environment Variables

### Log server (start_log_server.py)

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_SERVER_PORT` | 5003 | Port for log server |
| `LOG_SERVER_HOST` | 0.0.0.0 | Host to bind to |

### Worker (main.py) — required for live dashboard

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_SERVER_URL` | (empty) | Base URL of the log server, e.g. `http://127.0.0.1:5003`. When set, the worker POSTs each agent event to the log server so the dashboard shows live activity. |

## Performance Notes

- **Fire-and-forget**: Events are broadcast without waiting for acknowledgment
- **Queue-based**: Each WebSocket client has its own asyncio queue
- **History limit**: Last 1000 events kept in memory
- **Heartbeat**: 30-second timeout triggers heartbeat to detect dead connections

## Use Cases

1. **Development Debugging**: Watch what prompts are sent to LLMs
2. **Performance Analysis**: Track latency and token usage per agent
3. **Demonstration**: Show real-time security analysis to stakeholders
4. **Troubleshooting**: Identify which agent is slow or failing
5. **Learning**: Understand how multi-agent systems work