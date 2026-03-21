import pytest 
from backend .worker .core .agents .base_agent import BaseAgent 
from backend .worker .core .agents .models import AgentContext ,AgentFinding 

class MockAgent (BaseAgent ):

    def __init__ (self ,*args ,**kwargs ):
        super ().__init__ (*args ,**kwargs )
        self .prompt_called =False 
        self .response_data =None 

    def build_prompt (self ,context :AgentContext )->str :
        self .prompt_called =True 
        return f'Prompt for {self .name }\n\nContext: scan_id={context .scan_id }'

    def parse_response (self ,response :str )->list [AgentFinding ]:
        if self .response_data :
            return [AgentFinding .from_dict (self .response_data )]
        return []

class TestBaseAgent :

    @pytest .fixture 
    def mock_agent (self ):
        return MockAgent (name ='MockAgent',llm_client =None ,max_retries =3 ,timeout_seconds =120 )

    @pytest .fixture 
    def mock_context (self ):
        return AgentContext (scan_id ='test-scan',repo_path ='/test/repo',language ='python',framework ='flask')

    def test_base_agent_init (self ):
        agent =MockAgent (name ='TestAgent',llm_client =None ,max_retries =5 ,timeout_seconds =300 )
        assert agent .name =='TestAgent'
        assert agent .max_retries ==5 
        assert agent .timeout_seconds ==300 

    def test_build_prompt (self ,mock_agent ,mock_context ):
        prompt =mock_agent .build_prompt (mock_context )
        assert mock_agent .prompt_called is True 
        assert 'Prompt for MockAgent'in prompt 
        assert 'test-scan'in prompt 

    def test_run_with_mock_response (self ,mock_agent ,mock_context ):
        mock_agent .response_data ={'finding_id':'test-uuid','agent_source':'MockAgent','file_path':'test.py','line_start':1 ,'line_end':10 ,'vulnerability_class':'Test'}
        result =mock_agent .run (mock_context )
        assert len (result .findings )==1 
        assert result .findings [0 ].finding_id =='test-uuid'
        assert result .errors ==[]

    def test_run_with_empty_findings (self ,mock_agent ,mock_context ):
        mock_agent .response_data =None 
        result =mock_agent .run (mock_context )
        assert len (result .findings )==0 
        assert result .agent_name =='MockAgent'

    def test_validate_finding_valid (self ,mock_agent ):
        finding =AgentFinding (finding_id ='test-uuid',agent_source ='TestAgent',file_path ='test.py',line_start =1 ,line_end =10 ,vulnerability_class ='Test')
        assert mock_agent .validate_finding (finding )is True 

    def test_validate_finding_missing_required (self ,mock_agent ):
        finding =AgentFinding (finding_id ='',agent_source ='TestAgent',file_path ='test.py',line_start =1 ,line_end =10 ,vulnerability_class ='Test')
        assert mock_agent .validate_finding (finding )is False 

    def test_adjust_confidence_increase (self ,mock_agent ):
        finding =AgentFinding (finding_id ='test-uuid',agent_source ='TestAgent',file_path ='test.py',line_start =1 ,line_end =10 ,vulnerability_class ='Test',confidence =0.5 )
        mock_agent .adjust_confidence (finding ,0.3 )
        assert finding .confidence ==0.8 

    def test_adjust_confidence_clamp_max (self ,mock_agent ):
        finding =AgentFinding (finding_id ='test-uuid',agent_source ='TestAgent',file_path ='test.py',line_start =1 ,line_end =10 ,vulnerability_class ='Test',confidence =0.9 )
        mock_agent .adjust_confidence (finding ,0.3 )
        assert finding .confidence ==1.0 

    def test_adjust_confidence_clamp_min (self ,mock_agent ):
        finding =AgentFinding (finding_id ='test-uuid',agent_source ='TestAgent',file_path ='test.py',line_start =1 ,line_end =10 ,vulnerability_class ='Test',confidence =0.1 )
        mock_agent .adjust_confidence (finding ,-0.3 )
        assert finding .confidence ==0.0 

class TestBaseAgentLLMIntegration :

    @pytest .fixture 
    def mock_llm_client (self ):

        class MockClient :

            def complete (self ,prompt :str ,timeout :int )->str :
                return '{"finding_id": "mock-uuid", "agent_source": "TestAgent", "file_path": "test.py", "line_start": 1, "line_end": 10, "vulnerability_class": "Mock"}'
        return MockClient ()

    @pytest .fixture 
    def agent_with_llm (self ,mock_llm_client ):

        class TestAgent (BaseAgent ):

            def build_prompt (self ,context ):
                return 'test prompt'

            def parse_response (self ,response ):
                import json 
                data =json .loads (response )
                return [AgentFinding .from_dict (data )]
        return TestAgent (name ='TestAgent',llm_client =mock_llm_client ,max_retries =0 ,timeout_seconds =30 )

    def test_llm_call_success (self ,agent_with_llm ):
        context =AgentContext (scan_id ='test-scan',repo_path ='/test',language ='python',framework ='flask')
        result =agent_with_llm .run (context )
        assert len (result .findings )==1 
        assert result .findings [0 ].finding_id =='mock-uuid'
        assert result .errors ==[]

    def test_llm_call_failure_no_retries (self ,agent_with_llm ):

        class FailingClient :

            def complete (self ,prompt :str ,timeout :int )->str :
                raise ConnectionError ('LLM service unavailable')
        agent_with_llm .llm_client =FailingClient ()
        agent_with_llm .max_retries =0 
        context =AgentContext (scan_id ='test-scan',repo_path ='/test',language ='python',framework ='flask')
        result =agent_with_llm .run (context )
        assert len (result .findings )==0 
        assert len (result .errors )==1 
        assert 'FailingClient'in result .errors [0 ]
if __name__ =='__main__':
    pytest .main ([__file__ ,'-v'])
