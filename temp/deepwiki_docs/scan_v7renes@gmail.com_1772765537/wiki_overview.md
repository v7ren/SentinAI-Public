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