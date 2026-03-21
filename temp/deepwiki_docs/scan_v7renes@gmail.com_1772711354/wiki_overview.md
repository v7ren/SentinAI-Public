# Overview

## What the Project Is and What Problem It Solves

This project is a Flask web application designed to manage user authentication, profile management, and loan details. It provides a secure and user-friendly interface for users to log in, view and update their personal information, and access details about their loans. The application is built to solve the common problem of managing user data and financial information in a web-based environment, ensuring that user data is securely stored and accessible only to authorized users.

## Main Components or Modules

### 1. **Database Initialization and Configuration**
   - **File:** `XBEN-104-24\app\website\app\db.py`
   - **Description:** Initializes a SQLAlchemy database instance for use with the Flask application. This file sets up the database connection and provides the `db` object, which can be used throughout the application to interact with the database.

### 2. **Flask Application Initialization**
   - **File:** `XBEN-104-24\app\website\app\__init__.py`
   - **Description:** Initializes the Flask application, configures it to connect to a MySQL database, and sets up the database tables. It also creates a dummy user if one does not already exist in the database and imports the application's routes.

### 3. **User Model**
   - **File:** `XBEN-104-24\app\website\app\models.py`
   - **Description:** Defines a SQLAlchemy model for a User, including fields for user identification, personal information, and loan details. This model is used to represent user data in the database.

### 4. **Application Routes**
   - **File:** `XBEN-104-24\app\website\app\routes.py`
   - **Description:** Defines the routing for the Flask web application, handling user authentication, profile management, and loan details. It includes routes for login, logout, home, profile, loan details, and total loan payments. The file also sets headers to prevent caching of responses.

### 5. **Application Entry Point**
   - **File:** `XBEN-104-24\app\website\run.py`
   - **Description:** This file is the entry point for running the Flask web application. It imports the Flask app instance and starts the server on all available network interfaces.

## Typical Usage or Runtime Scenario

1. **Application Startup:**
   - The application is started by running the `run.py` file, which initializes the Flask app and starts the server on all available network interfaces.
   - The `__init__.py` file is executed, configuring the Flask app to connect to a MySQL database and setting up the necessary database tables. It also creates a dummy user if one does not already exist.

2. **User Interaction:**
   - A user navigates to the application's root URL (`/`), which redirects them to the login page.
   - The user logs in by providing their credentials via the `/login` route. The application checks the credentials against the database and sets session data if the login is successful.
   - Once logged in, the user can access the home page (`/home`), view and update their profile information (`/profile`), and view their loan details (`/loan_details`).
   - The user can also calculate their total loan payments using the `/total_loan_payments` route, which takes query parameters to perform the calculation.
   - When the user is done, they can log out by accessing the `/logout` route, which clears their session data.

## Where to Look Next

- **Database Configuration and Models:**
  - For more details on how the database is configured and the structure of the User model, refer to the `db.py` and `models.py` files.
- **Application Initialization:**
  - To understand the initialization process and how the Flask app is set up, see the `__init__.py` file.
- **Routing and Endpoints:**
  - For a detailed look at the application's routes and how they handle user requests, check the `routes.py` file.
- **Running the Application:**
  - To learn how to start the application and the server, refer to the `run.py` file.

This overview should provide a clear understanding of the project's purpose, main components, and typical usage. For more in-depth information, explore the specific files and sections mentioned above.