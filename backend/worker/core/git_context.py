import logging 
import subprocess 
from dataclasses import dataclass ,field 
from pathlib import Path 
from typing import Any 
logger =logging .getLogger (__name__ )
SECURITY_KEYWORDS =frozenset ({'fix','security','auth','sql','injection','xss','cve','vuln','patch'})

@dataclass 
class GitContext :
    high_churn_files :list [str ]=field (default_factory =list )
    recently_changed_files :list [str ]=field (default_factory =list )
    security_relevant_commits :list [str ]=field (default_factory =list )
    author_concentration :dict [str ,int ]=field (default_factory =dict )
    repo_path :str =''

def _run_git (repo_path :str ,*args :str )->str :
    try :
        r =subprocess .run (['git','-C',repo_path ,*args ],capture_output =True ,text =True ,timeout =30 ,cwd =repo_path or None )
        if r .returncode !=0 :
            return ''
        return (r .stdout or '').strip ()
    except (FileNotFoundError ,subprocess .TimeoutExpired ,Exception )as e :
        logger .debug ('git command failed: %s',e )
        return ''

def get_git_context (repo_path :str ,churn_days :int =90 ,churn_threshold :int =10 ,recent_days :int =30 )->GitContext :
    ctx =GitContext (repo_path =repo_path )
    if not repo_path or not Path (repo_path ).exists ():
        return ctx 
    try :
        out =_run_git (repo_path ,'log',f'--since={recent_days } days ago','--name-only','--pretty=format:')
        if out :
            ctx .recently_changed_files =sorted (set ((line .strip ()for line in out .splitlines ()if line .strip ())))
        out =_run_git (repo_path ,'log',f'--since={churn_days } days ago','--name-only','--pretty=format:.')
        if out :
            counts :dict [str ,int ]={}
            for line in out .splitlines ():
                line =line .strip ()
                if line and line !='.':
                    counts [line ]=counts .get (line ,0 )+1 
            ctx .high_churn_files =[f for f ,c in counts .items ()if c >=churn_threshold ]
        for kw in SECURITY_KEYWORDS :
            out =_run_git (repo_path ,'log','-E','--grep='+kw ,'--pretty=format:%H','-n','50')
            if out :
                ctx .security_relevant_commits .extend (out .splitlines ())
        ctx .security_relevant_commits =list (dict .fromkeys (ctx .security_relevant_commits ))[:100 ]
        out =_run_git (repo_path ,'shortlog','-sn','--all','--no-merges','--')
        if out :
            for line in out .splitlines ()[:500 ]:
                parts =line .strip ().split ('\t',1 )
                if len (parts )==2 :
                    try :
                        n =int (parts [0 ].strip ())
                        f =parts [1 ].strip ()
                        if f :
                            ctx .author_concentration [f ]=ctx .author_concentration .get (f ,0 )+n 
                    except ValueError :
                        pass 
    except Exception as e :
        logger .warning ('get_git_context failed: %s',e )
    return ctx 

def confidence_boost_for_file (file_path :str ,git_ctx :GitContext )->float :
    if not git_ctx or not file_path :
        return 0.0 
    path_norm =file_path .replace ('\\','/')
    if path_norm in git_ctx .high_churn_files :
        return 0.1 
    if path_norm in git_ctx .recently_changed_files :
        return 0.05 
    return 0.0 
