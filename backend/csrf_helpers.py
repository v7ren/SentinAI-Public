import os 
import secrets 
from flask import session ,request 
CSRF_EXEMPT_PATHS =('/api/pay/return','/auth/oauth/google/callback','/auth/admin-login')

def _is_state_changing ():
    return request .method in ('POST','PUT','PATCH','DELETE')

def _is_proxy_trusted ():
    secret =os .environ .get ('PROXY_SECRET','').strip ()
    if not secret :
        return False 
    return secrets .compare_digest ((request .headers .get ('X-Proxy-Secret')or '').strip (),secret )

def _is_exempt ():
    if _is_proxy_trusted ():
        return True 
    path =(request .path or '').rstrip ('/')
    for exempt in CSRF_EXEMPT_PATHS :
        if path ==exempt .rstrip ('/')or path .endswith (exempt ):
            return True 
    return False 

def ensure_csrf_token_in_session ():
    if 'csrf_token'not in session or not session ['csrf_token']:
        session ['csrf_token']=secrets .token_hex (32 )
    return session ['csrf_token']

def validate_csrf ():
    if not _is_state_changing ()or _is_exempt ():
        return None 
    token_from_header =(request .headers .get ('X-CSRF-Token')or '').strip ()
    token_in_session =(session .get ('csrf_token')or '').strip ()
    if not token_in_session or not token_from_header or (not secrets .compare_digest (token_from_header ,token_in_session )):
        return ({'error':'Invalid or missing CSRF token'},403 )
    return None 
