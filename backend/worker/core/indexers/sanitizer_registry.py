import os 
import re 
import json 
from typing import Dict ,List ,Set ,Optional 
from ..redis_client import redis_client ,REDIS_AVAILABLE 
from ..config import SCAN_TTL ,logger 

class SanitizerRegistry :
    SANITIZER_NAME_PATTERNS =['^sanitize_','^validate_','^escape_','^encode_','^clean_','^strip_','^filter_','^purify_','^normalize_','^hash_','^encrypt_','^decrypt_','^verify_','^check_','^is_valid','_hash$','_escape$','_encode$','_sanitize$']
    AUTH_GUARD_PATTERNS =['@login_required','@requires_auth','@jwt_required','@permission_required','@authenticate','@auth_required','@login_protected','@admin_required','@staff_required','@roles_required','@fresh_login_required','@oidc_require_login']
    FRAMEWORK_SANITIZER_PATTERNS ={'bleach.clean':re .compile ('bleach\\.clean\\s*\\('),'bleach.linkify':re .compile ('bleach\\.linkify\\s*\\('),'markupsafe.escape':re .compile ('(?:markupsafe\\.)?escape\\s*\\('),'markupsafe.Markup':re .compile ('Markup\\s*\\('),'html.escape':re .compile ('html\\.escape\\s*\\('),'cgi.escape':re .compile ('cgi\\.escape\\s*\\('),'urllib.parse.quote':re .compile ('urllib\\.parse\\.quote\\s*\\('),'bcrypt.checkpw':re .compile ('bcrypt\\.checkpw\\s*\\('),'bcrypt.hashpw':re .compile ('bcrypt\\.hashpw\\s*\\('),'hashlib.sha256':re .compile ('hashlib\\.sha256\\s*\\('),'hashlib.sha512':re .compile ('hashlib\\.sha512\\s*\\('),'hashlib.pbkdf2_hmac':re .compile ('hashlib\\.pbkdf2_hmac\\s*\\('),'hmac.compare_digest':re .compile ('hmac\\.compare_digest\\s*\\('),'secrets.compare_digest':re .compile ('secrets\\.compare_digest\\s*\\(')}
    PARAMETERIZED_QUERY_PATTERNS ={'sqlalchemy_execute':re .compile ('(?:session|db|conn|connection)\\.execute\\s*\\([^,]+,\\s*[^)]+\\)'),'django_raw':re .compile ('\\.raw\\s*\\([^,]+,\\s*[^)]+\\)'),'cursor_execute':re .compile ('cursor\\.execute\\s*\\([^,]+,\\s*[^)]+\\)'),'dbapi_execute':re .compile ('\\.execute\\s*\\([^,]+,\\s*[^)]+\\)')}

    def __init__ (self ):
        self .registry ={'custom_sanitizers':[],'auth_guards':[],'framework_sanitizers':[],'parameterized_queries':[],'full_map':{}}

    def _detect_language (self ,filepath :str )->Optional [str ]:
        ext =os .path .splitext (filepath )[1 ].lower ()
        language_map ={'.py':'python','.js':'javascript','.jsx':'javascript','.ts':'typescript','.tsx':'typescript'}
        return language_map .get (ext )

    def _is_sanitizer_by_name (self ,func_name :str )->bool :
        for pattern in self .SANITIZER_NAME_PATTERNS :
            if re .search (pattern ,func_name ,re .IGNORECASE ):
                return True 
        return False 

    def _extract_function_defs (self ,content :str ,filepath :str ,language :str )->List [Dict ]:
        functions =[]
        lines =content .splitlines ()
        if language =='python':
            decorator_stack =[]
            for line_num ,line in enumerate (lines ,1 ):
                stripped =line .strip ()
                if stripped .startswith ('@'):
                    decorator_stack .append (stripped )
                    continue 
                if stripped .startswith ('def '):
                    match =re .match ('def\\s+(\\w+)\\s*\\(',stripped )
                    if match :
                        func_name =match .group (1 )
                        decorators =list (decorator_stack )
                        is_auth_guard =False 
                        for dec in decorators :
                            for pattern in self .AUTH_GUARD_PATTERNS :
                                if re .search (pattern ,dec ):
                                    is_auth_guard =True 
                                    break 
                        functions .append ({'name':func_name ,'line':line_num ,'decorators':decorators ,'is_auth_guard':is_auth_guard })
                    decorator_stack =[]
                elif stripped and (not stripped .startswith ('#')):
                    decorator_stack =[]
        else :
            for line_num ,line in enumerate (lines ,1 ):
                stripped =line .strip ()
                patterns =['function\\s+(\\w+)\\s*\\(','(?:const|let|var)\\s+(\\w+)\\s*=\\s*function','(?:const|let|var)\\s+(\\w+)\\s*=\\s*.*?=>']
                for pattern in patterns :
                    match =re .search (pattern ,stripped )
                    if match :
                        func_name =match .group (1 )
                        functions .append ({'name':func_name ,'line':line_num ,'decorators':[],'is_auth_guard':False })
                        break 
        return functions 

    def _detect_framework_sanitizers (self ,content :str ,filepath :str )->List [str ]:
        found =[]
        for name ,pattern in self .FRAMEWORK_SANITIZER_PATTERNS .items ():
            if pattern .search (content ):
                found .append (name )
        return list (set (found ))

    def _detect_parameterized_queries (self ,content :str ,filepath :str )->List [str ]:
        found =[]
        for name ,pattern in self .PARAMETERIZED_QUERY_PATTERNS .items ():
            if pattern .search (content ):
                found .append (name )
        return list (set (found ))

    def _get_source_files (self ,project_path :str )->List [str ]:
        source_files =[]
        valid_extensions ={'.py','.js','.jsx','.ts','.tsx','.java','.go','.mjs'}
        for root ,dirs ,files in os .walk (project_path ):
            dirs [:]=[d for d in dirs if d not in {'node_modules','venv','.venv','__pycache__','.git','dist','build','.next','target','vendor','third_party'}]
            for file in files :
                ext =os .path .splitext (file )[1 ].lower ()
                if ext in valid_extensions :
                    full_path =os .path .join (root ,file )
                    rel_path =os .path .relpath (full_path ,project_path )
                    source_files .append (rel_path )
        return source_files 

    def build (self ,project_path :str ,scan_id :str )->Dict :
        logger .info (f'[{scan_id }] Building sanitizer registry...')
        source_files =self ._get_source_files (project_path )
        logger .info (f'[{scan_id }] Scanning {len (source_files )} files for sanitizers')
        custom_sanitizers =[]
        auth_guards =[]
        framework_sanitizers =set ()
        parameterized_queries =set ()
        full_map ={}
        for rel_path in source_files :
            language =self ._detect_language (rel_path )
            if not language :
                continue 
            full_path =os .path .join (project_path ,rel_path )
            try :
                with open (full_path ,'r',encoding ='utf-8',errors ='ignore')as f :
                    content =f .read ()
            except Exception as e :
                logger .warning (f'[{scan_id }] Failed to read {rel_path }: {e }')
                continue 
            functions =self ._extract_function_defs (content ,rel_path ,language )
            for func in functions :
                func_name =func ['name']
                is_sanitizer =self ._is_sanitizer_by_name (func_name )
                if is_sanitizer :
                    entry ={'name':func_name ,'file':rel_path ,'line':func ['line'],'role':'SANITIZER'}
                    custom_sanitizers .append (func_name )
                    key =f'{rel_path }::{func_name }'
                    full_map [key ]=entry 
                if func .get ('is_auth_guard'):
                    entry ={'name':func_name ,'file':rel_path ,'line':func ['line'],'role':'AUTH_GUARD'}
                    auth_guards .append (func_name )
                    key =f'{rel_path }::{func_name }'
                    full_map [key ]=entry 
            fw_sanitizers =self ._detect_framework_sanitizers (content ,rel_path )
            framework_sanitizers .update (fw_sanitizers )
            param_queries =self ._detect_parameterized_queries (content ,rel_path )
            for pq in param_queries :
                parameterized_queries .add (f'{rel_path }:{pq }')
        self .registry ={'custom_sanitizers':list (set (custom_sanitizers )),'auth_guards':list (set (auth_guards )),'framework_sanitizers':list (framework_sanitizers ),'parameterized_queries':list (parameterized_queries ),'full_map':full_map }
        if REDIS_AVAILABLE :
            try :
                redis_client .setex (f'{scan_id }:sanitizer_registry',SCAN_TTL ,json .dumps (self .registry ))
                logger .info (f'[{scan_id }] Sanitizer registry stored in Redis')
            except Exception as e :
                logger .error (f'[{scan_id }] Failed to store sanitizer_registry in Redis: {e }')
        else :
            logger .warning (f'[{scan_id }] Redis not available, sanitizer_registry not persisted')
        logger .info (f'[{scan_id }] SanitizerRegistry complete: {len (custom_sanitizers )} sanitizers, {len (auth_guards )} auth guards, {len (framework_sanitizers )} framework sanitizers')
        return self .registry 
