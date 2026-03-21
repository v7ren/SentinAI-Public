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