import os 
from urllib .parse import urlparse 

def is_production ()->bool :
    return os .getenv ('FLASK_ENV')=='production'or os .getenv ('ENV')=='production'

def get_frontend_url (*,required_in_production :bool =True )->str :
    url =(os .getenv ('FRONTEND_URL')or '').strip ().rstrip ('/')
    if is_production ()and required_in_production and (not url ):
        raise RuntimeError ('FRONTEND_URL environment variable is required in production')
    return url 

def get_backend_url (*,fallback :str ='',required_in_production :bool =False )->str :
    url =(os .getenv ('BACKEND_URL')or '').strip ().rstrip ('/')
    if url :
        return url 
    if is_production ()and required_in_production :
        raise RuntimeError ('BACKEND_URL environment variable is required in production')
    return fallback or 'http://localhost:5001'
