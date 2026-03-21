# GROUND_TRUTH: SAFE
"""
Parameterized SQL query - SAFE from SQL injection.
"""
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/user-safe')
def get_user_safe():
    username = request.args.get('username', '')
    
    # SAFE: Parameterized query with placeholder
    query = "SELECT * FROM users WHERE username = ?"
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query, (username,))  # Safe: parameterized
    result = cursor.fetchall()
    conn.close()
    
    return jsonify({"users": result})

if __name__ == '__main__':
    app.run(debug=True)
