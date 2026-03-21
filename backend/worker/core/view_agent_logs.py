import argparse 
import json 
from pathlib import Path 
from datetime import datetime 
from typing import Dict ,List ,Any 
LOG_DIR =Path (__file__ ).parent .parent .parent /'worker'/'data'/'agent_logs'

def list_logs ():
    if not LOG_DIR .exists ():
        print (f'❌ Log directory not found: {LOG_DIR }')
        return 
    log_files =sorted (LOG_DIR .glob ('agent_log_*.jsonl'))
    if not log_files :
        print ('No log files found.')
        return 
    print (f'\n📁 Found {len (log_files )} log file(s) in: {LOG_DIR }\n')
    print (f"{'Scan ID':<40} {'Timestamp':<20} {'Entries':<10}")
    print ('-'*70 )
    for log_file in log_files :
        parts =log_file .stem .replace ('agent_log_','').rsplit ('_',1 )
        if len (parts )==2 :
            scan_id ,timestamp =parts 
            try :
                dt =datetime .fromtimestamp (int (timestamp ))
                timestamp_str =dt .strftime ('%Y-%m-%d %H:%M:%S')
            except :
                timestamp_str ='Unknown'
        else :
            scan_id =log_file .stem 
            timestamp_str ='Unknown'
        with open (log_file ,'r',encoding ='utf-8')as f :
            entry_count =sum ((1 for _ in f ))
        print (f'{scan_id :<40} {timestamp_str :<20} {entry_count :<10}')

def load_log_entries (scan_id :str )->List [Dict [str ,Any ]]:
    log_files =list (LOG_DIR .glob (f'agent_log_{scan_id }_*.jsonl'))
    if not log_files :
        log_files =list (LOG_DIR .glob (f'agent_log_{scan_id }*.jsonl'))
    if not log_files :
        print (f'❌ No log file found for scan: {scan_id }')
        return []
    entries =[]
    with open (log_files [0 ],'r',encoding ='utf-8')as f :
        for line in f :
            entries .append (json .loads (line ))
    return entries 

def view_summary (scan_id :str ):
    summary_files =list (LOG_DIR .glob (f'agent_summary_{scan_id }*.json'))
    if not summary_files :
        print (f'❌ No summary file found for scan: {scan_id }')
        return 
    with open (summary_files [0 ],'r',encoding ='utf-8')as f :
        summary =json .load (f )
    print (f"\n{'='*70 }")
    print (f'📊 SCAN SUMMARY: {scan_id }')
    print (f"{'='*70 }\n")
    print (f"Start Time:        {summary .get ('start_time','N/A')}")
    print (f"End Time:          {summary .get ('end_time','N/A')}")
    print (f"Total Time:        {summary .get ('total_time_ms',0 )/1000 :.2f}s")
    print (f"Total Entries:     {summary .get ('total_entries',0 )}")
    print (f"Log File:          {summary .get ('log_file','N/A')}")
    print (f"\n{'─'*70 }")
    print ('📈 EVENT COUNTS:')
    print (f"{'─'*70 }\n")
    event_counts =summary .get ('event_counts',{})
    for event_type ,count in sorted (event_counts .items ()):
        print (f'  {event_type :<25} {count :>5}')
    print (f"\n{'─'*70 }")
    print ('🤖 AGENT PERFORMANCE:')
    print (f"{'─'*70 }\n")
    agent_summary =summary .get ('agent_summary',{})
    print (f"{'Agent':<25} {'Time (ms)':<12} {'Tokens':<10} {'Findings':<10} {'Errors'}")
    print ('-'*70 )
    for agent_name ,stats in agent_summary .items ():
        exec_time =stats .get ('execution_time_ms',0 )
        tokens =stats .get ('token_usage',0 )
        findings =stats .get ('findings_count',0 )
        errors =len (stats .get ('errors',[]))
        print (f'{agent_name :<25} {exec_time :<12} {tokens :<10} {findings :<10} {errors }')
    print (f"\n{'─'*70 }")
    print ('📋 FINAL STATS:')
    print (f"{'─'*70 }\n")
    final_stats =summary .get ('final_stats',{})
    for key ,value in final_stats .items ():
        print (f'  {key :<25} {value }')

def view_timeline (scan_id :str ):
    entries =load_log_entries (scan_id )
    if not entries :
        return 
    print (f"\n{'='*70 }")
    print (f'⏱️  EVENT TIMELINE: {scan_id }')
    print (f"{'='*70 }\n")
    for entry in entries :
        event_type =entry .get ('event_type','unknown')
        elapsed_ms =entry .get ('elapsed_ms',0 )
        seq =entry .get ('seq',0 )
        if event_type =='scan_start':
            print (f'[{seq :>3}] {elapsed_ms :>6}ms | 🚀 Scan started')
        elif event_type =='scan_complete':
            print (f"[{seq :>3}] {elapsed_ms :>6}ms | ✅ Scan completed ({entry .get ('total_time_ms',0 )}ms total)")
        elif event_type =='agent_start':
            agent_name =entry .get ('agent_name','Unknown')
            print (f'[{seq :>3}] {elapsed_ms :>6}ms | ▶️  {agent_name } started')
        elif event_type =='agent_complete':
            agent_name =entry .get ('agent_name','Unknown')
            findings =entry .get ('findings_count',0 )
            errors =len (entry .get ('errors',[]))
            print (f'[{seq :>3}] {elapsed_ms :>6}ms | ⏹️  {agent_name } completed ({findings } findings, {errors } errors)')
        elif event_type =='phase_transition':
            from_phase =entry .get ('from_phase','?')
            to_phase =entry .get ('to_phase','?')
            print (f'[{seq :>3}] {elapsed_ms :>6}ms | 🔄 Phase: {from_phase } → {to_phase }')
        elif event_type =='error':
            agent_name =entry .get ('agent_name','Unknown')
            error_type =entry .get ('error_type','Unknown')
            print (f'[{seq :>3}] {elapsed_ms :>6}ms | ❌ ERROR in {agent_name }: {error_type }')
        elif event_type =='deduplication':
            input_count =entry .get ('input_findings',0 )
            output_count =entry .get ('output_findings',0 )
            ratio =entry .get ('deduplication_ratio',0 )
            print (f'[{seq :>3}] {elapsed_ms :>6}ms | 🔍 Deduplication: {input_count } → {output_count } ({ratio :.1f}% reduction)')
        elif event_type =='skeptic_review':
            reviewed =entry .get ('findings_reviewed',0 )
            confirmed =entry .get ('confirmed',0 )
            downgraded =entry .get ('downgraded',0 )
            rejected =entry .get ('rejected',0 )
            print (f'[{seq :>3}] {elapsed_ms :>6}ms | 🎯 Skeptic: {reviewed } reviewed (✓{confirmed } ↓{downgraded } ✗{rejected })')
        else :
            print (f'[{seq :>3}] {elapsed_ms :>6}ms | 📌 {event_type }')

def view_errors (scan_id :str ):
    entries =load_log_entries (scan_id )
    if not entries :
        return 
    errors =[e for e in entries if e .get ('event_type')=='error']
    if not errors :
        print (f'\n✅ No errors found for scan: {scan_id }\n')
        return 
    print (f"\n{'='*70 }")
    print (f'❌ ERRORS: {scan_id } ({len (errors )} total)')
    print (f"{'='*70 }\n")
    for i ,error in enumerate (errors ,1 ):
        print (f"\n{'─'*70 }")
        print (f'Error #{i }')
        print (f"{'─'*70 }\n")
        print (f"Agent:        {error .get ('agent_name','Unknown')}")
        print (f"Type:         {error .get ('error_type','Unknown')}")
        print (f"Message:      {error .get ('error_message','N/A')}")
        print (f"Elapsed:      {error .get ('elapsed_ms',0 )}ms")
        if error .get ('stack_trace'):
            print (f'\nStack Trace:')
            print (error ['stack_trace'])

def view_agents (scan_id :str ):
    entries =load_log_entries (scan_id )
    if not entries :
        return 
    agent_completions =[e for e in entries if e .get ('event_type')=='agent_complete']
    if not agent_completions :
        print (f'\n⚠️  No agent completions found for scan: {scan_id }\n')
        return 
    print (f"\n{'='*70 }")
    print (f'🤖 AGENT PERFORMANCE: {scan_id }')
    print (f"{'='*70 }\n")
    print (f"{'Agent':<25} {'Time (ms)':<12} {'Tokens':<10} {'Findings':<10} {'Errors'}")
    print ('-'*70 )
    for entry in agent_completions :
        agent_name =entry .get ('agent_name','Unknown')
        exec_time =entry .get ('execution_time_ms',0 )
        tokens =entry .get ('token_usage',0 )
        findings =entry .get ('findings_count',0 )
        errors =len (entry .get ('errors',[]))
        error_indicator =f'❌ {errors }'if errors >0 else '✓'
        print (f'{agent_name :<25} {exec_time :<12} {tokens :<10} {findings :<10} {error_indicator }')
    total_time =sum ((e .get ('execution_time_ms',0 )for e in agent_completions ))
    total_tokens =sum ((e .get ('token_usage',0 )for e in agent_completions ))
    total_findings =sum ((e .get ('findings_count',0 )for e in agent_completions ))
    print ('-'*70 )
    print (f"{'TOTAL':<25} {total_time :<12} {total_tokens :<10} {total_findings :<10}")

def view_findings (scan_id :str ):
    entries =load_log_entries (scan_id )
    if not entries :
        return 
    findings_events =[e for e in entries if e .get ('event_type')=='agent_findings']
    if not findings_events :
        print (f'\n⚠️  No findings found for scan: {scan_id }\n')
        return 
    print (f"\n{'='*70 }")
    print (f'🔍 FINDINGS: {scan_id }')
    print (f"{'='*70 }\n")
    for event in findings_events :
        agent_name =event .get ('agent_name','Unknown')
        findings =event .get ('findings',[])
        print (f"\n{'─'*70 }")
        print (f'Agent: {agent_name } ({len (findings )} findings)')
        print (f"{'─'*70 }\n")
        for i ,finding in enumerate (findings ,1 ):
            vuln_class =finding .get ('vulnerability_class','Unknown')
            file_path =finding .get ('file_path','Unknown')
            line_start =finding .get ('line_start',0 )
            line_end =finding .get ('line_end',0 )
            severity =finding .get ('severity','Unknown')
            confidence =finding .get ('confidence',0 )
            cwe_id =finding .get ('cwe_id','')
            print (f'{i }. [{severity .upper ()}] {vuln_class }')
            print (f'   File: {file_path }:{line_start }-{line_end }')
            if cwe_id :
                print (f'   CWE: {cwe_id }')
            print (f'   Confidence: {confidence :.2f}')
            reasoning =finding .get ('reasoning','')
            if reasoning :
                preview =reasoning [:150 ]+'...'if len (reasoning )>150 else reasoning 
                print (f'   Reasoning: {preview }')
            print ()

def main ():
    parser =argparse .ArgumentParser (description ='View and analyze agent logs',formatter_class =argparse .RawDescriptionHelpFormatter ,epilog ='\nExamples:\n    python view_agent_logs.py list\n    python view_agent_logs.py summary scan_user123_1710237600\n    python view_agent_logs.py timeline scan_user123_1710237600\n    python view_agent_logs.py errors scan_user123_1710237600\n    python view_agent_logs.py agents scan_user123_1710237600\n    python view_agent_logs.py findings scan_user123_1710237600\n        ')
    subparsers =parser .add_subparsers (dest ='command',help ='Command to run')
    subparsers .add_parser ('list',help ='List all log files')
    parser_summary =subparsers .add_parser ('summary',help ='View scan summary')
    parser_summary .add_argument ('scan_id',help ='Scan ID to view')
    parser_timeline =subparsers .add_parser ('timeline',help ='View event timeline')
    parser_timeline .add_argument ('scan_id',help ='Scan ID to view')
    parser_errors =subparsers .add_parser ('errors',help ='View all errors')
    parser_errors .add_argument ('scan_id',help ='Scan ID to view')
    parser_agents =subparsers .add_parser ('agents',help ='View agent performance')
    parser_agents .add_argument ('scan_id',help ='Scan ID to view')
    parser_findings =subparsers .add_parser ('findings',help ='View all findings')
    parser_findings .add_argument ('scan_id',help ='Scan ID to view')
    args =parser .parse_args ()
    if not args .command :
        parser .print_help ()
        return 
    if args .command =='list':
        list_logs ()
    elif args .command =='summary':
        view_summary (args .scan_id )
    elif args .command =='timeline':
        view_timeline (args .scan_id )
    elif args .command =='errors':
        view_errors (args .scan_id )
    elif args .command =='agents':
        view_agents (args .scan_id )
    elif args .command =='findings':
        view_findings (args .scan_id )
if __name__ =='__main__':
    main ()
