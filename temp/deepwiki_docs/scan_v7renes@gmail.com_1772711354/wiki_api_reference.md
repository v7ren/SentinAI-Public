# API Reference

This section lists and describes all the available API endpoints, including their methods, paths, and functionalities. The endpoints are defined in the `routes.py` file and are part of a Flask web application.

## Endpoints

### Index
- **Method**: GET
- **Path**: `/`
- **Description**: Redirects to the login page.
- **File**: `XBEN-104-24\app\website\app\routes.py`

### Login
- **Method**: GET, POST
- **Path**: `/login`
- **Description**: Handles user login. For GET requests, it renders the login form. For POST requests, it checks the provided credentials and sets session data if the credentials are valid.
- **File**: `XBEN-104-24\app\website\app\routes.py`

### Logout
- **Method**: GET
- **Path**: `/logout`
- **Description**: Handles user logout by clearing session data and redirecting to the login page.
- **File**: `XBEN-104-24\app\website\app\routes.py`

### Home
- **Method**: GET
- **Path**: `/home`
- **Description**: Displays the home page if the user is logged in. If the user is not logged in, it redirects to the login page.
- **File**: `XBEN-104-24\app\website\app\routes.py`

### Profile
- **Method**: GET, POST
- **Path**: `/profile`
- **Description**: Allows users to view and update their profile information. For GET requests, it displays the current profile information. For POST requests, it updates the user's profile information in the database.
- **File**: `XBEN-104-24\app\website\app\routes.py`

### Loan Details
- **Method**: GET
- **Path**: `/loan_details`
- **Description**: Displays loan details for the logged-in user. It retrieves the loan information from the database and renders it on the page.
- **File**: `XBEN-104-24\app\website\app\routes.py`

### Total Loan Payments
- **Method**: GET
- **Path**: `/total_loan_payments`
- **Description**: Calculates and returns the total loan payments based on query parameters. It performs the necessary calculations and returns the result.
- **File**: `XBEN-104-24\app\website\app\routes.py`

## Security and Caching

- **After Request Function**: The `routes.py` file includes an `after_request` function that adds headers to responses to prevent caching. This ensures that sensitive data is not cached by the browser.
- **File**: `XBEN-104-24\app\website\app\routes.py`

## Database Interactions

- **Database Initialization**: The `db.py` file initializes a SQLAlchemy database instance for use with the Flask application. This instance is used throughout the application to interact with the database.
- **File**: `XBEN-104-24\app\website\app\db.py`

- **User Model**: The `models.py` file defines a SQLAlchemy model for a User, including fields for user identification, personal information, and loan details. This model is used to query and manipulate user data in the database.
- **File**: `XBEN-104-24\app\website\app\models.py`

## Application Initialization

- **Flask App Initialization**: The `__init__.py` file initializes the Flask application, configures it to connect to a MySQL database, and sets up the database tables. It also creates a dummy user if one does not already exist in the database and imports the application's routes.
- **File**: `XBEN-104-24\app\website\app\__init__.py`

## Running the Application

- **Application Entry Point**: The `run.py` file is the entry point for running the Flask web application. It imports the Flask app instance and starts the server on all available network interfaces.
- **File**: `XBEN-104-24\app\website\run.py`

By following this API reference, you can understand the available endpoints and their functionalities, as well as how they interact with the database and other components of the application.