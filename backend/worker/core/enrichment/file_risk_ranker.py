import os 
import re 
from typing import Dict ,List ,Optional 

class FileRiskRanker :
    FRONTEND_HIGH_RISK_SIGNALS ={'patterns':['dangerouslySetInnerHTML','innerHTML','document.write','eval(','localStorage.setItem','sessionStorage.setItem','window.location','router.push','router.replace','searchParams.get','query.'],'filenames':['login','auth','redirect','oauth','comment','task','user','profile','analytics','tracking','config']}
    RISK_SIGNALS =[('filename','(auth|login|register|password|token|session)',0.3 ,'auth'),('filename','(upload|file|download|export|import)',0.25 ,'file_handling'),('filename','(admin|dashboard|api|route|handler|view|controller)',0.25 ,'api'),('filename','(query|db|database|model|repository|dao)',0.2 ,'database'),('filename','(exec|command|shell|process|subprocess)',0.3 ,'command'),('filename','(user\\.py|auth\\.py|account\\.py|identity\\.py)',0.35 ,'user_model'),('filepath','models[/\\\\].*\\.py$',0.25 ,'models_directory'),('filename','(config\\.py|settings\\.py|constants\\.py|secrets\\.py)',0.3 ,'config_file'),('content','(SECRET_KEY|API_KEY|PASSWORD|TOKEN)\\s*=\\s*[\\"\'][^\\"\']+',0.4 ,'hardcoded_secret'),('content','eval\\s*\\(',0.3 ,'eval'),('content','exec\\s*\\(',0.3 ,'exec'),('content','pickle\\.loads?\\s*\\(',0.3 ,'pickle'),('content','yaml\\.load\\s*\\([^)]*\\)(?!.*SafeLoader)',0.3 ,'yaml_unsafe'),('content','deserializ',0.3 ,'deserialize'),('content','(SELECT|INSERT|UPDATE|DELETE)\\s+.*%\\s*\\(|\\+.*\\+|\\.format\\(|f[\\"\'].*SELECT',0.35 ,'sql_construction'),('content','(request\\.args|request\\.form|request\\.json).*\\+.*<\\w+|render_template_string',0.35 ,'xss_html_output'),('content','request\\.(form|args|json|cookies|headers)\\b',0.25 ,'user_input_source'),('content','render_template\\s*\\(',0.2 ,'template_render'),('content','params\\.|req\\.body|req\\.query\\b',0.25 ,'web_request_source'),('content','(subprocess\\.(getoutput|call|run)|os\\.(system|popen))\\s*\\(',0.35 ,'command_injection_sink'),('filename','(test_|_test|spec_|_spec|\\.test\\.|\\.spec\\.)',-0.4 ,'test_file'),('filename','(migration|seed|fixture|mock|factory)',-0.2 ,'migration')]

    def __init__ (self ):
        pass 
    CODE_EXTENSIONS ={'.py','.js','.jsx','.ts','.tsx','.java','.go','.php','.rb','.vue','.svelte','.html','.htm'}
    CONFIG_EXTENSIONS ={'.json','.yaml','.yml','.toml','.env','.ini','.cfg'}

    def _detect_language (self ,filepath :str )->Optional [str ]:
        ext =os .path .splitext (filepath )[1 ].lower ()
        language_map ={'.py':'python','.js':'javascript','.jsx':'javascript','.ts':'typescript','.tsx':'typescript','.java':'java','.go':'go'}
        return language_map .get (ext )

    def rank_one (self ,filepath :str ,content :str )->Dict :
        score =0.0 
        reasons =[]
        ext =os .path .splitext (filepath )[1 ].lower ()
        if ext in self .CODE_EXTENSIONS :
            score =0.08 
            reasons .append ('code_file')
        elif ext in self .CONFIG_EXTENSIONS :
            score =0.04 
            reasons .append ('config_file')
        basename =os .path .basename (filepath ).lower ()
        filepath_lower =filepath .lower ()
        for signal_type ,pattern ,adjustment ,reason_code in self .RISK_SIGNALS :
            if signal_type =='filename':
                if re .search (pattern ,basename ,re .IGNORECASE ):
                    score +=adjustment 
                    reasons .append (reason_code )
            elif signal_type =='filepath':
                if re .search (pattern ,filepath_lower ,re .IGNORECASE ):
                    score +=adjustment 
                    reasons .append (reason_code )
            elif signal_type =='content':
                if re .search (pattern ,content ,re .IGNORECASE ):
                    score +=adjustment 
                    reasons .append (reason_code )
        ext =os .path .splitext (filepath )[1 ].lower ()
        if ext in {'.jsx','.tsx','.js','.ts','.vue','.svelte','.html'}:
            for pat in self .FRONTEND_HIGH_RISK_SIGNALS ['patterns']:
                if pat in content :
                    score +=0.25 
                    reasons .append ('frontend_risk_pattern')
                    break 
            for name_part in self .FRONTEND_HIGH_RISK_SIGNALS ['filenames']:
                if name_part in basename :
                    score +=0.2 
                    reasons .append ('frontend_risk_filename')
                    break 
        score =max (0.0 ,min (1.0 ,score ))
        if score >0.7 :
            recommended_tier =3 
        elif score >0.4 :
            recommended_tier =2 
        else :
            recommended_tier =1 
        skip =score <0.05 
        return {'filepath':filepath ,'risk_score':round (score ,2 ),'recommended_tier':recommended_tier ,'skip':skip ,'risk_reasons':reasons ,'language':self ._detect_language (filepath )}

    def rank (self ,file_list :List [str ],project_path :str )->List [Dict ]:
        rankings =[]
        for filepath in file_list :
            full_path =os .path .join (project_path ,filepath )
            try :
                with open (full_path ,'r',encoding ='utf-8',errors ='ignore')as f :
                    content =f .read ()
            except Exception :
                rankings .append ({'filepath':filepath ,'risk_score':0.3 ,'recommended_tier':2 ,'skip':False ,'risk_reasons':['read_error'],'language':None })
                continue 
            ranking =self .rank_one (filepath ,content )
            rankings .append (ranking )
        rankings .sort (key =lambda x :x ['risk_score'],reverse =True )
        return rankings 
