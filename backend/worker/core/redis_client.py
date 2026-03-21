import redis 
from .config import REDIS_HOST ,REDIS_PORT ,REDIS_OPTIONAL ,logger 
try :
    redis_client =redis .Redis (host =REDIS_HOST ,port =REDIS_PORT ,db =0 ,decode_responses =True )
    redis_client .ping ()
    REDIS_AVAILABLE =True 
except Exception as e :
    REDIS_AVAILABLE =False 
    logger .error ("REDIS CONNECTION FAILED: Cannot connect to Redis at %s:%s. Error: %s. Start Redis (e.g. 'redis-server' or 'docker run -p 6379:6379 redis') or set REDIS_HOST/REDIS_PORT if Redis runs elsewhere.",REDIS_HOST ,REDIS_PORT ,e )
    if REDIS_OPTIONAL :
        logger .warning ('REDIS_OPTIONAL=1: Falling back to in-memory MockRedis. Index data (file_deps, call_graph, sanitizer_registry, dead_code_map) will NOT persist. Enrichment pipeline will be blind.')

        class MockRedis :

            def __init__ (self ):
                self .store ={}

            def get (self ,key ):
                return self .store .get (key )

            def setex (self ,key ,time ,value ):
                self .store [key ]=value 

            def ping (self ):
                return True 
        redis_client =MockRedis ()
    else :
        raise SystemExit (f"\nFATAL: Redis is required but unavailable.\n  Host: {REDIS_HOST }:{REDIS_PORT }\n  Error: {e }\n\nFix: Start Redis (e.g. 'redis-server' or 'docker run -d -p 6379:6379 redis')\n  or set REDIS_HOST/REDIS_PORT in .env if Redis runs elsewhere.\n  Set REDIS_OPTIONAL=1 only for unit tests (enrichment will be disabled).\n")
