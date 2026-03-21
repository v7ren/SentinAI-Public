# GROUND_TRUTH: VULNERABLE
"""
SSRF via requests.get with user-controlled URL.
"""
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/fetch')
def fetch_url():
    url = request.args.get('url', '')
    
    # VULNERABLE: User-controlled URL passed to requests.get
    # Can fetch internal resources like http://localhost:80 or
    # cloud metadata like http://169.254.169.254/latest/meta-data/
    try:
        response = requests.get(url, timeout=5)  # SSRF here
        return jsonify({
            "status": response.status_code,
            "content": response.text[:1000]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
