import os 
import re 
import json 
from typing import Dict ,List ,Set ,Optional ,Tuple 
from ..redis_client import redis_client ,REDIS_AVAILABLE 
from ..config import logger 

class ContextSlicer :
    SINK_PATTERNS =['execute\\s*\\(','query\\s*\\(','raw\\s*\\(','eval\\s*\\(','exec\\s*\\(','render\\s*\\(','innerHTML\\s*=','system\\s*\\(','popen\\s*\\(','call\\s*\\(','check_output\\s*\\(','deserializ','loads?\\s*\\(','unpickle','send_mail','smtp','request\\.get\\s*\\(','request\\.post\\s*\\(','subprocess','open\\s*\\(','\\.write\\s*\\(']
    SINK_REGEX =re .compile ('|'.join (SINK_PATTERNS ),re .IGNORECASE )
    DANGEROUS_SINK_FUNCTIONS ={'subprocess.getoutput','subprocess.call','subprocess.run','subprocess.Popen','subprocess.check_output','subprocess.check_call','os.system','os.popen','os.execv','os.execve','commands.getoutput','commands.getstatusoutput','eval','exec','compile','pickle.loads','pickle.load','cPickle.loads','yaml.load','yaml.unsafe_load','render_template_string','render_template','execute','raw'}
    FULL_SOURCE_DEPTH =2 
    SIGNATURE_DEPTH =3 
    CROSS_FILE_TAINT_DEPTH =2 

    def __init__ (self ):
        self .call_graph :Dict ={}
        self .sanitizer_registry :Dict ={}
        self .dead_code_map :Dict ={}
        self .file_store :Dict [str ,str ]={}

    def _load_from_redis (self ,scan_id :str )->bool :
        if not REDIS_AVAILABLE :
            logger .warning (f'[{scan_id }] Redis not available, context slicing disabled')
            return False 
        try :
            call_graph_data =redis_client .get (f'{scan_id }:call_graph')
            if call_graph_data :
                self .call_graph =json .loads (call_graph_data )
            sanitizer_data =redis_client .get (f'{scan_id }:sanitizer_registry')
            if sanitizer_data :
                self .sanitizer_registry =json .loads (sanitizer_data )
            dead_code_data =redis_client .get (f'{scan_id }:dead_code_map')
            if dead_code_data :
                self .dead_code_map =json .loads (dead_code_data )
            file_store_data =redis_client .get (f'{scan_id }:file_store')
            if file_store_data :
                self .file_store =json .loads (file_store_data )
            return True 
        except Exception as e :
            logger .error (f'[{scan_id }] Failed to load context from Redis: {e }')
            return False 

    def _get_function_key (self ,filepath :str ,function_name :str )->str :
        return f'{filepath }::{function_name }'

    def _is_sanitizer (self ,function_key :str )->bool :
        full_map =self .sanitizer_registry .get ('full_map',{})
        if function_key in full_map :
            role =full_map [function_key ].get ('role','')
            return role =='SANITIZER'
        return False 

    def _is_sink (self ,function_key :str )->bool :
        if '::'in function_key :
            func_name =function_key .split ('::')[1 ]
            if self .SINK_REGEX .search (func_name ):
                return True 
        return False 

    def _is_dead_code (self ,function_key :str )->bool :
        if function_key in self .dead_code_map :
            return self .dead_code_map [function_key ].get ('is_dead',False )
        return False 

    def _is_test_only (self ,function_key :str )->bool :
        if function_key in self .dead_code_map :
            return self .dead_code_map [function_key ].get ('is_test_only',False )
        return False 

    def _contains_dangerous_sink (self ,function_key :str ,project_path :str ,depth :int =0 ,visited :Optional [Set [str ]]=None )->Tuple [bool ,List [Dict ]]:
        if visited is None :
            visited =set ()
        if function_key in visited or depth >self .CROSS_FILE_TAINT_DEPTH :
            return (False ,[])
        visited .add (function_key )
        if function_key not in self .call_graph :
            return (False ,[])
        func_data =self .call_graph [function_key ]
        func_source =self ._get_function_source (function_key ,project_path )or ''
        sinks_found =[]
        for sink_func in self .DANGEROUS_SINK_FUNCTIONS :
            if sink_func in func_source :
                for line_num ,line in enumerate (func_source .splitlines (),func_data .get ('start_line',1 )):
                    if sink_func in line :
                        sinks_found .append ({'sink_function':sink_func ,'line':line_num ,'line_content':line .strip ()[:150 ],'in_function':function_key ,'depth':depth })
                        break 
        calls =func_data .get ('calls',[])
        for callee_key in calls :
            if callee_key in visited :
                continue 
            has_sink ,chain_sinks =self ._contains_dangerous_sink (callee_key ,project_path ,depth +1 ,visited )
            if has_sink :
                for sink_info in chain_sinks :
                    sink_info ['chain']=[function_key ]+sink_info .get ('chain',[])
                sinks_found .extend (chain_sinks )
        return (len (sinks_found )>0 ,sinks_found )

    def find_cross_file_taint_chains (self ,entry_function :str ,tainted_args :List [str ],project_path :str )->List [Dict ]:
        chains =[]
        if entry_function not in self .call_graph :
            return chains 
        func_data =self .call_graph [entry_function ]
        calls =func_data .get ('calls',[])
        for callee_key in calls :
            has_sink ,sink_info_list =self ._contains_dangerous_sink (callee_key ,project_path ,depth =0 ,visited =set ())
            if has_sink :
                for sink_info in sink_info_list :
                    chains .append ({'entry_point':entry_function ,'intermediate_function':callee_key ,'final_sink':sink_info ['sink_function'],'sink_line':sink_info ['line'],'sink_content':sink_info ['line_content'],'chain_depth':sink_info ['depth']+1 ,'tainted_args':tainted_args ,'full_chain':[entry_function ,callee_key ]+sink_info .get ('chain',[])})
        return chains 

    def _get_function_source (self ,function_key :str ,project_path :str )->Optional [str ]:
        if '::'not in function_key :
            return None 
        filepath ,func_name =function_key .split ('::',1 )
        content =self .file_store .get (filepath )
        if content is None and project_path :
            full_path =os .path .join (project_path ,filepath )
            if not os .path .exists (full_path ):
                return None 
            try :
                with open (full_path ,'r',encoding ='utf-8',errors ='ignore')as f :
                    content =f .read ()
            except Exception as e :
                logger .warning (f'Failed to get source for {function_key }: {e }')
                return None 
        try :
            lines =(content or '').splitlines ()
            if function_key not in self .call_graph :
                return None 
            func_data =self .call_graph [function_key ]
            start_line =func_data .get ('start_line',1 )
            end_line =func_data .get ('end_line',start_line +50 )
            func_lines =lines [start_line -1 :end_line ]
            return '\n'.join (func_lines )
        except Exception as e :
            logger .warning (f'Failed to get source for {function_key }: {e }')
            return None 

    def _get_function_signature (self ,function_key :str )->Optional [Dict ]:
        if function_key not in self .call_graph :
            return None 
        func_data =self .call_graph [function_key ]
        return {'name':func_data .get ('name'),'file':func_data .get ('file'),'line':func_data .get ('start_line'),'is_entry_point':func_data .get ('is_entry_point',False ),'is_test':func_data .get ('is_test',False )}

    def _get_callers (self ,function_key :str ,max_depth :int =5 )->List [Dict ]:
        if function_key not in self .call_graph :
            return []
        func_data =self .call_graph [function_key ]
        called_by =func_data .get ('called_by',[])
        callers =[]
        for caller_key in called_by [:max_depth ]:
            caller_sig =self ._get_function_signature (caller_key )
            if caller_sig :
                callers .append (caller_sig )
        return callers 

    def _get_callees_with_context (self ,function_key :str ,project_path :str ,depth :int =0 ,visited :Optional [Set [str ]]=None )->List [Dict ]:
        if visited is None :
            visited =set ()
        if function_key in visited :
            return []
        visited .add (function_key )
        if function_key not in self .call_graph :
            return []
        func_data =self .call_graph [function_key ]
        calls =func_data .get ('calls',[])
        callees =[]
        for callee_key in calls :
            if callee_key in visited :
                continue 
            role ='OTHER'
            source =None 
            if self ._is_sanitizer (callee_key ):
                role ='SANITIZER'
                if depth <self .FULL_SOURCE_DEPTH :
                    source =self ._get_function_source (callee_key ,project_path )
            elif self ._is_sink (callee_key ):
                role ='SINK'
                if depth <self .FULL_SOURCE_DEPTH :
                    source =self ._get_function_source (callee_key ,project_path )
            sig =self ._get_function_signature (callee_key )
            if sig :
                callee_info ={'key':callee_key ,'role':role ,'signature':sig ,'source':source }
                callees .append (callee_info )
                if depth <self .SIGNATURE_DEPTH :
                    sub_callees =self ._get_callees_with_context (callee_key ,project_path ,depth +1 ,visited )
        return callees 

    def slice_for_scan (self ,filepath :str ,function_name :str ,scan_id :str ,project_path :str ,tainted_variables :Optional [List [Dict ]]=None )->Dict :
        if not self ._load_from_redis (scan_id ):
            return {'callers':[],'security_callees':[],'function_key':None ,'is_entry_point':False ,'is_dead':False ,'is_test_only':False ,'cross_file_taint_chains':[]}
        function_key =self ._get_function_key (filepath ,function_name )
        is_entry_point =False 
        is_dead =False 
        is_test_only =False 
        if function_key in self .call_graph :
            func_data =self .call_graph [function_key ]
            is_entry_point =func_data .get ('is_entry_point',False )
            is_dead =self ._is_dead_code (function_key )
            is_test_only =self ._is_test_only (function_key )
        callers =self ._get_callers (function_key ,max_depth =5 )
        security_callees =self ._get_callees_with_context (function_key ,project_path ,depth =0 ,visited =set ())
        cross_file_taint_chains =[]
        if tainted_variables and is_entry_point :
            tainted_arg_names =[v .get ('variable')for v in tainted_variables if v .get ('variable')]
            if tainted_arg_names :
                cross_file_taint_chains =self .find_cross_file_taint_chains (function_key ,tainted_arg_names ,project_path or '')
                if cross_file_taint_chains :
                    logger .info (f'Cross-file taint chains found: {len (cross_file_taint_chains )}')
        return {'function_key':function_key ,'is_entry_point':is_entry_point ,'is_dead':is_dead ,'is_test_only':is_test_only ,'callers':callers ,'security_callees':security_callees ,'cross_file_taint_chains':cross_file_taint_chains }

    def format_for_prompt (self ,slice_data :Dict )->str :
        lines =['## Call Chain Context','']
        lines .append ('### Who calls this function:')
        if slice_data .get ('callers'):
            for caller in slice_data ['callers']:
                entry_marker =' [ENTRY POINT]'if caller .get ('is_entry_point')else ''
                test_marker =' [TEST ONLY]'if caller .get ('is_test_only')else ''
                lines .append (f"- {caller ['name']} ({caller ['file']}:{caller ['line']}){entry_marker }{test_marker }")
        else :
            lines .append ('- No callers found (may be an entry point or dead code)')
        lines .append ('')
        security_callees =slice_data .get ('security_callees',[])
        if security_callees :
            lines .append ('### Security-Relevant Callees:')
            for callee in security_callees :
                role =callee .get ('role','OTHER')
                sig =callee .get ('signature',{})
                source =callee .get ('source')
                lines .append (f"\n[ROLE: {role }] {sig .get ('name')} ({sig .get ('file')}:{sig .get ('line')})")
                if source :
                    lines .append ('```')
                    lines .append (source [:500 ])
                    lines .append ('```')
                else :
                    lines .append (f"  Signature: {sig .get ('name')}()")
        cross_file_chains =slice_data .get ('cross_file_taint_chains',[])
        if cross_file_chains :
            lines .append ('')
            lines .append ('### CROSS-FILE TAINT CHAINS DETECTED (CRITICAL):')
            lines .append ('User input flows from this function to dangerous sinks in other files:')
            for i ,chain in enumerate (cross_file_chains ,1 ):
                lines .append (f'\n**Chain {i }:**')
                lines .append (f"- Entry: {chain ['entry_point']}")
                lines .append (f"- Intermediate: {chain ['intermediate_function']}")
                lines .append (f"- Final Sink: {chain ['final_sink']} (line {chain ['sink_line']})")
                lines .append (f"- Tainted Args: {', '.join (chain ['tainted_args'])}")
                lines .append (f"- Full Chain: {' -> '.join (chain ['full_chain'])}")
                lines .append (f"- VULNERABILITY: **{chain ['final_sink'].upper ()} with unsanitized user input**")
            lines .append ('')
            lines .append ('> **ALERT**: The entry point function passes user-controlled input to another function which eventually reaches a dangerous execution sink. This is a HIGH SEVERITY cross-file taint vulnerability.')
        return '\n'.join (lines )
