# Authentication and Sessions

This section provides detailed information on how user authentication is handled in the Flask web application, including session management and encryption.

## Overview

The Flask application in `app.py` implements basic user authentication with the following key features:
- User credentials are stored in a dictionary.
- Session data is encrypted using AES in CBC mode.
- The application includes routes for the home page, login, and a welcome page.
- Admin users can read and display the contents of a flag file.

## File: `app.py`

### Key Components

- **Flask Application Setup**: The Flask application is set up to handle basic user authentication.
- **User Credentials**: User credentials are stored in a dictionary.
- **Session Management**: Session data is encrypted and decrypted using AES in CBC mode.
- **Routes**:
  - **Home Page**: `/` (GET)
  - **Login**: `/login` (POST)
  - **Welcome Page**: `/welcome` (GET)

### Authentication Flow

1. **Home Page (`/`)**:
   - The home page is rendered using the `index` route.
   - This route does not require authentication and is accessible to all users.

2. **Login (`/login`)**:
   - The `login` route handles user authentication.
   - It checks the provided credentials against the stored user dictionary.
   - If the credentials are valid, a session cookie is set, and the user is redirected to the welcome page.
   - If the credentials are invalid, an error message is displayed.

3. **Welcome Page (`/welcome`)**:
   - The `welcome` route displays a welcome message.
   - If the user is an admin, it reads and displays the contents of a flag file.
   - This route requires a valid session cookie to access.

### Session Management

- **Session Data Encryption**:
  - Session data is encrypted using AES in CBC mode.
  - The encryption and decryption functions are defined in the `app.py` file.
  - The session cookie is set with the encrypted session data.

### Example Code Snippets

#### User Credentials Dictionary

```python
users = {
    'user1': 'password1',
    'admin': 'adminpassword'
}
```

#### Login Route

```python
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username in users and users[username] == password:
        session['username'] = encrypt(username)
        return redirect('/welcome')
    else:
        return 'Invalid credentials', 401
```

#### Welcome Route

```python
@app.route('/welcome')
def welcome():
    if 'username' in session:
        username = decrypt(session['username'])
        if username == 'admin':
            with open('flag.txt', 'r') as file:
                flag = file.read()
            return f'Welcome, {username}! Here is the flag: {flag}'
        else:
            return f'Welcome, {username}!'
    else:
        return 'You are not logged in', 401
```

### Security Considerations

- **Credential Storage**: User credentials are stored in a dictionary, which is not secure for production environments. Consider using a secure database and hashing passwords.
- **Session Encryption**: Session data is encrypted using AES in CBC mode, which provides a good level of security.
- **Admin Access**: The admin user can read a flag file, which should be protected and accessed securely.

## Conclusion

The Flask application in `app.py` provides a basic implementation of user authentication and session management. While it is suitable for demonstration purposes, it is recommended to enhance security measures for production use, such as using a secure database and hashing passwords.