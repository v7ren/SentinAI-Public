import os 
import sys 
sys .path .insert (0 ,os .path .dirname (os .path .dirname (os .path .dirname (os .path .dirname (__file__ )))))
from backend .worker .core .log_server import run_server 
if __name__ =='__main__':
    import argparse 
    parser =argparse .ArgumentParser (description ='Start the SentinAI Agent Log Server')
    parser .add_argument ('--port','-p',type =int ,default =None ,help ='Port to run the server on (default: 5003)')
    parser .add_argument ('--host','-H',type =str ,default ='0.0.0.0',help ='Host to bind to (default: 0.0.0.0)')
    args =parser .parse_args ()
    run_server (port =args .port ,host =args .host )
