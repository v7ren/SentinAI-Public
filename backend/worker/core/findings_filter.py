import os 
import re 
from typing import Dict ,Any ,List ,Tuple ,Optional 
from dataclasses import dataclass 
import json 
from .config import PHASE1_CONFIDENCE_THRESHOLD ,HIGH_RECALL_MODE ,FP_FILTER_STRICTNESS ,logger 
HARD_DETECTION_PATTERNS ={'SQL_INJECTION':[{'pattern':'["\\\']\\s*(?:SELECT|INSERT|UPDATE|DELETE)\\s+.*%\\s*\\(','confidence':90 ,'severity':'HIGH','cwe':'CWE-89','description':'SQL query constructed with % string formatting - vulnerable to SQL injection'},{'pattern':'f["\\\'][^"\\\']*(?:SELECT|INSERT|UPDATE|DELETE)\\s+[^"\\\']*\\{[^}]+\\}','confidence':90 ,'severity':'HIGH','cwe':'CWE-89','description':'SQL query constructed with f-string - vulnerable to SQL injection'},{'pattern':'["\\\'][^"\\\']*(?:SELECT|INSERT|UPDATE|DELETE)\\s+[^"\\\']*["\\\']\\.format\\(','confidence':90 ,'severity':'HIGH','cwe':'CWE-89','description':'SQL query constructed with .format() - vulnerable to SQL injection'},{'pattern':'["\\\'][^"\\\']*(?:SELECT|INSERT|UPDATE|DELETE|WHERE)\\s+[^"\\\']*["\\\']\\s*\\+\\s*\\w+','confidence':85 ,'severity':'HIGH','cwe':'CWE-89','description':'SQL query constructed with string concatenation - vulnerable to SQL injection'}],'HARDCODED_SECRET':[{'pattern':'^\\s*SECRET_KEY\\s*=\\s*["\\\'][^"\\\']+["\\\']\\s*$','confidence':95 ,'severity':'HIGH','cwe':'CWE-798','description':'Hardcoded SECRET_KEY detected in configuration file'},{'pattern':'^\\s*\\w*API_KEY\\w*\\s*=\\s*["\\\'][^"\\\']{8,}["\\\']\\s*$','confidence':90 ,'severity':'HIGH','cwe':'CWE-798','description':'Hardcoded API key detected'},{'pattern':'^\\s*\\w*(?:PASSWORD|PASSWD|PWD)\\w*\\s*=\\s*["\\\'][^"\\\']{4,}["\\\']\\s*$','confidence':85 ,'severity':'HIGH','cwe':'CWE-798','description':'Hardcoded password detected','exclusions':['os.environ','getenv','config(','request.']},{'pattern':'^\\s*\\w*(?:TOKEN|AUTH_TOKEN|ACCESS_TOKEN)\\w*\\s*=\\s*["\\\'][^"\\\']{8,}["\\\']\\s*$','confidence':90 ,'severity':'HIGH','cwe':'CWE-798','description':'Hardcoded authentication token detected'}],'REFLECTED_XSS':[{'pattern':'request\\.(?:args|form|json|data)\\.(?:get|\\[)[^)]+\\].*\\+.*["\\\']<\\w+','confidence':85 ,'severity':'HIGH','cwe':'CWE-79','description':'User input from request parameters concatenated into HTML output - reflected XSS vulnerability'},{'pattern':'render_template_string\\s*\\([^)]*request\\.(?:args|form|json|data)','confidence':90 ,'severity':'HIGH','cwe':'CWE-79','description':'User input passed directly to render_template_string - SSTI/XSS vulnerability'},{'pattern':'make_response\\s*\\([^)]*["\\\']<[^"\\\']+[\\"\\\'][^)]*request\\.(?:args|form|json|data)','confidence':85 ,'severity':'HIGH','cwe':'CWE-79','description':'User input in HTML response construction - reflected XSS vulnerability'}],'COMMAND_INJECTION':[{'pattern':'subprocess\\.(?:getoutput|call|run|Popen)\\s*\\([^)]*request\\.(?:args|form|json|data|get_json)','confidence':95 ,'severity':'CRITICAL','cwe':'CWE-78','description':'User input passed directly to subprocess - command injection vulnerability'},{'pattern':'os\\.(?:system|popen)\\s*\\([^)]*request\\.(?:args|form|json|data|get_json)','confidence':95 ,'severity':'CRITICAL','cwe':'CWE-78','description':'User input passed directly to os.system/os.popen - command injection vulnerability'}]}
CONFIG_FILE_PATTERNS =['config\\.py$','settings\\.py$','local_settings\\.py$','production_settings\\.py$','constants\\.py$','secrets\\.py$','\\.env']

def apply_hard_detection_rules (filepath :str ,content :str ,language :str ='python')->List [Dict [str ,Any ]]:
    findings =[]
    lines =content .splitlines ()
    basename =os .path .basename (filepath ).lower ()
    is_config_file =any ((re .search (pattern ,filepath ,re .IGNORECASE )for pattern in CONFIG_FILE_PATTERNS ))
    for vuln_type ,patterns in HARD_DETECTION_PATTERNS .items ():
        for pattern_def in patterns :
            pattern =pattern_def ['pattern']
            confidence =pattern_def ['confidence']
            severity =pattern_def ['severity']
            cwe =pattern_def ['cwe']
            description =pattern_def ['description']
            exclusions =pattern_def .get ('exclusions',[])
            if vuln_type =='HARDCODED_SECRET'and (not is_config_file ):
                if 'config'not in filepath .lower ()and 'settings'not in filepath .lower ():
                    continue 
            for line_num ,line in enumerate (lines ,1 ):
                line_stripped =line .strip ()
                if line_stripped .startswith ('#')or line_stripped .startswith ('//'):
                    continue 
                if re .search (pattern ,line ,re .IGNORECASE ):
                    should_exclude =False 
                    for exclusion in exclusions :
                        if exclusion in line :
                            should_exclude =True 
                            break 
                    if should_exclude :
                        continue 
                    vulnerable_code =line .strip ()[:200 ]
                    finding ={'type':vuln_type ,'subtype':cwe ,'cwe_id':cwe ,'description':description ,'severity':severity ,'confidence_score':confidence ,'line':line_num ,'file':filepath ,'vulnerable_code':vulnerable_code ,'function_name':_extract_function_name (lines ,line_num ),'is_hard_rule_finding':True ,'_detection_rule':pattern_def }
                    findings .append (finding )
    return findings 

def _extract_function_name (lines :List [str ],line_num :int )->Optional [str ]:
    for i in range (line_num -1 ,-1 ,-1 ):
        if i >=len (lines ):
            continue 
        line =lines [i ]
        match =re .match ('^\\s*def\\s+(\\w+)\\s*\\(',line )
        if match :
            return match .group (1 )
        match =re .match ('^\\s*(?:function\\s+(\\w+)|(?:const|let|var)\\s+(\\w+)\\s*=\\s*(?:async\\s*)?\\()',line )
        if match :
            return match .group (1 )or match .group (2 )
    return None 
HARD_FALSE_POSITIVE_PATTERNS ={'MEMORY_SAFETY_NON_C':['(?i)(buffer.overflow|stack.overflow|heap.overflow)','(?i)(oob)\\s+(read|write|access)','(?i)(out.?of.?bounds?)','(?i)(memory.safety|memory.corruption)','(?i)(use.?after.?free|double.?free|null.?pointer.?dereference)','(?i)(segmentation.fault|segfault|memory.violation)','(?i)(bounds.check|boundary.check|array.bounds)','(?i)(integer.overflow|integer.underflow|integer.conversion)','(?i)arbitrary.?(memory.read|pointer.dereference|memory.address|memory.pointer)'],'PROVEN_HALLUCINATION':['(?i)(json\\.parse|response\\.json|JSON\\.parse).*insecure.deserialization','(?i)(setState|useState).*xss(?!.*dangerouslySetInnerHTML)']}
SOFT_FALSE_POSITIVE_PATTERNS ={'DOS':['(?i)(denial.of.service|dos\\.attack|resource.exhaustion|memory.exhaustion|cpu.exhaustion)','(?i)(rate.limit|rate.limiting|throttling)','(?i)(slowloris|infinite.loop|billion.laughs)','(?i)(exhaust|overwhelm|overload).*?(resource|memory|cpu)','(?i)(infinite|unbounded).*?(loop|recursion)'],'SECRETS_ON_DISK':['(?i)(secret|password|credential|token|api.key).*stored.*(?:file|disk|filesystem)'],'LOW_IMPACT':['(?i)(information.disclosure|information.leak).*version','(?i)(information.disclosure|information.leak).*path','(?i)(clickjacking|x.frame.options)','(?i)(verbose.error|error.disclosure)','(?i)(cors|cross.origin).*?misconfiguration'],'TEST_CODE':['(?i)(test.*file|spec.*file|__tests__|\\.test\\.|\\.spec\\.)','(?i)(mock|stub|fixture|test.data)','(?i)test.*\\.py$','(?i).*_test\\.py$','(?i).*\\.test\\.ts$','(?i).*\\.test\\.tsx$'],'REGEX_INJECTION':['(?i)(regex|regular.expression).*injection','(?i)(regex|regular.expression).*denial.of.service','(?i)(regex|regular.expression).*flooding','(?i)(redos|catastrophic.backtracking)'],'OPEN_REDIRECT':['(?i)(open.redirect|unvalidated.redirect)','(?i)(redirect.(attack|exploit|vulnerability))','(?i)(malicious.redirect)'],'LOG_SPOOFING':['(?i)(log.*injection|log.*spoofing|log.*forging)','(?i)(newline.*log|log.*newline|inject.*log)'],'SSRF_CLIENTSIDE':['(?i)(ssrf|server.?side.?request.?forgery)']}
HARDCODED_FALSE_POSITIVE_PATTERNS ={**HARD_FALSE_POSITIVE_PATTERNS ,**SOFT_FALSE_POSITIVE_PATTERNS }
FRONTEND_FALSE_POSITIVE_RULES =[{'name':'json_parse_not_deser','description_pattern':'(?i)(json\\.parse|response\\.json|JSON\\.parse)','vuln_code_pattern':'(?i)(JSON\\.parse|response\\.json\\(\\)|\\.json\\(\\))','type_match':'(?i)(insecure.deserialization|deserialization)','reason':'JSON.parse/response.json() is safe standard JSON parsing, not insecure deserialization (baseline precedent #1)'},{'name':'localstorage_not_deser','description_pattern':'(?i)(localStorage\\.(setItem|getItem)|sessionStorage)','vuln_code_pattern':'(?i)(localStorage\\.(setItem|getItem)|JSON\\.stringify.*localStorage)','type_match':'(?i)(insecure.deserialization|deserialization)','reason':'localStorage with JSON.stringify/parse is standard browser storage, not deserialization (baseline precedent #1)'},{'name':'hardcoded_localhost_url','description_pattern':'(?i)(localhost|127\\.0\\.0\\.1).*?(hardcoded|url|endpoint)','vuln_code_pattern':'(?i)(http://localhost|http://127\\.0\\.0\\.1)','type_match':'(?i)(hardcoded.secret|hardcoded.credential|secret)','reason':'Hardcoded localhost/dev URLs are not secrets (baseline precedent #2)'},{'name':'react_setstate_not_xss','description_pattern':'(?i)(set\\w+\\(.*?\\)|setState).*?(xss|cross.site)','vuln_code_pattern':'(?i)(set\\w+\\(data\\.|setError\\(|setQuery|setResult|setState)','type_match':'(?i)(xss|cross.site.scripting)','extra_check':'no_dangerous_html','reason':'React auto-escapes rendered values by default; setState is not XSS unless dangerouslySetInnerHTML is used (baseline precedent #6)'},{'name':'router_push_not_access_control','description_pattern':'(?i)(router\\.push|redirect|navigate).*?(access.control|unauthorized|without.*check)','vuln_code_pattern':'(?i)(router\\.push|router\\.replace|navigate\\(|redirect\\()','type_match':'(?i)(access.control|authorization|broken.access)','reason':'Client-side navigation after auth is normal pattern, not an access control vulnerability (baseline precedent #8)'},{'name':'window_open_not_crypto','description_pattern':'(?i)(window\\.open)','vuln_code_pattern':'(?i)(window\\.open)','type_match':'(?i)(insecure.crypto|weak.crypto|cryptograph)','reason':'window.open() is not related to cryptography'},{'name':'fetch_api_call_not_vuln','description_pattern':'(?i)(fetch|axios).*?(insecure|vulnerable)','vuln_code_pattern':'(?i)(await\\s+fetch\\(|axios\\.(get|post))','type_match':'(?i)(insecure.deserialization)','reason':'Making HTTP requests with fetch/axios is standard, not insecure deserialization'},{'name':'anonymous_fallback_not_access_control','description_pattern':'(?i)(anonymous|default.*value).*?(access|unauthorized)','vuln_code_pattern':'(?i)(\\|\\|\\s*[\'\\"]anonymous[\'\\"]|\\?\\?\\s*[\'\\"]anonymous[\'\\"])','type_match':'(?i)(access.control)','reason':'Fallback values for optional fields are not access control vulnerabilities on the client side (baseline precedent #8)'},{'name':'uuid_not_need_validation','description_pattern':'(?i)(uuid|guid).*?(validation|verify|check)','vuln_code_pattern':'(?i)(uuid|UUID|guid|GUID)','type_match':'(?i)(input.validation|missing.validation)','reason':'UUIDs can be assumed to be unguessable and do not need to be validated (baseline precedent #2)'},{'name':'env_var_trusted','description_pattern':'(?i)(environment.variable|env\\.var|process\\.env|os\\.environ)','vuln_code_pattern':'(?i)(process\\.env\\.|os\\.environ|os\\.getenv)','type_match':'(?i)(injection|tainted|untrusted)','reason':'Environment variables and CLI flags are trusted values in secure environments (baseline precedent #3)'},{'name':'react_xss_without_dangerous','description_pattern':'(?i)(xss|cross.site.scripting).*react','vuln_code_pattern':'(?i)(react|jsx|tsx)(?!.*dangerouslySetInnerHTML)(?!.*bypassSecurityTrustHtml)','type_match':'(?i)(xss|cross.site.scripting)','reason':'React and Angular are generally secure against XSS unless using dangerouslySetInnerHTML or similar bypass methods (baseline precedent #6)'},{'name':'clientside_auth_not_vuln','description_pattern':'(?i)(client.?side|frontend).*?(auth|authentication|permission)','vuln_code_pattern':'(?i)(localStorage.*role|sessionStorage.*role|client.*admin)','type_match':'(?i)(access.control|authentication|authorization)','reason':'A lack of permission checking in client-side code is not a vulnerability - backend must validate (baseline precedent #8)'},{'name':'non_pii_logging_not_vuln','description_pattern':'(?i)(logging|log).*?(data|info|input)','vuln_code_pattern':'(?i)(console\\.log|logger\\.|log\\.|print\\()','type_match':'(?i)(information.disclosure|data.exposure|sensitive.data)','reason':'Logging non-PII data is not a vulnerability. Only secrets, passwords, or PII in logs is a concern (baseline precedent #11)'},{'name':'client_fetch_not_ssrf','description_pattern':'(?i)(fetch|axios|xmlhttprequest|http.request).*?(ssrf|server.side.request)','vuln_code_pattern':'(?i)(fetch\\(|axios\\.(get|post|put|delete|patch)|XMLHttpRequest|\\.open\\()','type_match':'(?i)(ssrf|server.?side.?request.?forgery)','reason':'fetch()/axios/XMLHttpRequest in client-side code is a browser HTTP call, NOT SSRF. SSRF only applies to server-side HTTP requests.'},{'name':'nextjs_public_env_not_secret','description_pattern':'(?i)(next_public|NEXT_PUBLIC).*?(secret|exposed|leak)','vuln_code_pattern':'(?i)NEXT_PUBLIC_\\w+','type_match':'(?i)(hardcoded.secret|information.disclosure|sensitive.data)','reason':'NEXT_PUBLIC_ environment variables are intentionally exposed to the client in Next.js - this is by design, not a vulnerability.'},{'name':'react_usestate_not_xss','description_pattern':'(?i)(useState|useEffect|useMemo|useCallback).*?(xss|cross.site)','vuln_code_pattern':'(?i)(useState|useEffect|useMemo|useCallback|useRef)\\s*\\(','type_match':'(?i)(xss|cross.site.scripting)','reason':'React hooks (useState, useEffect, etc.) rendering data are NOT XSS. React auto-escapes output unless dangerouslySetInnerHTML is used.'},{'name':'map_filter_not_vuln','description_pattern':'(?i)(\\.map\\(|\\.filter\\(|\\.reduce\\().*?(injection|xss)','vuln_code_pattern':'(?i)\\.(map|filter|reduce|forEach)\\s*\\(','type_match':'(?i)(injection|xss|cross.site.scripting)','reason':'Array methods (.map, .filter, .reduce) are safe functional operations, not injection vectors in React/JSX.'}]
CRITICAL_VULNERABILITY_PATTERNS =['(?i)(remote.code.execution|rce|arbitrary.code.execution)','(?i)(sql.injection|sqli)','(?i)(command.injection|os.command)','(?i)(deserialization|unserialize|pickle\\.loads|yaml\\.load\\([^)]*Loader)','(?i)(authentication.bypass|privilege.escalation)','(?i)(ssrf|server.side.request.forgery)','(?i)(path.traversal|directory.traversal|lfi|local.file.inclusion)','(?i)(render_template_string|dangerouslySetInnerHTML)','(?i)(eval\\(|exec\\(|Function\\()','(?i)(subprocess.*shell\\s*=\\s*True|os\\.system|os\\.popen)','(?i)(hardcoded.*secret.*key|app\\.secret_key|SECRET_KEY.*=)','(?i)(jwt.*none.algorithm|algorithm.confusion)','(?i)(xxe|xml.external.entity)','(?i)(ssti|template.injection)','(?i)(nosql.injection|mongodb.injection)','(?i)(ldap.injection)','(?i)(xpath.injection)','(?i)(csv.injection|formula.injection)','(?i)(redos|regex.dos|catastrophic.backtracking)']
CRITICAL_CODE_PATTERNS =['cursor\\.execute\\(f[\\"\']','cursor\\.execute\\(.*?format\\(','cursor\\.execute\\(.*?\\+.*?\\+','cursor\\.execute\\(.*?%.*?%','pickle\\.loads?\\(','yaml\\.load\\([^)]*(?<!Safe)Loader','eval\\(','exec\\(','subprocess\\.\\w+\\(.*shell\\s*=\\s*True','render_template_string\\(','requests\\.(get|post|put|delete)\\([^)]*\\+','requests\\.(get|post|put|delete)\\([^)]*f[\\"\']','os\\.path\\.join\\(.*?\\+.*?\\+','\\.execute\\(\\s*query\\s*\\)','dangerouslySetInnerHTML\\s*=\\s*\\{','dangerouslySetInnerHTML.*__html','\\.innerHTML\\s*=','hashlib\\.md5\\(','hashlib\\.sha1\\(','app\\.secret_key\\s*=','SECRET_KEY\\s*=','jwt\\.decode\\([^)]*algorithms?\\s*=','ET\\.fromstring\\(','xml\\..*\\.parse\\(','Template\\([^)]*render','jinja2\\.Template\\(','db\\.\\w+\\.find\\([^)]*\\+','db\\.\\w+\\.find\\([^)]*f[\\"\']','\\.aggregate\\(\\[','ldap.*filter.*=.*f[\\"\']','\\.search\\([^)]*\\+','\\.search\\([^)]*%']
C_CPP_EXTENSIONS ={'.c','.cc','.cpp','.h','.hpp'}
HTML_EXTENSIONS ={'.html','.htm'}
FRONTEND_EXTENSIONS ={'.html','.htm','.tsx','.jsx','.ts','.js','.vue','.svelte'}

@dataclass 
class FilterResult :
    keep :bool 
    reason :str 
    category :str 
    confidence_adjustment :float 

class FindingsFilter :

    def __init__ (self ,use_hard_exclusions :bool =True ,use_llm_filtering :bool =False ,confidence_threshold :float =PHASE1_CONFIDENCE_THRESHOLD ):
        self .use_hard_exclusions =use_hard_exclusions 
        self .use_llm_filtering =use_llm_filtering 
        self .confidence_threshold =confidence_threshold 

    def filter_findings (self ,findings :List [Dict [str ,Any ]],context :Optional [Dict [str ,Any ]]=None )->Tuple [bool ,Dict [str ,Any ],Dict [str ,int ]]:
        if not findings :
            return (True ,{'filtered_findings':[],'excluded_findings':[]},{'total':0 ,'kept':0 })
        kept_findings =[]
        excluded_findings =[]
        if self .use_hard_exclusions :
            for finding in findings :
                result =self ._apply_hard_rules (finding )
                if result .keep :
                    kept_findings .append (finding )
                else :
                    excluded_findings .append ({**finding ,'_exclusion_reason':result .reason ,'_exclusion_category':result .category })
        else :
            kept_findings =findings 
        final_kept =[]
        for finding in kept_findings :
            confidence =self ._get_confidence_score (finding )
            if confidence >=self .confidence_threshold :
                finding ['_confidence_score']=confidence 
                final_kept .append (finding )
            else :
                excluded_findings .append ({**finding ,'_exclusion_reason':f'Confidence {confidence } below threshold {self .confidence_threshold }','_exclusion_category':'LOW_CONFIDENCE'})
        stats ={'total':len (findings ),'hard_excluded':len ([e for e in excluded_findings if e .get ('_exclusion_category')!='LOW_CONFIDENCE']),'confidence_filtered':len ([e for e in excluded_findings if e .get ('_exclusion_category')=='LOW_CONFIDENCE']),'kept':len (final_kept )}
        return (True ,{'filtered_findings':final_kept ,'excluded_findings':excluded_findings ,'analysis_summary':self ._generate_summary (final_kept ,excluded_findings )},stats )

    def _get_confidence_score (self ,finding :Dict [str ,Any ])->float :
        confidence =finding .get ('confidence_score',finding .get ('confidence',0 ))
        if isinstance (confidence ,(int ,float )):
            if 0 <confidence <=1.0 :
                return confidence *10 
            elif confidence >10 :
                return confidence /10 
            else :
                return float (confidence )
        return 10.0 

    def _apply_hard_rules (self ,finding :Dict [str ,Any ])->FilterResult :
        description =finding .get ('description','')
        finding_type =finding .get ('type','')
        finding_subtype =finding .get ('subtype','')
        severity =finding .get ('severity','').upper ()
        file_path =finding .get ('file','')
        vuln_code =finding .get ('vulnerable_code','')
        combined_text =f'{description } {finding_type } {finding_subtype }'
        file_ext =''
        if '.'in file_path :
            file_ext =f".{file_path .lower ().split ('.')[-1 ]}"
        for code_pattern in CRITICAL_CODE_PATTERNS :
            if re .search (code_pattern ,vuln_code ):
                return FilterResult (keep =True ,reason ='Critical code pattern detected in vulnerable_code',category ='CRITICAL_CODE_OVERRIDE',confidence_adjustment =0.0 )
        for critical_pattern in CRITICAL_VULNERABILITY_PATTERNS :
            if re .search (critical_pattern ,combined_text ):
                return FilterResult (keep =True ,reason ='Critical vulnerability pattern - bypasses all filters',category ='CRITICAL_OVERRIDE',confidence_adjustment =0.0 )
        if file_path .lower ().endswith ('.md'):
            return FilterResult (keep =False ,reason ='Finding in Markdown documentation file',category ='DOCUMENTATION_EXCLUSION',confidence_adjustment =0.0 )
        for fp_rule in FRONTEND_FALSE_POSITIVE_RULES :
            type_matches =re .search (fp_rule ['type_match'],finding_type )
            if not type_matches :
                continue 
            desc_matches =re .search (fp_rule ['description_pattern'],combined_text )if fp_rule .get ('description_pattern')else False 
            code_matches =re .search (fp_rule ['vuln_code_pattern'],vuln_code )if fp_rule .get ('vuln_code_pattern')else False 
            if desc_matches or code_matches :
                extra =fp_rule .get ('extra_check')
                if extra =='no_dangerous_html':
                    if 'dangerouslySetInnerHTML'in vuln_code or 'dangerouslySetInnerHTML'in description :
                        continue 
                    if '__html'in vuln_code :
                        continue 
                return FilterResult (keep =False ,reason =fp_rule ['reason'],category =f"FP_FILTER_{fp_rule ['name'].upper ()}",confidence_adjustment =-0.5 )
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS ['DOS']:
            if re .search (pattern ,combined_text ):
                return FilterResult (keep =False ,reason ='DoS/rate limiting/resource exhaustion excluded by baseline policy',category ='DOS_EXCLUSION',confidence_adjustment =-0.3 )
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS ['REGEX_INJECTION']:
            if re .search (pattern ,combined_text ):
                if re .search ('(?i)(redos|catastrophic\\.backtracking|user.?controlled\\.?pattern)',combined_text ):
                    break 
                return FilterResult (keep =False ,reason ='Regex injection (non-ReDoS) excluded by policy',category ='REGEX_INJECTION_EXCLUSION',confidence_adjustment =-0.3 )
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS ['OPEN_REDIRECT']:
            if re .search (pattern ,combined_text ):
                confidence =self ._get_confidence_score (finding )
                if severity =='LOW'and confidence <7.0 :
                    return FilterResult (keep =False ,reason ='Open redirect (low impact, low confidence) excluded',category ='OPEN_REDIRECT_EXCLUSION',confidence_adjustment =-0.2 )
                break 
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS ['LOG_SPOOFING']:
            if re .search (pattern ,combined_text ):
                return FilterResult (keep =False ,reason ='Log spoofing/injection excluded by baseline policy',category ='LOG_SPOOFING_EXCLUSION',confidence_adjustment =-0.2 )
        if file_ext not in C_CPP_EXTENSIONS :
            for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS ['MEMORY_SAFETY_NON_C']:
                if re .search (pattern ,combined_text ):
                    return FilterResult (keep =False ,reason =f'Memory safety finding in {file_ext } file (not C/C++ - impossible)',category ='MEMORY_SAFETY_NON_C',confidence_adjustment =-0.3 )
        if file_ext in FRONTEND_EXTENSIONS :
            for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS ['SSRF_CLIENTSIDE']:
                if re .search (pattern ,combined_text ):
                    return FilterResult (keep =False ,reason =f'SSRF finding in frontend {file_ext } file (client-side HTTP calls are not SSRF)',category ='SSRF_CLIENTSIDE_EXCLUSION',confidence_adjustment =-0.3 )
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS ['SECRETS_ON_DISK']:
            if re .search (pattern ,combined_text ):
                return FilterResult (keep =False ,reason ='Secrets on disk handled by separate scanner',category ='SECRETS_EXCLUSION',confidence_adjustment =-0.2 )
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS ['TEST_CODE']:
            if re .search (pattern ,file_path ):
                return FilterResult (keep =False ,reason ='Finding in test file',category ='TEST_FILE_EXCLUSION',confidence_adjustment =0.0 )
        for pattern in HARDCODED_FALSE_POSITIVE_PATTERNS ['LOW_IMPACT']:
            if re .search (pattern ,combined_text ):
                confidence =self ._get_confidence_score (finding )
                if confidence <7.0 :
                    return FilterResult (keep =False ,reason ='Low-impact informational finding with insufficient confidence',category ='LOW_IMPACT_EXCLUSION',confidence_adjustment =-0.1 )
        return FilterResult (keep =True ,reason ='Passed hard exclusion rules',category ='PASSED',confidence_adjustment =0.0 )

    def _generate_summary (self ,kept :List [Dict [str ,Any ]],excluded :List [Dict [str ,Any ]])->Dict [str ,Any ]:
        category_counts ={}
        for f in excluded :
            cat =f .get ('_exclusion_category','UNKNOWN')
            category_counts [cat ]=category_counts .get (cat ,0 )+1 
        severity_breakdown ={'HIGH':0 ,'MEDIUM':0 ,'LOW':0 ,'CRITICAL':0 }
        confidence_distribution ={'high (8-10)':0 ,'medium (5-7)':0 ,'low (<5)':0 }
        for f in kept :
            sev =f .get ('severity','MEDIUM').upper ()
            severity_breakdown [sev ]=severity_breakdown .get (sev ,0 )+1 
            conf =f .get ('_confidence_score',10 )
            if conf >=8 :
                confidence_distribution ['high (8-10)']+=1 
            elif conf >=5 :
                confidence_distribution ['medium (5-7)']+=1 
            else :
                confidence_distribution ['low (<5)']+=1 
        total =len (kept )+len (excluded )
        return {'total_findings':total ,'excluded_count':len (excluded ),'kept_count':len (kept ),'reduction_percentage':round (len (excluded )/max (1 ,total )*100 ,1 ),'exclusion_breakdown':category_counts ,'severity_breakdown':severity_breakdown ,'confidence_distribution':confidence_distribution ,'confidence_threshold':self .confidence_threshold }

def apply_filtering_to_results (findings :List [Dict [str ,Any ]],scan_type :str ,confidence_threshold :float =PHASE1_CONFIDENCE_THRESHOLD )->Tuple [List [Dict [str ,Any ]],Dict [str ,Any ]]:
    filter_instance =FindingsFilter (use_hard_exclusions =True ,confidence_threshold =confidence_threshold )
    success ,results ,stats =filter_instance .filter_findings (findings )
    if success :
        return (results ['filtered_findings'],results ['analysis_summary'])
    else :
        return (findings ,{'error':'Filtering failed','kept_count':len (findings )})
