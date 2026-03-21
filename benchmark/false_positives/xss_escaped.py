# GROUND_TRUTH: SAFE
"""
XSS-safe: User input sanitized with bleach.clean before template rendering.
"""
from flask import Flask, request, render_template_string
import bleach

app = Flask(__name__)

@app.route('/comment-safe')
def post_comment():
    comment = request.form.get('comment', '')
    
    # SAFE: Sanitize with bleach before rendering
    clean_comment = bleach.clean(
        comment,
        tags=['p', 'br'],  # Allow only safe tags
        strip=True  # Remove disallowed tags entirely
    )
    
    template = f"<div class='comment'>{clean_comment}</div>"
    return render_template_string(template)

if __name__ == '__main__':
    app.run(debug=True)
