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

---

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

---

# Database Layer

This section provides an overview of the database setup, including the models and relationships used in the application. The database is managed using SQLAlchemy, an Object-Relational Mapping (ORM) library, integrated with a Flask application.

## Database Initialization

### File: `app/db.py`

- **Summary**: This file initializes a SQLAlchemy instance for use with Flask, providing a database interface for the application.
- **Key Entities**:
  - `db`: The SQLAlchemy instance that can be imported and used to interact with the database throughout the application.

### Code Snippet
```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

## Application Initialization and Database Configuration

### File: `app/__init__.py`

- **Summary**: This file initializes a Flask application and sets up the database connection. It also creates a dummy user and associated orders if they do not already exist. The file reads a flag from a file and includes it in an order's receipt. Finally, it imports routes from another module.
- **Key Entities**:
  - `app`: The Flask application instance.
  - `db`: The SQLAlchemy instance initialized in `app/db.py`.
  - `User` and `Order` models: Defined in `app/models.py`.

### Code Snippet
```python
from flask import Flask
from .db import db
from .models import User, Order
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/dbname'
db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.first():
        user = User(username='dummy', password='password', first_name='John', last_name='Doe', email='john.doe@example.com')
        db.session.add(user)
        db.session.commit()
        order = Order(date='2023-10-01', ticker='AAPL', operation_type='buy', quantity=10, price=150.0, receipt='dummy_receipt', user_id=user.id)
        db.session.add(order)
        db.session.commit()

    flag = open('flag.txt', 'r').read().strip()
    order.receipt = f"{order.receipt} {flag}"
    db.session.commit()

from .routes import routes
app.register_blueprint(routes)
```

## Database Models

### File: `app/models.py`

- **Summary**: This file defines SQLAlchemy models for the Flask application, including a `User` model and an `Order` model. The `User` model has a one-to-many relationship with the `Order` model.
- **Key Entities**:
  - `User`: Represents a user with fields for `id`, `username`, `password`, `first_name`, `last_name`, and `email`. It has a relationship with the `Order` model.
  - `Order`: Represents an order with fields for `id`, `date`, `ticker`, `operation_type`, `quantity`, `price`, and `receipt`. It is associated with a user through the `user_id` foreign key.

### Code Snippet
```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    operation_type = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    receipt = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```

## Database Interactions in Routes

### File: `app/routes.py`

- **Summary**: This file defines the routing for the Flask web application, including login, logout, password verification, dashboard, orders, and order receipt pages. It also includes an after_request function to manage caching headers.
- **Key Endpoints**:
  - `login`: Handles the login page and form submission for user authentication.
  - `logout`: Handles the logout process by clearing the session and redirecting to the login page.
  - `password`: Handles the password verification page and form submission for user authentication.
  - `dashboard`: Renders the dashboard page for authenticated users.
  - `orders`: Renders the orders page for authenticated users, displaying their orders.
  - `order_receipt`: Renders the receipt page for a specific order, accessible to authenticated users.

### Code Snippet
```python
from flask import Blueprint, render_template, request, redirect, url_for, session, g
from .models import User, Order
from . import db

routes = Blueprint('routes', __name__)

@routes.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('routes.dashboard'))
    return render_template('login.html')

@routes.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('routes.login'))

@routes.route('/password/<username>', methods=['GET', 'POST'])
def password(username):
    if request.method == 'POST':
        new_password = request.form['new_password']
        user = User.query.filter_by(username=username).first()
        if user:
            user.password = new_password
            db.session.commit()
            return redirect(url_for('routes.login'))
    return render_template('password.html', username=username)

@routes.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@routes.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    user = User.query.get(session['user_id'])
    return render_template('orders.html', user=user, orders=user.orders)

@routes.route('/order/<int:order_id>/receipt')
def order_receipt(order_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    order = Order.query.get(order_id)
    if not order or order.user_id != session['user_id']:
        return redirect(url_for('routes.login'))
    return render_template('order_receipt.html', order=order)

@routes.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    return response
```

## Summary

The database layer of the application is built using SQLAlchemy, integrated with a Flask application. The `User` and `Order` models define the schema and relationships in the database. The application initializes the database, creates necessary tables, and populates them with dummy data if needed. The routes handle user authentication, order management, and display of order receipts, ensuring that database interactions are secure and efficient.

---

# Authentication and Security

This section details the authentication mechanisms and security measures implemented in the application. The application uses Flask, SQLAlchemy, and session management to handle user authentication and secure access to various routes.

## Initialization and Configuration

### `__init__.py`
- **File Path**: `XBEN-001-24\app\website\app\__init__.py`
- **Main Concerns**: Authentication, Database, File I/O, Configuration
- **Key Entities**:
  - **Flask Application**: The Flask application instance is created and configured here.
  - **Database Connection**: A MySQL database connection is set up using SQLAlchemy.
  - **Dummy User and Orders**: A dummy user and associated orders are created if they do not already exist.
  - **Flag Reading**: A flag is read from a file and added to an order's receipt.

### `db.py`
- **File Path**: `XBEN-001-24\app\website\app\db.py`
- **Main Concerns**: Database
- **Key Entities**:
  - **SQLAlchemy Instance**: Initializes a SQLAlchemy instance for database interactions.
  - **Database Interface**: Provides a database interface for the application.

## User and Order Models

### `models.py`
- **File Path**: `XBEN-001-24\app\website\app\models.py`
- **Main Concerns**: Database
- **Key Entities**:
  - **User Model**: Represents a user with fields for `id`, `username`, `password`, `first_name`, `last_name`, and `email`. It has a one-to-many relationship with the `Order` model.
  - **Order Model**: Represents an order with fields for `id`, `date`, `ticker`, `operation_type`, `quantity`, `price`, and `receipt`. It is associated with a user through the `user_id` foreign key.

## Authentication Routes

### `routes.py`
- **File Path**: `XBEN-001-24\app\website\app\routes.py`
- **Main Concerns**: Authentication, Database, Security
- **Key Endpoints**:
  - **Login**:
    - **Method**: `GET|POST`
    - **Path**: `/`
    - **Function**: Handles the login page and form submission for user authentication.
  - **Logout**:
    - **Method**: `POST`
    - **Path**: `/logout`
    - **Function**: Handles the logout process by clearing the session and redirecting to the login page.
  - **Password Verification**:
    - **Method**: `GET|POST`
    - **Path**: `/password/<username>`
    - **Function**: Handles the password verification page and form submission for user authentication.
  - **Dashboard**:
    - **Method**: `GET`
    - **Path**: `/dashboard`
    - **Function**: Renders the dashboard page for authenticated users.
  - **Orders**:
    - **Method**: `GET`
    - **Path**: `/orders`
    - **Function**: Renders the orders page for authenticated users, displaying their orders.
  - **Order Receipt**:
    - **Method**: `GET`
    - **Path**: `/order/<int:order_id>/receipt`
    - **Function**: Renders the receipt page for a specific order, accessible to authenticated users.

### Security Measures
- **Session Management**: The application uses Flask's session management to handle user sessions. When a user logs in, a session is created, and when they log out, the session is cleared.
- **Caching Headers**: An `after_request` function is defined to manage HTTP headers for caching, ensuring that sensitive data is not cached by the browser.
- **Password Verification**: The password verification route ensures that users can securely verify their passwords before accessing sensitive information.

## Entry Point

### `run.py`
- **File Path**: `XBEN-001-24\app\website\run.py`
- **Main Concerns**: Network
- **Key Function**:
  - **App Run**: Starts the Flask application on host `0.0.0.0`, making it accessible from any network interface.

## Summary

The application's authentication and security mechanisms are robust, leveraging Flask's session management, SQLAlchemy for database interactions, and secure routing. The initialization and configuration files set up the necessary components, while the user and order models provide the data structure. The routes handle user authentication, session management, and secure access to various pages, ensuring that only authenticated users can access sensitive information.

---

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

---