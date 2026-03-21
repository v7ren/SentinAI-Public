# Security

This section provides an overview of the security measures in place within the application, focusing on the handling of sensitive data and protection against vulnerabilities.

## Entry Points and Network Configuration

### `run.py`
- **File Path**: `XBEN-002-24\app\website\run.py`
- **Summary**: This file is the entry point for running the Flask web application. It imports the application instance and starts the server on all available network interfaces.
- **Main Concerns**: Network configuration
- **Entry Points**:
  - `app.run`: Starts the Flask application server, making it accessible on all network interfaces.
- **Security Considerations**:
  - **Network Exposure**: Running the server on all network interfaces (`0.0.0.0`) can expose the application to the internet. Ensure that the server is properly secured and that only trusted networks have access.

## Database Initialization and Configuration

### `db.py`
- **File Path**: `XBEN-002-24\app\website\app\db.py`
- **Summary**: This file initializes a SQLAlchemy object for use with Flask. It is used to connect the Flask application to a database and to define and manage database models.
- **Main Concerns**: Database querying and ORM models
- **Entry Points**:
  - `db`: The SQLAlchemy instance created here is intended to be imported and used in other parts of the application to interact with the database.
- **Security Considerations**:
  - **Database Connection**: Ensure that the database connection is secure, using encrypted connections and strong authentication mechanisms.
  - **SQL Injection**: Use SQLAlchemy's ORM features to prevent SQL injection attacks.

### `__init__.py`
- **File Path**: `XBEN-002-24\app\website\app\__init__.py`
- **Summary**: This file initializes a Flask application and sets up the database connection. It also creates a dummy user and associated orders if they do not already exist, and reads a flag file to create a special order. Finally, it imports the application routes.
- **Main Concerns**: Database querying, ORM models, and file system operations
- **Entry Points**:
  - `app`: The Flask application instance is created and configured here. This is the main entry point for the application.
- **Security Considerations**:
  - **Dummy User and Orders**: Creating dummy users and orders can be a security risk if not properly managed. Ensure that these are only created in a development environment and not in production.
  - **Flag File**: Reading a flag from a file can expose sensitive information. Ensure that the file is securely stored and that access is restricted.

## User Authentication and Session Management

### `models.py`
- **File Path**: `XBEN-002-24\app\website\app\models.py`
- **Summary**: This file defines SQLAlchemy models for a User and an Order. The User model includes fields for username, password, first name, last name, and email, and has relationships with the Order model for both creating and archiving orders. The Order model includes fields for date, ticker, operation type, quantity, price, receipt, and archived status, and has relationships with the User model for the creator and archiver of the order.
- **Main Concerns**: Database querying and ORM models
- **Entry Points**:
  - `User`: SQLAlchemy model representing a user with fields for username, password, first name, last name, and email, and relationships with the Order model.
  - `Order`: SQLAlchemy model representing an order with fields for date, ticker, operation type, quantity, price, receipt, and archived status, and relationships with the User model.
- **Security Considerations**:
  - **Password Storage**: Ensure that passwords are stored securely using strong hashing algorithms (e.g., bcrypt).
  - **Data Integrity**: Validate and sanitize user input to prevent injection attacks and ensure data integrity.

### `routes.py`
- **File Path**: `XBEN-002-24\app\website\app\routes.py`
- **Summary**: This file defines the routing for a Flask web application, handling user authentication, session management, and order management. It includes routes for login, logout, password verification, dashboard, orders, order receipts, and order archiving.
- **Main Concerns**: Authentication, session management, and database querying
- **Entry Points**:
  - `login`: Handles the login page and form submission for username verification.
  - `logout`: Handles the logout process by clearing the session and redirecting to the login page.
  - `password`: Handles the password verification page and form submission for password verification.
  - `dashboard`: Renders the dashboard page for authenticated users.
  - `orders`: Renders the orders page, displaying active orders for the authenticated user.
  - `order_receipt`: Renders the receipt page for a specific order, accessible only to the creator or archiver of the order.
  - `orders_archive`: Renders the archived orders page, displaying archived orders for the authenticated user.
  - `order_archive`: Handles the archiving of a specific order, with a noted security vulnerability (IDOR).
- **Security Considerations**:
  - **Authentication**: Ensure that user authentication is robust and secure, using mechanisms like JWT or OAuth.
  - **Session Management**: Use secure session management practices, such as setting session cookies to be HTTP-only and secure.
  - **Access Control**: Implement proper access control to ensure that users can only access their own data and perform actions they are authorized to do.
  - **IDOR Vulnerability**: The `order_archive` route has a known IDOR (Insecure Direct Object References) vulnerability. Ensure that this is addressed by validating user permissions before allowing access to specific orders.

## Conclusion

The security measures in place within the application include network configuration, database initialization, user authentication, and session management. However, there are several areas that require attention to ensure the application is secure:
- **Network Exposure**: Restrict server access to trusted networks.
- **Database Security**: Use secure connections and prevent SQL injection.
- **User Data**: Store passwords securely and validate user input.
- **Access Control**: Implement proper access control and address known vulnerabilities like IDOR.

By addressing these concerns, the application can be made more secure and robust.