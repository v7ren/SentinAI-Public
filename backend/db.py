import os 
import sqlite3 
from pathlib import Path 
from typing import Any ,Dict ,List ,Optional 
from contextlib import contextmanager 
_DB_PATH :Optional [Path ]=None 

def _get_db_path ()->Path :
    global _DB_PATH 
    if _DB_PATH is not None :
        return _DB_PATH 
    path =os .getenv ('DATABASE_PATH')
    if path :
        _DB_PATH =Path (path )
    else :
        _DB_PATH =Path (__file__ ).resolve ().parent /'app.db'
    return _DB_PATH 

@contextmanager 
def get_conn ():
    path =_get_db_path ()
    path .parent .mkdir (parents =True ,exist_ok =True )
    conn =sqlite3 .connect (str (path ))
    conn .row_factory =sqlite3 .Row 
    try :
        yield conn 
        conn .commit ()
    finally :
        conn .close ()

def init_db ()->None :
    with get_conn ()as conn :
        conn .executescript ("\n            CREATE TABLE IF NOT EXISTS user_memory (\n                email TEXT PRIMARY KEY,\n                memory TEXT,\n                updated_at TEXT DEFAULT (datetime('now'))\n            );\n            CREATE TABLE IF NOT EXISTS chats (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                user_email TEXT NOT NULL,\n                title TEXT NOT NULL DEFAULT 'New chat',\n                created_at TEXT DEFAULT (datetime('now')),\n                updated_at TEXT DEFAULT (datetime('now'))\n            );\n            CREATE INDEX IF NOT EXISTS idx_chats_user ON chats(user_email);\n            CREATE TABLE IF NOT EXISTS messages (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                chat_id INTEGER NOT NULL,\n                role TEXT NOT NULL,\n                content TEXT NOT NULL,\n                highlights TEXT,\n                created_at TEXT DEFAULT (datetime('now')),\n                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE\n            );\n            CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id);\n        ")

def get_user_memory (email :str )->Optional [str ]:
    if not (email or '').strip ():
        return None 
    email =email .strip ().lower ()
    with get_conn ()as conn :
        row =conn .execute ('SELECT memory FROM user_memory WHERE email = ?',(email ,)).fetchone ()
    return row ['memory']if row and row ['memory']else None 

def set_user_memory (email :str ,memory :str )->None :
    if not (email or '').strip ():
        return 
    email =email .strip ().lower ()
    with get_conn ()as conn :
        conn .execute ("INSERT INTO user_memory (email, memory, updated_at)\n               VALUES (?, ?, datetime('now'))\n               ON CONFLICT(email) DO UPDATE SET memory = excluded.memory, updated_at = datetime('now')",(email ,(memory or '').strip ()))

def list_chats (user_email :str )->List [Dict [str ,Any ]]:
    if not (user_email or '').strip ():
        return []
    user_email =user_email .strip ().lower ()
    with get_conn ()as conn :
        rows =conn .execute ('SELECT id, user_email, title, created_at, updated_at\n               FROM chats WHERE user_email = ? ORDER BY updated_at DESC',(user_email ,)).fetchall ()
    return [dict (r )for r in rows ]

def create_chat (user_email :str ,title :str ='New chat')->Dict [str ,Any ]:
    user_email =(user_email or '').strip ().lower ()
    if not user_email :
        raise ValueError ('user_email required')
    title =(title or 'New chat').strip ()or 'New chat'
    with get_conn ()as conn :
        cur =conn .execute ('INSERT INTO chats (user_email, title) VALUES (?, ?)',(user_email ,title ))
        chat_id =cur .lastrowid 
        row =conn .execute ('SELECT id, user_email, title, created_at, updated_at FROM chats WHERE id = ?',(chat_id ,)).fetchone ()
    return dict (row )

def get_chat (chat_id :int ,user_email :str )->Optional [Dict [str ,Any ]]:
    if not (user_email or '').strip ():
        return None 
    user_email =user_email .strip ().lower ()
    with get_conn ()as conn :
        row =conn .execute ('SELECT id, user_email, title, created_at, updated_at FROM chats WHERE id = ? AND user_email = ?',(chat_id ,user_email )).fetchone ()
    return dict (row )if row else None 

def update_chat_title (chat_id :int ,user_email :str ,title :str )->bool :
    user_email =(user_email or '').strip ().lower ()
    title =(title or '').strip ()or 'New chat'
    with get_conn ()as conn :
        cur =conn .execute ("UPDATE chats SET title = ?, updated_at = datetime('now') WHERE id = ? AND user_email = ?",(title ,chat_id ,user_email ))
    return cur .rowcount >0 

def delete_chat (chat_id :int ,user_email :str )->bool :
    user_email =(user_email or '').strip ().lower ()
    with get_conn ()as conn :
        cur =conn .execute ('DELETE FROM chats WHERE id = ? AND user_email = ?',(chat_id ,user_email ))
    return cur .rowcount >0 

def get_messages (chat_id :int ,user_email :str )->List [Dict [str ,Any ]]:
    chat =get_chat (chat_id ,user_email )
    if not chat :
        return []
    with get_conn ()as conn :
        rows =conn .execute ('SELECT id, chat_id, role, content, highlights, created_at\n               FROM messages WHERE chat_id = ? ORDER BY id ASC',(chat_id ,)).fetchall ()
    return [dict (r )for r in rows ]

def add_message (chat_id :int ,user_email :str ,role :str ,content :str ,highlights :Optional [str ]=None )->Optional [Dict [str ,Any ]]:
    chat =get_chat (chat_id ,user_email )
    if not chat :
        return None 
    with get_conn ()as conn :
        cur =conn .execute ('INSERT INTO messages (chat_id, role, content, highlights) VALUES (?, ?, ?, ?)',(chat_id ,role ,content ,highlights or ''))
        conn .execute ("UPDATE chats SET updated_at = datetime('now') WHERE id = ?",(chat_id ,))
        row =conn .execute ('SELECT id, chat_id, role, content, highlights, created_at FROM messages WHERE id = ?',(cur .lastrowid ,)).fetchone ()
    return dict (row )if row else None 

def get_consultation_count_this_month (user_email :str )->int :
    if not (user_email or '').strip ():
        return 0 
    user_email =user_email .strip ().lower ()
    with get_conn ()as conn :
        row =conn .execute ("SELECT COUNT(*) AS cnt FROM messages m\n               JOIN chats c ON c.id = m.chat_id AND c.user_email = ?\n               WHERE m.role = 'user' AND strftime('%Y-%m', m.created_at) = strftime('%Y-%m', 'now')",(user_email ,)).fetchone ()
    return int (row ['cnt'])if row else 0 
