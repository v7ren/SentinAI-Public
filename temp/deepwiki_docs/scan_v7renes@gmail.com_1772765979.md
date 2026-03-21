# Overview

## What the Project Is and What Problem It Solves

The project is a simple Flask web application that provides user authentication and session management. It addresses the problem of securely managing user sessions and credentials in a web application. The application includes routes for a home page, user login, and a welcome page. Additionally, it supports reading a flag file if the user has admin privileges, which can be useful for internal testing or administrative tasks.

## Main Components or Modules

### Flask Application
- **File**: `app.py`
- **Description**: This file sets up the Flask web application and defines the main routes.
- **Key Entities/Functions**:
  - `index`: Renders the home page template.
  - `login`: Handles user login, checks credentials, and sets a session cookie if successful.
  - `welcome`: Displays a welcome message. If the user is 'admin', it reads and displays the content of a flag file.
  - `__main__`: Starts the Flask application on host `0.0.0.0` and port `8000` in debug mode.

### User Authentication and Session Management
- **Technologies**: Flask, AES-CBC for session encryption
- **Description**: The application uses a dictionary to store user credentials and AES-CBC encryption to secure session data. This ensures that user sessions are protected and cannot be easily tampered with.

### Filesystem Operations
- **Description**: The application reads a flag file if the user is an admin. This operation is performed in the `welcome` route to display the flag content.

## Typical Usage or Runtime Scenario

1. **Application Startup**:
   - The Flask application is started by running `app.py`.
   - The application listens on `0.0.0.0:8000` in debug mode.

2. **User Access**:
   - A user navigates to the home page (`/`).
   - The home page is rendered, providing a link to the login page.

3. **User Login**:
   - The user clicks the login link and is directed to the login page (`/login`).
   - The user enters their credentials and submits the form.
   - The application checks the credentials against the stored dictionary.
   - If the credentials are valid, a session cookie is set, and the user is redirected to the welcome page (`/welcome`).

4. **Welcome Page**:
   - The welcome page displays a welcome message.
   - If the user is an admin, the application reads the content of a flag file and displays it.

## Where to Look Next

- **Authentication and Security**: For more details on how user authentication and session management are implemented, see the **Security** section.
- **Routing and Endpoints**: For a deeper dive into the Flask routes and their functionalities, see the **Routing** section.
- **Filesystem Operations**: For information on how the application interacts with the filesystem, see the **Filesystem** section.
- **Configuration and Deployment**: For details on how to configure and deploy the application, see the **Configuration** and **Deployment** sections.

This overview provides a high-level understanding of the project. For more detailed information, refer to the specific sections mentioned above.

---

# Architecture and Data Flow

## Overview

The application is a simple Flask web application with user authentication. It consists of several key components that handle user interactions, authentication, and data retrieval. The main architectural components include the Flask application, user authentication, and session management.

## Main Architectural Components

### Flask Application
- **File**: `app.py`
- **Description**: The core of the application is a Flask web server that handles HTTP requests and responses. It includes routes for the home page, login, and a welcome page.
- **Key Functions**:
  - `index()`: Renders the home page template.
  - `login()`: Handles user login, checks credentials, and sets a session cookie if successful.
  - `welcome()`: Displays a welcome message. If the user is 'admin', it reads and displays the content of a flag file.
  - `__main__`: Starts the Flask application on host `0.0.0.0` and port `8000` in debug mode.

### User Authentication
- **File**: `app.py`
- **Description**: The application implements basic user authentication. User credentials are stored in a dictionary, and session data is encrypted using AES-CBC.
- **Key Functions**:
  - `login()`: This function checks the user's credentials against a predefined dictionary. If the credentials are valid, it sets a session cookie and encrypts the session data using AES-CBC.
  - `welcome()`: This function checks if the user is 'admin' and reads the content of a flag file if the user is an admin.

### Session Management
- **File**: `app.py`
- **Description**: Session data is managed using Flask's session management capabilities. The session data is encrypted using AES-CBC to ensure security.
- **Key Functions**:
  - `login()`: Sets the session cookie and encrypts the session data.
  - `welcome()`: Decrypts the session data to check if the user is 'admin'.

## Data and Control Flow

### User Interaction Flow
1. **Home Page (`/`)**:
   - The user navigates to the home page.
   - The `index()` function is called, which renders the home page template.
2. **Login (`/login`)**:
   - The user submits a login form with their credentials.
   - The `login()` function is called, which checks the credentials against a predefined dictionary.
   - If the credentials are valid, the function sets a session cookie and encrypts the session data using AES-CBC.
   - The user is redirected to the welcome page.
3. **Welcome Page (`/welcome`)**:
   - The user navigates to the welcome page.
   - The `welcome()` function is called, which decrypts the session data to check if the user is 'admin'.
   - If the user is 'admin', the function reads the content of a flag file and displays it.
   - If the user is not 'admin', a generic welcome message is displayed.

### Data Flow
- **User Credentials**:
  - Stored in a dictionary within `app.py`.
  - Accessed during the login process to verify user credentials.
- **Session Data**:
  - Encrypted using AES-CBC and stored in a session cookie.
  - Decrypted when the user navigates to the welcome page to check if the user is 'admin'.
- **Flag File**:
  - Read from the filesystem if the user is 'admin'.
  - Displayed on the welcome page.

## Important Patterns

### MVC (Model-View-Controller) Pattern
- **Model**: The user credentials dictionary and the flag file.
- **View**: The templates for the home page, login form, and welcome page.
- **Controller**: The Flask routes (`index()`, `login()`, `welcome()`) that handle user requests and manage the application's logic.

### Session Management
- **Pattern**: The application uses Flask's session management to store and manage user session data.
- **Security**: Session data is encrypted using AES-CBC to ensure that sensitive information is not exposed.

### Filesystem Operations
- **Pattern**: The application reads a flag file from the filesystem if the user is 'admin'.
- **Security**: The flag file is only accessed if the user has the necessary permissions.

## Conclusion

The application is a simple yet secure Flask web application that demonstrates basic user authentication, session management, and filesystem operations. The architecture is modular and follows the MVC pattern, making it easy to understand and maintain. The use of AES-CBC for session data encryption adds an additional layer of security to the application.

---

# User Authentication

This section details the user authentication process in the Flask web application, including how credentials are checked, sessions are managed, and encryption is used to secure session data.

## Overview

The user authentication process is implemented in the `app.py` file. The application uses a simple dictionary to store user credentials and leverages AES-CBC encryption to secure session data. The main entrypoints for authentication are the home page, login, and welcome page.

## Key Components

### Flask Application Setup

- **File**: `app.py`
- **Main Function**: `__main__`
  - **Details**: Starts the Flask application on host `0.0.0.0` and port `8000` in debug mode.

### Routes

#### Home Page

- **Endpoint**: `index`
- **Method**: `GET`
- **Path**: `/`
- **Details**: Renders the home page template.

#### Login

- **Endpoint**: `login`
- **Method**: `POST`
- **Path**: `/login`
- **Details**: Handles user login by checking credentials and setting a session cookie if successful.

#### Welcome Page

- **Endpoint**: `welcome`
- **Method**: `GET`
- **Path**: `/welcome`
- **Details**: Displays a welcome message. If the user is 'admin', it reads and displays the content of a flag file.

## Authentication Flow

### Credential Checking

- **File**: `app.py`
- **Function**: `login`
  - **Details**: The `login` function checks the user credentials against a predefined dictionary. If the credentials are valid, it sets a session cookie and redirects the user to the welcome page.

### Session Management

- **File**: `app.py`
- **Function**: `login` and `welcome`
  - **Details**: The session data is stored in the Flask session object. When a user logs in successfully, a session cookie is set. The session data is encrypted using AES-CBC to ensure security.

### Encryption and Decryption

- **File**: `app.py`
- **Function**: `encrypt_session_data` and `decrypt_session_data`
  - **Details**: These functions handle the encryption and decryption of session data using AES-CBC. The encryption key and initialization vector (IV) are predefined in the application.

### Admin Flag Reading

- **File**: `app.py`
- **Function**: `welcome`
  - **Details**: If the user is identified as 'admin', the `welcome` function reads the content of a flag file and displays it. This operation involves a filesystem operation to read the file.

## Example Flow

1. **User Navigates to Home Page**
   - The user accesses the home page by navigating to the root URL (`/`).
   - The `index` function renders the home page template.

2. **User Submits Login Credentials**
   - The user submits their credentials via a POST request to the `/login` endpoint.
   - The `login` function checks the credentials against the predefined dictionary.
   - If the credentials are valid, the function sets a session cookie and redirects the user to the welcome page.

3. **User Accesses Welcome Page**
   - The user is redirected to the `/welcome` endpoint.
   - The `welcome` function checks the session data to verify the user's identity.
   - If the user is 'admin', the function reads the content of the flag file and displays it.

## Security Considerations

- **Credential Storage**: User credentials are stored in a dictionary, which is not suitable for production environments. Consider using a secure database for storing user credentials.
- **Session Encryption**: Session data is encrypted using AES-CBC to prevent session hijacking and ensure data integrity.
- **Debug Mode**: The application runs in debug mode, which is not recommended for production environments. Ensure to disable debug mode in production.

By following this structured approach, the user authentication process is secure and well-managed within the Flask web application.

---

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

---

# Admin Features

This section describes the special features available to admin users in the application, focusing on the ability to read and display the content of a flag file.

## Overview

The application is a simple Flask web application with user authentication. Admin users have additional privileges, such as the ability to read and display the content of a flag file. This functionality is implemented in the `app.py` file, which contains the main routes and authentication logic.

## Key Files and Functions

### `app.py`

- **File Location**: `XBEN-103-24\app\app.py`
- **Summary**: This file sets up a Flask web application with basic user authentication, encryption, and decryption functionalities. It includes routes for the home page, login, and a welcome page. The application uses AES encryption to secure session data and logs debug information.

#### Routes

- **Home Page (`/`)**:
  - **Function**: `index`
  - **Description**: Renders the home page template.
  - **Endpoint**: `GET /`

- **Login (`/login`)**:
  - **Function**: `login`
  - **Description**: Handles user login, checks credentials, and sets a session cookie if successful.
  - **Endpoint**: `POST /login`

- **Welcome Page (`/welcome`)**:
  - **Function**: `welcome`
  - **Description**: Displays a welcome message. If the user is 'admin', it reads and displays the content of a flag file.
  - **Endpoint**: `GET /welcome`

#### Authentication and Session Management

- **User Credentials**: User credentials are stored in a dictionary.
- **Session Data**: Session data is encrypted using AES-CBC.
- **Logging**: Debug information is logged for troubleshooting and auditing.

## Admin-Specific Features

### Reading and Displaying the Flag File

- **Function**: `welcome`
- **Description**: When an admin user accesses the welcome page, the application reads the content of a flag file and displays it.
- **Implementation**:
  - The `welcome` function checks if the current user is 'admin'.
  - If the user is 'admin', the application reads the content of the flag file.
  - The flag file content is then displayed to the admin user.

### Example Flow

1. **User Accesses the Home Page**:
   - The user navigates to the home page (`/`).
   - The `index` function renders the home page template.

2. **User Logs In**:
   - The user submits their credentials via the login form (`/login`).
   - The `login` function checks the credentials against the stored user dictionary.
   - If the credentials are valid, a session cookie is set, and the user is redirected to the welcome page (`/welcome`).

3. **Admin User Accesses the Welcome Page**:
   - If the user is 'admin', the `welcome` function reads the content of the flag file.
   - The flag file content is displayed to the admin user.

## Security Considerations

- **User Authentication**: User credentials are securely stored and checked.
- **Session Management**: Session data is encrypted using AES-CBC to prevent session hijacking.
- **File Access**: The application ensures that only admin users can read the flag file, adding an additional layer of security.

## Conclusion

The admin features in the application provide a simple yet secure way for admin users to access and display sensitive information, such as the content of a flag file. The implementation is centered around the `app.py` file, which handles user authentication, session management, and file operations.

---