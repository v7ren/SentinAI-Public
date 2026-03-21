# Routing and Endpoints

This section provides an overview of the application's routing system and the available endpoints for user interaction. The routing is managed by Flask, and the endpoints handle various user actions such as login, logout, password verification, and accessing user-specific data.

## Application Initialization and Configuration

### `__init__.py` (Initialization)
- **File Path**: `XBEN-001-24\app\website\app\__init__.py`
- **Main Concerns**: Authentication, Database Operations, File System Operations
- **Entry Points**:
  - `app`: The Flask application instance is created and configured here. This is the main entry point for the application.
- **Key Functions**:
  - Initializes a Flask application.
  - Configures a MySQL database connection.
  - Creates database tables.
  - Adds a dummy user and orders to the database if they do not already exist.
  - Reads a flag from a file and adds it as an order receipt.
  - Imports routes from the `routes.py` module.

## Database Configuration

### `db.py` (Database Initialization)
- **File Path**: `XBEN-001-24\app\website\app\db.py`
- **Main Concerns**: Database Querying, ORM Models
- **Entry Points**:
  - `db`: The SQLAlchemy instance that can be imported and used to interact with the database throughout the application.
- **Key Functions**:
  - Initializes a SQLAlchemy instance for use with Flask.

### `models.py` (Database Models)
- **File Path**: `XBEN-001-24\app\website\app\models.py`
- **Main Concerns**: Database Querying, ORM Models
- **Entry Points**:
  - `User`: SQLAlchemy model representing a user with fields for id, username, password, first name, last name, and email. Also has a relationship with the Order model.
  - `Order`: SQLAlchemy model representing an order with fields for id, date, ticker, operation type, quantity, price, and receipt. It is associated with a user through the user_id foreign key.
- **Key Functions**:
  - Defines two SQLAlchemy models, `User` and `Order`, which represent users and their orders in the database.

## Routing and Endpoints

### `routes.py` (Routing)
- **File Path**: `XBEN-001-24\app\website\app\routes.py`
- **Main Concerns**: Authentication, Database Operations
- **Entry Points**:
  - `login`: Handles the login page and form submission for user authentication.
  - `logout`: Handles the logout process by clearing the session and redirecting to the login page.
  - `password`: Handles the password verification page and form submission for user authentication.
  - `dashboard`: Renders the dashboard page for authenticated users.
  - `orders`: Renders the orders page for authenticated users, displaying their orders.
  - `order_receipt`: Renders the receipt page for a specific order, accessible to authenticated users.
- **Endpoints**:
  - `GET|POST /`: Login page and form submission.
  - `POST /logout`: Logout process.
  - `GET|POST /password/<username>`: Password verification page and form submission.
  - `GET /dashboard`: Dashboard page for authenticated users.
  - `GET /orders`: Orders page for authenticated users.
  - `GET /order/<int:order_id>/receipt`: Receipt page for a specific order.

### `run.py` (Application Entry Point)
- **File Path**: `XBEN-001-24\app\website\run.py`
- **Main Concerns**: Network Operations
- **Entry Points**:
  - `app.run`: Starts the Flask application on host '0.0.0.0', making it accessible from any network interface.
- **Key Functions**:
  - Imports the app instance and runs it on the specified host when the script is executed directly.

## Interaction Flow

1. **Application Initialization**:
   - The application is initialized in `__init__.py`, where the Flask app is created, the database is configured, and initial data (dummy user and orders) are added if necessary.
   - The `db.py` file initializes the SQLAlchemy instance, which is used throughout the application for database interactions.
   - The `models.py` file defines the `User` and `Order` models, which are used to represent users and their orders in the database.

2. **Routing and Endpoints**:
   - The `routes.py` file defines the routing for the application, including endpoints for login, logout, password verification, dashboard, orders, and order receipts.
   - The `run.py` file starts the Flask application, making it accessible on all network interfaces.

3. **User Interaction**:
   - **Login**: Users can access the login page at `GET|POST /` to authenticate. Upon successful login, they are redirected to the dashboard.
   - **Logout**: Users can log out by accessing `POST /logout`, which clears their session and redirects them to the login page.
   - **Password Verification**: Users can verify their password at `GET|POST /password/<username>`.
   - **Dashboard**: Authenticated users can access the dashboard at `GET /dashboard`.
   - **Orders**: Authenticated users can view their orders at `GET /orders`.
   - **Order Receipt**: Authenticated users can view the receipt for a specific order at `GET /order/<int:order_id>/receipt`.

By following this structure, the application ensures a clear and organized flow of user interactions, with each endpoint handling specific user actions and data retrieval.