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

---

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

---

# Data Layer

This section details the database structure of the application, including the SQLAlchemy models and how they are used to manage user and loan data.

## Database Initialization

### File: `app/db.py`

The database is initialized using SQLAlchemy, a powerful ORM (Object-Relational Mapping) library for Python. The `db` instance is created and can be used throughout the application to interact with the database.

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

### File: `app/__init__.py`

The Flask application is configured to connect to a MySQL database in the `__init__.py` file. This file also sets up the database tables and adds a dummy user if one does not already exist.

```python
from flask import Flask
from .db import db
from .models import User
from .routes import routes

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/dbname'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()
        if not User.query.first():
            db.session.add(User(username='dummy', password='dummy', email='dummy@example.com'))
            db.session.commit()

    app.register_blueprint(routes)
    return app
```

## SQLAlchemy Models

### File: `app/models.py`

The `models.py` file defines the SQLAlchemy model for the `User` entity. This model includes fields for user identification, personal information, and loan details.

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    loan_amount = db.Column(db.Float, nullable=True)
    loan_term = db.Column(db.Integer, nullable=True)
    interest_rate = db.Column(db.Float, nullable=True)
```

### Fields in the User Model

- **id**: Primary key for the user.
- **username**: Unique username for the user.
- **password**: User's password (should be hashed in a real application).
- **email**: Unique email address for the user.
- **first_name**: User's first name (optional).
- **last_name**: User's last name (optional).
- **loan_amount**: Amount of the loan (optional).
- **loan_term**: Term of the loan in months (optional).
- **interest_rate**: Interest rate for the loan (optional).

## Database Interactions

### File: `app/routes.py`

The `routes.py` file defines several Flask routes that interact with the database using the `User` model. These routes handle user authentication, profile management, and loan details.

#### User Authentication

- **Login**: The `login` route handles user login by checking credentials and setting session data.
- **Logout**: The `logout` route handles user logout by clearing session data.

```python
from flask import Blueprint, request, session, redirect, url_for
from .models import User
from .db import db

routes = Blueprint('routes', __name__)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('routes.home'))
        else:
            return 'Invalid credentials'
    return 'Login page'

@routes.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('routes.index'))
```

#### Profile Management

- **Profile**: The `profile` route allows users to view and update their profile information.

```python
@routes.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('routes.login'))
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        db.session.commit()
        return 'Profile updated'
    return f'Profile: {user.first_name} {user.last_name}'
```

#### Loan Details

- **Loan Details**: The `loan_details` route displays loan details for the logged-in user.
- **Total Loan Payments**: The `total_loan_payments` route calculates and returns the total loan payments based on query parameters.

```python
@routes.route('/loan_details')
def loan_details():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('routes.login'))
    user = User.query.get(user_id)
    return f'Loan Details: Amount: {user.loan_amount}, Term: {user.loan_term}, Interest Rate: {user.interest_rate}'

@routes.route('/total_loan_payments')
def total_loan_payments():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('routes.login'))
    user = User.query.get(user_id)
    if user.loan_amount and user.loan_term and user.interest_rate:
        monthly_interest_rate = user.interest_rate / 12 / 100
        total_payments = user.loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** user.loan_term) / ((1 + monthly_interest_rate) ** user.loan_term - 1)
        return f'Total Loan Payments: {total_payments:.2f}'
    return 'Loan details not available'
```

## Summary

The data layer of the application is built using SQLAlchemy to manage user and loan data. The `User` model is defined in `models.py` and is used in various routes to handle user authentication, profile management, and loan details. The database is initialized and configured in `__init__.py`, and the `db` instance is used throughout the application to interact with the database.

---

# Authentication and Authorization

This section explains the mechanisms used for user authentication and session management within the application. The application uses Flask, SQLAlchemy, and session management to handle user authentication and maintain user sessions.

## Key Components

### 1. Database Initialization
- **File**: `XBEN-104-24\app\website\app\db.py`
- **Summary**: Initializes a SQLAlchemy database instance for use with a Flask application.
- **Main Concerns**: Database querying and ORM models.
- **Entry Points**:
  - `db`: The SQLAlchemy instance that can be used to interact with the database throughout the application.

### 2. User Model
- **File**: `XBEN-104-24\app\website\app\models.py`
- **Summary**: Defines a SQLAlchemy model for a User, including fields for user identification, authentication, personal information, and loan details.
- **Main Concerns**: Database querying and ORM models.
- **Entry Points**:
  - `User`: SQLAlchemy model for user data, including personal and loan information.

### 3. Flask Application Initialization
- **File**: `XBEN-104-24\app\website\app\__init__.py`
- **Summary**: Initializes a Flask application, configures it to connect to a MySQL database, and sets up the database tables. It also creates a dummy user if one does not already exist in the database. Finally, it imports the application's routes.
- **Main Concerns**: Authentication, database querying, and configuration.
- **Entry Points**:
  - `Flask app`: The Flask application is initialized and configured in this file, serving as the entry point for HTTP requests.

### 4. Application Routes
- **File**: `XBEN-104-24\app\website\app\routes.py`
- **Summary**: Defines the routing for a Flask web application, handling user authentication, profile management, and loan details. It includes routes for login, logout, home, profile, loan details, and total loan payments. The file also sets headers to prevent caching of responses.
- **Main Concerns**: Authentication, database querying, and security.
- **Entry Points**:
  - `index`: Redirects to the login page.
  - `login`: Handles user login, checking credentials and setting session data.
  - `logout`: Handles user logout by clearing session data.
  - `home`: Displays the home page if the user is logged in, otherwise redirects to the login page.
  - `profile`: Allows users to view and update their profile information.
  - `loan_details`: Displays loan details for the logged-in user.
  - `total_loan_payments`: Calculates and returns the total loan payments based on query parameters.

## Authentication Flow

### 1. User Login
- **Route**: `/login` (GET, POST)
- **Description**: The login route handles user authentication. When a user submits their credentials (username and password), the application checks these credentials against the `User` model in the database. If the credentials are valid, a session is created, and the user is redirected to the home page. If the credentials are invalid, an error message is displayed.

### 2. User Logout
- **Route**: `/logout` (GET)
- **Description**: The logout route clears the user's session data, effectively logging them out of the application. The user is then redirected to the login page.

### 3. Home Page
- **Route**: `/home` (GET)
- **Description**: The home page route checks if the user is logged in by verifying the session data. If the user is logged in, the home page is displayed. If the user is not logged in, they are redirected to the login page.

### 4. Profile Management
- **Route**: `/profile` (GET, POST)
- **Description**: The profile route allows users to view and update their profile information. The route checks if the user is logged in and retrieves the user's data from the `User` model. If the user submits updated information, the changes are saved to the database.

### 5. Loan Details
- **Route**: `/loan_details` (GET)
- **Description**: The loan details route displays loan information for the logged-in user. The route checks if the user is logged in and retrieves the loan details from the `User` model.

### 6. Total Loan Payments
- **Route**: `/total_loan_payments` (GET)
- **Description**: The total loan payments route calculates and returns the total loan payments based on query parameters. The route checks if the user is logged in and retrieves the necessary data from the `User` model to perform the calculation.

## Security Measures

- **Session Management**: The application uses Flask's session management to handle user sessions. Session data is stored on the server side, and a session cookie is sent to the client to maintain the session state.
- **Caching Prevention**: The `routes.py` file includes an `after_request` function that adds headers to responses to prevent caching, ensuring that sensitive data is not cached by the browser.

## Summary

The authentication and authorization mechanisms in the application are designed to ensure secure user management and session handling. The `User` model in the database stores user information, and the Flask application routes handle user authentication, session management, and profile management. Security measures such as session management and caching prevention are implemented to protect user data.

---

# API Reference

This section lists and describes all the available API endpoints, including their methods, paths, and functionalities. The endpoints are defined in the `routes.py` file and are part of a Flask web application.

## Endpoints

### Index
- **Method**: GET
- **Path**: `/`
- **Description**: Redirects to the login page.
- **File**: `XBEN-104-24\app\website\app\routes.py`

### Login
- **Method**: GET, POST
- **Path**: `/login`
- **Description**: Handles user login. For GET requests, it renders the login form. For POST requests, it checks the provided credentials and sets session data if the credentials are valid.
- **File**: `XBEN-104-24\app\website\app\routes.py`

### Logout
- **Method**: GET
- **Path**: `/logout`
- **Description**: Handles user logout by clearing session data and redirecting to the login page.
- **File**: `XBEN-104-24\app\website\app\routes.py`

### Home
- **Method**: GET
- **Path**: `/home`
- **Description**: Displays the home page if the user is logged in. If the user is not logged in, it redirects to the login page.
- **File**: `XBEN-104-24\app\website\app\routes.py`

### Profile
- **Method**: GET, POST
- **Path**: `/profile`
- **Description**: Allows users to view and update their profile information. For GET requests, it displays the current profile information. For POST requests, it updates the user's profile information in the database.
- **File**: `XBEN-104-24\app\website\app\routes.py`

### Loan Details
- **Method**: GET
- **Path**: `/loan_details`
- **Description**: Displays loan details for the logged-in user. It retrieves the loan information from the database and renders it on the page.
- **File**: `XBEN-104-24\app\website\app\routes.py`

### Total Loan Payments
- **Method**: GET
- **Path**: `/total_loan_payments`
- **Description**: Calculates and returns the total loan payments based on query parameters. It performs the necessary calculations and returns the result.
- **File**: `XBEN-104-24\app\website\app\routes.py`

## Security and Caching

- **After Request Function**: The `routes.py` file includes an `after_request` function that adds headers to responses to prevent caching. This ensures that sensitive data is not cached by the browser.
- **File**: `XBEN-104-24\app\website\app\routes.py`

## Database Interactions

- **Database Initialization**: The `db.py` file initializes a SQLAlchemy database instance for use with the Flask application. This instance is used throughout the application to interact with the database.
- **File**: `XBEN-104-24\app\website\app\db.py`

- **User Model**: The `models.py` file defines a SQLAlchemy model for a User, including fields for user identification, personal information, and loan details. This model is used to query and manipulate user data in the database.
- **File**: `XBEN-104-24\app\website\app\models.py`

## Application Initialization

- **Flask App Initialization**: The `__init__.py` file initializes the Flask application, configures it to connect to a MySQL database, and sets up the database tables. It also creates a dummy user if one does not already exist in the database and imports the application's routes.
- **File**: `XBEN-104-24\app\website\app\__init__.py`

## Running the Application

- **Application Entry Point**: The `run.py` file is the entry point for running the Flask web application. It imports the Flask app instance and starts the server on all available network interfaces.
- **File**: `XBEN-104-24\app\website\run.py`

By following this API reference, you can understand the available endpoints and their functionalities, as well as how they interact with the database and other components of the application.

---