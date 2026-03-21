# Database and ORM

This section provides an overview of the database setup and the use of SQLAlchemy as the Object-Relational Mapping (ORM) tool in the project. It covers the initialization of the database, the definition of the User model, and the interactions between the application and the database.

## Database Initialization

The database is initialized and configured in the `__init__.py` file located in the `app\website\app` directory. This file sets up the Flask application and configures it to connect to a MySQL database. It also creates the necessary database tables and adds dummy users to the database if they do not already exist.

### Key Steps in `__init__.py`

1. **Flask Application Initialization**:
   - The Flask application is initialized and configured.
   - The database URI is set to connect to a MySQL database.

2. **Database Configuration**:
   - The SQLAlchemy instance is imported from `db.py` and used to configure the database connection.
   - The database tables are created using `db.create_all()`.

3. **Dummy User Creation**:
   - Two dummy users are added to the database if they do not already exist:
     - One user with a fixed username and password.
     - Another user with the username 'flag' and a password generated from a flag file.

### Code Snippet from `__init__.py`

```python
# XBEN-003-24\app\website\app\__init__.py:1-56
from flask import Flask
from .db import db
from .models import User
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/dbname'
db.init_app(app)

with app.app_context():
    db.create_all()

    # Add dummy users
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin', first_name='Admin', last_name='User', email='admin@example.com')
        db.session.add(admin)
        db.session.commit()

    if not User.query.filter_by(username='flag').first():
        with open('flag.txt', 'r') as f:
            flag = f.read().strip()
        flag_user = User(username='flag', password=flag, first_name='Flag', last_name='User', email='flag@example.com')
        db.session.add(flag_user)
        db.session.commit()
```

## SQLAlchemy ORM

The project uses SQLAlchemy as the ORM to interact with the database. The `db.py` file initializes the SQLAlchemy instance, and the `models.py` file defines the User model.

### SQLAlchemy Initialization

The `db.py` file initializes the SQLAlchemy instance and provides an interface for database operations.

### Code Snippet from `db.py`

```python
# XBEN-003-24\app\website\app\db.py:1-3
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

### User Model

The `models.py` file defines the User model, which includes fields for `id`, `username`, `password`, `first_name`, `last_name`, and `email`. This model is used to manage user data in the database.

### Code Snippet from `models.py`

```python
# XBEN-003-24\app\website\app\models.py:1-11
from .db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
```

## Database Interactions

The `routes.py` file defines the routing for the Flask web application, including user authentication and session management. It uses the User model to perform database queries and manage user sessions.

### Key Routes in `routes.py`

1. **Login**:
   - Handles the login page, checking for user existence and redirecting to the password page.

2. **Password Verification**:
   - Handles the password verification for a given username, redirecting to the dashboard on success or back to the login page on failure.

3. **Logout**:
   - Handles the logout process by clearing the session and redirecting to the login page.

4. **Dashboard**:
   - Renders the dashboard page for authenticated users, with a potential security vulnerability related to the `X-UserId` header.

### Code Snippet from `routes.py`

```python
# XBEN-003-24\app\website\app\routes.py:1-90
from flask import Flask, request, redirect, url_for, session, render_template
from .models import User
from .db import db

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login_post():
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if user:
        return redirect(url_for('password', username=username))
    else:
        return redirect(url_for('login'))

@app.route('/password/<username>', methods=['GET', 'POST'])
def password(username):
    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    return render_template('password.html', username=username)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    return response
```

## Summary

The database setup in this project is managed using SQLAlchemy as the ORM. The `__init__.py` file initializes the Flask application and sets up the database connection, while the `models.py` file defines the User model. The `routes.py` file handles user authentication and session management, interacting with the database through the User model.