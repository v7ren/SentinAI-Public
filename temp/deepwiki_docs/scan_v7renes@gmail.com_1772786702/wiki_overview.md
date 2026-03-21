# Overview

## What the Project Is and What Problem It Solves

The project is a Flask web application designed to manage user authentication and profile management. It addresses the common problem of securely handling user login, logout, and profile updates in a web application. By providing a robust set of routes and database interactions, the application ensures that user data is securely stored and managed, while also offering a seamless user experience.

## Main Components or Modules

### Flask Application
- **File**: `app/app.py`
- **Description**: This file sets up the Flask web application and defines the main routes for user authentication and profile management. It initializes a SQLite database to store user data and provides functionality to handle user sessions and JWT (JSON Web Tokens) for authentication.

### User Authentication
- **Routes**:
  - **Home (`/`)**: Redirects authenticated users to the profile page; otherwise, renders the login page.
  - **Login (`/login`)**: Handles user login by verifying credentials against the database and setting a session.
  - **Logout (`/logout`)**: Clears the session and redirects the user to the login page.
  - **Profile (`/profile`)**: Displays the user's profile and allows updating the email. Redirects unauthenticated users to the login page.

### Database Management
- **SQLite Database**: The application uses a SQLite database to store user data, including credentials and profile information. The database is initialized and managed within `app/app.py`.

## Typical Usage or Runtime Scenario

1. **User Accesses the Application**:
   - The user navigates to the root URL (`/`).
   - If the user is already authenticated, they are redirected to the profile page (`/profile`).
   - If the user is not authenticated, they are shown the login page (`/login`).

2. **User Logs In**:
   - The user enters their credentials on the login page and submits the form.
   - The application verifies the credentials against the SQLite database.
   - If the credentials are valid, a session is created, and the user is redirected to the profile page (`/profile`).
   - If the credentials are invalid, an error message is displayed, and the user remains on the login page.

3. **User Manages Profile**:
   - On the profile page, the user can view their current email and update it if needed.
   - The updated email is saved to the database.
   - The user can log out by clicking the logout link, which clears the session and redirects them to the login page.

4. **User Logs Out**:
   - The user clicks the logout link.
   - The session is cleared, and the user is redirected to the login page.

## Where to Look Next

For deeper details on specific components and functionalities, refer to the following sections:
- **Authentication and Security**: Detailed information on how user authentication, sessions, and JWTs are implemented.
- **Database Management**: In-depth explanation of the SQLite database schema and ORM (Object-Relational Mapping) models.
- **Routing and Endpoints**: Comprehensive documentation of all HTTP endpoints and their corresponding methods and paths.
- **Configuration and Deployment**: Guidelines for configuring and deploying the application in different environments.