import json 
from typing import Dict ,List ,Optional ,Any 
from ..config import OPENROUTER_API_KEY ,OPENROUTER_API_URL ,SMART_MODEL ,SCAN_TTL ,HIGH_RECALL_MODE ,logger 
from ..redis_client import REDIS_AVAILABLE ,redis_client 

class CrossFileConsistencyChecker :

    def __init__ (self ):
        self ._last_removed_findings :List [Dict [str ,Any ]]=[]
        self ._last_upgrade_count :int =0 

    def _build_findings_summary (self ,all_findings :List [Dict ])->str :
        summary_parts =[]
        for i ,finding in enumerate (all_findings ):
            if not isinstance (finding ,dict ):
                summary_parts .append (f'Finding {i }: [malformed finding: {type (finding ).__name__ }]')
                continue 
            summary_parts .append (f"Finding {i }:\n  File: {finding .get ('filename','unknown')}\n  Function: {finding .get ('function_name','unknown')}\n  Type: {finding .get ('type','unknown')}\n  Sink: {str (finding .get ('vulnerable_code','N/A'))[:100 ]}\n  Confidence: {finding .get ('confidence_score',0 )}\n  CVSS: {finding .get ('cvss_score',0 )}\n")
        return '\n'.join (summary_parts )

    def _load_graph_context (self ,scan_id :Optional [str ])->Dict [str ,Dict ]:
        if not scan_id or not REDIS_AVAILABLE :
            return {'call_graph':{},'file_deps':{},'dead_code_map':{}}
        return {'call_graph':self ._redis_json (f'{scan_id }:call_graph'),'file_deps':self ._redis_json (f'{scan_id }:file_deps'),'dead_code_map':self ._redis_json (f'{scan_id }:dead_code_map')}

    def _redis_json (self ,key :str )->Dict :
        try :
            raw =redis_client .get (key )
            if not raw :
                return {}
            return json .loads (raw )
        except Exception as e :
            logger .warning (f'CrossFileConsistency: failed to load Redis JSON for key {key }: {e }')
            return {}

    def _safe_float (self ,value :Any ,default :float =0.0 )->float :
        try :
            if value is None :
                return default 
            return float (value )
        except Exception :
            return default 

    def _normalize_correction_items (self ,items :Any ,kind :str )->List [Dict [str ,Any ]]:
        if not isinstance (items ,list ):
            logger .warning (f"CrossFileConsistency: expected list for '{kind }', got {type (items ).__name__ }; ignoring")
            return []
        normalized :List [Dict [str ,Any ]]=[]
        for item in items :
            if not isinstance (item ,dict ):
                logger .warning (f'CrossFileConsistency: malformed {kind } item ignored: {item !r }')
                continue 
            idx =item .get ('finding_index')
            reason =item .get ('reason','cross-file consistency rule')
            if idx is None :
                logger .warning (f'CrossFileConsistency: {kind } item missing finding_index; ignored: {item !r }')
                continue 
            try :
                idx =int (idx )
            except Exception :
                logger .warning (f'CrossFileConsistency: non-integer finding_index in {kind } item; ignored: {item !r }')
                continue 
            normalized .append ({'finding_index':idx ,'reason':str (reason )})
        return normalized 

    def _heuristic_corrections (self ,all_findings :List [Dict ],sanitizer_registry :Dict ,graph_ctx :Dict [str ,Dict ])->Dict [str ,List [Dict [str ,Any ]]]:
        remove :List [Dict [str ,Any ]]=[]
        upgrade :List [Dict [str ,Any ]]=[]
        seen_by_fp :Dict [str ,int ]={}
        seen_by_sink :Dict [str ,int ]={}
        dead_code_map =graph_ctx .get ('dead_code_map',{})or {}
        call_graph =graph_ctx .get ('call_graph',{})or {}
        for idx ,finding in enumerate (all_findings ):
            if not isinstance (finding ,dict ):
                logger .warning (f'CrossFileConsistency: skipping malformed finding at index {idx }: {type (finding ).__name__ }')
                continue 
            fingerprint =finding .get ('fingerprint')
            sink =str (finding .get ('vulnerable_code')or '').strip ()[:200 ]
            severity =str (finding .get ('severity')or '').upper ()
            filename =finding .get ('filename')or finding .get ('file')or ''
            function_name =finding .get ('function_name')or finding .get ('trigger')or ''
            function_key =f'{filename }::{function_name }'if filename and function_name else None 
            confidence =self ._safe_float (finding .get ('confidence_score',0 ),0.0 )
            if fingerprint :
                prev =seen_by_fp .get (fingerprint )
                if prev is not None and prev <len (all_findings )and isinstance (all_findings [prev ],dict ):
                    prev_conf =self ._safe_float (all_findings [prev ].get ('confidence_score',0 ),0.0 )
                    if confidence >prev_conf :
                        remove .append ({'finding_index':prev ,'reason':'duplicate fingerprint with lower confidence'})
                        seen_by_fp [fingerprint ]=idx 
                    else :
                        remove .append ({'finding_index':idx ,'reason':'duplicate fingerprint'})
                        continue 
                else :
                    seen_by_fp [fingerprint ]=idx 
            if sink :
                prev =seen_by_sink .get (sink )
                if prev is not None and prev <len (all_findings )and isinstance (all_findings [prev ],dict ):
                    prev_conf =self ._safe_float (all_findings [prev ].get ('confidence_score',0 ),0.0 )
                    if confidence >prev_conf :
                        remove .append ({'finding_index':prev ,'reason':'duplicate sink with lower confidence'})
                        seen_by_sink [sink ]=idx 
                    else :
                        remove .append ({'finding_index':idx ,'reason':'duplicate sink'})
                        continue 
                else :
                    seen_by_sink [sink ]=idx 
            dead_info =dead_code_map .get (function_key ,{})if function_key else {}
            if isinstance (dead_info ,dict )and dead_info .get ('is_test_only'):
                remove .append ({'finding_index':idx ,'reason':'finding only reachable from test code'})
                continue 
            call_info =call_graph .get (function_key ,{})if function_key else {}
            if isinstance (call_info ,dict )and call_info .get ('is_entry_point'):
                upgrade .append ({'finding_index':idx ,'reason':'entry point confirmed reachable from public route'})
            elif severity in {'MEDIUM','LOW'}and finding .get ('cross_file_taint'):
                upgrade .append ({'finding_index':idx ,'reason':'cross-file call path corroborates exploitability'})
        return {'remove':remove ,'upgrade':upgrade }

    def _merge_corrections (self ,base :Dict ,extra :Dict )->Dict [str ,List [Dict [str ,Any ]]]:
        merged ={'remove':self ._normalize_correction_items (base .get ('remove',[]),'remove'),'upgrade':self ._normalize_correction_items (base .get ('upgrade',[]),'upgrade')}
        seen_remove ={item .get ('finding_index')for item in merged ['remove']}
        seen_upgrade ={item .get ('finding_index')for item in merged ['upgrade']}
        for item in self ._normalize_correction_items (extra .get ('remove',[]),'remove'):
            idx =item .get ('finding_index')
            if idx not in seen_remove :
                merged ['remove'].append (item )
                seen_remove .add (idx )
        for item in self ._normalize_correction_items (extra .get ('upgrade',[]),'upgrade'):
            idx =item .get ('finding_index')
            if idx not in seen_upgrade :
                merged ['upgrade'].append (item )
                seen_upgrade .add (idx )
        return merged 

    async def check (self ,all_findings :List [Dict ],sanitizer_registry :Dict ,session =None ,scan_id :Optional [str ]=None )->Dict [str ,List [Dict [str ,Any ]]]:
        if not all_findings :
            return {'remove':[],'upgrade':[]}
        graph_ctx =self ._load_graph_context (scan_id )
        heuristic_result =self ._heuristic_corrections (all_findings =all_findings ,sanitizer_registry =sanitizer_registry ,graph_ctx =graph_ctx )
        if not session :
            logger .warning ('No session provided for CrossFileConsistencyChecker; using heuristic-only mode')
            return heuristic_result 
        findings_summary =self ._build_findings_summary (all_findings )
        sanitizer_summary ='\n'.join ([str (s )for s in sanitizer_registry .get ('custom_sanitizers',[])[:10 ]])or 'None'
        entry_points =[]
        for key ,value in (graph_ctx .get ('call_graph',{})or {}).items ():
            if isinstance (value ,dict )and value .get ('is_entry_point'):
                entry_points .append (key )
        consistency_prompt ='You are analyzing a set of security findings across an entire project.\nYour job is to find inconsistencies that only appear when looking at all findings together.\n\nCheck for:\n1. CONTRADICTIONS: Does any finding flag a function as vulnerable when another finding\n   already shows its input is sanitized upstream? Look for input->sanitizer->sink chains.\n   IMPORTANT: Do not infer sanitization merely because a function name appears in a rationale,\n   description, or code snippet. Only recommend removal when there is concrete evidence of a\n   true sanitization step that meaningfully neutralizes attacker control before the sink.\n\n2. DUPLICATES: Same sink, different descriptions. If two findings point to the same\n   vulnerable line, they are duplicates. Keep the highest confidence one.\n\n3. TEST-ONLY PATHS: Findings in files that are clearly **unit/test** files by **filename**:\n   - test_*.py, *_test.py, *.test.js, *.spec.js, *.test.ts, *.spec.ts (e.g. auth_test.py, app.spec.js).\n   Do NOT remove findings just because the path contains a directory named "test" or "tests".\n   Files like test/index.ts, tests/e2e/app.ts, or benchmark/vulnerable-apps/test/index.ts are often the\n   main application entry point, not unit tests — keep those findings unless they are true duplicates.\n\n4. SEVERITY INFLATION: Multiple medium findings on the same function shouldn\'t stack\n   into a critical finding. Each finding should stand on its own.\n\nCRITICAL SAFETY RULES:\n- Default to keeping findings if unsure.\n- Do NOT remove a finding solely because the sanitizer registry contains a function with a similar name.\n- Encryption/decryption, encoding/decoding, hashing, and serialization helpers are not automatically sanitizers.\n- For cryptographic findings (padding oracle, CBC/PKCS7, unauthenticated encryption, malleability),\n  be especially conservative: do not mark them as sanitized upstream without explicit, concrete evidence.\n\nReturn JSON in this exact format:\n{\n  "remove": [\n    {"finding_index": 0, "reason": "input sanitized upstream in auth_service.py"},\n    {"finding_index": 3, "reason": "duplicate of finding 1, same sink"}\n  ],\n  "upgrade": [\n    {"finding_index": 2, "reason": "entry point confirmed reachable from public route"}\n  ]\n}\n\nOnly include findings that have clear issues. Default to keeping findings if unsure.\nDo not mark findings as "test-only" solely because the path contains the substring "test" (e.g. test/index.ts is usually an app entry).'
        review_payload =f"FINDINGS SUMMARY:\n{findings_summary }\n\nSANITIZER REGISTRY:\n{sanitizer_summary }\n\nENTRY POINTS:\n{chr (10 ).join (entry_points [:20 ])or 'None'}\n\nAnalyze these findings for contradictions, duplicates, and test-only paths."
        try :
            url =OPENROUTER_API_URL 
            payload ={'model':SMART_MODEL ,'messages':[{'role':'system','content':consistency_prompt },{'role':'user','content':review_payload }],'temperature':0.1 ,'response_format':{'type':'json_object'}}
            import aiohttp 
            timeout =aiohttp .ClientTimeout (total =120 )
            async with session .post (url ,json =payload ,headers ={'Authorization':f'Bearer {OPENROUTER_API_KEY }'},timeout =timeout )as resp :
                if resp .status !=200 :
                    logger .error (f'CrossFileConsistency API error: {resp .status }')
                    return heuristic_result 
                result =await resp .json ()
                choices =result .get ('choices')
                if not isinstance (choices ,list )or not choices :
                    logger .warning ('CrossFileConsistency returned no choices; using heuristic result')
                    return heuristic_result 
                first_choice =choices [0 ]
                if not isinstance (first_choice ,dict ):
                    logger .warning ('CrossFileConsistency returned malformed first choice; using heuristic result')
                    return heuristic_result 
                message =first_choice .get ('message',{})
                if not isinstance (message ,dict ):
                    logger .warning ('CrossFileConsistency returned malformed message; using heuristic result')
                    return heuristic_result 
                raw_content =message .get ('content')
                if raw_content is None :
                    logger .warning ('CrossFileConsistency returned null content; using heuristic result')
                    return heuristic_result 
                if not isinstance (raw_content ,str ):
                    logger .warning (f'CrossFileConsistency returned non-string content ({type (raw_content ).__name__ }); using heuristic result')
                    return heuristic_result 
                try :
                    consistency_result =json .loads (raw_content )
                except json .JSONDecodeError :
                    logger .warning ('CrossFileConsistency returned invalid JSON; using heuristic result')
                    return heuristic_result 
                if not isinstance (consistency_result ,dict ):
                    logger .warning ('CrossFileConsistency returned non-object JSON; using heuristic result')
                    return heuristic_result 
                remove_list =self ._normalize_correction_items (consistency_result .get ('remove',[]),'remove')
                upgrade_list =self ._normalize_correction_items (consistency_result .get ('upgrade',[]),'upgrade')
                merged =self ._merge_corrections (heuristic_result ,{'remove':remove_list ,'upgrade':upgrade_list })
                logger .info (f"CrossFileConsistency: {len (merged ['remove'])} to remove, {len (merged ['upgrade'])} to upgrade")
                return merged 
        except Exception as e :
            logger .error (f'CrossFileConsistency failed: {e }')
            return heuristic_result 

    def apply_corrections (self ,all_findings :List [Dict ],corrections :Dict ,scan_id :Optional [str ]=None )->List [Dict ]:
        remove_items =self ._normalize_correction_items (corrections .get ('remove',[]),'remove')
        upgrade_items_list =self ._normalize_correction_items (corrections .get ('upgrade',[]),'upgrade')
        remove_map ={item ['finding_index']:item .get ('reason','cross-file consistency rule')for item in remove_items }
        APP_ENTRY_NAMES =('index.ts','index.js','main.ts','main.js','app.ts','app.js','server.ts','server.js')
        for idx in list (remove_map .keys ()):
            reason =str (remove_map [idx ]).lower ()
            if 'test'not in reason :
                continue 
            if 'duplicate'in reason and 'sink'in reason :
                continue 
            if 'duplicate'in reason and 'fingerprint'in reason :
                continue 
            finding =all_findings [idx ]if 0 <=idx <len (all_findings )and isinstance (all_findings [idx ],dict )else {}
            filename =str (finding .get ('filename')or finding .get ('file')or '').replace ('\\','/')
            basename =filename .split ('/')[-1 ].lower ()
            if basename in APP_ENTRY_NAMES :
                logger .info ("CrossFileConsistency: keeping finding %s (%s) — app-entry file %s in path with 'test'",idx ,finding .get ('type'),basename )
                del remove_map [idx ]
        upgrade_items ={item ['finding_index']:item for item in upgrade_items_list }
        corrected :List [Dict [str ,Any ]]=[]
        removed_findings :List [Dict [str ,Any ]]=[]
        for i ,finding in enumerate (all_findings ):
            if not isinstance (finding ,dict ):
                logger .warning (f'CrossFileConsistency: malformed finding at index {i } preserved unchanged: {type (finding ).__name__ }')
                corrected .append (finding )
                continue 
            if i in remove_map :
                removal_reason =remove_map [i ]
                reason_lower =str (removal_reason ).lower ()
                if 'duplicate'in reason_lower and 'fingerprint'in reason_lower :
                    removal_rule ='duplicate_fingerprint'
                elif 'duplicate'in reason_lower and 'sink'in reason_lower :
                    removal_rule ='duplicate_sink'
                elif 'sanitizer'in reason_lower :
                    removal_rule ='sanitized_upstream'
                elif 'test'in reason_lower :
                    removal_rule ='test_only_path'
                elif 'dead'in reason_lower :
                    removal_rule ='dead_code'
                else :
                    removal_rule ='cross_file_consistency'
                finding ['_removed_by']='cross_file_consistency'
                finding ['_removal_reason']=removal_reason 
                finding ['_removal_rule']=removal_rule 
                removed_findings .append (finding )
                logger .info (f"Removing finding {i }: {finding .get ('type')} ({removal_rule }: {removal_reason })")
                continue 
            if i in upgrade_items :
                finding ['_upgraded']=True 
                finding ['_upgrade_reason']=upgrade_items [i ].get ('reason')
                if finding .get ('severity')not in ['CRITICAL','HIGH']:
                    finding ['severity']='HIGH'
                score =self ._safe_float (finding .get ('confidence_score',0 ),0.0 )
                if score <=10 :
                    finding ['confidence_score']=min (10 ,round (score +1 ))
                else :
                    finding ['confidence_score']=min (100 ,round (score +10 ))
            corrected .append (finding )
        if scan_id and REDIS_AVAILABLE and removed_findings :
            try :
                consistency_log =[]
                for rf in removed_findings :
                    consistency_log .append ({'type':rf .get ('type'),'file':rf .get ('filename')or rf .get ('file'),'line':rf .get ('line'),'function':rf .get ('function_name')or rf .get ('trigger'),'_removed_by':rf .get ('_removed_by'),'_removal_reason':rf .get ('_removal_reason'),'_removal_rule':rf .get ('_removal_rule')})
                redis_client .setex (f'{scan_id }:consistency_log',SCAN_TTL ,json .dumps (consistency_log ))
                logger .info (f'Stored {len (consistency_log )} consistency removals to Redis for scan {scan_id }')
            except Exception as e :
                logger .warning (f'Failed to store consistency log in Redis: {e }')
        self ._last_removed_findings =removed_findings 
        self ._last_upgrade_count =len (upgrade_items )
        return corrected 
