import os 
from dotenv import load_dotenv 
load_dotenv ()

def _env_int (name :str ,default :int )->int :
    raw =(os .getenv (name )or '').strip ()
    if not raw :
        return default 
    try :
        return max (0 ,int (raw ))
    except ValueError :
        return default 
TIER_CAPS ={'free':_env_int ('FREE_TIER_MONTHLY_CAP',10 ),'pro':_env_int ('PRO_TIER_MONTHLY_CAP',100 ),'team':None }
