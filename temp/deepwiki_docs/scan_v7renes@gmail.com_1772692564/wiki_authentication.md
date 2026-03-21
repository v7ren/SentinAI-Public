# Authentication and Authorization

This section details how user authentication and session management are handled in the application, including the processes for login, logout, and password verification.

## Overview

The authentication and authorization mechanisms in this Flask application are primarily managed through the following components:

- **Flask Application Initialization**: The main entry point for the application.
- **Database Models**: Define the structure of user and order data.
- **Routing**: Handle HTTP requests for user authentication and session management.

## Flask Application Initialization

### File: `XBEN-002-24\app\website\app\__init__.py`

This file initializes the Flask application and sets up the database connection. It also creates a dummy user and associated orders if they do not already exist, and reads a flag file to create a special order.

- **Main Concerns**:
  - Database querying and ORM models
  - Filesystem operations
  - Configuration

- **Key Functions**:
  - **`app`**: The Flask application instance is created and configured here. This is the main entry point for the application.

## Database Models

### File: `XBEN-002-24\app\website\app\models.py`

This file defines SQLAlchemy models for a `User` and an `Order`.

- **Main Concerns**:
  - Database querying and ORM models

- **Models**:
  - **`User`**:
    - Fields: `username`, `password`, `first_name`, `last_name`, `email`
    - Relationships: 
      - `orders`: Orders created by the user
      - `archived_orders`: Orders archived by the user
  - **`Order`**:
    - Fields: `date`, `ticker`, `operation_type`, `quantity`, `price`, `receipt`, `archived_status`
    - Relationships:
      - `creator`: User who created the order
      - `archiver`: User who archived the order

## Routing

### File: `XBEN-002-24\app\website\app\routes.py`

This file defines the routing for the Flask web application, handling user authentication, session management, and order management.

- **Main Concerns**:
  - Authentication, login, session, JWT, OAuth, permissions
  - Database querying and ORM models

- **Routes**:
  - **`login`**:
    - **Path**: `/`
    - **Methods**: `GET`, `POST`
    - **Details**: Handles the login page and form submission for username verification.
  - **`logout`**:
    - **Path**: `/logout`
    - **Methods**: `POST`
    - **Details**: Handles the logout process by clearing the session and redirecting to the login page.
  - **`password`**:
    - **Path**: `/password/<username>`
    - **Methods**: `GET`, `POST`
    - **Details**: Handles the password verification page and form submission for password verification.
  - **`dashboard`**:
    - **Path**: `/dashboard`
    - **Methods**: `GET`
    - **Details**: Renders the dashboard page for authenticated users.
  - **`orders`**:
    - **Path**: `/orders`
    - **Methods**: `GET`
    - **Details**: Renders the orders page, displaying active orders for the authenticated user.
  - **`order_receipt`**:
    - **Path**: `/order/<int:order_id>/receipt`
    - **Methods**: `GET`
    - **Details**: Renders the receipt page for a specific order, accessible only to the creator or archiver of the order.
  - **`orders_archive`**:
    - **Path**: `/orders_archive`
    - **Methods**: `GET`
    - **Details**: Renders the archived orders page, displaying archived orders for the authenticated user.
  - **`order_archive`**:
    - **Path**: `/order/<int:order_id>/archive`
    - **Methods**: `GET`
    - **Details**: Handles the archiving of a specific order. It checks if the user is logged in, retrieves the order from the database, marks it as archived, and updates the database. If the user is not logged in, it redirects to the login page. Note: This route has a security vulnerability (IDOR).

## Security Considerations

- **Session Management**: The application uses Flask's session management to handle user sessions. Sessions are cleared upon logout.
- **Password Verification**: Password verification is handled through the `password` route, ensuring that only valid users can access protected resources.
- **Access Control**: Routes such as `order_receipt` and `order_archive` enforce access control by checking if the user is the creator or archiver of the order.
- **Security Vulnerability**: The `order_archive` route has a known security vulnerability (IDOR) that needs to be addressed to prevent unauthorized access to order archiving.

## Conclusion

The authentication and authorization mechanisms in this Flask application are designed to ensure secure user management and session handling. The routes and models work together to provide a robust system for user login, logout, and order management. However, it is important to address the identified security vulnerability to enhance the overall security of the application.