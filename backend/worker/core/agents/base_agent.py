import asyncio 
import json 
import re 
import time 
import uuid 
from pathlib import Path 
from abc import ABC ,abstractmethod 
from typing import Any 
from ..config import AGENT_AGENTIC_ENABLED ,AGENT_AGENTIC_MAX_ROUNDS ,AGENT_OPENROUTER_TIMEOUT_SECONDS ,OPENROUTER_API_KEY ,OPENROUTER_API_URL ,AGENT_MODEL ,logger 
from .models import AgentContext ,AgentFinding ,AgentResult 
from .openrouter_agentic import run_openrouter_agentic_loop 
from .agent_logger import get_logger ,AgentLogger 
from .import pipeline_tools 
from .pipeline_tools import PipelineToolExecutor ,PIPELINE_AGENT_TOOLS 
_SKILL_MD_CACHE :str |None =None 

def _get_skill_md ()->str :
    global _SKILL_MD_CACHE 
    if _SKILL_MD_CACHE is not None :
        return _SKILL_MD_CACHE 
    skill_path =Path (__file__ ).resolve ().parent /'skill.md'
    try :
        _SKILL_MD_CACHE =skill_path .read_text (encoding ='utf-8').strip ()
        return _SKILL_MD_CACHE 
    except OSError :
        _SKILL_MD_CACHE ='You are an AI security analysis agent. You have been given project context (source files, call graph, entry points, sanitizers) in the user message. Use that context to perform your task. Respond only with the requested JSON format.'
        return _SKILL_MD_CACHE 

def format_files_for_prompt (file_contents :dict [str ,str ],*,max_lines_per_file :int =80 ,max_total_lines :int =1200 )->str :
    if not file_contents :
        return 'No file contents provided.'
    parts :list [str ]=[]
    total_lines =0 
    for path ,content in file_contents .items ():
        remaining =max_total_lines -total_lines 
        if remaining <=0 :
            break 
        lines =content .splitlines ()
        take =min (len (lines ),max_lines_per_file ,remaining )
        head =lines [:take ]
        snippet ='\n'.join (head )
        if len (lines )>take :
            snippet +=f'\n\n[... truncated, {len (lines )-take } more lines ...]'
        parts .append (f'### FILE: {path }\n```\n{snippet }\n```')
        total_lines +=take 
    omitted =len (file_contents )-len (parts )
    if omitted >0 :
        parts .append (f'[... {omitted } more file(s) omitted to limit context size ...]')
    return '\n\n'.join (parts )

def format_context_metadata (context :AgentContext )->str :
    lines =[]
    fc =getattr (context ,'file_contents',None )or {}
    if fc :
        paths =sorted (fc .keys ())[:80 ]
        lines .append ('## FILE LIST (use fetch_file(path) or fetch_context_slice(path, line) to read code)')
        lines .append ('\n'.join ((f'  - {p }'for p in paths )))
        if len (fc )>80 :
            lines .append (f'  ... and {len (fc )-80 } more files')
    cg =getattr (context ,'call_graph',None )or {}
    if cg :
        lines .append ('\n## CALL GRAPH (use trace_callers(fn) / trace_callees(fn) to explore)')
        entries =list (cg .items ())[:100 ]
        for caller ,callees in entries :
            callee_list =callees [:5 ]if isinstance (callees ,list )else [callees ]
            lines .append (f"  {caller } -> {', '.join ((str (c )for c in callee_list ))}")
        if len (cg )>100 :
            lines .append (f'  ... and {len (cg )-100 } more entries')
    eps =getattr (context ,'entry_points',None )or []
    if eps :
        lines .append ('\n## ENTRY POINTS (where untrusted data enters)')
        for ep in eps [:30 ]:
            lines .append (f"  - {ep .file_path }:{ep .line_number } {ep .function_name } (auth={getattr (ep ,'authentication_required',None )})")
        if len (eps )>30 :
            lines .append (f'  ... and {len (eps )-30 } more')
    reg =getattr (context ,'sanitizer_registry',None )or {}
    if reg :
        lines .append ('\n## SANITIZER REGISTRY (use lookup_sanitizers() for full list)')
        for name in list (reg .keys ())[:20 ]:
            lines .append (f'  - {name }')
        if len (reg )>20 :
            lines .append (f'  ... and {len (reg )-20 } more')
    if not lines :
        return 'No metadata available.'
    return '\n'.join (lines )

class BaseAgent (ABC ):

    def __init__ (self ,name :str ,llm_client :Any |None =None ,max_retries :int =3 ,timeout_seconds :int =120 ):
        self .name =name 
        self .llm_client =llm_client 
        self .max_retries =max_retries 
        self .timeout_seconds =timeout_seconds 

    def get_system_prompt (self ,context :AgentContext )->str :
        return _get_skill_md ()

    @abstractmethod 
    def build_prompt (self ,context :AgentContext ,include_file_contents :bool =True )->str :
        pass 

    def _supports_agentic (self )->bool :
        name =(self .name or '').lower ()
        return 'specialist'in name or 'analyst'in name or 'hunter'in name 

    @staticmethod 
    def _parse_text_tool_calls (content :str )->tuple [list [tuple [str ,dict ]],str ]:
        if not content or '[TOOL_CALL]'not in content :
            return ([],content )
        out_calls :list [tuple [str ,dict ]]=[]
        stripped_parts :list [str ]=[]
        rest =content 
        pattern_braced =re .compile ('\\[TOOL_CALL\\]\\s*\\{([^}]+)\\}\\s*\\[/TOOL_CALL\\]',re .IGNORECASE |re .DOTALL )
        pattern_simple =re .compile ('\\[TOOL_CALL\\]\\s*(.+?)\\s*\\[/TOOL_CALL\\]',re .IGNORECASE |re .DOTALL )
        while True :
            m =pattern_braced .search (rest )
            if not m :
                m =pattern_simple .search (rest )
            if not m :
                stripped_parts .append (rest )
                break 
            stripped_parts .append (rest [:m .start ()])
            block =m .group (1 ).strip ()
            rest =rest [m .end ():]
            tool_name =''
            args :dict [str ,Any ]={}
            if 'tool'in block .lower ()or '=>'in block :
                tool_m =re .search ('tool\\s*=>\\s*["\\\']([^"\\\']+)["\\\']',block ,re .IGNORECASE )
                if tool_m :
                    tool_name =tool_m .group (1 ).strip ()
                args_m =re .search ('args\\s*=>\\s*\\{([^}]*)\\}',block ,re .IGNORECASE |re .DOTALL )
                if args_m :
                    args_block =args_m .group (1 )
                    path_m =re .search ('(?:--path|["\\\']?path["\\\']?\\s*[:=])\\s*["\\\']([^"\\\']+)["\\\']',args_block ,re .IGNORECASE )
                    if path_m :
                        args ['path']=path_m .group (1 ).strip ()
                    line_m =re .search ('(?:--line|["\\\']?line["\\\']?\\s*[:=])\\s*(\\d+)',args_block ,re .IGNORECASE )
                    if line_m :
                        args ['line']=int (line_m .group (1 ))
                    window_m =re .search ('(?:--window|["\\\']?window["\\\']?\\s*[:=])\\s*(\\d+)',args_block ,re .IGNORECASE )
                    if window_m :
                        args ['window']=int (window_m .group (1 ))
                    fn_m =re .search ('(?:--function_name|["\\\']?function_name["\\\']?\\s*[:=])\\s*["\\\']([^"\\\']+)["\\\']',args_block ,re .IGNORECASE )
                    if fn_m :
                        args ['function_name']=fn_m .group (1 ).strip ()
            else :
                lines =[ln .strip ()for ln in block .splitlines ()if ln .strip ()]
                if lines :
                    tool_name =lines [0 ].strip ()
            if tool_name :
                out_calls .append ((tool_name ,args ))
        return (out_calls ,''.join (stripped_parts ).strip ())

    def _run_agentic (self ,context :AgentContext ,start_time :float ,logger :AgentLogger |None ,errors :list [str ])->AgentResult :
        if not OPENROUTER_API_KEY :
            errors .append ('Agentic mode requires OPENROUTER_API_KEY')
            return self ._run_non_agentic_fallback (context ,start_time ,logger ,errors )
        system_prompt =self .get_system_prompt (context )+'\n\n## How to use tools\n- The platform provides tools (fetch_file, fetch_context_slice, fetch_function, trace_callers, trace_callees, lookup_sanitizers, check_dead_code). Use the tool-calling feature to invoke them when you need code or data — do NOT write [TOOL_CALL] or any custom syntax in your message; the system will execute tools when you call them.\n- When you need a file: call fetch_file with the path (and optional start_line/end_line). When you have enough context to conclude, stop calling tools.\n\n## Final response (critical)\n- When you are done analyzing, respond with ONLY a single JSON object in the exact format the task specifies (e.g. {"findings": [...]}). No markdown, no code fences, no explanation, no tool calls in that final message. The response must parse as valid JSON. If you have no findings, return {"findings": []}.'
        prompt =self .build_prompt (context ,include_file_contents =False )
        prompt +='\n\nReply by calling tools when you need code; when finished, respond with ONLY the JSON object (e.g. {"findings": [...]}), no other text.'
        messages =[{'role':'system','content':system_prompt },{'role':'user','content':prompt }]
        executor =PipelineToolExecutor (context )

        def execute_tool (name :str ,args :dict )->str :
            return executor .execute (name ,args )
        agent_log =get_logger ()

        def on_tool_call (name :str ,args :dict )->None :
            if agent_log :
                agent_log .log_tool_call (self .name ,name ,args ,'')

        def on_tool_result (name :str ,args :dict ,result :str )->None :
            if agent_log :
                agent_log .log_tool_result (self .name ,name ,result ,'')
        try :
            openrouter_timeout =max (self .timeout_seconds ,AGENT_OPENROUTER_TIMEOUT_SECONDS )
            last_content ,total_tokens =asyncio .run (run_openrouter_agentic_loop (messages ,PIPELINE_AGENT_TOOLS ,execute_tool ,model =AGENT_MODEL ,api_key =OPENROUTER_API_KEY ,api_url =OPENROUTER_API_URL ,max_rounds =AGENT_AGENTIC_MAX_ROUNDS ,timeout_seconds =openrouter_timeout ,parse_text_tool_calls =lambda c :self ._parse_text_tool_calls (c )[0 ],on_tool_call =on_tool_call ,on_tool_result =on_tool_result ))
        except Exception as e :
            errors .append (f'OpenRouter agentic loop: {e !r }')
            return self ._run_non_agentic_fallback (context ,start_time ,logger ,errors )
        content_for_parse =last_content 
        _ ,content_for_parse =self ._parse_text_tool_calls (content_for_parse )
        content_for_parse =(content_for_parse or last_content or '').strip ()
        if not content_for_parse or not content_for_parse .strip ():
            findings =[]
        else :
            try :
                findings =self .parse_response (content_for_parse )
            except Exception as e :
                errors .append (f'Agentic parse_response: {e !r }')
                findings =[]
        execution_time_ms =int ((time .time ()-start_time )*1000 )
        if logger :
            logger .log_agent_complete (agent_name =self .name ,execution_time_ms =execution_time_ms ,token_usage =total_tokens ,errors =errors ,findings_count =len (findings ))
        return AgentResult (agent_name =self .name ,findings =findings ,execution_time_ms =execution_time_ms ,token_usage =total_tokens ,errors =errors ,metadata ={'agentic':True })

    def _run_non_agentic_fallback (self ,context :AgentContext ,start_time :float ,logger :AgentLogger |None ,errors :list [str ])->AgentResult :
        prompt =self .build_prompt (context ,include_file_contents =True )
        if logger :
            logger .log_agent_prompt (agent_name =self .name ,prompt =prompt ,prompt_tokens =len (prompt .split ()))
        system_prompt =self .get_system_prompt (context )
        resp =self ._call_llm_with_retry (prompt ,context ,system_prompt )
        response =resp .content if hasattr (resp ,'content')else resp 
        if logger :
            logger .log_agent_response (agent_name =self .name ,response =response if isinstance (response ,str )else json .dumps (response ),response_tokens =len (str (response ).split ()),latency_ms =0 )
        try :
            findings =self .parse_response (response )
        except Exception as e :
            errors .append (f'parse_response: {e }')
            findings =[]
        execution_time_ms =int ((time .time ()-start_time )*1000 )
        token_usage =getattr (resp ,'total_tokens',0 )if hasattr (resp ,'total_tokens')else 0 
        if logger :
            findings_dicts =[f .to_dict ()if hasattr (f ,'to_dict')else f for f in findings ]
            logger .log_agent_findings (agent_name =self .name ,findings =findings_dicts )
            logger .log_agent_complete (agent_name =self .name ,execution_time_ms =execution_time_ms ,token_usage =token_usage ,errors =errors ,findings_count =len (findings ))
        return AgentResult (agent_name =self .name ,findings =findings ,execution_time_ms =execution_time_ms ,token_usage =token_usage ,errors =errors ,metadata ={'agentic':False })

    @abstractmethod 
    def parse_response (self ,response :str )->list [AgentFinding ]:
        pass 

    def run (self ,context :AgentContext )->AgentResult :
        start_time =time .time ()
        errors :list [str ]=[]
        logger =get_logger ()
        if logger :
            logger .log_agent_start (agent_name =self .name ,agent_type =self ._get_agent_type (),context =context .__dict__ if hasattr (context ,'__dict__')else {},config ={'max_retries':self .max_retries ,'timeout_seconds':self .timeout_seconds })
        try :
            if AGENT_AGENTIC_ENABLED and OPENROUTER_API_KEY and self ._supports_agentic ():
                return self ._run_agentic (context ,start_time ,logger ,errors )
            prompt =self .build_prompt (context )
            if logger :
                logger .log_agent_prompt (agent_name =self .name ,prompt =prompt ,prompt_tokens =len (prompt .split ()))
            llm_start =time .time ()
            system_prompt =self .get_system_prompt (context )
            resp =self ._call_llm_with_retry (prompt ,context ,system_prompt )
            llm_latency_ms =int ((time .time ()-llm_start )*1000 )
            response =resp .content if hasattr (resp ,'content')else resp 
            if logger :
                logger .log_agent_response (agent_name =self .name ,response =response if isinstance (response ,str )else json .dumps (response ),response_tokens =len (str (response ).split ()),latency_ms =llm_latency_ms )
            findings =self .parse_response (response )
            execution_time_ms =int ((time .time ()-start_time )*1000 )
            token_usage =getattr (resp ,'total_tokens',0 )if hasattr (resp ,'total_tokens')else 0 
            if logger :
                findings_dicts =[f .to_dict ()if hasattr (f ,'to_dict')else f for f in findings ]
                logger .log_agent_findings (agent_name =self .name ,findings =findings_dicts )
            result =AgentResult (agent_name =self .name ,findings =findings ,execution_time_ms =execution_time_ms ,token_usage =token_usage ,errors =errors ,metadata ={})
            if logger :
                logger .log_agent_complete (agent_name =self .name ,execution_time_ms =execution_time_ms ,token_usage =token_usage ,errors =errors ,findings_count =len (findings ))
            return result 
        except Exception as e :
            execution_time_ms =int ((time .time ()-start_time )*1000 )
            error_msg =f'{self .name } failed: {str (e )}'
            errors .append (error_msg )
            if logger :
                logger .log_error (agent_name =self .name ,error_type =type (e ).__name__ ,error_message =str (e ))
                logger .log_agent_complete (agent_name =self .name ,execution_time_ms =execution_time_ms ,token_usage =0 ,errors =errors ,findings_count =0 )
            return AgentResult (agent_name =self .name ,findings =[],execution_time_ms =execution_time_ms ,token_usage =0 ,errors =errors ,metadata ={'error_type':type (e ).__name__ })

    def _get_agent_type (self )->str :
        name_lower =self .name .lower ()
        if 'recon'in name_lower or 'pattern'in name_lower or 'threat'in name_lower :
            return 'pre-scan'
        elif 'specialist'in name_lower or 'analyst'in name_lower or 'hunter'in name_lower :
            return 'specialist'
        elif 'dedup'in name_lower or 'consensus'in name_lower or 'skeptic'in name_lower :
            return 'synthesis'
        elif 'chain'in name_lower or 'attack'in name_lower or 'remediation'in name_lower :
            return 'post-processing'
        return 'unknown'

    def _call_llm_with_retry (self ,prompt :str ,context :AgentContext ,system_prompt :str |None =None )->str :
        last_error :Exception |None =None 
        for attempt in range (self .max_retries +1 ):
            try :
                if self .llm_client is None :
                    return self ._generate_mock_response (prompt )
                resp =self .llm_client .complete (prompt =prompt ,system_prompt =system_prompt ,timeout_seconds =self .timeout_seconds )
                if attempt >0 :
                    logger .info ('%s LLM call succeeded on attempt %s/%s after retries.',self .name ,attempt +1 ,self .max_retries +1 )
                return resp 
            except Exception as e :
                last_error =e 
                if attempt <self .max_retries :
                    backoff_seconds =2 **attempt +1 
                    time .sleep (backoff_seconds )
        raise last_error 

    def _generate_mock_response (self ,prompt :str )->str :
        return json .dumps ({'mock_finding':{'finding_id':f'MOCK-{uuid .uuid4 ().hex [:8 ]}','agent_source':self .name ,'file_path':'mock/file.py','line_start':1 ,'line_end':10 ,'vulnerability_class':'Mock Vulnerability','cwe_id':'CWE-000','reasoning':'Mock finding for testing'}})

    def validate_finding (self ,finding :AgentFinding )->bool :
        required_fields =['finding_id','agent_source','file_path','line_start','line_end','vulnerability_class']
        for field in required_fields :
            if not getattr (finding ,field ,None ):
                return False 
        return True 

    def adjust_confidence (self ,finding :AgentFinding ,adjustment :float )->AgentFinding :
        finding .confidence =max (0.0 ,min (1.0 ,finding .confidence +adjustment ))
        return finding 
