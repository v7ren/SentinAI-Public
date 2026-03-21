# GROUND_TRUTH: VULNERABLE
"""
XSS via template injection. User input passed to render_template_string without escaping.
"""
from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/greet')
def greet():
    name = request.args.get('name', 'Guest')
    
    # VULNERABLE: User input in template without escaping
    template = f"<h1>Hello, {name}!</h1>"
    
    # render_template_string with unsanitized user data = XSS
    return render_template_string(template)

if __name__ == '__main__':
    app.run(debug=True)
