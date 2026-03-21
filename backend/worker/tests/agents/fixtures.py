from backend .worker .core .agents .models import AgentContext ,ArchPattern ,EntryPoint ,ScanMode ,ThreatModel 

def make_context (file_contents :dict [str ,str ]|None =None ,entry_points :list |None =None ,sanitizer_registry :dict |None =None ,architecture_patterns :ArchPattern |None =None ,threat_model :ThreatModel |None =None ,language :str ='python',framework :str ='flask')->AgentContext :
    return AgentContext (call_graph ={},dependency_map ={},sanitizer_registry =sanitizer_registry or {},dead_code_map ={},entry_points =entry_points or [make_entry_point ()],architecture_patterns =architecture_patterns ,threat_model =threat_model ,file_contents =file_contents or {'app.py':'# empty'},file_asts ={},scan_id ='test-scan-001',repo_path ='/tmp/test-repo',language =language ,framework =framework ,scan_mode =ScanMode .FULL ,changed_files =[])

def make_entry_point (entry_type :str ='http',file_path :str ='routes/app.py',line_number :int =10 ,handler_function :str ='index',authentication_required :bool =False )->EntryPoint :
    return EntryPoint (entry_type =entry_type ,file_path =file_path ,line_number =line_number ,function_name =handler_function ,handler_function =handler_function ,parameters =[],authentication_required =authentication_required ,authorization_required =False ,rate_limited =False ,framework ='flask')

def make_arch_pattern (middleware_order :list [str ]|None =None ,auth_middleware_files :list [str ]|None =None )->ArchPattern :
    return ArchPattern (pattern_type ='MVC',middleware_order =middleware_order or ['cors','auth','router'],auth_middleware_files =auth_middleware_files or ['middleware/auth.py'],orm_type ='sqlalchemy',template_engine ='jinja2',cors_config =None ,service_layer_files =[],repository_files =[],di_container =None )
