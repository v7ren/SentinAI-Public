import pytest 
from backend .worker .core .agents .deduplication_engine import DeduplicationEngine ,_lines_overlap ,_merge 
from backend .worker .core .agents .models import AgentFinding ,DeduplicatedFinding ,Exploitability ,Severity 

def _make_finding (finding_id :str ='f1',agent_source :str ='injection_specialist',file_path :str ='app.py',line_start :int =10 ,line_end :int =12 ,vulnerability_class :str ='SQL Injection',confidence :float =0.8 ,taint_sink :str |None =None ,taint_path :list [str ]|None =None ,false_positive_indicators :list [str ]|None =None )->AgentFinding :
    return AgentFinding (finding_id =finding_id ,agent_source =agent_source ,file_path =file_path ,line_start =line_start ,line_end =line_end ,function_name ='handler',vulnerability_class =vulnerability_class ,cwe_id ='CWE-89',owasp_category ='A03:2021',severity =Severity .HIGH ,confidence =confidence ,exploitability =Exploitability .CONFIRMED ,vulnerable_code ="query = 'SELECT' + user_input",taint_source ='request.args',taint_sink =taint_sink ,taint_path =taint_path or ['step1'],reasoning ='test',false_positive_indicators =false_positive_indicators or [],remediation_hint ='Use parameterized query')

def test_merges_exact_duplicate_findings ():
    engine =DeduplicationEngine ()
    f1 =_make_finding ('f1','injection_specialist','app.py',10 ,12 ,'SQL Injection')
    f2 =_make_finding ('f2','auth_specialist','app.py',11 ,13 ,'SQL Injection')
    result =engine .run ([f1 ,f2 ])
    assert len (result )==1 
    assert result [0 ].duplicate_count ==2 
    assert result [0 ].confidence ==0.8 

def test_merges_overlapping_line_range_findings ():
    engine =DeduplicationEngine ()
    f1 =_make_finding ('f1','a','x.py',5 ,10 ,'Command Injection')
    f2 =_make_finding ('f2','b','x.py',8 ,15 ,'Command Injection')
    result =engine .run ([f1 ,f2 ])
    assert len (result )==1 
    assert result [0 ].line_start ==5 
    assert result [0 ].line_end ==15 

def test_keeps_highest_confidence_score ():
    engine =DeduplicationEngine ()
    f1 =_make_finding ('f1','a','app.py',10 ,12 ,'SQL Injection',confidence =0.5 )
    f2 =_make_finding ('f2','b','app.py',11 ,12 ,'SQL Injection',confidence =0.95 )
    result =engine .run ([f1 ,f2 ])
    assert len (result )==1 
    assert result [0 ].confidence ==0.95 

def test_keeps_longest_taint_path ():
    engine =DeduplicationEngine ()
    f1 =_make_finding ('f1','a','app.py',10 ,12 ,'SQL Injection',taint_path =['a','b'])
    f2 =_make_finding ('f2','b','app.py',11 ,12 ,'SQL Injection',taint_path =['a','b','c','d'])
    result =engine .run ([f1 ,f2 ])
    assert len (result )==1 
    assert len (result [0 ].taint_path or [])==4 

def test_unions_false_positive_indicators ():
    engine =DeduplicationEngine ()
    f1 =_make_finding ('f1','a','app.py',10 ,12 ,'SQL Injection',false_positive_indicators =['x'])
    f2 =_make_finding ('f2','b','app.py',11 ,12 ,'SQL Injection',false_positive_indicators =['y'])
    result =engine .run ([f1 ,f2 ])
    assert len (result )==1 
    assert set (result [0 ].false_positive_indicators )=={'x','y'}

def test_records_all_contributing_agents ():
    engine =DeduplicationEngine ()
    f1 =_make_finding ('f1','injection_specialist','app.py',10 ,12 ,'SQL Injection')
    f2 =_make_finding ('f2','auth_specialist','app.py',11 ,12 ,'SQL Injection')
    result =engine .run ([f1 ,f2 ])
    assert len (result )==1 
    assert set (result [0 ].contributing_agents )=={'injection_specialist','auth_specialist'}

def test_does_not_merge_different_vulnerability_classes ():
    engine =DeduplicationEngine ()
    f1 =_make_finding ('f1','a','app.py',10 ,12 ,'SQL Injection')
    f2 =_make_finding ('f2','b','app.py',10 ,12 ,'Command Injection')
    result =engine .run ([f1 ,f2 ])
    assert len (result )==2 

def test_does_not_merge_different_files ():
    engine =DeduplicationEngine ()
    f1 =_make_finding ('f1','a','app.py',10 ,12 ,'SQL Injection')
    f2 =_make_finding ('f2','b','other.py',10 ,12 ,'SQL Injection')
    result =engine .run ([f1 ,f2 ])
    assert len (result )==2 

def test_single_finding_passes_through_unchanged ():
    engine =DeduplicationEngine ()
    f =_make_finding ('f1','injection_specialist','app.py',10 ,12 ,'SQL Injection')
    result =engine .run ([f ])
    assert len (result )==1 
    assert result [0 ].duplicate_count ==1 
    assert result [0 ].contributing_agents ==['injection_specialist']

def test_sink_match_merges_same_taint_sink ():
    engine =DeduplicationEngine ()
    f1 =_make_finding ('f1','a','a.py',1 ,2 ,'SQL Injection',taint_sink ='db.execute(q)')
    f2 =_make_finding ('f2','b','b.py',3 ,4 ,'SQL Injection',taint_sink ='db.execute(q)')
    result =engine .run ([f1 ,f2 ])
    assert len (result )==1 
    assert result [0 ].duplicate_count ==2 

def test_empty_findings_returns_empty ():
    engine =DeduplicationEngine ()
    assert engine .run ([])==[]

def test_lines_overlap_helper ():
    f1 =_make_finding ('a','x','f',10 ,20 ,'SQL')
    f2 =_make_finding ('b','y','f',15 ,25 ,'SQL')
    assert _lines_overlap (f1 ,f2 )is True 
    f3 =_make_finding ('c','z','f',21 ,30 ,'SQL')
    assert _lines_overlap (f1 ,f3 )is False 
