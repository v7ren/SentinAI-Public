import asyncio 
import json 
import os 
import re 
import ast 
from typing import Dict ,Any ,List ,Tuple ,Optional 
from dataclasses import dataclass 
import aiohttp 
from .config import OPENROUTER_API_KEY ,OPENROUTER_API_URL ,SMART_MODEL ,PHASE2_CONFIDENCE_THRESHOLD ,PHASE2_VALIDATION_MAX_PARALLEL ,PHASE2_VALIDATION_TIMEOUT_SECONDS ,PHASE2_VALIDATION_MAX_RETRIES ,VALIDATOR_DEBUG ,HIGH_RECALL_MODE ,logger 
from .agents .agent_logger import get_logger ,push_event_to_log_server 

@dataclass 
class ValidationResult :
    finding_index :int 
    keep :bool 
    confidence :float 
    justification :str 
    exclusion_reason :Optional [str ]
    original_finding :Dict [str ,Any ]
    validation_metadata :Optional [Dict [str ,Any ]]=None 

@dataclass 
class AgenticValidationConfig :
    max_tool_calls_per_finding :int =3 
    max_total_tool_calls_per_scan :int =60 
    tool_call_timeout_seconds :int =10 
    fallback_to_static :bool =True 
    agentic_confidence_ceiling :float =8.5 
VALIDATOR_TOOLS =[{'type':'function','function':{'name':'fetch_file','description':'Fetch file source. By default returns the full file (truncated at 8k chars). To save tokens, pass start_line and end_line (1-indexed) to get only that line range with line numbers.','parameters':{'type':'object','properties':{'path':{'type':'string','description':"Relative file path as it appears in the scan, e.g. 'utils/sanitizer.py'"},'start_line':{'type':'integer','description':'Optional. First line to include (1-indexed). Use with end_line to fetch only a range.'},'end_line':{'type':'integer','description':'Optional. Last line to include (1-indexed). Use with start_line to fetch only a range.'}},'required':['path']}}},{'type':'function','function':{'name':'fetch_function','description':'Fetch the source of a single named function from a file. Cheaper than fetch_file when you only need one function.','parameters':{'type':'object','properties':{'path':{'type':'string','description':'Relative file path'},'function_name':{'type':'string','description':'Exact function name to extract'}},'required':['path','function_name']}}},{'type':'function','function':{'name':'trace_callers','description':'Return all functions that call the given function, from the call graph. Use to understand who can reach a dangerous function.','parameters':{'type':'object','properties':{'function_name':{'type':'string','description':'Function to look up callers for'}},'required':['function_name']}}},{'type':'function','function':{'name':'trace_callees','description':'Return all functions called by the given function. Use to follow data flow downstream from a suspicious function.','parameters':{'type':'object','properties':{'function_name':{'type':'string','description':'Function to look up callees for'}},'required':['function_name']}}},{'type':'function','function':{'name':'lookup_sanitizers','description':'Return the full sanitizer registry for this scan. Use when you need to check whether any sanitization functions exist in the project.','parameters':{'type':'object','properties':{},'required':[]}}},{'type':'function','function':{'name':'check_dead_code','description':'Check whether a specific function is marked as dead/unreachable code in the dead code map.','parameters':{'type':'object','properties':{'path':{'type':'string','description':'Relative file path'},'function_name':{'type':'string','description':'Function name to check'}},'required':['path','function_name']}}},{'type':'function','function':{'name':'fetch_context_slice','description':'Fetch a wider line window around a specific line in a file. Use when ±10 lines is not enough to understand the surrounding logic.','parameters':{'type':'object','properties':{'path':{'type':'string','description':'Relative file path'},'line':{'type':'integer','description':'Center line number (1-indexed)'},'window':{'type':'integer','description':'Number of lines above and below to include. Default 30.','default':30 }},'required':['path','line']}}},{'type':'function','function':{'name':'find_stdin_invokers','description':'For findings in a script that reads from stdin/pipe (e.g. page.open(input), PhantomJS): find other files that likely invoke this script and write to its stdin. Use to decide if the sink input is attacker-controlled or only server-controlled (e.g. localhost URL).','parameters':{'type':'object','properties':{'script_path':{'type':'string','description':"Relative path of the script that reads from stdin/pipe, e.g. 'src/check.js'"}},'required':['script_path']}}}]

class ToolExecutor :

    def __init__ (self ,scan_id :str ,file_store :Dict [str ,str ],redis_client ):
        self .scan_id =scan_id 
        self .file_store =file_store or {}
        self .redis =redis_client 

    async def execute (self ,tool_name :str ,tool_args :Dict [str ,Any ])->str :
        try :
            if tool_name =='fetch_file':
                start_line =tool_args .get ('start_line')
                end_line =tool_args .get ('end_line')
                return self ._fetch_file (tool_args ['path'],start_line =start_line if isinstance (start_line ,int )else None ,end_line =end_line if isinstance (end_line ,int )else None )
            elif tool_name =='fetch_function':
                return self ._fetch_function (tool_args ['path'],tool_args ['function_name'])
            elif tool_name =='trace_callers':
                return await self ._trace_callers (tool_args ['function_name'])
            elif tool_name =='trace_callees':
                return await self ._trace_callees (tool_args ['function_name'])
            elif tool_name =='lookup_sanitizers':
                return await self ._lookup_sanitizers ()
            elif tool_name =='check_dead_code':
                return await self ._check_dead_code (tool_args ['path'],tool_args ['function_name'])
            elif tool_name =='fetch_context_slice':
                window =tool_args .get ('window',30 )
                return self ._fetch_context_slice (tool_args ['path'],tool_args ['line'],window )
            elif tool_name =='find_stdin_invokers':
                return await self ._find_stdin_invokers (tool_args ['script_path'])
            else :
                return f'Unknown tool: {tool_name }'
        except Exception as e :
            return f'Tool error ({tool_name }): {type (e ).__name__ }: {str (e )}'

    def _fetch_file (self ,path :str ,start_line :Optional [int ]=None ,end_line :Optional [int ]=None )->str :
        if not self .file_store :
            redis_key =f'{self .scan_id }:file_store'
            raw =None 
            if self .redis is None or not hasattr (self .redis ,'get'):
                logger .debug (f'[{self .scan_id }] fetch_file: redis_client missing; cannot load {redis_key !r }')
            else :
                try :
                    raw =self .redis .get (redis_key )
                except Exception as e :
                    logger .debug (f'[{self .scan_id }] fetch_file: Redis get failed key={redis_key !r }: {type (e ).__name__ }: {e }')
                    raw =None 
            logger .debug (f'[{self .scan_id }] fetch_file: Redis lookup key={redis_key !r } found={bool (raw )}')
            if raw :
                try :
                    self .file_store =json .loads (raw )
                    logger .debug (f'[{self .scan_id }] Loaded file_store from Redis with {len (self .file_store )} files')
                except Exception as e :
                    logger .error (f'[{self .scan_id }] Failed to parse file_store from Redis: {e }')
                    self .file_store ={}
        logger .debug (f'[{self .scan_id }] _fetch_file called for path: {path }, file_store size: {len (self .file_store )}')
        normalized =path .lstrip ('./').lstrip ('/')
        if normalized in self .file_store :
            content =self .file_store [normalized ]
            logger .debug (f'[{self .scan_id }] ✅ File found (exact match): {normalized }')
        else :
            matches =[k for k in self .file_store if k .endswith (normalized )or normalized .endswith (k )]
            if not matches :
                available =list (self .file_store .keys ())[:10 ]
                logger .warning (f'[{self .scan_id }] ❌ File not found: {path }. Available files (first 10): {available }')
                return f'File not found: {path }. Available files (first 10): {available }'
            content =self .file_store [matches [0 ]]
            logger .debug (f'[{self .scan_id }] ✅ File found (suffix match): {matches [0 ]} -> {normalized }')
        if start_line is not None and end_line is not None and (start_line >=1 )and (end_line >=start_line ):
            lines =content .splitlines ()
            total =len (lines )
            s =max (0 ,start_line -1 )
            e =min (total ,end_line )
            if s >=total :
                return f'File has {total } lines; start_line {start_line } is out of range.'
            result =[]
            for i in range (s ,e ):
                result .append (f'{i +1 :4}| {lines [i ]}')
            header =f'[Lines {s +1 }-{e } of {total }]\n'
            return header +'\n'.join (result )
        if len (content )>8000 :
            return content [:8000 ]+f'\n\n[TRUNCATED — full file is {len (content )} chars]'
        return content 

    def _fetch_function (self ,path :str ,function_name :str )->str :
        file_content =self ._fetch_file (path )

        def _extract_js_function (content :str ,func_name :str )->Optional [str ]:
            fn =re .escape (func_name )
            patterns =[f'(?:export\\s+)?(?:async\\s+)?function\\s+{fn }\\s*\\(',f'(?:const|let|var)\\s+{fn }\\s*=\\s*(?:async\\s+)?function\\s*\\(',f'(?:const|let|var)\\s+{fn }\\s*=\\s*(?:async\\s+)?\\(',f'(?:exports|module\\.exports)\\.{fn }\\s*=\\s*(?:async\\s+)?function\\s*\\(',f'{fn }\\s*:\\s*(?:async\\s+)?function\\s*\\(',f'(?:async\\s+)?{fn }\\s*\\([^)]*\\)\\s*\\{{']
            lines =content .splitlines ()
            for i ,line in enumerate (lines ):
                for pattern in patterns :
                    if re .search (pattern ,line ):
                        depth =0 
                        end =i 
                        for j in range (i ,min (i +80 ,len (lines ))):
                            depth +=lines [j ].count ('{')-lines [j ].count ('}')
                            end =j 
                            if depth <=0 and j >i :
                                break 
                        return '\n'.join (lines [i :end +1 ])
            return None 

        def _extract_from_content (content :str ,fp :str )->Optional [str ]:
            if any ((fp .endswith (ext )for ext in ('.js','.jsx','.ts','.tsx','.mjs','.cjs'))):
                js_result =_extract_js_function (content ,function_name )
                if js_result :
                    return js_result 
            try :
                tree =ast .parse (content )
                for node in ast .walk (tree ):
                    if isinstance (node ,(ast .FunctionDef ,ast .AsyncFunctionDef ))and node .name ==function_name :
                        lines =content .splitlines ()
                        start =node .lineno -1 
                        end =node .end_lineno 
                        return '\n'.join (lines [start :end ])
            except SyntaxError :
                lines =content .splitlines ()
                for i ,line in enumerate (lines ):
                    if f'def {function_name }'in line :
                        end =min (i +60 ,len (lines ))
                        return '\n'.join (lines [i :end ])+'\n[may be truncated]'
            return None 
        if not file_content .startswith ('File not found'):
            direct =_extract_from_content (file_content ,path )
            if direct :
                return direct 
        if not self .file_store :
            _ =self ._fetch_file (path )
        for fp ,content in (self .file_store or {}).items ():
            candidate =_extract_from_content (content ,fp )
            if candidate :
                prefix =''if fp ==path else f'[Found in {fp }, not {path }]\n'
                return prefix +candidate 
        if file_content .startswith ('File not found'):
            return file_content 
        return f"Function '{function_name }' not found in {path } or any indexed file."

    async def _trace_callers (self ,function_name :str )->str :
        raw =await self ._redis_get (f'{self .scan_id }:call_graph')
        if not raw :
            return 'Call graph not available for this scan.'
        try :
            call_graph =json .loads (raw )
            callers =[fn for fn ,data in call_graph .items ()if function_name in fn or function_name in [callee .split ('::')[-1 ]for callee in data .get ('calls',[])]]
            if not callers :
                return f"No callers found for '{function_name }' in call graph."
            return f"Functions that call '{function_name }':\n"+'\n'.join ((f'  - {c }'for c in callers ))
        except Exception as e :
            return f'Error parsing call graph: {e }'

    async def _trace_callees (self ,function_name :str )->str :
        raw =await self ._redis_get (f'{self .scan_id }:call_graph')
        if not raw :
            return 'Call graph not available for this scan.'
        try :
            call_graph =json .loads (raw )
            direct =call_graph .get (function_name )
            if direct is None :
                direct =next ((data for key ,data in call_graph .items ()if key .endswith (f'::{function_name }')),{})
            callees =direct .get ('calls',[])if isinstance (direct ,dict )else []
            if not callees :
                return f"'{function_name }' calls no other tracked functions, or is not in the call graph."
            return f"Functions called by '{function_name }':\n"+'\n'.join ((f'  - {c }'for c in callees ))
        except Exception as e :
            return f'Error parsing call graph: {e }'

    async def _lookup_sanitizers (self )->str :
        raw =await self ._redis_get (f'{self .scan_id }:sanitizer_registry')
        if not raw :
            return 'Sanitizer registry not available for this scan.'
        try :
            registry =json .loads (raw )
            if not registry :
                return 'No sanitizers found in this project.'
            lines =[]
            for name ,info in registry .items ():
                if isinstance (info ,list ):
                    lines .append (f"  - {name }: {', '.join ((str (item )for item in info [:10 ]))}")
                elif isinstance (info ,dict ):
                    lines .append (f'  - {name }: {json .dumps (info )[:200 ]}')
                else :
                    lines .append (f'  - {name }: {info }')
            return 'Sanitizer registry:\n'+'\n'.join (lines )
        except Exception as e :
            return f'Error parsing sanitizer registry: {e }'

    async def _check_dead_code (self ,path :str ,function_name :str )->str :
        raw =await self ._redis_get (f'{self .scan_id }:dead_code_map')
        if not raw :
            return 'Dead code map not available for this scan.'
        try :
            dead_map =json .loads (raw )
            key =f'{path }::{function_name }'
            alt_key =function_name 
            dead_info =dead_map .get (key )or dead_map .get (alt_key )or {}
            if dead_info :
                return f"'{function_name }' in {path } appears to be marked as dead or unreachable code."
            return f"'{function_name }' in {path } does not appear to be marked as dead code."
        except Exception as e :
            return f'Error parsing dead code map: {e }'

    async def _find_stdin_invokers (self ,script_path :str )->str :
        _ =self ._fetch_file (script_path )
        store =self .file_store or {}
        script_path_norm =script_path .lstrip ('./').replace ('\\','/')
        basename =script_path_norm .rsplit ('/',1 )[-1 ]
        invoker_re =re .compile ('(?:stdin|PIPE|subprocess|proc\\.stdin|\\.write\\s*\\(|phantomjs|child_process)',re .I )
        script_ref_re =re .compile (re .escape (basename )+'|phantomjs|check\\.js',re .I )
        max_chars =1200 
        results =[]
        for path ,content in store .items ():
            if not content or not isinstance (content ,str ):
                continue 
            path_norm =path .replace ('\\','/')
            if path_norm ==script_path_norm or path_norm .endswith ('/'+script_path_norm ):
                continue 
            if not script_ref_re .search (content )or not invoker_re .search (content ):
                continue 
            snippet =content if len (content )<=max_chars else content [:max_chars ]+'\n[TRUNCATED]'
            results .append (f'[{path_norm }]\n{snippet }')
        if not results :
            return f"No files that appear to invoke '{script_path }' (with stdin/PIPE/subprocess) were found in this scan."
        return 'Files that may invoke this script and write to its stdin:\n\n'+'\n\n---\n\n'.join (results )

    def _fetch_context_slice (self ,path :str ,line :int ,window :int =30 )->str :
        file_content =self ._fetch_file (path )
        if file_content .startswith ('File not found'):
            return file_content 
        lines =file_content .splitlines ()
        line_idx =max (0 ,min (line -1 ,len (lines )-1 ))
        start =max (0 ,line_idx -window )
        end =min (len (lines ),line_idx +window +1 )
        result =[]
        for i in range (start ,end ):
            prefix ='>>> 'if i ==line_idx else '    '
            result .append (f'{prefix }{i +1 :4}| {lines [i ]}')
        return '\n'.join (result )

    async def _redis_get (self ,key :str )->Optional [str ]:
        try :
            if hasattr (self .redis ,'get'):
                result =self .redis .get (key )
                if asyncio .iscoroutine (result ):
                    return await result 
                return result 
        except Exception as e :
            logger .warning (f'[TOOL_EXECUTOR] Redis get failed for {key }: {e }')
        return None 

def _truncate_for_log (text :str ,max_len :int =400 )->str :
    if not text :
        return ''
    one_line =text .replace ('\n',' ').strip ()
    if len (one_line )<=max_len :
        return one_line 
    return one_line [:max_len ].rstrip ()+f' ... [{len (text )} chars total]'

class FindingsValidator :

    def __init__ (self ,confidence_threshold :float =PHASE2_CONFIDENCE_THRESHOLD ,max_parallel :int =PHASE2_VALIDATION_MAX_PARALLEL ,timeout_seconds :int =PHASE2_VALIDATION_TIMEOUT_SECONDS ,max_retries :int =PHASE2_VALIDATION_MAX_RETRIES ):
        self .confidence_threshold =confidence_threshold 
        self .max_parallel =max_parallel 
        self .timeout_seconds =timeout_seconds 
        self .max_retries =max_retries 
        self .api_url =OPENROUTER_API_URL 

    def _extract_message_text (self ,result :Dict [str ,Any ])->str :
        message =result .get ('choices',[{}])[0 ].get ('message',{})
        content =message .get ('content','')
        if isinstance (content ,str ):
            return content 
        if isinstance (content ,list ):
            parts :List [str ]=[]
            for item in content :
                if isinstance (item ,dict ):
                    text_val =item .get ('text')
                    if isinstance (text_val ,str ):
                        parts .append (text_val )
                elif isinstance (item ,str ):
                    parts .append (item )
            return '\n'.join (parts ).strip ()
        return str (content or '')

    def _extract_json_object_from_text (self ,text :str )->Optional [str ]:
        if not text :
            return None 
        stripped =text .strip ()
        fence_match =re .search ('```(?:json)?\\s*(\\{.*?\\})\\s*```',stripped ,flags =re .DOTALL |re .IGNORECASE )
        if fence_match :
            return fence_match .group (1 ).strip ()
        if stripped .startswith ('{')and stripped .endswith ('}'):
            return stripped 
        start =stripped .find ('{')
        if start ==-1 :
            return None 
        depth =0 
        for idx in range (start ,len (stripped )):
            ch =stripped [idx ]
            if ch =='{':
                depth +=1 
            elif ch =='}':
                depth -=1 
                if depth ==0 :
                    return stripped [start :idx +1 ]
        return None 

    def _coerce_validation_payload (self ,raw_content :str )->Optional [Dict [str ,Any ]]:
        if not raw_content :
            return None 
        try :
            parsed =json .loads (raw_content )
            if isinstance (parsed ,dict ):
                return parsed 
        except Exception :
            pass 
        try :
            start =raw_content .find ('{')
            if start !=-1 :
                candidate =raw_content [start :].strip ()
                candidate =re .sub (',?\\s*"[^"]+"\\s*:\\s*$','',candidate )
                candidate =re .sub (',\\s*$','',candidate )
                if not candidate .endswith ('}'):
                    candidate =candidate +'}'
                parsed =json .loads (candidate )
                if isinstance (parsed ,dict ):
                    logger .debug ('[VALIDATOR] JSON recovery path=a_close_brace')
                    return parsed 
        except Exception :
            pass 
        try :
            keep_m =re .search ('"keep_finding"\\s*:\\s*(true|false)',raw_content ,flags =re .IGNORECASE )
            conf_m =re .search ('"confidence_score"\\s*:\\s*([0-9]+(?:\\.[0-9]+)?)',raw_content ,flags =re .IGNORECASE )
            disp_m =re .search ('"disposition"\\s*:\\s*"([^"]+)"',raw_content ,flags =re .IGNORECASE )
            if keep_m :
                keep_val =keep_m .group (1 ).lower ()=='true'
                conf_val =float (conf_m .group (1 ))if conf_m else None 
                out :Dict [str ,Any ]={'keep_finding':keep_val }
                if conf_val is not None :
                    out ['confidence_score']=conf_val 
                else :
                    out ['_confidence_missing']=True 
                if disp_m :
                    out ['disposition']=disp_m .group (1 )
                logger .debug ('[VALIDATOR] JSON recovery path=b_regex_extract')
                return out 
        except Exception :
            pass 
        extracted =self ._extract_json_object_from_text (raw_content )
        if extracted :
            try :
                parsed =json .loads (extracted )
                if isinstance (parsed ,dict ):
                    return parsed 
            except Exception :
                try :
                    parsed =ast .literal_eval (extracted )
                    if isinstance (parsed ,dict ):
                        return parsed 
                except Exception :
                    pass 
        return None 

    def _normalize_validation_fields (self ,data :Dict [str ,Any ])->Dict [str ,Any ]:
        keep =data .get ('keep_finding')
        if keep is None :
            keep =data .get ('keep')
        if isinstance (keep ,str ):
            keep =keep .strip ().lower ()in {'true','1','yes','keep'}
        if keep is None :
            keep =True 
        confidence =data .get ('confidence_score')
        if confidence is None :
            confidence =data .get ('confidence')
        if isinstance (confidence ,str ):
            m =re .search ('\\d+(\\.\\d+)?',confidence )
            confidence =float (m .group (0 ))if m else 5.0 
        try :
            confidence =float (confidence )
        except Exception :
            confidence =5.0 
        confidence =max (0.0 ,min (10.0 ,confidence ))
        justification =data .get ('justification')
        if not isinstance (justification ,str )or not justification .strip ():
            justification =data .get ('reasoning')or data .get ('reason')or 'Validation was inconclusive based on the available response'
        exclusion_reason =data .get ('exclusion_reason')
        if exclusion_reason is not None and (not isinstance (exclusion_reason ,str )):
            exclusion_reason =str (exclusion_reason )
        disposition =data .get ('disposition')
        if disposition is None :
            disposition ='retain_for_review'if keep else 'likely_not_clear_vulnerability'
        if not isinstance (disposition ,str ):
            disposition =str (disposition )
        return {'keep_finding':bool (keep ),'confidence_score':confidence ,'justification':str (justification ),'exclusion_reason':exclusion_reason ,'disposition':disposition }

    async def validate_findings_parallel (self ,session :aiohttp .ClientSession ,findings :List [Dict [str ,Any ]],filename :str ,file_content :str ,context_info :str ='')->Tuple [List [Dict [str ,Any ]],List [Dict [str ,Any ]],Dict [str ,Any ]]:
        if not findings :
            return ([],[],{'total':0 ,'kept':0 ,'excluded':0 })
        logger .info (f'[VALIDATOR] Phase 2: Validating {len (findings )} findings in parallel (confidence threshold: {self .confidence_threshold })')
        validation_tasks =[]
        for i ,finding in enumerate (findings ):
            task =self ._validate_single_finding (session =session ,finding_index =i ,finding =finding ,filename =filename ,file_content =file_content ,context_info =context_info )
            validation_tasks .append (task )
        all_results =[]
        for i in range (0 ,len (validation_tasks ),self .max_parallel ):
            batch =validation_tasks [i :i +self .max_parallel ]
            batch_results =await asyncio .gather (*batch ,return_exceptions =True )
            for j ,result in enumerate (batch_results ):
                if isinstance (result ,Exception ):
                    finding_idx =i +j 
                    logger .error (f'[VALIDATOR] Validation task exception for finding {finding_idx }: {type (result ).__name__ }: {repr (result )}')
                    original_finding =findings [finding_idx ]if finding_idx <len (findings )else {}
                    all_results .append (ValidationResult (finding_index =finding_idx ,keep =True ,confidence =5.5 ,justification =f'Validation task failed with {type (result ).__name__ }; retaining the finding as a precaution because validation was inconclusive',exclusion_reason =None ,original_finding =original_finding ,validation_metadata ={'validation_mode':'static_fallback','file_store_available':False ,'tool_failures':[]}))
                    continue 
                all_results .append (result )
        kept_findings =[]
        excluded_findings =[]
        confidence_distribution ={'high (8-10)':0 ,'medium (5-7)':0 ,'low (<5)':0 }
        parse_failures =0 
        for result in all_results :
            if result .confidence >=8 :
                confidence_distribution ['high (8-10)']+=1 
            elif result .confidence >=5 :
                confidence_distribution ['medium (5-7)']+=1 
            else :
                confidence_distribution ['low (<5)']+=1 
            original_validation_status =result .original_finding .get ('validation_status')
            if original_validation_status =='parse_failed':
                parse_failures +=1 
            if result .keep :
                if original_validation_status =='parse_failed':
                    phase ='parse_failed'
                else :
                    phase ='validated'
                enriched_finding ={**result .original_finding ,'_validation':{'confidence':result .confidence ,'justification':result .justification ,'phase':phase ,'disposition':'retain_for_review'}}
                if result .validation_metadata :
                    enriched_finding ['_validation']['validation_mode']=result .validation_metadata .get ('validation_mode','static_fallback')
                    enriched_finding ['_validation']['file_store_available']=result .validation_metadata .get ('file_store_available',False )
                    enriched_finding ['_validation']['tool_failures']=result .validation_metadata .get ('tool_failures',[])
                    val_mode =result .validation_metadata .get ('validation_mode','')
                    if val_mode =='static_fallback':
                        capped_confidence =min (result .confidence ,7.0 )
                        enriched_finding ['_validation']['confidence']=capped_confidence 
                        enriched_finding ['confidence_score']=min (enriched_finding .get ('confidence_score',capped_confidence ),capped_confidence )
                        enriched_finding ['_validation_warning']='Validated without richer contextual support. Confidence was capped at 7.0 to avoid overstating certainty.'
                kept_findings .append (enriched_finding )
            else :
                excluded_finding ={**result .original_finding ,'_validation':{'confidence':result .confidence ,'justification':result .justification ,'exclusion_reason':result .exclusion_reason ,'phase':'filtered','disposition':'likely_not_clear_vulnerability'}}
                excluded_findings .append (excluded_finding )
        stats ={'total':len (findings ),'kept':len (kept_findings ),'excluded':len (excluded_findings ),'parse_failures':parse_failures ,'confidence_distribution':confidence_distribution ,'confidence_threshold':self .confidence_threshold ,'reduction_rate':round (len (excluded_findings )/max (1 ,len (findings ))*100 ,1 )}
        logger .info (f"[VALIDATOR] Phase 2 complete: total_in={stats ['total']}, parse_failures={parse_failures }, kept={stats ['kept']}, dropped={stats ['excluded']} ({stats ['reduction_rate']}% filtered)")
        return (kept_findings ,excluded_findings ,stats )

    async def _validate_single_finding (self ,session :aiohttp .ClientSession ,finding_index :int ,finding :Dict [str ,Any ],filename :str ,file_content :str ,context_info :str )->ValidationResult :
        finding_type =finding .get ('type','Unknown')
        severity =finding .get ('severity','MEDIUM')
        description =finding .get ('description','')
        vuln_code =finding .get ('vulnerable_code','')
        line =finding .get ('line',0 )
        code_context =self ._get_code_context (file_content ,line )
        system_prompt =self ._build_validation_prompt ()
        user_content =self ._build_validation_content (filename =filename ,finding_type =finding_type ,severity =severity ,description =description ,vuln_code =vuln_code ,line =line ,code_context =code_context ,context_info =context_info )
        payload ={'model':SMART_MODEL ,'messages':[{'role':'system','content':system_prompt },{'role':'user','content':user_content }],'temperature':0.1 ,'response_format':{'type':'json_object'},'max_tokens':2048 }
        last_exception :Optional [Exception ]=None 
        for attempt in range (self .max_retries +1 ):
            try :
                async with session .post (self .api_url ,json =payload ,headers ={'Authorization':f'Bearer {OPENROUTER_API_KEY }'},timeout =aiohttp .ClientTimeout (total =self .timeout_seconds ))as resp :
                    if resp .status !=200 :
                        error_text =await resp .text ()
                        logger .error (f'[VALIDATOR] API error for finding {finding_index } (attempt {attempt +1 }/{self .max_retries +1 }): {resp .status } {error_text [:500 ]}'+('...'if len (error_text )>500 else ''))
                        if attempt <self .max_retries and resp .status in {408 ,429 ,500 ,502 ,503 ,504 }:
                            await asyncio .sleep (min (30 ,2 *(attempt +1 )))
                            continue 
                        return ValidationResult (finding_index =finding_index ,keep =True ,confidence =6.0 ,justification ='Validation could not be completed due to an API error; retaining the finding for review without strong confirmation',exclusion_reason =None ,original_finding =finding )
                    result =await resp .json ()
                    raw_content =self ._extract_message_text (result )
                    validation_data =self ._coerce_validation_payload (raw_content )
                    if validation_data is None :
                        full_raw =(raw_content or '').strip ()
                        if full_raw :
                            raw_preview =full_raw [:600 ]if len (full_raw )<=600 else full_raw [:600 ]+f' ... [{len (full_raw )} chars]'
                        else :
                            msg =(result .get ('choices')or [{}])[0 ].get ('message')or {}
                            content_preview =str (msg .get ('content',msg ))[:400 ]
                            raw_preview =f'Extracted text empty. message keys={list (msg .keys ())!r } content_preview={content_preview }'
                        logger .warning (f'[VALIDATOR] Parse failed for finding {finding_index } in {filename }. Raw response preview: {raw_preview }. Action: Kept but flagged with reduced confidence.')
                        logger .info (f'[VALIDATOR] Parse failed finding {finding_index } in {filename } | full raw (first 1200 chars): {(full_raw or raw_preview )[:1200 ]}'+('...'if len (full_raw or raw_preview )>1200 else ''))
                        if VALIDATOR_DEBUG and full_raw :
                            logger .info (f'[VALIDATOR_DEBUG] Parse failed finding {finding_index } in {filename } | full raw response (first 2000 chars): {full_raw [:2000 ]}'+('...'if len (full_raw )>2000 else ''))
                        original_confidence =finding .get ('confidence_score',finding .get ('confidence',10.0 ))
                        reduced_confidence =original_confidence *0.3 
                        finding ['validation_status']='parse_failed'
                        finding ['_validation_warning']=f'Validation was inconclusive because the LLM returned a malformed response. Original confidence {original_confidence :.1f} was reduced to {reduced_confidence :.1f}.'
                        return ValidationResult (finding_index =finding_index ,keep =True ,confidence =reduced_confidence ,justification =f'Validation response could not be parsed; retaining the finding with reduced confidence ({reduced_confidence :.1f}) because the result is inconclusive',exclusion_reason =None ,original_finding =finding )
                    normalized =self ._normalize_validation_fields (validation_data )
                    keep =normalized ['keep_finding']
                    confidence =normalized ['confidence_score']
                    justification =normalized ['justification']
                    exclusion_reason =normalized ['exclusion_reason']
                    if validation_data .get ('_confidence_missing')and keep :
                        try :
                            original_conf =float (finding .get ('confidence_score',finding .get ('confidence',confidence ))or confidence )
                            confidence =max (0.0 ,min (10.0 ,original_conf ))
                            logger .debug (f'[VALIDATOR] Recovery path=c_keep_original_confidence finding={finding_index } file={filename !r }')
                        except Exception :
                            pass 
                    if confidence <self .confidence_threshold :
                        if HIGH_RECALL_MODE :
                            keep =True 
                            finding ['validation_status']='validated_probable_fp'
                            finding ['_below_threshold_note']=f'Confidence {confidence :.1f} is below threshold {self .confidence_threshold :.1f} but kept in high-recall mode.'
                            logger .debug (f'[VALIDATOR] High-recall mode: keeping finding {finding_index } with confidence={confidence :.1f} (below threshold)')
                        else :
                            keep =False 
                            if not exclusion_reason :
                                exclusion_reason =f'Likely not a clear vulnerability: confidence {confidence :.1f} is below the retention threshold of {self .confidence_threshold :.1f}'
                    if attempt >0 :
                        logger .info (f'[VALIDATOR] Finding {finding_index } validation succeeded on attempt {attempt +1 }/{self .max_retries +1 } after retries (file={filename !r }).')
                    return ValidationResult (finding_index =finding_index ,keep =keep ,confidence =confidence ,justification =justification ,exclusion_reason =exclusion_reason if not keep else None ,original_finding =finding )
            except Exception as e :
                last_exception =e 
                error_str =str (e ).lower ()
                is_transient_network =any ((err in error_str for err in ['transfer','payload','connection','reset','eof','incomplete']))or isinstance (e ,(aiohttp .ClientPayloadError ,aiohttp .http_exceptions .TransferEncodingError ,aiohttp .ClientOSError ))
                if is_transient_network and attempt <self .max_retries :
                    wait_time =min (30 ,2 **attempt )
                    logger .warning (f'[VALIDATOR] Network error for finding {finding_index } (attempt {attempt +1 }/{self .max_retries +1 }): {type (e ).__name__ }: {repr (e )}. Retrying in {wait_time }s...')
                    await asyncio .sleep (wait_time )
                    continue 
                logger .error (f'[VALIDATOR] Exception for finding {finding_index } (attempt {attempt +1 }/{self .max_retries +1 }): {type (e ).__name__ }: {repr (e )}')
                if attempt <self .max_retries :
                    if isinstance (e ,asyncio .TimeoutError ):
                        await asyncio .sleep (2 *(attempt +1 ))
                    else :
                        await asyncio .sleep (1 )
                    continue 
        err_name =type (last_exception ).__name__ if last_exception else 'UnknownError'
        return ValidationResult (finding_index =finding_index ,keep =True ,confidence =5.5 ,justification =f'Validation was inconclusive after retries ({err_name }); retaining the finding as a precaution rather than as a confirmed vulnerability',exclusion_reason =None ,original_finding =finding )

    def _build_validation_prompt (self )->str :
        return 'You are a senior security engineer reviewing a potential vulnerability finding.\nYour task is to assess whether this finding appears to represent a clear, actionable vulnerability,\nor whether it more likely lacks sufficient evidence, exploitability, or security impact.\n\nVALIDATION GOAL:\nDecide whether the finding should be retained as a likely actionable vulnerability finding,\nor filtered out because it is likely not a clear vulnerability based on the available evidence.\n\nEVALUATION CRITERIA:\n1. Is there a plausible and concrete exploit path?\n2. Is there evidence of meaningful security impact?\n3. Are the code location and surrounding context sufficient to support the claim?\n4. Would this be actionable for a security team?\n5. Is this more than a theoretical concern or best-practice observation?\n\nSTRONG FILTERING SIGNALS:\nFilter out findings when they are more likely:\n1. A theoretical concern without a practical exploit path\n2. A best-practice issue rather than a concrete vulnerability\n3. Missing critical evidence needed to establish exploitability\n4. Low-impact behavior that does not clearly create security risk\n5. Better categorized as hardening advice, operational risk, or noise\n\nPRECEDENTS - These usually should NOT be treated as clear vulnerabilities:\n1. JSON.parse() / response.json() is standard parsing, not insecure deserialization\n2. Hardcoded localhost/127.0.0.1 URLs are dev endpoints, not secrets\n3. UUIDs are generally unguessable and do not require extra validation\n4. Environment variables and CLI flags are typically trusted in secure environments\n5. React setState with server data is not XSS unless unsafe HTML rendering is involved\n6. router.push() / redirect after login is a normal pattern, not an access control issue\n7. Client-side auth checks alone do not establish a vulnerability; backend validation matters\n8. React/Angular usually escape output by default unless explicitly bypassed\n9. Plaintext passwords in DB seed data are hardcoded credentials, not insecure deserialization\n10. Logging non-PII data like URLs or IDs is usually not a vulnerability\n11. LocalStorage with JSON.stringify is not insecure deserialization\n12. window.open() is not insecure cryptography\n\nCONFIDENCE SCORING:\n- 9-10: Strong evidence of a clear, actionable vulnerability with plausible exploitation\n- 8-9: Likely real vulnerability with good supporting evidence\n- 6-8: Suspicious and possibly valid, but context or exploitability is not fully established\n- 4-6: Likely not a clear vulnerability; evidence is limited or ambiguous\n- 1-4: Very likely not a clear vulnerability\n\nIMPORTANT LANGUAGE RULES:\n- Avoid absolute claims such as "definitely vulnerable", "definitely safe", or "proven false positive"\n- If filtering out a finding, describe it as "likely not a clear vulnerability" or\n  "insufficiently supported by the available evidence"\n- Be evidence-based and cautious in tone\n\nRESPONSE FORMAT (JSON):\n{\n    "keep_finding": true/false,\n    "confidence_score": 1-10,\n    "disposition": "retain_for_review or likely_not_clear_vulnerability",\n    "justification": "Brief explanation using cautious, non-absolute language",\n    "exclusion_reason": "If filtered out, explain why it is likely not a clear vulnerability"\n}\n'

    def _build_validation_content (self ,filename :str ,finding_type :str ,severity :str ,description :str ,vuln_code :str ,line :int ,code_context :str ,context_info :str )->str :
        return f'VALIDATE THIS FINDING:\n\nFile: {filename }\nLine: {line }\nSeverity: {severity }\nType: {finding_type }\n\nOriginal Description:\n{description }\n\nVulnerable Code Snippet:\n```\n{vuln_code }\n```\n\nCode Context (±10 lines):\n```\n{code_context }\n```\n\nProject Context:\n{context_info [:500 ]}\n\nAssess whether this appears to be a likely actionable vulnerability or more likely not a clear vulnerability.\nReturn JSON only.'

    def _get_code_context (self ,content :str ,line :int ,window :int =10 )->str :
        lines =content .splitlines ()
        if not lines :
            return ''
        line_idx =max (0 ,min (line -1 ,len (lines )-1 ))
        start =max (0 ,line_idx -window )
        end =min (len (lines ),line_idx +window +1 )
        context_lines =[]
        for i in range (start ,end ):
            prefix ='>>> 'if i ==line_idx else '    '
            context_lines .append (f'{prefix }{i +1 :4}| {lines [i ]}')
        return '\n'.join (context_lines )

class AgenticFindingsValidator (FindingsValidator ):

    def __init__ (self ,scan_id :str ,file_store :Dict [str ,str ],redis_client ,agentic_config :Optional [AgenticValidationConfig ]=None ,**kwargs ):
        super ().__init__ (**kwargs )
        self .scan_id =scan_id 
        self .file_store =file_store 
        self .redis_client =redis_client 
        self .agentic_config =agentic_config or AgenticValidationConfig ()
        self ._scan_tool_calls_used =0 

    def _build_validation_prompt (self )->str :
        base =super ()._build_validation_prompt ()
        agentic_section ='\n\nYOU ARE AN AI SECURITY VALIDATION AGENT:\nYou have access to tools that let you request more code and data before deciding. Use them when the snippet below is not enough to confidently keep or filter the finding.\n\nAVAILABLE TOOLS (call these when you need more context):\n- fetch_file(path [, start_line, end_line]) — get full file or a line range (saves tokens).\n- fetch_function(path, function_name) — get a single function’s source.\n- fetch_context_slice(path, line, window) — get ±N lines around a line.\n- trace_callers(function_name) — who calls this function (call graph).\n- trace_callees(function_name) — what this function calls.\n- lookup_sanitizers() — list of sanitizers in the project.\n- check_dead_code(path, function_name) — is this function dead/unreachable?\n- find_stdin_invokers(script_path) — for scripts that read stdin/pipe: list files that invoke this script and write to its stdin (use to check if URL/input is attacker-controlled).\n\nEVALUATE WHETHER CROSS-FILE CONTEXT IS NEEDED:\n- Consider: could this finding depend on data flow across files (sink in one file, source in another)? If the snippet only shows the sink and not who supplies the input, cross-file tools may be needed to decide if the finding is exploitable or a false positive.\n- If yes, choose the right tool: (1) Script that reads stdin/pipe (e.g. page.open(input), PhantomJS): use find_stdin_invokers(script_path) then fetch_file on returned paths to see if the written value is user-controlled. (2) Dangerous function/sink: use trace_callers(function_name) to see who calls it, then fetch_file or fetch_function on callers to see if they pass user input. (3) Need more lines or a helper: use fetch_context_slice or fetch_function.\n- Use the result to decide: attacker-controlled input -> finding may be valid; only server-controlled (constants, localhost URL, server-built path) -> likely false positive.\n\nWHEN TO CALL TOOLS:\n- Call tools when the code shown is insufficient to make a confident decision.\n- Examples: you see a sink but not whether a sanitizer wraps it; you need to evaluate cross-file data flow (who supplies the input); you need more lines or a helper in another file.\n- Do NOT call tools when the finding is already clearly weak or already clearly actionable with the visible code.\n- Hard limit: maximum 3 tool calls per finding; then render your verdict with what you have.\n\nTOOL SELECTION:\n- Taint/injection (SQLi, XSS, Path Traversal, SSRF, Command Injection): lookup_sanitizers first; then if input source is unclear, use find_stdin_invokers (for stdin-reading scripts) or trace_callers + fetch_file (for other sinks) to check if input is attacker-controlled.\n- IDOR / access-control: fetch_context_slice around the vulnerable line to see route/middleware/auth.\n- Any finding where who supplies the input matters: consider find_stdin_invokers, trace_callers, or fetch_file on files that reference this file.\n\nWhen you have enough context (or after your tool budget), you MUST respond with ONLY valid JSON: {"keep_finding": true|false, "confidence_score": number, "justification": "..."}. No prose, no markdown, no explanation outside the JSON. The response must parse as JSON so the system can use it.\n'
        return base +agentic_section 

    async def _validate_single_finding (self ,session :aiohttp .ClientSession ,finding_index :int ,finding :Dict [str ,Any ],filename :str ,file_content :str ,context_info :str )->ValidationResult :
        original_confidence =finding .get ('confidence_score',finding .get ('confidence',5.0 ))
        if original_confidence >=self .agentic_config .agentic_confidence_ceiling :
            logger .debug (f'[AGENTIC] Finding {finding_index } file={filename !r } confidence {original_confidence } >= {self .agentic_config .agentic_confidence_ceiling } ceiling — using static validation')
            return await super ()._validate_single_finding (session ,finding_index ,finding ,filename ,file_content ,context_info )
        if self ._scan_tool_calls_used >=self .agentic_config .max_total_tool_calls_per_scan :
            logger .info (f'[AGENTIC] Scan tool call budget exhausted ({self ._scan_tool_calls_used }/{self .agentic_config .max_total_tool_calls_per_scan }) — falling back to static for finding {finding_index } file={filename !r }')
            return await super ()._validate_single_finding (session ,finding_index ,finding ,filename ,file_content ,context_info )
        finding_type =finding .get ('type','Unknown')
        severity =finding .get ('severity','MEDIUM')
        description =finding .get ('description','')
        vuln_code =finding .get ('vulnerable_code','')
        line =finding .get ('line',0 )
        logger .info (f'[AGENTIC] Starting agentic validation file={filename !r } finding_index={finding_index } type={finding_type !r } line={line } (scan_id={self .scan_id })')
        push_event_to_log_server (self .scan_id ,'agent_start','Tier3Validator',{'agent_type':'validation','context_summary':{'file':filename ,'finding_index':finding_index ,'finding_type':finding_type ,'line':line }})
        executor =ToolExecutor (self .scan_id ,self .file_store ,self .redis_client )
        tool_calls_this_finding =0 
        code_context =self ._get_code_context (file_content ,line )
        tool_failures :List [str ]=[]
        any_tool_succeeded :bool =False 
        system_content =self ._build_validation_prompt ()
        user_content =self ._build_validation_content (filename =filename ,finding_type =finding_type ,severity =severity ,description =description ,vuln_code =vuln_code ,line =line ,code_context =code_context ,context_info =context_info )
        messages =[{'role':'system','content':system_content },{'role':'user','content':user_content }]
        push_event_to_log_server (self .scan_id ,'agent_prompt','Tier3Validator',{'prompt_full':f'[System]\n{system_content }\n\n[User]\n{user_content }','prompt_preview':user_content [:800 ]+'…'if len (user_content )>800 else user_content ,'filename':filename ,'finding_index':finding_index })
        last_exception :Optional [Exception ]=None 
        for attempt in range (self .max_retries +1 ):
            try :
                while tool_calls_this_finding <self .agentic_config .max_tool_calls_per_finding :
                    payload ={'model':SMART_MODEL ,'messages':messages ,'tools':VALIDATOR_TOOLS ,'tool_choice':'auto','temperature':0.1 ,'max_tokens':2048 }
                    async with session .post (self .api_url ,json =payload ,headers ={'Authorization':f'Bearer {OPENROUTER_API_KEY }'},timeout =aiohttp .ClientTimeout (total =self .timeout_seconds ))as resp :
                        if resp .status !=200 :
                            error_text =await resp .text ()
                            logger .error (f'[AGENTIC] API error file={filename !r } finding={finding_index } attempt {attempt +1 }: {resp .status } {error_text [:200 ]}')
                            if attempt <self .max_retries and resp .status in {408 ,429 ,500 ,502 ,503 ,504 }:
                                await asyncio .sleep (min (30 ,2 *(attempt +1 )))
                                break 
                            if self .agentic_config .fallback_to_static :
                                return await super ()._validate_single_finding (session ,finding_index ,finding ,filename ,file_content ,context_info )
                            return ValidationResult (finding_index =finding_index ,keep =True ,confidence =6.0 ,justification ='Agentic validation could not be completed due to an API error; retaining the finding for review without strong confirmation',exclusion_reason =None ,original_finding =finding )
                        result =await resp .json ()
                    choice =result .get ('choices',[{}])[0 ]
                    finish_reason =choice .get ('finish_reason','stop')
                    message =choice .get ('message',{})or {}
                    assistant_turn ={'role':'assistant'}
                    for key in ('content','tool_calls','thinking','reasoning','reasoning_content'):
                        if key in message :
                            assistant_turn [key ]=message [key ]
                    messages .append (assistant_turn )
                    response_text =(message .get ('content')or '').strip ()
                    tool_calls_list =message .get ('tool_calls')or []
                    if tool_calls_list :
                        response_text +='\n\n[Tool calls requested: '+', '.join (((tc .get ('function')or {}).get ('name','?')for tc in tool_calls_list ))+']'
                    push_event_to_log_server (self .scan_id ,'agent_response','Tier3Validator',{'response_full':response_text or '(no text; tool calls only)','response_preview':response_text [:600 ]+'…'if len (response_text )>600 else response_text ,'filename':filename ,'finding_index':finding_index ,'has_tool_calls':bool (tool_calls_list )})
                    if finish_reason =='tool_calls'or message .get ('tool_calls'):
                        tool_calls =message .get ('tool_calls',[])
                        tool_results =[]
                        for tc in tool_calls :
                            tc_id =tc .get ('id','')
                            tc_name_raw =tc .get ('function',{}).get ('name','')
                            tc_name =tc_name_raw .strip ()
                            try :
                                tc_args =json .loads (tc .get ('function',{}).get ('arguments','{}'))
                            except Exception :
                                tc_args ={}
                            _KNOWN_TOOLS ={'fetch_file','fetch_function','trace_callers','trace_callees','lookup_sanitizers','check_dead_code','fetch_context_slice','find_stdin_invokers'}
                            if tc_name not in _KNOWN_TOOLS :
                                logger .warning (f'[AGENTIC] Unknown tool name file={filename !r } finding={finding_index } raw_name={tc_name_raw !r } stripped_name={tc_name !r }. Available tools: {sorted (_KNOWN_TOOLS )}')
                                tool_result =f"Unknown tool '{tc_name }'. Available tools: {', '.join (sorted (_KNOWN_TOOLS ))}. Please use one of these tool names exactly."
                            else :
                                logger .info (f'[AGENTIC] Agent requested tool file={filename !r } finding={finding_index } tool={tc_name !r } args={tc_args } [budget: {tool_calls_this_finding +1 }/{self .agentic_config .max_tool_calls_per_finding }]')
                                agent_log =get_logger ()
                                if agent_log :
                                    agent_log .log_tool_call ('Tier3Validator',tc_name ,tc_args or {},filename )
                                push_event_to_log_server (self .scan_id ,'tool_call','Tier3Validator',{'tool_name':tc_name ,'tool_args':tc_args or {},'filename':filename })
                                tool_result =await executor .execute (tc_name ,tc_args )
                            _NOT_AVAILABLE_MARKERS =('File not found','not available','Tool error','Unknown tool','No callers found','not in the call graph')
                            _is_failure =any ((m in tool_result for m in _NOT_AVAILABLE_MARKERS ))
                            if _is_failure :
                                tool_failures .append (tc_name )
                            else :
                                any_tool_succeeded =True 
                            tool_results .append ({'role':'tool','tool_call_id':tc_id ,'content':tool_result })
                            tool_calls_this_finding +=1 
                            self ._scan_tool_calls_used +=1 
                            logger .info (f'[AGENTIC] Tool response file={filename !r } finding={finding_index } tool={tc_name !r } -> {_truncate_for_log (tool_result )}')
                            agent_log =get_logger ()
                            if agent_log :
                                agent_log .log_tool_result ('Tier3Validator',tc_name ,tool_result ,filename )
                            result_preview =tool_result if isinstance (tool_result ,str )else str (tool_result )
                            if len (result_preview )>500 :
                                result_preview =result_preview [:500 ]+'...'
                            push_event_to_log_server (self .scan_id ,'tool_result','Tier3Validator',{'tool_name':tc_name ,'result_preview':result_preview ,'filename':filename })
                        messages .extend (tool_results )
                        logger .info (f'[AGENTIC] Continuing validation file={filename !r } finding={finding_index } tool_calls_this_finding={tool_calls_this_finding }')
                        continue 
                    raw_content =self ._extract_message_text (result )
                    validation_data =self ._coerce_validation_payload (raw_content )
                    if validation_data is None :
                        full_raw =(raw_content or '').strip ()
                        if full_raw :
                            raw_preview =full_raw [:600 ]if len (full_raw )<=600 else full_raw [:600 ]+f' ... [{len (full_raw )} chars]'
                        else :
                            msg =(result .get ('choices')or [{}])[0 ].get ('message')or {}
                            raw_preview =f"Extracted empty. keys={list (msg .keys ())!r } content={str (msg .get ('content',''))[:400 ]}"
                        logger .warning (f'[AGENTIC] Parse failed file={filename !r } finding={finding_index }. Raw: {raw_preview }')
                        logger .info (f'[AGENTIC] Parse failed file={filename !r } finding={finding_index } full raw (1200 chars): {(full_raw or raw_preview )[:1200 ]}'+('...'if len (full_raw or raw_preview )>1200 else ''))
                        finding ['validation_status']='parse_failed'
                        original_conf =finding .get ('confidence_score',10.0 )
                        reduced =original_conf *0.3 
                        return ValidationResult (finding_index =finding_index ,keep =True ,confidence =reduced ,justification =f'Agentic validation response could not be parsed; retaining the finding with reduced confidence ({reduced :.1f}) because the result is inconclusive',exclusion_reason =None ,original_finding =finding )
                    normalized =self ._normalize_validation_fields (validation_data )
                    keep =normalized ['keep_finding']
                    confidence =normalized ['confidence_score']
                    justification =normalized ['justification']
                    exclusion_reason =normalized ['exclusion_reason']
                    if confidence <self .confidence_threshold :
                        if HIGH_RECALL_MODE :
                            keep =True 
                            finding ['validation_status']='validated_probable_fp'
                            finding ['_below_threshold_note']=f'Confidence {confidence :.1f} is below threshold {self .confidence_threshold :.1f} (agentic) but kept in high-recall mode.'
                            logger .debug (f'[AGENTIC] High-recall mode: keeping finding {finding_index } with confidence={confidence :.1f} (below threshold)')
                        else :
                            keep =False 
                            if not exclusion_reason :
                                exclusion_reason =f'Likely not a clear vulnerability: confidence {confidence :.1f} is below the retention threshold of {self .confidence_threshold :.1f}'
                    logger .info (f'[AGENTIC] Verdict file={filename !r } finding={finding_index } keep={keep } confidence={confidence } tool_calls_used={tool_calls_this_finding }')
                    if tool_calls_this_finding ==0 :
                        val_mode ='static_fallback'
                    elif tool_failures and any_tool_succeeded :
                        val_mode ='agentic_degraded'
                    elif any_tool_succeeded :
                        val_mode ='agentic_full'
                    else :
                        val_mode ='static_fallback'
                    push_event_to_log_server (self .scan_id ,'agent_complete','Tier3Validator',{'findings_count':1 if keep else 0 ,'errors':[],'execution_time_ms':0 ,'token_usage':0 ,'verdict_keep':keep ,'verdict_confidence':confidence ,'tool_calls_used':tool_calls_this_finding ,'file':filename ,'finding_index':finding_index ,'validation_mode':val_mode })
                    if attempt >0 :
                        logger .info (f'[AGENTIC] Finding {finding_index } file={filename !r } succeeded on attempt {attempt +1 }/{self .max_retries +1 } after retries.')
                    return ValidationResult (finding_index =finding_index ,keep =keep ,confidence =confidence ,justification =justification ,exclusion_reason =exclusion_reason if not keep else None ,original_finding =finding ,validation_metadata ={'validation_mode':val_mode ,'file_store_available':any_tool_succeeded ,'tool_failures':tool_failures })
                logger .info (f'[AGENTIC] Finding {finding_index } file={filename !r } hit per-finding tool cap ({self .agentic_config .max_tool_calls_per_finding }) — falling back to static')
                if self .agentic_config .fallback_to_static :
                    return await super ()._validate_single_finding (session ,finding_index ,finding ,filename ,file_content ,context_info )
                payload ={'model':SMART_MODEL ,'messages':messages +[{'role':'user','content':'Tool budget exhausted. Render your final JSON verdict now based on what you have.'}],'temperature':0.1 ,'response_format':{'type':'json_object'},'max_tokens':1024 }
                async with session .post (self .api_url ,json =payload ,headers ={'Authorization':f'Bearer {OPENROUTER_API_KEY }'},timeout =aiohttp .ClientTimeout (total =self .timeout_seconds ))as resp :
                    result =await resp .json ()
                raw_content =self ._extract_message_text (result )
                validation_data =self ._coerce_validation_payload (raw_content )
                if validation_data :
                    normalized =self ._normalize_validation_fields (validation_data )
                    keep =normalized ['keep_finding']
                    confidence =normalized ['confidence_score']
                    if confidence <self .confidence_threshold :
                        keep =False 
                    return ValidationResult (finding_index =finding_index ,keep =keep ,confidence =confidence ,justification =normalized ['justification'],exclusion_reason =normalized ['exclusion_reason']if not keep else None ,original_finding =finding )
                return ValidationResult (finding_index =finding_index ,keep =True ,confidence =5.0 ,justification ='Tool budget was exhausted and the final validation response was inconclusive; retaining the finding with reduced confidence',exclusion_reason =None ,original_finding =finding )
            except Exception as e :
                last_exception =e 
                error_str =str (e ).lower ()
                is_transient =any ((err in error_str for err in ['transfer','payload','connection','reset','eof']))or isinstance (e ,(aiohttp .ClientPayloadError ,aiohttp .ClientOSError ))
                if is_transient and attempt <self .max_retries :
                    wait =min (30 ,2 **attempt )
                    logger .warning (f'[AGENTIC] Network error finding {finding_index }, retrying in {wait }s: {e }')
                    await asyncio .sleep (wait )
                    continue 
                logger .error (f'[AGENTIC] Exception finding {finding_index }: {type (e ).__name__ }: {e }')
                if attempt <self .max_retries :
                    await asyncio .sleep (2 *(attempt +1 ))
                    continue 
        if self .agentic_config .fallback_to_static :
            logger .info (f'[AGENTIC] All retries exhausted for finding {finding_index } file={filename !r } — falling back to static')
            return await super ()._validate_single_finding (session ,finding_index ,finding ,filename ,file_content ,context_info )
        err_name =type (last_exception ).__name__ if last_exception else 'UnknownError'
        return ValidationResult (finding_index =finding_index ,keep =True ,confidence =5.5 ,justification =f'Agentic validation was inconclusive after retries ({err_name }); retaining the finding as a precaution rather than as a confirmed vulnerability',exclusion_reason =None ,original_finding =finding )

async def apply_two_phase_validation (session :aiohttp .ClientSession ,findings :List [Dict [str ,Any ]],filename :str ,file_content :str ,context_info :str ='',confidence_threshold :float =PHASE2_CONFIDENCE_THRESHOLD ,agentic_config :Optional [AgenticValidationConfig ]=None ,scan_id :Optional [str ]=None ,file_store :Optional [Dict [str ,str ]]=None ,redis_client =None )->Tuple [List [Dict [str ,Any ]],Dict [str ,Any ]]:
    use_agentic =agentic_config is not None and scan_id is not None and (file_store is not None )and (redis_client is not None )
    if use_agentic :
        validator =AgenticFindingsValidator (scan_id =scan_id ,file_store =file_store ,redis_client =redis_client ,agentic_config =agentic_config ,confidence_threshold =confidence_threshold )
    else :
        validator =FindingsValidator (confidence_threshold =confidence_threshold )
    kept ,excluded ,stats =await validator .validate_findings_parallel (session =session ,findings =findings ,filename =filename ,file_content =file_content ,context_info =context_info )
    summary ={'phase':'two_phase_validation','mode':'agentic'if use_agentic else 'static','threshold':confidence_threshold ,'original_count':stats ['total'],'kept_count':stats ['kept'],'excluded_count':stats ['excluded'],'parse_failures':stats .get ('parse_failures',0 ),'reduction_rate':stats ['reduction_rate'],'confidence_distribution':stats ['confidence_distribution'],'excluded_findings':[{'type':f .get ('type'),'line':f .get ('line'),'reason':f .get ('_validation',{}).get ('exclusion_reason'),'disposition':f .get ('_validation',{}).get ('disposition','likely_not_clear_vulnerability')}for f in excluded ],'parse_failed_findings':[{'type':f .get ('type'),'line':f .get ('line'),'warning':f .get ('_validation_warning','Validation was inconclusive due to a parse error')}for f in kept if f .get ('validation_status')=='parse_failed']}
    mode_counts ={'agentic_full':0 ,'agentic_degraded':0 ,'static_fallback':0 }
    any_store_healthy =False 
    for f in kept :
        vm =(f .get ('_validation')or {}).get ('validation_mode','static_fallback')
        mode_counts [vm ]=mode_counts .get (vm ,0 )+1 
        if (f .get ('_validation')or {}).get ('file_store_available'):
            any_store_healthy =True 
    summary ['validation_coverage']=mode_counts 
    summary ['file_store_healthy']=any_store_healthy 
    return (kept ,summary )
