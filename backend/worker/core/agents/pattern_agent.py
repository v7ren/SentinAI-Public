import re 
from typing import Any 
from .base_agent import BaseAgent 
from .models import AgentContext ,AgentFinding ,ArchPattern ,CORSConfig 

class PatternAgent (BaseAgent ):
    FRAMEWORK_PATTERNS ={'python':{'flask':['from\\s+flask\\s+import','Flask\\s*\\('],'fastapi':['from\\s+fastapi\\s+import','FastAPI\\s*\\('],'django':['from\\s+django\\s+import','Django','class\\s+\\w+\\s*\\(models\\.Model\\)'],'sqlalchemy':['from\\s+sqlalchemy\\s+import','SessionLocal'],'pydantic':['from\\s+pydantic\\s+import','class\\s+\\w+\\s*\\(BaseModel\\)']},'javascript':{'express':['from\\s+["\\\']express["\\\']','require\\s*\\(\\s*["\\\']express["\\\']'],'nextjs':['from\\s+["\\\']next["\\\']','getServerSideProps'],'prisma':['from\\s+@prisma\\/client','new\\s+PrismaClient'],'sequelize':['from\\s+sequelize','Sequence\\.define']},'java':{'spring':['@SpringBootApplication','@RestController','springframework'],'hibernate':['@Entity','@Table','jakarta\\.persisten']}}
    MIDDLEWARE_PATTERNS ={'express':['app\\.use\\s*\\(\\s*(?:\\/\\*.*?\\*\\/\\s*)?(?:cors|auth|jsonwebtoken|express\\.json|express\\.urlencoded)','app\\.use\\s*\\(\\s*(?:authentication|authorize|isAdmin)'],'flask':['@app\\.before_request','@app\\.teardown_request','flask\\.g\\.'],'fastapi':['@app\\.middleware\\(http\\)','app\\.add_middleware']}
    ORM_PATTERNS ={'sqlalchemy':['class\\s+\\w+\\s*\\(Base\\)','self\\.\\w+\\s*=\\s*Column','SeessionLocal\\(\\)'],'prisma':['prisma\\.\\w+','PrismaClient'],'sequelize':['Sequence\\.define','sequlize\\.define']}

    def __init__ (self ,*args ,**kwargs ):
        name =kwargs .pop ('name','PatternAgent')
        super ().__init__ (*args ,name =name ,**kwargs )

    def build_prompt (self ,context :AgentContext ,include_file_contents :bool =True )->str :
        return f'You are an architecture analyst tasked with identifying patterns in this codebase.\n\n## Instructions\n\nIdentify the following architectural patterns:\n\n1. **Architecture Pattern**: "MVC", "microservice", "monolith", "serverless"\n\n2. **Middleware Chain** (if applicable):\n   - List middleware functions in EXECUTION ORDER\n   - Note which files contain auth middleware\n\n3. **ORM Usage**:\n   - sqlalchemy, prisma, sequelize, hibernate, etc.\n   - Or null if no ORM detected\n\n4. **Template Engine** (if applicable):\n   - jinja2, handlebars, pug, react, vue, etc.\n   - Or null if no template engine\n\n5. **CORS Configuration**:\n   - allow_origin, allow_methods, allow_headers\n   - Whether credentials are allowed\n\n6. **Service Layer**: Files containing service classes\n\n7. **Repository Layer**: Files containing repository/data access classes\n\n8. **Dependency Injection**: Any DI container detected (e.g., "inversify", "hilt")\n\n## Output Format\n\nReturn a JSON object matching ArchPattern:\n{{\n  "pattern_type": "MVC",\n  "middleware_order": ["cors", "auth", "logging"],\n  "auth_middleware_files": ["middleware/auth.py"],\n  "orm_type": "sqlalchemy",\n  "template_engine": "jinja2",\n  "cors_config": {{\n    "allow_origin": "*",\n    "allow_methods": ["GET", "POST"],\n    "allow_headers": ["Content-Type"],\n    "expose_headers": [],\n    "max_age": 3600,\n    "allow_credentials": false\n  }},\n  "service_layer_files": ["services/user_service.py"],\n  "repository_files": ["repositories/user_repo.py"],\n  "di_container": null\n}}\n\n## Context\n\nLanguage: {context .language }\nFramework: {context .framework }\n'

    def parse_response (self ,response :str )->list [AgentFinding ]:
        import json 
        findings =[]
        try :
            data =json .loads (response )
            arch_pattern =ArchPattern (pattern_type =data .get ('pattern_type','unknown'),middleware_order =data .get ('middleware_order',[]),auth_middleware_files =data .get ('auth_middleware_files',[]),orm_type =data .get ('orm_type'),template_engine =data .get ('template_engine'),cors_config =data .get ('cors_config'),service_layer_files =data .get ('service_layer_files',[]),repository_files =data .get ('repository_files',[]),di_container =data .get ('di_container'))
            finding =AgentFinding (finding_id =f'PATTERN-{self ._generate_finding_id (data )}',agent_source =self .name ,file_path ='',line_start =0 ,line_end =0 ,function_name ='',vulnerability_class ='Architecture Pattern',cwe_id ='',severity ='info',reasoning =f'Detected architecture pattern: {arch_pattern .pattern_type }',metadata ={'arch_pattern':arch_pattern .__dict__ })
            findings .append (finding )
        except json .JSONDecodeError :
            pass 
        return findings 

    def _generate_finding_id (self ,data :dict )->str :
        import hashlib 
        key =data .get ('pattern_type','unknown')
        return hashlib .md5 (key .encode ()).hexdigest ()[:8 ]

    def detect_patterns_from_patterns (self ,context :AgentContext )->ArchPattern |None :
        patterns_found :dict [str ,list [str ]]={}
        for file_path ,content in context .file_contents .items ():
            for lang ,frameworks in self .FRAMEWORK_PATTERNS .items ():
                for fw_name ,fw_patterns in frameworks .items ():
                    for pattern in fw_patterns :
                        if re .search (pattern ,content ,re .IGNORECASE ):
                            key =f'{lang }:{fw_name }'
                            if key not in patterns_found :
                                patterns_found [key ]=[]
                            patterns_found [key ].append (file_path )
        if 'python:flask'in patterns_found :
            orm_type ='none'
            for pattern_list in self .ORM_PATTERNS .values ():
                for pattern in pattern_list :
                    for file_path ,content in context .file_contents .items ():
                        if re .search (pattern ,content ,re .IGNORECASE ):
                            orm_type =list (self .ORM_PATTERNS .keys ())[list (self .ORM_PATTERNS .values ()).index (pattern_list )]
                            break 
            return ArchPattern (pattern_type ='MVC',middleware_order =['cors','auth'],auth_middleware_files =[],orm_type =orm_type if orm_type !='none'else None ,template_engine ='jinja2',cors_config =None ,service_layer_files =[],repository_files =[],di_container =None )
        return None 

    def extract_middleware_order (self ,context :AgentContext )->list [str ]:
        middleware_order =[]
        if context .language =='javascript'and context .framework =='express':
            for file_path ,content in context .file_contents .items ():
                for pattern in self .MIDDLEWARE_PATTERNS ['express']:
                    matches =re .finditer (pattern ,content )
                    for match in matches :
                        middleware_name =self ._extract_middleware_name (match .group (0 ))
                        if middleware_name and middleware_name not in middleware_order :
                            middleware_order .append (middleware_name )
        return middleware_order 

    def _extract_middleware_name (self ,match_text :str )->str |None :
        patterns =['cors','auth','jsonwebtoken','express\\.json','express\\.urlencoded','logging','rateLimit']
        for pattern in patterns :
            if re .search (pattern ,match_text ,re .IGNORECASE ):
                return pattern 
        return None 

class CORSConfig :

    def __init__ (self ,allow_origin :str ='*',allow_methods :list [str ]|None =None ):
        self .allow_origin =allow_origin 
        self .allow_methods =allow_methods or ['GET','POST','PUT','DELETE']
        self .allow_headers =['Content-Type','Authorization']
        self .expose_headers :list [str ]=[]
        self .max_age :int |None =None 
        self .allow_credentials =False 

    @classmethod 
    def from_config (cls ,config :dict )->'CORSConfig':
        return cls (allow_origin =config .get ('allow_origin','*'),allow_methods =config .get ('allow_methods'))
