import asyncio 
from unittest .mock import MagicMock 
import pytest 
from backend .worker .core .agents .base_agent import BaseAgent 
from backend .worker .core .agents .coordinator import AgentCoordinator ,ScanResult 
from backend .worker .core .agents .models import AgentContext ,AgentFinding ,AgentResult ,ScanMode 

class MockAgent (BaseAgent ):

    def __init__ (self ,name :str ,findings :list [AgentFinding ]|None =None ):
        super ().__init__ (name =name ,llm_client =None )
        self .findings =findings or []

    def build_prompt (self ,context :AgentContext )->str :
        return f'Mock prompt for {self .name }'

    def parse_response (self ,response :str )->list [AgentFinding ]:
        return self .findings 

class TestAgentCoordinator :

    @pytest .fixture 
    def mock_recon_agent (self ):
        agent =MockAgent (name ='ReconAgent')
        agent .run =MagicMock (return_value =(AgentResult ('ReconAgent',[]),[]))
        return agent 

    @pytest .fixture 
    def mock_pattern_agent (self ):
        agent =MockAgent (name ='PatternAgent')
        agent .run =MagicMock (return_value =AgentResult ('PatternAgent',[]))
        return agent 

    @pytest .fixture 
    def mock_threat_agent (self ):
        agent =MockAgent (name ='ThreatModelAgent')
        agent .run =MagicMock (return_value =AgentResult ('ThreatModelAgent',[]))
        return agent 

    @pytest .fixture 
    def mock_specialist_agents (self ):
        agent1 =MockAgent (name ='InjectionSpecialist',findings =[AgentFinding (finding_id ='find-1',agent_source ='InjectionSpecialist',file_path ='api.py',line_start =10 ,line_end =15 ,vulnerability_class ='SQL Injection')])
        agent2 =MockAgent (name ='AuthSpecialist',findings =[AgentFinding (finding_id ='find-2',agent_source ='AuthSpecialist',file_path ='auth.py',line_start =20 ,line_end =25 ,vulnerability_class ='Authentication Bypass')])
        return [agent1 ,agent2 ]

    @pytest .fixture 
    def coordinator (self ,mock_recon_agent ,mock_pattern_agent ,mock_threat_agent ,mock_specialist_agents ):
        return AgentCoordinator (recon_agent =mock_recon_agent ,pattern_agent =mock_pattern_agent ,threat_model_agent =mock_threat_agent ,specialist_agents =mock_specialist_agents )

    @pytest .fixture 
    def mock_context (self ):
        return AgentContext (scan_id ='test-scan',repo_path ='/test/repo',language ='python',framework ='flask',file_contents ={'api.py':'test'})

    def test_coordinator_init (self ,coordinator ):
        assert coordinator .recon_agent .name =='ReconAgent'
        assert coordinator .pattern_agent .name =='PatternAgent'
        assert coordinator .threat_model_agent .name =='ThreatModelAgent'
        assert len (coordinator .specialist_agents )==2 

    @pytest .mark .asyncio 
    async def test_run_scan (self ,coordinator ,mock_context ):
        result ,context =await coordinator .run_scan (mock_context )
        assert result .agent_name =='Coordinator'
        assert len (result .findings )==2 
        assert context .language =='python'

    @pytest .mark .asyncio 
    async def test_run_scan_no_specialists (self ,mock_recon_agent ,mock_pattern_agent ,mock_threat_agent ):
        coordinator =AgentCoordinator (recon_agent =mock_recon_agent ,pattern_agent =mock_pattern_agent ,threat_model_agent =mock_threat_agent ,specialist_agents =[])
        mock_context =AgentContext (scan_id ='test-scan',repo_path ='/test',language ='python',framework ='flask')
        result ,context =await coordinator .run_scan (mock_context )
        assert len (result .findings )==0 

    @pytest .mark .asyncio 
    async def test_run_pre_scan_agents (self ,coordinator ,mock_context ):
        context =await coordinator ._run_pre_scan_agents (mock_context )
        assert context .entry_points ==[]
        assert context .language =='python'

    @pytest .mark .asyncio 
    async def test_run_specialist_agents_parallel (self ,coordinator ,mock_context ):
        results =await coordinator ._run_specialist_agents_parallel (mock_context )
        assert len (results )==2 

    def test_merge_specialist_results (self ,coordinator ):
        result1 =AgentResult (agent_name ='Agent1',findings =[AgentFinding (finding_id ='find-1',agent_source ='Agent1',file_path ='api.py',line_start =1 ,line_end =10 ,vulnerability_class ='Test')])
        result2 =AgentResult (agent_name ='Agent2',findings =[AgentFinding (finding_id ='find-2',agent_source ='Agent2',file_path ='auth.py',line_start =1 ,line_end =10 ,vulnerability_class ='Test')])
        merged =coordinator ._merge_specialist_results ([result1 ,result2 ])
        assert len (merged )==2 
        assert merged [0 ].finding_id =='find-1'
        assert merged [1 ].finding_id =='find-2'

    def test_create_context_from_indexer (self ):
        coordinator =AgentCoordinator (recon_agent =MagicMock (),pattern_agent =MagicMock (),threat_model_agent =MagicMock (),specialist_agents =[])
        indexer_output ={'scan_id':'scan-123','call_graph':{'func1':['func2']},'dependency_map':{'api.py':['utils.py']},'file_contents':{'api.py':'test'}}
        context =coordinator .create_context_from_indexer (indexer_output =indexer_output ,repo_path ='/test/repo',language ='python',framework ='flask',scan_mode =ScanMode .FULL )
        assert context .scan_id =='scan-123'
        assert context .language =='python'
        assert context .framework =='flask'
        assert context .call_graph =={'func1':['func2']}

class TestScanResult :

    def test_scan_result_creation (self ):
        finding =AgentFinding (finding_id ='test-uuid',agent_source ='TestAgent',file_path ='test.py',line_start =1 ,line_end =10 ,vulnerability_class ='Test')
        context =AgentContext (scan_id ='test-scan',repo_path ='/test',language ='python',framework ='flask')
        result =ScanResult (findings =[finding ],context =context ,execution_time_ms =1500 ,total_tokens_used =5000 )
        assert result .findings_count ==1 
        assert result .execution_time_ms ==1500 
        assert result .total_tokens_used ==5000 

    def test_scan_result_to_dict (self ):
        finding =AgentFinding (finding_id ='test-uuid',agent_source ='TestAgent',file_path ='test.py',line_start =1 ,line_end =10 ,vulnerability_class ='Test')
        context =AgentContext (scan_id ='test-scan',repo_path ='/test',language ='python',framework ='flask')
        result =ScanResult (findings =[finding ],context =context )
        result_dict =result .to_dict ()
        assert result_dict ['findings_count']==1 
        assert 'findings'in result_dict 
        assert result_dict ['context']['language']=='python'
if __name__ =='__main__':
    pytest .main ([__file__ ,'-v'])
