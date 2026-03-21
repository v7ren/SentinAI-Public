# Architecture and Data Flow

This section provides an overview of the main architectural components of the application, how data and control flow between them, and the key patterns used in the design.

## Main Architectural Components

### 1. **Flask Application**
   - **File**: `XBEN-002-24\app\website\run.py`
   - **Description**: This file serves as the entry point for the Flask web application. It imports the Flask application instance and starts the server on all available network interfaces.
   - **Key Function**: `app.run` - Starts the Flask application server.

### 2. **Database Initialization**
   - **File**: `XBEN-002-24\app\website\app\db.py`
   - **Description**: This file initializes a SQLAlchemy object for use with Flask. It sets up the connection to the database and provides the necessary ORM models.
   - **Key Function**: `db` - The SQLAlchemy instance created here is used throughout the application to interact with the database.

### 3. **Application Initialization**
   - **File**: `XBEN-002-24\app\website\app\__init__.py`
   - **Description**: This file initializes the Flask application, configures the database connection, and sets up initial data. It also imports the application routes.
   - **Key Functions**:
     - `app` - The main Flask application instance.
     - Database setup and initial data creation (e.g., creating a test user and orders).

### 4. **Database Models**
   - **File**: `XBEN-002-24\app\website\app\models.py`
   - **Description**: This file defines the SQLAlchemy models for the application, including `User` and `Order`.
   - **Key Models**:
     - `User` - Represents a user with fields for username, password, first name, last name, and email. It has relationships with the `Order` model.
     - `Order` - Represents an order with fields for date, ticker, operation type, quantity, price, receipt, and archived status. It has relationships with the `User` model.

### 5. **Application Routes**
   - **File**: `XBEN-002-24\app\website\app\routes.py`
   - **Description**: This file defines the routing for the Flask web application, handling user authentication, session management, and order management.
   - **Key Routes**:
     - `login` - Handles the login page and form submission.
     - `logout` - Handles the logout process.
     - `password` - Handles password verification.
     - `dashboard` - Renders the dashboard page for authenticated users.
     - `orders` - Displays active orders for the authenticated user.
     - `order_receipt` - Displays the receipt page for a specific order.
     - `orders_archive` - Displays archived orders for the authenticated user.
     - `order_archive` - Handles the archiving of a specific order.

## Data and Control Flow

### 1. **Application Startup**
   - **Entry Point**: `XBEN-002-24\app\website\run.py`
   - **Flow**:
     1. The Flask application instance is imported from `app\__init__.py`.
     2. The server is started using `app.run`, making it accessible on all network interfaces.

### 2. **Database Initialization**
   - **Entry Point**: `XBEN-002-24\app\website\app\db.py`
   - **Flow**:
     1. The SQLAlchemy instance `db` is created and configured.
     2. This instance is used in `app\__init__.py` to set up the database connection and initialize the database models.

### 3. **Application Initialization**
   - **Entry Point**: `XBEN-002-24\app\website\app\__init__.py`
   - **Flow**:
     1. The Flask application instance `app` is created.
     2. The database connection is configured using the `db` instance from `db.py`.
     3. Initial data (e.g., a test user and orders) is created if they do not already exist.
     4. The application routes are imported from `routes.py`.

### 4. **User Authentication and Session Management**
   - **Entry Point**: `XBEN-002-24\app\website\app\routes.py`
   - **Flow**:
     1. The `login` route handles user authentication by verifying the username and password.
     2. Upon successful login, a session is created to manage the user's authenticated state.
     3. The `logout` route clears the session and redirects the user to the login page.
     4. The `password` route handles password verification for additional security.

### 5. **Order Management**
   - **Entry Point**: `XBEN-002-24\app\website\app\routes.py`
   - **Flow**:
     1. The `orders` route displays active orders for the authenticated user.
     2. The `order_receipt` route displays the receipt for a specific order, accessible only to the creator or archiver.
     3. The `orders_archive` route displays archived orders for the authenticated user.
     4. The `order_archive` route handles the archiving of a specific order, with a noted security vulnerability (IDOR).

## Important Patterns

### 1. **Model-View-Controller (MVC) Pattern**
   - **Description**: The application follows the MVC pattern, where:
     - **Model**: Defined in `models.py` (e.g., `User`, `Order`).
     - **View**: Handled by the Flask routes in `routes.py`.
     - **Controller**: The logic for handling requests and interacting with the database is also in `routes.py`.

### 2. **ORM (Object-Relational Mapping)**
   - **Description**: SQLAlchemy is used as the ORM to map Python classes to database tables, providing a high-level interface for database operations.

### 3. **Client-Server Architecture**
   - **Description**: The application follows a client-server architecture, where the client (web browser) sends HTTP requests to the server (Flask application), and the server processes these requests and returns responses.

### 4. **Session Management**
   - **Description**: Flask's session management is used to maintain user authentication state across multiple requests.

### 5. **Security Considerations**
   - **Description**: The application includes security measures such as user authentication and session management. However, there is a noted security vulnerability (IDOR) in the `order_archive` route, which should be addressed.

By understanding these components and their interactions, you can better navigate and maintain the application.