# GROUND_TRUTH: VULNERABLE
"""
Command injection via subprocess with shell=True and user input.
"""
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_file():
    filename = request.form.get('filename', '')
    
    # VULNERABLE: User input passed to subprocess with shell=True
    # Attacker can inject commands: "file.txt; rm -rf /"
    cmd = f"convert {filename} output.png"
    
    result = subprocess.run(
        cmd,
        shell=True,  # DANGEROUS: shell=True with user input
        capture_output=True,
        text=True
    )
    
    return jsonify({"output": result.stdout})

if __name__ == '__main__':
    app.run(debug=True)
