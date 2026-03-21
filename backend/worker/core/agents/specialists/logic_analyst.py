from __future__ import annotations 
import json 
import uuid 
from typing import Any 
from backend .worker .core .agents .base_agent import BaseAgent ,format_files_for_prompt ,format_context_metadata 
from backend .worker .core .agents .models import AgentContext ,AgentFinding ,AgentResult ,Exploitability ,Severity 
from backend .worker .core .llm_client import LLMClient 
SYSTEM_PROMPT ='You are a senior penetration tester specializing in business logic vulnerabilities.\nUnlike injection or crypto bugs, logic flaws require understanding what the application is SUPPOSED to do\nand finding ways to abuse the intended functionality. You output ONLY valid JSON. No prose. No markdown.'

class LogicAnalyst (BaseAgent ):
    name ='logic_analyst'

    def __init__ (self ,llm_client :LLMClient ):
        super ().__init__ (name ='logic_analyst',llm_client =llm_client )
        self ._parse_error :str |None =None 

    def run (self ,context :AgentContext )->AgentResult :
        self ._parse_error =None 
        result =super ().run (context )
        if self ._parse_error is not None :
            result .errors .append (self ._parse_error )
        return result 

    def build_prompt (self ,context :AgentContext ,include_file_contents :bool =True )->str :
        files_summary =format_context_metadata (context )if not include_file_contents else self ._format_files (context .file_contents )
        return f'\nYou are a senior penetration tester specializing in business logic vulnerabilities.\n\nFor each piece of code, ask yourself:\n1. What is this code trying to accomplish for the business?\n2. What assumptions does it make about user behavior?\n3. How could an attacker violate those assumptions?\n4. Is there an ownership check before returning user-specific data?\n5. Is there a multi-step flow where steps can be reordered or skipped?\n6. Is there a numeric value (price, quantity, discount) that a user controls?\n7. Is there a check-then-act pattern that could be raced?\n\nFocus especially on:\n- Any place where a user-supplied ID is used to fetch data without verifying that the authenticated user owns that resource\n- Any place where a workflow has numbered steps and the application trusts the client to follow the correct order\n- Any place where a user-controlled value affects pricing, permissions, or quotas\n\n## VULNERABILITY CLASSES\n- IDOR (CWE-639): resource IDs from user input without ownership verification\n- Race conditions (CWE-362): check-then-act without atomic operations\n- Business logic bypasses: skippable workflow steps, price manipulation, coupon abuse\n- Mass assignment (CWE-915): ORM models accepting all fields from user input\n- TOCTOU: auth checks separated from resource access\n\n## SOURCE FILES\n{files_summary }\n\n## OUTPUT FORMAT\nReturn JSON: {{ "findings": [ {{ "file_path", "line_start", "line_end", "function_name", "vulnerability_class", "cwe_id", "severity", "confidence", "exploitability", "vulnerable_code", "reasoning", "false_positive_indicators", "remediation_hint" }} ] }}\nIf no findings: {{ "findings": [] }}\n'

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
            self ._parse_error =f'LogicAnalyst parse failed: {e }'
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
