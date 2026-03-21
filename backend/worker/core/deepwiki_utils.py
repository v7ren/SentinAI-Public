from typing import List ,Dict 

def build_security_context (project_ir :Dict ,max_files :int =25 )->str :
    files =project_ir .get ('files',{})
    if not files :
        return 'No project security overview available.'
    all_concerns :List [str ]=[]
    all_entrypoints :List [dict ]=[]
    for _path ,info in files .items ():
        mc =info .get ('main_concerns')or []
        se =info .get ('suspected_entrypoints')or []
        all_concerns .extend ([str (c ).strip ()for c in mc if c ])
        all_entrypoints .extend (se )
    concerns_clean =sorted (set ((c for c in all_concerns if c )))

    def fmt_entry (ep :dict )->str :
        kind =(ep .get ('kind')or '').strip ()
        name =(ep .get ('name')or '').strip ()
        details =(ep .get ('details')or '').strip ()
        label =''
        if kind and name :
            label =f'[{kind }] {name }'
        elif name :
            label =name 
        elif kind :
            label =f'[{kind }]'
        return f'{label } – {details }'if details and label else (label or details or '').strip ()
    entrypoints_clean =[fmt_entry (ep )for ep in all_entrypoints ]
    entrypoints_clean =[e for e in entrypoints_clean if e ]
    lines :List [str ]=[]
    lines .append ('=== PROJECT SECURITY OVERVIEW ===')
    lines .append ('')
    if concerns_clean :
        lines .append ('Main concerns (deduped):')
        for c in concerns_clean [:12 ]:
            lines .append (f'  - {c }')
        lines .append ('')
    if entrypoints_clean :
        lines .append ('Sample suspected entrypoints (truncated):')
        for ep in entrypoints_clean [:10 ]:
            lines .append (f'  - {ep }')
        lines .append ('')
    lines .append ('=== FILE SUMMARIES (TRUNCATED) ===')
    for path ,info in list (files .items ())[:max_files ]:
        lines .append (f'FILE: {path }')
        fs =(info .get ('file_summary')or '').strip ()
        if len (fs )>400 :
            fs =fs [:400 ].rstrip ()+'...'
        lines .append (f'SUMMARY: {fs }')
        mc =[str (c ).strip ()for c in info .get ('main_concerns')or []if c ]
        if mc :
            lines .append ('MAIN_CONCERNS:')
            for c in mc :
                lines .append (f'  - {c }')
        else :
            lines .append ('MAIN_CONCERNS: (none detected)')
        se_list =info .get ('suspected_entrypoints')or []
        if se_list :
            lines .append ('ENTRYPOINTS:')
            for ep in se_list :
                ep_line =fmt_entry (ep )
                if ep_line :
                    lines .append (f'  - {ep_line }')
        else :
            lines .append ('ENTRYPOINTS: (none detected)')
        lines .append ('')
    return '\n'.join (lines )
