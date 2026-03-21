import logging 
from typing import Any 
logger =logging .getLogger (__name__ )

def _file_from_key (key :str )->str |None :
    if '::'in key :
        return key .split ('::',1 )[0 ].replace ('\\','/')
    return key .replace ('\\','/')if key else None 

def expand_changed_files (changed_files :list [str ],dependency_map :dict [str ,list [str ]],call_graph :dict [str ,Any ],depth :int =2 )->list [str ]:
    if not changed_files :
        return []
    changed_set =set ((f .replace ('\\','/')for f in changed_files ))
    dep_map_norm :dict [str ,list [str ]]={}
    for k ,v in dependency_map .items ():
        key =k .replace ('\\','/')
        dep_map_norm [key ]=[x .replace ('\\','/')for x in (v if isinstance (v ,list )else [])]
    imported_by :dict [str ,set [str ]]={}
    for importer ,deps in dep_map_norm .items ():
        for dep in deps :
            imported_by .setdefault (dep ,set ()).add (importer )

    def file_from_key (key :str )->str |None :
        return _file_from_key (key )
    call_graph_files :dict [str ,set [str ]]={}
    for func_key ,data in call_graph .items ():
        f =file_from_key (func_key )
        if not f :
            continue 
        call_graph_files .setdefault (f ,set ())
        if isinstance (data ,dict ):
            for callee in data .get ('callees',[])or data .get ('callees_list',[]):
                c =file_from_key (callee )if isinstance (callee ,str )else None 
                if c and c !=f :
                    call_graph_files [f ].add (c )
            for caller in data .get ('called_by',[])or data .get ('callers',[]):
                c =file_from_key (caller )if isinstance (caller ,str )else None 
                if c and c !=f :
                    call_graph_files [f ].add (c )
        elif isinstance (data ,list ):
            for callee in data :
                c =file_from_key (callee )if isinstance (callee ,str )else None 
                if c and c !=f :
                    call_graph_files [f ].add (c )
    expanded :set [str ]=set (changed_set )
    current_front =set (changed_set )
    for _ in range (depth ):
        next_front :set [str ]=set ()
        for path in current_front :
            for importer in imported_by .get (path ,[]):
                if importer not in expanded :
                    expanded .add (importer )
                    next_front .add (importer )
            for dep in dep_map_norm .get (path ,[]):
                if dep not in expanded :
                    expanded .add (dep )
                    next_front .add (dep )
            for neighbor in call_graph_files .get (path ,[]):
                if neighbor not in expanded :
                    expanded .add (neighbor )
                    next_front .add (neighbor )
        current_front =next_front 
        if not current_front :
            break 
    return sorted (expanded )

def build_diff_context (file_contents :dict [str ,str ],expanded_paths :list [str ],dependency_map :dict [str ,Any ],call_graph :dict [str ,Any ])->dict [str ,Any ]:
    expanded_set =set (expanded_paths )
    contents ={k :v for k ,v in file_contents .items ()if k in expanded_set }
    deps ={k :[x for x in (v if isinstance (v ,list )else [])if x in expanded_set ]for k ,v in dependency_map .items ()if k in expanded_set }
    cg_trimmed :dict [str ,Any ]={}
    for k ,v in call_graph .items ():
        f =_file_from_key (k )
        if f not in expanded_set :
            continue 
        if isinstance (v ,dict ):
            cg_trimmed [k ]={**v ,'callees':[c for c in v .get ('callees')or []if _file_from_key (c )in expanded_set ],'called_by':[c for c in v .get ('called_by')or []if _file_from_key (c )in expanded_set ]}
        else :
            cg_trimmed [k ]=v 
    return {'file_contents':contents ,'dependency_map':deps ,'call_graph':cg_trimmed ,'expanded_paths':expanded_paths ,'changed_count':len (expanded_paths )}
