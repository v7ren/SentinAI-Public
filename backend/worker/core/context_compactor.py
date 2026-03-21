import json 
import re 
from typing import Any ,Dict ,List ,Optional ,Set ,Tuple 
import aiohttp 
from .config import COMPACTION_CHEAP_MODEL ,COMPACTION_CHEAP_MODEL_TIMEOUT_SECONDS ,COMPACTION_LLM_MAX_CANDIDATES ,COMPACTION_MAX_DROP_RATIO ,COMPACTION_USE_CHEAP_LLM ,OPENROUTER_API_KEY ,OPENROUTER_API_URL ,logger 
RISKY_TOKENS =('exec(','eval(','subprocess','os.system','pickle.loads','yaml.load','jwt.','token','password','secret','api_key','cursor.execute','query(','redirect(','send_file(','open(','chmod(','setcookie','cookie','request.args','request.form','request.json')

def _is_blank (line :str )->bool :
    return not line .strip ()

def _is_comment_only (line :str )->bool :
    s =line .strip ()
    return s .startswith ('#')or s .startswith ('//')or s .startswith ('/*')or s .startswith ('*')or s .startswith ('*/')

def _is_import_only (line :str )->bool :
    s =line .strip ()
    if re .match ('^(from\\s+\\S+\\s+import\\s+.+)$',s ):
        return True 
    if re .match ('^(import\\s+[\\w\\.\\,\\s]+)$',s ):
        return True 
    if re .match ('^(const|let|var)\\s+\\w+\\s*=\\s*require\\(.+\\)\\s*;?$',s ):
        return True 
    if re .match ('^import\\s+.+\\s+from\\s+[\'\\"].+[\'\\"]\\s*;?$',s ):
        return True 
    return False 

def _is_trivial_log_or_print (line :str )->bool :
    s =line .strip ()
    if re .match ('^(print|console\\.log|logger\\.(debug|info|warning|error)|logging\\.(debug|info|warning|error))\\s*\\(',s ):
        if re .search ('(\\{.+\\}|%s|%d|f\\"|f\'|\\+|\\w+\\s*,)',s ):
            return False 
        return True 
    return False 

def _has_risky_signal (line :str ,recall_keywords :Optional [Set [str ]]=None )->bool :
    s =line .lower ()
    if any ((tok in s for tok in RISKY_TOKENS )):
        return True 
    if recall_keywords :
        for kw in recall_keywords :
            if kw and kw in s :
                return True 
    return False 

async def _llm_judge_drop_candidates (session :aiohttp .ClientSession ,filename :str ,candidates :List [Dict [str ,Any ]])->Set [int ]:
    if not candidates :
        return set ()
    payload ={'model':COMPACTION_CHEAP_MODEL ,'messages':[{'role':'system','content':'You are a code preprocessor for security scanning context reduction.\nTask: Decide if each candidate line can be dropped without harming vulnerability detection.\nOnly drop lines that are clearly low-signal noise: trivial imports, blank/comment-only, or pure static debug prints/logs with no runtime variables.\nIf unsure, KEEP.\nReturn strict JSON object: {"decisions":[{"line":123,"drop":true|false,"reason":"..."}]}.\nNever return markdown.'},{'role':'user','content':json .dumps ({'file':filename ,'candidates':candidates },ensure_ascii =True )}],'temperature':0.0 ,'response_format':{'type':'json_object'},'max_tokens':2500 }
    try :
        async with session .post (OPENROUTER_API_URL ,json =payload ,headers ={'Authorization':f'Bearer {OPENROUTER_API_KEY }'},timeout =aiohttp .ClientTimeout (total =COMPACTION_CHEAP_MODEL_TIMEOUT_SECONDS ))as resp :
            if resp .status !=200 :
                logger .warning ('[COMPACTOR] LLM arbitration failed status=%s; using deterministic fallback',resp .status )
                return set ()
            data =await resp .json ()
            raw =(data .get ('choices',[{}])[0 ].get ('message',{}).get ('content')or '').strip ()
            parsed =json .loads (raw )
            decisions =parsed .get ('decisions',[])
            return {int (d .get ('line'))for d in decisions if d .get ('drop')is True }
    except Exception as e :
        logger .warning ('[COMPACTOR] LLM arbitration exception: %s',e )
        return set ()

async def compact_security_context (session :aiohttp .ClientSession ,filename :str ,content :str ,recall_keywords :Optional [List [str ]]=None )->Tuple [str ,Dict [str ,Any ]]:
    lines =content .splitlines ()
    total =len (lines )
    if total ==0 :
        return (content ,{'enabled':True ,'total_lines':0 ,'kept_lines':0 ,'dropped_lines':0 ,'drop_ratio':0.0 })
    recall_set ={k .lower ()for k in recall_keywords or []if isinstance (k ,str )and k .strip ()}
    keep_flags =[True ]*total 
    candidate_rows :List [Dict [str ,Any ]]=[]
    deterministically_dropped =0 
    for idx ,line in enumerate (lines ,start =1 ):
        stripped =line .strip ()
        if re .match ('^(def|class|async def|function|if|elif|else|try|except|finally|for|while|with)\\b',stripped ):
            continue 
        if _has_risky_signal (line ,recall_set ):
            continue 
        if _is_blank (line )or _is_comment_only (line ):
            keep_flags [idx -1 ]=False 
            deterministically_dropped +=1 
            continue 
        if _is_import_only (line )or _is_trivial_log_or_print (line ):
            candidate_rows .append ({'line':idx ,'code':line [:240 ]})
    llm_drop_lines :Set [int ]=set ()
    if COMPACTION_USE_CHEAP_LLM and candidate_rows :
        llm_candidates =candidate_rows [:COMPACTION_LLM_MAX_CANDIDATES ]
        llm_drop_lines =await _llm_judge_drop_candidates (session ,filename ,llm_candidates )
    else :
        llm_drop_lines ={row ['line']for row in candidate_rows }
    for ln in llm_drop_lines :
        if 1 <=ln <=total and keep_flags [ln -1 ]:
            keep_flags [ln -1 ]=False 
    dropped =sum ((1 for k in keep_flags if not k ))
    drop_ratio =dropped /max (1 ,total )
    if drop_ratio >COMPACTION_MAX_DROP_RATIO :
        target_drop =int (total *COMPACTION_MAX_DROP_RATIO )
        for i in range (total -1 ,-1 ,-1 ):
            if dropped <=target_drop :
                break 
            if not keep_flags [i ]:
                keep_flags [i ]=True 
                dropped -=1 
    kept_lines =[line for i ,line in enumerate (lines )if keep_flags [i ]]
    compacted ='\n'.join (kept_lines ).strip ()
    if not compacted :
        compacted =content 
        dropped =0 
    meta ={'enabled':True ,'model_used':COMPACTION_CHEAP_MODEL if COMPACTION_USE_CHEAP_LLM else 'deterministic','total_lines':total ,'kept_lines':total -dropped ,'dropped_lines':dropped ,'drop_ratio':round (dropped /max (1 ,total ),3 ),'deterministic_dropped':deterministically_dropped ,'llm_candidate_count':len (candidate_rows ),'llm_dropped_count':len (llm_drop_lines )}
    return (compacted ,meta )
