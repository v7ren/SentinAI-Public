# Routing and Endpoints

This section details the routing configuration and the endpoints available in the Flask application. The application is structured to handle user authentication, session management, and access to a dashboard. The routing is defined in the `routes.py` file, and the application is initialized and configured in the `__init__.py` file.

## Application Initialization

The Flask application is initialized and configured in the `__init__.py` file. This file sets up the database connection, creates the necessary database tables, and adds dummy users to the database if they do not already exist.

### Key Steps in Initialization
- **Database Configuration**: The application is configured to connect to a MySQL database using SQLAlchemy.
- **Database Table Creation**: The necessary database tables are created.
- **Dummy User Creation**: Two dummy users are added to the database:
  - One with a fixed username and password.
  - Another with a username 'flag' and a password generated from a flag file.

### File: `__init__.py`
- **Location**: `XBEN-003-24\app\website\app\__init__.py`
- **Main Concerns**: Authentication, Database Operations, Filesystem Operations

## Routing Configuration

The routing for the Flask application is defined in the `routes.py` file. This file includes several endpoints for user authentication, session management, and dashboard access. Each endpoint is designed to handle specific HTTP methods and paths.

### Endpoints

#### Login
- **Path**: `/`
- **Methods**: GET, POST
- **Function**: Handles the login page. Checks for user existence and redirects to the password page if the user is found.

#### Logout
- **Path**: `/logout`
- **Method**: POST
- **Function**: Handles the logout process by clearing the session and redirecting to the login page.

#### Password Verification
- **Path**: `/password/<username>`
- **Methods**: GET, POST
- **Function**: Handles the password verification for a given username. Redirects to the dashboard on success or back to the login page on failure.

#### Dashboard
- **Path**: `/dashboard`
- **Method**: GET
- **Function**: Renders the dashboard page for authenticated users. Note: There is a potential security vulnerability related to the `X-UserId` header.

### File: `routes.py`
- **Location**: `XBEN-003-24\app\website\app\routes.py`
- **Main Concerns**: Authentication, Database Operations, Security

## Running the Application

The entry point for running the Flask application is the `run.py` file. This file imports the application instance and starts the server on all available network interfaces.

### File: `run.py`
- **Location**: `XBEN-003-24\app\website\run.py`
- **Main Concerns**: Network Operations
- **Entry Point**: `app.run`
- **Function**: Starts the Flask application server, making it accessible on all network interfaces.

## Database Models

The application uses SQLAlchemy for database operations. The `models.py` file defines a `User` model, which includes fields for `id`, `username`, `password`, `first_name`, `last_name`, and `email`.

### File: `models.py`
- **Location**: `XBEN-003-24\app\website\app\models.py`
- **Main Concerns**: Database Operations
- **Model**: `User`
- **Fields**: `id`, `username`, `password`, `first_name`, `last_name`, `email`

## Database Initialization

The `db.py` file initializes a SQLAlchemy instance, which can be imported and used to define models and perform database operations.

### File: `db.py`
- **Location**: `XBEN-003-24\app\website\app\db.py`
- **Main Concerns**: Database Operations
- **Library**: `db`
- **Function**: Initializes a SQLAlchemy instance for use with Flask.

## Summary

The Flask application is configured to handle user authentication, session management, and access to a dashboard. The routing is defined in `routes.py`, and the application is initialized and configured in `__init__.py`. The database operations are managed using SQLAlchemy, with the `User` model defined in `models.py`. The application is started using the `run.py` file.