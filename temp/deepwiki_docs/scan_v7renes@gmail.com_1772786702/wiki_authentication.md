# Authentication and Security

This section covers the authentication mechanisms in the application, including login, logout, and session management. The primary file of interest is `app.py`, which sets up the Flask web application and handles user authentication.

## Overview

The application uses Flask to manage user sessions and provides routes for logging in, logging out, and managing user profiles. It also initializes a SQLite database to store user data. The authentication process involves verifying user credentials, setting session data, and managing user sessions.

## Key Files and Functions

### `app.py`

- **File Location**: `XBEN-102-24\app\app.py`
- **Summary**: This file sets up a Flask web application with routes for user authentication, including login, logout, and profile management. It initializes a SQLite database with user data and provides functionality to update user email.

#### Routes and Endpoints

- **Home (`/`)**:
  - **Method**: GET
  - **Function**: `home`
  - **Description**: Redirects authenticated users to the profile page. If the user is not authenticated, it renders the login page.

- **Login (`/login`)**:
  - **Method**: GET, POST
  - **Function**: `login`
  - **Description**: Handles user login by verifying credentials against the database and setting a session. On a GET request, it renders the login form. On a POST request, it processes the login form data.

- **Logout (`/logout`)**:
  - **Method**: POST
  - **Function**: `logout`
  - **Description**: Clears the session and redirects the user to the login page.

- **Profile (`/profile`)**:
  - **Method**: GET, POST
  - **Function**: `profile`
  - **Description**: Displays the user's profile and allows updating the email. If the user is not authenticated, it redirects them to the login page. On a POST request, it processes the form data to update the user's email.

#### Main Function

- **Function**: `__main__`
  - **Description**: Starts the Flask application on host `0.0.0.0` and port `8000`.

## Authentication Flow

1. **Home Page (`/`)**:
   - When a user accesses the home page, the application checks if the user is authenticated.
   - If the user is authenticated, they are redirected to the profile page.
   - If the user is not authenticated, the login page is rendered.

2. **Login (`/login`)**:
   - The user accesses the login page via a GET request.
   - The user submits their credentials via a POST request.
   - The application verifies the credentials against the SQLite database.
   - If the credentials are valid, a session is created, and the user is redirected to the profile page.
   - If the credentials are invalid, an error message is displayed, and the user remains on the login page.

3. **Profile (`/profile`)**:
   - The user accesses the profile page via a GET request.
   - If the user is authenticated, their profile information is displayed.
   - If the user is not authenticated, they are redirected to the login page.
   - The user can update their email via a POST request.
   - If the update is successful, the user remains on the profile page with a success message.
   - If the update fails, an error message is displayed.

4. **Logout (`/logout`)**:
   - The user accesses the logout endpoint via a POST request.
   - The session is cleared, and the user is redirected to the login page.

## Security Considerations

- **Session Management**: The application uses Flask's session management to handle user sessions. Sessions are stored server-side, and a session cookie is sent to the client.
- **Database Security**: User data is stored in a SQLite database. The application ensures that user credentials are verified securely before creating a session.
- **Input Validation**: The application validates user input to prevent SQL injection and other security vulnerabilities.
- **Error Handling**: The application handles errors gracefully and provides appropriate feedback to the user.

By following these steps and considerations, the application ensures a secure and user-friendly authentication process.