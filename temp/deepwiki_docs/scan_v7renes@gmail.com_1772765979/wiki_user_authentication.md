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