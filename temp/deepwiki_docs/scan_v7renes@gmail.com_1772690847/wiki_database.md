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