# Authentication and Authorization

This section explains the mechanisms used for user authentication and session management within the application. The application uses Flask, SQLAlchemy, and session management to handle user authentication and maintain user sessions.

## Key Components

### 1. Database Initialization
- **File**: `XBEN-104-24\app\website\app\db.py`
- **Summary**: Initializes a SQLAlchemy database instance for use with a Flask application.
- **Main Concerns**: Database querying and ORM models.
- **Entry Points**:
  - `db`: The SQLAlchemy instance that can be used to interact with the database throughout the application.

### 2. User Model
- **File**: `XBEN-104-24\app\website\app\models.py`
- **Summary**: Defines a SQLAlchemy model for a User, including fields for user identification, authentication, personal information, and loan details.
- **Main Concerns**: Database querying and ORM models.
- **Entry Points**:
  - `User`: SQLAlchemy model for user data, including personal and loan information.

### 3. Flask Application Initialization
- **File**: `XBEN-104-24\app\website\app\__init__.py`
- **Summary**: Initializes a Flask application, configures it to connect to a MySQL database, and sets up the database tables. It also creates a dummy user if one does not already exist in the database. Finally, it imports the application's routes.
- **Main Concerns**: Authentication, database querying, and configuration.
- **Entry Points**:
  - `Flask app`: The Flask application is initialized and configured in this file, serving as the entry point for HTTP requests.

### 4. Application Routes
- **File**: `XBEN-104-24\app\website\app\routes.py`
- **Summary**: Defines the routing for a Flask web application, handling user authentication, profile management, and loan details. It includes routes for login, logout, home, profile, loan details, and total loan payments. The file also sets headers to prevent caching of responses.
- **Main Concerns**: Authentication, database querying, and security.
- **Entry Points**:
  - `index`: Redirects to the login page.
  - `login`: Handles user login, checking credentials and setting session data.
  - `logout`: Handles user logout by clearing session data.
  - `home`: Displays the home page if the user is logged in, otherwise redirects to the login page.
  - `profile`: Allows users to view and update their profile information.
  - `loan_details`: Displays loan details for the logged-in user.
  - `total_loan_payments`: Calculates and returns the total loan payments based on query parameters.

## Authentication Flow

### 1. User Login
- **Route**: `/login` (GET, POST)
- **Description**: The login route handles user authentication. When a user submits their credentials (username and password), the application checks these credentials against the `User` model in the database. If the credentials are valid, a session is created, and the user is redirected to the home page. If the credentials are invalid, an error message is displayed.

### 2. User Logout
- **Route**: `/logout` (GET)
- **Description**: The logout route clears the user's session data, effectively logging them out of the application. The user is then redirected to the login page.

### 3. Home Page
- **Route**: `/home` (GET)
- **Description**: The home page route checks if the user is logged in by verifying the session data. If the user is logged in, the home page is displayed. If the user is not logged in, they are redirected to the login page.

### 4. Profile Management
- **Route**: `/profile` (GET, POST)
- **Description**: The profile route allows users to view and update their profile information. The route checks if the user is logged in and retrieves the user's data from the `User` model. If the user submits updated information, the changes are saved to the database.

### 5. Loan Details
- **Route**: `/loan_details` (GET)
- **Description**: The loan details route displays loan information for the logged-in user. The route checks if the user is logged in and retrieves the loan details from the `User` model.

### 6. Total Loan Payments
- **Route**: `/total_loan_payments` (GET)
- **Description**: The total loan payments route calculates and returns the total loan payments based on query parameters. The route checks if the user is logged in and retrieves the necessary data from the `User` model to perform the calculation.

## Security Measures

- **Session Management**: The application uses Flask's session management to handle user sessions. Session data is stored on the server side, and a session cookie is sent to the client to maintain the session state.
- **Caching Prevention**: The `routes.py` file includes an `after_request` function that adds headers to responses to prevent caching, ensuring that sensitive data is not cached by the browser.

## Summary

The authentication and authorization mechanisms in the application are designed to ensure secure user management and session handling. The `User` model in the database stores user information, and the Flask application routes handle user authentication, session management, and profile management. Security measures such as session management and caching prevention are implemented to protect user data.