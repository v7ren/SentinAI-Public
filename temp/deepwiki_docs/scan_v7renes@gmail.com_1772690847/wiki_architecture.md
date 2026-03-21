# Architecture and Data Flow

This section provides an overview of the main architectural components of the application, how data and control flow between them, and the important patterns used in the design.

## Main Architectural Components

### 1. **Flask Application**
- **File**: `XBEN-001-24\app\website\app\__init__.py`
- **Description**: This file initializes the Flask application and sets up the database connection. It also creates a dummy user and associated orders if they do not already exist. The file reads a flag from a file and includes it in an order's receipt. Finally, it imports routes from another module.
- **Key Entities**:
  - `app`: The Flask application instance.
  - `db`: The SQLAlchemy instance for database operations.
  - `User` and `Order` models: Defined in `models.py` and used to interact with the database.

### 2. **Database Layer**
- **File**: `XBEN-001-24\app\website\app\db.py`
- **Description**: This file initializes a SQLAlchemy instance for use with Flask, providing a database interface for the application.
- **Key Entities**:
  - `db`: The SQLAlchemy instance that can be imported and used to interact with the database throughout the application.

### 3. **Models**
- **File**: `XBEN-001-24\app\website\app\models.py`
- **Description**: This file defines SQLAlchemy models for the application, including a `User` model and an `Order` model. The `User` model has a one-to-many relationship with the `Order` model.
- **Key Entities**:
  - `User`: Represents a user with fields for `id`, `username`, `password`, `first_name`, `last_name`, and `email`. It has a relationship with the `Order` model.
  - `Order`: Represents an order with fields for `id`, `date`, `ticker`, `operation_type`, `quantity`, `price`, and `receipt`. It is associated with a user through the `user_id` foreign key.

### 4. **Routes and Controllers**
- **File**: `XBEN-001-24\app\website\app\routes.py`
- **Description**: This file defines the routing for the Flask web application, including login, logout, password verification, dashboard, orders, and order receipt pages. It also includes an `after_request` function to manage caching headers.
- **Key Endpoints**:
  - `login`: Handles the login page and form submission for user authentication.
  - `logout`: Handles the logout process by clearing the session and redirecting to the login page.
  - `password`: Handles the password verification page and form submission for user authentication.
  - `dashboard`: Renders the dashboard page for authenticated users.
  - `orders`: Renders the orders page for authenticated users, displaying their orders.
  - `order_receipt`: Renders the receipt page for a specific order, accessible to authenticated users.

### 5. **Application Entry Point**
- **File**: `XBEN-001-24\app\website\run.py`
- **Description**: This file is the entry point for the Flask web application. It imports the application instance and runs it on all available network interfaces.
- **Key Function**:
  - `app.run`: Starts the Flask application on host `0.0.0.0`, making it accessible from any network interface.

## Data and Control Flow

### 1. **Application Initialization**
- The application starts with the execution of `run.py`, which imports the `app` instance from `__init__.py` and runs it.
- In `__init__.py`, the Flask application is initialized, and the database connection is set up using the `db` instance from `db.py`.
- The application creates database tables and adds a dummy user and orders if they do not already exist.
- The application reads a flag from a file and includes it in an order's receipt.

### 2. **User Authentication and Session Management**
- The `login` endpoint in `routes.py` handles user authentication. It processes the login form submission, verifies the user credentials, and sets up the session.
- The `logout` endpoint clears the session and redirects the user to the login page.
- The `password` endpoint handles password verification, allowing users to verify their password.

### 3. **User Interaction and Data Retrieval**
- Once authenticated, users can access the `dashboard` endpoint, which renders the dashboard page.
- The `orders` endpoint retrieves and displays the user's orders.
- The `order_receipt` endpoint retrieves and displays the receipt for a specific order.

### 4. **Database Operations**
- The `User` and `Order` models in `models.py` are used to interact with the database.
- The `db` instance from `db.py` is used to perform database operations such as querying, inserting, and updating records.
- The `__init__.py` file creates the necessary database tables and populates them with initial data.

### 5. **Caching and Security**
- The `after_request` function in `routes.py` manages HTTP headers for caching, ensuring that sensitive data is not cached by the browser.

## Important Patterns

### 1. **Model-View-Controller (MVC)**
- The application follows the MVC pattern:
  - **Model**: Defined in `models.py`, the `User` and `Order` models represent the data structure and business logic.
  - **View**: The HTML templates and rendered pages serve as the view.
  - **Controller**: The routes defined in `routes.py` act as the controller, handling user requests and interacting with the models.

### 2. **Client-Server Architecture**
- The application is a client-server architecture, where the Flask web application (server) serves HTTP requests from clients (web browsers).
- The server handles user authentication, session management, and data retrieval, while the client interacts with the server through HTTP endpoints.

### 3. **Event-Driven and Layered Design**
- The application is event-driven, with routes handling specific HTTP requests and triggering the appropriate actions.
- The application is layered, with the Flask application at the top, the routes and controllers in the middle, and the database layer at the bottom.

By understanding these components and their interactions, you can better navigate and maintain the application.