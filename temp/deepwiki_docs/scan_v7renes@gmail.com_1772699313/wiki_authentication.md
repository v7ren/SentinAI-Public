# Authentication and Security

This section provides an overview of the authentication mechanisms, user sessions, and security practices implemented in the application. The primary focus is on the Flask application setup, user authentication, and the security measures in place to protect user data and application integrity.

## Flask Application Setup

The main application is defined in `app/app.py`. This file sets up a Flask application with the following key components:

- **User Authentication**: The application uses a combination of session management and JSON Web Tokens (JWT) for user authentication.
- **Database Management**: SQLAlchemy is used for database operations, including querying and managing prescription data.
- **GraphQL Endpoint**: A GraphQL endpoint is provided for querying and mutating prescription data.

### Entry Points

The application defines several HTTP endpoints for handling user interactions:

- **Home (`/`)**: Redirects to the login page.
- **Login (`/login`)**: Handles user login, checks credentials, and authenticates the user.
- **Logout (`/logout`)**: Logs out the current user and redirects to the login page.
- **Add Prescription (`/add_prescription`)**: Renders the add prescription page for authenticated users.
- **View Prescriptions (`/view_prescriptions`)**: Renders the view prescriptions page for authenticated users.
- **GraphQL (`/graphql`)**: GraphQL endpoint for querying and mutating prescription data.

### Authentication Flow

1. **Home Page (`/`)**:
   - When a user accesses the home page, they are redirected to the login page.

2. **Login (`/login`)**:
   - The user is presented with a login form.
   - Upon submission, the application checks the provided credentials against the database.
   - If the credentials are valid, a session is created, and the user is authenticated.
   - The user is then redirected to the `add_prescription` or `view_prescriptions` page, depending on the application logic.

3. **Logout (`/logout`)**:
   - The user can log out by accessing the logout endpoint.
   - The session is terminated, and the user is redirected back to the login page.

4. **Authenticated Routes**:
   - Routes such as `add_prescription` and `view_prescriptions` require the user to be authenticated.
   - If the user is not authenticated, they are redirected to the login page.

### Security Practices

- **Session Management**:
  - The application uses Flask's session management to handle user sessions.
  - Sessions are stored securely and are tied to the user's authentication status.

- **JSON Web Tokens (JWT)**:
  - JWTs are used to securely transmit information between the client and the server.
  - JWTs are signed to ensure data integrity and are validated on each request.

- **Database Security**:
  - SQLAlchemy is used to manage database operations, ensuring that data is accessed and modified securely.
  - The application includes a chunk of code that queries a user with the username 'admin' and password '!@ED#'. This user is used to seed the database with 89 prescriptions, including one prescription (number 43) that includes a flag from an environment variable. This practice should be reviewed for security implications.

- **Environment Variables**:
  - Sensitive information, such as the flag for prescription number 43, is stored in environment variables to avoid hardcoding sensitive data in the source code.

### Example Code Snippets

#### Initializing the Flask Application

```python
# app/app.py:1-120
from flask import Flask, session, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
from graphene import ObjectType, String, Field, Schema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prescriptions.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

# Define routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('add_prescription'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/add_prescription')
def add_prescription():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('add_prescription.html')

@app.route('/view_prescriptions')
def view_prescriptions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('view_prescriptions.html')

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=Schema(query=Query), graphiql=True))

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=5003)
```

#### Seeding the Database

```python
# app/app.py:121-145
from app.models import User, Prescription

admin_user = User.query.filter_by(username='admin', password='!@ED#').first()
if not admin_user:
    admin_user = User(username='admin', password='!@ED#')
    db.session.add(admin_user)
    db.session.commit()

prescriptions = Prescription.query.filter_by(user_id=admin_user.id).all()
if len(prescriptions) < 89:
    for i in range(1, 90):
        prescription = Prescription(user_id=admin_user.id, number=i, flag=os.getenv('FLAG') if i == 43 else None)
        db.session.add(prescription)
    db.session.commit()

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=5003)
```

## Conclusion

The application implements a robust authentication and security framework using Flask, SQLAlchemy, and JWT. User sessions are managed securely, and sensitive data is protected through environment variables. The GraphQL endpoint provides a powerful interface for querying and mutating prescription data, while ensuring that only authenticated users can access certain routes.