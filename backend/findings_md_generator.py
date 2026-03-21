import os 
import sys 
import json 
from pathlib import Path 
_PROJECT_ROOT =Path (__file__ ).resolve ().parent .parent 
if str (_PROJECT_ROOT )not in sys .path :
    sys .path .insert (0 ,str (_PROJECT_ROOT ))
DEFAULT_SCAN_RESULTS_DIR =_PROJECT_ROOT /'backend'/'scan_results'

def _short_name (path :str )->str :
    return path .split ('/')[-1 ]if '/'in path else path .split ('\\')[-1 ]

def _format_duration (seconds :float )->str :
    if seconds <60 :
        return f'{seconds :.1f}s'
    m =int (seconds //60 )
    s =seconds %60 
    return f'{m }m {s :.1f}s'if s >=0.1 else f'{m }m'

def _format_remediation (rem :list |str |None )->str :
    if not rem :
        return ''
    if isinstance (rem ,str ):
        return rem .strip ()
    if isinstance (rem ,list ):
        lines =[]
        for item in rem :
            if isinstance (item ,str ):
                lines .append (item .strip ())
            elif isinstance (item ,dict ):
                v =item .get ('vector')or item .get ('step')or item .get ('text')or str (item )
                if v :
                    lines .append (v )
        return '\n'.join (lines )if lines else ''
    return str (rem )

def generate_findings_md (scan_data :dict ,output_path :str |Path )->None :
    output_path =Path (output_path )
    lines =[]
    scan_id =scan_data .get ('scan_id','unknown')
    ts =scan_data .get ('timestamp','')
    stats =scan_data .get ('stats',{})
    proj =(scan_data .get ('project_analysis')or {}).get ('project_info',{})or {}
    project_name =proj .get ('name','')
    framework =proj .get ('framework','')
    files_scanned =stats .get ('files_scanned',0 )
    vuln_count =stats .get ('vulnerabilities',0 )
    elapsed =stats .get ('elapsed_seconds',0 )
    total_issues =0 
    vulns =scan_data .get ('vulnerabilities',[])
    for v in vulns :
        total_issues +=len (v .get ('issues',[]))
    lines .append ('# Security Scan Findings')
    lines .append ('')
    lines .append (f'**Scan ID:** `{scan_id }` | **Date:** {ts }')
    if project_name :
        lines .append (f'**Project:** {project_name }'+(f' ({framework })'if framework else ''))
    lines .append (f'**Files Scanned:** {files_scanned } | **Total Issues:** {total_issues } across {vuln_count } files')
    lines .append (f'**Duration:** {_format_duration (elapsed )}')
    lines .append ('')
    lines .append ('---')
    lines .append ('')
    skipped_files =[v for v in vulns if (v .get ('status')or '').upper ()=='NOT_SCANNED'or v .get ('skipped')]
    if skipped_files :
        lines .append ('## Files Skipped (Cost / Risk)')
        lines .append ('')
        lines .append ('The following files were not sent to the LLM for scanning (low estimated risk). They are not marked as safe.')
        lines .append ('')
        for v in skipped_files :
            fn =v .get ('filename','unknown')
            reason =v .get ('skip_reason')or f"Risk score {v .get ('risk_score','N/A')} below threshold"
            lines .append (f'- **{_short_name (fn )}** — {reason }')
        lines .append ('')
        lines .append ('---')
        lines .append ('')
    if not vulns or total_issues ==0 :
        if not skipped_files :
            lines .append ('No vulnerabilities found.')
        else :
            lines .append ('No vulnerabilities reported for scanned files.')
        output_path .write_text ('\n'.join (lines ),encoding ='utf-8')
        return 
    severity_counts ={}
    for v in vulns :
        for i in v .get ('issues',[]):
            sev =(i .get ('severity')or 'UNKNOWN').upper ()
            if 'INFO'in sev :
                sev ='INFO'
            severity_counts [sev ]=severity_counts .get (sev ,0 )+1 
    lines .append ('## Summary by Severity')
    lines .append ('')
    lines .append ('| Severity | Count |')
    lines .append ('|----------|-------|')
    for sev in ['CRITICAL','HIGH','MEDIUM','LOW','INFO','INFORMATIONAL']:
        if sev in severity_counts :
            lines .append (f'| {sev } | {severity_counts [sev ]} |')
    lines .append (f'| **Total** | **{total_issues }** |')
    lines .append ('')
    status_counts ={}
    for v in vulns :
        for i in v .get ('issues',[]):
            st =(i .get ('validation_status')or '').lower ()
            if st in ('validated_probable_fp','unvalidated','parse_failed'):
                status_counts ['uncertain']=status_counts .get ('uncertain',0 )+1 
            elif i .get ('_fp_soft_flag')or i .get ('_below_threshold_note'):
                status_counts ['informational']=status_counts .get ('informational',0 )+1 
            else :
                status_counts ['confirmed']=status_counts .get ('confirmed',0 )+1 
    if status_counts :
        lines .append ('## Summary by Certainty')
        lines .append ('')
        lines .append ('| Certainty | Count |')
        lines .append ('|------------|-------|')
        if status_counts .get ('confirmed'):
            lines .append (f"| Confirmed / validated | {status_counts ['confirmed']} |")
        if status_counts .get ('uncertain'):
            lines .append (f"| Uncertain / likely FP | {status_counts ['uncertain']} |")
        if status_counts .get ('informational'):
            lines .append (f"| Informational / soft-flagged | {status_counts ['informational']} |")
        lines .append ('')
    lines .append ('---')
    lines .append ('')
    idx =0 
    for vuln in vulns :
        filename =vuln .get ('filename','unknown')
        issues =vuln .get ('issues',[])
        if not issues :
            continue 
        lines .append (f'## {_short_name (filename )}')
        lines .append ('')
        lines .append (f'**Path:** `{filename }`')
        lines .append ('')
        for issue in issues :
            idx +=1 
            severity =(issue .get ('severity')or 'MEDIUM').upper ()
            if 'INFO'in severity :
                severity ='INFO'
            issue_type =issue .get ('type','Unknown')
            line_num =issue .get ('line',0 )
            cwe =issue .get ('cwe_id','')
            cvss =issue .get ('cvss_score')or 0 
            cvss_str =f'{cvss :.1f}'if isinstance (cvss ,(int ,float ))else str (cvss )
            lines .append (f'### {idx }. [{severity }] {issue_type }')
            lines .append ('')
            badges =[]
            if issue .get ('validation_status'):
                badges .append (f"**Status:** {issue ['validation_status']}")
            if issue .get ('_fp_soft_flag'):
                badges .append (f"**FP filter:** {issue ['_fp_soft_flag']}")
            if issue .get ('_cross_file_flag')or issue .get ('_removal_rule'):
                flag =issue .get ('_cross_file_flag')or issue .get ('_removal_rule','')
                if flag :
                    badges .append (f'**Cross-file:** {flag }')
            if issue .get ('_below_threshold_note'):
                badges .append (f"*{issue ['_below_threshold_note']}*")
            if badges :
                lines .append (' · '.join (badges ))
                lines .append ('')
            extra =[]
            if cwe :
                extra .append (f'**CWE:** {cwe }')
            if cvss is not None and (isinstance (cvss ,(int ,float ))or str (cvss )):
                extra .append (f'**CVSS:** {cvss_str }')
            suffix =' · '.join (extra )
            lines .append (f'**File:** `{filename }` · **Line:** {line_num }'+(f' · {suffix }'if suffix else ''))
            lines .append ('')
            subtype =issue .get ('subtype','')
            if subtype :
                lines .append (f'**Subtype:** {subtype }')
                lines .append ('')
            desc =issue .get ('description','')
            if desc :
                lines .append ('**Description:**')
                lines .append (desc )
                lines .append ('')
            impact =issue .get ('impact_summary','')
            if impact :
                lines .append ('**Impact:** '+impact )
                lines .append ('')
            vcode =(issue .get ('vulnerable_code')or '').strip ()
            if vcode :
                vcode_short =vcode [:600 ]+'...'if len (vcode )>600 else vcode 
                lines .append ('**Vulnerable Code:**')
                lines .append ('```')
                lines .append (vcode_short )
                lines .append ('```')
                lines .append ('')
            rem =issue .get ('remediation')
            if rem :
                rem_text =_format_remediation (rem )
                if rem_text :
                    lines .append ('**Remediation:**')
                    lines .append ('```')
                    lines .append (rem_text )
                    lines .append ('```')
                    lines .append ('')
            fix_complexity =issue .get ('fix_complexity','')
            if fix_complexity and fix_complexity !='UNKNOWN':
                lines .append (f'**Fix Complexity:** {fix_complexity }')
                lines .append ('')
            lines .append ('---')
            lines .append ('')
    output_path .write_text ('\n'.join (lines ),encoding ='utf-8')

def generate_from_result_json (result_path :str |Path )->Path |None :
    result_path =Path (result_path )
    if not result_path .exists ():
        return None 
    if result_path .is_dir ():
        result_path =result_path /'result.json'
    if not result_path .name .endswith ('.json'):
        result_path =result_path .parent /'result.json'
    if not result_path .exists ():
        return None 
    try :
        data =json .loads (result_path .read_text (encoding ='utf-8'))
    except Exception :
        return None 
    out_path =result_path .parent /'findings.md'
    generate_findings_md (data ,out_path )
    return out_path 

def main ():
    if len (sys .argv )>1 :
        paths =sys .argv [1 :]
    else :
        if not DEFAULT_SCAN_RESULTS_DIR .exists ():
            print ('Usage: python -m backend.findings_md_generator [result.json or scan_folder]')
            sys .exit (1 )
        paths =[str (d )for d in DEFAULT_SCAN_RESULTS_DIR .iterdir ()if d .is_dir ()]
    for path in paths :
        out =generate_from_result_json (path )
        if out :
            print (f'Generated: {out }')
        else :
            print (f'Skipped (no result.json): {path }')
if __name__ =='__main__':
    main ()
