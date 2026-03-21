import uuid 
from typing import Any 
from .models import AgentContext ,DeduplicatedFinding ,EntryPoint ,VulnerabilityChain 
AUTH_BYPASS_CLASSES =frozenset ({'missing authentication','auth bypass','broken authentication','authentication bypass'})
REQUIRES_AUTH_CLASSES =frozenset ({'idor','insecure direct object reference','privilege escalation','sensitive data exposure','access control'})

def _normalize_class (s :str )->str :
    return (s or '').strip ().lower ()

def _is_auth_bypass (f :DeduplicatedFinding )->bool :
    return _normalize_class (f .vulnerability_class )in AUTH_BYPASS_CLASSES or ('auth'in _normalize_class (f .vulnerability_class )and 'bypass'in _normalize_class (f .vulnerability_class ))

def _requires_auth (f :DeduplicatedFinding )->bool :
    n =_normalize_class (f .vulnerability_class )
    if n in REQUIRES_AUTH_CLASSES :
        return True 
    return any ((r in n for r in ('idor','privilege','access control','sensitive data')))

def _direct_taint_flow (a :DeduplicatedFinding ,b :DeduplicatedFinding )->bool :
    sink =(a .taint_sink or '').strip ()
    source =(b .taint_source or '').strip ()
    if not sink or not source :
        return False 
    return sink in source or sink ==source 

def _chainable (a :DeduplicatedFinding ,b :DeduplicatedFinding )->bool :
    if a .finding_id ==b .finding_id :
        return False 
    if _direct_taint_flow (a ,b ):
        return True 
    if _is_auth_bypass (a )and _requires_auth (b ):
        return True 
    a_class =_normalize_class (a .vulnerability_class )
    b_class =_normalize_class (b .vulnerability_class )
    if 'information disclosure'in a_class or 'info leak'in a_class :
        if 'idor'in b_class or 'injection'in b_class or 'privilege'in b_class :
            return True 
    return False 

class ChainCombiner :

    def __init__ (self ,llm_client :Any |None =None ):
        self .llm_client =llm_client 

    def run (self ,findings :list [DeduplicatedFinding ],context :AgentContext )->tuple [list [VulnerabilityChain ],list [DeduplicatedFinding ]]:
        if not findings :
            return ([],[])
        graph =self ._build_chain_graph (findings )
        chains :list [VulnerabilityChain ]=[]
        used_ids :set [str ]=set ()
        for start in findings :
            if start .finding_id in used_ids :
                continue 
            path =self ._extend_chain (start ,graph ,used_ids )
            if len (path )>=2 :
                chain =self ._make_chain (path ,context )
                chains .append (chain )
                for d in path :
                    used_ids .add (d .finding_id )
        unchained =[f for f in findings if f .finding_id not in used_ids ]
        return (chains ,unchained )

    def _build_chain_graph (self ,findings :list [DeduplicatedFinding ])->dict [str ,list [DeduplicatedFinding ]]:
        by_id ={f .finding_id :f for f in findings }
        graph :dict [str ,list [DeduplicatedFinding ]]={f .finding_id :[]for f in findings }
        for a in findings :
            for b in findings :
                if _chainable (a ,b ):
                    graph [a .finding_id ].append (b )
        return graph 

    def _extend_chain (self ,start :DeduplicatedFinding ,graph :dict [str ,list [DeduplicatedFinding ]],used :set [str ])->list [DeduplicatedFinding ]:
        path =[start ]
        current =start 
        while True :
            next_list =[n for n in graph .get (current .finding_id ,[])if n .finding_id not in used and n not in path ]
            if not next_list :
                break 
            next_f =next_list [0 ]
            for n in next_list :
                if _direct_taint_flow (current ,n ):
                    next_f =n 
                    break 
            path .append (next_f )
            used .add (next_f .finding_id )
            current =next_f 
        return path 

    def _make_chain (self ,path :list [DeduplicatedFinding ],context :AgentContext )->VulnerabilityChain :
        chain_id =f'chain-{uuid .uuid4 ().hex [:12 ]}'
        names =[f .vulnerability_class for f in path ]
        chain_name =' → '.join (names [:5 ])+(' …'if len (names )>5 else '')
        entry_point :EntryPoint |None =None 
        if context .entry_points and path :
            first =path [0 ]
            for ep in context .entry_points :
                if ep .file_path in first .file_path or first .file_path in ep .file_path :
                    entry_point =ep 
                    break 
            if not entry_point :
                entry_point =context .entry_points [0 ]
        impact =path [-1 ].vulnerability_class if path else ''
        exploitability =path [-1 ].exploitability .value if hasattr (path [-1 ].exploitability ,'value')else str (path [-1 ].exploitability )
        attack_narrative =self ._generate_narrative (path ,chain_name ,context )
        return VulnerabilityChain (chain_id =chain_id ,chain_name =chain_name ,findings =list (path ),entry_point =entry_point ,impact =impact ,exploitability =exploitability ,attack_narrative =attack_narrative ,chain_length =len (path ))

    def _generate_narrative (self ,path :list [DeduplicatedFinding ],chain_name :str ,context :AgentContext )->str :
        if not path :
            return ''
        parts =[]
        for i ,f in enumerate (path ,1 ):
            parts .append (f'{i }. [{f .vulnerability_class }] {f .file_path }:{f .line_start } — {f .reasoning [:200 ]}')
        fallback ='Attack chain:\n'+'\n'.join (parts )
        if not self .llm_client :
            return fallback 
        try :
            prompt =f'Summarize this vulnerability chain in 2-4 sentences for a penetration test report.\n\nChain: {chain_name }\n\nSteps:\n{chr (10 ).join (parts )}\n\nWrite only the narrative, no bullet list.'
            resp =self .llm_client .complete (prompt =prompt ,system_prompt ='You are a security analyst. Output only the attack narrative.')
            text =getattr (resp ,'content',resp )if hasattr (resp ,'content')else str (resp )
            return (text or '').strip ()or fallback 
        except Exception :
            return fallback 
