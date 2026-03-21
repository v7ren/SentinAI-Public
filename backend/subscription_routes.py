from flask import Blueprint ,jsonify 
from auth_helpers import require_user 
from user_db import get_subscription_info ,get_subscription_plans ,get_token_packages 
from db import get_consultation_count_this_month 
from subscription_config import TIER_CAPS 
subscription_bp =Blueprint ('subscription',__name__ ,url_prefix ='/api')

@subscription_bp .route ('/subscription/me',methods =['GET'])
def subscription_me ():
    email ,err =require_user ()
    if err :
        return (jsonify (err [0 ]),err [1 ])
    info =get_subscription_info (email )
    usage =get_consultation_count_this_month (email )
    cap =TIER_CAPS .get (info ['tier'])
    info ['usage_this_month']=usage 
    info ['monthly_cap']=cap 
    info ['plans']=get_subscription_plans ()
    info ['token_packages']=get_token_packages ()
    return jsonify (info )
