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