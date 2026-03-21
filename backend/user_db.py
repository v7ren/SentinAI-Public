import json 
import os 
import sqlite3 
from pathlib import Path 
from typing import Any ,Dict ,List ,Optional 
from contextlib import contextmanager 
_DB_PATH :Optional [Path ]=None 

def _get_db_path ()->Path :
    global _DB_PATH 
    if _DB_PATH is not None :
        return _DB_PATH 
    path =os .getenv ('AUTH_USERS_DB')or os .getenv ('USERS_DB_PATH')
    if path :
        _DB_PATH =Path (path )
        return _DB_PATH 
    database_url =os .getenv ('DATABASE_URL','sqlite:///sentinel.db').strip ()
    if database_url .startswith ('sqlite:///'):
        db_part =database_url .replace ('sqlite:///','').strip ('/')
        db_part =db_part or 'sentinel.db'
        _DB_PATH =Path (db_part )if os .path .isabs (db_part )else Path .cwd ()/db_part 
    else :
        _DB_PATH =Path (__file__ ).resolve ().parent /'sentinel.db'
    return _DB_PATH 

@contextmanager 
def _get_conn ():
    path =_get_db_path ()
    path .parent .mkdir (parents =True ,exist_ok =True )
    conn =sqlite3 .connect (str (path ))
    conn .row_factory =sqlite3 .Row 
    try :
        yield conn 
        conn .commit ()
    finally :
        conn .close ()

def init_user_db ()->None :
    _migrate_sentinai_users_table_if_needed ()
    with _get_conn ()as conn :
        conn .execute ("\n            CREATE TABLE IF NOT EXISTS users (\n                email TEXT PRIMARY KEY,\n                password_hash TEXT,\n                name TEXT,\n                auth_methods TEXT DEFAULT '[]'\n            )\n        ")
    _migrate_from_json_if_exists ()
    _add_subscription_columns ()
    _ensure_plans_tables ()

def _migrate_sentinai_users_table_if_needed ()->None :
    path =_get_db_path ()
    if not path .exists ():
        return 
    try :
        conn =sqlite3 .connect (str (path ))
        try :
            r =conn .execute ("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users', 'scan_users')").fetchall ()
            names ={row [0 ]for row in r }
            if 'users'not in names :
                return 
            info =conn .execute ('PRAGMA table_info(users)').fetchall ()
            cols ={row [1 ]for row in info }
            if 'email'in cols :
                return 
            if 'scan_users'not in names :
                conn .execute ('ALTER TABLE users RENAME TO scan_users')
            else :
                conn .execute ('DROP TABLE users')
            conn .commit ()
        finally :
            conn .close ()
    except Exception :
        pass 

def _add_subscription_columns ()->None :
    with _get_conn ()as conn :
        info =conn .execute ('PRAGMA table_info(users)').fetchall ()
        cols ={r [1 ]for r in info }
        if 'tier'not in cols :
            conn .execute ("ALTER TABLE users ADD COLUMN tier TEXT NOT NULL DEFAULT 'free'")
        if 'token_balance'not in cols :
            conn .execute ('ALTER TABLE users ADD COLUMN token_balance INTEGER NOT NULL DEFAULT 0')
        if 'subscription_ends_at'not in cols :
            conn .execute ('ALTER TABLE users ADD COLUMN subscription_ends_at TEXT')

def _ensure_plans_tables ()->None :
    with _get_conn ()as conn :
        conn .execute ('\n            CREATE TABLE IF NOT EXISTS subscription_plans (\n                id TEXT PRIMARY KEY,\n                name TEXT NOT NULL,\n                name_en TEXT,\n                amount INTEGER NOT NULL,\n                tier TEXT NOT NULL,\n                months INTEGER NOT NULL DEFAULT 1,\n                description TEXT,\n                active INTEGER NOT NULL DEFAULT 1\n            )\n        ')
        conn .execute ('\n            CREATE TABLE IF NOT EXISTS token_packages (\n                id TEXT PRIMARY KEY,\n                name TEXT NOT NULL,\n                tokens INTEGER NOT NULL,\n                amount INTEGER NOT NULL,\n                description TEXT,\n                active INTEGER NOT NULL DEFAULT 1\n            )\n        ')
        if conn .execute ('SELECT COUNT(*) FROM subscription_plans').fetchone ()[0 ]==0 :
            conn .execute ('INSERT INTO subscription_plans (id, name, name_en, amount, tier, months, description, active)\n                   VALUES (?, ?, ?, ?, ?, ?, ?, 1)',('pro_monthly','專業方案月訂','Pro Monthly',990 ,'pro',1 ,'每月 100 次諮詢，完整報告與匯出，優先支援'))
        if conn .execute ('SELECT COUNT(*) FROM token_packages').fetchone ()[0 ]==0 :
            for row in [('tokens_50','50 點數',50 ,199 ,'50 次諮詢點數'),('tokens_100','100 點數',100 ,349 ,'100 次諮詢點數'),('tokens_300','300 點數',300 ,899 ,'300 次諮詢點數')]:
                conn .execute ('INSERT INTO token_packages (id, name, tokens, amount, description, active)\n                       VALUES (?, ?, ?, ?, ?, 1)',(row [0 ],row [1 ],row [2 ],row [3 ],row [4 ]))

def _migrate_from_json_if_exists ()->None :
    json_path =Path (__file__ ).resolve ().parent /'users.json'
    if not json_path .exists ():
        return 
    try :
        with open (json_path ,'r',encoding ='utf-8')as f :
            data =json .load (f )
        users =data .get ('users')or []
        if not users :
            return 
        with _get_conn ()as conn :
            for u in users :
                email =(u .get ('email')or '').strip ().lower ()
                if not email or '@'not in email :
                    continue 
                methods =u .get ('auth_methods')
                if not isinstance (methods ,list ):
                    methods =['password']if u .get ('password_hash')else []
                conn .execute ('INSERT OR REPLACE INTO users (email, password_hash, name, auth_methods)\n                       VALUES (?, ?, ?, ?)',(email ,u .get ('password_hash')or None ,(u .get ('name')or '').strip ()or None ,json .dumps (methods )))
    except (json .JSONDecodeError ,OSError ,sqlite3 .Error ):
        pass 

def _row_to_user (row :sqlite3 .Row )->Dict [str ,Any ]:
    methods =row ['auth_methods']
    if isinstance (methods ,str ):
        try :
            methods =json .loads (methods )if methods else []
        except json .JSONDecodeError :
            methods =[]
    if not isinstance (methods ,list ):
        methods =[]
    out ={'email':row ['email'],'password_hash':row ['password_hash'],'name':row ['name']or '','auth_methods':methods }
    if 'tier'in row .keys ():
        out ['tier']=row ['tier']or 'free'
    if 'token_balance'in row .keys ():
        out ['token_balance']=int (row ['token_balance']or 0 )
    if 'subscription_ends_at'in row .keys ():
        out ['subscription_ends_at']=row ['subscription_ends_at']
    return out 

def get_user_by_email (email :str )->Optional [Dict [str ,Any ]]:
    email_lower =(email or '').strip ().lower ()
    if not email_lower or '@'not in email_lower :
        return None 
    with _get_conn ()as conn :
        row =conn .execute ('SELECT * FROM users WHERE email = ?',(email_lower ,)).fetchone ()
    return _row_to_user (row )if row else None 

def create_user (email :str ,*,password_hash :Optional [str ]=None ,name :Optional [str ]=None ,auth_methods :Optional [List [str ]]=None )->None :
    email_lower =(email or '').strip ().lower ()
    if not email_lower or '@'not in email_lower :
        raise ValueError ('Valid email required')
    methods =auth_methods or []
    with _get_conn ()as conn :
        conn .execute ('INSERT INTO users (email, password_hash, name, auth_methods)\n               VALUES (?, ?, ?, ?)',(email_lower ,password_hash ,(name or '').strip ()or email_lower .split ('@')[0 ],json .dumps (methods )))

def update_user (email :str ,*,password_hash :Optional [str ]=None ,name :Optional [str ]=None ,auth_methods :Optional [List [str ]]=None ,tier :Optional [str ]=None ,token_balance :Optional [int ]=None ,subscription_ends_at :Optional [str ]=None )->bool :
    email_lower =(email or '').strip ().lower ()
    if not email_lower or '@'not in email_lower :
        return False 
    user =get_user_by_email (email_lower )
    if not user :
        return False 
    updates :List [str ]=[]
    params :List [Any ]=[]
    if password_hash is not None :
        updates .append ('password_hash = ?')
        params .append (password_hash )
    if name is not None :
        updates .append ('name = ?')
        params .append ((name or '').strip ())
    if auth_methods is not None :
        updates .append ('auth_methods = ?')
        params .append (json .dumps (list (auth_methods )))
    if tier is not None :
        updates .append ('tier = ?')
        params .append (tier )
    if token_balance is not None :
        updates .append ('token_balance = ?')
        params .append (token_balance )
    if subscription_ends_at is not None :
        updates .append ('subscription_ends_at = ?')
        params .append (subscription_ends_at )
    if not updates :
        return True 
    params .append (email_lower )
    with _get_conn ()as conn :
        conn .execute (f"UPDATE users SET {', '.join (updates )} WHERE email = ?",params )
    return True 

def get_subscription_info (email :str )->Dict [str ,Any ]:
    user =get_user_by_email ((email or '').strip ().lower ())
    if not user :
        return {'tier':'free','token_balance':0 ,'subscription_ends_at':None }
    return {'tier':user .get ('tier')or 'free','token_balance':int (user .get ('token_balance')or 0 ),'subscription_ends_at':user .get ('subscription_ends_at')}

def add_tokens (email :str ,amount :int )->bool :
    if amount <=0 :
        return False 
    email_lower =(email or '').strip ().lower ()
    with _get_conn ()as conn :
        conn .execute ('UPDATE users SET token_balance = COALESCE(token_balance, 0) + ? WHERE email = ?',(amount ,email_lower ))
    return True 

def consume_one_token (email :str )->bool :
    email_lower =(email or '').strip ().lower ()
    with _get_conn ()as conn :
        conn .execute ('UPDATE users SET token_balance = COALESCE(token_balance, 0) - 1 WHERE email = ? AND COALESCE(token_balance, 0) >= 1',(email_lower ,))
        cur =conn .execute ('SELECT changes()').fetchone ()
    return bool (cur and cur [0 ]>0 )

def set_subscription (email :str ,tier :str ,ends_at :Optional [str ])->bool :
    email_lower =(email or '').strip ().lower ()
    return update_user (email_lower ,tier =tier ,subscription_ends_at =ends_at )

def get_subscription_plans ()->List [Dict [str ,Any ]]:
    with _get_conn ()as conn :
        rows =conn .execute ('SELECT id, name, name_en, amount, tier, months, description FROM subscription_plans WHERE active = 1 ORDER BY amount ASC').fetchall ()
    return [{'id':r ['id'],'name':r ['name'],'name_en':r ['name_en']or '','amount':int (r ['amount']),'tier':r ['tier'],'months':int (r ['months']),'description':r ['description']or ''}for r in rows ]

def get_token_packages ()->List [Dict [str ,Any ]]:
    with _get_conn ()as conn :
        rows =conn .execute ('SELECT id, name, tokens, amount, description FROM token_packages WHERE active = 1 ORDER BY amount ASC').fetchall ()
    return [{'id':r ['id'],'name':r ['name'],'tokens':int (r ['tokens']),'amount':int (r ['amount']),'description':r ['description']or ''}for r in rows ]

def get_plan_by_id (plan_id :str )->Optional [Dict [str ,Any ]]:
    if not (plan_id or '').strip ():
        return None 
    with _get_conn ()as conn :
        row =conn .execute ('SELECT id, name, name_en, amount, tier, months, description FROM subscription_plans WHERE id = ? AND active = 1',(plan_id .strip (),)).fetchone ()
    if not row :
        return None 
    return {'id':row ['id'],'name':row ['name'],'name_en':row ['name_en']or '','amount':int (row ['amount']),'tier':row ['tier'],'months':int (row ['months']),'description':row ['description']or ''}

def get_token_package_by_id (package_id :str )->Optional [Dict [str ,Any ]]:
    if not (package_id or '').strip ():
        return None 
    with _get_conn ()as conn :
        row =conn .execute ('SELECT id, name, tokens, amount, description FROM token_packages WHERE id = ? AND active = 1',(package_id .strip (),)).fetchone ()
    if not row :
        return None 
    return {'id':row ['id'],'name':row ['name'],'tokens':int (row ['tokens']),'amount':int (row ['amount']),'description':row ['description']or ''}
