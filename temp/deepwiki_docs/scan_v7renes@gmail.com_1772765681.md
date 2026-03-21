# Overview

## What the Project Is and What Problem It Solves

The project is a simple Flask web application designed to demonstrate basic user authentication and session management. It provides a secure way to handle user logins, manage sessions, and restrict access to certain pages based on user roles. The application is particularly useful for understanding how to implement secure user authentication and session handling in a web application, which is a common requirement for many web-based systems.

## Main Components or Modules

### Flask Application
- **File:** `app/app.py`
- **Components:**
  - **Routes:**
    - **Home Page (`/`)**: Renders the home page template.
    - **Login (`/login`)**: Handles user login, checks credentials, and sets a session cookie if successful.
    - **Welcome Page (`/welcome`)**: Renders the welcome page template, decrypts the session cookie, and displays the username. If the user is an admin, it reads and displays a flag from a file.
  - **Authentication:**
    - User credentials are stored in a dictionary.
    - Session data is encrypted using AES-CBC.
  - **File Operations:**
    - Reads a flag from a file if the user is an admin.
  - **Logging:**
    - Logs debug information for better traceability and troubleshooting.

### Main Concerns
- **Authentication and Session Management**: The application handles user login, session management, and role-based access control.
- **Encryption and Decryption**: Session data is encrypted using AES-CBC to ensure security.
- **Filesystem Operations**: The application reads a flag from a file if the user is an admin.
- **Logging**: Debug information is logged for better visibility and troubleshooting.

## Typical Usage or Runtime Scenario

1. **Application Startup**:
   - The Flask application is started by running the `__main__` entrypoint in `app/app.py`. It listens on host `0.0.0.0` and port `8000` in debug mode.

2. **User Accesses Home Page**:
   - The user navigates to the home page (`/`), which is rendered by the `index` endpoint.

3. **User Logs In**:
   - The user navigates to the login page (`/login`).
   - The user enters their credentials (username and password).
   - The `login` endpoint checks the credentials against the stored dictionary.
   - If the credentials are valid, a session cookie is set, and the user is redirected to the welcome page.

4. **User Accesses Welcome Page**:
   - The user navigates to the welcome page (`/welcome`).
   - The `welcome` endpoint decrypts the session cookie to retrieve the username.
   - If the user is an admin, the application reads and displays a flag from a file.
   - The welcome page is rendered, displaying the username and any additional information.

## Where to Look Next

For a deeper dive into the project, consider exploring the following sections:

- **Authentication and Session Management**: Detailed explanation of how user authentication and session management are implemented.
- **Encryption and Decryption**: In-depth look at the AES-CBC encryption and decryption processes used to secure session data.
- **File Operations**: Explanation of how the application reads and displays the flag from a file for admin users.
- **Logging**: Detailed information on how debug logs are generated and used for troubleshooting.

These sections will provide a more granular understanding of the project's components and their interactions.

---

# Architecture and Data Flow

## Overview

The project is a simple Flask web application that includes basic user authentication, session management, and file operations. The application is structured around a single main file, `app.py`, which handles all the routing, authentication, and data processing. The architecture is straightforward and follows a client-server pattern, with the Flask application serving as the server and handling HTTP requests from clients.

## Main Architectural Components

### 1. Flask Application (`app.py`)
- **Role**: The core of the application, responsible for handling HTTP requests and responses.
- **Key Components**:
  - **Routes**: 
    - `index`: Renders the home page.
    - `login`: Handles user login, checks credentials, and sets a session cookie if successful.
    - `welcome`: Renders the welcome page, decrypts the session cookie, and displays the username. If the user is 'admin', it reads and displays a flag from a file.
  - **Authentication**:
    - User credentials are stored in a dictionary.
    - Session data is encrypted using AES-CBC.
  - **File Operations**:
    - Reads a flag from a file if the user is an admin.
  - **Logging**:
    - Logs debug information for various operations.

### 2. User Authentication and Session Management
- **Role**: Manages user authentication and session data.
- **Key Functions**:
  - **`login`**: 
    - Authenticates users by checking credentials against a dictionary.
    - Sets a session cookie if the login is successful.
  - **`welcome`**:
    - Decrypts the session cookie to retrieve the username.
    - Checks if the user is an admin and reads a flag from a file if so.

### 3. Encryption and Decryption
- **Role**: Ensures the security of session data.
- **Key Functions**:
  - **AES-CBC**:
    - Used to encrypt and decrypt session data.
    - Ensures that session information is not exposed in plain text.

## Data and Control Flow

### 1. Client-Server Interaction
- **Client**:
  - Sends HTTP requests to the Flask application.
- **Server (`app.py`)**:
  - Receives HTTP requests and processes them based on the defined routes.
  - Responds with appropriate HTTP responses (e.g., HTML pages, JSON data).

### 2. Authentication Flow
1. **Home Page (`index`)**:
   - The client requests the home page.
   - The server renders the home page template and sends it to the client.
2. **Login (`login`)**:
   - The client submits a login form with username and password.
   - The server checks the credentials against a dictionary.
   - If the credentials are valid, the server sets a session cookie and redirects the client to the welcome page.
3. **Welcome Page (`welcome`)**:
   - The client requests the welcome page.
   - The server decrypts the session cookie to retrieve the username.
   - If the user is an admin, the server reads a flag from a file and displays it.
   - The server renders the welcome page template and sends it to the client.

### 3. File Operations
- **Reading the Flag**:
  - If the user is an admin, the server reads a flag from a file and includes it in the welcome page response.

## Important Patterns

### 1. Client-Server Pattern
- The application follows a client-server pattern, where the Flask application acts as the server and handles HTTP requests from clients.

### 2. Session Management
- The application uses session cookies to manage user sessions. Session data is encrypted using AES-CBC to ensure security.

### 3. Simple Authentication
- User authentication is handled by checking credentials against a dictionary. This is a simple and straightforward approach suitable for small-scale applications.

### 4. File Operations
- The application reads a flag from a file if the user is an admin. This is a simple file operation that demonstrates how the application interacts with the filesystem.

## Conclusion

The architecture of the application is simple and efficient, leveraging Flask for web development, AES-CBC for session encryption, and basic file operations. The client-server pattern ensures that the application can handle HTTP requests and responses effectively, while the session management and authentication mechanisms provide a secure user experience.

---

# Authentication and Security

This section details the implementation of user authentication in the application, including the use of AES encryption for session data and the handling of admin privileges.

## Overview

The authentication system is implemented in the `app.py` file, which sets up a Flask web application. The application includes routes for the home page, login, and a welcome page. User credentials are stored in a dictionary, and session data is encrypted using AES-CBC. Additionally, the application checks if the user is an admin and reads a flag from a file if the user has admin privileges.

## Key Components

### Flask Application Setup

- **File**: `app.py`
- **Main Concerns**:
  - User authentication
  - Session management
  - Admin privilege handling

### Routes

#### Home Page

- **Endpoint**: `index`
- **Method**: `GET`
- **Path**: `/`
- **Description**: Renders the home page template.

#### Login

- **Endpoint**: `login`
- **Method**: `POST`
- **Path**: `/login`
- **Description**: Handles user login by checking credentials and setting a session cookie if the login is successful.

#### Welcome Page

- **Endpoint**: `welcome`
- **Method**: `GET`
- **Path**: `/welcome`
- **Description**: Renders the welcome page template, decrypts the session cookie, and displays the username. If the user is 'admin', it reads and displays a flag from a file.

### User Authentication

- **User Credentials**: User credentials are stored in a dictionary within the `app.py` file.
- **Login Process**:
  - The `login` endpoint checks the provided username and password against the stored credentials.
  - If the credentials are valid, a session cookie is set using AES-CBC encryption to secure the session data.

### Session Management

- **Session Data**: Session data is encrypted using AES-CBC.
- **Encryption and Decryption**:
  - The application uses the `cryptography` library to handle AES encryption and decryption.
  - The session cookie is encrypted when the user logs in and decrypted when the user accesses the welcome page.

### Admin Privileges

- **Admin Check**: The application checks if the logged-in user is 'admin'.
- **Flag Reading**:
  - If the user is 'admin', the application reads a flag from a file and displays it on the welcome page.

## Flow of Authentication

1. **Home Page**:
   - The user navigates to the home page (`/`).
   - The home page template is rendered.

2. **Login**:
   - The user submits a login request to the `/login` endpoint.
   - The application checks the provided username and password against the stored credentials.
   - If the credentials are valid, a session cookie is set with the user's username encrypted using AES-CBC.

3. **Welcome Page**:
   - The user navigates to the welcome page (`/welcome`).
   - The application decrypts the session cookie to retrieve the username.
   - The welcome page template is rendered, displaying the username.
   - If the user is 'admin', the application reads a flag from a file and displays it on the page.

## Security Considerations

- **AES Encryption**: Session data is encrypted using AES-CBC to ensure the security of user sessions.
- **Filesystem Operations**: The application reads a flag from a file if the user is 'admin'. This operation is performed securely to prevent unauthorized access to the flag.
- **Debug Mode**: The application runs in debug mode, which is suitable for development but should be disabled in production to avoid security risks.

By following this structured approach, the application ensures that user authentication is secure and that admin privileges are handled appropriately.

---

# Routing and Endpoints

This section describes the different routes and endpoints available in the application, including their functionalities and how they interact with the user. The application is built using Flask, a lightweight web framework for Python, and includes basic user authentication and session management.

## Overview

The main file for the application is `app.py`, which sets up the Flask application and defines the following routes:

- **Home Page (`/`)**: The landing page of the application.
- **Login (`/login`)**: Handles user authentication and session management.
- **Welcome Page (`/welcome`)**: Displays a welcome message and additional information based on user roles.

## Routes and Endpoints

### Home Page (`/`)

- **Method**: GET
- **Function**: `index`
- **Description**: This endpoint renders the home page template. It is the landing page of the application and does not require authentication.
- **File**: `app.py`

### Login (`/login`)

- **Method**: POST
- **Function**: `login`
- **Description**: This endpoint handles user login. It checks the provided credentials against a dictionary of user data. If the credentials are valid, it sets a session cookie and redirects the user to the welcome page. The session data is encrypted using AES-CBC.
- **File**: `app.py`

### Welcome Page (`/welcome`)

- **Method**: GET
- **Function**: `welcome`
- **Description**: This endpoint renders the welcome page template. It decrypts the session cookie to retrieve the username and displays a welcome message. If the user is an admin (username is 'admin'), it reads and displays a flag from a file.
- **File**: `app.py`

## Authentication and Session Management

### User Authentication

- **Credentials Storage**: User credentials are stored in a dictionary within the application.
- **Encryption**: Session data is encrypted using AES-CBC to ensure security.
- **Session Handling**: Upon successful login, a session cookie is set. This cookie is used to maintain the user's session across requests.

### Admin Privileges

- **Admin Check**: If the logged-in user has the username 'admin', the application reads and displays a flag from a file. This functionality is specific to the welcome page endpoint.

## Filesystem Operations

- **Flag Reading**: The application reads a flag from a file if the user is an admin. This operation is performed in the `welcome` endpoint.

## Debugging and Logging

- **Debug Mode**: The Flask application is started in debug mode, which provides detailed error messages and helps with development.
- **Logging**: Debug information is logged to help with troubleshooting and monitoring the application's behavior.

## Main Entry Point

- **Function**: `__main__`
- **Description**: This is the main entry point of the application. It starts the Flask server on host `0.0.0.0` and port `8000`.
- **File**: `app.py`

By understanding these routes and endpoints, you can navigate and interact with the application effectively. Each endpoint serves a specific purpose and is designed to provide a seamless user experience while ensuring security and functionality.

---

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

---