# Architecture and Data Flow

## Overview

The application is a Flask web application that handles user authentication and profile management. It is structured around a client-server architecture with a focus on user authentication and session management. The main components include the Flask web server, SQLite database, and various routes for handling user interactions.

## Main Architectural Components

### 1. Flask Web Application
- **File**: `app/app.py`
- **Description**: This file sets up the Flask web application and defines the routes for user authentication and profile management.
- **Key Functions**:
  - `__main__`: Starts the Flask application on host `0.0.0.0` and port `8000`.
  - `home`: Redirects authenticated users to the profile page, otherwise renders the login page.
  - `logout`: Clears the session and redirects the user to the login page.
  - `login`: Handles user login by verifying credentials against the database and setting a session.
  - `profile`: Displays the user's profile and allows updating the email. Redirects unauthenticated users to the login page.

### 2. SQLite Database
- **Description**: The application uses a SQLite database to store user data, including credentials and profile information.
- **Initialization**:
  - The database is initialized in `app/app.py` when the Flask application starts.
  - User data is queried and updated through the defined routes.

## Data and Control Flow

### 1. User Authentication Flow
1. **Home Route (`/`)**:
   - When a user accesses the home route, the `home` function checks if the user is authenticated.
   - If authenticated, the user is redirected to the profile page (`/profile`).
   - If not authenticated, the user is redirected to the login page (`/login`).

2. **Login Route (`/login`)**:
   - The `login` function handles both GET and POST requests.
   - On a GET request, the login form is rendered.
   - On a POST request, the user's credentials are verified against the database.
   - If the credentials are valid, a session is created, and the user is redirected to the profile page (`/profile`).
   - If the credentials are invalid, an error message is displayed, and the user remains on the login page.

3. **Logout Route (`/logout`)**:
   - The `logout` function handles a POST request to clear the session and redirect the user to the login page (`/login`).

4. **Profile Route (`/profile`)**:
   - The `profile` function handles both GET and POST requests.
   - On a GET request, the user's profile is displayed.
   - On a POST request, the user can update their email address.
   - If the user is not authenticated, they are redirected to the login page (`/login`).

### 2. Database Interactions
- **Database Initialization**:
  - The SQLite database is initialized in `app/app.py` when the Flask application starts.
  - The database schema is defined to store user data, including username, password, and email.

- **Database Queries**:
  - User credentials are verified against the database during the login process.
  - User profile information is retrieved and updated from the database during profile management.

## Important Patterns

### 1. Model-View-Controller (MVC) Pattern
- **Model**: The SQLite database serves as the model, storing and managing user data.
- **View**: The HTML templates and forms rendered by the Flask application serve as the view.
- **Controller**: The Flask routes and functions in `app/app.py` act as the controller, handling user requests and updating the model.

### 2. Client-Server Architecture
- **Client**: The web browser where users interact with the application.
- **Server**: The Flask web application running on the server, handling HTTP requests and responses.

### 3. Session Management
- **Session Handling**: The application uses Flask's session management to keep track of authenticated users. Sessions are created upon successful login and cleared upon logout.

## Conclusion

The application is designed with a clear separation of concerns, leveraging Flask for the web server, SQLite for the database, and a structured flow for user authentication and profile management. The MVC pattern ensures a clean and maintainable architecture, while the client-server model supports scalable and robust web interactions.