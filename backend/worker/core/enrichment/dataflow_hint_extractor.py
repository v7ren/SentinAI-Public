import os 
import re 
from typing import Dict ,List ,Optional ,Tuple 
from ..config import logger 

class DataflowHintExtractor :
    SECRET_VAR_PATTERNS =['SECRET_KEY','SECRET','API_KEY','APIKEY','API_SECRET','PASSWORD','PASSWD','PASS','TOKEN','AUTH_TOKEN','ACCESS_TOKEN','REFRESH_TOKEN','PRIVATE_KEY','PRIVATEKEY','ADMIN_KEY','SERVICE_TOKEN','INTERNAL_TOKEN','DB_PASSWORD','DATABASE_PASSWORD','REDIS_PASSWORD','CONN_STRING','CONNECTION_STRING']
    SECRET_VAR_REGEX =re .compile ('^\\s*(\\w*(?:'+'|'.join (SECRET_VAR_PATTERNS )+')\\w*)\\s*=\\s*([\\"\'])(.+?)\\2',re .IGNORECASE |re .MULTILINE )
    CONFIG_FILE_PATTERNS =['config\\.py','settings\\.py','constants\\.py','config\\.js','config\\.ts','\\.env\\.','local_settings','production_settings','secrets\\.','credentials']
    CONFIG_FILE_REGEX =re .compile ('|'.join (CONFIG_FILE_PATTERNS ),re .IGNORECASE )
    TAINT_PATTERNS ={'python':{'request.args':re .compile ('request\\.args(?:\\.get|\\[)'),'request.form':re .compile ('request\\.form(?:\\.get|\\[)'),'request.json':re .compile ('request\\.json'),'request.data':re .compile ('request\\.data'),'request.files':re .compile ('request\\.files'),'request.headers':re .compile ('request\\.headers'),'request.cookies':re .compile ('request\\.cookies'),'request.stream':re .compile ('request\\.stream'),'os.environ':re .compile ('os\\.environ'),'sys.argv':re .compile ('sys\\.argv'),'input()':re .compile ('\\binput\\s*\\(\\s*\\)'),'argparse':re .compile ('args\\.\\w+'),'click.argument':re .compile ('@click\\.(argument|option)'),'socket.recv':re .compile ('\\.recv\\s*\\('),'file.read':re .compile ('\\.read\\s*\\(')},'javascript':{'req.body':re .compile ('req\\.body'),'req.query':re .compile ('req\\.query'),'req.params':re .compile ('req\\.params'),'req.headers':re .compile ('req\\.headers'),'req.cookies':re .compile ('req\\.cookies'),'req.files':re .compile ('req\\.files'),'process.env':re .compile ('process\\.env'),'event.data':re .compile ('event\\.data'),'window.prompt':re .compile ('window\\.prompt|prompt\\s*\\('),'document.location':re .compile ('document\\.location|window\\.location'),'URLSearchParams':re .compile ('URLSearchParams'),'FormData':re .compile ('FormData')},'typescript':{'req.body':re .compile ('req\\.body'),'req.query':re .compile ('req\\.query'),'req.params':re .compile ('req\\.params'),'req.headers':re .compile ('req\\.headers'),'req.cookies':re .compile ('req\\.cookies'),'req.files':re .compile ('req\\.files'),'process.env':re .compile ('process\\.env'),'event.data':re .compile ('event\\.data'),'window.prompt':re .compile ('window\\.prompt|prompt\\s*\\('),'document.location':re .compile ('document\\.location|window\\.location'),'URLSearchParams':re .compile ('URLSearchParams'),'FormData':re .compile ('FormData')},'java':{'request.getParameter':re .compile ('request\\.getParameter'),'request.getHeader':re .compile ('request\\.getHeader'),'System.getenv':re .compile ('System\\.getenv'),'args[]':re .compile ('\\bargs\\['),'Scanner':re .compile ('Scanner\\s*\\(\\s*System\\.in\\s*\\)'),'BufferedReader':re .compile ('BufferedReader.*System\\.in'),'ServletInputStream':re .compile ('ServletInputStream'),'MultipartFile':re .compile ('MultipartFile')},'go':{'r.URL.Query':re .compile ('r\\.URL\\.Query\\s*\\(\\s*\\)'),'r.FormValue':re .compile ('r\\.FormValue\\s*\\('),'r.PostFormValue':re .compile ('r\\.PostFormValue\\s*\\('),'r.Header.Get':re .compile ('r\\.Header\\.Get\\s*\\('),'r.Header.Values':re .compile ('r\\.Header\\.Values\\s*\\('),'os.Getenv':re .compile ('os\\.Getenv\\s*\\('),'os.Args':re .compile ('os\\.Args'),'bufio.Scanner':re .compile ('bufio\\.NewScanner'),'flag.String':re .compile ('flag\\.\\w+\\s*\\(')}}
    VAR_ASSIGNMENT_PATTERNS ={'python':re .compile ('(\\w+)\\s*=\\s*(.+)',re .MULTILINE ),'javascript':re .compile ('(?:const|let|var)?\\s*(\\w+)\\s*=\\s*(.+)',re .MULTILINE ),'typescript':re .compile ('(?:const|let|var)?\\s*(\\w+)\\s*=\\s*(.+)',re .MULTILINE ),'java':re .compile ('(?:\\w+(?:<[^>]+>)?)\\s+(\\w+)\\s*=\\s*(.+);',re .MULTILINE ),'go':re .compile ('(\\w+)\\s*(:?)=\\s*(.+)',re .MULTILINE )}
    DANGEROUS_SINKS ={'python':{'html_concat':re .compile ('([\\"\']<\\w+[^\\"\']*>[\\"\']\\s*\\+|f[\\"\'][^\\"\']*<\\w+|\\+\\s*[\\"\'][^\\"\']*<\\w+)'),'render_template_string':re .compile ('render_template_string\\s*\\('),'make_response_html':re .compile ('make_response\\s*\\([^)]*\\)\\s*,\\s*\\d+\\s*,\\s*\\{[^}]*text/html'),'html_string_concat':re .compile ('[\\"\']<!DOCTYPE\\s+html|<html|<body|<div|<script|<p[^>]*>[\\"\']'),'subprocess_shell':re .compile ('subprocess\\.(?:getoutput|call|run|Popen|check_output)\\s*\\(|os\\.(?:system|popen)'),'sql_string_formatting':re .compile ('(?:execute|query|raw)\\s*\\(\\s*(?:f["\\\']|["\\\'][^"\\\']*%s|["\\\'][^"\\\']*\\{)',re .IGNORECASE ),'eval_exec':re .compile ('\\b(?:eval|exec)\\s*\\('),'pickle_loads':re .compile ('pickle\\.loads?\\s*\\('),'yaml_load':re .compile ('yaml\\.load\\s*\\(')},'javascript':{'exec_shell':re .compile ('(?:child_process\\.(?:exec|execSync|spawn)|require\\s*\\(\\s*[\\"\']child_process[\\"\']\\s*\\)\\.exec)\\s*\\('),'eval':re .compile ('\\beval\\s*\\('),'innerHTML':re .compile ('\\.innerHTML\\s*='),'document_write':re .compile ('document\\.write\\s*\\('),'dangerouslySetInnerHTML':re .compile ('dangerouslySetInnerHTML\\s*=\\s*\\{\\s*__html'),'window_location':re .compile ('window\\.location(?:\\.href)?\\s*='),'router_push_replace':re .compile ('router\\.(?:push|replace)\\s*\\(')},'typescript':{'exec_shell':re .compile ('(?:child_process\\.(?:exec|execSync|spawn)|require\\s*\\(\\s*[\\"\']child_process[\\"\']\\s*\\)\\.exec)\\s*\\('),'eval':re .compile ('\\beval\\s*\\('),'innerHTML':re .compile ('\\.innerHTML\\s*='),'document_write':re .compile ('document\\.write\\s*\\('),'dangerouslySetInnerHTML':re .compile ('dangerouslySetInnerHTML\\s*=\\s*\\{\\s*__html'),'window_location':re .compile ('window\\.location(?:\\.href)?\\s*='),'router_push_replace':re .compile ('router\\.(?:push|replace)\\s*\\(')}}
    HTML_OUTPUT_INDICATORS =['<!DOCTYPE\\s+html','<html','<body','<div','<p>','<script','<head','<title','Content-Type.*text/html']
    HTML_OUTPUT_REGEX =re .compile ('|'.join (HTML_OUTPUT_INDICATORS ),re .IGNORECASE )
    DANGEROUS_SINK_FUNCTIONS ={'subprocess.getoutput','subprocess.call','subprocess.run','subprocess.Popen','subprocess.check_output','os.system','os.popen','os.execv','commands.getoutput','eval','exec','pickle.loads','yaml.load','render_template_string','execute','raw'}

    def _detect_language (self ,filepath :str )->Optional [str ]:
        ext =os .path .splitext (filepath )[1 ].lower ()
        language_map ={'.py':'python','.js':'javascript','.jsx':'javascript','.ts':'typescript','.tsx':'typescript','.java':'java','.go':'go'}
        return language_map .get (ext )

    def _extract_variable_from_line (self ,line :str ,language :str )->Optional [str ]:
        pattern =self .VAR_ASSIGNMENT_PATTERNS .get (language )
        if not pattern :
            return None 
        match =pattern .match (line .strip ())
        if match :
            return match .group (1 )
        return None 

    def _extract_secrets (self ,filepath :str ,content :str ,language :str ,scan_id :Optional [str ]=None )->List [Dict ]:
        secrets =[]
        is_config_file =self .CONFIG_FILE_REGEX .search (filepath )is not None 
        is_python_config =language =='python'and ('config'in filepath .lower ()or 'settings'in filepath .lower ()or 'constants'in filepath .lower ())
        if not (is_config_file or is_python_config ):
            return secrets 
        lines =content .splitlines ()
        for line_num ,line in enumerate (lines ,1 ):
            line_stripped =line .strip ()
            if language =='python'and line_stripped .startswith ('#'):
                continue 
            for pattern in self .SECRET_VAR_PATTERNS :
                safe_pat =re .escape (pattern )
                try :
                    regex =re .compile (f"""^\\s*(\\w*{safe_pat }\\w*)\\s*=\\s*([\\"'])(.+?)\\2""",re .IGNORECASE )
                except re .error as e :
                    logger .warning (f'[ENRICHMENT] Bad regex pattern while scanning secrets. scan_id={scan_id !r } file={filepath !r } pattern={pattern !r } error={e }')
                    continue 
                match =regex .search (line )
                if match :
                    var_name =match .group (1 )
                    secret_value =match .group (3 )
                    if any ((skip in secret_value for skip in ['os.environ','getenv','os.get','config(','settings(','request.','self.','args['])):
                        continue 
                    if any ((placeholder in secret_value .lower ()for placeholder in ['your_','placeholder','<','>','{{','}}','change_','replace_','todo','fixme'])):
                        continue 
                    secrets .append ({'variable':var_name ,'line':line_num ,'line_content':line .strip ()[:100 ],'secret_type':self ._classify_secret_type (var_name )})
                    break 
        return secrets 

    def _classify_secret_type (self ,var_name :str )->str :
        name_upper =var_name .upper ()
        if 'SECRET_KEY'in name_upper :
            return 'SECRET_KEY'
        elif 'API_KEY'in name_upper or 'APIKEY'in name_upper :
            return 'API_KEY'
        elif 'TOKEN'in name_upper :
            return 'TOKEN'
        elif 'PASSWORD'in name_upper or 'PASSWD'in name_upper :
            return 'PASSWORD'
        elif 'PRIVATE_KEY'in name_upper :
            return 'PRIVATE_KEY'
        else :
            return 'GENERIC_SECRET'

    def _extract_sink_argument (self ,line :str ,sink_name :str ,language :str )->Optional [str ]:
        if language =='python':
            if sink_name =='subprocess_shell':
                m =re .search ('(?:subprocess\\.\\w+|os\\.(?:system|popen))\\s*\\(\\s*([^),]+)',line )
                return m .group (1 ).strip ().split ('.')[-1 ]if m else None 
            if sink_name =='eval_exec':
                m =re .search ('\\b(?:eval|exec)\\s*\\(\\s*([^),]+)',line )
                return m .group (1 ).strip ().split ('.')[-1 ]if m else None 
            if sink_name in ('pickle_loads','yaml_load'):
                m =re .search ('(?:pickle\\.loads?|yaml\\.load)\\s*\\(\\s*([^),]+)',line )
                return m .group (1 ).strip ().split ('.')[-1 ]if m else None 
        if language in ('javascript','typescript'):
            if sink_name =='exec_shell':
                m =re .search ('(?:exec|execSync|spawn)\\s*\\(\\s*([^),]+)',line )
                return m .group (1 ).strip ().split ('.')[-1 ]if m else None 
            if sink_name =='eval':
                m =re .search ('eval\\s*\\(\\s*([^)]+)\\)',line )
                return m .group (1 ).strip ().split ('.')[-1 ]if m else None 
            if sink_name in ('innerHTML','document_write','dangerouslySetInnerHTML'):
                m =re .search ('(?:innerHTML|__html)\\s*[=:]\\s*([^;}\\s]+)',line )or re .search ('document\\.write\\s*\\(\\s*([^)]+)\\)',line )
                return m .group (1 ).strip ().split ('.')[-1 ]if m else None 
            if sink_name in ('window_location','router_push_replace'):
                m =re .search ('(?:location\\.href|location)\\s*=\\s*([^;]+)',line )or re .search ('router\\.(?:push|replace)\\s*\\(\\s*([^),]+)',line )
                return m .group (1 ).strip ().split ('.')[-1 ]if m else None 
        return None 

    def _sink_type_for_sink_name (self ,sink_name :str ,language :str )->Optional [str ]:
        if language =='python':
            if sink_name in ['html_concat','render_template_string','make_response_html']:
                return 'XSS_HTML_OUTPUT'
            if sink_name =='subprocess_shell':
                return 'COMMAND_INJECTION'
            if sink_name =='sql_string_formatting':
                return 'SQL_INJECTION'
            if sink_name in ['eval_exec','pickle_loads','yaml_load']:
                return 'CODE_INJECTION'
        if language in ('javascript','typescript'):
            if sink_name =='exec_shell':
                return 'COMMAND_INJECTION'
            if sink_name =='eval':
                return 'CODE_INJECTION'
            if sink_name in ['innerHTML','document_write','dangerouslySetInnerHTML']:
                return 'XSS_HTML_OUTPUT'
            if sink_name in ['window_location','router_push_replace']:
                return 'OPEN_REDIRECT'
        return None 

    def _extract_taint_flows_to_sinks (self ,filepath :str ,content :str ,language :str ,tainted_variables :List [Dict ])->List [Dict ]:
        taint_flows =[]
        tainted_var_names ={v ['variable']for v in tainted_variables }
        tainted_by_var ={v ['variable']:v .get ('source','unknown')for v in tainted_variables }
        lines =content .splitlines ()
        sink_patterns =self .DANGEROUS_SINKS .get (language ,{})
        for line_num ,line in enumerate (lines ,1 ):
            line_stripped =line .strip ()
            if language =='python'and line_stripped .startswith ('#'):
                continue 
            if language in ('javascript','typescript')and (line_stripped .startswith ('//')or line_stripped .startswith ('*')):
                continue 
            for sink_name ,pattern in sink_patterns .items ():
                if not pattern .search (line ):
                    continue 
                sink_type =self ._sink_type_for_sink_name (sink_name ,language )
                if not sink_type :
                    continue 
                if language =='python'and sink_type =='XSS_HTML_OUTPUT':
                    if not self .HTML_OUTPUT_REGEX .search (line ):
                        continue 
                input_var =self ._extract_sink_argument (line ,sink_name ,language )
                found_tainted =False 
                for var_name in tainted_var_names :
                    if var_name in line :
                        found_tainted =True 
                        param_source ={'traced_to':None ,'original_source':tainted_by_var .get (var_name ),'sanitized':False ,'confidence':'high'}
                        taint_flows .append ({'source_variable':var_name ,'sink_type':sink_type ,'sink_name':sink_name ,'line':line_num ,'line_content':line .strip ()[:150 ],'severity':'HIGH','parameter_source':param_source })
                if not found_tainted and input_var and input_var .isidentifier ():
                    param_source ={'traced_to':None ,'original_source':None ,'sanitized':False ,'confidence':'unknown'}
                    taint_flows .append ({'source_variable':input_var ,'sink_type':sink_type ,'sink_name':sink_name ,'line':line_num ,'line_content':line .strip ()[:150 ],'severity':'HIGH','parameter_source':param_source })
        return taint_flows 

    def _detect_cross_file_taint (self ,filepath :str ,content :str ,language :str ,tainted_variables :List [Dict ])->List [Dict ]:
        cross_file_taints =[]
        if not tainted_variables or language !='python':
            return cross_file_taints 
        tainted_var_names ={v ['variable']for v in tainted_variables }
        lines =content .splitlines ()
        func_call_pattern =re .compile ('(\\w+)\\s*\\(([^)]*)\\)')
        for line_num ,line in enumerate (lines ,1 ):
            line_stripped =line .strip ()
            if line_stripped .startswith ('#')or line_stripped .startswith ('def '):
                continue 
            for match in func_call_pattern .finditer (line ):
                func_name =match .group (1 )
                args_str =match .group (2 )
                tainted_args =[]
                for var_name in tainted_var_names :
                    if var_name in args_str :
                        tainted_args .append (var_name )
                if tainted_args :
                    cross_file_taints .append ({'caller_function':None ,'called_function':func_name ,'tainted_args':tainted_args ,'line':line_num ,'line_content':line .strip ()[:100 ]})
        return cross_file_taints 

    def extract (self ,filepath :str ,content :str ,language :Optional [str ]=None ,scan_id :Optional [str ]=None )->Dict :
        if language is None :
            language =self ._detect_language (filepath )
        if not language or language not in self .TAINT_PATTERNS :
            secrets =self ._extract_secrets (filepath ,content ,language or 'python',scan_id =scan_id )
            return {'tainted_variables':[],'has_user_input':False ,'entry_points':[],'secrets':secrets ,'has_secrets':len (secrets )>0 ,'taint_flows':[],'cross_file_taints':[]}
        patterns =self .TAINT_PATTERNS [language ]
        tainted_variables =[]
        lines =content .splitlines ()
        for line_num ,line in enumerate (lines ,1 ):
            line_stripped =line .strip ()
            if language =='python'and line_stripped .startswith ('#'):
                continue 
            if language in ('javascript','typescript','java','go'):
                if line_stripped .startswith ('//')or line_stripped .startswith ('*'):
                    continue 
            for source_name ,pattern in patterns .items ():
                if pattern .search (line ):
                    var_name =self ._extract_variable_from_line (line ,language )
                    if var_name :
                        tainted_variables .append ({'variable':var_name ,'source':source_name ,'line':line_num ,'line_content':line .strip ()})
        has_user_input =len (tainted_variables )>0 
        entry_points =[]
        for var in tainted_variables :
            line_idx =var ['line']-1 
            for i in range (line_idx ,-1 ,-1 ):
                line =lines [i ]if i <len (lines )else ''
                if language =='python'and line .strip ().startswith ('def '):
                    func_match =re .match ('def\\s+(\\w+)',line )
                    if func_match :
                        entry_points .append (func_match .group (1 ))
                        break 
                elif language in ('javascript','typescript'):
                    if re .match ('(?:function\\s+(\\w+)|\\s*(\\w+)\\s*[=:]\\s*(?:async\\s*)?\\()',line ):
                        func_match =re .search ('(?:function\\s+(\\w+)|(\\w+)\\s*[=:])',line )
                        if func_match :
                            entry_points .append (func_match .group (1 )or func_match .group (2 ))
                            break 
        secrets =self ._extract_secrets (filepath ,content ,language ,scan_id =scan_id )
        taint_flows =self ._extract_taint_flows_to_sinks (filepath ,content ,language ,tainted_variables )
        cross_file_taints =self ._detect_cross_file_taint (filepath ,content ,language ,tainted_variables )
        return {'tainted_variables':tainted_variables ,'has_user_input':has_user_input ,'entry_points':list (set (entry_points )),'secrets':secrets ,'has_secrets':len (secrets )>0 ,'taint_flows':taint_flows ,'has_taint_flows':len (taint_flows )>0 ,'cross_file_taints':cross_file_taints ,'has_cross_file_taints':len (cross_file_taints )>0 }
