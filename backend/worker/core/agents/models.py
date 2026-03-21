from dataclasses import dataclass ,field 
from datetime import datetime 
from enum import Enum 
from typing import Any 

class ScanMode (str ,Enum ):
    FULL ='full'
    DIFF ='diff'

class Severity (str ,Enum ):
    CRITICAL ='critical'
    HIGH ='high'
    MEDIUM ='medium'
    LOW ='low'
    INFO ='info'

class Exploitability (str ,Enum ):
    CONFIRMED ='confirmed'
    LIKELY ='likely'
    POSSIBLE ='possible'
    UNLIKELY ='unlikely'

@dataclass 
class EntryPoint :
    entry_type :str 
    file_path :str 
    line_number :int 
    function_name :str 
    handler_function :str 
    parameters :list [str ]=field (default_factory =list )
    authentication_required :bool =False 
    authorization_required :bool =False 
    rate_limited :bool =False 
    framework :str =''

@dataclass 
class EntryParameter :
    name :str 
    location :str 
    type_ :str ='string'

@dataclass 
class ArchPattern :
    pattern_type :str 
    middleware_order :list [str ]=field (default_factory =list )
    auth_middleware_files :list [str ]=field (default_factory =list )
    orm_type :str |None =None 
    template_engine :str |None =None 
    cors_config :dict [str ,Any ]|None =None 
    service_layer_files :list [str ]=field (default_factory =list )
    repository_files :list [str ]=field (default_factory =list )
    di_container :str |None =None 

@dataclass 
class CORSConfig :
    allow_origin :str 
    allow_methods :list [str ]
    allow_headers :list [str ]
    expose_headers :list [str ]
    max_age :int |None =None 
    allow_credentials :bool =False 

@dataclass 
class ThreatScenario :
    description :str 
    priority :float 
    cwe_ids :list [str ]=field (default_factory =list )

@dataclass 
class ThreatModel :
    stack_summary :str 
    high_priority_threats :list [ThreatScenario ]=field (default_factory =list )
    framework_specific_sinks :list [str ]=field (default_factory =list )
    framework_specific_sources :list [str ]=field (default_factory =list )
    known_cve_patterns :list [str ]=field (default_factory =list )

@dataclass 
class SanitizerInfo :
    function_name :str 
    file_path :str 
    sanitizes :list [str ]

@dataclass 
class DeadCodeRegion :
    file_path :str 
    line_start :int 
    line_end :int 
    reason :str 

@dataclass 
class AgentContext :
    call_graph :dict [str ,list [str ]]=field (default_factory =dict )
    dependency_map :dict [str ,list [str ]]=field (default_factory =dict )
    sanitizer_registry :dict [str ,SanitizerInfo ]=field (default_factory =dict )
    dead_code_map :dict [str ,DeadCodeRegion ]=field (default_factory =dict )
    entry_points :list [EntryPoint ]=field (default_factory =list )
    architecture_patterns :ArchPattern |None =None 
    threat_model :ThreatModel |None =None 
    file_contents :dict [str ,str ]=field (default_factory =dict )
    file_asts :dict [str ,Any ]=field (default_factory =dict )
    scan_id :str =''
    repo_path :str =''
    language :str =''
    framework :str =''
    scan_mode :ScanMode =ScanMode .FULL 
    changed_files :list [str ]=field (default_factory =list )

@dataclass 
class AgentFinding :
    finding_id :str 
    agent_source :str 
    file_path :str 
    line_start :int 
    line_end :int 
    function_name :str =''
    vulnerability_class :str =''
    cwe_id :str =''
    owasp_category :str =''
    severity :Severity =Severity .MEDIUM 
    confidence :float =0.0 
    exploitability :Exploitability =Exploitability .POSSIBLE 
    vulnerable_code :str =''
    taint_source :str |None =None 
    taint_sink :str |None =None 
    taint_path :list [str ]|None =None 
    chain_id :str |None =None 
    chain_position :int |None =None 
    reasoning :str =''
    false_positive_indicators :list [str ]=field (default_factory =list )
    remediation_hint :str =''
    metadata :dict [str ,Any ]=field (default_factory =dict )

    def to_dict (self )->dict [str ,Any ]:
        return {'finding_id':self .finding_id ,'agent_source':self .agent_source ,'file_path':self .file_path ,'line_start':self .line_start ,'line_end':self .line_end ,'function_name':self .function_name ,'vulnerability_class':self .vulnerability_class ,'cwe_id':self .cwe_id ,'owasp_category':self .owasp_category ,'severity':self .severity .value if isinstance (self .severity ,Severity )else self .severity ,'confidence':self .confidence ,'exploitability':self .exploitability .value if isinstance (self .exploitability ,Exploitability )else self .exploitability ,'vulnerable_code':self .vulnerable_code ,'taint_source':self .taint_source ,'taint_sink':self .taint_sink ,'taint_path':self .taint_path ,'chain_id':self .chain_id ,'chain_position':self .chain_position ,'reasoning':self .reasoning ,'false_positive_indicators':self .false_positive_indicators ,'remediation_hint':self .remediation_hint ,'metadata':self .metadata }

    @classmethod 
    def from_dict (cls ,data :dict [str ,Any ])->'AgentFinding':
        severity =data .get ('severity')
        if isinstance (severity ,str ):
            try :
                severity =Severity (severity )
            except ValueError :
                severity =Severity .MEDIUM 
        exploitability =data .get ('exploitability')
        if isinstance (exploitability ,str ):
            try :
                exploitability =Exploitability (exploitability )
            except ValueError :
                exploitability =Exploitability .POSSIBLE 
        return cls (finding_id =data .get ('finding_id',''),agent_source =data .get ('agent_source',''),file_path =data .get ('file_path',''),line_start =data .get ('line_start',0 ),line_end =data .get ('line_end',0 ),function_name =data .get ('function_name',''),vulnerability_class =data .get ('vulnerability_class',''),cwe_id =data .get ('cwe_id',''),owasp_category =data .get ('owasp_category',''),severity =severity ,confidence =data .get ('confidence',0.0 ),exploitability =exploitability ,vulnerable_code =data .get ('vulnerable_code',''),taint_source =data .get ('taint_source'),taint_sink =data .get ('taint_sink'),taint_path =data .get ('taint_path'),chain_id =data .get ('chain_id'),chain_position =data .get ('chain_position'),reasoning =data .get ('reasoning',''),false_positive_indicators =data .get ('false_positive_indicators',[]),remediation_hint =data .get ('remediation_hint',''),metadata =data .get ('metadata',{}))

@dataclass 
class AgentResult :
    agent_name :str 
    findings :list [AgentFinding ]=field (default_factory =list )
    execution_time_ms :int =0 
    token_usage :int =0 
    errors :list [str ]=field (default_factory =list )
    metadata :dict [str ,Any ]=field (default_factory =dict )

    def to_dict (self )->dict [str ,Any ]:
        return {'agent_name':self .agent_name ,'findings':[f .to_dict ()for f in self .findings ],'execution_time_ms':self .execution_time_ms ,'token_usage':self .token_usage ,'errors':self .errors ,'metadata':self .metadata }

@dataclass 
class DeduplicatedFinding :
    finding_id :str 
    agent_source :str 
    file_path :str 
    line_start :int 
    line_end :int 
    function_name :str =''
    vulnerability_class :str =''
    cwe_id :str =''
    owasp_category :str =''
    severity :Severity =Severity .MEDIUM 
    confidence :float =0.0 
    exploitability :Exploitability =Exploitability .POSSIBLE 
    vulnerable_code :str =''
    taint_source :str |None =None 
    taint_sink :str |None =None 
    taint_path :list [str ]|None =None 
    chain_id :str |None =None 
    chain_position :int |None =None 
    reasoning :str =''
    false_positive_indicators :list [str ]=field (default_factory =list )
    remediation_hint :str =''
    metadata :dict [str ,Any ]=field (default_factory =dict )
    contributing_agents :list [str ]=field (default_factory =list )
    duplicate_count :int =1 

    def to_agent_finding (self )->AgentFinding :
        return AgentFinding (finding_id =self .finding_id ,agent_source =self .agent_source ,file_path =self .file_path ,line_start =self .line_start ,line_end =self .line_end ,function_name =self .function_name ,vulnerability_class =self .vulnerability_class ,cwe_id =self .cwe_id ,owasp_category =self .owasp_category ,severity =self .severity ,confidence =self .confidence ,exploitability =self .exploitability ,vulnerable_code =self .vulnerable_code ,taint_source =self .taint_source ,taint_sink =self .taint_sink ,taint_path =self .taint_path ,chain_id =self .chain_id ,chain_position =self .chain_position ,reasoning =self .reasoning ,false_positive_indicators =self .false_positive_indicators ,remediation_hint =self .remediation_hint ,metadata =self .metadata )

@dataclass 
class VulnerabilityChain :
    chain_id :str 
    chain_name :str 
    findings :list ['DeduplicatedFinding']
    entry_point :EntryPoint |None 
    impact :str 
    exploitability :str 
    attack_narrative :str 
    chain_length :int =0 

@dataclass 
class AttackStep :
    step_number :int 
    action :str 
    target_endpoint :str 
    payload_type :str 
    expected_response :str 
    finding_reference :str 

@dataclass 
class AttackPath :
    path_id :str 
    entry_point :EntryPoint |None 
    chains_involved :list [VulnerabilityChain ]
    steps :list [AttackStep ]
    final_impact :str 
    attacker_prerequisites :list [str ]=field (default_factory =list )
    estimated_complexity :str ='unknown'
    proof_of_concept_outline :str =''

@dataclass 
class SkepticVerdict :
    finding_id :str 
    verdict :str 
    confidence_adjustment :float 
    skeptic_reasoning :str 
    surviving_risk :str |None =None 

@dataclass 
class Remediation :
    finding_id :str 
    fix_description :str 
    fixed_code :str 
    fix_type :str 
    unit_test_code :str =''
    unit_test_framework :str =''
    verification_steps :list [str ]=field (default_factory =list )
    regression_risk :str =''

@dataclass 
class FuzzingHint :
    attack_path_id :str 
    entry_point :str 
    http_method :str 
    required_parameters :list [str ]=field (default_factory =list )
    injection_points :list [str ]=field (default_factory =list )
    payload_templates :list [str ]=field (default_factory =list )
    boundary_values :list [str ]=field (default_factory =list )
    authentication_required :bool =False 
    auth_setup_steps :list [str ]=field (default_factory =list )
