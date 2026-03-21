from typing import Dict ,List 

class MultiSignalConfidenceScorer :
    WEIGHTS ={'taint_hint_present':0.25 ,'sanitizer_registry_clear':0.25 ,'tier1_exploitable':0.2 ,'tier23_confirmed':0.2 ,'skeptic_survived':0.1 ,'entrypoint_source_confirmed':0.1 }
    SEVERITY_BANDS =[(0 ,40 ,'INFORMATIONAL'),(40 ,60 ,'LOW'),(60 ,75 ,'MEDIUM'),(75 ,90 ,'HIGH'),(90 ,100 ,'CRITICAL')]

    def __init__ (self ):
        pass 

    def score (self ,finding :Dict )->Dict :
        signals_present =[]
        weighted_score =0.0 
        if finding .get ('tainted_variable'):
            signals_present .append ('taint_hint_present')
            weighted_score +=self .WEIGHTS ['taint_hint_present']
        if finding .get ('sanitizers_checked')and (not finding .get ('sanitizer_blocked')):
            signals_present .append ('sanitizer_registry_clear')
            weighted_score +=self .WEIGHTS ['sanitizer_registry_clear']
        tier1_confidence =finding .get ('confidence_score',0 )
        if tier1_confidence <=1.0 and tier1_confidence >0 :
            tier1_confidence =tier1_confidence *100 
        if tier1_confidence >=70 :
            signals_present .append ('tier1_exploitable')
            weighted_score +=self .WEIGHTS ['tier1_exploitable']
        if finding .get ('tier1_was_correct'):
            signals_present .append ('tier23_confirmed')
            weighted_score +=self .WEIGHTS ['tier23_confirmed']
        if finding .get ('skeptic_passed'):
            signals_present .append ('skeptic_survived')
            weighted_score +=self .WEIGHTS ['skeptic_survived']
        if finding .get ('source_is_public_entry')or finding .get ('distance_to_entry_point')==0 :
            signals_present .append ('entrypoint_source_confirmed')
            weighted_score +=self .WEIGHTS ['entrypoint_source_confirmed']
        max_possible =sum (self .WEIGHTS .values ())
        normalized_score =min (100.0 ,weighted_score /max_possible *100.0 )
        normalized_score =max (30.0 ,normalized_score )
        distance =finding .get ('distance_to_entry_point')
        if isinstance (distance ,int ):
            if distance <=2 :
                normalized_score =min (100.0 ,normalized_score +8.0 )
            elif distance >=5 :
                normalized_score =max (20.0 ,normalized_score -8.0 )
        if finding .get ('is_dead'):
            normalized_score =max (15.0 ,normalized_score -20.0 )
        elif finding .get ('is_test_only'):
            normalized_score =max (20.0 ,normalized_score -15.0 )
        severity ='LOW'
        for low ,high ,sev in self .SEVERITY_BANDS :
            if low <=normalized_score <=high :
                severity =sev 
                break 
        at_floor =normalized_score <=40.0 
        cvss =finding .get ('cvss_score')
        if at_floor and cvss is not None and isinstance (cvss ,(int ,float )):
            try :
                cvss_f =float (cvss )
                if cvss_f >=9.0 :
                    severity ='CRITICAL'
                elif cvss_f >=7.0 :
                    severity ='HIGH'
                elif cvss_f >=4.0 :
                    severity ='MEDIUM'
                elif cvss_f >=0.1 :
                    severity ='LOW'
            except (TypeError ,ValueError ):
                pass 
        if finding .get ('is_dead')or finding .get ('is_test_only'):
            severity_order =['INFORMATIONAL','LOW','MEDIUM','HIGH','CRITICAL']
            try :
                idx =severity_order .index (severity )
                severity =severity_order [max (0 ,idx -1 )]
            except ValueError :
                pass 
        finding ['confidence_score']=round (normalized_score )
        finding ['severity']=severity 
        finding ['signals_present']=signals_present 
        finding ['_confidence_scale']='0-100 (percentage)'
        return finding 

    def score_all (self ,findings :List [Dict ])->List [Dict ]:
        return [self .score (f )for f in findings ]
