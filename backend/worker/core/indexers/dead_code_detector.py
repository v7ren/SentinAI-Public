import os 
import re 
import json 
from typing import Dict ,List ,Set 
from ..redis_client import redis_client ,REDIS_AVAILABLE 
from ..config import SCAN_TTL ,logger 

class DeadCodeDetector :
    TEST_FILE_PATTERNS =['^test_','_test\\.py$','_test\\.js$','_test\\.ts$','\\.test\\.js$','\\.test\\.ts$','\\.test\\.tsx$','\\.test\\.jsx$','\\.spec\\.js$','\\.spec\\.ts$','\\.spec\\.tsx$','\\.spec\\.jsx$','^tests?/','/tests?/','__tests__/','spec/','/spec/']
    MIGRATION_PATTERNS =['migration','seed','fixture','mock','factory','populate']

    def __init__ (self ):
        self .dead_code_map :Dict [str ,Dict ]={}

    def _is_test_file (self ,filepath :str )->bool :
        for pattern in self .TEST_FILE_PATTERNS :
            if re .search (pattern ,filepath ,re .IGNORECASE ):
                return True 
        return False 

    def _is_migration_file (self ,filepath :str )->bool :
        for pattern in self .MIGRATION_PATTERNS :
            if re .search (pattern ,filepath ,re .IGNORECASE ):
                return True 
        return False 

    def _count_inbound_calls (self ,func_key :str ,call_graph :Dict )->int :
        count =0 
        for other_key ,other_data in call_graph .items ():
            if func_key in other_data .get ('calls',[]):
                count +=1 
        return count 

    def _get_callers (self ,func_key :str ,call_graph :Dict )->List [str ]:
        callers =[]
        for other_key ,other_data in call_graph .items ():
            if func_key in other_data .get ('calls',[]):
                callers .append (other_key )
        return callers 

    def _get_caller_files (self ,callers :List [str ])->List [str ]:
        files =set ()
        for caller in callers :
            if '::'in caller :
                file_path =caller .split ('::')[0 ]
                files .add (file_path )
        return list (files )

    def build (self ,project_path :str ,scan_id :str ,call_graph :Dict )->Dict :
        logger .info (f'[{scan_id }] Analyzing dead code...')
        for func_key ,func_data in call_graph .items ():
            file_path =func_data .get ('file','')
            is_entry_point =func_data .get ('is_entry_point',False )
            is_test =func_data .get ('is_test',False )
            if is_entry_point :
                self .dead_code_map [func_key ]={'inbound_call_count':-1 ,'is_dead':False ,'is_test_only':False ,'is_entry_point':True ,'called_from_files':[]}
                continue 
            inbound_count =self ._count_inbound_calls (func_key ,call_graph )
            callers =self ._get_callers (func_key ,call_graph )
            caller_files =self ._get_caller_files (callers )
            is_dead =inbound_count ==0 
            is_test_only =False 
            if not is_dead :
                all_callers_are_tests =all ((self ._is_test_file (f )for f in caller_files ))
                if all_callers_are_tests :
                    is_test_only =True 
            if self ._is_test_file (file_path )or self ._is_migration_file (file_path ):
                is_test_only =True 
            self .dead_code_map [func_key ]={'inbound_call_count':inbound_count ,'is_dead':is_dead ,'is_test_only':is_test_only ,'is_entry_point':False ,'called_from_files':caller_files }
        if REDIS_AVAILABLE :
            try :
                redis_client .setex (f'{scan_id }:dead_code_map',SCAN_TTL ,json .dumps (self .dead_code_map ))
                logger .info (f'[{scan_id }] Dead code map stored in Redis')
            except Exception as e :
                logger .error (f'[{scan_id }] Failed to store dead_code_map in Redis: {e }')
        else :
            logger .warning (f'[{scan_id }] Redis not available, dead_code_map not persisted')
        dead_count =sum ((1 for v in self .dead_code_map .values ()if v .get ('is_dead')))
        test_only_count =sum ((1 for v in self .dead_code_map .values ()if v .get ('is_test_only')))
        entry_point_count =sum ((1 for v in self .dead_code_map .values ()if v .get ('is_entry_point')))
        logger .info (f'[{scan_id }] DeadCodeDetector complete: {dead_count } dead functions, {test_only_count } test-only, {entry_point_count } entry points')
        return self .dead_code_map 
