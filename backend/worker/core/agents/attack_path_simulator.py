import uuid 
from .models import AgentContext ,AttackPath ,AttackStep ,DeduplicatedFinding ,EntryPoint ,VulnerabilityChain 

def _find_max_depth (call_graph :dict [str ,list [str ]])->int :
    if not call_graph :
        return 0 

    def dfs (node :str ,path :set [str ])->int :
        if node in path :
            return 0 
        path .add (node )
        depth =0 
        for c in call_graph .get (node ,[]):
            depth =max (depth ,1 +dfs (c ,path ))
        path .discard (node )
        return depth 
    max_d =0 
    for start in call_graph :
        max_d =max (max_d ,dfs (start ,set ()))
    return max_d 

class AttackPathSimulator :

    def _validate_call_graph_depth (self ,context :AgentContext )->bool :
        max_depth =_find_max_depth (context .call_graph )
        if max_depth <5 :
            print (f'[AttackPathSimulator] WARNING: Call graph depth {max_depth } < 5. Path simulation will be limited to shallow paths.')
            return False 
        return True 

    def run (self ,chains :list [VulnerabilityChain ],context :AgentContext )->list [AttackPath ]:
        if not chains :
            return []
        deep_graph =self ._validate_call_graph_depth (context )
        paths :list [AttackPath ]=[]
        for chain in chains :
            steps =self ._build_steps_for_chain (chain )
            entry =chain .entry_point 
            ep_desc =f'{entry .file_path }:{entry .line_number }'if entry else 'unknown'
            prerequisites =self ._attacker_prerequisites (chain ,context )
            complexity =self ._estimate_complexity (chain ,prerequisites )
            poc =self ._proof_of_concept_outline (chain ,steps )
            path =AttackPath (path_id =f'path-{uuid .uuid4 ().hex [:12 ]}',entry_point =entry ,chains_involved =[chain ],steps =steps ,final_impact =chain .impact or 'Vulnerability exploitation',attacker_prerequisites =prerequisites ,estimated_complexity =complexity ,proof_of_concept_outline =poc )
            paths .append (path )
        return paths 

    def _build_steps_for_chain (self ,chain :VulnerabilityChain )->list [AttackStep ]:
        steps =[]
        for i ,f in enumerate (chain .findings ,1 ):
            steps .append (AttackStep (step_number =i ,action =f'Exploit {f .vulnerability_class } at {f .file_path }:{f .line_start }',target_endpoint =f .file_path ,payload_type =_payload_type_for_class (f .vulnerability_class ),expected_response ='Code execution or data exposure',finding_reference =f .finding_id ))
        return steps 

    def _attacker_prerequisites (self ,chain :VulnerabilityChain ,context :AgentContext )->list [str ]:
        pre :list [str ]=[]
        if chain .entry_point :
            ep =chain .entry_point 
            if not ep .authentication_required :
                pre .append ('No authentication required (public endpoint)')
            else :
                pre .append ('Valid credentials or session')
            pre .append (f'Access to {ep .entry_type } entry: {ep .file_path }:{ep .line_number }')
        else :
            pre .append ('Access to application entry point')
        if any (('injection'in (f .vulnerability_class or '').lower ()for f in chain .findings )):
            pre .append ('Ability to send crafted input (e.g. HTTP request body)')
        return pre 

    def _estimate_complexity (self ,chain :VulnerabilityChain ,prerequisites :list [str ])->str :
        impact_lower =(chain .impact or '').lower ()
        unauthenticated =any (('no authentication'in p .lower ()for p in prerequisites ))
        if unauthenticated and ('rce'in impact_lower or 'remote code'in impact_lower or 'command'in impact_lower ):
            return 'trivial'
        if unauthenticated :
            return 'low'
        if len (chain .findings )>=3 :
            return 'high'
        return 'medium'

    def _proof_of_concept_outline (self ,chain :VulnerabilityChain ,steps :list [AttackStep ])->str :
        lines =[f'Chain: {chain .chain_name }','']
        for s in steps :
            lines .append (f'{s .step_number }. {s .action }')
            lines .append (f'   Payload type: {s .payload_type }')
        return '\n'.join (lines )

def _payload_type_for_class (vuln_class :str )->str :
    c =(vuln_class or '').lower ()
    if 'sql'in c :
        return 'SQL injection payload'
    if 'command'in c or 'os'in c :
        return 'Command injection payload'
    if 'xss'in c or 'script'in c :
        return 'JavaScript/script payload'
    if 'ldap'in c :
        return 'LDAP filter payload'
    if 'template'in c or 'ssti'in c :
        return 'Template injection payload'
    if 'auth'in c or 'bypass'in c :
        return 'Auth bypass / session payload'
    if 'idor'in c :
        return 'Manipulated resource ID'
    return 'Crafted input'
