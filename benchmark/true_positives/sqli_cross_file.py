# GROUND_TRUTH: VULNERABLE (cross-file SQLi)
"""
Cross-file SQL injection. This file defines the sink that receives
tainted input from user_input_handler.py.
"""
import sqlite3

def get_user(user_id):
    """
    VULNERABLE: Builds SQL with unsanitized user input.
    Called from user_input_handler.py with request.args input.
    """
    # VULNERABLE: f-string with user-controlled parameter
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)  # SQLi via cross-file flow
    result = cursor.fetchone()
    conn.close()
    
    return result
