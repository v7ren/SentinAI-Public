# Architecture and Data Flow

This section provides an overview of the main architectural components, data flow, and important patterns used in the project. The architecture is primarily based on a Flask web application with a MySQL database, and it follows a client-server model with a focus on user authentication and data management.

## Main Architectural Components

### 1. **Flask Application**
- **File**: `XBEN-104-24\app\website\app\__init__.py`
- **Description**: This file initializes the Flask application, configures it to connect to a MySQL database, and sets up the necessary database tables. It also creates a dummy user if one does not already exist and imports the application's routes.
- **Key Functions**:
  - `create_app()`: Initializes the Flask app and configures the database.
  - `create_tables()`: Creates the necessary database tables.
  - `create_dummy_user()`: Adds a dummy user to the database if it does not already exist.

### 2. **Database Management**
- **File**: `XBEN-104-24\app\website\app\db.py`
- **Description**: This file initializes a SQLAlchemy database instance for use with the Flask application.
- **Key Entities**:
  - `db`: The SQLAlchemy instance used to interact with the database.

### 3. **User Model**
- **File**: `XBEN-104-24\app\website\app\models.py`
- **Description**: This file defines a SQLAlchemy model for a User, including fields for user identification, authentication, personal information, and loan details.
- **Key Class**:
  - `User`: SQLAlchemy model for user data.

### 4. **Application Routes**
- **File**: `XBEN-104-24\app\website\app\routes.py`
- **Description**: This file defines the routing for the Flask web application, handling user authentication, profile management, and loan details.
- **Key Endpoints**:
  - `index()`: Redirects to the login page.
  - `login()`: Handles user login, checking credentials and setting session data.
  - `logout()`: Handles user logout by clearing session data.
  - `home()`: Displays the home page if the user is logged in, otherwise redirects to the login page.
  - `profile()`: Allows users to view and update their profile information.
  - `loan_details()`: Displays loan details for the logged-in user.
  - `total_loan_payments()`: Calculates and returns the total loan payments based on query parameters.

### 5. **Application Entry Point**
- **File**: `XBEN-104-24\app\website\run.py`
- **Description**: This file is the entry point for running the Flask web application. It imports the Flask app instance and starts the server on all available network interfaces.
- **Key Function**:
  - `app.run()`: Starts the Flask application server on host '0.0.0.0'.

## Data and Control Flow

### 1. **Application Initialization**
- **Flow**:
  1. The Flask application is initialized in `__init__.py`.
  2. The database is configured and the necessary tables are created.
  3. A dummy user is added to the database if it does not already exist.
  4. The application routes are imported from `routes.py`.

### 2. **User Authentication and Session Management**
- **Flow**:
  1. Users access the application through the `index` route, which redirects them to the login page.
  2. Users submit their credentials via the `login` route.
  3. The `login` function checks the credentials against the `User` model in the database.
  4. If the credentials are valid, a session is created, and the user is redirected to the home page.
  5. Users can log out via the `logout` route, which clears the session data.

### 3. **Profile Management**
- **Flow**:
  1. Logged-in users can access their profile via the `profile` route.
  2. The `profile` function retrieves the user's information from the `User` model and displays it.
  3. Users can update their profile information, which is then saved back to the database.

### 4. **Loan Details and Payments**
- **Flow**:
  1. Logged-in users can view their loan details via the `loan_details` route.
  2. The `loan_details` function retrieves the loan information from the `User` model and displays it.
  3. Users can calculate their total loan payments via the `total_loan_payments` route.
  4. The `total_loan_payments` function calculates the total based on query parameters and returns the result.

## Important Patterns

### 1. **Model-View-Controller (MVC) Pattern**
- **Description**: The application follows a simplified MVC pattern.
  - **Model**: The `User` model in `models.py` represents the data structure and interacts with the database.
  - **View**: The HTML templates (not shown in the provided files) would handle the presentation layer.
  - **Controller**: The routes in `routes.py` handle the business logic and control the flow of data between the model and the view.

### 2. **Client-Server Model**
- **Description**: The application is a client-server model where the client (web browser) sends HTTP requests to the server (Flask application).
  - **Client**: Web browser or any HTTP client.
  - **Server**: Flask application running on the server, handling requests and responses.

### 3. **Session Management**
- **Description**: The application uses session management to handle user authentication and maintain user state.
  - **Session**: Created and managed in the `login` and `logout` routes.

### 4. **Database ORM (Object-Relational Mapping)**
- **Description**: SQLAlchemy is used as the ORM to interact with the MySQL database.
  - **ORM**: Provides a high-level, object-oriented interface to the database, abstracting away the SQL queries.

By understanding these components and their interactions, you can better navigate and maintain the application.