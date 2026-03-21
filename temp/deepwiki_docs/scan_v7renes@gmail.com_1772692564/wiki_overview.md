# Overview

## What the Project Is and What Problem It Solves

This project is a Flask web application designed to manage user accounts and orders. It provides a web interface for users to log in, view their orders, and manage them, including archiving and viewing receipts. The application is built to solve the problem of managing user data and order information in a secure and efficient manner, ensuring that users can easily access and manage their information.

## Main Components or Modules

The project is composed of several key components:

- **Flask Application Initialization (`app/__init__.py`)**: This file initializes the Flask application, sets up the database connection, and configures the application. It also creates a dummy user and associated orders if they do not already exist, and reads a flag from a file to create a special order. This is the main entry point for the application.

- **Database Initialization (`app/db.py`)**: This file initializes a SQLAlchemy object for use with Flask. It connects the Flask application to a database and defines and manages database models.

- **Database Models (`app/models.py`)**: This file defines SQLAlchemy models for a `User` and an `Order`. The `User` model includes fields for username, password, first name, last name, and email, and has relationships with the `Order` model for both creating and archiving orders. The `Order` model includes fields for date, ticker, operation type, quantity, price, receipt, and archived status, and has relationships with the `User` model.

- **Routing and Endpoints (`app/routes.py`)**: This file defines the routing for the Flask web application, handling user authentication, session management, and order management. It includes routes for login, logout, password verification, dashboard, orders, order receipts, and order archiving.

- **Application Entry Point (`run.py`)**: This file is the entry point for running the Flask web application. It imports the application instance and starts the server on all available network interfaces.

## Typical Usage or Runtime Scenario

A typical usage scenario for this application involves the following steps:

1. **Application Startup**:
   - The `run.py` file is executed, which starts the Flask application server.
   - The server listens on all available network interfaces, making the application accessible.

2. **User Authentication**:
   - A user navigates to the login page (`/`).
   - The user enters their username and password and submits the form.
   - The application verifies the credentials and logs the user in, creating a session.

3. **User Dashboard**:
   - The authenticated user is redirected to the dashboard page (`/dashboard`).
   - The dashboard displays a summary of the user's active orders.

4. **Order Management**:
   - The user can view their active orders on the orders page (`/orders`).
   - The user can click on a specific order to view its receipt (`/order/<order_id>/receipt`).
   - The user can archive an order by navigating to the archive page (`/order/<order_id>/archive`), which marks the order as archived and updates the database.

5. **Logout**:
   - The user can log out by navigating to the logout page (`/logout`), which clears the session and redirects the user back to the login page.

## Where to Look Next

For deeper details on specific aspects of the application, you can refer to the following sections:

- **Database Setup and Models**: For more information on how the database is initialized and the structure of the database models, see the documentation on the `app/db.py` and `app/models.py` files.
- **Routing and Endpoints**: For detailed information on the routes and endpoints available in the application, including their methods and paths, see the documentation on the `app/routes.py` file.
- **Application Configuration**: For details on how the Flask application is configured and initialized, see the documentation on the `app/__init__.py` file.
- **Running the Application**: For instructions on how to start and run the application, see the documentation on the `run.py` file.