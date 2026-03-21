import asyncio 
import json 
import logging 
import os 
import sys 
import threading 
import time 
from dataclasses import asdict ,dataclass ,field 
from datetime import datetime 
from typing import Any ,Dict ,List ,Optional ,Set 
from queue import Queue 
from contextlib import asynccontextmanager 
sys .path .insert (0 ,os .path .dirname (os .path .dirname (os .path .dirname (os .path .dirname (__file__ )))))
from fastapi import FastAPI ,WebSocket ,WebSocketDisconnect 
from fastapi .responses import HTMLResponse ,JSONResponse 
from fastapi .middleware .cors import CORSMiddleware 
import uvicorn 
logger =logging .getLogger (__name__ )

@dataclass 
class AgentLogEvent :
    event_type :str 
    agent_name :str 
    timestamp :str 
    scan_id :str =''
    data :Dict [str ,Any ]=field (default_factory =dict )

    def to_json (self )->str :
        return json .dumps ({'event_type':self .event_type ,'agent_name':self .agent_name ,'timestamp':self .timestamp ,'scan_id':self .scan_id ,'data':self .data })

class AgentLogBus :

    def __init__ (self ):
        self ._subscribers :Set [asyncio .Queue ]=set ()
        self ._lock =asyncio .Lock ()
        self ._event_history :List [AgentLogEvent ]=[]
        self ._max_history =1000 
        self ._current_scan_id :str =''
        self ._active_agent :str =''
        self ._active_phase :str =''

    async def subscribe (self )->asyncio .Queue :
        queue =asyncio .Queue ()
        async with self ._lock :
            self ._subscribers .add (queue )
        return queue 

    async def unsubscribe (self ,queue :asyncio .Queue ):
        async with self ._lock :
            self ._subscribers .discard (queue )

    async def broadcast (self ,event :AgentLogEvent ):
        self ._event_history .append (event )
        if len (self ._event_history )>self ._max_history :
            self ._event_history =self ._event_history [-self ._max_history :]
        if event .event_type =='scan_start':
            self ._current_scan_id =event .scan_id 
        elif event .event_type =='phase_transition':
            self ._active_phase =event .data .get ('to_phase','')
        elif event .event_type =='agent_start':
            self ._active_agent =event .agent_name 
        elif event .event_type =='agent_complete':
            self ._active_agent =''
        async with self ._lock :
            dead_queues =set ()
            for queue in self ._subscribers :
                try :
                    queue .put_nowait (event )
                except asyncio .QueueFull :
                    dead_queues .add (queue )
            for q in dead_queues :
                self ._subscribers .discard (q )

    def get_history (self ,limit :int =100 )->List [AgentLogEvent ]:
        return self ._event_history [-limit :]

    def get_state (self )->Dict [str ,Any ]:
        return {'current_scan_id':self ._current_scan_id ,'active_agent':self ._active_agent ,'active_phase':self ._active_phase ,'events_count':len (self ._event_history ),'subscribers_count':len (self ._subscribers )}

    async def clear_history (self )->None :
        self ._event_history .clear ()
        self ._current_scan_id =''
        self ._active_agent =''
        self ._active_phase =''
        async with self ._lock :
            for queue in self ._subscribers :
                try :
                    queue .put_nowait ('__clear__')
                except Exception :
                    pass 
log_bus =AgentLogBus ()

class LogServerInterface :

    def __init__ (self ,bus :AgentLogBus ):
        self ._bus =bus 
        self ._loop :Optional [asyncio .AbstractEventLoop ]=None 
        self ._started =False 

    def set_loop (self ,loop :asyncio .AbstractEventLoop ):
        self ._loop =loop 
        self ._started =True 

    def broadcast_event (self ,event :AgentLogEvent ):
        if not self ._started or self ._loop is None :
            return 
        try :
            future =asyncio .run_coroutine_threadsafe (self ._bus .broadcast (event ),self ._loop )
        except Exception as e :
            logger .debug (f'Failed to broadcast event: {e }')

    def log_agent_start (self ,agent_name :str ,agent_type :str ,scan_id :str ='',config :Dict =None ):
        self .broadcast_event (AgentLogEvent (event_type ='agent_start',agent_name =agent_name ,timestamp =datetime .utcnow ().isoformat (),scan_id =scan_id ,data ={'agent_type':agent_type ,'config':config or {}}))

    def log_agent_prompt (self ,agent_name :str ,prompt :str ,prompt_tokens :int =None ,scan_id :str =''):
        self .broadcast_event (AgentLogEvent (event_type ='agent_prompt',agent_name =agent_name ,timestamp =datetime .utcnow ().isoformat (),scan_id =scan_id ,data ={'prompt_length':len (prompt ),'prompt_tokens':prompt_tokens ,'prompt_preview':prompt [:500 ]+'...'if len (prompt )>500 else prompt ,'prompt_full':prompt }))

    def log_agent_response (self ,agent_name :str ,response :str ,response_tokens :int =None ,latency_ms :int =None ,scan_id :str =''):
        self .broadcast_event (AgentLogEvent (event_type ='agent_response',agent_name =agent_name ,timestamp =datetime .utcnow ().isoformat (),scan_id =scan_id ,data ={'response_length':len (response ),'response_tokens':response_tokens ,'latency_ms':latency_ms ,'response_preview':response [:500 ]+'...'if len (response )>500 else response ,'response_full':response }))

    def log_tool_call (self ,agent_name :str ,tool_name :str ,tool_args :Dict ,scan_id :str =''):
        self .broadcast_event (AgentLogEvent (event_type ='tool_call',agent_name =agent_name ,timestamp =datetime .utcnow ().isoformat (),scan_id =scan_id ,data ={'tool_name':tool_name ,'tool_args':tool_args }))

    def log_tool_result (self ,agent_name :str ,tool_name :str ,tool_result :Any ,scan_id :str =''):
        result_str =str (tool_result )if not isinstance (tool_result ,str )else tool_result 
        self .broadcast_event (AgentLogEvent (event_type ='tool_result',agent_name =agent_name ,timestamp =datetime .utcnow ().isoformat (),scan_id =scan_id ,data ={'tool_name':tool_name ,'result_preview':result_str [:500 ]+'...'if len (result_str )>500 else result_str }))

    def log_agent_findings (self ,agent_name :str ,findings :List [Dict ],scan_id :str =''):
        self .broadcast_event (AgentLogEvent (event_type ='agent_findings',agent_name =agent_name ,timestamp =datetime .utcnow ().isoformat (),scan_id =scan_id ,data ={'findings_count':len (findings ),'findings':findings [:10 ],'all_findings':findings }))

    def log_agent_complete (self ,agent_name :str ,execution_time_ms :int ,token_usage :int ,errors :List [str ],findings_count :int ,scan_id :str =''):
        self .broadcast_event (AgentLogEvent (event_type ='agent_complete',agent_name =agent_name ,timestamp =datetime .utcnow ().isoformat (),scan_id =scan_id ,data ={'execution_time_ms':execution_time_ms ,'token_usage':token_usage ,'errors':errors ,'findings_count':findings_count }))

    def log_phase_transition (self ,from_phase :str ,to_phase :str ,data :Dict =None ,scan_id :str =''):
        self .broadcast_event (AgentLogEvent (event_type ='phase_transition',agent_name ='coordinator',timestamp =datetime .utcnow ().isoformat (),scan_id =scan_id ,data ={'from_phase':from_phase ,'to_phase':to_phase ,'phase_data':data or {}}))

    def log_error (self ,agent_name :str ,error_type :str ,error_message :str ,stack_trace :str =None ,scan_id :str =''):
        self .broadcast_event (AgentLogEvent (event_type ='error',agent_name =agent_name ,timestamp =datetime .utcnow ().isoformat (),scan_id =scan_id ,data ={'error_type':error_type ,'error_message':error_message ,'stack_trace':stack_trace }))

    def log_scan_start (self ,scan_id :str ,language :str ,framework :str ,file_count :int ):
        self .broadcast_event (AgentLogEvent (event_type ='scan_start',agent_name ='coordinator',timestamp =datetime .utcnow ().isoformat (),scan_id =scan_id ,data ={'language':language ,'framework':framework ,'file_count':file_count }))

    def log_scan_complete (self ,scan_id :str ,total_findings :int ,total_time_ms :int ):
        self .broadcast_event (AgentLogEvent (event_type ='scan_complete',agent_name ='coordinator',timestamp =datetime .utcnow ().isoformat (),scan_id =scan_id ,data ={'total_findings':total_findings ,'total_time_ms':total_time_ms }))
log_interface =LogServerInterface (log_bus )
main_loop :Optional [asyncio .AbstractEventLoop ]=None 

@asynccontextmanager 
async def lifespan (app :FastAPI ):
    global main_loop 
    main_loop =asyncio .get_running_loop ()
    log_interface .set_loop (main_loop )
    logger .info ('Log server started, event loop ready')
    yield 
    logger .info ('Log server shutting down')
app =FastAPI (title ='SentinAI Agent Log Server',description ='Real-time WebSocket server for monitoring AI agent activities',version ='1.0.0',lifespan =lifespan )
app .add_middleware (CORSMiddleware ,allow_origins =['*'],allow_credentials =True ,allow_methods =['*'],allow_headers =['*'])

@app .websocket ('/ws/logs')
async def websocket_logs (websocket :WebSocket ):
    await websocket .accept ()
    logger .info (f"WebSocket client connected from {(websocket .client .host if websocket .client else 'unknown')}")
    queue =await log_bus .subscribe ()
    try :
        await websocket .send_json ({'type':'state','data':log_bus .get_state ()})
        for event in log_bus .get_history (limit =50 ):
            await websocket .send_json ({'type':'history','data':json .loads (event .to_json ())})
        while True :
            try :
                event =await asyncio .wait_for (queue .get (),timeout =30.0 )
                if event =='__clear__':
                    await websocket .send_json ({'type':'cleared'})
                    continue 
                await websocket .send_json ({'type':'event','data':json .loads (event .to_json ())})
            except asyncio .TimeoutError :
                await websocket .send_json ({'type':'heartbeat'})
    except WebSocketDisconnect :
        logger .info ('WebSocket client disconnected')
    except Exception as e :
        logger .error (f'WebSocket error: {e }')
    finally :
        await log_bus .unsubscribe (queue )

@app .get ('/')
async def root ():
    return HTMLResponse (content =DASHBOARD_HTML )

@app .get ('/api/state')
async def get_state ():
    return JSONResponse (content =log_bus .get_state ())

@app .get ('/api/history')
async def get_history (limit :int =100 ):
    events =log_bus .get_history (limit =limit )
    return JSONResponse (content ={'events':[json .loads (e .to_json ())for e in events ],'count':len (events )})

@app .post ('/api/clear')
async def clear_logs ():
    await log_bus .clear_history ()
    return JSONResponse (content ={'ok':True ,'message':'Event history cleared'})

@app .post ('/api/broadcast')
async def broadcast_event (event :Dict [str ,Any ]):
    data =event .get ('data',{})
    timestamp =data .get ('timestamp')if isinstance (data .get ('timestamp'),str )else datetime .utcnow ().isoformat ()
    log_event =AgentLogEvent (event_type =event .get ('event_type','manual'),agent_name =event .get ('agent_name',''),timestamp =timestamp ,scan_id =event .get ('scan_id',''),data =data )
    await log_bus .broadcast (log_event )
    return JSONResponse (content ={'status':'ok','event':json .loads (log_event .to_json ())})
DASHBOARD_HTML ='\n<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>SentinAI Agent Log Server</title>\n    <style>\n        * {\n            box-sizing: border-box;\n            margin: 0;\n            padding: 0;\n        }\n        \n        body {\n            font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;\n            background: #0a0a0a;\n            color: #e0e0e0;\n            min-height: 100vh;\n        }\n        \n        .header {\n            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);\n            padding: 20px;\n            border-bottom: 1px solid #2a2a4a;\n            display: flex;\n            justify-content: space-between;\n            align-items: center;\n        }\n        \n        .header h1 {\n            font-size: 1.5rem;\n            color: #00d4ff;\n        }\n        \n        .status {\n            display: flex;\n            gap: 20px;\n            align-items: center;\n        }\n        \n        .status-item {\n            display: flex;\n            align-items: center;\n            gap: 8px;\n            font-size: 0.9rem;\n        }\n        \n        .status-dot {\n            width: 10px;\n            height: 10px;\n            border-radius: 50%;\n            background: #4CAF50;\n        }\n        \n        .status-dot.disconnected {\n            background: #f44336;\n        }\n        \n        .main {\n            display: grid;\n            grid-template-columns: 300px 1fr;\n            height: calc(100vh - 70px);\n        }\n        \n        .sidebar {\n            background: #12121a;\n            border-right: 1px solid #2a2a4a;\n            overflow-y: auto;\n        }\n        \n        .sidebar-header {\n            padding: 15px;\n            border-bottom: 1px solid #2a2a4a;\n            font-weight: bold;\n            color: #00d4ff;\n        }\n        \n        .agent-item {\n            padding: 12px 15px;\n            border-bottom: 1px solid #1a1a2a;\n            cursor: pointer;\n            transition: background 0.2s;\n        }\n        \n        .agent-item:hover {\n            background: #1a1a2e;\n        }\n        \n        .agent-item.active {\n            background: #16213e;\n            border-left: 3px solid #00d4ff;\n        }\n        \n        .agent-name {\n            font-weight: 500;\n            margin-bottom: 4px;\n        }\n        \n        .agent-type {\n            font-size: 0.75rem;\n            color: #888;\n        }\n        \n        .content {\n            display: flex;\n            flex-direction: column;\n            overflow: hidden;\n        }\n        \n        .tabs {\n            display: flex;\n            background: #12121a;\n            border-bottom: 1px solid #2a2a4a;\n        }\n        \n        .tab {\n            padding: 12px 20px;\n            cursor: pointer;\n            border-bottom: 2px solid transparent;\n            transition: all 0.2s;\n        }\n        \n        .tab:hover {\n            background: #1a1a2e;\n        }\n        \n        .tab.active {\n            color: #00d4ff;\n            border-bottom-color: #00d4ff;\n        }\n        \n        .tab-content {\n            flex: 1;\n            overflow: hidden;\n            display: none;\n        }\n        \n        .tab-content.active {\n            display: flex;\n            flex-direction: column;\n        }\n        \n        .log-container {\n            flex: 1;\n            overflow-y: auto;\n            padding: 15px;\n            background: #0d0d14;\n        }\n        \n        .log-entry {\n            margin-bottom: 10px;\n            padding: 12px;\n            border-radius: 8px;\n            background: #1a1a24;\n            border-left: 4px solid #444;\n            animation: fadeIn 0.3s ease;\n        }\n        \n        @keyframes fadeIn {\n            from { opacity: 0; transform: translateY(-10px); }\n            to { opacity: 1; transform: translateY(0); }\n        }\n        \n        .log-entry.agent_start { border-left-color: #2196F3; }\n        .log-entry.agent_prompt { border-left-color: #9C27B0; }\n        .log-entry.agent_response { border-left-color: #4CAF50; }\n        .log-entry.agent_findings { border-left-color: #f44336; }\n        .log-entry.agent_complete { border-left-color: #00d4ff; }\n        .log-entry.tool_call { border-left-color: #FF9800; }\n        .log-entry.tool_result { border-left-color: #FFC107; }\n        .log-entry.phase_transition { border-left-color: #00BCD4; }\n        .log-entry.error { border-left-color: #f44336; background: #2a1a1a; }\n        \n        .log-header {\n            display: flex;\n            justify-content: space-between;\n            margin-bottom: 8px;\n        }\n        \n        .log-type {\n            font-weight: bold;\n            color: #00d4ff;\n            font-size: 0.85rem;\n        }\n        \n        .log-time {\n            color: #888;\n            font-size: 0.75rem;\n        }\n        \n        .log-agent {\n            color: #4CAF50;\n            font-size: 0.8rem;\n            margin-bottom: 8px;\n        }\n        \n        .log-data {\n            background: #0a0a10;\n            padding: 10px;\n            border-radius: 4px;\n            font-family: \'Consolas\', \'Monaco\', monospace;\n            font-size: 0.8rem;\n            overflow-x: auto;\n            white-space: pre-wrap;\n            word-break: break-word;\n        }\n        \n        .log-data.collapsed {\n            max-height: 100px;\n            overflow: hidden;\n        }\n        \n        .expand-btn {\n            margin-top: 5px;\n            padding: 4px 8px;\n            font-size: 0.7rem;\n            background: #2a2a4a;\n            border: none;\n            color: #888;\n            cursor: pointer;\n            border-radius: 4px;\n        }\n        \n        .expand-btn:hover {\n            background: #3a3a5a;\n            color: #00d4ff;\n        }\n        \n        .state-panel {\n            background: #12121a;\n            padding: 15px;\n            border-bottom: 1px solid #2a2a4a;\n        }\n        \n        .state-row {\n            display: flex;\n            justify-content: space-between;\n            padding: 5px 0;\n        }\n        \n        .state-label {\n            color: #888;\n        }\n        \n        .state-value {\n            color: #00d4ff;\n            font-family: monospace;\n        }\n        \n        .filter-bar {\n            padding: 10px 15px;\n            background: #12121a;\n            border-bottom: 1px solid #2a2a4a;\n        }\n        \n        .filter-input {\n            width: 100%;\n            padding: 8px 12px;\n            background: #1a1a2e;\n            border: 1px solid #2a2a4a;\n            border-radius: 4px;\n            color: #e0e0e0;\n            font-size: 0.9rem;\n        }\n        \n        .filter-input:focus {\n            outline: none;\n            border-color: #00d4ff;\n        }\n        \n        .clear-btn {\n            padding: 8px 16px;\n            background: #2a2a4a;\n            border: none;\n            color: #e0e0e0;\n            border-radius: 4px;\n            cursor: pointer;\n            margin-left: 10px;\n        }\n        \n        .clear-btn:hover {\n            background: #3a3a5a;\n        }\n        \n        .prompt-viewer {\n            background: #0a0a10;\n            padding: 15px;\n            border-radius: 8px;\n            margin-top: 10px;\n        }\n        \n        .prompt-viewer pre {\n            white-space: pre-wrap;\n            word-break: break-word;\n            font-family: \'Consolas\', \'Monaco\', monospace;\n            font-size: 0.85rem;\n            line-height: 1.5;\n        }\n        \n        .highlight {\n            background: #1a1a24;\n            padding: 2px 4px;\n            border-radius: 3px;\n        }\n        \n        .keyword { color: #ff79c6; }\n        .string { color: #f1fa8c; }\n        .number { color: #bd93f9; }\n        .comment { color: #6272a4; }\n    </style>\n</head>\n<body>\n    <div class="header">\n        <div>\n            <h1>🔍 SentinAI Agent Log Server</h1>\n        </div>\n        <div class="status">\n            <div class="status-item">\n                <div class="status-dot" id="connection-dot"></div>\n                <span id="connection-text">Connecting...</span>\n            </div>\n            <div class="status-item">\n                <span>Scan:</span>\n                <span id="current-scan" class="state-value">-</span>\n            </div>\n            <div class="status-item">\n                <span>Agent:</span>\n                <span id="current-agent" class="state-value">-</span>\n            </div>\n            <div class="status-item">\n                <span>Phase:</span>\n                <span id="current-phase" class="state-value">-</span>\n            </div>\n        </div>\n    </div>\n    \n    <div class="main">\n        <div class="sidebar">\n            <div class="sidebar-header">📋 Event Types</div>\n            <div id="event-types">\n                <div class="agent-item" data-type="all">\n                    <div class="agent-name">All Events</div>\n                </div>\n                <div class="agent-item" data-type="agent_start">\n                    <div class="agent-name">🚀 Agent Start</div>\n                    <div class="agent-type">Agent initialization</div>\n                </div>\n                <div class="agent-item" data-type="agent_prompt">\n                    <div class="agent-name">📤 Prompt Sent</div>\n                    <div class="agent-type">LLM request</div>\n                </div>\n                <div class="agent-item" data-type="agent_response">\n                    <div class="agent-name">📥 Response Received</div>\n                    <div class="agent-type">LLM response</div>\n                </div>\n                <div class="agent-item" data-type="tool_call">\n                    <div class="agent-name">🔧 Tool Call</div>\n                    <div class="agent-type">Function invocation</div>\n                </div>\n                <div class="agent-item" data-type="tool_result">\n                    <div class="agent-name">📥 Tool Result</div>\n                    <div class="agent-type">Function return</div>\n                </div>\n                <div class="agent-item" data-type="agent_findings">\n                    <div class="agent-name">🔍 Findings</div>\n                    <div class="agent-type">Vulnerabilities found</div>\n                </div>\n                <div class="agent-item" data-type="agent_complete">\n                    <div class="agent-name">✅ Agent Complete</div>\n                    <div class="agent-type">Agent finished</div>\n                </div>\n                <div class="agent-item" data-type="phase_transition">\n                    <div class="agent-name">🔄 Phase Transition</div>\n                    <div class="agent-type">Pipeline stage</div>\n                </div>\n                <div class="agent-item" data-type="error">\n                    <div class="agent-name">❌ Errors</div>\n                    <div class="agent-type">Error events</div>\n                </div>\n            </div>\n        </div>\n        \n        <div class="content">\n            <div class="tabs">\n                <div class="tab active" data-tab="stream">📡 Live Stream</div>\n                <div class="tab" data-tab="prompts">💬 Prompts</div>\n                <div class="tab" data-tab="findings">🔍 Findings</div>\n            </div>\n            \n            <div class="filter-bar">\n                <input type="text" class="filter-input" id="filter-input" placeholder="Filter events...">\n                <button class="clear-btn" onclick="clearLogs()">Clear</button>\n            </div>\n            \n            <div class="tab-content active" id="stream-tab">\n                <div class="log-container" id="log-container"></div>\n            </div>\n            \n            <div class="tab-content" id="prompts-tab">\n                <div class="log-container" id="prompts-container"></div>\n            </div>\n            \n            <div class="tab-content" id="findings-tab">\n                <div class="log-container" id="findings-container"></div>\n            </div>\n        </div>\n    </div>\n    \n    <script>\n        let ws = null;\n        let logs = [];\n        let prompts = [];\n        let findings = [];\n        let filterType = \'all\';\n        let filterText = \'\';\n        let reconnectTimeout = null;\n        \n        function connect() {\n            const wsUrl = `ws://${window.location.host}/ws/logs`;\n            ws = new WebSocket(wsUrl);\n            \n            ws.onopen = () => {\n                document.getElementById(\'connection-dot\').classList.remove(\'disconnected\');\n                document.getElementById(\'connection-text\').textContent = \'Connected\';\n            };\n            \n            ws.onclose = () => {\n                document.getElementById(\'connection-dot\').classList.add(\'disconnected\');\n                document.getElementById(\'connection-text\').textContent = \'Disconnected\';\n                // Reconnect after 3 seconds\n                if (reconnectTimeout) clearTimeout(reconnectTimeout);\n                reconnectTimeout = setTimeout(connect, 3000);\n            };\n            \n            ws.onerror = (err) => {\n                console.error(\'WebSocket error:\', err);\n            };\n            \n            ws.onmessage = (event) => {\n                const msg = JSON.parse(event.data);\n                \n                if (msg.type === \'state\') {\n                    updateState(msg.data);\n                } else if (msg.type === \'history\') {\n                    addLog(msg.data, false);\n                } else if (msg.type === \'event\') {\n                    addLog(msg.data, true);\n                }\n            };\n        }\n        \n        function updateState(state) {\n            document.getElementById(\'current-scan\').textContent = state.current_scan_id || \'-\';\n            document.getElementById(\'current-agent\').textContent = state.active_agent || \'-\';\n            document.getElementById(\'current-phase\').textContent = state.active_phase || \'-\';\n        }\n        \n        function addLog(event, animate = true) {\n            logs.push(event);\n            if (logs.length > 500) logs.shift();\n            \n            // Store prompts and findings separately\n            if (event.event_type === \'agent_prompt\' || event.event_type === \'agent_response\') {\n                prompts.push(event);\n                if (prompts.length > 200) prompts.shift();\n                renderPrompts();\n            }\n            \n            if (event.event_type === \'agent_findings\') {\n                findings.push(event);\n                if (findings.length > 200) findings.shift();\n                renderFindings();\n            }\n            \n            renderLogs(animate);\n        }\n        \n        function renderLogs(animate = true) {\n            const container = document.getElementById(\'log-container\');\n            const filtered = logs.filter(log => {\n                if (filterType !== \'all\' && log.event_type !== filterType) return false;\n                if (filterText && !JSON.stringify(log).toLowerCase().includes(filterText.toLowerCase())) return false;\n                return true;\n            });\n            \n            container.innerHTML = filtered.slice(-100).map(log => formatLogEntry(log)).join(\'\');\n            \n            if (animate) {\n                container.scrollTop = container.scrollHeight;\n            }\n        }\n        \n        function renderPrompts() {\n            const container = document.getElementById(\'prompts-container\');\n            const filtered = prompts.filter(log => {\n                if (filterText && !JSON.stringify(log).toLowerCase().includes(filterText.toLowerCase())) return false;\n                return true;\n            });\n            \n            container.innerHTML = filtered.slice(-50).map(log => formatPromptEntry(log)).join(\'\');\n            container.scrollTop = container.scrollHeight;\n        }\n        \n        function renderFindings() {\n            const container = document.getElementById(\'findings-container\');\n            const filtered = findings.filter(log => {\n                if (filterText && !JSON.stringify(log).toLowerCase().includes(filterText.toLowerCase())) return false;\n                return true;\n            });\n            \n            container.innerHTML = filtered.slice(-50).map(log => formatFindingsEntry(log)).join(\'\');\n            container.scrollTop = container.scrollHeight;\n        }\n        \n        function formatLogEntry(event) {\n            const time = new Date(event.timestamp).toLocaleTimeString();\n            const data = event.data || {};\n            \n            let dataDisplay = \'\';\n            if (event.event_type === \'agent_prompt\') {\n                dataDisplay = `<div class="prompt-viewer"><pre>${escapeHtml(data.prompt_preview || data.prompt_full || \'\')}</pre></div>`;\n            } else if (event.event_type === \'agent_response\') {\n                dataDisplay = `<div class="prompt-viewer"><pre>${escapeHtml(data.response_preview || \'\')}</pre></div>`;\n            } else {\n                dataDisplay = `<div class="log-data">${escapeHtml(JSON.stringify(data, null, 2))}</div>`;\n            }\n            \n            return `\n                <div class="log-entry ${event.event_type}">\n                    <div class="log-header">\n                        <span class="log-type">${formatEventType(event.event_type)}</span>\n                        <span class="log-time">${time}</span>\n                    </div>\n                    <div class="log-agent">${event.agent_name} ${event.scan_id ? `(${event.scan_id.slice(0, 8)}...)` : \'\'}</div>\n                    ${dataDisplay}\n                </div>\n            `;\n        }\n        \n        function formatPromptEntry(event) {\n            const time = new Date(event.timestamp).toLocaleTimeString();\n            const isPrompt = event.event_type === \'agent_prompt\';\n            const data = event.data || {};\n            \n            return `\n                <div class="log-entry ${event.event_type}">\n                    <div class="log-header">\n                        <span class="log-type">${isPrompt ? \'📤 Prompt\' : \'📥 Response\'}</span>\n                        <span class="log-time">${time}</span>\n                        <span class="log-agent">${event.agent_name}</span>\n                    </div>\n                    <div class="prompt-viewer">\n                        <pre>${escapeHtml(isPrompt ? (data.prompt_preview || \'\') : (data.response_preview || \'\'))}</pre>\n                    </div>\n                    ${isPrompt && data.prompt_tokens ? `<div>Tokens: ${data.prompt_tokens}</div>` : \'\'}\n                    ${!isPrompt && data.latency_ms ? `<div>Latency: ${data.latency_ms}ms</div>` : \'\'}\n                </div>\n            `;\n        }\n        \n        function formatFindingsEntry(event) {\n            const time = new Date(event.timestamp).toLocaleTimeString();\n            const data = event.data || {};\n            const findings = data.all_findings || [];\n            \n            const findingsHtml = findings.slice(0, 5).map(f => `\n                <div style="margin: 8px 0; padding: 8px; background: #1a1a24; border-radius: 4px;">\n                    <strong>${f.vulnerability_class || \'Unknown\'}</strong> in ${f.file_path || \'unknown\'}:${f.line_start || 0}\n                    <br><small>${f.reasoning ? f.reasoning.slice(0, 100) + \'...\' : \'\'}</small>\n                </div>\n            `).join(\'\');\n            \n            return `\n                <div class="log-entry agent_findings">\n                    <div class="log-header">\n                        <span class="log-type">🔍 ${findings.length} Finding(s)</span>\n                        <span class="log-time">${time}</span>\n                    </div>\n                    <div class="log-agent">${event.agent_name}</div>\n                    ${findingsHtml}\n                    ${findings.length > 5 ? `<div style="color: #888;">...and ${findings.length - 5} more</div>` : \'\'}\n                </div>\n            `;\n        }\n        \n        function formatEventType(type) {\n            const icons = {\n                \'agent_start\': \'🚀 Agent Start\',\n                \'agent_prompt\': \'📤 Prompt Sent\',\n                \'agent_response\': \'📥 Response\',\n                \'agent_findings\': \'🔍 Findings\',\n                \'agent_complete\': \'✅ Complete\',\n                \'tool_call\': \'🔧 Tool Call\',\n                \'tool_result\': \'📥 Tool Result\',\n                \'phase_transition\': \'🔄 Phase\',\n                \'error\': \'❌ Error\',\n                \'scan_start\': \'🎯 Scan Start\',\n                \'scan_complete\': \'🏁 Scan Complete\',\n            };\n            return icons[type] || type;\n        }\n        \n        function escapeHtml(text) {\n            if (!text) return \'\';\n            return text\n                .replace(/&/g, \'&amp;\')\n                .replace(/</g, \'&lt;\')\n                .replace(/>/g, \'&gt;\')\n                .replace(/"/g, \'&quot;\')\n                .replace(/\'/g, \'&#039;\');\n        }\n        \n        function clearLogs() {\n            logs = [];\n            prompts = [];\n            findings = [];\n            document.getElementById(\'log-container\').innerHTML = \'\';\n            document.getElementById(\'prompts-container\').innerHTML = \'\';\n            document.getElementById(\'findings-container\').innerHTML = \'\';\n        }\n        \n        // Tab switching\n        document.querySelectorAll(\'.tab\').forEach(tab => {\n            tab.addEventListener(\'click\', () => {\n                document.querySelectorAll(\'.tab\').forEach(t => t.classList.remove(\'active\'));\n                document.querySelectorAll(\'.tab-content\').forEach(c => c.classList.remove(\'active\'));\n                tab.classList.add(\'active\');\n                document.getElementById(`${tab.dataset.tab}-tab`).classList.add(\'active\');\n            });\n        });\n        \n        // Event type filtering\n        document.querySelectorAll(\'.agent-item\').forEach(item => {\n            item.addEventListener(\'click\', () => {\n                document.querySelectorAll(\'.agent-item\').forEach(i => i.classList.remove(\'active\'));\n                item.classList.add(\'active\');\n                filterType = item.dataset.type;\n                renderLogs(false);\n            });\n        });\n        \n        // Text filtering\n        document.getElementById(\'filter-input\').addEventListener(\'input\', (e) => {\n            filterText = e.target.value;\n            renderLogs(false);\n            renderPrompts();\n            renderFindings();\n        });\n        \n        // Connect on load\n        connect();\n    </script>\n</body>\n</html>\n'

def run_server (port :int =None ,host :str ='0.0.0.0'):
    port =port or int (os .getenv ('LOG_SERVER_PORT','5003'))
    print (f'\n╔══════════════════════════════════════════════════════════════╗\n║           SentinAI Agent Log Server                         ║\n╠══════════════════════════════════════════════════════════════╣\n║  Dashboard:  http://{host }:{port }/                              ║\n║  WebSocket:  ws://{host }:{port }/ws/logs                        ║\n║  REST API:   http://{host }:{port }/api/state                     ║\n║              http://{host }:{port }/api/history                   ║\n║              http://{host }:{port }/api/clear (POST)              ║\n╚══════════════════════════════════════════════════════════════╝\n')
    uvicorn .run (app ,host =host ,port =port ,log_level ='info')
if __name__ =='__main__':
    run_server ()
