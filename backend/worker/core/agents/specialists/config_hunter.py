from __future__ import annotations 
import json 
import re 
import uuid 
from pathlib import Path 
from typing import Any 
from backend .worker .core .agents .base_agent import BaseAgent ,format_files_for_prompt ,format_context_metadata 
from backend .worker .core .agents .models import AgentContext ,AgentFinding ,AgentResult ,Exploitability ,Severity 
from backend .worker .core .llm_client import LLMClient 
SECRET_PATTERNS :dict [str ,str ]={'aws_access_key':'AKIA[0-9A-Z]{16}','aws_secret_key':'[0-9a-zA-Z/+]{40}','github_token':'ghp_[0-9a-zA-Z]{36}','stripe_key':'sk_live_[0-9a-zA-Z]{24}','private_key_header':'-----BEGIN (RSA |EC )?PRIVATE KEY-----','generic_password':'(?i)(password|passwd|pwd)\\s*[:=]\\s*[\'\\"]([^\'\\"]{8,})[\'\\"]','generic_api_key':'(?i)(api_key|apikey|api-key)\\s*[:=]\\s*[\'\\"]([^\'\\"]{16,})[\'\\"]'}
CONFIG_FILE_PATTERNS :list [str ]=['**/.env','**/.env.*','**/config.yaml','**/config.yml','**/config.json','**/settings.py','**/application.properties','**/docker-compose.yml','**/docker-compose.yaml','**/Dockerfile','**/.github/workflows/*.yml','**/kubernetes/*.yaml','**/k8s/*.yaml','**/nginx.conf','**/apache.conf']

class ConfigHunter (BaseAgent ):
    name ='config_hunter'

    def __init__ (self ,llm_client :LLMClient ):
        super ().__init__ (name ='config_hunter',llm_client =llm_client )
        self ._parse_error :str |None =None 

    def run (self ,context :AgentContext )->AgentResult :
        self ._parse_error =None 
        pattern_findings =[]
        for path ,content in context .file_contents .items ():
            pattern_findings .extend (self ._pattern_scan (path ,content ))
        result =super ().run (context )
        result .findings =pattern_findings +result .findings 
        if self ._parse_error is not None :
            result .errors .append (self ._parse_error )
        return result 

    def _pattern_scan (self ,file_path :str ,content :str )->list [AgentFinding ]:
        findings =[]
        lines =content .split ('\n')
        for name ,pattern in SECRET_PATTERNS .items ():
            for i ,line in enumerate (lines ,1 ):
                if re .search (pattern ,line ):
                    finding =AgentFinding (finding_id =str (uuid .uuid4 ()),agent_source =self .name ,file_path =file_path ,line_start =i ,line_end =i ,function_name ='',vulnerability_class ='Hardcoded Secret',cwe_id ='CWE-798',owasp_category ='',severity =Severity .HIGH ,confidence =0.9 ,exploitability =Exploitability .CONFIRMED ,vulnerable_code =line .strip ()[:200 ],taint_source =None ,taint_sink =None ,taint_path =None ,chain_id =None ,chain_position =None ,reasoning =f'Pattern match: {name }',false_positive_indicators =[],remediation_hint ='Move to environment or secret manager')
                    findings .append (finding )
        return findings 

    def build_prompt (self ,context :AgentContext ,include_file_contents :bool =True )->str :
        files_summary =format_context_metadata (context )if not include_file_contents else self ._format_files (context .file_contents )
        return f'\nYou are a security analyst scanning configuration and non-source files for misconfigurations.\n\n## FILES (configs, Docker, K8s, CI/CD, nginx, etc.)\n{files_summary }\n\n## FIND\n- Debug mode enabled in production config\n- CORS wildcard (Access-Control-Allow-Origin: *) on authenticated endpoints\n- Missing security headers (CSP, HSTS, X-Frame-Options)\n- Default credentials not changed in docker-compose\n- Secrets in plaintext in Kubernetes YAML\n- Command injection in GitHub Actions workflow inputs\n- Overly permissive RBAC\n\n## OUTPUT FORMAT\nReturn JSON: {{ "findings": [ {{ "file_path", "line_start", "line_end", "function_name", "vulnerability_class", "cwe_id", "severity", "confidence", "exploitability", "vulnerable_code", "reasoning", "false_positive_indicators", "remediation_hint" }} ] }}\nIf no findings: {{ "findings": [] }}\n'

    def parse_response (self ,response :str )->list [AgentFinding ]:
        try :
            data =json .loads (response .strip ())
            findings =[]
            for raw in data .get ('findings',[]):
                severity =self ._parse_severity (raw .get ('severity','medium'))
                exploitability =self ._parse_exploitability (raw .get ('exploitability','possible'))
                finding =AgentFinding (finding_id =str (uuid .uuid4 ()),agent_source =self .name ,file_path =raw .get ('file_path',''),line_start =int (raw .get ('line_start',0 )),line_end =int (raw .get ('line_end',0 )),function_name =raw .get ('function_name',''),vulnerability_class =raw .get ('vulnerability_class',''),cwe_id =raw .get ('cwe_id',''),owasp_category =raw .get ('owasp_category',''),severity =severity ,confidence =self ._parse_confidence (raw .get ('confidence',0.5 )),exploitability =exploitability ,vulnerable_code =raw .get ('vulnerable_code',''),taint_source =raw .get ('taint_source'),taint_sink =raw .get ('taint_sink'),taint_path =raw .get ('taint_path'),chain_id =None ,chain_position =None ,reasoning =raw .get ('reasoning',''),false_positive_indicators =raw .get ('false_positive_indicators',[]),remediation_hint =raw .get ('remediation_hint',''))
                findings .append (finding )
            return findings 
        except (json .JSONDecodeError ,KeyError ,TypeError )as e :
            self ._parse_error =f'ConfigHunter parse failed: {e }'
            return []

    def _format_files (self ,file_contents :dict [str ,str ])->str :
        return format_files_for_prompt (file_contents )

    def _parse_confidence (self ,value :str |int |float |Any )->float :
        if value is None :
            return 0.5 
        if isinstance (value ,(int ,float )):
            return float (value )
        if isinstance (value ,str ):
            return {'high':0.9 ,'medium':0.6 ,'low':0.3 ,'critical':0.95 }.get (value .lower (),0.5 )
        return 0.5 

    def _parse_severity (self ,value :str |Any )->Severity :
        if isinstance (value ,Severity ):
            return value 
        try :
            return Severity (value .lower ())
        except ValueError :
            return Severity .MEDIUM 

    def _parse_exploitability (self ,value :str |Any )->Exploitability :
        if isinstance (value ,Exploitability ):
            return value 
        try :
            return Exploitability (value .lower ())
        except ValueError :
            return Exploitability .POSSIBLE 
