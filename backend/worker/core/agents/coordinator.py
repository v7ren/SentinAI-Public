import asyncio 
from typing import Any 
from .base_agent import BaseAgent 
from .models import AgentContext ,AgentFinding ,AgentResult ,ScanMode 
from .agent_logger import get_logger 

class AgentCoordinator :

    def __init__ (self ,recon_agent :BaseAgent ,pattern_agent :BaseAgent ,threat_model_agent :BaseAgent ,specialist_agents :list [BaseAgent ],post_scan_agents :list [BaseAgent ]|None =None ):
        self .recon_agent =recon_agent 
        self .pattern_agent =pattern_agent 
        self .threat_model_agent =threat_model_agent 
        self .specialist_agents =specialist_agents 
        self .post_scan_agents =post_scan_agents or []

    async def run_scan (self ,context :AgentContext )->tuple [AgentResult ,AgentContext ]:
        logger =get_logger ()
        if logger :
            logger .log_phase_transition ('start','pre-scan',{'context':context .__dict__ })
        context =await self ._run_pre_scan_agents (context )
        if logger :
            logger .log_phase_transition ('pre-scan','specialist-detection',{'entry_points':len (context .entry_points )})
        specialist_results =await self ._run_specialist_agents_parallel (context )
        all_findings =self ._merge_specialist_results (specialist_results )
        if logger :
            logger .log_phase_transition ('specialist-detection','post-scan-synthesis',{'findings_count':len (all_findings )})
        synthesized_result =await self ._run_post_scan_synthesis (all_findings ,context )
        if logger :
            logger .log_phase_transition ('post-scan-synthesis','complete',{'final_findings':len (synthesized_result .findings )})
        return (synthesized_result ,context )

    async def _run_pre_scan_agents (self ,context :AgentContext )->AgentContext :
        recon_task =asyncio .to_thread (self .recon_agent .run ,context )
        pattern_task =asyncio .to_thread (self .pattern_agent .run ,context )
        recon_out ,pattern_result =await asyncio .gather (recon_task ,pattern_task )
        _recon_result ,entry_points =recon_out 
        context .entry_points =entry_points 
        if pattern_result .findings :
            pattern_data =pattern_result .findings [0 ].metadata .get ('arch_pattern',{})
            context .architecture_patterns =self ._dict_to_arch_pattern (pattern_data )
        threat_result =await asyncio .to_thread (self .threat_model_agent .run ,context )
        if threat_result .findings :
            threat_model =self ._build_threat_model_from_findings (threat_result .findings )
            context .threat_model =threat_model 
        return context 

    def _dict_to_arch_pattern (self ,data :dict )->Any :
        from .models import ArchPattern 
        return ArchPattern (pattern_type =data .get ('pattern_type','unknown'),middleware_order =data .get ('middleware_order',[]),auth_middleware_files =data .get ('auth_middleware_files',[]),orm_type =data .get ('orm_type'),template_engine =data .get ('template_engine'),cors_config =data .get ('cors_config'),service_layer_files =data .get ('service_layer_files',[]),repository_files =data .get ('repository_files',[]),di_container =data .get ('di_container'))

    def _build_threat_model_from_findings (self ,findings :list [AgentFinding ])->Any :
        from .models import ThreatModel ,ThreatScenario 
        threats =[ThreatScenario (description =f .finding_id ,priority =0.7 ,cwe_ids =[f .cwe_id ]if f .cwe_id else [])for f in findings ]
        return ThreatModel (stack_summary ='Detected Stack',high_priority_threats =threats ,framework_specific_sinks =[],framework_specific_sources =[],known_cve_patterns =[])

    async def _run_specialist_agents_parallel (self ,context :AgentContext )->list [AgentResult ]:
        if not self .specialist_agents :
            return []
        tasks =[asyncio .to_thread (agent .run ,context )for agent in self .specialist_agents ]
        results =await asyncio .gather (*tasks ,return_exceptions =True )
        valid_results =[]
        for result in results :
            if isinstance (result ,AgentResult ):
                valid_results .append (result )
            else :
                valid_results .append (AgentResult (agent_name =str (result .__class__ .__name__ )if hasattr (result ,'__class__')else 'Unknown',findings =[],errors =[str (result )]))
        return valid_results 

    def _merge_specialist_results (self ,results :list [AgentResult ])->list [AgentFinding ]:
        all_findings :list [AgentFinding ]=[]
        for result in results :
            if isinstance (result ,AgentResult ):
                all_findings .extend (result .findings )
        return all_findings 

    async def _run_post_scan_synthesis (self ,findings :list [AgentFinding ],context :AgentContext )->AgentResult :
        current_findings =findings 
        for agent in self .post_scan_agents :
            result =agent .run (AgentContext (scan_id =context .scan_id ,repo_path =context .repo_path ,language =context .language ,framework =context .framework ,file_contents =context .file_contents ,entry_points =context .entry_points ,architecture_patterns =context .architecture_patterns ,threat_model =context .threat_model ,call_graph =context .call_graph ,dependency_map =context .dependency_map ,sanitizer_registry =context .sanitizer_registry ,dead_code_map =context .dead_code_map ))
            current_findings =result .findings 
        return AgentResult (agent_name ='Coordinator',findings =current_findings ,metadata ={'total_specialist_agents':len (self .specialist_agents ),'pre_scan_agents':['ReconAgent','PatternAgent','ThreatModelAgent'],'post_scan_agents':[a .name for a in self .post_scan_agents ]})

    def create_context_from_indexer (self ,indexer_output :dict ,repo_path :str ,language :str ,framework :str ,scan_mode :ScanMode =ScanMode .FULL )->AgentContext :
        context =AgentContext (scan_id =indexer_output .get ('scan_id',''),repo_path =repo_path ,language =language ,framework =framework ,scan_mode =scan_mode ,call_graph =indexer_output .get ('call_graph',{}),dependency_map =indexer_output .get ('dependency_map',{}),file_contents =indexer_output .get ('file_contents',{}))
        return context 

class ScanResult :

    def __init__ (self ,findings :list [AgentFinding ],context :AgentContext ,execution_time_ms :int =0 ,total_tokens_used :int =0 ):
        self .findings =findings 
        self .context =context 
        self .execution_time_ms =execution_time_ms 
        self .total_tokens_used =total_tokens_used 

    def to_dict (self )->dict [str ,Any ]:
        return {'findings_count':len (self .findings ),'findings':[f .to_dict ()for f in self .findings ],'execution_time_ms':self .execution_time_ms ,'total_tokens_used':self .total_tokens_used ,'context':{'scan_id':self .context .scan_id ,'language':self .context .language ,'framework':self .context .framework ,'entry_points_count':len (self .context .entry_points ),'threat_model':self .context .threat_model is not None }}
