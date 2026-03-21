# File Operations

This section covers the file operations used in the application, specifically focusing on reading the flag for admin users. The primary file involved in this process is `app.py`, which contains the Flask web application and the logic for handling file operations.

## Overview

The application includes a route that reads a flag from a file if the user is an admin. This operation is part of the `welcome` endpoint, which is responsible for rendering the welcome page and displaying user-specific information.

## File Operations in `app.py`

### File: `app.py`

#### Key Functions and Endpoints

- **`index` Endpoint**
  - **Path**: `/`
  - **Method**: `GET`
  - **Description**: Renders the home page template.

- **`login` Endpoint**
  - **Path**: `/login`
  - **Method**: `POST`
  - **Description**: Handles user login, checks credentials, and sets a session cookie if successful.

- **`welcome` Endpoint**
  - **Path**: `/welcome`
  - **Method**: `GET`
  - **Description**: Renders the welcome page template, decrypts the session cookie, and displays the username. If the user is 'admin', it reads and displays a flag from a file.

### File Reading Logic

The file reading logic is implemented within the `welcome` endpoint. Here is a breakdown of the process:

1. **Session Decryption**: The session cookie is decrypted using AES-CBC to retrieve the user's session data.
2. **User Check**: The application checks if the user is an admin by comparing the username to the string `'admin'`.
3. **Flag Reading**: If the user is an admin, the application reads the flag from a file.
4. **Display**: The flag is then displayed on the welcome page.

#### Code Snippet

```python
@app.route('/welcome')
def welcome():
    # Decrypt session cookie to get user data
    session_data = decrypt_session_cookie(request.cookies.get('session'))
    
    # Check if the user is an admin
    if session_data.get('username') == 'admin':
        # Read the flag from a file
        with open('flag.txt', 'r') as file:
            flag = file.read()
        return render_template('welcome.html', username=session_data['username'], flag=flag)
    else:
        return render_template('welcome.html', username=session_data['username'])
```

### Security Considerations

- **Session Encryption**: The session data is encrypted using AES-CBC to ensure that sensitive information, such as user credentials, is not exposed.
- **File Access**: The flag file (`flag.txt`) is read only if the user is an admin, which helps to restrict access to sensitive information.

## Conclusion

The file operations in the application are primarily focused on reading a flag for admin users. This is achieved through the `welcome` endpoint, which decrypts the session data, checks the user's role, and reads the flag from a file if the user is an admin. The process is designed to be secure, with session data encrypted and file access restricted to authorized users.