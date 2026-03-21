import json 
import os 
import sys 
import time 
from datetime import datetime ,timezone 
from urllib .request import Request ,urlopen 
from urllib .error import URLError ,HTTPError 
LOG_SERVER_URL =(os .getenv ('LOG_SERVER_URL')or 'http://127.0.0.1:5003').rstrip ('/')
BROADCAST_URL =f'{LOG_SERVER_URL }/api/broadcast'
SCAN_ID ='test-scan-'+str (int (time .time ()))

def send_event (event_type :str ,agent_name :str ,data :dict )->bool :
    payload ={'event_type':event_type ,'agent_name':agent_name ,'scan_id':SCAN_ID ,'data':{**data ,'timestamp':datetime .now (timezone .utc ).isoformat ()}}
    body =json .dumps (payload ).encode ('utf-8')
    req =Request (BROADCAST_URL ,data =body ,method ='POST',headers ={'Content-Type':'application/json'})
    try :
        with urlopen (req ,timeout =5 )as resp :
            if resp .status !=200 :
                print (f'  [!] {event_type } -> HTTP {resp .status }')
                return False 
            return True 
    except HTTPError as e :
        print (f'  [!] {event_type } -> HTTP {e .code }: {e .reason }')
        return False 
    except URLError as e :
        print (f'  [!] {event_type } -> {e .reason }')
        return False 

def main ():
    print (f'Agent Log Server Tester')
    print (f'  Log server: {LOG_SERVER_URL }')
    print (f'  Scan ID:    {SCAN_ID }')
    print ()
    print ('Sending scan_start...')
    if not send_event ('scan_start','coordinator',{'language':'python','framework':'flask','file_count':3 }):
        print ('  Failed. Is the log server running on port 5003?')
        sys .exit (1 )
    time .sleep (0.2 )
    print ('Sending agent_start (TestAgent)...')
    send_event ('agent_start','TestAgent',{'agent_type':'specialist','context':{'files':['app.py','utils/auth.py'],'entry_points':2 },'config':{'model':'test-model','max_tokens':2048 }})
    time .sleep (0.15 )
    print ('Sending agent_prompt...')
    send_event ('agent_prompt','TestAgent',{'prompt':'Analyze the following code for security issues:\n\n```python\ndef login(user, pwd):\n    query = f"SELECT * FROM users WHERE pass=\'{pwd}\'"\n    return db.execute(query)\n```','prompt_tokens':42 })
    time .sleep (0.2 )
    print ('Sending tool_call (lookup_sanitizers)...')
    send_event ('tool_call','TestAgent',{'tool_name':'lookup_sanitizers','tool_args':{},'filename':'app.py'})
    time .sleep (0.1 )
    print ('Sending tool_result...')
    send_event ('tool_result','TestAgent',{'tool_name':'lookup_sanitizers','result_preview':'Sanitizer registry: parameterized_queries: psycopg2.execute, cursor.execute','filename':'app.py'})
    time .sleep (0.1 )
    print ('Sending tool_call (fetch_file)...')
    send_event ('tool_call','TestAgent',{'tool_name':'fetch_file','tool_args':{'path':'utils/auth.py'},'filename':'app.py'})
    time .sleep (0.1 )
    print ('Sending tool_result...')
    send_event ('tool_result','TestAgent',{'tool_name':'fetch_file','result_preview':'def sanitize(s): return s.replace(\'"\', \'\') ...','filename':'app.py'})
    time .sleep (0.2 )
    print ('Sending agent_response...')
    send_event ('agent_response','TestAgent',{'response':'The code has a SQL injection risk. Use parameterized queries.','response_tokens':28 ,'latency_ms':1250 })
    time .sleep (0.1 )
    print ('Sending agent_findings...')
    send_event ('agent_findings','TestAgent',{'findings_count':1 ,'findings':[{'type':'SQL_INJECTION','line':2 ,'confidence':9.0 }]})
    time .sleep (0.1 )
    print ('Sending agent_complete...')
    send_event ('agent_complete','TestAgent',{'execution_time_ms':2100 ,'token_usage':320 ,'errors':[],'findings_count':1 })
    time .sleep (0.1 )
    print ('Sending second agent (ReconAgent)...')
    send_event ('agent_start','ReconAgent',{'agent_type':'recon','config':{}})
    time .sleep (0.05 )
    send_event ('agent_complete','ReconAgent',{'execution_time_ms':450 ,'token_usage':80 ,'errors':[],'findings_count':0 })
    print ()
    print ("Done. Open /admin and check 'Agent activity' — you should see TestAgent and ReconAgent blocks.")
    print ('  WebSocket: '+LOG_SERVER_URL .replace ('http','ws')+'/ws/logs')
    print ('  History:   '+LOG_SERVER_URL +'/api/history?limit=50')
if __name__ =='__main__':
    main ()
