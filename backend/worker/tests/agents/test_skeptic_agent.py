import json 
import pytest 
from backend .worker .core .agents .skeptic_agent import SkepticAgent 
from backend .worker .core .agents .models import DeduplicatedFinding ,Exploitability ,Severity 
from backend .worker .tests .agents .fixtures import make_context 

def _make_dedup (finding_id :str ='f1',confidence :float =0.8 ,severity :Severity =Severity .HIGH )->DeduplicatedFinding :
    return DeduplicatedFinding (finding_id =finding_id ,agent_source ='injection_specialist',file_path ='app.py',line_start =10 ,line_end =12 ,function_name ='handler',vulnerability_class ='SQL Injection',cwe_id ='CWE-89',severity =severity ,confidence =confidence ,exploitability =Exploitability .CONFIRMED ,vulnerable_code ="query = 'SELECT' + user_id",reasoning ='String concat into SQL',contributing_agents =['injection_specialist'],duplicate_count =1 )

def test_confirms_genuine_sqli_finding ():
    client =__import__ ('backend.worker.core.llm_client',fromlist =['MockLLMClient']).MockLLMClient (responses =[json .dumps ({'verdict':'confirmed','reasoning':'Valid SQLi.','surviving_risk':None })])
    agent =SkepticAgent (llm_client =client )
    ctx =make_context (file_contents ={'app.py':"def handler():\n  query = 'SELECT' + user_id\n  db.execute(query)"})
    findings =[_make_dedup ()]
    result =agent .run (findings ,ctx )
    assert len (result )==1 
    assert result [0 ].confidence ==pytest .approx (0.9 ,rel =1e-05 )

def test_rejects_finding_with_sanitizer_applied ():
    client =__import__ ('backend.worker.core.llm_client',fromlist =['MockLLMClient']).MockLLMClient (responses =[json .dumps ({'verdict':'rejected','reasoning':'Sanitizer applied.','surviving_risk':None })])
    agent =SkepticAgent (llm_client =client )
    ctx =make_context ()
    findings =[_make_dedup ()]
    result =agent .run (findings ,ctx )
    assert len (result )==0 

def test_rejects_finding_in_dead_code ():
    client =__import__ ('backend.worker.core.llm_client',fromlist =['MockLLMClient']).MockLLMClient (responses =[json .dumps ({'verdict':'rejected','reasoning':'Dead code.','surviving_risk':None })])
    agent =SkepticAgent (llm_client =client )
    ctx =make_context ()
    from backend .worker .core .agents .models import DeadCodeRegion 
    ctx .dead_code_map ={'app.py':DeadCodeRegion ('app.py',1 ,50 ,'unreachable')}
    findings =[_make_dedup ()]
    result =agent .run (findings ,ctx )
    assert len (result )==0 

def test_downgrades_finding_with_framework_protection ():
    client =__import__ ('backend.worker.core.llm_client',fromlist =['MockLLMClient']).MockLLMClient (responses =[json .dumps ({'verdict':'downgraded','reasoning':'Framework mitigates.','surviving_risk':'Low risk remains.'})])
    agent =SkepticAgent (llm_client =client )
    ctx =make_context ()
    findings =[_make_dedup (severity =Severity .HIGH )]
    result =agent .run (findings ,ctx )
    assert len (result )==1 
    assert result [0 ].severity ==Severity .MEDIUM 

def test_confirmed_finding_confidence_boosted ():
    client =__import__ ('backend.worker.core.llm_client',fromlist =['MockLLMClient']).MockLLMClient (responses =[json .dumps ({'verdict':'confirmed','reasoning':'Real vuln.','surviving_risk':None })])
    agent =SkepticAgent (llm_client =client )
    ctx =make_context ()
    findings =[_make_dedup (confidence =0.7 )]
    result =agent .run (findings ,ctx )
    assert result [0 ].confidence ==pytest .approx (0.8 ,rel =1e-05 )

def test_rejected_finding_removed_from_output ():
    client =__import__ ('backend.worker.core.llm_client',fromlist =['MockLLMClient']).MockLLMClient (responses =[json .dumps ({'verdict':'confirmed','reasoning':'Ok','surviving_risk':None }),json .dumps ({'verdict':'rejected','reasoning':'FP','surviving_risk':None })])
    agent =SkepticAgent (llm_client =client )
    ctx =make_context ()
    findings =[_make_dedup ('f1'),_make_dedup ('f2')]
    result =agent .run (findings ,ctx )
    assert len (result )==1 
    assert result [0 ].finding_id =='f1'

def test_downgraded_finding_severity_reduced_one_level ():
    client =__import__ ('backend.worker.core.llm_client',fromlist =['MockLLMClient']).MockLLMClient (responses =[json .dumps ({'verdict':'downgraded','reasoning':'Mitigated.','surviving_risk':'Residual'})])
    agent =SkepticAgent (llm_client =client )
    ctx =make_context ()
    findings =[_make_dedup (severity =Severity .CRITICAL )]
    result =agent .run (findings ,ctx )
    assert result [0 ].severity ==Severity .HIGH 

def test_high_rejection_rate_logs_warning (caplog ):
    client =__import__ ('backend.worker.core.llm_client',fromlist =['MockLLMClient']).MockLLMClient (responses =[json .dumps ({'verdict':'rejected','reasoning':'No','surviving_risk':None })]*5 )
    agent =SkepticAgent (llm_client =client )
    ctx =make_context ()
    findings =[_make_dedup (finding_id =f'f{i }')for i in range (5 )]
    agent .run (findings ,ctx )
    assert 'rejection rate'in caplog .text .lower ()or '20'in caplog .text 

def test_no_llm_client_defaults_confirmed ():
    agent =SkepticAgent (llm_client =None )
    ctx =make_context ()
    findings =[_make_dedup ()]
    result =agent .run (findings ,ctx )
    assert len (result )==1 
    assert result [0 ].confidence ==pytest .approx (0.9 ,rel =1e-05 )
