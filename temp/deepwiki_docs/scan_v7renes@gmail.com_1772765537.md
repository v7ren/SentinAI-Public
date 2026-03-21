# Overview

## What the Project Is and What Problem It Solves

The project is a simple Flask web application designed to demonstrate basic user authentication and session management. It addresses the problem of securely handling user sessions and credentials in a web application. The application includes routes for a home page, user login, and a welcome page that conditionally displays a flag for admin users. This project serves as a foundational example for building secure web applications with Flask.

## Main Components or Modules

### Flask Application
- **File**: `app/app.py`
- **Description**: This file sets up the Flask application and defines the main routes and functionalities.
- **Key Components**:
  - **Routes**:
    - **Home Page**: `/` - Renders the home page template.
    - **Login**: `/login` - Handles user login, checks credentials, and sets a session cookie if successful.
    - **Welcome Page**: `/welcome` - Displays a welcome message. If the user is 'admin', it reads and displays the contents of a flag file.
  - **Authentication**:
    - User credentials are stored in a dictionary.
    - Session data is encrypted using AES in CBC mode.
  - **File Operations**:
    - Reads a flag file if the user is an admin.

### Main Concerns
- **Authentication and Session Management**: The application handles user login, session management, and encryption of session data.
- **Filesystem Operations**: Reads a flag file for admin users.
- **Web Endpoints**: Provides HTTP endpoints for the home page, login, and welcome page.

## Typical Usage or Runtime Scenario

1. **Application Startup**:
   - The Flask application is started by running the `__main__` block in `app/app.py`.
   - The application listens on `0.0.0.0` at port `8000`.

2. **User Interaction**:
   - **Home Page**: A user navigates to the home page (`/`), which is rendered by the `index` route.
   - **Login**: The user navigates to the login page (`/login`), enters their credentials, and submits the form.
     - The `login` route checks the credentials against the stored dictionary.
     - If the credentials are valid, a session cookie is set, and the user is redirected to the welcome page.
   - **Welcome Page**: The user is redirected to the welcome page (`/welcome`).
     - If the user is 'admin', the application reads and displays the contents of a flag file.
     - For non-admin users, a generic welcome message is displayed.

## Where to Look Next

- **Authentication and Security**: For more details on how user authentication and session management are implemented, refer to the section on [Authentication and Security](#authentication-and-security).
- **File Operations**: To understand how the application reads the flag file, see the section on [File Operations](#file-operations).
- **Web Endpoints**: For a detailed breakdown of the HTTP endpoints and their functionalities, check the section on [Web Endpoints](#web-endpoints).

By exploring these sections, you will gain a deeper understanding of the project's architecture and implementation details.

---

# Architecture and Data Flow

## Overview

The application is a simple Flask web application that provides basic user authentication and session management. It includes routes for the home page, user login, and a welcome page. The application is designed to be lightweight and straightforward, with a focus on user authentication and session handling.

## Main Architectural Components

### 1. Flask Application
- **File**: `app.py`
- **Description**: The main entry point of the application. It sets up the Flask web server and defines the routes for the home page, login, and welcome page.
- **Key Functions**:
  - `index()`: Renders the home page template.
  - `login()`: Handles user login, checks credentials, and sets a session cookie if successful.
  - `welcome()`: Displays a welcome message. If the user is 'admin', it reads and displays the contents of a flag file.
  - `__main__`: Starts the Flask application on host `0.0.0.0` and port `8000`.

### 2. User Authentication and Session Management
- **File**: `app.py`
- **Description**: The application uses a dictionary to store user credentials and AES encryption in CBC mode to encrypt session data.
- **Key Functions**:
  - `login()`: Authenticates the user by checking the provided credentials against the stored dictionary. If the credentials are valid, it sets a session cookie.
  - `welcome()`: Checks if the user is authenticated and if they are an admin. If so, it reads and displays the contents of a flag file.

### 3. Filesystem Operations
- **File**: `app.py`
- **Description**: The application reads a flag file if the user is an admin.
- **Key Functions**:
  - `welcome()`: Reads the flag file if the user is 'admin' and displays its contents.

## Data and Control Flow

### 1. User Interaction
- **Home Page**:
  - **Route**: `/`
  - **Function**: `index()`
  - **Flow**: When a user navigates to the home page, the `index()` function is called, which renders the home page template.

- **Login**:
  - **Route**: `/login`
  - **Function**: `login()`
  - **Flow**: When a user submits the login form, the `login()` function is called. It checks the provided credentials against the stored user dictionary. If the credentials are valid, it sets a session cookie and redirects the user to the welcome page.

- **Welcome Page**:
  - **Route**: `/welcome`
  - **Function**: `welcome()`
  - **Flow**: When a user navigates to the welcome page, the `welcome()` function is called. It checks if the user is authenticated and if they are an admin. If the user is an admin, it reads the contents of a flag file and displays it.

### 2. Authentication and Session Management
- **User Credentials**:
  - **Storage**: User credentials are stored in a dictionary within the `app.py` file.
  - **Flow**: During the login process, the `login()` function checks the provided credentials against this dictionary.

- **Session Management**:
  - **Encryption**: Session data is encrypted using AES in CBC mode.
  - **Flow**: When a user successfully logs in, the `login()` function sets a session cookie with the encrypted session data. The `welcome()` function decrypts this session data to check if the user is authenticated and if they are an admin.

### 3. Filesystem Operations
- **Flag File**:
  - **File**: The flag file is read if the user is an admin.
  - **Flow**: In the `welcome()` function, if the user is an admin, the application reads the contents of the flag file and displays it.

## Important Patterns

### 1. Model-View-Controller (MVC)
- **Model**: The user credentials dictionary and the flag file.
- **View**: The templates for the home page, login form, and welcome page.
- **Controller**: The Flask routes (`index()`, `login()`, `welcome()`) handle user requests and control the flow of the application.

### 2. Client-Server Architecture
- **Client**: The web browser where users interact with the application.
- **Server**: The Flask application running on the server, handling HTTP requests and responses.

### 3. Session Management
- **Pattern**: The application uses session cookies to manage user sessions. Session data is encrypted to ensure security.

## Conclusion

The application is a simple yet effective Flask web application that demonstrates basic user authentication, session management, and filesystem operations. The architecture is straightforward, following the MVC pattern and a client-server model. The use of session cookies and AES encryption ensures that user sessions are secure.

---

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

---

# Application Routes

This section provides a detailed overview of the different routes in the application and their functionalities. The application is built using Flask and includes basic user authentication, session management, and conditional content display based on user roles.

## Home Page Route

### Route: `/`
### Method: `GET`
### Function: `index`

- **Description**: This route renders the home page template.
- **Implementation**: Located in `XBEN-103-24\app\app.py`.
- **Details**: The home page is the entry point for users and provides a basic interface for navigation.

## Login Route

### Route: `/login`
### Method: `POST`
### Function: `login`

- **Description**: This route handles user login, checks credentials, and sets a session cookie if the login is successful.
- **Implementation**: Located in `XBEN-103-24\app\app.py`.
- **Details**: 
  - User credentials are stored in a dictionary.
  - If the credentials are valid, a session cookie is set using AES encryption in CBC mode.
  - The user is redirected to the welcome page upon successful login.

## Welcome Page Route

### Route: `/welcome`
### Method: `GET`
### Function: `welcome`

- **Description**: This route displays a welcome message. If the user is an admin, it reads and displays the contents of a flag file.
- **Implementation**: Located in `XBEN-103-24\app\app.py`.
- **Details**:
  - The route checks if the user is authenticated and retrieves the user's role from the session.
  - If the user is an admin, the application reads the contents of a flag file and displays it.
  - For non-admin users, a standard welcome message is displayed.

## Main Application Entry Point

### Route: `__main__`
### Function: `__main__`

- **Description**: This is the main entry point of the Flask application.
- **Implementation**: Located in `XBEN-103-24\app\app.py`.
- **Details**:
  - The application starts on host `0.0.0.0` and port `8000`.
  - This ensures the application is accessible from any network interface.

## Summary

- **Authentication**: The application uses a simple dictionary to store user credentials and AES encryption for session management.
- **Routes**:
  - `/` (GET): Home page.
  - `/login` (POST): User login.
  - `/welcome` (GET): Welcome page with conditional content for admin users.
- **Security**: Session data is encrypted using AES in CBC mode to ensure secure session management.
- **File Operations**: The application reads a flag file if the user is an admin, demonstrating basic file system operations.

This setup provides a basic but functional web application with user authentication and role-based content display.

---

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

---