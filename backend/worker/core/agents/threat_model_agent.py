import re 
from typing import Any 
from .base_agent import BaseAgent 
from .models import AgentContext ,AgentFinding ,ThreatModel ,ThreatScenario 

class ThreatModelAgent (BaseAgent ):
    STACK_THREATS ={'python':{'flask':[ThreatScenario (description ='SQL injection in raw SQL queries with Flask-SQLAlchemy',priority =0.9 ,cwe_ids =['CWE-89']),ThreatScenario (description ='JWT token forgery or weak secret in authentication',priority =0.85 ,cwe_ids =['CWE-347','CWE-798']),ThreatScenario (description ='Server-side template injection in Jinja2',priority =0.8 ,cwe_ids =['CWE-94']),ThreatScenario (description ='Insecure direct object reference in Flask routes',priority =0.75 ,cwe_ids =['CWE-639'])],'fastapi':[ThreatScenario (description ='Pydantic validation bypass with nested models',priority =0.85 ,cwe_ids =['CWE-20']),ThreatScenario (description ='SQL injection in raw async queries',priority =0.9 ,cwe_ids =['CWE-89']),ThreatScenario (description ='JWT algorithm confusion (HS256 vs RS256)',priority =0.8 ,cwe_ids =['CWE-347'])],'django':[ThreatScenario (description ='SQL injection in raw() queries',priority =0.9 ,cwe_ids =['CWE-89']),ThreatScenario (description ='Template injection in Django templates',priority =0.75 ,cwe_ids =['CWE-94']),ThreatScenario (description ='Missing @login_required on sensitive views',priority =0.8 ,cwe_ids =['CWE-306'])]},'javascript':{'express':[ThreatScenario (description ='NoSQL injection in MongoDB queries with Mongoose',priority =0.9 ,cwe_ids =['CWE-943']),ThreatScenario (description ='Prototype pollution via lodash merge',priority =0.85 ,cwe_ids =['CWE-1321']),ThreatScenario (description ="JWT token forgery with 'none' algorithm",priority =0.85 ,cwe_ids =['CWE-347']),ThreatScenario (description ='Command injection via child_process',priority =0.9 ,cwe_ids =['CWE-78'])],'nextjs':[ThreatScenario (description ='SSRF in getServerSideProps with external API calls',priority =0.8 ,cwe_ids =['CWE-918']),ThreatScenario (description =' XSS in dangerouslySetInnerHTML',priority =0.75 ,cwe_ids =['CWE-79'])]},'java':{'spring':[ThreatScenario (description ='SQL injection in JPA native queries',priority =0.9 ,cwe_ids =['CWE-89']),ThreatScenario (description ='Spring Security bypass via URL pattern manipulation',priority =0.85 ,cwe_ids =['CWE-285']),ThreatScenario (description ='Deserialization vulnerability in Spring',priority =0.8 ,cwe_ids =['CWE-502'])]}}
    FRAMEWORK_SINKS ={'python':{'flask':['execute()','cursor.execute()','raw()'],'fastapi':['execute()','raw_query()','async_session.execute()'],'django':['raw()','extra()','execute()']},'javascript':{'express':['db.collection.find()','exec()','eval()','child_process.spawn()'],'nextjs':['fetch()','axios.get()','router.push()']},'java':{'spring':['JdbcTemplate.execute()','entityManager.createNativeQuery()','Runtime.exec()']}}
    FRAMEWORK_SOURCES ={'python':{'flask':['request.args','request.form','request.json','request.headers'],'fastapi':['request.query','request.body','request.headers'],'django':['request.GET','request.POST','request.json']},'javascript':{'express':['req.query','req.body','req.params','req.headers'],'nextjs':['query','req.body','req.headers']}}
    CVE_PATTERNS ={'python':{'flask':['CVE-2018-1000656','CVE-2019-1010083'],'django':['CVE-2021-33203','CVE-2021-28658']},'javascript':{'express':['CVE-2022-24999'],'lodash':['CVE-2020-28500','CVE-2021-23337']}}

    def __init__ (self ,*args ,**kwargs ):
        name =kwargs .pop ('name','ThreatModelAgent')
        super ().__init__ (*args ,name =name ,**kwargs )

    def build_prompt (self ,context :AgentContext ,include_file_contents :bool =True )->str :
        stack_parts =[]
        if context .language :
            stack_parts .append (context .language .capitalize ())
        if context .framework :
            stack_parts .append (context .framework .capitalize ())
        stack_summary ='/'.join (stack_parts )if stack_parts else 'Unknown Stack'
        return f'You are a security architect tasked with generating a threat model for this codebase.\n\n## Instructions\n\nBased on the detected technology stack, identify the HIGH-PRIORITY threat scenarios.\n\n## Tech Stack\n\nStack: {stack_summary }\nLanguage: {context .language }\nFramework: {context .framework }\n\n## Output Format\n\nReturn a JSON object matching ThreatModel:\n{{\n  "stack_summary": "Python/Flask",\n  "high_priority_threats": [\n    {{\n      "description": "SQL injection in raw SQL queries",\n      "priority": 0.9,\n      "cwe_ids": ["CWE-89"]\n    }}\n  ],\n  "framework_specific_sinks": ["execute()", "cursor.execute()"],\n  "framework_specific_sources": ["request.args", "request.form"],\n  "known_cve_patterns": ["CVE-2018-1000656"]\n}}\n\n## Guidelines\n\n1. **Priority Range**: 0.0 - 1.0 (1.0 = highest priority)\n2. **Focus on**: Stack-specific vulnerabilities, not generic OWASP Top 10\n3. **Be Specific**: Mention exact functions/methods that are dangerous\n4. **Include CWE IDs**: Link each threat to relevant CWE\n'

    def parse_response (self ,response :str )->list [AgentFinding ]:
        import json 
        findings =[]
        try :
            data =json .loads (response )
            threat_model =ThreatModel (stack_summary =data .get ('stack_summary','Unknown Stack'),high_priority_threats =[ThreatScenario (description =t .get ('description',''),priority =t .get ('priority',0.5 ),cwe_ids =t .get ('cwe_ids',[]))for t in data .get ('high_priority_threats',[])],framework_specific_sinks =data .get ('framework_specific_sinks',[]),framework_specific_sources =data .get ('framework_specific_sources',[]),known_cve_patterns =data .get ('known_cve_patterns',[]))
            for threat in threat_model .high_priority_threats :
                finding =AgentFinding (finding_id =f'THREAT-{self ._generate_finding_id (threat .description )}',agent_source =self .name ,file_path ='',line_start =0 ,line_end =0 ,function_name ='',vulnerability_class ='Threat Scenario',cwe_id =threat .cwe_ids [0 ]if threat .cwe_ids else '',severity ='high'if threat .priority >0.8 else 'medium',reasoning =f'High-priority threat: {threat .description }',metadata ={'threat_scenario':threat .__dict__ })
                findings .append (finding )
        except json .JSONDecodeError :
            pass 
        return findings 

    def _generate_finding_id (self ,text :str )->str :
        import hashlib 
        return hashlib .md5 (text .encode ()).hexdigest ()[:8 ]

    def generate_threat_model (self ,context :AgentContext )->ThreatModel |None :
        lang =context .language 
        framework =context .framework 
        if not lang or not framework :
            return None 
        stack_threats =self .STACK_THREATS .get (lang ,{}).get (framework ,[])
        sinks =self .FRAMEWORK_SINKS .get (lang ,{}).get (framework ,[])
        sources =self .FRAMEWORK_SOURCES .get (lang ,{}).get (framework ,[])
        cves =self .CVE_PATTERNS .get (lang ,{}).get (framework ,[])
        stack_summary =f'{lang .capitalize ()}/{framework .capitalize ()}'
        return ThreatModel (stack_summary =stack_summary ,high_priority_threats =stack_threats ,framework_specific_sinks =sinks ,framework_specific_sources =sources ,known_cve_patterns =cves )

    def analyze_entry_points_for_threats (self ,context :AgentContext ,entry_points :list )->list [ThreatScenario ]:
        additional_threats =[]
        for ep in entry_points :
            if not ep .authentication_required :
                additional_threats .append (ThreatScenario (description =f'Unauthenticated entry point at {ep .file_path }:{ep .line_number }',priority =0.8 ,cwe_ids =['CWE-306']))
            if ep .entry_type =='http':
                additional_threats .append (ThreatScenario (description =f'HTTP entry point may be susceptible to downgrade attacks',priority =0.6 ,cwe_ids =['CWE-319']))
        return additional_threats 

    def get_priority_weights (self ,context :AgentContext )->dict [str ,float ]:
        weights ={'SQL Injection':0.9 ,'Command Injection':0.9 ,'Authentication Bypass':0.85 ,'XSS':0.7 ,'CSRF':0.6 ,'IDOR':0.75 }
        if context .threat_model :
            for threat in context .threat_model .high_priority_threats :
                if 'SQL'in threat .description :
                    weights ['SQL Injection']=max (weights ['SQL Injection'],threat .priority )
                if 'Command'in threat .description :
                    weights ['Command Injection']=max (weights ['Command Injection'],threat .priority )
        return weights 
