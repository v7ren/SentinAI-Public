import asyncio 
import json 
import re 
import traceback 
from typing import Dict ,Optional ,Any ,List ,Tuple 
from ..config import OPENROUTER_API_KEY ,OPENROUTER_API_URL ,SMART_MODEL ,SKEPTIC_CVSS_THRESHOLD ,SKEPTIC_DEBUG ,logger 

def safe_slice (value :Any ,limit :int =2000 )->str :
    if value is None :
        return ''
    if isinstance (value ,(dict ,list )):
        try :
            value =json .dumps (value )
        except (TypeError ,ValueError ):
            value =str (value )
    if not isinstance (value ,str ):
        value =str (value )
    return value [:limit ]

class SkepticPass :
    SKEPTIC_PROMPT ='You are a senior security engineer reviewing a finding before customer delivery.\nYour job is to find reasons this finding is WRONG or OVERSTATED.\n\nCheck:\n1. Is the CVSS score justified? Justify every vector component. Most findings are not 9.8.\n2. Is attack complexity correctly assessed?\n3. Does exploiting this require authentication not accounted for?\n4. Is there a framework-level protection missed (CSRF token, ORM escaping, Content-Security-Policy, CORS restriction)?\n5. Does the sanitizer registry contain anything that covers this input?\n6. Cross-file context: If a "Cross-file context" block is present below, use it to decide whether the vulnerable input is attacker-controlled or only server-controlled. If the data comes only from server-controlled code (constants, server-built URL/path/command, no user/request input), set skeptic_passed=false and explain in skeptic_note (e.g. "False positive: input is not attacker-controlled").\n7. BEFORE DOWNGRADING: If the code_context provided is truncated or incomplete, \n   you MUST NOT downgrade the finding. A truncated snippet is NOT sufficient evidence\n   to dismiss a vulnerability. State "insufficient_context": true in your response\n   instead of downgrading.\n\nIMPORTANT: If you see truncated code ("...", cut-off lines, missing function bodies), \nyou lack the context to safely downgrade. In that case, keep skeptic_passed=true and \nnote that context was insufficient to make a downgrade determination.\n\nReview the finding carefully. Find any reason it might be incorrect.\n\nReturn JSON in this exact format:\n{\n  "skeptic_passed": true/false,\n  "corrected_cvss_score": float (if downgraded, else same as input),\n  "corrected_severity": "CRITICAL/HIGH/MEDIUM/LOW/INFO" (if downgraded),\n  "skeptic_note": "null" or "explanation of what was wrong",\n  "insufficient_context": true/false\n}\n\nYou must respond with ONLY a valid JSON object. No markdown, no code blocks, no extra text.\nYour entire response must be parseable by json.loads().\n\nSet skeptic_passed=true only if the finding survives all your checks.\nIf you find any issue, set skeptic_passed=false and explain in skeptic_note.\nSet insufficient_context=true if you cannot confidently validate due to truncated code.'

    def __init__ (self ,model_client =None ,scan_id =None ,redis_client =None ):
        self .model_client =model_client 
        self .scan_id =scan_id 
        self .redis_client =redis_client 

    def fetch_context (self ,filepath :str )->Optional [str ]:
        if not self .scan_id or not self .redis_client :
            return None 
        try :
            raw =self .redis_client .get (f'{self .scan_id }:file_store')
            if not raw :
                return None 
            file_store =json .loads (raw )
            content =file_store .get (filepath )
            if content :
                return content 
            basename =filepath .rsplit ('/',1 )[-1 ]if '/'in filepath else filepath 
            for key ,val in file_store .items ():
                if key .endswith (f'/{basename }')or key ==basename :
                    return val 
            return None 
        except Exception as e :
            logger .warning (f'[SKEPTIC] fetch_context failed for {filepath }: {e }')
            return None 

    def _is_ssrf_finding (self ,finding :Dict )->bool :
        cwe =(finding .get ('cwe_id')or '').upper ()
        if '918'in cwe :
            return True 
        type_str =(finding .get ('type')or '').upper ()
        reason =(finding .get ('reason')or '')+(finding .get ('vulnerable_code')or '')
        if 'SSRF'in type_str or 'SSRF'in reason .upper ():
            return True 
        return False 

    def _cross_file_relevant (self ,finding :Dict )->bool :
        cwe =(finding .get ('cwe_id')or '').upper ()
        type_str =(finding .get ('type')or '').upper ()
        reason =(finding .get ('reason')or '')+(finding .get ('vulnerable_code')or '')
        combined =(cwe +' '+type_str +' '+reason ).upper ()
        if any ((c in cwe for c in ('918','78','22','89','502','611','79'))):
            return True 
        if any ((k in combined for k in ('SSRF','COMMAND INJECTION','PATH TRAVERSAL','SQL INJECTION','DESERIALIZATION','USER INPUT','REQUEST.','STDIN','ARGV','INJECTION','TAINT','CROSS-FILE'))):
            return True 
        return False 

    def _fetch_cross_file_ssrf_context (self ,finding :Dict )->Optional [str ]:
        if not self ._is_ssrf_finding (finding ):
            return None 
        finding_file =(finding .get ('filename')or finding .get ('file')or '').strip ()
        if not finding_file :
            return None 
        if not re .search ('\\.(js|ts|mjs|cjs|py)$',finding_file ,re .I ):
            return None 
        if not self .scan_id or not self .redis_client :
            return None 
        try :
            raw =self .redis_client .get (f'{self .scan_id }:file_store')
            if not raw :
                return None 
            file_store =json .loads (raw )
        except Exception as e :
            logger .warning (f'[SKEPTIC] cross-file SSRF: file_store load failed: {e }')
            return None 
        basename =finding_file .replace ('\\','/').rsplit ('/',1 )[-1 ]
        invoker_patterns =re .compile ('(?:stdin|PIPE|subprocess|proc\\.stdin|\\.write\\s*\\(|phantomjs|node\\s+|child_process)',re .I )
        script_ref_pattern =re .compile (re .escape (basename )+'|phantomjs|check\\.js',re .I )
        max_files =2 
        max_chars_per_file =2800 
        snippets :List [Tuple [str ,str ]]=[]
        for path ,content in file_store .items ():
            if not content or not isinstance (content ,str ):
                continue 
            path_norm =path .replace ('\\','/')
            if path_norm ==finding_file or path_norm .endswith ('/'+finding_file ):
                continue 
            if not script_ref_pattern .search (content )or not invoker_patterns .search (content ):
                continue 
            snippet =content if len (content )<=max_chars_per_file else content [:max_chars_per_file ]+'\n[TRUNCATED]'
            snippets .append ((path_norm ,snippet ))
            if len (snippets )>=max_files :
                break 
        if not snippets :
            return None 
        parts =['Cross-file context (possible invokers of this script — use to decide if the URL/sink input is attacker-controlled):','']
        for path_norm ,snippet in snippets :
            parts .append (f'[{path_norm }]')
            parts .append ('---')
            parts .append (snippet )
            parts .append ('')
        parts .append ("If the above invoker(s) write only a server-controlled URL (e.g. localhost, fixed host, no user input) to stdin, then this is NOT exploitable SSRF — set skeptic_passed=false and skeptic_note='SSRF false positive: URL is not attacker-controlled'.")
        return '\n'.join (parts )

    def _fetch_cross_file_related_context (self ,finding :Dict )->Optional [str ]:
        finding_file =(finding .get ('filename')or finding .get ('file')or '').strip ()
        if not finding_file :
            return None 
        if not self .scan_id or not self .redis_client :
            return None 
        try :
            raw =self .redis_client .get (f'{self .scan_id }:file_store')
            if not raw :
                return None 
            file_store =json .loads (raw )
        except Exception as e :
            logger .warning (f'[SKEPTIC] cross-file related: file_store load failed: {e }')
            return None 
        finding_file_norm =finding_file .replace ('\\','/')
        basename =finding_file_norm .rsplit ('/',1 )[-1 ]
        ref_pattern =re .compile (re .escape (basename )+'|require\\s*\\(\\s*[\\\'\\"]\\.|import\\s+.*from|from\\s+[\\\'\\"]\\.|include|load_file|subprocess|Popen|exec\\s*\\(',re .I )
        source_pattern =re .compile ('(?:request\\.|req\\.|form|get\\s*\\(|input\\s*\\(|argv|stdin|params|query|body|user_?input|user_?controlled)',re .I )
        max_files =2 
        max_chars_per_file =2400 
        snippets :List [Tuple [str ,str ]]=[]
        for path ,content in file_store .items ():
            if not content or not isinstance (content ,str ):
                continue 
            path_norm =path .replace ('\\','/')
            if path_norm ==finding_file_norm or path_norm .endswith ('/'+finding_file_norm ):
                continue 
            if not ref_pattern .search (content ):
                continue 
            if not source_pattern .search (content ):
                continue 
            snippet =content if len (content )<=max_chars_per_file else content [:max_chars_per_file ]+'\n[TRUNCATED]'
            snippets .append ((path_norm ,snippet ))
            if len (snippets )>=max_files :
                break 
        if not snippets :
            return None 
        parts =['Cross-file context (other files that may supply input to this code — use to decide if the vulnerable input is attacker-controlled or server-controlled):','']
        for path_norm ,snippet in snippets :
            parts .append (f'[{path_norm }]')
            parts .append ('---')
            parts .append (snippet )
            parts .append ('')
        parts .append ('If the vulnerable input is only supplied by server-controlled code above (constants, server-built values, no user/request data), the finding may be a false positive — set skeptic_passed=false and explain in skeptic_note.')
        return '\n'.join (parts )

    def _fetch_cross_file_context (self ,finding :Dict )->Optional [str ]:
        if not self ._cross_file_relevant (finding ):
            return None 
        if self ._is_ssrf_finding (finding ):
            return self ._fetch_cross_file_ssrf_context (finding )
        return self ._fetch_cross_file_related_context (finding )

    async def _call_skeptic_api (self ,session ,payload :Dict ,finding_type :str ,max_retries :int =2 )->Optional [Dict ]:
        import aiohttp 
        url =OPENROUTER_API_URL 
        last_error =None 
        for attempt in range (max_retries +1 ):
            try :
                timeout =aiohttp .ClientTimeout (total =120 ,sock_read =90 )
                async with session .post (url ,json =payload ,headers ={'Authorization':f'Bearer {OPENROUTER_API_KEY }'},timeout =timeout )as resp :
                    if resp .status ==200 :
                        result =await resp .json ()
                        if attempt >0 :
                            logger .info ('[SKEPTIC] API call for %s succeeded on attempt %s/%s after retries.',finding_type ,attempt +1 ,max_retries +1 )
                        return result 
                    if resp .status in {408 ,429 ,500 ,502 ,503 ,504 }and attempt <max_retries :
                        wait_time =min (30 ,2 **attempt )
                        logger .warning (f'[SKEPTIC] API error {resp .status } for {finding_type } (attempt {attempt +1 }/{max_retries +1 }), retrying in {wait_time }s...')
                        await asyncio .sleep (wait_time )
                        continue 
                    logger .error (f'[SKEPTIC] API error for {finding_type }: {resp .status }')
                    return None 
            except (asyncio .TimeoutError ,TimeoutError )as e :
                last_error =e 
                if attempt <max_retries :
                    wait_time =min (30 ,2 **attempt )
                    logger .warning (f'[SKEPTIC] Timeout for {finding_type } (attempt {attempt +1 }/{max_retries +1 }), retrying in {wait_time }s...')
                    await asyncio .sleep (wait_time )
                else :
                    logger .error (f'[SKEPTIC] Timeout exhausted for {finding_type }')
                    return None 
            except Exception as e :
                last_error =e 
                error_str =str (e ).lower ()
                is_transient =any ((err in error_str for err in ['transfer','payload','connection','reset','eof']))
                if is_transient and attempt <max_retries :
                    wait_time =min (30 ,2 **attempt )
                    logger .warning (f'[SKEPTIC] Network error for {finding_type }: {e } (attempt {attempt +1 }/{max_retries +1 }), retrying in {wait_time }s...')
                    await asyncio .sleep (wait_time )
                else :
                    logger .error (f'[SKEPTIC] Failed for {finding_type }: {e }')
                    if not is_transient :
                        logger .error (f'[SKEPTIC] Full traceback:\n{traceback .format_exc ()}')
                    return None 
        return None 

    async def run (self ,finding :Dict ,code_context :str ,sanitizer_registry :Dict ,session =None )->Dict :
        cvss_score =finding .get ('cvss_score',0.0 )
        finding_type =finding .get ('type','Unknown')
        if cvss_score <SKEPTIC_CVSS_THRESHOLD :
            finding ['skeptic_passed']=True 
            finding ['skeptic_note']=None 
            finding ['validation_status']='validated'
            return finding 
        if not session :
            logger .warning (f'[SKEPTIC] No session provided for {finding_type }, skipping')
            finding ['skeptic_passed']=True 
            finding ['skeptic_note']='SkepticPass skipped - no session'
            finding ['validation_status']='unvalidated'
            return finding 
        finding_file =finding .get ('filename')or finding .get ('file')or ''
        fetched_context =self .fetch_context (finding_file )if finding_file else None 
        context_source ='full_file'if fetched_context else 'code_context_snippet'
        sanitizer_list =sanitizer_registry .get ('custom_sanitizers',[])
        sanitizer_summary ='\n'.join (sanitizer_list [:10 ])or 'None detected'
        vulnerable_code =safe_slice (finding .get ('vulnerable_code'),1000 )
        reason =safe_slice (finding .get ('reason'),500 )
        code_context_safe =safe_slice (code_context ,2000 )
        review_payload =f"FINDING TO REVIEW:\nType: {finding_type }\nSeverity: {finding .get ('severity','Unknown')}\nCVSS Score: {cvss_score }\nCWE: {finding .get ('cwe_id','Unknown')}\nFunction: {finding .get ('function_name','Unknown')}\nLine: {finding .get ('line','Unknown')}\n\nVulnerable Code:\n{vulnerable_code }\n\nReasoning:\n{reason }\n\nCode Context ({context_source }):\n{(safe_slice (fetched_context ,3000 )if fetched_context else code_context_safe )}\n\nSanitizer Registry:\n{sanitizer_summary }\n"
        cross_file_ctx =self ._fetch_cross_file_context (finding )
        if cross_file_ctx :
            review_payload +='\n\n'+safe_slice (cross_file_ctx ,4500 )
        review_payload +='\n\nReview this finding critically. Find reasons it might be wrong or overstated.\nIMPORTANT: If the code context above is truncated or incomplete, set insufficient_context=true.'
        payload ={'model':SMART_MODEL ,'messages':[{'role':'system','content':self .SKEPTIC_PROMPT },{'role':'user','content':review_payload }],'temperature':0.1 ,'response_format':{'type':'json_object'}}
        result =await self ._call_skeptic_api (session ,payload ,finding_type ,max_retries =2 )
        if result is None :
            finding ['skeptic_passed']=True 
            finding ['skeptic_note']='SkepticPass failed after retries - network/API error'
            finding ['validation_status']='unvalidated'
            return finding 
        try :
            raw_content =result .get ('choices')or []
            raw_content =(raw_content [0 ]or {}).get ('message',{}).get ('content')if raw_content else None 
            if raw_content is None or (isinstance (raw_content ,str )and (not raw_content .strip ())):
                logger .warning (f'[SKEPTIC] Empty or null content for {finding_type }, defaulting to pass')
                finding ['skeptic_passed']=True 
                finding ['skeptic_note']='SkepticPass returned no content'
                finding ['validation_status']='unvalidated'
                return finding 
            try :
                skeptic_result =json .loads (raw_content )
            except json .JSONDecodeError :
                preview =(raw_content or '').strip ().replace ('\n',' ')[:100 ]
                text =(raw_content or '').lower ()
                confirmed_markers =('confirmed','valid','vulnerable')
                rejected_markers =('false positive','not vulnerable','reject')
                if any ((m in text for m in confirmed_markers )):
                    logger .warning (f'[SKEPTIC] Invalid JSON recovery=confirmed for {finding_type }. preview={preview !r }')
                    finding ['skeptic_passed']=True 
                    finding ['skeptic_note']='Recovered verdict from non-JSON output: confirmed/valid/vulnerable'
                    finding ['validation_status']='validated'
                    return finding 
                if any ((m in text for m in rejected_markers )):
                    logger .warning (f'[SKEPTIC] Invalid JSON recovery=rejected for {finding_type }. preview={preview !r }')
                    finding ['skeptic_passed']=False 
                    finding ['skeptic_note']='Recovered verdict from non-JSON output: false positive/not vulnerable/reject'
                    finding ['validation_status']='rejected'
                    return finding 
                logger .warning (f'[SKEPTIC] Invalid JSON recovery=fail_open for {finding_type }. preview={preview !r }')
                finding ['skeptic_passed']=True 
                finding ['skeptic_note']='SkepticPass returned invalid JSON (fail-open)'
                finding ['validation_status']='unvalidated'
                return finding 
            finding ['skeptic_passed']=skeptic_result .get ('skeptic_passed',True )
            finding ['skeptic_note']=skeptic_result .get ('skeptic_note')
            insufficient_ctx =skeptic_result .get ('insufficient_context',False )
            if not finding ['skeptic_passed']and insufficient_ctx :
                logger .warning (f'[SKEPTIC] Safety override for {finding_type }: downgrade reversed because insufficient_context=true (context_source={context_source })')
                finding ['skeptic_passed']=True 
                finding ['skeptic_note']=f"Downgrade reversed: Skeptic reported insufficient context. Original note: {skeptic_result .get ('skeptic_note','')}"
            if not finding ['skeptic_passed']and context_source =='code_context_snippet':
                corrected_score =skeptic_result .get ('corrected_cvss_score')
                original_score =cvss_score 
                try :
                    score_drop =float (original_score )-float (corrected_score or original_score )
                except (TypeError ,ValueError ):
                    score_drop =0.0 
                if score_drop >=3.0 :
                    logger .warning (f'[SKEPTIC] Safety override for {finding_type }: large downgrade ({original_score } -> {corrected_score }) reversed because only snippet context was available (no full file from Redis file store)')
                    finding ['skeptic_passed']=True 
                    finding ['skeptic_note']=f"Large downgrade reversed due to missing full file context. Original note: {skeptic_result .get ('skeptic_note','')}"
            if not finding ['skeptic_passed']:
                corrected_score =skeptic_result .get ('corrected_cvss_score')
                corrected_severity =skeptic_result .get ('corrected_severity')
                if corrected_score is not None :
                    finding ['cvss_score']=corrected_score 
                if corrected_severity :
                    finding ['severity']=corrected_severity 
            if finding ['skeptic_passed']:
                finding ['validation_status']='validated'
            else :
                finding ['validation_status']='skeptic_failed'
            if finding ['skeptic_passed']:
                logger .info (f"[SKEPTIC] {finding_type } - passed=True, status={finding .get ('validation_status')}")
            else :
                note =finding .get ('skeptic_note')or '(no note)'
                corrected =[]
                if skeptic_result .get ('corrected_cvss_score')is not None :
                    corrected .append (f"cvss→{skeptic_result ['corrected_cvss_score']}")
                if skeptic_result .get ('corrected_severity'):
                    corrected .append (f"severity→{skeptic_result ['corrected_severity']}")
                logger .warning (f'[SKEPTIC] {finding_type } - passed=False, status=skeptic_failed | reason: {note }'+(f" | corrected: {', '.join (corrected )}"if corrected else '')+f" | file={finding .get ('filename')or finding .get ('file','?')} line={finding .get ('line','?')}")
                if SKEPTIC_DEBUG :
                    logger .info (f"[SKEPTIC_DEBUG] {finding_type } line={finding .get ('line')} | review_payload (first 800 chars): {review_payload [:800 ]}...")
                    logger .info (f'[SKEPTIC_DEBUG] raw_response: {raw_content }')
        except Exception as e :
            logger .error (f'[SKEPTIC] Error processing result for {finding_type }: {e }')
            logger .error (f'[SKEPTIC] Full traceback:\n{traceback .format_exc ()}')
            finding ['skeptic_passed']=True 
            finding ['skeptic_note']=f'SkepticPass processing error: {str (e )}'
            finding ['validation_status']='unvalidated'
        return finding 
