# Security Measures

This section provides an overview of the security measures implemented in the application, focusing on encryption, user authentication, and admin access controls.

## User Authentication

### Authentication Mechanism
- **File:** `app.py`
- **Endpoints:**
  - `GET /`: Renders the home page template.
  - `POST /login`: Handles user login, checks credentials, and sets a session cookie if successful.
  - `GET /welcome`: Displays a welcome message. If the user is 'admin', it reads and displays the contents of a flag file.

The application uses a simple dictionary to store user credentials. The `login` endpoint verifies the provided credentials against this dictionary. If the credentials are valid, a session cookie is set, and the user is redirected to the welcome page.

### Session Management
- **Encryption:**
  - Session data is encrypted using AES in CBC mode. This ensures that the session data is secure and cannot be tampered with or read by unauthorized parties.
  - The encryption and decryption logic is implemented in the `app.py` file.

### Example Code Snippet
```python
from flask import Flask, request, session, redirect, url_for, render_template
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# User credentials stored in a dictionary
users = {
    'user1': 'password1',
    'admin': 'adminpassword'
}

# AES encryption key
cipher_key = Fernet.generate_key()
cipher = Fernet(cipher_key)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username in users and users[username] == password:
        # Encrypt session data
        session['username'] = cipher.encrypt(username.encode())
        return redirect(url_for('welcome'))
    else:
        return 'Invalid credentials', 401

@app.route('/welcome')
def welcome():
    if 'username' in session:
        username = cipher.decrypt(session['username']).decode()
        if username == 'admin':
            with open('flag.txt', 'r') as file:
                flag = file.read()
            return f'Welcome, {username}! Here is the flag: {flag}'
        else:
            return f'Welcome, {username}!'
    else:
        return 'You are not logged in', 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

## Admin Access Controls

### Flag File Access
- **File:** `app.py`
- **Endpoint:**
  - `GET /welcome`: If the user is 'admin', the application reads and displays the contents of a flag file.

The `welcome` endpoint checks if the logged-in user is 'admin'. If so, it reads the contents of the `flag.txt` file and displays it. This ensures that only the admin user has access to sensitive information.

### Example Code Snippet
```python
@app.route('/welcome')
def welcome():
    if 'username' in session:
        username = cipher.decrypt(session['username']).decode()
        if username == 'admin':
            with open('flag.txt', 'r') as file:
                flag = file.read()
            return f'Welcome, {username}! Here is the flag: {flag}'
        else:
            return f'Welcome, {username}!'
    else:
        return 'You are not logged in', 401
```

## Summary

The application implements basic security measures to protect user sessions and control access to sensitive information. Key features include:
- **User Authentication:** Credentials are verified against a dictionary, and session data is encrypted.
- **Session Management:** Session data is encrypted using AES in CBC mode to ensure security.
- **Admin Access Controls:** Only the 'admin' user can access the contents of the `flag.txt` file.

These measures provide a foundation for securing the application and protecting user data.