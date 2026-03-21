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