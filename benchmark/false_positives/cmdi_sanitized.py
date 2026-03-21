# GROUND_TRUTH: SAFE
"""
Command injection-safe: User input sanitized with shlex.quote.
"""
from flask import Flask, request, jsonify
import subprocess
import shlex

app = Flask(__name__)

@app.route('/convert-safe', methods=['POST'])
def convert_file_safe():
    filename = request.form.get('filename', '')
    
    # SAFE: Quote the user input to prevent command injection
    safe_filename = shlex.quote(filename)
    
    cmd = f"convert {safe_filename} output.png"
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    return jsonify({"output": result.stdout})

if __name__ == '__main__':
    app.run(debug=True)
