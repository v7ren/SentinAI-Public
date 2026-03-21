from datetime import datetime 
from typing import List ,Optional 
from sqlalchemy import create_engine ,Column ,Integer ,String ,Float ,Boolean ,DateTime ,Text ,ForeignKey ,JSON ,Index ,Table 
from sqlalchemy .orm import declarative_base ,relationship ,Session 
from sqlalchemy .pool import StaticPool 
Base =declarative_base ()

class User (Base ):
    __tablename__ ='scan_users'
    id =Column (String (100 ),primary_key =True )
    created_at =Column (DateTime ,default =datetime .utcnow )
    updated_at =Column (DateTime ,default =datetime .utcnow ,onupdate =datetime .utcnow )
    projects =relationship ('Project',back_populates ='user',cascade ='all, delete-orphan')

    def __repr__ (self ):
        return f'<User(id={self .id })>'

class Project (Base ):
    __tablename__ ='projects'
    id =Column (String (50 ),primary_key =True )
    user_id =Column (String (100 ),ForeignKey ('scan_users.id'),nullable =False ,index =True )
    name =Column (String (255 ),nullable =False )
    created_at =Column (DateTime ,nullable =False )
    user =relationship ('User',back_populates ='projects')
    scans =relationship ('Scan',back_populates ='project',cascade ='all, delete-orphan')
    __table_args__ =(Index ('idx_project_user_name','user_id','name'),)

    def __repr__ (self ):
        return f'<Project(id={self .id }, name={self .name })>'

class Scan (Base ):
    __tablename__ ='scans'
    id =Column (String (100 ),primary_key =True )
    project_id =Column (String (50 ),ForeignKey ('projects.id'),nullable =False ,index =True )
    scan_type =Column (String (10 ),nullable =False )
    timestamp =Column (DateTime ,nullable =False )
    project_name =Column (String (255 ))
    result_json =Column (Text ,nullable =True )
    deepwiki_doc =Column (Text ,nullable =True )
    files_scanned =Column (Integer ,default =0 )
    vulnerabilities_count =Column (Integer ,default =0 )
    elapsed_seconds =Column (Float ,default =0.0 )
    project =relationship ('Project',back_populates ='scans')
    vulnerabilities =relationship ('Vulnerability',back_populates ='scan',cascade ='all, delete-orphan')
    project_analysis =relationship ('ProjectAnalysis',back_populates ='scan',uselist =False ,cascade ='all, delete-orphan')
    __table_args__ =(Index ('idx_scan_project_timestamp','project_id','timestamp'),Index ('idx_scan_type','scan_type'))

    def __repr__ (self ):
        return f'<Scan(id={self .id }, type={self .scan_type })>'

class ProjectAnalysis (Base ):
    __tablename__ ='project_analyses'
    id =Column (Integer ,primary_key =True ,autoincrement =True )
    scan_id =Column (String (100 ),ForeignKey ('scans.id'),nullable =False ,unique =True )
    project_name =Column (String (255 ))
    framework =Column (String (100 ))
    description =Column (Text )
    has_authentication =Column (Boolean ,default =False )
    has_database =Column (Boolean ,default =False )
    scan =relationship ('Scan',back_populates ='project_analysis')
    external_apis =relationship ('ExternalApi',back_populates ='project_analysis',cascade ='all, delete-orphan')
    top_concerns =relationship ('TopConcern',back_populates ='project_analysis',cascade ='all, delete-orphan')

    def __repr__ (self ):
        return f'<ProjectAnalysis(scan_id={self .scan_id })>'

class ExternalApi (Base ):
    __tablename__ ='external_apis'
    id =Column (Integer ,primary_key =True ,autoincrement =True )
    project_analysis_id =Column (Integer ,ForeignKey ('project_analyses.id'),nullable =False ,index =True )
    api_name =Column (String (255 ),nullable =False )
    project_analysis =relationship ('ProjectAnalysis',back_populates ='external_apis')

class TopConcern (Base ):
    __tablename__ ='top_concerns'
    id =Column (Integer ,primary_key =True ,autoincrement =True )
    project_analysis_id =Column (Integer ,ForeignKey ('project_analyses.id'),nullable =False ,index =True )
    concern =Column (Text ,nullable =False )
    project_analysis =relationship ('ProjectAnalysis',back_populates ='top_concerns')

class Vulnerability (Base ):
    __tablename__ ='vulnerabilities'
    id =Column (Integer ,primary_key =True ,autoincrement =True )
    scan_id =Column (String (100 ),ForeignKey ('scans.id'),nullable =False ,index =True )
    filename =Column (String (500 ),nullable =False )
    status =Column (String (20 ),nullable =False ,default ='VULNERABLE')
    source_code =Column (Text )
    scan =relationship ('Scan',back_populates ='vulnerabilities')
    issues =relationship ('Issue',back_populates ='vulnerability',cascade ='all, delete-orphan')
    __table_args__ =(Index ('idx_vuln_scan_filename','scan_id','filename'),)

    def __repr__ (self ):
        return f'<Vulnerability(filename={self .filename }, issues={(len (self .issues )if self .issues else 0 )})>'

class Issue (Base ):
    __tablename__ ='issues'
    id =Column (Integer ,primary_key =True ,autoincrement =True )
    vulnerability_id =Column (Integer ,ForeignKey ('vulnerabilities.id'),nullable =False ,index =True )
    severity =Column (String (20 ),nullable =False ,index =True )
    type =Column (String (100 ),nullable =False )
    subtype =Column (String (100 ))
    trigger =Column (String (100 ))
    line =Column (Integer ,nullable =False )
    description =Column (Text ,nullable =False )
    vulnerable_code =Column (Text )
    impact_summary =Column (Text )
    confidence_score =Column (Integer )
    cwe_id =Column (String (20 ))
    remediation =Column (JSON )
    consequences =Column (Text )
    references =Column (JSON )
    fingerprint =Column (String (50 ),index =True )
    cvss_score =Column (Float )
    fix_complexity =Column (String (20 ))
    code_context_before =Column (JSON )
    code_context_target =Column (Text )
    code_context_after =Column (JSON )
    poc_verbal_vectors =Column (JSON )
    poc_verbal_steps =Column (JSON )
    vulnerability =relationship ('Vulnerability',back_populates ='issues')
    keywords_detected =relationship ('KeywordDetected',back_populates ='issue',cascade ='all, delete-orphan')
    poc_scripts =relationship ('PoCScript',back_populates ='issue',cascade ='all, delete-orphan')
    __table_args__ =(Index ('idx_issue_severity_type','severity','type'),Index ('idx_issue_fingerprint','fingerprint'),Index ('idx_issue_vulnerability','vulnerability_id'))

    def __repr__ (self ):
        return f'<Issue(type={self .type }, severity={self .severity }, line={self .line })>'

class KeywordDetected (Base ):
    __tablename__ ='keywords_detected'
    id =Column (Integer ,primary_key =True ,autoincrement =True )
    issue_id =Column (Integer ,ForeignKey ('issues.id'),nullable =False ,index =True )
    keyword =Column (String (100 ),nullable =False )
    line =Column (Integer ,nullable =False )
    context =Column (Text )
    issue =relationship ('Issue',back_populates ='keywords_detected')

    def __repr__ (self ):
        return f'<KeywordDetected(keyword={self .keyword }, line={self .line })>'

class PoCScript (Base ):
    __tablename__ ='poc_scripts'
    id =Column (Integer ,primary_key =True ,autoincrement =True )
    issue_id =Column (Integer ,ForeignKey ('issues.id'),nullable =False ,index =True ,unique =True )
    language =Column (String (50 ))
    script =Column (Text ,nullable =False )
    exploit_type =Column (String (100 ))
    created_at =Column (DateTime ,default =datetime .utcnow )
    issue =relationship ('Issue',back_populates ='poc_scripts')

    def __repr__ (self ):
        return f'<PoCScript(language={self .language })>'

def init_db (database_url :str ='sqlite:///sentinel.db'):
    engine =create_engine (database_url ,connect_args ={'check_same_thread':False }if database_url .startswith ('sqlite')else {},poolclass =StaticPool if database_url .startswith ('sqlite')else None ,echo =False )
    Base .metadata .create_all (engine )
    return engine 

def get_session (engine ):
    return Session (engine )
