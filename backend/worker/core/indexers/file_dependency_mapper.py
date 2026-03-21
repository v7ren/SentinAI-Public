import os 
import re 
import json 
from typing import Dict ,List ,Set ,Optional 
from ..redis_client import redis_client ,REDIS_AVAILABLE 
from ..config import SCAN_TTL ,logger 

class FileDependencyMapper :
    IMPORT_PATTERNS ={'python':{'from_import':re .compile ('^from\\s+([\\w.]+)\\s+import',re .MULTILINE ),'direct_import':re .compile ('^import\\s+([\\w.]+)',re .MULTILINE )},'javascript':{'require':re .compile ('require\\s*\\(\\s*[\'\\"]([^\'\\"]+)[\'\\"]\\s*\\)'),'es6_import':re .compile ('import\\s+(?:.*?\\s+from\\s+)?[\'\\"]([^\'\\"]+)[\'\\"]'),'dynamic_import':re .compile ('import\\s*\\(\\s*[\'\\"]([^\'\\"]+)[\'\\"]\\s*\\)')},'typescript':{'require':re .compile ('require\\s*\\(\\s*[\'\\"]([^\'\\"]+)[\'\\"]\\s*\\)'),'es6_import':re .compile ('import\\s+(?:.*?\\s+from\\s+)?[\'\\"]([^\'\\"]+)[\'\\"]'),'dynamic_import':re .compile ('import\\s*\\(\\s*[\'\\"]([^\'\\"]+)[\'\\"]\\s*\\)')},'java':{'import':re .compile ('^import\\s+([\\w.]+);',re .MULTILINE )},'go':{'import':re .compile ('^import\\s*(?:\\([\\s\\S]*?\\"([^\\"]+)\\".*?\\)|\\"([^\\"]+)\\")',re .MULTILINE )}}

    def __init__ (self ):
        self .file_deps :Dict [str ,Dict ]={}

    def _detect_language (self ,filepath :str )->Optional [str ]:
        ext =os .path .splitext (filepath )[1 ].lower ()
        language_map ={'.py':'python','.js':'javascript','.jsx':'javascript','.ts':'typescript','.tsx':'typescript','.java':'java','.go':'go'}
        return language_map .get (ext )

    def _extract_imports (self ,content :str ,language :str )->List [str ]:
        imports =[]
        patterns =self .IMPORT_PATTERNS .get (language ,{})
        if language =='python':
            for match in patterns .get ('from_import',re .compile ('$^')).finditer (content ):
                imports .append (match .group (1 ))
            for match in patterns .get ('direct_import',re .compile ('$^')).finditer (content ):
                imports .append (match .group (1 ))
        elif language in ('javascript','typescript'):
            for match in patterns .get ('require',re .compile ('$^')).finditer (content ):
                imports .append (match .group (1 ))
            for match in patterns .get ('es6_import',re .compile ('$^')).finditer (content ):
                imports .append (match .group (1 ))
            for match in patterns .get ('dynamic_import',re .compile ('$^')).finditer (content ):
                imports .append (match .group (1 ))
        elif language =='java':
            for match in patterns .get ('import',re .compile ('$^')).finditer (content ):
                imports .append (match .group (1 ))
        elif language =='go':
            for match in patterns .get ('import',re .compile ('$^')).finditer (content ):
                imp =match .group (1 )or match .group (2 )
                if imp :
                    imports .append (imp )
        return list (set (imports ))

    def _resolve_import_path (self ,import_path :str ,current_file :str ,project_path :str )->Optional [str ]:
        if import_path .startswith ('./')or import_path .startswith ('../'):
            current_dir =os .path .dirname (os .path .join (project_path ,current_file ))
            resolved =os .path .normpath (os .path .join (current_dir ,import_path ))
            if resolved .startswith (project_path ):
                rel_path =os .path .relpath (resolved ,project_path )
                if os .path .exists (os .path .join (project_path ,rel_path )):
                    return rel_path 
                for ext in ['.py','.js','.ts','.jsx','.tsx','.java','.go','.mjs']:
                    if os .path .exists (os .path .join (project_path ,rel_path +ext )):
                        return rel_path +ext 
            return None 
        if '.'in import_path and (not import_path .startswith ('.')):
            path_candidate =import_path .replace ('.','/')
            for ext in ['.py','.js','.ts','/__init__.py','.java','.go','.mjs']:
                full_candidate =path_candidate +ext 
                if os .path .exists (os .path .join (project_path ,full_candidate )):
                    return full_candidate 
        if not import_path .startswith ('.')and (not import_path .startswith ('/')):
            return f'EXTERNAL:{import_path }'
        return None 

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
        logger .info (f'[{scan_id }] Building file dependency map...')
        source_files =self ._get_source_files (project_path )
        logger .info (f'[{scan_id }] Found {len (source_files )} source files')
        file_imports :Dict [str ,List [str ]]={}
        external_packages :Dict [str ,Set [str ]]={}
        for rel_path in source_files :
            full_path =os .path .join (project_path ,rel_path )
            try :
                with open (full_path ,'r',encoding ='utf-8',errors ='ignore')as f :
                    content =f .read ()
            except Exception as e :
                logger .warning (f'[{scan_id }] Failed to read {rel_path }: {e }')
                continue 
            language =self ._detect_language (rel_path )
            if not language :
                continue 
            raw_imports =self ._extract_imports (content ,language )
            resolved_imports =[]
            external_packages [rel_path ]=set ()
            for imp in raw_imports :
                resolved =self ._resolve_import_path (imp ,rel_path ,project_path )
                if resolved :
                    if resolved .startswith ('EXTERNAL:'):
                        external_packages [rel_path ].add (resolved [9 :])
                    else :
                        resolved_imports .append (resolved )
            file_imports [rel_path ]=list (set (resolved_imports ))
        reverse_imports :Dict [str ,List [str ]]={f :[]for f in source_files }
        for file ,imports in file_imports .items ():
            for imp in imports :
                if imp in reverse_imports :
                    reverse_imports [imp ].append (file )
        for rel_path in source_files :
            self .file_deps [rel_path ]={'imports':file_imports .get (rel_path ,[]),'imported_by':reverse_imports .get (rel_path ,[]),'external_packages':list (external_packages .get (rel_path ,set ()))}
        if REDIS_AVAILABLE :
            try :
                redis_client .setex (f'{scan_id }:file_deps',SCAN_TTL ,json .dumps (self .file_deps ))
                logger .info (f'[{scan_id }] File dependency map stored in Redis')
            except Exception as e :
                logger .error (f'[{scan_id }] Failed to store file_deps in Redis: {e }')
        else :
            logger .warning (f'[{scan_id }] Redis not available, file_deps not persisted')
        logger .info (f'[{scan_id }] FileDependencyMapper complete: {len (self .file_deps )} files mapped')
        return self .file_deps 
