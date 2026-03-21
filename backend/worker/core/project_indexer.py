import json 
import re 
from typing import Dict 

class ProjectIndexer :

    def __init__ (self ):
        self .symbol_table :Dict [str ,dict ]={}
        self .call_graph :Dict [str ,list ]={}
        self .file_symbols :Dict [str ,list ]={}
        self .patterns ={'python':['(?m)^[ \\t]*def\\s+([a-zA-Z0-9_]+)\\s*\\(','(?m)^[ \\t]*class\\s+([a-zA-Z0-9_]+)'],'javascript':['function\\s+([a-zA-Z0-9_]+)\\s*\\(','class\\s+([a-zA-Z0-9_]+)','(?:const|let|var)\\s+([a-zA-Z0-9_]+)\\s*=\\s*(?:async\\s*)?(?:\\(|[a-zA-Z0-9_]+)\\s*=>','([a-zA-Z0-9_]+)\\s*:\\s*function'],'java':['(?:public|private|protected|static|\\s) +[\\w\\<\\>\\[\\]]+\\s+([a-zA-Z0-9_]+)\\s*\\(','class\\s+([a-zA-Z0-9_]+)'],'go':['func\\s+([a-zA-Z0-9_]+)\\s*\\(','func\\s+\\(.*\\)\\s+([a-zA-Z0-9_]+)\\s*\\('],'php':['function\\s+([a-zA-Z0-9_]+)\\s*\\(','class\\s+([a-zA-Z0-9_]+)']}

    def index_file (self ,filepath :str ,content :str ):
        self .remove_file (filepath )
        lang =None 
        if filepath .endswith ('.py'):
            lang ='python'
        elif filepath .endswith (('.js','.ts','.jsx','.tsx')):
            lang ='javascript'
        elif filepath .endswith ('.java'):
            lang ='java'
        elif filepath .endswith ('.go'):
            lang ='go'
        elif filepath .endswith ('.php'):
            lang ='php'
        if not lang :
            return 
        indexed_names =[]
        for pat in self .patterns [lang ]:
            for match in re .finditer (pat ,content ):
                name =match .group (1 )
                if len (name )<2 :
                    continue 
                start_index =match .start ()
                if lang =='python':
                    body_slice =content [start_index :].splitlines ()[:50 ]
                else :
                    body_slice =content [start_index :].splitlines ()[:30 ]
                code_body ='\n'.join (body_slice )
                self .symbol_table [name ]={'file':filepath ,'code':code_body ,'dependencies':[]}
                if name not in indexed_names :
                    indexed_names .append (name )
        if indexed_names :
            self .file_symbols [filepath ]=indexed_names 

    def remove_file (self ,filepath :str ):
        for symbol in self .file_symbols .pop (filepath ,[]):
            data =self .symbol_table .get (symbol )
            if data and data .get ('file')==filepath :
                self .symbol_table .pop (symbol ,None )
            self .call_graph .pop (symbol ,None )

    def list_indexed_files (self ):
        return list (self .file_symbols .keys ())

    def _populate_dependencies (self ):
        self .call_graph ={}
        all_symbols =set (self .symbol_table .keys ())
        for name ,data in self .symbol_table .items ():
            body =data ['code']
            self .call_graph [name ]=[]
            for other in all_symbols :
                if other !=name and other in body :
                    if other not in self .call_graph [name ]:
                        self .call_graph [name ].append (other )

    def get_context_for_code (self ,code_content :str ,max_depth :int =2 )->str :
        self ._populate_dependencies ()
        relevant_snippets ={}
        direct_hits =[name for name in self .symbol_table if name in code_content ]
        queue =[(name ,0 )for name in direct_hits ]
        visited =set (direct_hits )
        while queue :
            current_name ,depth =queue .pop (0 )
            if current_name in self .symbol_table :
                data =self .symbol_table [current_name ]
                relevant_snippets [current_name ]=f"--- Ref: {current_name } (Depth {depth } - {data ['file']}) ---\n{data ['code']}\n"
            if depth <max_depth :
                children =self .call_graph .get (current_name ,[])
                for child in children :
                    if child not in visited :
                        visited .add (child )
                        queue .append ((child ,depth +1 ))
        return '\n'.join (list (relevant_snippets .values ())[:6 ])

    def to_json (self )->str :
        return json .dumps ({'symbol_table':self .symbol_table ,'call_graph':self .call_graph ,'file_symbols':self .file_symbols })

    @staticmethod 
    def from_json (json_str :str )->'ProjectIndexer':
        data =json .loads (json_str )
        indexer =ProjectIndexer ()
        indexer .symbol_table =data .get ('symbol_table',{})
        indexer .call_graph =data .get ('call_graph',{})
        indexer .file_symbols =data .get ('file_symbols',{})
        return indexer 
