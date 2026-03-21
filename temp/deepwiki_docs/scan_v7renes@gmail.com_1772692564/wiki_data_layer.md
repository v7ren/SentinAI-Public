# Data Layer

This section provides an overview of the database models and how data is stored and managed within the application. The data layer is built using SQLAlchemy, an Object-Relational Mapping (ORM) library, which is integrated with Flask to handle database interactions.

## Database Initialization

### File: `XBEN-002-24\app\website\app\db.py`

This file initializes a SQLAlchemy object for use with Flask. It is responsible for connecting the Flask application to the database and defining the ORM models.

- **Key Functionality**:
  - Initializes a SQLAlchemy instance.
  - Provides the `db` object that is used throughout the application to interact with the database.

- **Code Snippet**:
  ```python
  from flask_sqlalchemy import SQLAlchemy
  db = SQLAlchemy()
  ```

## Flask Application Initialization

### File: `XBEN-002-24\app\website\app\__init__.py`

This file initializes the Flask application and sets up the database connection. It also includes logic to create a dummy user and associated orders if they do not already exist, and reads a flag file to create a special order.

- **Key Functionality**:
  - Initializes the Flask application.
  - Configures a MySQL database connection.
  - Creates database tables.
  - Adds a test user and several orders to the database.
  - Reads a flag from a file and adds it to an order.

- **Code Snippet**:
  ```python
  from flask import Flask
  from .db import db
  from .models import User, Order
  from .routes import app as routes

  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/dbname'
  db.init_app(app)

  with app.app_context():
      db.create_all()
      # Add test user and orders
      if not User.query.filter_by(username='testuser').first():
          user = User(username='testuser', password='password', first_name='Test', last_name='User', email='testuser@example.com')
          db.session.add(user)
          db.session.commit()
          # Add orders
          order1 = Order(date='2023-01-01', ticker='AAPL', operation_type='BUY', quantity=10, price=150.0, receipt='receipt1', creator_id=user.id)
          order2 = Order(date='2023-01-02', ticker='GOOG', operation_type='SELL', quantity=5, price=200.0, receipt='receipt2', creator_id=user.id)
          db.session.add_all([order1, order2])
          db.session.commit()
      # Read flag file and add special order
      with open('flag.txt', 'r') as file:
          flag = file.read().strip()
          special_order = Order(date='2023-01-03', ticker='FLAG', operation_type='BUY', quantity=1, price=1.0, receipt=flag, creator_id=user.id)
          db.session.add(special_order)
          db.session.commit()

  app.register_blueprint(routes)
  ```

## Database Models

### File: `XBEN-002-24\app\website\app\models.py`

This file defines the SQLAlchemy models for the application. The models represent the structure of the data stored in the database and the relationships between different entities.

- **User Model**:
  - **Fields**:
    - `username`: Unique username for the user.
    - `password`: Password for the user.
    - `first_name`: First name of the user.
    - `last_name`: Last name of the user.
    - `email`: Email address of the user.
  - **Relationships**:
    - `created_orders`: Orders created by the user.
    - `archived_orders`: Orders archived by the user.

- **Order Model**:
  - **Fields**:
    - `date`: Date of the order.
    - `ticker`: Ticker symbol of the stock.
    - `operation_type`: Type of operation (e.g., BUY, SELL).
    - `quantity`: Quantity of the stock.
    - `price`: Price of the stock.
    - `receipt`: Receipt or additional information.
    - `archived`: Boolean indicating if the order is archived.
  - **Relationships**:
    - `creator`: User who created the order.
    - `archiver`: User who archived the order.

- **Code Snippet**:
  ```python
  from flask_sqlalchemy import SQLAlchemy
  from .db import db

  class User(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      username = db.Column(db.String(80), unique=True, nullable=False)
      password = db.Column(db.String(120), nullable=False)
      first_name = db.Column(db.String(80), nullable=False)
      last_name = db.Column(db.String(80), nullable=False)
      email = db.Column(db.String(120), unique=True, nullable=False)
      created_orders = db.relationship('Order', backref='creator', lazy=True, foreign_keys='Order.creator_id')
      archived_orders = db.relationship('Order', backref='archiver', lazy=True, foreign_keys='Order.archiver_id')

  class Order(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      date = db.Column(db.Date, nullable=False)
      ticker = db.Column(db.String(10), nullable=False)
      operation_type = db.Column(db.String(10), nullable=False)
      quantity = db.Column(db.Integer, nullable=False)
      price = db.Column(db.Float, nullable=False)
      receipt = db.Column(db.String(255), nullable=False)
      archived = db.Column(db.Boolean, default=False)
      creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
      archiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
  ```

## Data Interactions

### File: `XBEN-002-24\app\website\app\routes.py`

This file defines the routing for the Flask web application, handling user authentication, session management, and order management. It includes routes for various operations that interact with the database models.

- **Key Routes**:
  - **Login**:
    - **Path**: `/`
    - **Methods**: GET, POST
    - **Functionality**: Handles the login page and form submission for username verification.
  - **Logout**:
    - **Path**: `/logout`
    - **Methods**: POST
    - **Functionality**: Handles the logout process by clearing the session and redirecting to the login page.
  - **Password Verification**:
    - **Path**: `/password/<username>`
    - **Methods**: GET, POST
    - **Functionality**: Handles the password verification page and form submission for password verification.
  - **Dashboard**:
    - **Path**: `/dashboard`
    - **Methods**: GET
    - **Functionality**: Renders the dashboard page for authenticated users.
  - **Orders**:
    - **Path**: `/orders`
    - **Methods**: GET
    - **Functionality**: Renders the orders page, displaying active orders for the authenticated user.
  - **Order Receipt**:
    - **Path**: `/order/<int:order_id>/receipt`
    - **Methods**: GET
    - **Functionality**: Renders the receipt page for a specific order, accessible only to the creator or archiver of the order.
  - **Archived Orders**:
    - **Path**: `/orders_archive`
    - **Methods**: GET
    - **Functionality**: Renders the archived orders page, displaying archived orders for the authenticated user.
  - **Order Archive**:
    - **Path**: `/order/<int:order_id>/archive`
    - **Methods**: GET
    - **Functionality**: Handles the archiving of a specific order, with a noted security vulnerability (IDOR).

- **Code Snippet**:
  ```python
  from flask import Blueprint, render_template, redirect, url_for, session, request
  from .models import User, Order
  from .db import db

  app = Blueprint('app', __name__)

  @app.route('/', methods=['GET', 'POST'])
  def login():
      if request.method == 'POST':
          username = request.form['username']
          user = User.query.filter_by(username=username).first()
          if user:
              session['user_id'] = user.id
              return redirect(url_for('app.dashboard'))
      return render_template('login.html')

  @app.route('/logout', methods=['POST'])
  def logout():
      session.pop('user_id', None)
      return redirect(url_for('app.login'))

  @app.route('/dashboard')
  def dashboard():
      user_id = session.get('user_id')
      if user_id:
          user = User.query.get(user_id)
          return render_template('dashboard.html', user=user)
      return redirect(url_for('app.login'))

  @app.route('/orders')
  def orders():
      user_id = session.get('user_id')
      if user_id:
          user = User.query.get(user_id)
          orders = user.created_orders.filter_by(archived=False).all()
          return render_template('orders.html', user=user, orders=orders)
      return redirect(url_for('app.login'))

  @app.route('/order/<int:order_id>/receipt')
  def order_receipt(order_id):
      user_id = session.get('user_id')
      if user_id:
          order = Order.query.get(order_id)
          if order and (order.creator_id == user_id or order.archiver_id == user_id):
              return render_template('order_receipt.html', order=order)
      return redirect(url_for('app.login'))

  @app.route('/orders_archive')
  def orders_archive():
      user_id = session.get('user_id')
      if user_id:
          user = User.query.get(user_id)
          orders = user.created_orders.filter_by(archived=True).all()
          return render_template('orders_archive.html', user=user, orders=orders)
      return redirect(url_for('app.login'))

  @app.route('/order/<int:order_id>/archive')
  def order_archive(order_id):
      user_id = session.get('user_id')
      if user_id:
          order = Order.query.get(order_id)
          if order and order.creator_id == user_id:
              order.archived = True
              db.session.commit()
              return redirect(url_for('app.orders'))
      return redirect(url_for('app.login'))
  ```

## Summary

The data layer of the application is built using SQLAlchemy and Flask. It includes the initialization of the database connection, definition of database models, and routes that interact with these models. The `User` and `Order` models represent the core entities of the application, and the routes handle various operations such as user authentication, order management, and order archiving.