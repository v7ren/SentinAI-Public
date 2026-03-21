import json 
import pytest 
from backend .worker .core .agents .specialists .cipher_design_specialist import CipherDesignSpecialist 
from backend .worker .core .llm_client import MockLLMClient 
from backend .worker .tests .agents .fixtures import make_context 

@pytest .fixture (autouse =True )
def _force_non_agentic_specialist (monkeypatch :pytest .MonkeyPatch )->None :
    monkeypatch .setattr ('backend.worker.core.agents.base_agent.AGENT_AGENTIC_ENABLED',False )

def test_parses_padding_oracle_finding ():
    payload ={'findings':[{'file_path':'crypto/tokens.py','line_start':40 ,'line_end':55 ,'function_name':'decrypt_cookie','vulnerability_class':'Padding Oracle','cwe_id':'CWE-327','owasp_category':'A02:2021','severity':'high','confidence':0.88 ,'exploitability':'likely','vulnerable_code':'except BadPadding:','reasoning':'Distinct exception path for invalid PKCS7 padding before MAC check','false_positive_indicators':[],'remediation_hint':'Use AES-GCM or constant-time decrypt-then-MAC'}]}
    client =MockLLMClient (responses =[json .dumps (payload )])
    agent =CipherDesignSpecialist (llm_client =client )
    result =agent .run (make_context (file_contents ={'crypto/tokens.py':'AES.new'}))
    assert len (result .findings )==1 
    assert result .findings [0 ].agent_source =='cipher_design_specialist'
    assert 'Padding'in result .findings [0 ].vulnerability_class 

def test_empty_findings ():
    client =MockLLMClient (responses =[json .dumps ({'findings':[]})])
    agent =CipherDesignSpecialist (llm_client =client )
    result =agent .run (make_context ())
    assert result .findings ==[]
