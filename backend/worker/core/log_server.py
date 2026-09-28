"""
Agent Log Server — Real-time WebSocket server for monitoring AI agent activities.

This is a separate server from main.py, dedicated to streaming agent logs in real-time.
Captures:
- Agent activities (what agent is running)
- Tool calls (what function was called)
- LLM requests (what prompt was sent to AI)
- LLM responses (what the AI responded)
- Agent findings (what vulnerabilities were found)

Run with: python -m backend.worker.core.log_server
Port: 5003 (configurable via LOG_SERVER_PORT env var)
"""

import asyncio
import json
import logging
import os
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from queue import Queue
from contextlib import asynccontextmanager

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class AgentLogEvent:
    """Represents a single log event from an agent."""
    event_type: str  # agent_start, agent_prompt, agent_response, agent_findings, tool_call, etc.
    agent_name: str
    timestamp: str
    scan_id: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "event_type": self.event_type,
            "agent_name": self.agent_name,
            "timestamp": self.timestamp,
            "scan_id": self.scan_id,
            "data": self.data,
        })


# =============================================================================
# Global Event Bus
# =============================================================================

class AgentLogBus:
    """
    Global event bus for broadcasting agent logs to all connected WebSocket clients.
    
    Thread-safe implementation using asyncio queues.
    """
    
    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()
        self._event_history: List[AgentLogEvent] = []
        self._max_history = 1000  # Keep last 1000 events for new connections
        self._current_scan_id: str = ""
        self._active_agent: str = ""
        self._active_phase: str = ""
    
    async def subscribe(self) -> asyncio.Queue:
        """Subscribe to event stream. Returns a queue that will receive events."""
        queue = asyncio.Queue()
        async with self._lock:
            self._subscribers.add(queue)
        return queue
    
    async def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from event stream."""
        async with self._lock:
            self._subscribers.discard(queue)
    
    async def broadcast(self, event: AgentLogEvent):
        """Broadcast event to all subscribers."""
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
        
        # Update state
        if event.event_type == "scan_start":
            self._current_scan_id = event.scan_id
        elif event.event_type == "phase_transition":
            self._active_phase = event.data.get("to_phase", "")
        elif event.event_type == "agent_start":
            self._active_agent = event.agent_name
        elif event.event_type == "agent_complete":
            self._active_agent = ""
        
        # Broadcast to all subscribers
        async with self._lock:
            dead_queues = set()
            for queue in self._subscribers:
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    dead_queues.add(queue)
            
            # Clean up dead queues
            for q in dead_queues:
                self._subscribers.discard(q)
    
    def get_history(self, limit: int = 100) -> List[AgentLogEvent]:
        """Get recent event history."""
        return self._event_history[-limit:]
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state (active scan, agent, phase)."""
        return {
            "current_scan_id": self._current_scan_id,
            "active_agent": self._active_agent,
            "active_phase": self._active_phase,
            "events_count": len(self._event_history),
            "subscribers_count": len(self._subscribers),
        }

    async def clear_history(self) -> None:
        """Clear buffered events and pipeline state (admin / UI reset)."""
        self._event_history.clear()
        self._current_scan_id = ""
        self._active_agent = ""
        self._active_phase = ""
        async with self._lock:
            for queue in self._subscribers:
                try:
                    queue.put_nowait("__clear__")
                except Exception:
                    pass


# Global instance
log_bus = AgentLogBus()


# =============================================================================
# Synchronous Interface for Non-Async Code
# =============================================================================

class LogServerInterface:
    """
    Synchronous interface for non-async code to broadcast events.
    
    This is what agent_logger.py uses to send events to the log server.
    """
    
    def __init__(self, bus: AgentLogBus):
        self._bus = bus
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._started = False
    
    def set_loop(self, loop: asyncio.AbstractEventLoop):
        """Set the event loop for async operations."""
        self._loop = loop
        self._started = True
    
    def broadcast_event(self, event: AgentLogEvent):
        """Broadcast event from synchronous code."""
        if not self._started or self._loop is None:
            return
        
        try:
            # Schedule the broadcast on the event loop
            future = asyncio.run_coroutine_threadsafe(
                self._bus.broadcast(event),
                self._loop
            )
            # Don't wait for completion - fire and forget for performance
        except Exception as e:
            logger.debug(f"Failed to broadcast event: {e}")
    
    def log_agent_start(self, agent_name: str, agent_type: str, scan_id: str = "", config: Dict = None):
        """Log agent start event."""
        self.broadcast_event(AgentLogEvent(
            event_type="agent_start",
            agent_name=agent_name,
            timestamp=datetime.utcnow().isoformat(),
            scan_id=scan_id,
            data={
                "agent_type": agent_type,
                "config": config or {},
            }
        ))
    
    def log_agent_prompt(self, agent_name: str, prompt: str, prompt_tokens: int = None, scan_id: str = ""):
        """Log LLM prompt sent."""
        self.broadcast_event(AgentLogEvent(
            event_type="agent_prompt",
            agent_name=agent_name,
            timestamp=datetime.utcnow().isoformat(),
            scan_id=scan_id,
            data={
                "prompt_length": len(prompt),
                "prompt_tokens": prompt_tokens,
                "prompt_preview": prompt[:500] + "..." if len(prompt) > 500 else prompt,
                "prompt_full": prompt,
            }
        ))
    
    def log_agent_response(self, agent_name: str, response: str, response_tokens: int = None, 
                          latency_ms: int = None, scan_id: str = ""):
        """Log LLM response received."""
        self.broadcast_event(AgentLogEvent(
            event_type="agent_response",
            agent_name=agent_name,
            timestamp=datetime.utcnow().isoformat(),
            scan_id=scan_id,
            data={
                "response_length": len(response),
                "response_tokens": response_tokens,
                "latency_ms": latency_ms,
                "response_preview": response[:500] + "..." if len(response) > 500 else response,
                "response_full": response,
            }
        ))
    
    def log_tool_call(self, agent_name: str, tool_name: str, tool_args: Dict, scan_id: str = ""):
        """Log a tool call made by the agent."""
        self.broadcast_event(AgentLogEvent(
            event_type="tool_call",
            agent_name=agent_name,
            timestamp=datetime.utcnow().isoformat(),
            scan_id=scan_id,
            data={
                "tool_name": tool_name,
                "tool_args": tool_args,
            }
        ))
    
    def log_tool_result(self, agent_name: str, tool_name: str, tool_result: Any, scan_id: str = ""):
        """Log the result from a tool call."""
        result_str = str(tool_result) if not isinstance(tool_result, str) else tool_result
        self.broadcast_event(AgentLogEvent(
            event_type="tool_result",
            agent_name=agent_name,
            timestamp=datetime.utcnow().isoformat(),
            scan_id=scan_id,
            data={
                "tool_name": tool_name,
                "result_preview": result_str[:500] + "..." if len(result_str) > 500 else result_str,
            }
        ))
    
    def log_agent_findings(self, agent_name: str, findings: List[Dict], scan_id: str = ""):
        """Log findings produced by agent."""
        self.broadcast_event(AgentLogEvent(
            event_type="agent_findings",
            agent_name=agent_name,
            timestamp=datetime.utcnow().isoformat(),
            scan_id=scan_id,
            data={
                "findings_count": len(findings),
                "findings": findings[:10],  # First 10 findings
                "all_findings": findings,
            }
        ))
    
    def log_agent_complete(self, agent_name: str, execution_time_ms: int, token_usage: int,
                          errors: List[str], findings_count: int, scan_id: str = ""):
        """Log agent completion."""
        self.broadcast_event(AgentLogEvent(
            event_type="agent_complete",
            agent_name=agent_name,
            timestamp=datetime.utcnow().isoformat(),
            scan_id=scan_id,
            data={
                "execution_time_ms": execution_time_ms,
                "token_usage": token_usage,
                "errors": errors,
                "findings_count": findings_count,
            }
        ))
    
    def log_phase_transition(self, from_phase: str, to_phase: str, data: Dict = None, scan_id: str = ""):
        """Log phase transition in pipeline."""
        self.broadcast_event(AgentLogEvent(
            event_type="phase_transition",
            agent_name="coordinator",
            timestamp=datetime.utcnow().isoformat(),
            scan_id=scan_id,
            data={
                "from_phase": from_phase,
                "to_phase": to_phase,
                "phase_data": data or {},
            }
        ))
    
    def log_error(self, agent_name: str, error_type: str, error_message: str, 
                 stack_trace: str = None, scan_id: str = ""):
        """Log an error."""
        self.broadcast_event(AgentLogEvent(
            event_type="error",
            agent_name=agent_name,
            timestamp=datetime.utcnow().isoformat(),
            scan_id=scan_id,
            data={
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace,
            }
        ))
    
    def log_scan_start(self, scan_id: str, language: str, framework: str, file_count: int):
        """Log scan start."""
        self.broadcast_event(AgentLogEvent(
            event_type="scan_start",
            agent_name="coordinator",
            timestamp=datetime.utcnow().isoformat(),
            scan_id=scan_id,
            data={
                "language": language,
                "framework": framework,
                "file_count": file_count,
            }
        ))
    
    def log_scan_complete(self, scan_id: str, total_findings: int, total_time_ms: int):
        """Log scan completion."""
        self.broadcast_event(AgentLogEvent(
            event_type="scan_complete",
            agent_name="coordinator",
            timestamp=datetime.utcnow().isoformat(),
            scan_id=scan_id,
            data={
                "total_findings": total_findings,
                "total_time_ms": total_time_ms,
            }
        ))


# Global interface instance
log_interface = LogServerInterface(log_bus)


# =============================================================================
# FastAPI Application
# =============================================================================

# Store the main event loop
main_loop: Optional[asyncio.AbstractEventLoop] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - set up event loop reference."""
    global main_loop
    main_loop = asyncio.get_running_loop()
    log_interface.set_loop(main_loop)
    logger.info("Log server started, event loop ready")
    yield
    logger.info("Log server shutting down")


app = FastAPI(
    title="SentinAI Agent Log Server",
    description="Real-time WebSocket server for monitoring AI agent activities",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# WebSocket Endpoint
# =============================================================================

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time log streaming."""
    await websocket.accept()
    logger.info(f"WebSocket client connected from {websocket.client.host if websocket.client else 'unknown'}")
    
    queue = await log_bus.subscribe()
    
    try:
        # Send current state first
        await websocket.send_json({
            "type": "state",
            "data": log_bus.get_state(),
        })
        
        # Send recent history
        for event in log_bus.get_history(limit=50):
            await websocket.send_json({
                "type": "history",
                "data": json.loads(event.to_json()),
            })
        
        # Stream new events
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                if event == "__clear__":
                    await websocket.send_json({"type": "cleared"})
                    continue
                await websocket.send_json({
                    "type": "event",
                    "data": json.loads(event.to_json()),
                })
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({"type": "heartbeat"})
    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await log_bus.unsubscribe(queue)


# =============================================================================
# REST Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint - returns dashboard HTML."""
    return HTMLResponse(content=DASHBOARD_HTML)


@app.get("/api/state")
async def get_state():
    """Get current server state."""
    return JSONResponse(content=log_bus.get_state())


@app.get("/api/history")
async def get_history(limit: int = 100):
    """Get event history."""
    events = log_bus.get_history(limit=limit)
    return JSONResponse(content={
        "events": [json.loads(e.to_json()) for e in events],
        "count": len(events),
    })


@app.post("/api/clear")
async def clear_logs():
    """Clear in-memory event history (live clients receive type: cleared)."""
    await log_bus.clear_history()
    return JSONResponse(content={"ok": True, "message": "Event history cleared"})


@app.post("/api/broadcast")
async def broadcast_event(event: Dict[str, Any]):
    """Receive events from worker (AgentLogger) and broadcast to WebSocket clients."""
    data = event.get("data", {})
    # Preserve worker timestamp so admin UI ordering and display are correct
    timestamp = data.get("timestamp") if isinstance(data.get("timestamp"), str) else datetime.utcnow().isoformat()
    log_event = AgentLogEvent(
        event_type=event.get("event_type", "manual"),
        agent_name=event.get("agent_name", ""),
        timestamp=timestamp,
        scan_id=event.get("scan_id", ""),
        data=data,
    )
    await log_bus.broadcast(log_event)
    return JSONResponse(content={"status": "ok", "event": json.loads(log_event.to_json())})


# =============================================================================
# Dashboard HTML
# =============================================================================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SentinAI Agent Log Server</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 20px;
            border-bottom: 1px solid #2a2a4a;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 1.5rem;
            color: #00d4ff;
        }
        
        .status {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4CAF50;
        }
        
        .status-dot.disconnected {
            background: #f44336;
        }
        
        .main {
            display: grid;
            grid-template-columns: 300px 1fr;
            height: calc(100vh - 70px);
        }
        
        .sidebar {
            background: #12121a;
            border-right: 1px solid #2a2a4a;
            overflow-y: auto;
        }
        
        .sidebar-header {
            padding: 15px;
            border-bottom: 1px solid #2a2a4a;
            font-weight: bold;
            color: #00d4ff;
        }
        
        .agent-item {
            padding: 12px 15px;
            border-bottom: 1px solid #1a1a2a;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .agent-item:hover {
            background: #1a1a2e;
        }
        
        .agent-item.active {
            background: #16213e;
            border-left: 3px solid #00d4ff;
        }
        
        .agent-name {
            font-weight: 500;
            margin-bottom: 4px;
        }
        
        .agent-type {
            font-size: 0.75rem;
            color: #888;
        }
        
        .content {
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .tabs {
            display: flex;
            background: #12121a;
            border-bottom: 1px solid #2a2a4a;
        }
        
        .tab {
            padding: 12px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }
        
        .tab:hover {
            background: #1a1a2e;
        }
        
        .tab.active {
            color: #00d4ff;
            border-bottom-color: #00d4ff;
        }
        
        .tab-content {
            flex: 1;
            overflow: hidden;
            display: none;
        }
        
        .tab-content.active {
            display: flex;
            flex-direction: column;
        }
        
        .log-container {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #0d0d14;
        }
        
        .log-entry {
            margin-bottom: 10px;
            padding: 12px;
            border-radius: 8px;
            background: #1a1a24;
            border-left: 4px solid #444;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .log-entry.agent_start { border-left-color: #2196F3; }
        .log-entry.agent_prompt { border-left-color: #9C27B0; }
        .log-entry.agent_response { border-left-color: #4CAF50; }
        .log-entry.agent_findings { border-left-color: #f44336; }
        .log-entry.agent_complete { border-left-color: #00d4ff; }
        .log-entry.tool_call { border-left-color: #FF9800; }
        .log-entry.tool_result { border-left-color: #FFC107; }
        .log-entry.phase_transition { border-left-color: #00BCD4; }
        .log-entry.error { border-left-color: #f44336; background: #2a1a1a; }
        
        .log-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .log-type {
            font-weight: bold;
            color: #00d4ff;
            font-size: 0.85rem;
        }
        
        .log-time {
            color: #888;
            font-size: 0.75rem;
        }
        
        .log-agent {
            color: #4CAF50;
            font-size: 0.8rem;
            margin-bottom: 8px;
        }
        
        .log-data {
            background: #0a0a10;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.8rem;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-word;
        }
        
        .log-data.collapsed {
            max-height: 100px;
            overflow: hidden;
        }
        
        .expand-btn {
            margin-top: 5px;
            padding: 4px 8px;
            font-size: 0.7rem;
            background: #2a2a4a;
            border: none;
            color: #888;
            cursor: pointer;
            border-radius: 4px;
        }
        
        .expand-btn:hover {
            background: #3a3a5a;
            color: #00d4ff;
        }
        
        .state-panel {
            background: #12121a;
            padding: 15px;
            border-bottom: 1px solid #2a2a4a;
        }
        
        .state-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
        }
        
        .state-label {
            color: #888;
        }
        
        .state-value {
            color: #00d4ff;
            font-family: monospace;
        }
        
        .filter-bar {
            padding: 10px 15px;
            background: #12121a;
            border-bottom: 1px solid #2a2a4a;
        }
        
        .filter-input {
            width: 100%;
            padding: 8px 12px;
            background: #1a1a2e;
            border: 1px solid #2a2a4a;
            border-radius: 4px;
            color: #e0e0e0;
            font-size: 0.9rem;
        }
        
        .filter-input:focus {
            outline: none;
            border-color: #00d4ff;
        }
        
        .clear-btn {
            padding: 8px 16px;
            background: #2a2a4a;
            border: none;
            color: #e0e0e0;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
        }
        
        .clear-btn:hover {
            background: #3a3a5a;
        }
        
        .prompt-viewer {
            background: #0a0a10;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }
        
        .prompt-viewer pre {
            white-space: pre-wrap;
            word-break: break-word;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85rem;
            line-height: 1.5;
        }
        
        .highlight {
            background: #1a1a24;
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        .keyword { color: #ff79c6; }
        .string { color: #f1fa8c; }
        .number { color: #bd93f9; }
        .comment { color: #6272a4; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🔍 SentinAI Agent Log Server</h1>
        </div>
        <div class="status">
            <div class="status-item">
                <div class="status-dot" id="connection-dot"></div>
                <span id="connection-text">Connecting...</span>
            </div>
            <div class="status-item">
                <span>Scan:</span>
                <span id="current-scan" class="state-value">-</span>
            </div>
            <div class="status-item">
                <span>Agent:</span>
                <span id="current-agent" class="state-value">-</span>
            </div>
            <div class="status-item">
                <span>Phase:</span>
                <span id="current-phase" class="state-value">-</span>
            </div>
        </div>
    </div>
    
    <div class="main">
        <div class="sidebar">
            <div class="sidebar-header">📋 Event Types</div>
            <div id="event-types">
                <div class="agent-item" data-type="all">
                    <div class="agent-name">All Events</div>
                </div>
                <div class="agent-item" data-type="agent_start">
                    <div class="agent-name">🚀 Agent Start</div>
                    <div class="agent-type">Agent initialization</div>
                </div>
                <div class="agent-item" data-type="agent_prompt">
                    <div class="agent-name">📤 Prompt Sent</div>
                    <div class="agent-type">LLM request</div>
                </div>
                <div class="agent-item" data-type="agent_response">
                    <div class="agent-name">📥 Response Received</div>
                    <div class="agent-type">LLM response</div>
                </div>
                <div class="agent-item" data-type="tool_call">
                    <div class="agent-name">🔧 Tool Call</div>
                    <div class="agent-type">Function invocation</div>
                </div>
                <div class="agent-item" data-type="tool_result">
                    <div class="agent-name">📥 Tool Result</div>
                    <div class="agent-type">Function return</div>
                </div>
                <div class="agent-item" data-type="agent_findings">
                    <div class="agent-name">🔍 Findings</div>
                    <div class="agent-type">Vulnerabilities found</div>
                </div>
                <div class="agent-item" data-type="agent_complete">
                    <div class="agent-name">✅ Agent Complete</div>
                    <div class="agent-type">Agent finished</div>
                </div>
                <div class="agent-item" data-type="phase_transition">
                    <div class="agent-name">🔄 Phase Transition</div>
                    <div class="agent-type">Pipeline stage</div>
                </div>
                <div class="agent-item" data-type="error">
                    <div class="agent-name">❌ Errors</div>
                    <div class="agent-type">Error events</div>
                </div>
            </div>
        </div>
        
        <div class="content">
            <div class="tabs">
                <div class="tab active" data-tab="stream">📡 Live Stream</div>
                <div class="tab" data-tab="prompts">💬 Prompts</div>
                <div class="tab" data-tab="findings">🔍 Findings</div>
            </div>
            
            <div class="filter-bar">
                <input type="text" class="filter-input" id="filter-input" placeholder="Filter events...">
                <button class="clear-btn" onclick="clearLogs()">Clear</button>
            </div>
            
            <div class="tab-content active" id="stream-tab">
                <div class="log-container" id="log-container"></div>
            </div>
            
            <div class="tab-content" id="prompts-tab">
                <div class="log-container" id="prompts-container"></div>
            </div>
            
            <div class="tab-content" id="findings-tab">
                <div class="log-container" id="findings-container"></div>
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let logs = [];
        let prompts = [];
        let findings = [];
        let filterType = 'all';
        let filterText = '';
        let reconnectTimeout = null;
        
        function connect() {
            const wsUrl = `ws://${window.location.host}/ws/logs`;
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                document.getElementById('connection-dot').classList.remove('disconnected');
                document.getElementById('connection-text').textContent = 'Connected';
            };
            
            ws.onclose = () => {
                document.getElementById('connection-dot').classList.add('disconnected');
                document.getElementById('connection-text').textContent = 'Disconnected';
                // Reconnect after 3 seconds
                if (reconnectTimeout) clearTimeout(reconnectTimeout);
                reconnectTimeout = setTimeout(connect, 3000);
            };
            
            ws.onerror = (err) => {
                console.error('WebSocket error:', err);
            };
            
            ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                
                if (msg.type === 'state') {
                    updateState(msg.data);
                } else if (msg.type === 'history') {
                    addLog(msg.data, false);
                } else if (msg.type === 'event') {
                    addLog(msg.data, true);
                }
            };
        }
        
        function updateState(state) {
            document.getElementById('current-scan').textContent = state.current_scan_id || '-';
            document.getElementById('current-agent').textContent = state.active_agent || '-';
            document.getElementById('current-phase').textContent = state.active_phase || '-';
        }
        
        function addLog(event, animate = true) {
            logs.push(event);
            if (logs.length > 500) logs.shift();
            
            // Store prompts and findings separately
            if (event.event_type === 'agent_prompt' || event.event_type === 'agent_response') {
                prompts.push(event);
                if (prompts.length > 200) prompts.shift();
                renderPrompts();
            }
            
            if (event.event_type === 'agent_findings') {
                findings.push(event);
                if (findings.length > 200) findings.shift();
                renderFindings();
            }
            
            renderLogs(animate);
        }
        
        function renderLogs(animate = true) {
            const container = document.getElementById('log-container');
            const filtered = logs.filter(log => {
                if (filterType !== 'all' && log.event_type !== filterType) return false;
                if (filterText && !JSON.stringify(log).toLowerCase().includes(filterText.toLowerCase())) return false;
                return true;
            });
            
            container.innerHTML = filtered.slice(-100).map(log => formatLogEntry(log)).join('');
            
            if (animate) {
                container.scrollTop = container.scrollHeight;
            }
        }
        
        function renderPrompts() {
            const container = document.getElementById('prompts-container');
            const filtered = prompts.filter(log => {
                if (filterText && !JSON.stringify(log).toLowerCase().includes(filterText.toLowerCase())) return false;
                return true;
            });
            
            container.innerHTML = filtered.slice(-50).map(log => formatPromptEntry(log)).join('');
            container.scrollTop = container.scrollHeight;
        }
        
        function renderFindings() {
            const container = document.getElementById('findings-container');
            const filtered = findings.filter(log => {
                if (filterText && !JSON.stringify(log).toLowerCase().includes(filterText.toLowerCase())) return false;
                return true;
            });
            
            container.innerHTML = filtered.slice(-50).map(log => formatFindingsEntry(log)).join('');
            container.scrollTop = container.scrollHeight;
        }
        
        function formatLogEntry(event) {
            const time = new Date(event.timestamp).toLocaleTimeString();
            const data = event.data || {};
            
            let dataDisplay = '';
            if (event.event_type === 'agent_prompt') {
                dataDisplay = `<div class="prompt-viewer"><pre>${escapeHtml(data.prompt_preview || data.prompt_full || '')}</pre></div>`;
            } else if (event.event_type === 'agent_response') {
                dataDisplay = `<div class="prompt-viewer"><pre>${escapeHtml(data.response_preview || '')}</pre></div>`;
            } else {
                dataDisplay = `<div class="log-data">${escapeHtml(JSON.stringify(data, null, 2))}</div>`;
            }
            
            return `
                <div class="log-entry ${event.event_type}">
                    <div class="log-header">
                        <span class="log-type">${formatEventType(event.event_type)}</span>
                        <span class="log-time">${time}</span>
                    </div>
                    <div class="log-agent">${event.agent_name} ${event.scan_id ? `(${event.scan_id.slice(0, 8)}...)` : ''}</div>
                    ${dataDisplay}
                </div>
            `;
        }
        
        function formatPromptEntry(event) {
            const time = new Date(event.timestamp).toLocaleTimeString();
            const isPrompt = event.event_type === 'agent_prompt';
            const data = event.data || {};
            
            return `
                <div class="log-entry ${event.event_type}">
                    <div class="log-header">
                        <span class="log-type">${isPrompt ? '📤 Prompt' : '📥 Response'}</span>
                        <span class="log-time">${time}</span>
                        <span class="log-agent">${event.agent_name}</span>
                    </div>
                    <div class="prompt-viewer">
                        <pre>${escapeHtml(isPrompt ? (data.prompt_preview || '') : (data.response_preview || ''))}</pre>
                    </div>
                    ${isPrompt && data.prompt_tokens ? `<div>Tokens: ${data.prompt_tokens}</div>` : ''}
                    ${!isPrompt && data.latency_ms ? `<div>Latency: ${data.latency_ms}ms</div>` : ''}
                </div>
            `;
        }
        
        function formatFindingsEntry(event) {
            const time = new Date(event.timestamp).toLocaleTimeString();
            const data = event.data || {};
            const findings = data.all_findings || [];
            
            const findingsHtml = findings.slice(0, 5).map(f => `
                <div style="margin: 8px 0; padding: 8px; background: #1a1a24; border-radius: 4px;">
                    <strong>${f.vulnerability_class || 'Unknown'}</strong> in ${f.file_path || 'unknown'}:${f.line_start || 0}
                    <br><small>${f.reasoning ? f.reasoning.slice(0, 100) + '...' : ''}</small>
                </div>
            `).join('');
            
            return `
                <div class="log-entry agent_findings">
                    <div class="log-header">
                        <span class="log-type">🔍 ${findings.length} Finding(s)</span>
                        <span class="log-time">${time}</span>
                    </div>
                    <div class="log-agent">${event.agent_name}</div>
                    ${findingsHtml}
                    ${findings.length > 5 ? `<div style="color: #888;">...and ${findings.length - 5} more</div>` : ''}
                </div>
            `;
        }
        
        function formatEventType(type) {
            const icons = {
                'agent_start': '🚀 Agent Start',
                'agent_prompt': '📤 Prompt Sent',
                'agent_response': '📥 Response',
                'agent_findings': '🔍 Findings',
                'agent_complete': '✅ Complete',
                'tool_call': '🔧 Tool Call',
                'tool_result': '📥 Tool Result',
                'phase_transition': '🔄 Phase',
                'error': '❌ Error',
                'scan_start': '🎯 Scan Start',
                'scan_complete': '🏁 Scan Complete',
            };
            return icons[type] || type;
        }
        
        function escapeHtml(text) {
            if (!text) return '';
            return text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }
        
        function clearLogs() {
            logs = [];
            prompts = [];
            findings = [];
            document.getElementById('log-container').innerHTML = '';
            document.getElementById('prompts-container').innerHTML = '';
            document.getElementById('findings-container').innerHTML = '';
        }
        
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById(`${tab.dataset.tab}-tab`).classList.add('active');
            });
        });
        
        // Event type filtering
        document.querySelectorAll('.agent-item').forEach(item => {
            item.addEventListener('click', () => {
                document.querySelectorAll('.agent-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                filterType = item.dataset.type;
                renderLogs(false);
            });
        });
        
        // Text filtering
        document.getElementById('filter-input').addEventListener('input', (e) => {
            filterText = e.target.value;
            renderLogs(false);
            renderPrompts();
            renderFindings();
        });
        
        // Connect on load
        connect();
    </script>
</body>
</html>
"""


# =============================================================================
# Main Entry Point
# =============================================================================

def run_server(port: int = None, host: str = "0.0.0.0"):
    """Run the log server."""
    port = port or int(os.getenv("LOG_SERVER_PORT", "5003"))
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           SentinAI Agent Log Server                         ║
╠══════════════════════════════════════════════════════════════╣
║  Dashboard:  http://{host}:{port}/                              ║
║  WebSocket:  ws://{host}:{port}/ws/logs                        ║
║  REST API:   http://{host}:{port}/api/state                     ║
║              http://{host}:{port}/api/history                   ║
║              http://{host}:{port}/api/clear (POST)              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_server()