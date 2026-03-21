import logging 
from dataclasses import dataclass ,field 
from typing import Any 
from backend .worker .core .agents .models import AttackPath ,FuzzingHint 
logger =logging .getLogger (__name__ )

@dataclass 
class FuzzParam :
    name :str 
    location :str 
    type_hint :str ='string'

@dataclass 
class InjectionPoint :
    parameter_or_field :str 
    payload_type :str 
    suggestion :str 

def _payload_templates_for_class (vuln_class :str )->list [str ]:
    c =(vuln_class or '').lower ()
    if 'sql'in c :
        return ["' OR 1=1--",'1; DROP TABLE users--','1 UNION SELECT null,null--']
    if 'command'in c or 'os'in c :
        return ['; id','| cat /etc/passwd','`id`']
    if 'template'in c or 'ssti'in c :
        return ['{{7*7}}','${7*7}','<%= 7*7 %>']
    if 'xss'in c :
        return ['<script>alert(1)</script>','<img src=x onerror=alert(1)>']
    if 'ldap'in c :
        return ['*)(uid=*','admin)(|(password=*']
    if 'auth'in c or 'bypass'in c :
        return ['admin','Bearer invalid','Cookie: session=../../etc/passwd']
    if 'idor'in c :
        return ['../other_user_id','0','-1']
    return ['<payload>','{{PAYLOAD}}']

def generate_hints_from_attack_path (path :AttackPath ,entry_point_http_method :str ='POST')->FuzzingHint :
    entry =path .entry_point 
    entry_str =f'{entry .file_path }:{entry .line_number }'if entry else 'unknown'
    steps =getattr (path ,'steps',[])
    payload_templates :list [str ]=[]
    for s in steps :
        pt =getattr (s ,'payload_type','')
        if pt and pt not in payload_templates :
            payload_templates .append (pt )
    for chain in getattr (path ,'chains_involved',[]):
        for f in getattr (chain ,'findings',[]):
            for t in _payload_templates_for_class (getattr (f ,'vulnerability_class','')):
                if t not in payload_templates :
                    payload_templates .append (t )
    if not payload_templates :
        payload_templates =['<payload>']
    return FuzzingHint (attack_path_id =getattr (path ,'path_id',''),entry_point =entry_str ,http_method =entry_point_http_method ,required_parameters =[],injection_points =[],payload_templates =payload_templates [:20 ],boundary_values =['','0','-1','null','very_long_string_'+'x'*500 ],authentication_required =getattr (entry ,'authentication_required',False )if entry else False ,auth_setup_steps =['Obtain valid session or token']if entry and getattr (entry ,'authentication_required',False )else [])

def generate_hints_from_findings (findings :list [Any ],entry_point :str ='',http_method :str ='POST')->list [FuzzingHint ]:
    hints =[]
    for f in findings :
        vuln_class =getattr (f ,'vulnerability_class',None )or (f .get ('type')if isinstance (f ,dict )else '')
        path_id =getattr (f ,'finding_id',None )or (f .get ('finding_id')if isinstance (f ,dict )else '')
        file_path =getattr (f ,'file_path',None )or (f .get ('file_path')if isinstance (f ,dict )else '')
        ep =entry_point or file_path or 'unknown'
        hints .append (FuzzingHint (attack_path_id =path_id or '',entry_point =ep ,http_method =http_method ,required_parameters =[],injection_points =[],payload_templates =_payload_templates_for_class (vuln_class ),boundary_values =['','0','null'],authentication_required =False ,auth_setup_steps =[]))
    return hints 
