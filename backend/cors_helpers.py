import os 
from urllib .parse import urlparse 
from flask import request 

def _allowed_origins (frontend_url :str )->set :
    allowed =set ()
    if frontend_url :
        frontend_url =frontend_url .strip ().rstrip ('/')
        allowed .add (frontend_url )
        try :
            p =urlparse (frontend_url )
            if p .scheme and p .netloc :
                other ='https'if p .scheme =='http'else 'http'
                allowed .add (f'{other }://{p .netloc }')
        except Exception :
            pass 
    extra =(os .getenv ('CORS_ORIGINS')or '').strip ()
    if extra :
        allowed .update ((o .strip ().rstrip ('/')for o in extra .split (',')if o .strip ()))
    return allowed 

def get_cors_origin (*,frontend_url :str ='')->str :
    req_origin =(request .origin or '').strip ().rstrip ('/')if request .origin else ''
    allowed =_allowed_origins (frontend_url )
    if req_origin and req_origin in allowed :
        return req_origin 
    if allowed :
        return next (iter (allowed ))
    if req_origin :
        return req_origin 
    return '*'

def add_cors_headers_to_response (response ,origin :str )->None :
    response .headers ['Access-Control-Allow-Origin']=origin 
    response .headers ['Access-Control-Allow-Methods']='GET, POST, PUT, PATCH, DELETE, OPTIONS'
    response .headers ['Access-Control-Allow-Headers']='Content-Type, Authorization, X-CSRF-Token'
    response .headers ['Access-Control-Allow-Credentials']='true'if origin !='*'else 'false'
    response .headers ['Vary']='Origin'
