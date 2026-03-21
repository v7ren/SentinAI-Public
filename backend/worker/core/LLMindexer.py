import os 
import sys 
import json 
import time 
import textwrap 
from typing import List ,Dict ,Any 
from concurrent .futures import ThreadPoolExecutor ,as_completed 
from dotenv import load_dotenv 
import requests 
try :
    from backend .worker .core .config import OPENROUTER_API_KEY as _OR_KEY ,OPENROUTER_API_URL as _OR_URL ,INDEXER_MODEL as _INDEXER_MODEL 
except ImportError :
    load_dotenv ()
    _OR_KEY =os .getenv ('OPENROUTER_API_KEY')
    _OR_URL =os .getenv ('OPENROUTER_API_URL','https://openrouter.ai/api/v1/chat/completions')
    _INDEXER_MODEL =os .getenv ('INDEXER_MODEL','openai/gpt-oss-120b')
MAX_FILE_CHARS =24000 
CHUNK_LINES =120 
INDEXER_CHAT_MAX_RETRIES =int (os .environ .get ('LLM_INDEXER_CHAT_RETRIES','3'))
INDEXER_CHAT_BACKOFF_SEC =float (os .environ .get ('LLM_INDEXER_CHAT_BACKOFF','2'))
CODE_EXTENSIONS =('.py','.js','.ts','.tsx','.jsx','.java','.go','.rb','.php','.rs','.cs')
SKIP_DIRS ={'.git','node_modules','.venv','venv','__pycache__','dist','build','.next','.idea','.vscode'}
MAX_WORKERS =int (os .environ .get ('LLM_INDEXER_THREADS','10'))
WIKI_MAX_WORKERS =int (os .environ .get ('WIKI_THREADS','5'))

class OpenRouterSyncClient :

    def __init__ (self ,api_key :str ,model :str ):
        if not api_key :
            raise RuntimeError ('OPENROUTER_API_KEY is not set')
        self .api_key =api_key 
        self .model =model 
        self .url =_OR_URL 

    def chat (self ,system_prompt :str ,user_prompt :str ,max_tokens :int =2048 ,temperature :float =0.1 ,json_mode :bool =False )->str :
        headers ={'Authorization':f'Bearer {self .api_key }','Content-Type':'application/json'}
        payload :Dict [str ,Any ]={'model':self .model ,'messages':[{'role':'system','content':system_prompt },{'role':'user','content':user_prompt }],'max_tokens':max_tokens ,'temperature':temperature }
        if json_mode :
            payload ['response_format']={'type':'json_object'}
        resp =requests .post (self .url ,headers =headers ,json =payload ,timeout =120 )
        if resp .status_code !=200 :
            raise RuntimeError (f'OpenRouter error: {resp .status_code } {resp .text }')
        data =resp .json ()
        try :
            content =data ['choices'][0 ]['message']['content']
        except Exception as e :
            raise RuntimeError (f'Unexpected OpenRouter response: {data }')from e 
        return content 

    def chat_json (self ,system_prompt :str ,user_prompt :str ,max_tokens :int =2048 ,temperature :float =0.1 )->Dict [str ,Any ]:
        raw =self .chat (system_prompt =system_prompt ,user_prompt =user_prompt ,max_tokens =max_tokens ,temperature =temperature ,json_mode =True )
        try :
            return json .loads (raw )
        except json .JSONDecodeError :
            cleaned =raw .strip ()
            if '{'in cleaned and '}'in cleaned :
                cleaned =cleaned [cleaned .index ('{'):cleaned .rindex ('}')+1 ]
                return json .loads (cleaned )
            raise 

class LLMProjectIndexer :

    def __init__ (self ,root_path :str ,client :OpenRouterSyncClient ):
        self .root_path =os .path .abspath (root_path )
        self .client =client 
        self .project_ir :Dict [str ,Any ]={'root_path':self .root_path ,'files':{}}

    def _is_code_file (self ,rel_path :str )->bool :
        return rel_path .endswith (CODE_EXTENSIONS )

    def discover_files (self )->List [str ]:
        files :List [str ]=[]
        for root ,dirs ,filenames in os .walk (self .root_path ):
            dirs [:]=[d for d in dirs if d not in SKIP_DIRS ]
            for fn in filenames :
                full =os .path .join (root ,fn )
                rel =os .path .relpath (full ,self .root_path )
                if self ._is_code_file (rel ):
                    files .append (rel )
        return sorted (files )

    def _read_file (self ,rel_path :str )->str :
        full =os .path .join (self .root_path ,rel_path )
        with open (full ,'r',encoding ='utf-8',errors ='ignore')as f :
            return f .read ()

    def detect_language (self ,rel_path :str )->str :
        lower =rel_path .lower ()
        if lower .endswith ('.py'):
            return 'python'
        if lower .endswith (('.js','.jsx','.ts','.tsx')):
            return 'javascript'
        if lower .endswith ('.java'):
            return 'java'
        if lower .endswith ('.go'):
            return 'go'
        if lower .endswith ('.rb'):
            return 'ruby'
        if lower .endswith ('.php'):
            return 'php'
        if lower .endswith ('.rs'):
            return 'rust'
        if lower .endswith ('.cs'):
            return 'csharp'
        return 'text'

    def chunk_file (self ,content :str ,max_lines :int =CHUNK_LINES )->List [Dict [str ,Any ]]:
        lines =content .splitlines ()
        chunks :List [Dict [str ,Any ]]=[]
        start =0 
        while start <len (lines ):
            end =min (start +max_lines ,len (lines ))
            chunk_text ='\n'.join (lines [start :end ])
            chunks .append ({'start_line':start +1 ,'end_line':end ,'text':chunk_text })
            start =end 
        return chunks 

    def _file_summary_prompt (self ,rel_path :str ,language :str ,content :str )->str :
        trimmed =content [:MAX_FILE_CHARS ]
        return textwrap .dedent (f"""\n            You are a code comprehension assistant.\n\n            You are given the full contents of a single source file from a codebase.\n            Your job is to produce a JSON description of what this file does.\n\n            Rules:\n            - Only describe behavior that is clearly present in the code.\n            - If you are unsure about something, omit it or mark it as null.\n            - DO NOT invent endpoints or functions that are not present.\n            - Output valid JSON ONLY, no comments or extra text.\n\n            Return JSON with this exact structure:\n\n            {{\n              "file_summary": "short paragraph describing this file's purpose",\n              "main_concerns": [\n                "auth / login / session / jwt / oauth / permissions if applicable",\n                "database querying / orm models if applicable",\n                "external http calls (apis, webhooks, etc) if applicable",\n                "filesystem operations if applicable",\n                "message queues, redis, kafka, websockets if applicable"\n              ],\n              "suspected_entrypoints": [\n                {{\n                  "kind": "http_endpoint | ws_handler | cli | main | library",\n                  "name": "symbol name or description",\n                  "details": "short explanation"\n                }}\n              ]\n            }}\n\n            File path: {rel_path }\n            Language: {language }\n\n            Code:\n            {trimmed }\n            """).strip ()

    def _chunk_summary_prompt (self ,rel_path :str ,language :str ,chunk_text :str ,start_line :int ,end_line :int )->str :
        return textwrap .dedent (f"""\n            You are a code indexing assistant.\n\n            You are given a contiguous chunk of code from a single file.\n            Your task is to produce a JSON description of this chunk that can be used\n            for building a project index map, and extracting ALL HTTP endpoints declared in this chunk.\n\n            Rules:\n            - Only talk about behavior that appears in THIS chunk.\n            - DO NOT invent functions, routes, or behavior that is not in this code.\n            - If you see HTTP routes, describe ALL of them as separate items in http_endpoints.\n            - If unsure, use null/empty lists. Do not guess.\n            - Output valid JSON ONLY, no comments or extra text.\n\n            Return JSON with this exact structure:\n\n            {{\n              "chunk_id": "unique identifier for this chunk (e.g. '{rel_path }:{start_line }-{end_line }')",\n              "start_line": {start_line },\n              "end_line": {end_line },\n              "summary": "one short paragraph explaining what this chunk does",\n              "tags": [\n                "auth",\n                "db",\n                "network",\n                "file_io",\n                "crypto",\n                "process",\n                "config",\n                "testing",\n                "logging",\n                "ws",\n                "security",\n                "other"\n              ],\n              "http_endpoints": [\n                {{\n                  "method": "GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD",\n                  "path": "string (e.g. '/api/login')",\n                  "framework": "flask|fastapi|express|django|aiohttp|other|unknown",\n                  "handler": "function/class name if visible, else null",\n                  "notes": "short explanation or null"\n                }}\n              ],\n              "ws_handlers": [\n                {{\n                  "path": "string or null",\n                  "framework": "socketio|ws|other|unknown",\n                  "expects_auth": "boolean or null",\n                  "message_types": ["string", "..."]\n                }}\n              ]\n            }}\n\n            Fill fields as accurately as you can based ONLY on the code below.\n\n            File: {rel_path }\n            Language: {language }\n            Lines: {start_line }-{end_line }\n\n            Code chunk:\n            {chunk_text }\n            """).strip ()

    def _chat_json_with_retry (self ,system_prompt :str ,user_prompt :str ,label :str ='')->Dict [str ,Any ]:
        last_err =None 
        for attempt in range (INDEXER_CHAT_MAX_RETRIES ):
            try :
                return self .client .chat_json (system_prompt ,user_prompt )
            except Exception as e :
                last_err =e 
                if attempt <INDEXER_CHAT_MAX_RETRIES -1 :
                    wait =INDEXER_CHAT_BACKOFF_SEC *(attempt +1 )
                    print (f"[!] {label or 'LLM'} attempt {attempt +1 }/{INDEXER_CHAT_MAX_RETRIES } failed: {e }. Retrying in {wait }s...")
                    time .sleep (wait )
                else :
                    raise 
        raise last_err 

    def index_file (self ,rel_path :str )->Dict [str ,Any ]:
        content =self ._read_file (rel_path )
        language =self .detect_language (rel_path )
        system_prompt ='You are a careful code analysis model. Always return STRICTLY valid JSON that matches the requested schema.'
        print (f'[+] Indexing file: {rel_path }')
        file_prompt =self ._file_summary_prompt (rel_path ,language ,content )
        try :
            file_json =self ._chat_json_with_retry (system_prompt ,file_prompt ,label =f'File-level {rel_path }')
        except Exception as e :
            print (f'[!] File-level summary failed for {rel_path }: {e }')
            file_json ={'file_summary':'','main_concerns':[],'suspected_entrypoints':[]}
        chunks =self .chunk_file (content )
        chunk_entries :List [Dict [str ,Any ]]=[]
        for ch in chunks :
            start_line =ch ['start_line']
            end_line =ch ['end_line']
            chunk_text =ch ['text']
            chunk_prompt =self ._chunk_summary_prompt (rel_path ,language ,chunk_text ,start_line ,end_line )
            try :
                chunk_json =self ._chat_json_with_retry (system_prompt ,chunk_prompt ,label =f'Chunk {rel_path }:{start_line }-{end_line }')
                if not chunk_json .get ('chunk_id'):
                    chunk_json ['chunk_id']=f'{rel_path }:{start_line }-{end_line }'
                if 'start_line'not in chunk_json :
                    chunk_json ['start_line']=start_line 
                if 'end_line'not in chunk_json :
                    chunk_json ['end_line']=end_line 
                if 'http_endpoints'not in chunk_json or not isinstance (chunk_json .get ('http_endpoints'),list ):
                    chunk_json ['http_endpoints']=[]
                legacy_ep =chunk_json .get ('http_endpoint')
                if isinstance (legacy_ep ,dict ):
                    m =legacy_ep .get ('method')
                    p =legacy_ep .get ('path')
                    if m and p :
                        chunk_json ['http_endpoints'].append ({'method':m ,'path':p ,'framework':legacy_ep .get ('framework'),'handler':None ,'notes':legacy_ep .get ('notes')})
                if 'ws_handlers'not in chunk_json or not isinstance (chunk_json .get ('ws_handlers'),list ):
                    chunk_json ['ws_handlers']=[]
                legacy_ws =chunk_json .get ('ws_handler')
                if isinstance (legacy_ws ,dict ):
                    path =legacy_ws .get ('path')
                    if path :
                        chunk_json ['ws_handlers'].append ({'path':path ,'framework':'unknown','expects_auth':legacy_ws .get ('expects_auth'),'message_types':legacy_ws .get ('message_types')or []})
                if 'http_endpoint'in chunk_json :
                    del chunk_json ['http_endpoint']
                if 'ws_handler'in chunk_json :
                    del chunk_json ['ws_handler']
            except Exception as e :
                print (f'[!] Chunk-level summary failed for {rel_path }:{start_line }-{end_line }: {e }')
                chunk_json ={'chunk_id':f'{rel_path }:{start_line }-{end_line }','start_line':start_line ,'end_line':end_line ,'summary':'','tags':[],'http_endpoints':[],'ws_handlers':[]}
            chunk_entries .append (chunk_json )
            time .sleep (0.2 )
        file_ir ={'language':language ,'file_summary':file_json .get ('file_summary',''),'main_concerns':file_json .get ('main_concerns',[]),'suspected_entrypoints':file_json .get ('suspected_entrypoints',[]),'chunks':chunk_entries }
        return file_ir 

    def build_index (self )->None :
        files =self .discover_files ()
        print (f'[+] Found {len (files )} code files under {self .root_path }')
        if not files :
            return 
        with ThreadPoolExecutor (max_workers =MAX_WORKERS )as executor :
            future_to_file ={executor .submit (self .index_file ,rel ):rel for rel in files }
            for future in as_completed (future_to_file ):
                rel_path =future_to_file [future ]
                try :
                    file_ir =future .result ()
                    self .project_ir ['files'][rel_path ]=file_ir 
                except Exception as e :
                    print (f'[!] Failed to index {rel_path }: {e }')

    def to_json (self )->str :
        return json .dumps (self .project_ir ,indent =2 )

class WikiGenerator :

    def __init__ (self ,client :OpenRouterSyncClient ,project_ir :Dict [str ,Any ]):
        self .client =client 
        self .project_ir =project_ir 

    def _collect_snippets (self )->Dict [str ,str ]:
        files =self .project_ir .get ('files',{})
        snippets :List [str ]=[]
        for path ,info in files .items ():
            summary =info .get ('file_summary','')
            main_concerns =info .get ('main_concerns',[])
            suspected =info .get ('suspected_entrypoints',[])
            chunks =info .get ('chunks',[])
            chunk_summaries :List [str ]=[]
            for c in chunks :
                eps =c .get ('http_endpoints')or []
                ep_text =''
                if eps :
                    ep_text =' endpoints='+str ([{'method':e .get ('method'),'path':e .get ('path')}for e in eps ])
                chunk_summaries .append (f"{c .get ('chunk_id')}: {c .get ('summary','')} [tags={c .get ('tags',[])}]{ep_text }")
            combined ='\n'.join ([f'FILE: {path }',f'SUMMARY: {summary }',f'MAIN_CONCERNS: {main_concerns }',f'ENTRYPOINTS: {suspected }','CHUNKS:',*chunk_summaries ,''])
            snippets .append (combined )
        return {'all':'\n'.join (snippets )}

    def _generate_toc (self ,raw_index_text :str )->Dict [str ,Any ]:
        system_prompt ='You are designing a documentation structure for a codebase, based on a project index. You MUST output STRICT JSON, no markdown, no explanations.'
        user_prompt =textwrap .dedent (f'\n            You are given an LLM-derived project index (file summaries, entrypoints, chunk summaries).\n\n            1. Propose a small table of contents for technical documentation.\n            2. You MUST include at least these two sections:\n               - A high-level "Overview"\n               - An "Architecture" style section about how the system is structured and how data/requests flow\n            3. You may add up to 4 more sections whose names make sense for THIS project\n               (e.g. "Key Components", "Gameplay Systems", "Data Layer", "Frontend", "API Reference", "Security").\n            4. Section IDs must be simple lowercase identifiers with underscores, e.g. "overview", "architecture", "key_components".\n            5. Titles should be human-readable.\n\n            IMPORTANT:\n            - Do NOT assume this is a web server; infer the domain from the index.\n            - Only propose sections that are justified by the provided index.\n            - Total sections: minimum 2 (overview, architecture), maximum 6.\n\n            Return JSON ONLY in this format:\n\n            {{\n              "sections": [\n                {{\n                  "id": "overview",\n                  "title": "Overview",\n                  "description": "Short sentence about what this section will cover"\n                }},\n                {{\n                  "id": "architecture",\n                  "title": "Architecture and Data Flow",\n                  "description": "..."\n                }}\n              ]\n            }}\n\n            Here is the project index:\n\n            {raw_index_text }\n            ').strip ()
        raw =self .client .chat (system_prompt =system_prompt ,user_prompt =user_prompt ,max_tokens =1024 ,temperature =0.2 ,json_mode =True )
        try :
            toc =json .loads (raw )
        except json .JSONDecodeError :
            cleaned =raw .strip ()
            if '{'in cleaned and '}'in cleaned :
                cleaned =cleaned [cleaned .index ('{'):cleaned .rindex ('}')+1 ]
                toc =json .loads (cleaned )
            else :
                raise 
        ids ={s .get ('id')for s in toc .get ('sections',[])if isinstance (s ,dict )}

        def ensure_section (sec_id ,title ,desc ):
            nonlocal toc ,ids 
            if sec_id not in ids :
                toc .setdefault ('sections',[]).insert (0 ,{'id':sec_id ,'title':title ,'description':desc })
                ids .add (sec_id )
        ensure_section ('overview','Overview','High-level overview of what the project is and what it does.')
        ensure_section ('architecture','Architecture','How the project is structured internally and how data/requests flow.')
        seen =set ()
        cleaned_sections =[]
        for s in toc .get ('sections',[]):
            sec_id =s .get ('id')
            if not sec_id or sec_id in seen :
                continue 
            seen .add (sec_id )
            cleaned_sections .append (s )
        toc ['sections']=cleaned_sections [:6 ]
        return toc 

    def _wiki_prompt (self ,section_id :str ,title :str ,description :str ,raw_snippets :str )->str :
        base_intro =textwrap .dedent ('\n            You are generating high-level documentation for a codebase.\n            You are given an LLM-derived project index: per-file summaries, entrypoints,\n            and chunk summaries (with tags and sometimes endpoints).\n\n            Your task is to write a clear, opinionated markdown document for ONE section\n            of the documentation. You must:\n            - Base your answers ONLY on the provided summaries.\n            - Be concrete and map concepts back to file names and key entities/functions.\n            - Avoid hallucinating technologies or components that are not mentioned.\n            - Use headings, bullet lists, and short paragraphs.\n            - Explain flows and interactions between components, not just listing files.\n            ').strip ()
        if section_id =='overview':
            extra =textwrap .dedent ('\n                This is the high-level Overview section. Explain:\n                - What the project is and what problem it solves.\n                - The main components or modules at a very high level.\n                - A typical usage or runtime scenario in broad strokes.\n                - Where to look next (other sections) for deeper details.\n                ').strip ()
        elif section_id =='architecture':
            extra =textwrap .dedent ('\n                This is the Architecture section. Explain:\n                - The main architectural components (modules, services, subsystems).\n                - How data and control flow between them.\n                - Any important patterns (e.g., MVC, event-driven, layered, client/server).\n                - Reference specific files and important functions or classes where relevant.\n                ').strip ()
        else :
            extra =textwrap .dedent (f'\n                This section is titled "{title }". Use the description below as guidance:\n                "{description }"\n\n                Focus on this theme specifically, and organize content with clear headings.\n                ').strip ()
        return f'{base_intro }\n\nSection ID: {section_id }\nSection Title: {title }\n\n{extra }\n\nHere is the project index subset for this section:\n\n{raw_snippets }'

    def generate_section (self ,section_id :str ,title :str ,description :str ,raw_snippets :str )->str :
        if not raw_snippets .strip ():
            return f'# {title }\n\n_No relevant information found in index._\n'
        system_prompt ='You are a senior engineer turning a project index into clear documentation. Write high-quality markdown with headings and lists. Do not hallucinate APIs.'
        user_prompt =self ._wiki_prompt (section_id ,title ,description ,raw_snippets )
        md =self .client .chat (system_prompt =system_prompt ,user_prompt =user_prompt ,max_tokens =4096 ,temperature =0.2 ,json_mode =False )
        return md 

    def generate_all (self ,out_dir :str )->List [str ]:
        os .makedirs (out_dir ,exist_ok =True )
        snippets =self ._collect_snippets ()
        all_text =snippets .get ('all','')
        print ('[+] Generating dynamic table of contents...')
        toc =self ._generate_toc (all_text )
        sections =toc .get ('sections',[])
        print (f"[+] Sections chosen by LLM: {[s .get ('id')for s in sections ]}")
        if not sections :
            print ('[!] No sections returned from TOC generation, aborting wiki generation.')
            return []

        def generate_one_section (section :Dict [str ,Any ])->None :
            sec_id =section .get ('id')
            title =section .get ('title',sec_id .title ()if sec_id else 'Section')
            desc =section .get ('description','')
            filename =f'wiki_{sec_id }.md'if sec_id else 'wiki_section.md'
            print (f'[+] Generating wiki section: {sec_id } ({title })')
            md =self .generate_section (sec_id ,title ,desc ,all_text )
            out_path =os .path .join (out_dir ,filename )
            with open (out_path ,'w',encoding ='utf-8')as f :
                f .write (md )
            print (f'[+] Wrote {out_path }')
        max_workers =min (len (sections ),WIKI_MAX_WORKERS or 1 )
        with ThreadPoolExecutor (max_workers =max_workers )as executor :
            futures =[executor .submit (generate_one_section ,s )for s in sections ]
            for future in as_completed (futures ):
                try :
                    future .result ()
                except Exception as e :
                    print (f'[!] A section failed to generate: {e }')
        ordered_files =[]
        for section in sections :
            sec_id =section .get ('id')
            if sec_id :
                filename =f'wiki_{sec_id }.md'
                if os .path .exists (os .path .join (out_dir ,filename )):
                    ordered_files .append (filename )
        return ordered_files 

def build_ai_endpoint_map (project_ir :Dict [str ,Any ])->Dict [str ,Any ]:
    base_url =os .environ .get ('ENDPOINT_BASE_URL','').strip ().rstrip ('/')
    api_prefix =os .environ .get ('ENDPOINT_API_PREFIX','').strip ()

    def norm_path (p :str )->str :
        if not p :
            return p 
        p =str (p ).strip ()
        if not p .startswith ('/'):
            p ='/'+p 
        if api_prefix :
            pref =api_prefix if api_prefix .startswith ('/')else '/'+api_prefix 
            if not p .startswith (pref ):
                p =pref .rstrip ('/')+p 
        return p 
    seen =set ()
    endpoints =[]
    files =project_ir .get ('files',{})or {}
    for file_path ,finfo in files .items ():
        for ch in finfo .get ('chunks',[])or []:
            for ep in ch .get ('http_endpoints')or []:
                method =(ep .get ('method')or '').strip ().upper ()
                path =ep .get ('path')
                if not method or not path :
                    continue 
                path =norm_path (path )
                key =(method ,path )
                if key in seen :
                    continue 
                seen .add (key )
                url =f'{base_url }{path }'if base_url else path 
                endpoints .append ({'method':method ,'path':path ,'url':url ,'framework':ep .get ('framework'),'handler':ep .get ('handler'),'notes':ep .get ('notes'),'source':{'file':file_path ,'chunk_id':ch .get ('chunk_id'),'lines':f"{ch .get ('start_line')}-{ch .get ('end_line')}"}})
    endpoints .sort (key =lambda e :(e ['path'],e ['method'],e ['url']))
    return {'base_url':base_url ,'api_prefix':api_prefix ,'endpoints':endpoints }

def endpoint_map_to_markdown (endpoint_map :Dict [str ,Any ])->str :
    lines =['# Endpoint Map','']
    base_url =(endpoint_map .get ('base_url')or '').rstrip ('/')
    if base_url :
        lines .append (f'Base URL: `{base_url }`')
        lines .append ('')
    for e in endpoint_map .get ('endpoints',[])or []:
        lines .append (f"- `{e .get ('url')}` [{e .get ('method')}]")
    lines .append ('')
    return '\n'.join (lines )

def main ():
    if len (sys .argv )<4 :
        print ('Usage:\n  python deepwiki_like_indexer.py /path/to/project index.json wiki_out_dir/\n\nEnv:\n  OPENROUTER_API_KEY      (required)\n  INDEXER_MODEL           (optional, default=openai/gpt-oss-120b)\n  LLM_INDEXER_THREADS     (optional, default=10)\n  WIKI_THREADS            (optional, default=5)\n  ENDPOINT_BASE_URL       (optional, e.g. http://127.0.0.1:5001)\n  ENDPOINT_API_PREFIX     (optional, e.g. /api)\n')
        sys .exit (1 )
    folder_path =sys .argv [1 ]
    index_path =sys .argv [2 ]
    wiki_dir =sys .argv [3 ]
    if not os .path .isdir (folder_path ):
        print (f"Error: '{folder_path }' is not a directory")
        sys .exit (1 )
    api_key =_OR_KEY 
    if not api_key :
        print ('Error: OPENROUTER_API_KEY is not set')
        sys .exit (1 )
    print (f'[+] Using model: {_INDEXER_MODEL }')
    print (f'[+] Using up to {MAX_WORKERS } threads for indexing')
    client =OpenRouterSyncClient (api_key ,_INDEXER_MODEL )
    indexer =LLMProjectIndexer (folder_path ,client )
    indexer .build_index ()
    with open (index_path ,'w',encoding ='utf-8')as f :
        f .write (indexer .to_json ())
    print (f'[+] Index written to {index_path }')
    endpoint_map =build_ai_endpoint_map (indexer .project_ir )
    base ,_ =os .path .splitext (index_path )
    endpoint_json_path =base +'.endpoints.json'
    endpoint_md_path =base +'.endpoints.md'
    with open (endpoint_json_path ,'w',encoding ='utf-8')as f :
        json .dump (endpoint_map ,f ,indent =2 )
    with open (endpoint_md_path ,'w',encoding ='utf-8')as f :
        f .write (endpoint_map_to_markdown (endpoint_map ))
    print (f'[+] Endpoint map written to {endpoint_json_path }')
    print (f'[+] Endpoint map (md) written to {endpoint_md_path }')
    project_ir =indexer .project_ir 
    wiki =WikiGenerator (client ,project_ir )
    wiki .generate_all (wiki_dir )
    print (f'[+] Wiki pages written to {wiki_dir }')
if __name__ =='__main__':
    main ()
