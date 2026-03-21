# GROUND_TRUTH: VULNERABLE
"""
Basic SQL injection vulnerability.
Flask route takes username from request.args and builds SQL with f-string.
"""
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/user')
def get_user():
    username = request.args.get('username', '')
    
    # VULNERABLE: f-string interpolation with user input
    query = f"SELECT * FROM users WHERE username = '{username}'"
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)  # SQLi here - unsanitized user input
    result = cursor.fetchall()
    conn.close()
    
    return jsonify({"users": result})

if __name__ == '__main__':
    app.run(debug=True)
