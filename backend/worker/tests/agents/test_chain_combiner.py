import pytest 
from backend .worker .core .agents .chain_combiner import ChainCombiner ,_chainable 
from backend .worker .core .agents .models import DeduplicatedFinding ,Exploitability ,Severity 
from backend .worker .tests .agents .fixtures import make_context ,make_entry_point ,make_arch_pattern 

def _make_dedup (finding_id :str ='f1',vulnerability_class :str ='SQL Injection',taint_source :str |None =None ,taint_sink :str |None =None )->DeduplicatedFinding :
    return DeduplicatedFinding (finding_id =finding_id ,agent_source ='test',file_path ='app.py',line_start =10 ,line_end =12 ,function_name ='handler',vulnerability_class =vulnerability_class ,cwe_id ='CWE-89',owasp_category ='A03',severity =Severity .HIGH ,confidence =0.9 ,exploitability =Exploitability .CONFIRMED ,vulnerable_code ='query = x',taint_source =taint_source ,taint_sink =taint_sink ,taint_path =[],reasoning ='test',false_positive_indicators =[],remediation_hint ='fix',contributing_agents =['test'],duplicate_count =1 )

def test_direct_taint_flow_creates_chain ():
    combiner =ChainCombiner ()
    a =_make_dedup ('f1','SQL Injection',taint_source ='request.args',taint_sink ='db.execute(q)')
    b =_make_dedup ('f2','Command Injection',taint_source ='db.execute(q)',taint_sink ='os.system(cmd)')
    context =make_context ()
    chains ,unchained =combiner .run ([a ,b ],context )
    assert len (chains )>=1 
    assert any ((len (c .findings )>=2 for c in chains ))
    assert len (unchained )<2 

def test_chains_auth_bypass_with_idor ():
    combiner =ChainCombiner ()
    auth =_make_dedup ('f1','Missing Authentication',taint_sink ='handler()')
    idor =_make_dedup ('f2','IDOR',taint_source ='other')
    context =make_context ()
    chains ,unchained =combiner .run ([auth ,idor ],context )
    assert len (chains )>=1 
    assert any (('Missing Authentication'in c .chain_name and 'IDOR'in c .chain_name for c in chains ))

def test_unrelated_findings_not_chained ():
    combiner =ChainCombiner ()
    a =_make_dedup ('f1','SQL Injection',taint_source ='x',taint_sink ='sink_a')
    b =_make_dedup ('f2','XSS',taint_source ='y',taint_sink ='sink_b')
    context =make_context ()
    chains ,unchained =combiner .run ([a ,b ],context )
    assert len (chains )==0 
    assert len (unchained )==2 

def test_chain_name_reflects_finding_classes ():
    combiner =ChainCombiner ()
    a =_make_dedup ('f1','SQL Injection',taint_source ='req',taint_sink ='db.run')
    b =_make_dedup ('f2','Command Injection',taint_source ='db.run',taint_sink ='os.system')
    context =make_context ()
    chains ,_ =combiner .run ([a ,b ],context )
    assert len (chains )>=1 
    assert 'SQL Injection'in chains [0 ].chain_name 
    assert 'Command Injection'in chains [0 ].chain_name 

def test_unchained_findings_returned_separately ():
    combiner =ChainCombiner ()
    a =_make_dedup ('f1','SQL Injection',taint_source ='a',taint_sink ='s1')
    b =_make_dedup ('f2','SQL Injection',taint_source ='s1',taint_sink ='s2')
    c =_make_dedup ('f3','XSS',taint_source ='z',taint_sink ='out')
    context =make_context ()
    chains ,unchained =combiner .run ([a ,b ,c ],context )
    unchained_ids ={f .finding_id for f in unchained }
    assert 'f3'in unchained_ids or len (chains )==0 

def test_chain_length_correct ():
    combiner =ChainCombiner ()
    a =_make_dedup ('f1','A',taint_source ='x',taint_sink ='y')
    b =_make_dedup ('f2','B',taint_source ='y',taint_sink ='z')
    context =make_context ()
    chains ,_ =combiner .run ([a ,b ],context )
    assert len (chains )>=1 
    assert chains [0 ].chain_length ==len (chains [0 ].findings )

def test_chains_info_disclosure_with_exploitation ():
    combiner =ChainCombiner ()
    info =_make_dedup ('f1','Information Disclosure',taint_sink ='response.json')
    idor =_make_dedup ('f2','IDOR',taint_source ='response')
    context =make_context ()
    chains ,unchained =combiner .run ([info ,idor ],context )
    assert isinstance (chains ,list )
    assert isinstance (unchained ,list )
    assert len (chains )+len (unchained )>=1 

def test_empty_findings_returns_empty_chains_and_unchained ():
    combiner =ChainCombiner ()
    context =make_context ()
    chains ,unchained =combiner .run ([],context )
    assert chains ==[]
    assert unchained ==[]

def test_single_finding_no_chain ():
    combiner =ChainCombiner ()
    a =_make_dedup ('f1','SQL Injection')
    context =make_context ()
    chains ,unchained =combiner .run ([a ],context )
    assert len (chains )==0 
    assert len (unchained )==1 
    assert unchained [0 ].finding_id =='f1'
