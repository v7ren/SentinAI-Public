# Overview

## What the Project Is and What Problem It Solves

This project is a Flask web application designed to manage user accounts and orders. It provides a secure and user-friendly interface for users to log in, view their orders, and access order receipts. The application is built using Flask, a lightweight web framework for Python, and leverages SQLAlchemy for database operations.

The primary problem this project solves is the need for a centralized and secure system to manage user authentication, order management, and data storage. It ensures that users can easily log in, view their orders, and access detailed receipts, while the application maintains the integrity and security of the data.

## Main Components or Modules

### 1. **Database Initialization (`app/db.py`)**

- **File**: `XBEN-001-24\app\website\app\db.py`
- **Description**: This file initializes a SQLAlchemy instance, which is used throughout the application to interact with the database. It provides a convenient interface for performing database operations such as querying and managing ORM models.
- **Key Entity**: `db` - The SQLAlchemy instance that can be imported and used to interact with the database.

### 2. **Application Initialization (`app/__init__.py`)**

- **File**: `XBEN-001-24\app\website\app\__init__.py`
- **Description**: This file initializes the Flask application and sets up the database connection. It also creates a dummy user and associated orders if they do not already exist. Additionally, it reads a flag from a file and includes it in an order's receipt. Finally, it imports routes from another module.
- **Key Entity**: `app` - The Flask application instance that is the main entry point for the application.

### 3. **Routing and Endpoints (`app/routes.py`)**

- **File**: `XBEN-001-24\app\website\app\routes.py`
- **Description**: This file defines the routing for the Flask web application, including endpoints for login, logout, password verification, dashboard, orders, and order receipt pages. It also includes an after_request function to manage caching headers.
- **Key Endpoints**:
  - `login` - Handles the login page and form submission for user authentication.
  - `logout` - Handles the logout process by clearing the session and redirecting to the login page.
  - `password` - Handles the password verification page and form submission for user authentication.
  - `dashboard` - Renders the dashboard page for authenticated users.
  - `orders` - Renders the orders page for authenticated users, displaying their orders.
  - `order_receipt` - Renders the receipt page for a specific order, accessible to authenticated users.

### 4. **Database Models (`app/models.py`)**

- **File**: `XBEN-001-24\app\website\app\models.py`
- **Description**: This file defines SQLAlchemy models for the application, including the `User` and `Order` models. The `User` model has a one-to-many relationship with the `Order` model.
- **Key Models**:
  - `User` - Represents a user with fields for id, username, password, first name, last name, and email. It has a relationship with the `Order` model.
  - `Order` - Represents an order with fields for id, date, ticker, operation type, quantity, price, and receipt. It is linked to a user through the `user_id` foreign key.

### 5. **Application Entry Point (`run.py`)**

- **File**: `XBEN-001-24\app\website\run.py`
- **Description**: This file is the entry point for the Flask web application. It imports the application instance and runs it on all available network interfaces, making it accessible from any network interface.
- **Key Function**: `app.run` - Starts the Flask application on host `0.0.0.0`.

## Typical Usage or Runtime Scenario

1. **Application Startup**:
   - The application is started by running the `run.py` file, which imports the Flask application instance and runs it on all available network interfaces.
   - The `__init__.py` file initializes the Flask application, sets up the database connection, and creates a dummy user and orders if they do not already exist.

2. **User Authentication**:
   - A user navigates to the login page (`/`).
   - The user submits their credentials, which are verified by the `login` endpoint.
   - Upon successful authentication, the user is redirected to the dashboard page (`/dashboard`).

3. **Order Management**:
   - The authenticated user can view their orders by navigating to the orders page (`/orders`).
   - The user can click on a specific order to view its detailed receipt (`/order/<int:order_id>/receipt`).

4. **Logout**:
   - The user can log out by navigating to the logout page (`/logout`), which clears the session and redirects them to the login page.

## Where to Look Next

- **Database Operations**: For more details on how the application interacts with the database, refer to the `db.py` and `models.py` files.
- **Routing and Endpoints**: To understand the different routes and their functionalities, see the `routes.py` file.
- **Application Configuration**: For information on how the application is initialized and configured, check the `__init__.py` file.
- **Running the Application**: To learn how to start the application, refer to the `run.py` file.

For deeper technical details and specific implementation aspects, explore the individual files and their respective sections in the documentation.