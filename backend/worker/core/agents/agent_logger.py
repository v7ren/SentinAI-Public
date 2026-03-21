import json 
import os 
import threading 
import time 
import uuid 
from datetime import datetime 
from pathlib import Path 
from typing import Any ,Dict ,List ,Optional 
from dataclasses import asdict ,is_dataclass 

class AgentLogger :
    LOG_DIR =Path (__file__ ).parent .parent .parent .parent /'worker'/'data'/'agent_logs'

    def __init__ (self ,scan_id :str ,file_count :int =0 ,language :str ='',framework :str =''):
        self .scan_id =scan_id 
        self .start_time =time .time ()
        self .log_id =f'{scan_id }_{int (self .start_time )}'
        self .LOG_DIR .mkdir (parents =True ,exist_ok =True )
        self .log_file =self .LOG_DIR /f'agent_log_{self .log_id }.jsonl'
        self .summary_file =self .LOG_DIR /f'agent_summary_{self .log_id }.json'
        self .entries :List [Dict [str ,Any ]]=[]
        self ._write_entry ({'event_type':'scan_start','agent_name':'coordinator','timestamp':datetime .utcnow ().isoformat (),'scan_id':scan_id ,'log_version':'1.0','file_count':file_count ,'language':language or '','framework':framework or ''})

    def _serialize_value (self ,value :Any )->Any :
        if is_dataclass (value ):
            return asdict (value )
        elif isinstance (value ,(list ,tuple )):
            return [self ._serialize_value (v )for v in value ]
        elif isinstance (value ,dict ):
            return {k :self ._serialize_value (v )for k ,v in value .items ()}
        elif isinstance (value ,(str ,int ,float ,bool ,type (None ))):
            return value 
        else :
            return str (value )

    def _push_to_log_server (self ,entry :Dict [str ,Any ])->None :
        try :
            from backend .worker .core .config import LOG_SERVER_URL 
            if not LOG_SERVER_URL :
                return 
            url =f'{LOG_SERVER_URL }/api/broadcast'
            payload ={'event_type':entry .get ('event_type','event'),'agent_name':entry .get ('agent_name',''),'scan_id':self .scan_id ,'data':entry }
            if 'timestamp'not in payload ['data']:
                payload ['data']=dict (payload ['data'],timestamp =datetime .utcnow ().isoformat ())
            body =json .dumps (payload ,default =str ).encode ('utf-8')
            try :
                from urllib .request import Request ,urlopen 
                req =Request (url ,data =body ,method ='POST',headers ={'Content-Type':'application/json'})
                urlopen (req ,timeout =2 )
            except Exception :
                pass 
        except Exception :
            pass 

    def _write_entry (self ,entry :Dict [str ,Any ]):
        entry ['seq']=len (self .entries )
        entry ['elapsed_ms']=int ((time .time ()-self .start_time )*1000 )
        if 'timestamp'not in entry :
            entry ['timestamp']=datetime .utcnow ().isoformat ()
        self .entries .append (entry )
        with open (self .log_file ,'a',encoding ='utf-8')as f :
            f .write (json .dumps (entry ,default =str )+'\n')
        try :
            from backend .worker .core .config import LOG_SERVER_URL 
            if LOG_SERVER_URL :
                threading .Thread (target =self ._push_to_log_server ,args =(dict (entry ),),daemon =True ).start ()
        except Exception :
            pass 

    def log_agent_start (self ,agent_name :str ,agent_type :str ,context :Dict [str ,Any ],config :Optional [Dict [str ,Any ]]=None ):
        entry ={'event_type':'agent_start','agent_name':agent_name ,'agent_type':agent_type ,'context_summary':self ._summarize_context (context ),'context_full':self ._serialize_value (context ),'config':config or {}}
        self ._write_entry (entry )

    def log_agent_prompt (self ,agent_name :str ,prompt :str ,prompt_tokens :Optional [int ]=None ):
        entry ={'event_type':'agent_prompt','agent_name':agent_name ,'prompt_length':len (prompt ),'prompt_tokens':prompt_tokens ,'prompt_preview':prompt [:2000 ]+'...'if len (prompt )>2000 else prompt ,'prompt_full':prompt }
        self ._write_entry (entry )

    def log_agent_response (self ,agent_name :str ,response :str ,response_tokens :Optional [int ]=None ,latency_ms :Optional [int ]=None ):
        entry ={'event_type':'agent_response','agent_name':agent_name ,'response_length':len (response ),'response_tokens':response_tokens ,'latency_ms':latency_ms ,'response_preview':response [:2000 ]+'...'if len (response )>2000 else response ,'response_full':response }
        self ._write_entry (entry )

    def log_agent_findings (self ,agent_name :str ,findings :List [Dict [str ,Any ]],parsing_errors :Optional [List [str ]]=None ):
        entry ={'event_type':'agent_findings','agent_name':agent_name ,'findings_count':len (findings ),'findings':[self ._serialize_value (f )for f in findings ],'parsing_errors':parsing_errors or []}
        self ._write_entry (entry )

    def log_agent_complete (self ,agent_name :str ,execution_time_ms :int ,token_usage :int ,errors :List [str ],findings_count :int ):
        entry ={'event_type':'agent_complete','agent_name':agent_name ,'execution_time_ms':execution_time_ms ,'token_usage':token_usage ,'errors':errors ,'findings_count':findings_count }
        self ._write_entry (entry )

    def log_deduplication (self ,input_findings :int ,output_findings :int ,duplicates_found :int ,merged_groups :List [Dict [str ,Any ]]):
        entry ={'event_type':'deduplication','agent_name':'DeduplicationEngine','input_findings':input_findings ,'output_findings':output_findings ,'duplicates_found':duplicates_found ,'deduplication_ratio':round ((1 -output_findings /input_findings )*100 ,2 )if input_findings >0 else 0 ,'merged_groups':merged_groups }
        self ._write_entry (entry )

    def log_consensus_scoring (self ,findings_scored :int ,confidence_adjustments :List [Dict [str ,Any ]]):
        entry ={'event_type':'consensus_scoring','agent_name':'ConsensusScorer','findings_scored':findings_scored ,'adjustments':confidence_adjustments }
        self ._write_entry (entry )

    def log_skeptic_review (self ,findings_reviewed :int ,verdicts :List [Dict [str ,Any ]],rejection_rate :float ):
        entry ={'event_type':'skeptic_review','agent_name':'SkepticAgent','findings_reviewed':findings_reviewed ,'verdicts':verdicts ,'rejection_rate':rejection_rate ,'confirmed':sum ((1 for v in verdicts if v .get ('verdict')=='confirmed')),'downgraded':sum ((1 for v in verdicts if v .get ('verdict')=='downgraded')),'rejected':sum ((1 for v in verdicts if v .get ('verdict')=='rejected'))}
        self ._write_entry (entry )

    def log_tool_call (self ,agent_name :str ,tool_name :str ,tool_args :Dict [str ,Any ],filename :str =''):
        entry ={'event_type':'tool_call','agent_name':agent_name ,'tool_name':tool_name ,'tool_args':tool_args ,'filename':filename }
        self ._write_entry (entry )

    def log_tool_result (self ,agent_name :str ,tool_name :str ,tool_result :Any ,filename :str =''):
        result_str =str (tool_result )if not isinstance (tool_result ,str )else tool_result 
        entry ={'event_type':'tool_result','agent_name':agent_name ,'tool_name':tool_name ,'result_preview':result_str [:500 ]+'...'if len (result_str )>500 else result_str ,'filename':filename }
        self ._write_entry (entry )

    def log_chain_combiner (self ,chains_created :int ,unchained_findings :int ,chains :List [Dict [str ,Any ]]):
        entry ={'event_type':'chain_combiner','agent_name':'ChainCombiner','chains_created':chains_created ,'unchained_findings':unchained_findings ,'chains':chains }
        self ._write_entry (entry )

    def log_attack_paths (self ,paths_simulated :int ,paths :List [Dict [str ,Any ]]):
        entry ={'event_type':'attack_paths','agent_name':'AttackPathSimulator','paths_simulated':paths_simulated ,'paths':paths }
        self ._write_entry (entry )

    def log_remediation (self ,remediations_generated :int ,remediations :List [Dict [str ,Any ]]):
        entry ={'event_type':'remediation','agent_name':'RemediationAgent','remediations_generated':remediations_generated ,'remediations':remediations }
        self ._write_entry (entry )

    def log_error (self ,agent_name :str ,error_type :str ,error_message :str ,stack_trace :Optional [str ]=None ):
        entry ={'event_type':'error','agent_name':agent_name ,'error_type':error_type ,'error_message':error_message ,'stack_trace':stack_trace }
        self ._write_entry (entry )

    def log_phase_transition (self ,from_phase :str ,to_phase :str ,phase_data :Optional [Dict [str ,Any ]]=None ):
        entry ={'event_type':'phase_transition','agent_name':'coordinator','from_phase':from_phase ,'to_phase':to_phase ,'phase_data':phase_data or {}}
        self ._write_entry (entry )

    def finalize (self ,final_stats :Optional [Dict [str ,Any ]]=None ):
        total_time_ms =int ((time .time ()-self .start_time )*1000 )
        stats =final_stats or {}
        total_findings =stats .get ('total_findings',0 )
        self ._write_entry ({'event_type':'scan_complete','agent_name':'coordinator','total_time_ms':total_time_ms ,'total_findings':total_findings ,'final_stats':stats })
        summary ={'scan_id':self .scan_id ,'log_id':self .log_id ,'start_time':datetime .fromtimestamp (self .start_time ).isoformat (),'end_time':datetime .utcnow ().isoformat (),'total_time_ms':total_time_ms ,'total_entries':len (self .entries ),'log_file':str (self .log_file ),'event_counts':self ._count_events (),'agent_summary':self ._summarize_agents (),'final_stats':final_stats or {}}
        with open (self .summary_file ,'w',encoding ='utf-8')as f :
            json .dump (summary ,f ,indent =2 ,default =str )
        return summary 

    def _summarize_context (self ,context :Dict [str ,Any ])->Dict [str ,Any ]:
        summary ={}
        if 'file_contents'in context :
            summary ['file_count']=len (context ['file_contents'])
        if 'entry_points'in context :
            summary ['entry_points_count']=len (context ['entry_points'])
        if 'call_graph'in context :
            summary ['call_graph_nodes']=len (context ['call_graph'])
        summary ['language']=context .get ('language','unknown')
        summary ['framework']=context .get ('framework','unknown')
        summary ['scan_mode']=context .get ('scan_mode','unknown')
        return summary 

    def _count_events (self )->Dict [str ,int ]:
        counts ={}
        for entry in self .entries :
            event_type =entry .get ('event_type','unknown')
            counts [event_type ]=counts .get (event_type ,0 )+1 
        return counts 

    def _summarize_agents (self )->Dict [str ,Dict [str ,Any ]]:
        agents ={}
        for entry in self .entries :
            if entry .get ('event_type')=='agent_complete':
                agent_name =entry .get ('agent_name','unknown')
                agents [agent_name ]={'execution_time_ms':entry .get ('execution_time_ms'),'token_usage':entry .get ('token_usage'),'findings_count':entry .get ('findings_count'),'errors':entry .get ('errors',[])}
        return agents 

    def get_log_file_path (self )->str :
        return str (self .log_file )

    def get_summary_file_path (self )->str :
        return str (self .summary_file )
_current_logger :Optional [AgentLogger ]=None 

def set_logger (logger :AgentLogger ):
    global _current_logger 
    _current_logger =logger 

def get_logger ()->Optional [AgentLogger ]:
    return _current_logger 

def clear_logger ():
    global _current_logger 
    _current_logger =None 

def push_event_to_log_server (scan_id :str ,event_type :str ,agent_name :str ,data :Dict [str ,Any ])->None :
    try :
        from backend .worker .core .config import LOG_SERVER_URL 
        if not LOG_SERVER_URL :
            return 
        entry =dict (data )
        entry .setdefault ('timestamp',datetime .utcnow ().isoformat ())
        payload ={'event_type':event_type ,'agent_name':agent_name ,'scan_id':scan_id ,'data':entry }
        body =json .dumps (payload ,default =str ).encode ('utf-8')
        import threading 

        def _post ():
            try :
                from urllib .request import Request ,urlopen 
                req =Request (f'{LOG_SERVER_URL }/api/broadcast',data =body ,method ='POST',headers ={'Content-Type':'application/json'})
                urlopen (req ,timeout =2 )
            except Exception :
                pass 
        threading .Thread (target =_post ,daemon =True ).start ()
    except Exception :
        pass 
