from __future__ import annotations 
import json 
import uuid 
from typing import Any 
from backend .worker .core .agents .base_agent import BaseAgent ,format_files_for_prompt ,format_context_metadata 
from backend .worker .core .agents .models import AgentContext ,AgentFinding ,AgentResult ,Exploitability ,Severity 
from backend .worker .core .llm_client import LLMClient 
SYSTEM_PROMPT ='You are a senior security engineer specializing in LLM-powered applications.\nYour job is to find vulnerabilities specific to applications that use Large Language Models:\nprompt injection (direct and indirect), insecure output handling, sensitive data exposure in prompts,\ninsecure tool use, and training data poisoning vectors.\nYou output ONLY valid JSON. No prose. No markdown. No explanation outside the JSON.'

class LLMSecurityAgent (BaseAgent ):
    name ='llm_security_agent'

    def __init__ (self ,llm_client :LLMClient ):
        super ().__init__ (name ='llm_security_agent',llm_client =llm_client )
        self ._parse_error :str |None =None 

    def run (self ,context :AgentContext )->AgentResult :
        self ._parse_error =None 
        result =super ().run (context )
        if self ._parse_error is not None :
            result .errors .append (self ._parse_error )
        return result 

    def build_prompt (self ,context :AgentContext ,include_file_contents :bool =True )->str :
        files_summary =format_context_metadata (context )if not include_file_contents else self ._format_files (context .file_contents )
        entry_summary =self ._format_entry_points (context .entry_points )
        return f"""\nYou are analyzing a {context .language } application that uses LLM APIs (OpenAI, Anthropic, LangChain, etc.)\nfor LLM-specific security vulnerabilities.\n\n## ENTRY POINTS\n{entry_summary }\n\n## SOURCE FILES\n{files_summary }\n\n## VULNERABILITY CLASSES TO FIND\n1. **Direct Prompt Injection (CWE-74)**: User input passed directly into LLM system or user prompt without sanitization/delimitation; attacker can override instructions.\n2. **Indirect Prompt Injection**: External content (web pages, documents, emails) fetched and included in prompts without clear boundaries; attacker controls external content.\n3. **LLM Output Injection / Insecure Output Handling**: LLM output rendered as HTML, executed as code, or used in SQL/shell without sanitization.\n4. **Insecure Tool Use**: LLM given tools (code execution, file access, API calls) without guardrails; user can induce dangerous tool calls via prompt.\n5. **Sensitive Data in Prompts**: PII, secrets, or credentials included in prompts that may be logged or leak via side channels.\n6. **Missing Output Validation**: LLM response used for access control or business logic without validation.\n\n## DETECTION SIGNALS\n- Look for: openai.ChatCompletion, anthropic.messages, langchain, llm.invoke, chat.completions.create, messages.create\n- Trace what data flows into "messages", "system", "user" content\n- Check if user-controlled or external content is concatenated into prompts\n- Check if LLM output is passed to eval(), exec(), innerHTML, or SQL/command execution\n\n## OUTPUT FORMAT\nReturn a JSON object with this exact structure. No other text.\n{{\n  "findings": [\n    {{\n      "file_path": "path/to/file.py",\n      "line_start": 42,\n      "line_end": 44,\n      "function_name": "chat_handler",\n      "vulnerability_class": "Direct Prompt Injection",\n      "cwe_id": "CWE-74",\n      "owasp_category": "LLM01",\n      "severity": "high",\n      "confidence": 0.9,\n      "exploitability": "confirmed",\n      "vulnerable_code": "messages.append({{'role':'user','content': user_input}})",\n      "taint_source": "user_input from request.body",\n      "taint_sink": "openai.ChatCompletion.create(messages=...)",\n      "taint_path": ["request.body -> user_input", "user_input -> messages[].content"],\n      "reasoning": "User input is appended directly to chat messages without delimiter or sanitization; attacker can inject system-level instructions.",\n      "false_positive_indicators": [],\n      "remediation_hint": "Use clear delimiters and instruct the model to ignore content outside user message block; or sanitize/detect injection attempts."\n    }}\n  ]\n}}\n\nIf no LLM-specific vulnerabilities are found, return: {{"findings": []}}\n"""

    def parse_response (self ,response :str )->list [AgentFinding ]:
        try :
            text =response .strip ()
            if '```'in text :
                for part in text .split ('```'):
                    part =part .strip ()
                    if part .startswith ('json'):
                        part =part [4 :].strip ()
                    if part .startswith ('{'):
                        text =part 
                        break 
            data =json .loads (text )
            findings =[]
            for raw in data .get ('findings',[]):
                severity =self ._parse_severity (raw .get ('severity','medium'))
                exploitability =self ._parse_exploitability (raw .get ('exploitability','possible'))
                finding =AgentFinding (finding_id =str (uuid .uuid4 ()),agent_source =self .name ,file_path =raw .get ('file_path',''),line_start =int (raw .get ('line_start',0 )),line_end =int (raw .get ('line_end',0 )),function_name =raw .get ('function_name',''),vulnerability_class =raw .get ('vulnerability_class','LLM Vulnerability'),cwe_id =raw .get ('cwe_id',''),owasp_category =raw .get ('owasp_category',''),severity =severity ,confidence =self ._parse_confidence (raw .get ('confidence',0.5 )),exploitability =exploitability ,vulnerable_code =raw .get ('vulnerable_code',''),taint_source =raw .get ('taint_source'),taint_sink =raw .get ('taint_sink'),taint_path =raw .get ('taint_path'),chain_id =None ,chain_position =None ,reasoning =raw .get ('reasoning',''),false_positive_indicators =raw .get ('false_positive_indicators',[]),remediation_hint =raw .get ('remediation_hint',''))
                findings .append (finding )
            return findings 
        except (json .JSONDecodeError ,KeyError ,TypeError )as e :
            self ._parse_error =f'LLMSecurityAgent parse failed: {e }'
            return []

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

    def _format_files (self ,file_contents :dict [str ,str ])->str :
        return format_files_for_prompt (file_contents )

    def _format_entry_points (self ,entry_points :list )->str :
        if not entry_points :
            return 'No entry points detected.'
        return '\n'.join ((f'- {ep .entry_type } | {ep .file_path }:{ep .line_number } | {ep .handler_function }'for ep in entry_points [:20 ]))
