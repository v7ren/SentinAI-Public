# GROUND_TRUTH: VULNERABLE (part of cross-file chain)
"""
Entry point for cross-file SQL injection.
Takes user input and passes to another function.
"""
from flask import Flask, request, jsonify
from sqli_cross_file import get_user

app = Flask(__name__)

@app.route('/profile')
def profile():
    user_id = request.args.get('id', '')
    
    # Pass user input to another function (cross-file call)
    user = get_user(user_id)
    
    return jsonify({"user": user})

if __name__ == '__main__':
    app.run(debug=True)
