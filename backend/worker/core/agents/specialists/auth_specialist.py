from __future__ import annotations 
import json 
import uuid 
from typing import Any 
from backend .worker .core .agents .base_agent import BaseAgent ,format_files_for_prompt ,format_context_metadata 
from backend .worker .core .agents .models import AgentContext ,AgentFinding ,AgentResult ,ArchPattern ,Exploitability ,Severity 
from backend .worker .core .llm_client import LLMClient 
SYSTEM_PROMPT ='You are a senior penetration tester specializing in authentication and session management.\nYour focus is broken authentication, session vulnerabilities, JWT weaknesses, and privilege escalation.\nPay special attention to middleware chain ordering — auth middleware that runs after route handlers\nis a critical bypass vulnerability.\nYou output ONLY valid JSON. No prose. No markdown.'

class AuthSpecialist (BaseAgent ):
    name ='auth_specialist'

    def __init__ (self ,llm_client :LLMClient ):
        super ().__init__ (name ='auth_specialist',llm_client =llm_client )
        self ._parse_error :str |None =None 

    def run (self ,context :AgentContext )->AgentResult :
        self ._parse_error =None 
        result =super ().run (context )
        if self ._parse_error is not None :
            result .errors .append (self ._parse_error )
        return result 

    def build_prompt (self ,context :AgentContext ,include_file_contents :bool =True )->str :
        middleware_section =self ._check_middleware_chain (context )
        entry_points_summary =self ._format_entry_points (context .entry_points )
        files_summary =format_context_metadata (context )if not include_file_contents else self ._format_files (context .file_contents )
        return f'\nYou are analyzing a {context .language } application using the {context .framework } framework\nfor authentication and session management vulnerabilities.\n\n## MIDDLEWARE CHAIN (auth bypass analysis)\n{middleware_section }\n\n## ENTRY POINTS\n{entry_points_summary }\n\n## SOURCE FILES\n{files_summary }\n\n## VULNERABILITY CLASSES TO FIND\n1. Missing authentication on sensitive routes (cross-reference entry_points where authentication_required=False)\n2. Session fixation (CWE-384) — session ID not regenerated after login\n3. JWT weaknesses — algorithm confusion ("none"), weak secrets, missing expiry/signature validation\n4. OAuth flaws — missing state parameter, redirect URI bypass, authorization code reuse\n5. Password policy — no minimum length, weak hashing (MD5/SHA1), no rate limiting on login\n6. Privilege escalation — IDOR, role checks bypassable via parameter manipulation\n7. Broken auth — auth bypassable via header manipulation\n\n## OUTPUT FORMAT\nReturn JSON: {{ "findings": [ {{ "file_path", "line_start", "line_end", "function_name", "vulnerability_class", "cwe_id", "owasp_category", "severity", "confidence", "exploitability", "vulnerable_code", "taint_source", "taint_sink", "taint_path", "reasoning", "false_positive_indicators", "remediation_hint" }} ] }}\nIf no findings: {{ "findings": [] }}\n'

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
            self ._parse_error =f'AuthSpecialist parse failed: {e }'
            return []

    def _check_middleware_chain (self ,context :AgentContext )->str :
        if not context .architecture_patterns :
            return 'No middleware chain data available.'
        ap :ArchPattern =context .architecture_patterns 
        order =ap .middleware_order 
        auth_files =ap .auth_middleware_files 
        lines =[f"Middleware execution order: {' → '.join (order )}"]
        lines .append (f"Auth middleware located in: {', '.join (auth_files )}")
        for i ,middleware in enumerate (order ):
            if 'route'in middleware .lower ()or 'handler'in middleware .lower ():
                if i <len (order )-1 :
                    lines .append (f"WARNING: Route handler '{middleware }' appears at position {i } — check if auth middleware runs before this")
        return '\n'.join (lines )

    def _format_entry_points (self ,entry_points :list )->str :
        if not entry_points :
            return 'No entry points.'
        return '\n'.join ((f'- {ep .file_path }:{ep .line_number } auth_required={ep .authentication_required }'for ep in entry_points ))

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
