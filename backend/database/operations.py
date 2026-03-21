import json 
from datetime import datetime 
from typing import List ,Optional ,Dict ,Any 
from sqlalchemy .orm import Session ,joinedload 
from sqlalchemy import desc ,text 
from .models import User ,Project ,Scan ,Vulnerability ,Issue ,KeywordDetected ,ProjectAnalysis ,ExternalApi ,TopConcern ,PoCScript ,init_db ,get_session 

class Database :

    def __init__ (self ,database_url :str ='sqlite:///sentinel.db'):
        self .engine =init_db (database_url )
        self ._ensure_result_json_column ()
        self ._ensure_deepwiki_doc_column ()
        self ._migrate_sentinai_users_to_scan_users ()

    def _ensure_result_json_column (self ):
        try :
            with self .engine .connect ()as conn :
                conn .execute (text ('ALTER TABLE scans ADD COLUMN result_json TEXT'))
                conn .commit ()
        except Exception :
            pass 

    def _ensure_deepwiki_doc_column (self ):
        try :
            with self .engine .connect ()as conn :
                conn .execute (text ('ALTER TABLE scans ADD COLUMN deepwiki_doc TEXT'))
                conn .commit ()
        except Exception :
            pass 

    def _migrate_sentinai_users_to_scan_users (self ):
        try :
            with self .engine .connect ()as conn :
                r =conn .execute (text ("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users', 'scan_users')")).fetchall ()
                names ={row [0 ]for row in r }
                if 'users'not in names :
                    return 
                info =conn .execute (text ('PRAGMA table_info(users)')).fetchall ()
                cols ={row [1 ]for row in info }
                if 'email'in cols :
                    return 
                if 'scan_users'not in names :
                    conn .execute (text ('ALTER TABLE users RENAME TO scan_users'))
                else :
                    conn .execute (text ('DROP TABLE users'))
                conn .commit ()
        except Exception :
            pass 

    def get_session (self )->Session :
        return get_session (self .engine )

    def get_or_create_user (self ,user_id :str )->User :
        with self .get_session ()as session :
            user =session .query (User ).filter_by (id =user_id ).first ()
            if not user :
                user =User (id =user_id )
                session .add (user )
                session .commit ()
                session .refresh (user )
            return user 

    def get_user (self ,user_id :str )->Optional [User ]:
        with self .get_session ()as session :
            return session .query (User ).filter_by (id =user_id ).first ()

    def user_exists (self ,user_id :str )->bool :
        with self .get_session ()as session :
            return session .query (User ).filter_by (id =user_id ).first ()is not None 

    def get_or_create_project (self ,user_id :str ,project_name :str ,project_id :str =None )->Project :
        with self .get_session ()as session :
            user =session .query (User ).filter_by (id =user_id ).first ()
            if not user :
                user =User (id =user_id )
                session .add (user )
            project =session .query (Project ).filter_by (user_id =user_id ,name =project_name ).first ()
            if not project :
                if not project_id :
                    project_id =f'proj_{int (datetime .utcnow ().timestamp ())}'
                project =Project (id =project_id ,user_id =user_id ,name =project_name ,created_at =datetime .utcnow ())
                session .add (project )
                session .commit ()
                session .refresh (project )
            return project 

    def get_project (self ,user_id :str ,project_name :str )->Optional [Project ]:
        with self .get_session ()as session :
            return session .query (Project ).filter_by (user_id =user_id ,name =project_name ).first ()

    def get_project_by_id (self ,project_id :str )->Optional [Project ]:
        with self .get_session ()as session :
            return session .query (Project ).filter_by (id =project_id ).first ()

    def get_user_projects (self ,user_id :str )->List [Dict [str ,Any ]]:
        with self .get_session ()as session :
            projects =session .query (Project ).filter_by (user_id =user_id ).all ()
            result =[]
            for project in projects :
                scan_count =session .query (Scan ).filter_by (project_id =project .id ).count ()
                result .append ({'id':project .id ,'name':project .name ,'created_at':project .created_at .strftime ('%Y-%m-%d %H:%M:%S'),'scan_count':scan_count })
            return result 

    def get_user_projects_with_scans (self ,user_id :str )->List [Dict [str ,Any ]]:
        with self .get_session ()as session :
            projects =session .query (Project ).filter_by (user_id =user_id ).order_by (desc (Project .created_at )).all ()
            result =[]
            for project in projects :
                scans =session .query (Scan ).filter_by (project_id =project .id ).order_by (desc (Scan .timestamp )).all ()
                scan_dicts =[]
                for scan in scans :
                    scan_dict =self .export_scan_to_dict (scan .id )
                    if scan_dict :
                        scan_dicts .append (scan_dict )
                result .append ({'id':project .id ,'name':project .name ,'created_at':project .created_at .strftime ('%Y-%m-%d %H:%M:%S'),'scans':scan_dicts })
            return result 

    def save_scan (self ,user_id :str ,project_name :str ,scan_data :Dict [str ,Any ])->str :
        with self .get_session ()as session :
            project =self ._get_or_create_project_internal (session ,user_id ,project_name )
            scan_id =scan_data .get ('scan_id',f'scan_{user_id }_{int (datetime .utcnow ().timestamp ())}')
            timestamp_str =scan_data .get ('timestamp',datetime .utcnow ().strftime ('%Y-%m-%d %H:%M:%S'))
            try :
                ts =datetime .strptime (timestamp_str ,'%Y-%m-%d %H:%M:%S')
            except Exception :
                ts =datetime .utcnow ()
            stats =scan_data .get ('stats',{})
            scan =Scan (id =scan_id ,project_id =project .id ,scan_type =scan_data .get ('scan_type','1'),timestamp =ts ,project_name =scan_data .get ('project_name',project_name ),files_scanned =stats .get ('files_scanned',0 ),vulnerabilities_count =stats .get ('vulnerabilities',0 ),elapsed_seconds =stats .get ('elapsed_seconds',0.0 ),result_json =json .dumps (scan_data ))
            session .add (scan )
            session .commit ()
            return scan_id 

    def _get_or_create_project_internal (self ,session :Session ,user_id :str ,project_name :str )->Project :
        user =session .query (User ).filter_by (id =user_id ).first ()
        if not user :
            user =User (id =user_id )
            session .add (user )
        project =session .query (Project ).filter_by (user_id =user_id ,name =project_name ).first ()
        if not project :
            project =Project (id =f'proj_{int (datetime .utcnow ().timestamp ())}',user_id =user_id ,name =project_name ,created_at =datetime .utcnow ())
            session .add (project )
            session .flush ()
        return project 

    def _save_project_analysis (self ,session :Session ,scan_id :str ,analysis_data :Dict [str ,Any ]):
        project_info =analysis_data .get ('project_info',{})
        security_context =analysis_data .get ('security_context',{})
        risk_summary =analysis_data .get ('risk_summary',{})
        project_analysis =ProjectAnalysis (scan_id =scan_id ,project_name =project_info .get ('name'),framework =project_info .get ('framework'),description =project_info .get ('description'),has_authentication =security_context .get ('has_authentication',False ),has_database =security_context .get ('has_database',False ))
        session .add (project_analysis )
        session .flush ()
        for api in security_context .get ('external_apis',[]):
            session .add (ExternalApi (project_analysis_id =project_analysis .id ,api_name =api ))
        for concern in risk_summary .get ('top_concerns',[]):
            session .add (TopConcern (project_analysis_id =project_analysis .id ,concern =concern ))

    def _save_vulnerability (self ,session :Session ,scan_id :str ,vuln_data :Dict [str ,Any ]):
        vulnerability =Vulnerability (scan_id =scan_id ,filename =vuln_data .get ('filename',''),status =vuln_data .get ('status','VULNERABLE'),source_code =vuln_data .get ('source_code',''))
        session .add (vulnerability )
        session .flush ()
        for issue_data in vuln_data .get ('issues',[]):
            self ._save_issue (session ,vulnerability .id ,issue_data )

    def _save_issue (self ,session :Session ,vulnerability_id :int ,issue_data :Dict [str ,Any ]):
        code_context =issue_data .get ('code_context',{})
        poc_verbal =issue_data .get ('poc_verbal',{})
        issue =Issue (vulnerability_id =vulnerability_id ,severity =issue_data .get ('severity','HIGH'),type =issue_data .get ('type','Unknown'),subtype =issue_data .get ('subtype'),trigger =issue_data .get ('trigger'),line =issue_data .get ('line',1 ),description =issue_data .get ('description',''),vulnerable_code =issue_data .get ('vulnerable_code',''),impact_summary =issue_data .get ('impact_summary'),confidence_score =issue_data .get ('confidence_score'),cwe_id =issue_data .get ('cwe_id'),remediation =issue_data .get ('remediation'),consequences =issue_data .get ('consequences'),references =issue_data .get ('references'),fingerprint =issue_data .get ('fingerprint',''),cvss_score =issue_data .get ('cvss_score'),fix_complexity =issue_data .get ('fix_complexity'),code_context_before =code_context .get ('before',[]),code_context_target =code_context .get ('target',''),code_context_after =code_context .get ('after',[]),poc_verbal_vectors =poc_verbal .get ('vectors',[]),poc_verbal_steps =poc_verbal .get ('steps',[]))
        session .add (issue )
        session .flush ()
        for keyword_data in issue_data .get ('keywords_detected',[]):
            session .add (KeywordDetected (issue_id =issue .id ,keyword =keyword_data .get ('keyword',''),line =keyword_data .get ('line',0 ),context =keyword_data .get ('context','')))
        poc =issue_data .get ('poc_script')or issue_data .get ('poc')
        if poc and isinstance (poc ,dict )and poc .get ('script'):
            session .add (PoCScript (issue_id =issue .id ,language =poc .get ('language','text'),script =poc .get ('script',''),exploit_type =poc .get ('exploit_type')))

    def get_scan (self ,scan_id :str )->Optional [Scan ]:
        with self .get_session ()as session :
            return session .query (Scan ).options (joinedload (Scan .vulnerabilities ).joinedload (Vulnerability .issues ).joinedload (Issue .keywords_detected ),joinedload (Scan .vulnerabilities ).joinedload (Vulnerability .issues ).joinedload (Issue .poc_scripts ),joinedload (Scan .project_analysis ).joinedload (ProjectAnalysis .external_apis ),joinedload (Scan .project_analysis ).joinedload (ProjectAnalysis .top_concerns )).filter_by (id =scan_id ).first ()

    def get_scan_by_user_project (self ,user_id :str ,project_name :str ,scan_id :str )->Optional [Scan ]:
        with self .get_session ()as session :
            project =session .query (Project ).filter_by (user_id =user_id ,name =project_name ).first ()
            if not project :
                return None 
            return session .query (Scan ).filter_by (id =scan_id ,project_id =project .id ).first ()

    def get_user_scans (self ,user_id :str )->List [Scan ]:
        with self .get_session ()as session :
            return session .query (Scan ).join (Project ).filter (Project .user_id ==user_id ).order_by (desc (Scan .timestamp )).all ()

    def scan_exists_for_user (self ,user_id :str ,scan_id :str )->bool :
        with self .get_session ()as session :
            scan =session .query (Scan ).join (Project ).filter (Scan .id ==scan_id ,Project .user_id ==user_id ).first ()
            return scan is not None 

    def get_scan_deepwiki (self ,scan_id :str )->Optional [str ]:
        with self .get_session ()as session :
            scan =session .query (Scan ).filter_by (id =scan_id ).first ()
            if not scan :
                return None 
            return getattr (scan ,'deepwiki_doc',None )

    def update_scan_deepwiki (self ,scan_id :str ,doc_text :str )->bool :
        with self .get_session ()as session :
            scan =session .query (Scan ).filter_by (id =scan_id ).first ()
            if not scan :
                return False 
            scan .deepwiki_doc =doc_text 
            session .commit ()
            return True 

    def update_issue_poc (self ,fingerprint :str ,poc_data :Dict [str ,Any ]):
        with self .get_session ()as session :
            issue =session .query (Issue ).filter_by (fingerprint =fingerprint ).first ()
            if not issue :
                return False 
            existing_poc =session .query (PoCScript ).filter_by (issue_id =issue .id ).first ()
            if existing_poc :
                existing_poc .language =poc_data .get ('language',existing_poc .language )
                existing_poc .script =poc_data .get ('script',existing_poc .script )
                existing_poc .exploit_type =poc_data .get ('exploit_type',existing_poc .exploit_type )
            else :
                session .add (PoCScript (issue_id =issue .id ,language =poc_data .get ('language','text'),script =poc_data .get ('script',''),exploit_type =poc_data .get ('exploit_type')))
            session .commit ()
            return True 

    def get_poc_by_fingerprint (self ,user_id :str ,scan_id :str ,fingerprint :str )->Optional [PoCScript ]:
        with self .get_session ()as session :
            scan =session .query (Scan ).join (Project ).filter (Scan .id ==scan_id ,Project .user_id ==user_id ).first ()
            if not scan :
                return None 
            poc =session .query (PoCScript ).join (Issue ).join (Vulnerability ).filter (PoCScript .issue_id ==Issue .id ,Issue .fingerprint ==fingerprint ,Vulnerability .scan_id ==scan_id ).first ()
            return poc 

    def export_scan_to_dict (self ,scan_id :str )->Optional [Dict [str ,Any ]]:
        with self .get_session ()as session :
            scan =session .query (Scan ).filter_by (id =scan_id ).first ()
            if not scan :
                return None 
            if getattr (scan ,'result_json',None )and scan .result_json :
                try :
                    return json .loads (scan .result_json )
                except Exception :
                    pass 
        scan =self .get_scan (scan_id )
        if not scan :
            return None 
        result ={'scan_id':scan .id ,'scan_type':scan .scan_type ,'timestamp':scan .timestamp .strftime ('%Y-%m-%d %H:%M:%S'),'project_name':scan .project_name ,'stats':{'files_scanned':scan .files_scanned ,'vulnerabilities':scan .vulnerabilities_count ,'elapsed_seconds':scan .elapsed_seconds },'project_analysis':{},'vulnerabilities':[]}
        if scan .project_analysis :
            pa =scan .project_analysis 
            result ['project_analysis']={'project_info':{'name':pa .project_name ,'framework':pa .framework ,'description':pa .description },'security_context':{'has_authentication':pa .has_authentication ,'has_database':pa .has_database ,'external_apis':[api .api_name for api in pa .external_apis ]},'risk_summary':{'top_concerns':[concern .concern for concern in pa .top_concerns ]}}
        for vuln in scan .vulnerabilities :
            vuln_dict ={'filename':vuln .filename ,'status':vuln .status ,'source_code':vuln .source_code ,'issues':[]}
            for issue in vuln .issues :
                issue_dict ={'severity':issue .severity ,'type':issue .type ,'trigger':issue .trigger ,'line':issue .line ,'description':issue .description ,'vulnerable_code':issue .vulnerable_code ,'subtype':issue .subtype ,'impact_summary':issue .impact_summary ,'confidence_score':issue .confidence_score ,'cwe_id':issue .cwe_id ,'remediation':issue .remediation ,'consequences':issue .consequences ,'references':issue .references ,'fingerprint':issue .fingerprint ,'cvss_score':issue .cvss_score ,'fix_complexity':issue .fix_complexity ,'code_context':{'before':issue .code_context_before or [],'target':issue .code_context_target or '','after':issue .code_context_after or []},'poc_verbal':{'vectors':issue .poc_verbal_vectors or [],'steps':issue .poc_verbal_steps or []},'keywords_detected':[{'keyword':kw .keyword ,'line':kw .line ,'context':kw .context }for kw in issue .keywords_detected ]}
                if issue .poc_scripts :
                    poc =issue .poc_scripts [0 ]
                    issue_dict ['poc_script']={'language':poc .language ,'script':poc .script }
                    issue_dict ['poc']=issue_dict ['poc_script']
                vuln_dict ['issues'].append (issue_dict )
            result ['vulnerabilities'].append (vuln_dict )
        return result 

    def export_user_data (self ,user_id :str )->Dict [str ,Any ]:
        with self .get_session ()as session :
            projects =session .query (Project ).filter_by (user_id =user_id ).all ()
            result ={'user_id':user_id ,'projects':[]}
            for project in projects :
                project_dict ={'id':project .id ,'name':project .name ,'created_at':project .created_at .strftime ('%Y-%m-%d %H:%M:%S'),'scans':[]}
                for scan in project .scans :
                    scan_dict =self .export_scan_to_dict (scan .id )
                    if scan_dict :
                        project_dict ['scans'].append (scan_dict )
                result ['projects'].append (project_dict )
            return result 
db =None 

def init_database (database_url :str ='sqlite:///sentinel.db')->Database :
    global db 
    db =Database (database_url )
    return db 
