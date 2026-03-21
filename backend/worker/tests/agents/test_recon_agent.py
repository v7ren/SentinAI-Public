import pytest 
from backend .worker .core .agents .models import AgentContext ,EntryParameter ,EntryPoint 
from backend .worker .core .agents .recon_agent import ReconAgent 

class TestReconAgent :

    @pytest .fixture 
    def recon_agent (self ):
        return ReconAgent (name ='ReconAgent',llm_client =None ,max_retries =3 ,timeout_seconds =120 )

    @pytest .fixture 
    def mock_context (self ):
        return AgentContext (scan_id ='test-scan',repo_path ='/test/repo',language ='python',framework ='flask',file_contents ={'routes/api.py':"\nfrom flask import Flask, request\n\napp = Flask(__name__)\n\n@app.route('/login', methods=['POST'])\ndef login():\n    username = request.form['username']\n    password = request.form['password']\n    return authenticate(username, password)\n\n@app.route('/users/<int:user_id>')\ndef get_user(user_id):\n    return fetch_user(user_id)\n"})

    def test_recon_agent_init (self ):
        agent =ReconAgent (name ='TestRecon',llm_client =None )
        assert agent .name =='TestRecon'

    def test_build_prompt (self ,recon_agent ,mock_context ):
        prompt =recon_agent .build_prompt (mock_context )
        assert 'penetration tester'in prompt .lower ()
        assert 'entry point'in prompt .lower ()
        assert 'python'in prompt 
        assert 'flask'in prompt 

    def test_detect_entry_points_from_patterns (self ,recon_agent ,mock_context ):
        entry_points =recon_agent .detect_entry_points_from_patterns (mock_context )
        assert len (entry_points )>=1 

    def test_scan_file_for_entry_points (self ,recon_agent ):
        content ="\nfrom flask import Flask, request\n\napp = Flask(__name__)\n\n@app.route('/login', methods=['POST'])\ndef login():\n    username = request.form['username']\n    return username\n"
        entry_points =recon_agent ._scan_file_for_entry_points ('routes/api.py',content ,mock_context )
        assert len (entry_points )>=1 
        assert entry_points [0 ].entry_type =='http'
        assert entry_points [0 ].function_name =='login'

    def test_identify_taint_source (self ,recon_agent ):
        ep_data ={'entry_type':'http','parameters':['username','password']}
        source =recon_agent ._identify_taint_source (ep_data )
        assert source =='req.username'

    def test_entry_point_with_no_params (self ,recon_agent ):
        ep_data ={'entry_type':'http','parameters':[]}
        source =recon_agent ._identify_taint_source (ep_data )
        assert source =='req.body'

class TestReconAgentEntryPoints :

    def test_create_http_entry_point (self ):
        ep =EntryPoint (entry_type ='http',file_path ='routes/api.py',line_number =42 ,function_name ='login',handler_function ='handle_login',parameters =['username','password'],authentication_required =False ,authorization_required =False ,rate_limited =True ,framework ='flask')
        assert ep .entry_type =='http'
        assert ep .file_path =='routes/api.py'
        assert ep .authentication_required is False 
        assert ep .rate_limited is True 

    def test_create_cli_entry_point (self ):
        ep =EntryPoint (entry_type ='cli',file_path ='cli/commands.py',line_number =10 ,function_name ='main',handler_function ='process_command',parameters =['command','args'],authentication_required =False ,authorization_required =False ,rate_limited =False ,framework ='click')
        assert ep .entry_type =='cli'
        assert ep .function_name =='main'

    def test_create_webhook_entry_point (self ):
        ep =EntryPoint (entry_type ='webhook',file_path ='webhooks/paypal.py',line_number =25 ,function_name ='handle_webhook',handler_function ='process_paypal_webhook',parameters =['webhook_id','data'],authentication_required =True ,authorization_required =False ,rate_limited =True ,framework ='flask')
        assert ep .entry_type =='webhook'
        assert ep .authentication_required is True 

class TestReconAgentFrameworkDetection :

    @pytest .fixture 
    def recon_agent (self ):
        return ReconAgent (name ='ReconAgent',llm_client =None )

    def test_flask_patterns (self ,recon_agent ):
        content ='@app.route("/login")'
        matches =recon_agent .FRAMEWORK_PATTERNS ['python']['flask'][0 ]
        import re 
        result =re .search (matches ,content ,re .IGNORECASE )
        assert result is not None 

    def test_express_patterns (self ,recon_agent ):
        content ="app.get('/login', handler)"
        matches =recon_agent .FRAMEWORK_PATTERNS ['javascript']['express'][0 ]
        import re 
        result =re .search (matches ,content ,re .IGNORECASE )
        assert result is not None 
if __name__ =='__main__':
    pytest .main ([__file__ ,'-v'])
