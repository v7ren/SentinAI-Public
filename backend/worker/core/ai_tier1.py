import json 
import aiohttp 
from .config import OPENROUTER_API_KEY ,OPENROUTER_API_URL ,CHEAP_MODEL ,DETECTOR_MIN_CONFIDENCE ,TIER1_OPENROUTER_TIMEOUT_SECONDS ,logger 
from .utils import find_line_number ,clean_json_response ,detect_language ,parse_json_with_fallbacks 
TIER1_CHUNK_SIZE =32000 
TIER1_CHUNK_OVERLAP =1000 

def _build_numbered_content (content :str )->str :
    lines =content .splitlines ()
    numbered =[]
    for i ,line in enumerate (lines ,1 ):
        numbered .append (f'{i :>4}| {line }')
    return '\n'.join (numbered )

def _chunk_content (content :str ,chunk_size :int =TIER1_CHUNK_SIZE ,overlap :int =TIER1_CHUNK_OVERLAP ):
    lines =content .splitlines (keepends =True )
    chunks =[]
    current_chunk_lines =[]
    current_size =0 
    chunk_start_line =1 
    for i ,line in enumerate (lines ):
        current_chunk_lines .append (line )
        current_size +=len (line )
        if current_size >=chunk_size :
            chunk_text =''.join (current_chunk_lines )
            chunks .append ((chunk_start_line ,chunk_text ))
            overlap_lines =[]
            overlap_size =0 
            for ol in reversed (current_chunk_lines ):
                if overlap_size +len (ol )>overlap :
                    break 
                overlap_lines .insert (0 ,ol )
                overlap_size +=len (ol )
            overlap_count =len (overlap_lines )
            chunk_start_line =i +2 -overlap_count 
            current_chunk_lines =list (overlap_lines )
            current_size =overlap_size 
    if current_chunk_lines :
        chunk_text =''.join (current_chunk_lines )
        if chunk_text .strip ():
            chunks .append ((chunk_start_line ,chunk_text ))
    return chunks 

def _build_system_prompt (schema :dict ,filename :str ='')->str :
    language ,is_frontend =detect_language (filename )
    if is_frontend :
        primary_vulns ="XSS via dangerouslySetInnerHTML={{ __html: userInput }}, element.innerHTML = userInput, document.write(userInput), Hardcoded Secrets (API keys, auth tokens, private keys literally in source), Insecure Deserialization (ONLY pickle/yaml.unsafe_load/eval - NOT JSON.parse or response.json), RCE via eval(userInput) or Function() with user-controlled input, Path Traversal in Next.js/SSR API routes using user-controlled paths, PostMessage without origin check (window.addEventListener('message') using event.data without event.origin validation), Client-side JWT decode (atob/token.split without signature verification), Clickjacking (missing X-Frame-Options or frame-ancestors CSP), Plaintext credentials in localStorage/sessionStorage (tokens, passwords), document.cookie read without HttpOnly (session theft risk), fetch/axios with user-controlled URL (client-side request to arbitrary host), Open redirect (router.push/navigate/redirect with user-controlled URL, searchParams.get('next')), Prototype pollution (Object.assign/merge with URL/query-derived object spread into defaults), Debug credential exposure (?debug=true or similar logging username/password to console)."
        language_rules ='FRONTEND FILE RULES - READ CAREFULLY:\n- NEVER report SQL Injection in .tsx/.jsx/.ts/.js files: they CANNOT run cursor.execute, db.execute, or Python SQL. These are backend-only.\n- If you see cursor.execute or similar in a frontend file, it is mock/example/comment code - NOT a real vuln. Do NOT report it.\n- FLAG: dangerouslySetInnerHTML, innerHTML =, document.write with user/URL data = XSS\n- FLAG: localStorage/sessionStorage storing tokens, passwords, or PII = insecure storage\n- FLAG: fetch(url) or axios.get(url) where url comes from user input = client-side arbitrary request\n- fetch(), axios with hardcoded URLs are NOT vulnerabilities - only when URL is user-controlled\n- React/Vue/Angular auto-escape output - only flag XSS if dangerouslySetInnerHTML or .innerHTML is used\n- JSON.parse() and response.json() are SAFE - not insecure deserialization\n- localStorage / sessionStorage with JSON.stringify are SAFE - not deserialization\n- Client-side role/permission checks are NOT vulnerabilities (backend must validate)\n- router.push() / navigate() / redirect() after login is NORMAL - not access control issue\n- console.log() is NOT information disclosure unless logging passwords, tokens, or PII\n- setState / useState with server data is NOT XSS - React auto-escapes\n- NEXT_PUBLIC_ env vars exposed client-side is BY DESIGN in Next.js - not a secret exposure\n- window.open() has nothing to do with cryptography\n\n'
    else :
        primary_vulns ='SQL Injection (f-strings/string concat in SQL queries), NoSQL Injection (MongoDB find/findOne with user input, $ne/$gt in query), Command Injection (subprocess/os.system with shell=True + user input), XSS (render_template_string with user data, dangerouslySetInnerHTML), SSRF (requests.get/post/put/delete, urllib.request.urlopen, httpx.get/post with user-controlled URL), Path Traversal (os.path.join(base_dir, user_input), open(os.path.join(...)), send_file, shutil.copy with user path, werkzeug.secure_filename bypass), Insecure Deserialization (pickle.loads, yaml.load/yaml.full_load without SafeLoader, marshal.loads), RCE (eval/exec with user-controlled input), Hardcoded Secrets (secret_key, API keys, passwords in source), Weak Crypto (hashlib.md5/sha1 for passwords, tokens, signing, or auth), IDOR (route param or request.args/form user_id in SELECT/UPDATE/DELETE without WHERE current_user check), SSTI (Jinja2/Mako Template() with user data), Session fixation (accepting client-provided session_id), JWT issues (jwt.decode with user-controlled algorithm or verify_exp: False, algorithms=[user_input]), Mass assignment (update_one/$set or .update with unchecked user fields), GraphQL introspection exposed (__schema/__type), Unrestricted file upload (no extension/mimetype validation), CSV injection (user data in export without formula sanitization), Host header injection (X-Forwarded-Host in URL generation), Open redirect (RedirectResponse(redirect_url), redirect(user_input) with no allowlist), ReDoS (re.match/re.search/re.compile with user-controlled pattern), Race condition / TOCTOU (check-then-update without lock), Info disclosure (debug endpoints, os.environ in response, traceback.format_exc(), SECRET_KEY exposed).'
        language_rules =''
    return f'You are an elite SAST (Static Application Security Testing) scanner analyzing {language } code. Analyze the code for exploitable security vulnerabilities.\nYour role is RECALL — flag everything suspicious. Precision is handled by Tier 2 and Tier 3. It is better to over-flag here than to miss a real vulnerability. Do NOT self-filter based on confidence at this stage.\nReturn strictly valid JSON: {json .dumps (schema )}\n\nRULES:\n1. Be THOROUGH: scan EVERY function in the code. Do NOT stop after the first few findings.\n2. Be PRECISE: only flag real, exploitable vulnerabilities with actual dangerous code patterns.\n3. Primary vulnerabilities to look for in this {language } file: {primary_vulns }\n\n'+(language_rules if language_rules else '')+f"""================================================================================\nANALYSIS CHECKLIST - Answer YES/NO/MAYBE for each category:\n================================================================================\n1. SQL_INJECTION - Unparameterized queries with user input\n2. XSS - User data in HTML/JS without escaping\n3. PATH_TRAVERSAL - User input in file paths (open, send_file, os.path.join, shutil.copy)\n4. COMMAND_INJECTION - User input in shell commands\n5. SSRF - requests.get/post/put, urllib.urlopen, httpx with user-controlled URL\n6. HARDCODED_SECRET - API keys, passwords in source\n7. INSECURE_DESERIALIZATION - pickle.loads, yaml.load (without SafeLoader), marshal.loads\n8. YAML_RCE - yaml.load() or yaml.full_load() without Loader=yaml.SafeLoader\n9. WEAK_CRYPTO - hashlib.md5/sha1 for passwords, tokens, or auth contexts\n10. IDOR - Route param or request.args/form user_id in DB query without ownership check\n11. AUTH_BYPASS - Missing auth checks\n\nIDOR patterns: @app.route('/api/team/<int:member_id>') then SELECT/UPDATE/DELETE by member_id with no WHERE user_id=session['user_id'] or current_user.id check; request.args.get('user_id') in query without ownership verification.\n\nFor each YES or MAYBE, provide:\n- line_number (exact line)\n- sink_code (the vulnerable line)\n- tainted_variable (which user input reaches here, or null)\n- sanitizers_checked (did you check if sanitizers block this path?)\n- why_not_fp (one sentence proving this is exploitable, not theoretical)\n\n================================================================================\nCONFIDENCE CALIBRATION - Adjust your confidence_score:\n================================================================================\nDOWNGRADE by 2 points if:\n- Function has 0 call sites (dead code, not reachable)\n- Sanitizer registry shows this input path is covered\n- Vulnerability requires 3+ chained conditions to trigger\n- Sink is inside a test file (test_*, *_test.py, *.test.js)\n\nUPGRADE only if ALL of these are true:\n- Exact HTTP input -> sink trace exists (no sanitizer in between)\n- Function is called from a public route (entry point)\n- You can describe the exact HTTP request that triggers it\n\n================================================================================\nCONFIDENCE SCORING - REQUIRED for every finding:\n================================================================================\nScore confidence_score (1-10) for each finding:\n- 10: Certain exploit, can write PoC immediately\n- 8-9: Clear vulnerable pattern, proven attack path\n- 7: Likely vulnerable, exploitable with conditions\n- 5-6: Suspicious but might be false positive. DO NOT REPORT.\n- Below 5: Almost certainly false positive. DO NOT REPORT.\nONLY include findings with confidence_score >= {int (DETECTOR_MIN_CONFIDENCE )}. Borderline findings should still be included if exploitability is plausible and verifiable downstream.\n\nHIGH-RECALL MODE:\nWhen enabled, also include lower-confidence findings (confidence_score 4-6) as "informational" or "low-confidence" items. Mark these with:\n  - severity: "INFO" or "LOW"\n  - confidence_score: the actual score (4-6)\n  - _low_confidence_flag: true\nDo not suppress findings entirely when in high-recall mode; instead, downgrade the confidence.\n\n================================================================================\nPRECEDENTS - These patterns are NOT vulnerabilities:\n================================================================================\n1. JSON.parse() / response.json() is NOT insecure deserialization\n2. Hardcoded localhost/127.0.0.1 URLs are NOT secrets\n3. UUIDs do NOT need validation\n4. Environment variables are TRUSTED in secure environments\n5. React setState with server data is NOT XSS - React auto-escapes\n6. router.push() after login is NOT an access control issue\n7. window.open() is NOT insecure cryptography\n8. localStorage with JSON.stringify is NOT insecure deserialization\n9. Client-side auth checks are NOT vulnerabilities - backend MUST validate\n10. React/Angular/Vue are XSS-safe unless using dangerouslySetInnerHTML\n11. Plaintext passwords in DB seeds = 'Hardcoded Credentials', NOT 'Insecure Deserialization'\n12. Logging non-PII data (URLs, IDs) is NOT a vulnerability\n\nEXCLUSIONS - DO NOT report:\n- DoS, resource exhaustion, rate limiting, throttling\n- Memory/CPU consumption, Log spoofing\n- Memory safety in Python/JS (impossible)\nReport with MEDIUM or LOW severity when clearly exploitable: Open redirect (redirect with user-controlled URL), ReDoS (regex with user input and catastrophic backtracking), Prototype pollution (__proto__/constructor in security-sensitive merge).\n\nWhen you detect hardcoded credentials or secrets, set 'type' to 'Hardcoded Secret'.\nWhen you detect plain passwords in DB seeds, set 'type' to 'Hardcoded Credentials'.\n"""

async def _scan_chunk (session ,url ,system_prompt ,filename ,chunk_text ,chunk_start_line ,context_block ):
    numbered =[]
    for i ,line in enumerate (chunk_text .splitlines (),chunk_start_line ):
        numbered .append (f'{i :>4}| {line }')
    numbered_code ='\n'.join (numbered )
    payload ={'model':CHEAP_MODEL ,'messages':[{'role':'system','content':system_prompt },{'role':'user','content':f'{context_block }File: {filename }\n(Lines {chunk_start_line }-{chunk_start_line +len (chunk_text .splitlines ())-1 })\n\nCode:\n{numbered_code }'}],'temperature':0.1 ,'response_format':{'type':'json_object'}}
    t =TIER1_OPENROUTER_TIMEOUT_SECONDS 
    timeout =aiohttp .ClientTimeout (total =t ,connect =60 ,sock_connect =60 ,sock_read =t )
    async with session .post (url ,json =payload ,headers ={'Authorization':f'Bearer {OPENROUTER_API_KEY }'},timeout =timeout )as resp :
        if resp .status !=200 :
            error_text =await resp .text ()
            logger .error (f'OpenRouter API Error ({resp .status }): {error_text }')
            return None 
        result =await resp .json ()
        raw_content =result ['choices'][0 ]['message']['content']
        logger .info (f'\n========== [TIER 1 CHUNK] ({filename } ~line {chunk_start_line }) ==========\n{raw_content [:800 ]}...\n==============================================================')
        clean_content =clean_json_response (raw_content )
        ok ,parsed =parse_json_with_fallbacks (clean_content ,'Tier 1 chunk response')
        if not ok :
            return None 
        return parsed 

def _filter_frontend_sqli_hallucinations (findings :list ,filename :str )->list :
    if not findings :
        return findings 
    ext ='.'+filename .rsplit ('.',1 )[-1 ].lower ()if '.'in filename else ''
    if ext not in {'.tsx','.jsx','.ts','.js','.vue','.svelte','.html'}:
        return findings 
    backend_sqli_sinks =('cursor.execute','db.execute','executemany','cursor.executemany','connection.execute')
    kept =[]
    for f in findings :
        if f .get ('type','')!='SQL Injection':
            kept .append (f )
            continue 
        vuln_code =(f .get ('vulnerable_code')or '').lower ()
        if any ((sink in vuln_code for sink in backend_sqli_sinks )):
            logger .debug (f'[TIER 1] Dropping frontend SQLi hallucination (Python sink in {filename }): {vuln_code [:80 ]}...')
            continue 
        kept .append (f )
    return kept 

def _filter_low_confidence (findings :list ,threshold :float =DETECTOR_MIN_CONFIDENCE )->list :
    kept =[]
    for f in findings :
        score =f .get ('confidence_score')
        if score is None :
            logger .warning (f"[TIER 1] Missing confidence_score: {f .get ('type')} — defaulting to 5.0")
            score =5.0 
        try :
            score =int (score )
        except (TypeError ,ValueError ):
            logger .warning (f'[TIER 1] Unparseable confidence_score — defaulting to 5.0')
            score =5.0 
        if score >=threshold :
            kept .append (f )
        else :
            logger .debug (f"[TIER 1] Dropping low-confidence finding (score={score }): {f .get ('type')}")
    return kept 

async def scan_tier_1_basic (session :aiohttp .ClientSession ,filename :str ,content :str ,context_info :str =''):
    url =OPENROUTER_API_URL 
    schema ={'status':'VULNERABLE or SAFE','findings':[{'type':'Vulnerability Type','severity':'HIGH/MEDIUM/LOW','confidence_score':f'Integer 1-10 (only include findings >= {int (DETECTOR_MIN_CONFIDENCE )})','function_name':'Name of the function containing the bug','vulnerable_code':'The exact code snippet','reason':'Short explanation','line_number':'Exact line number of the vulnerable code','tainted_variable':'Variable name that carries user input to this sink, or null','sanitizers_checked':'Boolean - did you verify no sanitizer blocks this path?','why_not_fp':'One sentence proving exploitability, not pattern matching'}]}
    system_prompt =_build_system_prompt (schema ,filename )
    context_block =''
    if context_info :
        context_block =f'Context (project + code graph):\n{context_info [:2000 ]}\n\n'
    content_len =len (content )
    if content_len <=TIER1_CHUNK_SIZE :
        numbered_code =_build_numbered_content (content )
        payload ={'model':CHEAP_MODEL ,'messages':[{'role':'system','content':system_prompt },{'role':'user','content':f'{context_block }File: {filename }\n\nCode:\n{numbered_code }'}],'temperature':0.1 ,'response_format':{'type':'json_object'}}
        t =TIER1_OPENROUTER_TIMEOUT_SECONDS 
        timeout =aiohttp .ClientTimeout (total =t ,connect =60 ,sock_connect =60 ,sock_read =t )
        try :
            async with session .post (url ,json =payload ,headers ={'Authorization':f'Bearer {OPENROUTER_API_KEY }'},timeout =timeout )as resp :
                if resp .status !=200 :
                    error_text =await resp .text ()
                    logger .error (f'OpenRouter API Error ({resp .status }): {error_text }')
                    return {'status':'UNKNOWN','details':f'OpenRouter Error: {resp .status }'}
                result =await resp .json ()
                raw_content =result ['choices'][0 ]['message']['content']
                logger .info (f'\n========== [TIER 1 RAW] ({filename }) ==========\n{raw_content }\n==============================================================')
                clean_content =clean_json_response (raw_content )
                ok ,parsed =parse_json_with_fallbacks (clean_content ,'Tier 1 response')
                if not ok :
                    return {'status':'UNKNOWN','details':'Invalid JSON from Tier 1 model'}
                data =parsed 
                if data .get ('findings'):
                    for f in data ['findings']:
                        f ['line']=find_line_number (content ,f .get ('vulnerable_code',''),f .get ('function_name',''))
                    data ['findings']=_filter_frontend_sqli_hallucinations (data ['findings'],filename )
                    data ['findings']=_filter_low_confidence (data ['findings'])
                if not data .get ('findings'):
                    data ['status']='SAFE'
                elif 'status'not in data :
                    data ['status']='VULNERABLE'
                return data 
        except TimeoutError :
            logger .warning ('Tier 1 timed out reading OpenRouter response (%s); verdict UNKNOWN (try TIER1_OPENROUTER_TIMEOUT_SECONDS)',filename )
            return {'status':'UNKNOWN','details':'OpenRouter request timed out'}
        except aiohttp .ClientError as e :
            logger .warning ('Tier 1 HTTP error (%s): %s',filename ,e )
            return {'status':'UNKNOWN','details':str (e )}
        except Exception as e :
            logger .exception (f'Tier 1 Unexpected Error: {str (e )}')
            return {'status':'UNKNOWN','details':str (e )}
    chunks =_chunk_content (content )
    logger .info (f'[TIER 1] Large file ({content_len } chars, {len (content .splitlines ())} lines) -> {len (chunks )} chunks')
    all_findings =[]
    seen_fingerprints =set ()
    for chunk_start ,chunk_text in chunks :
        try :
            chunk_result =await _scan_chunk (session ,url ,system_prompt ,filename ,chunk_text ,chunk_start ,context_block )
            if chunk_result and chunk_result .get ('findings'):
                for f in chunk_result ['findings']:
                    line_num =find_line_number (content ,f .get ('vulnerable_code',''),f .get ('function_name',''))
                    f ['line']=line_num 
                    fp_key =f"{f .get ('type','')}:{f .get ('function_name','')}:{line_num }"
                    if fp_key not in seen_fingerprints :
                        seen_fingerprints .add (fp_key )
                        all_findings .append (f )
        except TimeoutError :
            logger .warning ('Tier 1 chunk timed out (~line %s in %s); skipping chunk',chunk_start ,filename )
            continue 
        except Exception as e :
            logger .error (f'Tier 1 chunk scan failed (line ~{chunk_start }): {e }')
            continue 
    all_findings =_filter_frontend_sqli_hallucinations (all_findings ,filename )
    all_findings =_filter_low_confidence (all_findings )
    if all_findings :
        return {'status':'VULNERABLE','findings':all_findings }
    else :
        return {'status':'SAFE','findings':[]}
