import re 
from typing import Any 
from .base_agent import BaseAgent 
from .models import AgentContext ,AgentFinding ,EntryPoint ,EntryParameter 

class ReconAgent (BaseAgent ):
    FRAMEWORK_PATTERNS ={'python':{'flask':['@\\w+\\s*\\(\\s*["\\\']([^"\\\']+)["\\\']\\s*\\)','def\\s+(\\w+)\\s*\\([^)]*request[^)]*\\)'],'fastapi':['@(\\w+)\\s*\\(\\s*["\\\']([^"\\\']+)["\\\']\\s*\\)','async\\s+def\\s+(\\w+)\\s*\\([^)]*request[^)]*\\)','def\\s+(\\w+)\\s*\\([^)]*request[^)]*\\)'],'django':['def\\s+(\\w+)\\s*\\([^)]*request[^)]*\\)','@(?:method_decorator|require_\\w+)\\s*\\('],'python_generic':['request\\.(args|form|json|data|cookies|headers)\\[','request\\.(args|form|json|data|cookies|headers)\\.get\\(']},'javascript':{'express':['app\\.(get|post|put|delete|patch)\\s*\\(\\s*["\\\']([^"\\\']+)["\\\']\\s*,','r\\.(get|post|put|delete|patch)\\s*\\(\\s*["\\\']([^"\\\']+)["\\\']\\s*,','async\\s*\\(?\\s*req\\s*,?\\s*res\\s*\\)?\\s*=>','function\\s*\\(\\s*req\\s*,?\\s*res\\s*\\)'],'fastify':['server\\.(get|post|put|delete|patch)\\s*\\(\\s*["\\\']([^"\\\']+)["\\\']\\s*,','fastify\\.(get|post|put|delete|patch)\\s*\\(\\s*["\\\']([^"\\\']+)["\\\']\\s*,'],'node_generic':['req\\.(body|params|query|headers|cookies|file)\\[','req\\.(body|params|query|headers|cookies|file)\\.get\\(']},'java':{'spring':['@(?:GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\\s*\\(\\s*["\\\']([^"\\\']+)["\\\']','public\\s+(?:async\\s+)?\\w+\\s+(\\w+)\\s*\\([^)]*HttpServletRequest']},'go':{'gorilla':['mux\\.NewRouter\\(\\)\\.([A-Za-z]+)\\s*\\(\\s*["\\\']([^"\\\']+)["\\\']\\s*,','func\\s+(\\w+)\\s*\\(\\s*w\\s+http\\.ResponseWriter,\\s*r\\s*\\*http\\.Request']}}
    ENTRY_TYPE_PATTERNS ={'http':['request\\.(body|params|query|headers|cookies|args|form|json)','req\\.(body|params|query|headers|cookies)'],'cli':['argparse\\.ArgumentParser','click\\.\\(.*@click\\.command','cobra\\.Command','parser\\.add_argument'],'mq':['kafka\\.Consumer','RabbitMQ','pika\\.BasicConsumer','sqs\\.receive_message','@\\.subscribe'],'file':['open\\s*\\([^)]*\\+','os\\.path\\.(join|join)\\s*\\([^)]*\\+','pathlib\\.Path\\s*\\([^)]*\\+'],'env':['os\\.environ\\[[\\\'"]','os\\.getenv\\s*\\(','process\\.env\\.'],'webhook':['webhook','callback','webhook_handler']}

    def __init__ (self ,*args ,**kwargs ):
        name =kwargs .pop ('name','ReconAgent')
        super ().__init__ (*args ,name =name ,**kwargs )

    def build_prompt (self ,context :AgentContext ,include_file_contents :bool =True )->str :
        return f'You are a penetration tester tasked with mapping the attack surface of this application.\nYour job is to identify every location where untrusted external data can enter the system.\n\n## Instructions\n\n1. Identify all ENTRY POINTS where external data enters:\n   - HTTP routes (REST APIs, GraphQL endpoints, web hooks)\n   - CLI argument parsers\n   - Message queue consumers (Kafka, RabbitMQ, SQS)\n   - File path readers (where path comes from user input)\n   - Environment variable readers (os.environ, process.env)\n   - IPC handlers\n\n2. For each entry point, determine:\n   - entry_type: "http", "cli", "mq", "file", "env", "ipc", "webhook"\n   - file_path: Source file where entry point is defined\n   - line_number: Line number of the route/handler definition\n   - function_name: Name of the handler function\n   - handler_function: The actual function that processes the request\n   - parameters: List of parameter names that accept external data\n   - authentication_required: True if auth middleware is applied BEFORE this route\n   - authorization_required: True if permission checks exist\n   - rate_limited: True if rate limiting is configured\n   - framework: Detected framework (express, flask, fastapi, django, spring, etc.)\n\n3. Pay special attention to:\n   - Routes WITHOUT authentication (flag as HIGH priority)\n   - Request parameters from user-controlled sources (req.body, req.params, query strings)\n   - Indirect data sources (environment variables, config files, message queues)\n\n## Output Format\n\nReturn a JSON array of EntryPoint objects:\n[\n  {{\n    "entry_type": "http",\n    "file_path": "routes/api.py",\n    "line_number": 42,\n    "function_name": "login",\n    "handler_function": "handle_login",\n    "parameters": ["username", "password"],\n    "authentication_required": false,\n    "authorization_required": false,\n    "rate_limited": true,\n    "framework": "flask"\n  }}\n]\n\n## Context\n\nLanguage: {context .language }\nFramework: {context .framework }\n\nFiles analyzed: {list (context .file_contents .keys ())[:10 ]}...\n\nScan mode: {context .scan_mode .value }\n'

    def parse_response (self ,response :str )->list [AgentFinding ]:
        import json 
        findings =[]
        try :
            data =json .loads (response )
            if isinstance (data ,dict )and 'entry_points'in data :
                entry_points =data ['entry_points']
            elif isinstance (data ,list ):
                entry_points =data 
            else :
                return findings 
            for ep_data in entry_points :
                finding =AgentFinding (finding_id =f'RECON-{self ._generate_finding_id (ep_data )}',agent_source =self .name ,file_path =ep_data .get ('file_path',''),line_start =ep_data .get ('line_number',0 ),line_end =ep_data .get ('line_number',0 )+1 ,function_name =ep_data .get ('function_name',''),vulnerability_class ='Entry Point',cwe_id ='CWE-200'if not ep_data .get ('authentication_required',True )else '',severity ='high'if not ep_data .get ('authentication_required',True )else 'info',reasoning =f"Entry point detected: {ep_data .get ('entry_type','unknown')}",taint_source =self ._identify_taint_source (ep_data ),metadata ={'entry_point':{'entry_type':ep_data .get ('entry_type'),'parameters':ep_data .get ('parameters',[]),'authentication_required':ep_data .get ('authentication_required',False ),'authorization_required':ep_data .get ('authorization_required',False )}})
                findings .append (finding )
        except json .JSONDecodeError as e :
            pass 
        return findings 

    def run (self ,context :AgentContext )->Any :
        result =super ().run (context )
        entry_points =[]
        for finding in result .findings :
            if 'entry_point'in finding .metadata :
                ep_data =finding .metadata ['entry_point']
                ep =EntryPoint (entry_type =ep_data .get ('entry_type','unknown'),file_path =finding .file_path ,line_number =finding .line_start ,function_name =finding .function_name ,handler_function =finding .function_name ,parameters =ep_data .get ('parameters',[]),authentication_required =ep_data .get ('authentication_required',False ),authorization_required =ep_data .get ('authorization_required',False ),rate_limited =ep_data .get ('rate_limited',False ),framework =context .framework )
                entry_points .append (ep )
        return (result ,entry_points )

    def _generate_finding_id (self ,ep_data :dict )->str :
        import hashlib 
        key =f"{ep_data .get ('file_path','')}:{ep_data .get ('line_number',0 )}:{ep_data .get ('function_name','')}"
        return hashlib .md5 (key .encode ()).hexdigest ()[:8 ]

    def _identify_taint_source (self ,ep_data :dict )->str |None :
        params =ep_data .get ('parameters',[])
        if not params :
            return None 
        entry_type =ep_data .get ('entry_type','http')
        location_map ={'http':'req.{}'.format (params [0 ]if params else 'body'),'cli':'args.{}'.format (params [0 ]if params else 'input'),'mq':'message.body.{}'.format (params [0 ]if params else 'data'),'file':'user_provided_path','env':'os.environ.{}'.format (params [0 ]if params else 'VAR')}
        return location_map .get (entry_type ,'unknown_source')

    def detect_entry_points_from_patterns (self ,context :AgentContext )->list [EntryPoint ]:
        entry_points =[]
        for file_path ,content in context .file_contents .items ():
            detected =self ._scan_file_for_entry_points (file_path ,content ,context )
            entry_points .extend (detected )
        return entry_points 

    def _scan_file_for_entry_points (self ,file_path :str ,content :str ,context :AgentContext )->list [EntryPoint ]:
        entry_points =[]
        lines =content .split ('\n')
        lang =context .language 
        patterns =self .FRAMEWORK_PATTERNS .get (lang ,{}).get (context .framework ,self .FRAMEWORK_PATTERNS .get (lang ,{}).get ('generic',[]))
        for line_num ,line in enumerate (lines ,1 ):
            for pattern in patterns :
                matches =re .finditer (pattern ,line ,re .IGNORECASE )
                for match in matches :
                    function_name =match .group (1 )if match .lastindex and match .lastindex >=1 else f'handler_{line_num }'
                    entry_point =EntryPoint (entry_type ='http',file_path =file_path ,line_number =line_num ,function_name =function_name ,handler_function =function_name ,parameters =[],authentication_required =False ,authorization_required =False ,rate_limited =False ,framework =context .framework )
                    entry_points .append (entry_point )
                    break 
        return entry_points 
