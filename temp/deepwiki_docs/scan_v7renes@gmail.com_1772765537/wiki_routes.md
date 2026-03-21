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