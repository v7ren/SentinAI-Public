import asyncio 
import json 
import os 
import sys 
import threading 
from datetime import datetime 
from typing import Any ,Dict ,List ,Optional 
sys .path .insert (0 ,os .path .dirname (os .path .dirname (os .path .dirname (os .path .dirname (__file__ )))))
try :
    from backend .worker .core .log_server import log_interface ,LogServerInterface 
    LOG_SERVER_AVAILABLE =True 
except ImportError :
    LOG_SERVER_AVAILABLE =False 
    log_interface =None 
    LogServerInterface =None 
from backend .worker .core .agents .agent_logger import AgentLogger 

class LogBridge :

    def __init__ (self ,scan_id :str ):
        self .scan_id =scan_id 
        self .file_logger :Optional [AgentLogger ]=None 
        self .server_interface :Optional [LogServerInterface ]=None 
        self ._enabled =True 

    def set_file_logger (self ,logger :AgentLogger ):
        self .file_logger =logger 

    def set_server_interface (self ,interface :LogServerInterface ):
        self .server_interface =interface 

    def enable (self ):
        self ._enabled =True 

    def disable (self ):
        self ._enabled =False 

    def start_scan (self ,language :str ='',framework :str ='',file_count :int =0 ):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .log_scan_start (scan_id =self .scan_id ,language =language ,framework =framework ,file_count =file_count )

    def end_scan (self ,total_findings :int =0 ,total_time_ms :int =0 ):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .log_scan_complete (scan_id =self .scan_id ,total_findings =total_findings ,total_time_ms =total_time_ms )
        if self .file_logger :
            self .file_logger .finalize ({'total_findings':total_findings ,'total_time_ms':total_time_ms })

    def log_agent_start (self ,agent_name :str ,agent_type :str ,context :Optional [Dict ]=None ,config :Optional [Dict ]=None ):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .log_agent_start (agent_name =agent_name ,agent_type =agent_type ,scan_id =self .scan_id ,config =config or {})
        if self .file_logger :
            self .file_logger .log_agent_start (agent_name =agent_name ,agent_type =agent_type ,context =context or {},config =config or {})

    def log_agent_prompt (self ,agent_name :str ,prompt :str ,prompt_tokens :Optional [int ]=None ):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .log_agent_prompt (agent_name =agent_name ,prompt =prompt ,prompt_tokens =prompt_tokens ,scan_id =self .scan_id )
        if self .file_logger :
            self .file_logger .log_agent_prompt (agent_name =agent_name ,prompt =prompt ,prompt_tokens =prompt_tokens )

    def log_agent_response (self ,agent_name :str ,response :str ,response_tokens :Optional [int ]=None ,latency_ms :Optional [int ]=None ):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .log_agent_response (agent_name =agent_name ,response =response ,response_tokens =response_tokens ,latency_ms =latency_ms ,scan_id =self .scan_id )
        if self .file_logger :
            self .file_logger .log_agent_response (agent_name =agent_name ,response =response ,response_tokens =response_tokens ,latency_ms =latency_ms )

    def log_tool_call (self ,agent_name :str ,tool_name :str ,tool_args :Dict [str ,Any ]):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .log_tool_call (agent_name =agent_name ,tool_name =tool_name ,tool_args =tool_args ,scan_id =self .scan_id )
        if self .file_logger :
            self .file_logger ._write_entry ({'event_type':'tool_call','agent_name':agent_name ,'tool_name':tool_name ,'tool_args':tool_args })

    def log_tool_result (self ,agent_name :str ,tool_name :str ,tool_result :Any ):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .log_tool_result (agent_name =agent_name ,tool_name =tool_name ,tool_result =tool_result ,scan_id =self .scan_id )
        if self .file_logger :
            self .file_logger ._write_entry ({'event_type':'tool_result','agent_name':agent_name ,'tool_name':tool_name ,'result_preview':str (tool_result )[:500 ]})

    def log_agent_findings (self ,agent_name :str ,findings :List [Dict [str ,Any ]],parsing_errors :Optional [List [str ]]=None ):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .log_agent_findings (agent_name =agent_name ,findings =findings ,scan_id =self .scan_id )
        if self .file_logger :
            self .file_logger .log_agent_findings (agent_name =agent_name ,findings =findings ,parsing_errors =parsing_errors )

    def log_agent_complete (self ,agent_name :str ,execution_time_ms :int ,token_usage :int ,errors :List [str ],findings_count :int ):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .log_agent_complete (agent_name =agent_name ,execution_time_ms =execution_time_ms ,token_usage =token_usage ,errors =errors ,findings_count =findings_count ,scan_id =self .scan_id )
        if self .file_logger :
            self .file_logger .log_agent_complete (agent_name =agent_name ,execution_time_ms =execution_time_ms ,token_usage =token_usage ,errors =errors ,findings_count =findings_count )

    def log_phase_transition (self ,from_phase :str ,to_phase :str ,phase_data :Optional [Dict ]=None ):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .log_phase_transition (from_phase =from_phase ,to_phase =to_phase ,data =phase_data or {},scan_id =self .scan_id )
        if self .file_logger :
            self .file_logger .log_phase_transition (from_phase =from_phase ,to_phase =to_phase ,phase_data =phase_data or {})

    def log_deduplication (self ,input_findings :int ,output_findings :int ,duplicates_found :int ,merged_groups :List [Dict ]):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .broadcast_event (type ('Event',(),{'event_type':'deduplication','agent_name':'DeduplicationEngine','timestamp':datetime .utcnow ().isoformat (),'scan_id':self .scan_id ,'data':{'input_findings':input_findings ,'output_findings':output_findings ,'duplicates_found':duplicates_found }})())
        if self .file_logger :
            self .file_logger .log_deduplication (input_findings =input_findings ,output_findings =output_findings ,duplicates_found =duplicates_found ,merged_groups =merged_groups )

    def log_consensus_scoring (self ,findings_scored :int ,confidence_adjustments :List [Dict ]):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .broadcast_event (type ('Event',(),{'event_type':'consensus_scoring','agent_name':'ConsensusScorer','timestamp':datetime .utcnow ().isoformat (),'scan_id':self .scan_id ,'data':{'findings_scored':findings_scored ,'adjustments':confidence_adjustments }})())
        if self .file_logger :
            self .file_logger .log_consensus_scoring (findings_scored =findings_scored ,confidence_adjustments =confidence_adjustments )

    def log_skeptic_review (self ,findings_reviewed :int ,verdicts :List [Dict ],rejection_rate :float ):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .broadcast_event (type ('Event',(),{'event_type':'skeptic_review','agent_name':'SkepticAgent','timestamp':datetime .utcnow ().isoformat (),'scan_id':self .scan_id ,'data':{'findings_reviewed':findings_reviewed ,'verdicts':verdicts ,'rejection_rate':rejection_rate }})())
        if self .file_logger :
            self .file_logger .log_skeptic_review (findings_reviewed =findings_reviewed ,verdicts =verdicts ,rejection_rate =rejection_rate )

    def log_chain_combiner (self ,chains_created :int ,unchained_findings :int ,chains :List [Dict ]):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .broadcast_event (type ('Event',(),{'event_type':'chain_combiner','agent_name':'ChainCombiner','timestamp':datetime .utcnow ().isoformat (),'scan_id':self .scan_id ,'data':{'chains_created':chains_created ,'unchained_findings':unchained_findings }})())
        if self .file_logger :
            self .file_logger .log_chain_combiner (chains_created =chains_created ,unchained_findings =unchained_findings ,chains =chains )

    def log_attack_paths (self ,paths_simulated :int ,paths :List [Dict ]):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .broadcast_event (type ('Event',(),{'event_type':'attack_paths','agent_name':'AttackPathSimulator','timestamp':datetime .utcnow ().isoformat (),'scan_id':self .scan_id ,'data':{'paths_simulated':paths_simulated }})())
        if self .file_logger :
            self .file_logger .log_attack_paths (paths_simulated =paths_simulated ,paths =paths )

    def log_remediation (self ,remediations_generated :int ,remediations :List [Dict ]):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .broadcast_event (type ('Event',(),{'event_type':'remediation','agent_name':'RemediationAgent','timestamp':datetime .utcnow ().isoformat (),'scan_id':self .scan_id ,'data':{'remediations_generated':remediations_generated }})())
        if self .file_logger :
            self .file_logger .log_remediation (remediations_generated =remediations_generated ,remediations =remediations )

    def log_error (self ,agent_name :str ,error_type :str ,error_message :str ,stack_trace :Optional [str ]=None ):
        if not self ._enabled :
            return 
        if self .server_interface :
            self .server_interface .log_error (agent_name =agent_name ,error_type =error_type ,error_message =error_message ,stack_trace =stack_trace ,scan_id =self .scan_id )
        if self .file_logger :
            self .file_logger .log_error (agent_name =agent_name ,error_type =error_type ,error_message =error_message ,stack_trace =stack_trace )
_current_bridge :Optional [LogBridge ]=None 

def create_log_bridge (scan_id :str ,enable_file_logging :bool =True )->LogBridge :
    global _current_bridge 
    bridge =LogBridge (scan_id )
    if LOG_SERVER_AVAILABLE and log_interface :
        bridge .set_server_interface (log_interface )
    if enable_file_logging :
        try :
            file_logger =AgentLogger (scan_id )
            bridge .set_file_logger (file_logger )
        except Exception as e :
            print (f'[LogBridge] Warning: Could not create file logger: {e }')
    _current_bridge =bridge 
    return bridge 

def get_log_bridge ()->Optional [LogBridge ]:
    return _current_bridge 

def clear_log_bridge ():
    global _current_bridge 
    _current_bridge =None 

def log_tool_call (agent_name :str ,tool_name :str ,tool_args :Dict [str ,Any ]):
    bridge =get_log_bridge ()
    if bridge :
        bridge .log_tool_call (agent_name ,tool_name ,tool_args )

def log_tool_result (agent_name :str ,tool_name :str ,tool_result :Any ):
    bridge =get_log_bridge ()
    if bridge :
        bridge .log_tool_result (agent_name ,tool_name ,tool_result )
