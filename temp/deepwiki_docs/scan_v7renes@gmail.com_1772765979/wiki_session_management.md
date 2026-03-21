# Session Management

This section explains how sessions are created, maintained, and secured using AES encryption, and how session data is used to manage user state in the Flask web application.

## Overview

The session management system in this application ensures that user sessions are securely created and maintained. It uses AES encryption to protect session data and manages user state across different routes. The key components and files involved in session management are:

- **`app.py`**: The main Flask application file that handles user authentication, session creation, and session data encryption.

## Session Creation and Authentication

### User Login

The user login process is handled by the `login` endpoint in `app.py`. Here’s how it works:

1. **User Credentials**: User credentials are stored in a dictionary within the application.
2. **Credential Verification**: When a user submits a login request, the application checks the provided credentials against the stored credentials.
3. **Session Creation**: If the credentials are valid, a session is created, and a session cookie is set in the user's browser.
4. **AES Encryption**: The session data is encrypted using AES-CBC before being stored in the session cookie.

#### Code Snippet: User Login

```python
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username in users and users[username] == password:
        session['username'] = username
        session['data'] = encrypt_session_data(username)
        return redirect(url_for('welcome'))
    else:
        return 'Invalid credentials', 401
```

## Session Maintenance and Data Management

### Session Data Encryption

The session data is encrypted using AES-CBC to ensure that it cannot be easily read or tampered with. The encryption and decryption functions are defined in `app.py`.

#### Code Snippet: AES Encryption and Decryption

```python
def encrypt_session_data(data):
    key = b'secret_key_1234567890123456'  # Example key
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data.encode(), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return base64.b64encode(iv + encrypted_data).decode()

def decrypt_session_data(encrypted_data):
    key = b'secret_key_1234567890123456'  # Example key
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded_data = cipher.decrypt(encrypted_data[16:])
    decrypted_data = unpad(decrypted_padded_data, AES.block_size)
    return decrypted_data.decode()
```

### Session Data Usage

The session data is used to manage user state across different routes. For example, the `welcome` endpoint checks if the user is an admin and reads the content of a flag file if they are.

#### Code Snippet: Welcome Page

```python
@app.route('/welcome')
def welcome():
    username = session.get('username')
    if username:
        if username == 'admin':
            with open('flag.txt', 'r') as file:
                flag = file.read()
            return f'Welcome, {username}! Here is the flag: {flag}'
        else:
            return f'Welcome, {username}!'
    else:
        return 'You are not logged in', 401
```

## Security Considerations

### AES Encryption

- **Key Management**: The AES key is hardcoded in the application for simplicity. In a production environment, it is recommended to use a secure key management system.
- **Initialization Vector (IV)**: A random IV is generated for each encryption operation to ensure that the same plaintext does not produce the same ciphertext.

### Session Cookie

- **Secure Flag**: The session cookie should be marked as secure to ensure it is only transmitted over HTTPS.
- **HttpOnly Flag**: The session cookie should be marked as HttpOnly to prevent access via client-side scripts.

## Conclusion

The session management system in this Flask application ensures that user sessions are securely created, maintained, and managed. By using AES encryption, the application protects sensitive session data and maintains user state across different routes.