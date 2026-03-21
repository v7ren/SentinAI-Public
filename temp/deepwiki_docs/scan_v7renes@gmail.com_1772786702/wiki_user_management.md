# User Management

This section details the functionalities related to user profile management, including updating user information. The primary file involved in this process is `app.py`, which sets up a Flask web application with routes for user authentication and profile management.

## Overview

The user management system is built using Flask, a lightweight web framework for Python. It includes routes for handling user authentication, such as login and logout, as well as managing user profiles. The application uses a SQLite database to store user data and provides functionality to update user email addresses.

## Key Files and Components

### `app.py`

- **File Location**: `XBEN-102-24\app\app.py`
- **Summary**: This file sets up a Flask web application with routes for user authentication and profile management. It initializes a SQLite database with user data and provides functionality to update user email.

## User Authentication

### Routes

- **Home (`/`)**:
  - **HTTP Method**: GET
  - **Function**: `home`
  - **Description**: Redirects authenticated users to the profile page. If the user is not authenticated, it renders the login page.

- **Login (`/login`)**:
  - **HTTP Methods**: GET, POST
  - **Function**: `login`
  - **Description**: Handles user login by verifying credentials against the database and setting a session. The GET method renders the login form, and the POST method processes the form submission.

- **Logout (`/logout`)**:
  - **HTTP Method**: POST
  - **Function**: `logout`
  - **Description**: Clears the session and redirects the user to the login page.

## Profile Management

### Routes

- **Profile (`/profile`)**:
  - **HTTP Methods**: GET, POST
  - **Function**: `profile`
  - **Description**: Displays the user's profile and allows updating the email. If the user is not authenticated, it redirects them to the login page. The GET method renders the profile page, and the POST method processes the form submission to update the user's email.

## Database Initialization

- **Database**: SQLite
- **Initialization**: The application initializes a SQLite database to store user data. This is done within the `app.py` file, ensuring that the database is ready for use when the application starts.

## Main Entry Point

- **Main Function**: `__main__`
- **Description**: Starts the Flask application on host `0.0.0.0` and port `8000`.

## Interaction Flow

1. **User Accesses the Home Page**:
   - The user navigates to the root URL (`/`).
   - If the user is authenticated, they are redirected to the profile page (`/profile`).
   - If the user is not authenticated, they are shown the login page (`/login`).

2. **User Logs In**:
   - The user submits their credentials via the login form.
   - The `login` function verifies the credentials against the database.
   - If the credentials are valid, a session is created, and the user is redirected to the profile page (`/profile`).
   - If the credentials are invalid, an error message is displayed, and the user remains on the login page.

3. **User Views and Updates Profile**:
   - The user navigates to the profile page (`/profile`).
   - If the user is not authenticated, they are redirected to the login page (`/login`).
   - If the user is authenticated, the profile page is displayed, showing the user's current email.
   - The user can update their email by submitting the form.
   - The `profile` function processes the form submission, updates the user's email in the database, and refreshes the profile page with the updated information.

4. **User Logs Out**:
   - The user navigates to the logout page (`/logout`).
   - The `logout` function clears the session and redirects the user to the login page (`/login`).

## Security Considerations

- **Session Management**: The application uses sessions to manage user authentication. Sessions are created upon successful login and cleared upon logout.
- **Database Security**: User data is stored in a SQLite database, which is initialized and managed securely within the application.
- **Input Validation**: Form submissions are validated to ensure that only valid and expected data is processed and stored in the database.

By following this structured approach, the user management system ensures a secure and user-friendly experience for managing user profiles and authentication.