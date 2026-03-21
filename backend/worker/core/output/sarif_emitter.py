import os 
import json 
from typing import Dict ,List ,Optional 
from datetime import datetime 

class SARIFEmitter :
    CWE_TAXA ={'CWE-89':{'name':'SQL Injection','precision':'very-high'},'CWE-79':{'name':'Cross-site Scripting','precision':'very-high'},'CWE-78':{'name':'OS Command Injection','precision':'very-high'},'CWE-94':{'name':'Code Injection','precision':'very-high'},'CWE-22':{'name':'Path Traversal','precision':'very-high'},'CWE-502':{'name':'Deserialization of Untrusted Data','precision':'very-high'},'CWE-918':{'name':'Server-Side Request Forgery (SSRF)','precision':'very-high'},'CWE-798':{'name':'Use of Hard-coded Credentials','precision':'high'},'CWE-327':{'name':'Use of Broken or Risky Cryptographic Algorithm','precision':'high'},'CWE-352':{'name':'Cross-Site Request Forgery (CSRF)','precision':'high'},'CWE-639':{'name':'Authorization Bypass','precision':'high'},'CWE-611':{'name':'XML External Entity Reference','precision':'very-high'},'CWE-200':{'name':'Information Exposure','precision':'medium'},'CWE-201':{'name':'Information Exposure Through Sent Data','precision':'medium'},'CWE-532':{'name':'Insertion of Sensitive Information into Log File','precision':'medium'}}

    def __init__ (self ,tool_name :str ='SentinelAI',tool_version :str ='2.0'):
        self .tool_name =tool_name 
        self .tool_version =tool_version 

    def _severity_to_level (self ,severity :str )->str :
        mapping ={'CRITICAL':'error','HIGH':'error','MEDIUM':'warning','LOW':'note','INFORMATIONAL':'note'}
        return mapping .get (severity .upper (),'warning')

    def _confidence_to_rank (self ,confidence :float )->float :
        return min (100.0 ,max (0.0 ,confidence *100 ))

    def _cwe_to_rule_id (self ,cwe_id :str ,finding_type :str )->str :
        if cwe_id and cwe_id .startswith ('CWE-'):
            return cwe_id 
        return f"SENTINEL-{finding_type .upper ().replace (' ','-')}".replace ('--','-')

    def _build_rule_index (self ,findings :List [Dict ])->Dict :
        rules ={}
        for finding in findings :
            cwe_id =finding .get ('cwe_id','')
            finding_type =finding .get ('type','Unknown')
            rule_id =self ._cwe_to_rule_id (cwe_id ,finding_type )
            if rule_id not in rules :
                taxa =self .CWE_TAXA .get (cwe_id ,{})
                rules [rule_id ]={'id':rule_id ,'name':taxa .get ('name',finding_type ),'shortDescription':{'text':taxa .get ('name',finding_type )},'fullDescription':{'text':finding .get ('description',finding_type )},'defaultConfiguration':{'level':self ._severity_to_level (finding .get ('severity','MEDIUM')),'rank':self ._confidence_to_rank (finding .get ('confidence_score',0.5 ))},'help':{'text':finding .get ('remediation','No remediation provided.')},'properties':{'cwe':cwe_id ,'precision':taxa .get ('precision','medium'),'problem.severity':finding .get ('severity','MEDIUM').lower (),'security-severity':str (finding .get ('cvss_score',5.0 ))}}
        return rules 

    def _convert_finding_to_result (self ,finding :Dict ,run_index :int =0 )->Dict :
        cwe_id =finding .get ('cwe_id','')
        finding_type =finding .get ('type','Unknown')
        rule_id =self ._cwe_to_rule_id (cwe_id ,finding_type )
        filename =finding .get ('filename','unknown')
        line =finding .get ('line',1 )
        location ={'physicalLocation':{'artifactLocation':{'uri':filename ,'uriBaseId':f'{run_index }-srcRoot'},'region':{'startLine':line ,'endLine':line ,'snippet':{'text':finding .get ('vulnerable_code','')[:200 ]}}},'logicalLocations':[{'fullyQualifiedName':finding .get ('function_name','unknown'),'name':finding .get ('function_name','unknown').split ('.')[-1 ]if finding .get ('function_name')else 'unknown'}]}
        level =self ._severity_to_level (finding .get ('severity','MEDIUM'))
        validation_status =finding .get ('validation_status','')
        if validation_status in ('validated_probable_fp','unvalidated','parse_failed'):
            level ='note'
        result ={'ruleId':rule_id ,'ruleIndex':list (self ._build_rule_index ([finding ]).keys ()).index (rule_id )if rule_id in self ._build_rule_index ([finding ])else 0 ,'level':level ,'message':{'text':finding .get ('description',finding_type ),'markdown':f"**{finding_type }**\\n\\n{finding .get ('description','')}"},'locations':[location ],'rank':self ._confidence_to_rank (finding .get ('confidence_score',0.5 )),'properties':{'confidence':finding .get ('confidence_score',0.5 ),'cvssScore':finding .get ('cvss_score',0.0 ),'cvssVector':finding .get ('cvss_vector',''),'cweId':cwe_id ,'tier1Confirmed':finding .get ('tier1_was_correct',True ),'skepticPassed':finding .get ('skeptic_passed',True ),'fingerprint':finding .get ('fingerprint',''),'validationStatus':validation_status or 'validated','fpSoftFlag':finding .get ('_fp_soft_flag',''),'crossFileFlag':finding .get ('_cross_file_flag','')or finding .get ('_removal_rule',''),'belowThresholdNote':finding .get ('_below_threshold_note','')}}
        if finding .get ('remediation'):
            result ['fixes']=[{'description':{'text':finding .get ('remediation')},'artifactChanges':[{'artifactLocation':{'uri':filename ,'uriBaseId':f'{run_index }-srcRoot'},'replacements':[{'deletedRegion':{'startLine':line ,'endLine':line },'insertedContent':{'text':'[See remediation guidance]'}}]}]}]
        return result 

    def convert (self ,scan_results :Dict )->Dict :
        vulnerabilities =scan_results .get ('vulnerabilities',[])
        all_findings =[]
        for vuln in vulnerabilities :
            for issue in vuln .get ('issues',[]):
                issue ['filename']=vuln .get ('filename','unknown')
                all_findings .append (issue )
        rules =self ._build_rule_index (all_findings )
        results =[self ._convert_finding_to_result (f ,0 )for f in all_findings ]
        sarif ={'$schema':'https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json','version':'2.1.0','runs':[{'tool':{'driver':{'name':self .tool_name ,'version':self .tool_version ,'informationUri':'https://sentinel.ai','rules':list (rules .values ())}},'invocations':[{'executionSuccessful':True ,'startTimeUtc':scan_results .get ('timestamp',datetime .now ().isoformat ()),'toolExecutionNotifications':[]}],'results':results ,'artifacts':[{'location':{'uri':vuln .get ('filename','unknown'),'uriBaseId':'0-srcRoot'},'sourceLanguage':self ._detect_language (vuln .get ('filename',''))}for vuln in vulnerabilities ],'properties':{'scanId':scan_results .get ('scan_id','unknown'),'scanType':scan_results .get ('scan_type','1'),'projectName':scan_results .get ('project_name','unknown'),'filesScanned':scan_results .get ('stats',{}).get ('files_scanned',0 ),'vulnerabilitiesFound':len (all_findings )}}]}
        return sarif 

    def _detect_language (self ,filename :str )->str :
        ext =os .path .splitext (filename )[1 ].lower ()
        language_map ={'.py':'python','.js':'javascript','.jsx':'javascript','.ts':'typescript','.tsx':'typescript','.java':'java','.go':'go'}
        return language_map .get (ext ,'unknown')

    def emit (self ,scan_results :Dict ,output_path :str )->str :
        sarif =self .convert (scan_results )
        with open (output_path ,'w',encoding ='utf-8')as f :
            json .dump (sarif ,f ,indent =2 ,ensure_ascii =False )
        return output_path 
