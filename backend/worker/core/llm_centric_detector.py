import json 
import re 
import asyncio 
from typing import Dict ,Any ,List ,Tuple ,Optional 
import aiohttp 
from .config import OPENROUTER_API_KEY ,OPENROUTER_API_URL ,CHEAP_MODEL ,SMART_MODEL ,DETECTOR_MIN_CONFIDENCE ,logger 
from .utils import clean_json_response 

class LLMCentricDetector :

    def __init__ (self ,model :str =SMART_MODEL ,confidence_threshold :float =DETECTOR_MIN_CONFIDENCE ):
        self .model =model 
        self .confidence_threshold =confidence_threshold 
        self .api_url =OPENROUTER_API_URL 

    async def detect_and_filter (self ,session :aiohttp .ClientSession ,filename :str ,content :str ,context_info :str ='')->Tuple [List [Dict [str ,Any ]],Dict [str ,Any ]]:
        system_prompt =self ._build_detection_prompt ()
        user_content =self ._build_user_content (filename ,content ,context_info )
        payload ={'model':self .model ,'messages':[{'role':'system','content':system_prompt },{'role':'user','content':user_content }],'temperature':0.2 ,'response_format':{'type':'json_object'},'max_tokens':8192 }
        timeout_seconds =180 
        last_error =None 
        for attempt in range (2 ):
            try :
                async with session .post (self .api_url ,json =payload ,headers ={'Authorization':f'Bearer {OPENROUTER_API_KEY }'},timeout =aiohttp .ClientTimeout (total =timeout_seconds ))as resp :
                    if resp .status !=200 :
                        error_text =await resp .text ()
                        logger .error (f'[LLM-CENTRIC] API error: {resp .status }')
                        return ([],{'error':f'API error: {resp .status }'})
                    result =await resp .json ()
                    raw_content =result .get ('choices',[{}])[0 ].get ('message',{}).get ('content')or ''
                    if not raw_content or not raw_content .strip ():
                        logger .warning ('[LLM-CENTRIC] Empty or missing content from API')
                        return ([],{'error':'Empty API response'})
                    clean_content =clean_json_response (raw_content )
                    if not clean_content :
                        logger .warning ('[LLM-CENTRIC] Content empty after cleaning')
                        return ([],{'error':'Empty content after cleaning'})
                    try :
                        data =json .loads (clean_content )
                    except json .JSONDecodeError as e :
                        logger .error (f'[LLM-CENTRIC] JSON parse error: {e }. Raw (first 500 chars): {repr (raw_content [:500 ])}')
                        return ([],{'error':'JSON parse error'})
                    findings =data .get ('findings',[])
                    reasoning =data .get ('analysis_reasoning',{})

                    def _confidence (f :dict )->float :
                        v =f .get ('confidence_score',f .get ('confidence',None ))
                        if v is None :
                            return 8.0 
                        try :
                            return float (v )
                        except (TypeError ,ValueError ):
                            return 8.0 
                    high_confidence_findings =[f for f in findings if _confidence (f )>=self .confidence_threshold ]
                    if findings and (not high_confidence_findings ):
                        logger .warning (f'[LLM-CENTRIC] All {len (findings )} findings below threshold {self .confidence_threshold }; keeping all (fail-open)')
                        high_confidence_findings =findings 
                    filtered_findings =self ._apply_policy_exclusions (high_confidence_findings )
                    metadata ={'total_detected':len (findings ),'high_confidence':len (high_confidence_findings ),'after_policy_filter':len (filtered_findings ),'confidence_threshold':self .confidence_threshold ,'llm_reasoning':reasoning ,'excluded_count':len (findings )-len (filtered_findings )}
                    logger .info (f'[LLM-CENTRIC] Detected {len (findings )}, kept {len (filtered_findings )} after LLM self-filtering')
                    return (filtered_findings ,metadata )
            except (asyncio .TimeoutError ,TimeoutError ,aiohttp .ServerTimeoutError ,aiohttp .ClientError )as e :
                last_error =e 
                if attempt ==0 :
                    logger .warning (f'[LLM-CENTRIC] Attempt {attempt +1 }/2 failed ({e }), retrying...')
                    await asyncio .sleep (2 )
                else :
                    logger .exception (f'[LLM-CENTRIC] Detection failed after retry: {e }')
                    return ([],{'error':str (e )})
            except Exception as e :
                logger .exception (f'[LLM-CENTRIC] Detection failed: {e }')
                return ([],{'error':str (e )})
        return ([],{'error':str (last_error )})

    def _build_detection_prompt (self )->str :
        prompt ='You are an expert security engineer performing code review. Analyze the code for security vulnerabilities.\n\nYOUR TASK:\n1. Identify security vulnerabilities in the code\n2. For each finding, assess confidence (1-10) based on exploitability certainty\n3. Reason about whether this is a true vulnerability or false positive\n4. Report findings where confidence is >= __MIN_CONF__ and exploitability is plausible.\n5. Actively look for chained attack paths, not just isolated bugs.\n\nSECURITY ANALYSIS FRAMEWORK:\n\nWhen analyzing, consider:\n- Is there a concrete attack path? (Not theoretical)\n- Can an attacker actually exploit this? (Not just "best practice")\n- Is this a real security boundary violation?\n- Would you raise this in a production code review?\n- Does this combine with another weakness into a chain (for example IDOR -> privilege escalation -> RCE)?\n\nVULNERABILITY CATEGORIES TO DETECT:\n- Injection: SQLi, Command Injection, NoSQLi, LDAPi, XPathi, SSTI, XXE\n- Authentication: Auth bypass, session fixation, weak password hashing\n- Authorization: IDOR, privilege escalation, broken access control  \n- Cryptography: Hardcoded secrets, weak algorithms (MD5/SHA1), JWT issues\n- Data Exposure: Sensitive data logging, PII leaks, debug info exposure\n- Code Execution: RCE via eval/exec, deserialization, unsafe reflection\n- Input Validation: Path traversal, file upload, unsafe redirects\n\nAUTOMATIC EXCLUSIONS (Policy - do NOT report these):\n1. Denial of Service (DoS) or resource exhaustion attacks\n2. Rate limiting concerns or throttling\n3. Memory/CPU consumption issues\n4. Log spoofing / log injection (outputting user input to logs)\n5. Memory safety issues in Python/JavaScript (impossible)\n6. Race conditions that are purely theoretical (no clear TOCTOU)\nReport with MEDIUM/LOW when clearly exploitable: ReDoS (regex with user input and catastrophic backtracking), open redirects (user-controlled redirect URL), prototype pollution (merge with __proto__ affecting security checks), information disclosure (debug endpoints exposing secrets/tracebacks).\n\nREASONING GUIDELINES:\n\nConfidence Scoring (1-10):\n- 10: Certain exploit, can write PoC immediately\n- 8-9: Clear vulnerable pattern, proven attack path exists\n- 7: Likely vulnerable, needs specific conditions but exploitable\n- 5-6: Suspicious but might be false positive (DON\'T REPORT)\n- Below 5: Almost certainly false positive (DON\'T REPORT)\n\nWhen in doubt, EXCLUDE:\n- "Better to miss a theoretical issue than flood with false positives"\n- Only report what you\'d confidently flag in a PR review\n\nCommon False Positives to EXCLUDE:\n- JSON.parse() or response.json() → Safe standard parsing, NOT deserialization\n- Hardcoded localhost URLs → Dev endpoints, NOT secrets\n- React setState with server data → Auto-escaped by React, NOT XSS\n- router.push() after login → Normal auth flow, NOT access control issue\n- Client-side permission checks → Backend must validate, NOT a vuln\n- Environment variables → Trusted in secure environments\n- UUID validation → UUIDs are unguessable, don\'t need validation\n- Plaintext passwords in seed data → "Hardcoded Credentials", NOT "Deserialization"\n\nRESPONSE FORMAT:\n{\n    "findings": [\n        {\n            "type": "Vulnerability Type (e.g., SQL Injection)",\n            "severity": "HIGH/MEDIUM/LOW",\n            "confidence_score": 1-10,\n            "line": 42,\n            "function_name": "vulnerable_function",\n            "vulnerable_code": "exact code snippet",\n            "reasoning": "Why this is exploitable (attack path)",\n            "false_positive_check": "Why this is NOT a false positive",\n            "exploit_scenario": "How attacker would exploit this",\n            "attack_scenario": {\n                "attacker_profile": "who the attacker is",\n                "preconditions": "what they need first",\n                "actions": "what they do",\n                "outcome": "what they gain"\n            },\n            "is_chain": true,\n            "chain_summary": "short description of the multi-step attack path",\n            "chain_components": ["step 1", "step 2", "step 3"],\n            "cwe_id": "CWE-89"\n        }\n    ],\n    "analysis_reasoning": {\n        "total_scanned": "number of functions/patterns examined",\n        "excluded_count": "how many potential findings were excluded as false positives",\n        "exclusion_reasons": ["list of main reasons for exclusions"],\n        "confidence_distribution": {"high": X, "medium": Y, "low": Z}\n    }\n}\n\nIMPORTANT:\n- Return EMPTY findings array if no plausible vulnerabilities are found\n- Prefer precision, but keep borderline plausible findings for downstream validation\n- Focus on exploitability and actionable signal\n- Think like a pentester - would you actually exploit this?\n- Use adversarial framing: assume the attacker is actively trying to break the code, chain weaknesses together, and move from entry point to impact.'
        return prompt .replace ('__MIN_CONF__',str (int (DETECTOR_MIN_CONFIDENCE )))

    def _build_user_content (self ,filename :str ,content :str ,context_info :str )->str :
        numbered_lines =[]
        for i ,line in enumerate (content .splitlines (),1 ):
            numbered_lines .append (f'{i :4}| {line }')
        numbered_code ='\n'.join (numbered_lines )
        return f'Analyze this code for security vulnerabilities:\n\nFile: {filename }\n\nProject Context:\n{context_info [:2000 ]}\n\nCode to Analyze:\n```\n{numbered_code [:32000 ]}\n```\n\nProvide your analysis in the specified JSON format. Think carefully about each potential finding - is it really exploitable or just a pattern match?'

    def _apply_policy_exclusions (self ,findings :List [Dict [str ,Any ]])->List [Dict [str ,Any ]]:
        policy_exclusions =['(?i)(denial.of.service|dos.attack|resource.exhaustion)','(?i)(rate.limit|throttling)','(?i)(redos|regex.dos)']
        kept =[]
        for finding in findings :
            finding_type =finding .get ('type','')
            should_exclude =False 
            for pattern in policy_exclusions :
                if re .search (pattern ,finding_type ):
                    should_exclude =True 
                    break 
            if not should_exclude :
                kept .append (finding )
            else :
                logger .debug (f'[LLM-CENTRIC] Policy exclusion: {finding_type }')
        return kept 

class SmartLLMFilter :

    def __init__ (self ,model :str =CHEAP_MODEL ,confidence_boost :bool =True ):
        self .model =model 
        self .confidence_boost =confidence_boost 
        self .api_url =OPENROUTER_API_URL 

    async def filter_findings_batch (self ,session :aiohttp .ClientSession ,findings :List [Dict [str ,Any ]],filename :str ,file_content :str )->Tuple [List [Dict [str ,Any ]],List [Dict [str ,Any ]],Dict [str ,Any ]]:
        if not findings :
            return ([],[],{'total':0 ,'kept':0 ,'excluded':0 })
        if len (findings )>10 :
            return await self ._filter_large_batch (session ,findings ,filename ,file_content )
        system_prompt ='You are a senior security engineer reviewing vulnerability findings.\n\nYour task: Judge each finding as TRUE POSITIVE or FALSE POSITIVE.\n\nFor each finding, evaluate:\n1. Is there a concrete exploit path? (Not just a pattern match)\n2. Would this actually be exploitable in production?\n3. Is this a real security issue vs theoretical concern?\n\nConfidence Guidelines:\n- Keep findings with confidence >= 7 (true vulnerabilities)\n- Exclude findings with confidence < 7 (likely false positives)\n\nCommon False Positive Patterns:\n- React setState flagged as XSS (React auto-escapes)\n- JSON.parse flagged as deserialization (it\'s safe)\n- localhost URLs flagged as secrets (dev endpoints)\n- Client-side auth checks (backend must validate)\n\nResponse format:\n{\n    "judgments": [\n        {\n            "finding_index": 0,\n            "keep": true/false,\n            "confidence": 1-10,\n            "reasoning": "brief explanation",\n            "false_positive_reason": "if excluding, explain why"\n        }\n    ]\n}'
        findings_text =[]
        for i ,f in enumerate (findings ):
            findings_text .append (f"Finding {i }:\n  Type: {f .get ('type','Unknown')}\n  Severity: {f .get ('severity','MEDIUM')}\n  Line: {f .get ('line',0 )}\n  Code: {f .get ('vulnerable_code','N/A')[:100 ]}\n  Description: {f .get ('description','N/A')[:150 ]}\n")
        user_content =f'Review these {len (findings )} vulnerability findings from {filename }:\n\n{chr (10 ).join (findings_text )}\n\nJudge each finding. Return JSON with your judgments.'
        payload ={'model':self .model ,'messages':[{'role':'system','content':system_prompt },{'role':'user','content':user_content }],'temperature':0.1 ,'response_format':{'type':'json_object'},'max_tokens':4096 }
        try :
            async with session .post (self .api_url ,json =payload ,headers ={'Authorization':f'Bearer {OPENROUTER_API_KEY }'},timeout =aiohttp .ClientTimeout (total =60 ))as resp :
                if resp .status !=200 :
                    return (findings ,[],{'error':f'API error: {resp .status }','kept':len (findings )})
                result =await resp .json ()
                raw_content =result ['choices'][0 ]['message']['content']
                try :
                    data =json .loads (raw_content )
                except json .JSONDecodeError :
                    return (findings ,[],{'error':'JSON parse error','kept':len (findings )})
                judgments =data .get ('judgments',[])
                kept =[]
                excluded =[]
                for judgment in judgments :
                    idx =judgment .get ('finding_index',0 )
                    if idx >=len (findings ):
                        continue 
                    finding =findings [idx ]
                    if judgment .get ('keep',True ):
                        finding ['_llm_judgment']={'confidence':judgment .get ('confidence',7 ),'reasoning':judgment .get ('reasoning','')}
                        kept .append (finding )
                    else :
                        finding ['_llm_judgment']={'excluded':True ,'reason':judgment .get ('false_positive_reason','Filtered by LLM')}
                        excluded .append (finding )
                judged_indices ={j .get ('finding_index',0 )for j in judgments }
                for i ,finding in enumerate (findings ):
                    if i not in judged_indices :
                        kept .append (finding )
                metadata ={'total':len (findings ),'kept':len (kept ),'excluded':len (excluded ),'reduction_rate':round (len (excluded )/max (1 ,len (findings ))*100 ,1 )}
                return (kept ,excluded ,metadata )
        except Exception as e :
            logger .exception (f'[SMART-FILTER] Batch filtering failed: {e }')
            return (findings ,[],{'error':str (e ),'kept':len (findings )})

    async def _filter_large_batch (self ,session :aiohttp .ClientSession ,findings :List [Dict [str ,Any ]],filename :str ,file_content :str )->Tuple [List [Dict [str ,Any ]],List [Dict [str ,Any ]],Dict [str ,Any ]]:
        all_kept =[]
        all_excluded =[]
        chunk_size =10 
        for i in range (0 ,len (findings ),chunk_size ):
            chunk =findings [i :i +chunk_size ]
            kept ,excluded ,_ =await self .filter_findings_batch (session ,chunk ,filename ,file_content )
            all_kept .extend (kept )
            all_excluded .extend (excluded )
        metadata ={'total':len (findings ),'kept':len (all_kept ),'excluded':len (all_excluded ),'chunks':(len (findings )+chunk_size -1 )//chunk_size }
        return (all_kept ,all_excluded ,metadata )

async def llm_centric_scan (session :aiohttp .ClientSession ,filename :str ,content :str ,context_info :str ='',use_smart_filter :bool =True )->Tuple [List [Dict [str ,Any ]],Dict [str ,Any ]]:
    detector =LLMCentricDetector ()
    findings ,detection_meta =await detector .detect_and_filter (session ,filename ,content ,context_info )
    if not findings or not use_smart_filter :
        return (findings ,detection_meta )
    smart_filter =SmartLLMFilter ()
    kept ,excluded ,filter_meta =await smart_filter .filter_findings_batch (session ,findings ,filename ,content )
    if findings and (not kept ):
        logger .warning (f'[LLM-CENTRIC] Smart filter kept 0 of {len (findings )}; using pre-filter findings (fail-open)')
        kept =findings 
    combined_meta ={'detection':detection_meta ,'filtering':filter_meta ,'final_count':len (kept )}
    return (kept ,combined_meta )
