import os 
from typing import Optional ,Tuple ,Any 
from flask import session 

def get_current_user_email ()->Optional [str ]:
    email =(session .get ('email')or '').strip ().lower ()
    if not email or '@'not in email :
        return None 
    return email 

def _admin_emails ()->set :
    raw =(os .getenv ('ADMIN_EMAILS')or '').strip ()
    return {e .strip ().lower ()for e in raw .split (',')if e .strip ()and '@'in e .strip ()}

def is_admin_session ()->bool :
    return bool (session .get ('admin_authenticated'))

def require_user ():
    email =get_current_user_email ()
    if email :
        return (email ,None )
    return (None ,({'error':'Login required'},401 ))

def require_admin ():
    if is_admin_session ():
        return (session .get ('admin_account')or 'admin',None )
    email ,err =require_user ()
    if err :
        return (None ,err )
    if email not in _admin_emails ():
        return (None ,({'error':'Admin access required'},403 ))
    return (email ,None )
