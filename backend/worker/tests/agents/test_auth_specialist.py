import json 
import pytest 
from backend .worker .core .agents .specialists .auth_specialist import AuthSpecialist 
from backend .worker .core .llm_client import MockLLMClient 
from backend .worker .tests .agents .fixtures import make_context ,make_arch_pattern ,make_entry_point 
AUTH_FINDING =json .dumps ({'findings':[{'file_path':'routes/admin.py','line_start':10 ,'line_end':12 ,'function_name':'admin_panel','vulnerability_class':'Missing Authentication','cwe_id':'CWE-306','owasp_category':'A07:2021','severity':'high','confidence':0.9 ,'exploitability':'confirmed','vulnerable_code':"@app.route('/admin')",'taint_source':None ,'taint_sink':None ,'taint_path':[],'reasoning':'Sensitive route has no auth','false_positive_indicators':[],'remediation_hint':'Add @login_required'}]})
JWT_NONE_FINDING =json .dumps ({'findings':[{'file_path':'auth/jwt.py','line_start':42 ,'line_end':44 ,'function_name':'verify_token','vulnerability_class':'JWT Algorithm Confusion','cwe_id':'CWE-347','severity':'critical','confidence':0.95 ,'exploitability':'confirmed','vulnerable_code':"jwt.decode(..., algorithms=['none'])",'reasoning':'Accepts none algorithm','false_positive_indicators':[],'remediation_hint':"Reject 'none' algorithm"}]})
NO_FINDINGS =json .dumps ({'findings':[]})

def test_detects_missing_auth_on_sensitive_route ():
    client =MockLLMClient (responses =[AUTH_FINDING ])
    agent =AuthSpecialist (llm_client =client )
    ep =make_entry_point (authentication_required =False )
    context =make_context (entry_points =[ep ],file_contents ={'routes/admin.py':"@app.route('/admin')\ndef admin_panel(): pass"})
    result =agent .run (context )
    assert len (result .findings )>=1 
    assert any (('Missing'in f .vulnerability_class or 'Authentication'in f .vulnerability_class for f in result .findings ))

def test_detects_jwt_none_algorithm ():
    client =MockLLMClient (responses =[JWT_NONE_FINDING ])
    agent =AuthSpecialist (llm_client =client )
    context =make_context (file_contents ={'auth/jwt.py':"jwt.decode(token, algorithms=['none'])"})
    result =agent .run (context )
    assert len (result .findings )==1 
    assert 'JWT'in result .findings [0 ].vulnerability_class or 'algorithm'in result .findings [0 ].reasoning .lower ()

def test_detects_session_fixation ():
    finding =json .dumps ({'findings':[{'file_path':'auth/login.py','line_start':1 ,'line_end':5 ,'function_name':'login','vulnerability_class':'Session Fixation','cwe_id':'CWE-384','severity':'medium','confidence':0.8 ,'exploitability':'likely','reasoning':'Session not regenerated','false_positive_indicators':[],'remediation_hint':'Regenerate session'}]})
    client =MockLLMClient (responses =[finding ])
    agent =AuthSpecialist (llm_client =client )
    result =agent .run (make_context ())
    assert len (result .findings )==1 
    assert result .findings [0 ].cwe_id =='CWE-384'

def test_detects_weak_password_hashing ():
    finding =json .dumps ({'findings':[{'file_path':'auth/utils.py','line_start':10 ,'line_end':12 ,'function_name':'hash_password','vulnerability_class':'Weak Password Hashing','cwe_id':'CWE-327','severity':'high','confidence':0.9 ,'exploitability':'confirmed','reasoning':'MD5 used','false_positive_indicators':[],'remediation_hint':'Use bcrypt'}]})
    client =MockLLMClient (responses =[finding ])
    agent =AuthSpecialist (llm_client =client )
    result =agent .run (make_context ())
    assert len (result .findings )==1 

def test_middleware_chain_included_in_prompt ():
    client =MockLLMClient (responses =[NO_FINDINGS ])
    agent =AuthSpecialist (llm_client =client )
    arch =make_arch_pattern (middleware_order =['cors','auth','router'])
    context =make_context (architecture_patterns =arch )
    agent .run (context )
    assert 'cors'in (client .last_prompt or '')and 'auth'in (client .last_prompt or '')

def test_handles_missing_architecture_patterns ():
    client =MockLLMClient (responses =[NO_FINDINGS ])
    agent =AuthSpecialist (llm_client =client )
    context =make_context (architecture_patterns =None )
    result =agent .run (context )
    assert 'No middleware chain'in (client .last_prompt or '')

def test_detects_missing_oauth_state_parameter ():
    finding =json .dumps ({'findings':[{'file_path':'oauth/callback.py','line_start':1 ,'line_end':10 ,'function_name':'callback','vulnerability_class':'Missing OAuth State Parameter','cwe_id':'CWE-352','severity':'high','confidence':0.85 ,'exploitability':'likely','reasoning':'No state param','false_positive_indicators':[],'remediation_hint':'Add state'}]})
    client =MockLLMClient (responses =[finding ])
    agent =AuthSpecialist (llm_client =client )
    result =agent .run (make_context ())
    assert len (result .findings )==1 
