import json 
import logging 
from typing import Any 
from .models import AgentContext ,DeduplicatedFinding ,Severity ,SkepticVerdict 
logger =logging .getLogger (__name__ )
SYSTEM_PROMPT ='You are a senior security reviewer playing devil\'s advocate. For each finding, argue why it might NOT be a real vulnerability.\nCheck ALL of the following and output ONLY valid JSON:\n\n1. SANITIZATION: Is there a sanitizer between source and sink that the detector missed? Check the sanitizer registry and full function context.\n\n2. DEAD CODE: Is this code path actually reachable? Check if the location is in dead/unreachable code.\n\n3. FRAMEWORK PROTECTION: Does the framework automatically mitigate this? (e.g. Django ORM parameterizes, React escapes JSX)\n\n4. UPSTREAM VALIDATION: Is input validated before reaching this function? Look for validation decorators, middleware, guards.\n\n5. AUTHENTICATION GATE: Is the endpoint actually protected? Check middleware chain.\n\n6. TYPE CONSTRAINT: Does the type system prevent the attack? (e.g. integer parameter cannot be SQL injection)\n\n7. CONTEXT CONSTRAINT: Is the code only reachable in a context where the attack is impossible?\n\nOutput a JSON object with exactly: {"verdict": "confirmed"|"downgraded"|"rejected", "reasoning": "...", "surviving_risk": "..." (only if downgraded)}.\nIf the finding is clearly valid and none of the above apply, use verdict "confirmed". If mitigations exist but some risk remains, use "downgraded". If the finding is a false positive, use "rejected".'
SEVERITY_ORDER =[Severity .CRITICAL ,Severity .HIGH ,Severity .MEDIUM ,Severity .LOW ,Severity .INFO ]

def _severity_one_level_lower (s :Severity )->Severity :
    try :
        i =SEVERITY_ORDER .index (s )
        if i +1 <len (SEVERITY_ORDER ):
            return SEVERITY_ORDER [i +1 ]
    except (ValueError ,AttributeError ):
        pass 
    return Severity .LOW 

class SkepticAgent :
    CONFIRMED_BOOST =0.1 
    REJECTION_RATE_WARN_THRESHOLD =0.2 

    def __init__ (self ,llm_client :Any |None =None ):
        self .llm_client =llm_client 

    def run (self ,findings :list [DeduplicatedFinding ],context :AgentContext )->list [DeduplicatedFinding ]:
        if not findings :
            return []
        verdicts :list [SkepticVerdict ]=[]
        output :list [DeduplicatedFinding ]=[]
        for f in findings :
            verdict =self ._review_one (f ,context )
            verdicts .append (verdict )
            if verdict .verdict =='rejected':
                continue 
            if verdict .verdict =='confirmed':
                new_conf =min (1.0 ,f .confidence +self .CONFIRMED_BOOST )
                output .append (DeduplicatedFinding (finding_id =f .finding_id ,agent_source =f .agent_source ,file_path =f .file_path ,line_start =f .line_start ,line_end =f .line_end ,function_name =f .function_name ,vulnerability_class =f .vulnerability_class ,cwe_id =f .cwe_id ,owasp_category =f .owasp_category ,severity =f .severity ,confidence =new_conf ,exploitability =f .exploitability ,vulnerable_code =f .vulnerable_code ,taint_source =f .taint_source ,taint_sink =f .taint_sink ,taint_path =f .taint_path ,chain_id =f .chain_id ,chain_position =f .chain_position ,reasoning =f .reasoning +'\n[Skeptic confirmed] '+verdict .skeptic_reasoning ,false_positive_indicators =f .false_positive_indicators ,remediation_hint =f .remediation_hint ,metadata =f .metadata ,contributing_agents =f .contributing_agents ,duplicate_count =f .duplicate_count ))
            else :
                new_severity =_severity_one_level_lower (f .severity if isinstance (f .severity ,Severity )else Severity (f .severity )if isinstance (f .severity ,str )else Severity .MEDIUM )
                surviving =verdict .surviving_risk or verdict .skeptic_reasoning 
                output .append (DeduplicatedFinding (finding_id =f .finding_id ,agent_source =f .agent_source ,file_path =f .file_path ,line_start =f .line_start ,line_end =f .line_end ,function_name =f .function_name ,vulnerability_class =f .vulnerability_class ,cwe_id =f .cwe_id ,owasp_category =f .owasp_category ,severity =new_severity ,confidence =f .confidence ,exploitability =f .exploitability ,vulnerable_code =f .vulnerable_code ,taint_source =f .taint_source ,taint_sink =f .taint_sink ,taint_path =f .taint_path ,chain_id =f .chain_id ,chain_position =f .chain_position ,reasoning =f .reasoning +'\n[Skeptic downgraded] '+verdict .skeptic_reasoning +(' Surviving risk: '+surviving if surviving else ''),false_positive_indicators =f .false_positive_indicators ,remediation_hint =f .remediation_hint ,metadata =f .metadata ,contributing_agents =f .contributing_agents ,duplicate_count =f .duplicate_count ))
        rate =self ._rejection_rate (verdicts )
        if rate >self .REJECTION_RATE_WARN_THRESHOLD :
            logger .warning ('Skeptic Agent rejection rate %.1f%% > 20%%. Prompt may need tuning.',rate *100 )
        return output 

    def _review_one (self ,finding :DeduplicatedFinding ,context :AgentContext )->SkepticVerdict :
        func_ctx =self ._get_function_context (finding ,context )
        sanitizers =getattr (context ,'sanitizer_registry',None )or {}
        sanitizer_str ='\n'.join ((f'- {k }: {v }'for k ,v in (sanitizers .items ()if isinstance (sanitizers ,dict )else [])))
        dead ='Yes'if self ._in_dead_code (finding ,context )else 'No'
        prompt =f"""Finding:\n- File: {finding .file_path } lines {finding .line_start }-{finding .line_end }\n- Class: {finding .vulnerability_class }\n- Reasoning: {finding .reasoning }\n- Vulnerable code: {finding .vulnerable_code }\n\nFull function context (±20 lines):\n```\n{func_ctx }\n```\n\nSanitizer registry:\n{sanitizer_str or 'None'}\n\nIs this finding in dead code? {dead }\n\nOutput JSON only: {{"verdict": "confirmed"|"downgraded"|"rejected", "reasoning": "...", "surviving_risk": "..."}}"""
        if not self .llm_client :
            return SkepticVerdict (finding_id =finding .finding_id ,verdict ='confirmed',confidence_adjustment =self .CONFIRMED_BOOST ,skeptic_reasoning ='No LLM client; defaulting to confirmed.',surviving_risk =None )
        try :
            resp =self .llm_client .complete (prompt =prompt ,system_prompt =SYSTEM_PROMPT )
            text =getattr (resp ,'content',resp )if hasattr (resp ,'content')else str (resp )
            data =json .loads (text .strip ().split ('\n')[0 ]if '\n'in text else text )
            v =(data .get ('verdict')or 'confirmed').lower ()
            if v not in ('confirmed','downgraded','rejected'):
                v ='confirmed'
            return SkepticVerdict (finding_id =finding .finding_id ,verdict =v ,confidence_adjustment =self .CONFIRMED_BOOST if v =='confirmed'else 0.0 ,skeptic_reasoning =data .get ('reasoning','')[:500 ],surviving_risk =data .get ('surviving_risk'))
        except (json .JSONDecodeError ,KeyError ,TypeError )as e :
            logger .debug ('Skeptic parse error: %s',e )
            return SkepticVerdict (finding_id =finding .finding_id ,verdict ='confirmed',confidence_adjustment =self .CONFIRMED_BOOST ,skeptic_reasoning ='Parse failed; defaulting to confirmed.',surviving_risk =None )

    def _get_function_context (self ,finding :DeduplicatedFinding ,context :AgentContext )->str :
        contents =getattr (context ,'file_contents',None )or {}
        text =contents .get (finding .file_path )or ''
        lines =text .splitlines ()
        if not lines :
            return ''
        lo =max (0 ,finding .line_start -1 -20 )
        hi =min (len (lines ),finding .line_end +20 )
        return '\n'.join (lines [lo :hi ])

    def _in_dead_code (self ,finding :DeduplicatedFinding ,context :AgentContext )->bool :
        dead_map =getattr (context ,'dead_code_map',None )or {}
        region =dead_map .get (finding .file_path )
        if not region :
            return False 
        line_start =getattr (region ,'line_start',None )or (region .get ('line_start')if isinstance (region ,dict )else None )
        line_end =getattr (region ,'line_end',None )or (region .get ('line_end')if isinstance (region ,dict )else None )
        if line_start is None or line_end is None :
            return True 
        return not (finding .line_end <line_start or line_end <finding .line_start )

    def _rejection_rate (self ,verdicts :list [SkepticVerdict ])->float :
        if not verdicts :
            return 0.0 
        rejected =sum ((1 for v in verdicts if v .verdict =='rejected'))
        return rejected /len (verdicts )
