import hashlib 
import json 
import logging 
import os 
from dataclasses import asdict ,dataclass 
from datetime import datetime 
logger =logging .getLogger (__name__ )
FEEDBACK_RECORDS_PATH =os .path .join (os .path .dirname (__file__ ),'..','..','data','learning','feedback_records.jsonl')
SUPPRESSION_PATTERNS_PATH =os .path .join (os .path .dirname (__file__ ),'..','..','data','learning','suppression_patterns.json')
CONFIDENCE_CALIBRATION_PATH =os .path .join (os .path .dirname (__file__ ),'..','..','data','learning','confidence_calibration.json')

@dataclass 
class FeedbackRecord :
    finding_id :str 
    scan_id :str 
    analyst_verdict :str 
    analyst_notes :str 
    codebase_fingerprint :str 
    agent_source :str 
    vulnerability_class :str 
    timestamp :str 

class LearningAgent :

    def __init__ (self ,feedback_path :str |None =None ,suppression_path :str |None =None ,calibration_path :str |None =None ):
        self .feedback_path =feedback_path or FEEDBACK_RECORDS_PATH 
        self .suppression_path =suppression_path or SUPPRESSION_PATTERNS_PATH 
        self .calibration_path =calibration_path or CONFIDENCE_CALIBRATION_PATH 
        self ._ensure_data_dir ()

    def _ensure_data_dir (self )->None :
        d =os .path .dirname (self .feedback_path )
        if d :
            os .makedirs (d ,exist_ok =True )

    def record_feedback (self ,feedback :FeedbackRecord )->None :
        self ._ensure_data_dir ()
        line =json .dumps (asdict (feedback ))+'\n'
        with open (self .feedback_path ,'a',encoding ='utf-8')as f :
            f .write (line )
        logger .info ('Recorded feedback for finding %s',feedback .finding_id )

    def get_suppression_patterns (self ,codebase_fingerprint :str )->list [str ]:
        if not os .path .isfile (self .suppression_path ):
            return []
        try :
            with open (self .suppression_path ,'r',encoding ='utf-8')as f :
                data =json .load (f )
            return data .get (codebase_fingerprint ,[])
        except (json .JSONDecodeError ,OSError ):
            return []

    def get_confidence_calibration (self ,agent_name :str ,vuln_class :str )->float :
        if not os .path .isfile (self .calibration_path ):
            return 1.0 
        try :
            with open (self .calibration_path ,'r',encoding ='utf-8')as f :
                data =json .load (f )
            key =f'{agent_name }:{vuln_class }'
            return float (data .get (key ,1.0 ))
        except (json .JSONDecodeError ,OSError ,TypeError ):
            return 1.0 

    def rebuild_patterns (self )->None :
        self ._ensure_data_dir ()
        records :list [FeedbackRecord ]=[]
        if os .path .isfile (self .feedback_path ):
            with open (self .feedback_path ,'r',encoding ='utf-8')as f :
                for line in f :
                    line =line .strip ()
                    if not line :
                        continue 
                    try :
                        d =json .loads (line )
                        records .append (FeedbackRecord (finding_id =d .get ('finding_id',''),scan_id =d .get ('scan_id',''),analyst_verdict =d .get ('analyst_verdict',''),analyst_notes =d .get ('analyst_notes',''),codebase_fingerprint =d .get ('codebase_fingerprint',''),agent_source =d .get ('agent_source',''),vulnerability_class =d .get ('vulnerability_class',''),timestamp =d .get ('timestamp','')))
                    except (json .JSONDecodeError ,KeyError ,TypeError ):
                        continue 
        fp_by_fingerprint :dict [str ,list [tuple [str ,str ]]]={}
        for r in records :
            if r .analyst_verdict !='false_positive':
                continue 
            fp_by_fingerprint .setdefault (r .codebase_fingerprint ,[]).append ((r .agent_source ,r .vulnerability_class ))
        suppression :dict [str ,list [str ]]={}
        for fp ,pairs in fp_by_fingerprint .items ():
            patterns =list ({f'{a }:{v }'for a ,v in pairs })
            suppression [fp ]=patterns 
        with open (self .suppression_path ,'w',encoding ='utf-8')as f :
            json .dump (suppression ,f ,indent =2 )
        agent_vuln_counts :dict [str ,list [str ]]={}
        for r in records :
            key =f'{r .agent_source }:{r .vulnerability_class }'
            agent_vuln_counts .setdefault (key ,[]).append (r .analyst_verdict )
        calibration :dict [str ,float ]={}
        for key ,verdicts in agent_vuln_counts .items ():
            fp_count =sum ((1 for v in verdicts if v =='false_positive'))
            total =len (verdicts )
            if total >=3 and fp_count /total >0.5 :
                calibration [key ]=0.9 
            else :
                calibration [key ]=1.0 
        with open (self .calibration_path ,'w',encoding ='utf-8')as f :
            json .dump (calibration ,f ,indent =2 )
        logger .info ('Rebuilt suppression patterns and confidence calibration from %d records',len (records ))
