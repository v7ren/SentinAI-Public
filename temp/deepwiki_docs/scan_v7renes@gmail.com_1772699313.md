# Overview

## What the Project Is and What Problem It Solves

This project is a web application built using Flask, SQLAlchemy, and GraphQL. It provides a secure and efficient way to manage prescription data for healthcare providers. The application includes user authentication, database operations, and a GraphQL API for querying and mutating prescription data. The primary problem it solves is the need for a centralized, secure, and easily accessible system for managing prescription information.

## Main Components or Modules

### Flask Application
- **File:** `app/app.py`
- **Description:** This file sets up the Flask application, which serves as the core of the web application. It includes:
  - **User Authentication:** Handles user login, logout, and session management.
  - **Database Operations:** Uses SQLAlchemy for ORM (Object-Relational Mapping) to interact with the database.
  - **GraphQL Endpoint:** Provides a powerful and flexible API for querying and mutating prescription data.

### Routes and Endpoints
- **Home (`/`)**: Redirects to the login page.
- **Login (`/login`)**: Handles user login, checks credentials, and authenticates the user.
- **Logout (`/logout`)**: Logs out the current user and redirects to the login page.
- **Add Prescription (`/add_prescription`)**: Renders the page for authenticated users to add new prescriptions.
- **View Prescriptions (`/view_prescriptions`)**: Renders the page for authenticated users to view their prescriptions.
- **GraphQL (`/graphql`)**: Endpoint for querying and mutating prescription data using GraphQL.

### Database Initialization
- **File:** `app/app.py`
- **Description:** Initializes the database and ensures that it is ready for use. It also includes a script to add a default user and some sample prescriptions to the database.

## Typical Usage or Runtime Scenario

1. **User Accesses the Application:**
   - The user navigates to the home page (`/`), which redirects them to the login page (`/login`).

2. **User Logs In:**
   - The user provides their credentials (username and password) and submits the login form.
   - The application checks the credentials and, if valid, authenticates the user and sets up a session.

3. **User Adds a Prescription:**
   - The authenticated user navigates to the add prescription page (`/add_prescription`).
   - The user fills out the form and submits it.
   - The application validates the input and adds the new prescription to the database.

4. **User Views Prescriptions:**
   - The authenticated user navigates to the view prescriptions page (`/view_prescriptions`).
   - The application queries the database for the user's prescriptions and displays them on the page.

5. **User Logs Out:**
   - The user clicks the logout button, which logs them out and redirects them to the login page (`/logout`).

6. **GraphQL API Usage:**
   - The application provides a GraphQL endpoint (`/graphql`) that can be used to query and mutate prescription data.
   - This endpoint is particularly useful for more complex data operations and can be accessed by authenticated users or external systems.

## Where to Look Next

- **Authentication and Security:** For more details on how user authentication and security are implemented, see the **Authentication** section.
- **Database Operations:** For a deeper dive into how the application interacts with the database, see the **Database** section.
- **GraphQL API:** For information on how to use the GraphQL endpoint, see the **GraphQL API** section.
- **Configuration and Deployment:** For details on how to configure and deploy the application, see the **Configuration and Deployment** section.

By following these sections, you can gain a comprehensive understanding of the project's architecture and functionality.

---

# Architecture and Data Flow

## Main Architectural Components

The application is built using a combination of Flask, SQLAlchemy, and GraphQL. The main components and their roles are as follows:

### 1. **Flask Application (`app/app.py`)**

- **Role**: The core of the application, handling HTTP requests and responses.
- **Key Functions**:
  - **Initialization**: The application is initialized in the `main` function, which sets up the database and starts the Flask server.
  - **Routes**:
    - **Home (`/`)**: Redirects to the login page.
    - **Login (`/login`)**: Handles user authentication and session management.
    - **Logout (`/logout`)**: Logs out the current user and redirects to the login page.
    - **Add Prescription (`/add_prescription`)**: Renders the form for adding new prescriptions, accessible only to authenticated users.
    - **View Prescriptions (`/view_prescriptions`)**: Displays the list of prescriptions for the authenticated user.
    - **GraphQL (`/graphql`)**: Provides a GraphQL endpoint for querying and mutating prescription data.

### 2. **SQLAlchemy ORM**

- **Role**: Manages database operations, including creating, reading, updating, and deleting (CRUD) operations.
- **Key Entities**:
  - **User Model**: Represents the user entity in the database.
  - **Prescription Model**: Represents the prescription entity in the database.

### 3. **GraphQL**

- **Role**: Provides a powerful and flexible API for querying and mutating prescription data.
- **Key Endpoints**:
  - **GraphQL Endpoint (`/graphql`)**: Allows clients to execute GraphQL queries and mutations.

## Data and Control Flow

### 1. **User Authentication and Session Management**

- **Flow**:
  - **Home Page (`/`)**: When a user accesses the home page, they are redirected to the login page.
  - **Login Page (`/login`)**: The user provides their credentials (username and password). The application checks these credentials against the database.
  - **Session Management**: If the credentials are valid, a session is created, and the user is redirected to the add prescription or view prescriptions page.
  - **Logout Page (`/logout`)**: The user can log out, which invalidates the session and redirects them back to the login page.

### 2. **Prescription Management**

- **Flow**:
  - **Add Prescription (`/add_prescription`)**: Authenticated users can access this page to add new prescriptions. The form data is submitted to the server, where it is validated and stored in the database using SQLAlchemy.
  - **View Prescriptions (`/view_prescriptions`)**: Authenticated users can view a list of their prescriptions. The application queries the database for prescriptions associated with the logged-in user and renders the results.

### 3. **GraphQL Endpoint**

- **Flow**:
  - **GraphQL Queries and Mutations (`/graphql`)**: Clients can send GraphQL queries and mutations to the `/graphql` endpoint. The server processes these requests, interacts with the database using SQLAlchemy, and returns the results.

### 4. **Database Initialization and Data Seeding**

- **Flow**:
  - **Initialization**: When the application starts, it initializes the database and checks for the presence of a user with the username 'admin' and password '!@ED#'.
  - **Data Seeding**: If the user exists, the application checks if there are any prescriptions for this user. If not, it adds 89 prescriptions to the database. One of these prescriptions (number 43) includes a flag from an environment variable.

## Important Patterns

### 1. **Model-View-Controller (MVC) Pattern**

- **Model**: SQLAlchemy ORM models represent the data structures (User, Prescription).
- **View**: Flask routes and templates handle the presentation of data to the user.
- **Controller**: Flask routes and functions manage the application logic, including user authentication, prescription management, and database interactions.

### 2. **Client-Server Architecture**

- **Client**: Web browsers or GraphQL clients.
- **Server**: The Flask application running on `0.0.0.0:5003`.
- **Communication**: HTTP requests and responses, including form submissions and GraphQL queries/mutations.

### 3. **Event-Driven Architecture (Partial)**

- **Event**: User actions (login, logout, add prescription, view prescriptions).
- **Handler**: Flask routes and functions that respond to these events by performing the necessary operations (authentication, database queries, rendering templates).

## Conclusion

The application is structured to provide a robust and secure environment for managing prescriptions. It leverages Flask for the web framework, SQLAlchemy for database operations, and GraphQL for a flexible API. The architecture follows the MVC pattern and a client-server model, ensuring clear separation of concerns and efficient data flow.

---

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

---

# Database and ORM

This section provides an overview of the database schema, ORM models, and database operations used in the application. The application leverages SQLAlchemy as the ORM and Flask-SQLAlchemy for database management. The database is used to store user authentication data and prescription information.

## Database Schema

The database schema is designed to support user authentication and prescription management. The key entities in the schema are:

- **User**: Represents a user in the system.
- **Prescription**: Represents a prescription added by a user.

### User Model

The `User` model is defined in the `app/app.py` file. It includes the following fields:

- `id`: Unique identifier for the user.
- `username`: Username for the user.
- `password`: Password for the user (hashed for security).

### Prescription Model

The `Prescription` model is also defined in the `app/app.py` file. It includes the following fields:

- `id`: Unique identifier for the prescription.
- `user_id`: Foreign key linking to the `User` model.
- `details`: Details of the prescription.
- `flag`: An optional field that can be set from an environment variable.

## ORM Models

The ORM models are defined using SQLAlchemy in the `app/app.py` file. The models are used to interact with the database and perform CRUD operations.

### User Model

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    prescriptions = db.relationship('Prescription', backref='user', lazy=True)
```

### Prescription Model

```python
class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    details = db.Column(db.Text, nullable=False)
    flag = db.Column(db.String(120), nullable=True)
```

## Database Operations

The application performs various database operations, including querying, adding, and updating records. These operations are primarily handled in the `app/app.py` file.

### Initialization

The database is initialized and the application is started in the `main` function of `app/app.py`. This function also checks if there are any prescriptions for the user 'admin' and adds 89 prescriptions if none exist.

```python
def main():
    with app.app_context():
        db.create_all()
        user = User.query.filter_by(username='admin').first()
        if user:
            prescriptions = Prescription.query.filter_by(user_id=user.id).all()
            if not prescriptions:
                for i in range(1, 90):
                    flag = os.getenv('FLAG') if i == 43 else None
                    prescription = Prescription(user_id=user.id, details=f'Prescription {i}', flag=flag)
                    db.session.add(prescription)
                db.session.commit()
    app.run(host='0.0.0.0', port=5003)
```

### Querying Users and Prescriptions

The application queries users and prescriptions in various routes. For example, the `login` route checks the user's credentials:

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            # Authentication successful
            return redirect('/view_prescriptions')
        else:
            # Authentication failed
            return 'Invalid credentials'
    return render_template('login.html')
```

### Adding Prescriptions

The `add_prescription` route allows authenticated users to add new prescriptions:

```python
@app.route('/add_prescription', methods=['GET', 'POST'])
@login_required
def add_prescription():
    if request.method == 'POST':
        details = request.form['details']
        prescription = Prescription(user_id=current_user.id, details=details)
        db.session.add(prescription)
        db.session.commit()
        return redirect('/view_prescriptions')
    return render_template('add_prescription.html')
```

### Viewing Prescriptions

The `view_prescriptions` route displays all prescriptions for the authenticated user:

```python
@app.route('/view_prescriptions', methods=['GET'])
@login_required
def view_prescriptions():
    prescriptions = Prescription.query.filter_by(user_id=current_user.id).all()
    return render_template('view_prescriptions.html', prescriptions=prescriptions)
```

## GraphQL Endpoint

The application also provides a GraphQL endpoint for querying and mutating prescription data. This endpoint is defined in the `app/app.py` file and uses the GraphQL library to handle requests.

```python
@app.route('/graphql', methods=['GET', 'POST'])
def graphql():
    schema = graphene.Schema(query=Query, mutation=Mutation)
    result = schema.execute(request.data)
    return jsonify(result.data)
```

### GraphQL Schema

The GraphQL schema is defined in the same file and includes queries and mutations for prescriptions. For example, a query to fetch prescriptions for a user might look like this:

```python
class Query(graphene.ObjectType):
    prescriptions = graphene.List(PrescriptionType, user_id=graphene.Int())

    def resolve_prescriptions(self, info, user_id):
        return Prescription.query.filter_by(user_id=user_id).all()

class Mutation(graphene.ObjectType):
    add_prescription = AddPrescription.Field()
```

## Security Considerations

The application includes security measures to protect user data and prevent unauthorized access. User passwords are hashed, and authentication is required for most routes. The `login_required` decorator ensures that only authenticated users can access certain endpoints.

```python
from flask_login import login_required, current_user

@app.route('/view_prescriptions', methods=['GET'])
@login_required
def view_prescriptions():
    prescriptions = Prescription.query.filter_by(user_id=current_user.id).all()
    return render_template('view_prescriptions.html', prescriptions=prescriptions)
```

## Summary

The database and ORM setup in the application is designed to support user authentication and prescription management. SQLAlchemy is used as the ORM, and the database schema includes `User` and `Prescription` models. The application performs various database operations, including querying, adding, and updating records, and provides a GraphQL endpoint for more advanced data manipulation. Security measures are in place to protect user data and ensure authorized access.

---

# GraphQL API

This section provides an overview of the GraphQL API endpoint in the application, including how to query and mutate prescription data. The GraphQL endpoint is a powerful tool for interacting with the prescription data managed by the application.

## Overview

The GraphQL API is implemented in the `app/app.py` file, which sets up a Flask application with user authentication, SQLAlchemy for database operations, and a GraphQL endpoint. The endpoint allows authenticated users to perform queries and mutations on prescription data.

## Authentication

Before accessing the GraphQL endpoint, users must be authenticated. The application provides the following authentication-related endpoints:

- **Login**: 
  - **Endpoint**: `/login`
  - **Methods**: `GET`, `POST`
  - **Description**: Handles user login, checks credentials, and authenticates the user.

- **Logout**:
  - **Endpoint**: `/logout`
  - **Methods**: `GET`
  - **Description**: Logs out the current user and redirects to the login page.

## GraphQL Endpoint

The GraphQL endpoint is accessible at the following URL:

- **Endpoint**: `/graphql`
  - **Methods**: `GET`, `POST`
  - **Description**: This endpoint allows authenticated users to query and mutate prescription data.

### Querying Prescription Data

To query prescription data, you can use the GraphQL endpoint with a query operation. The application uses SQLAlchemy to manage the database, and the GraphQL schema is designed to interact with the prescription data stored in the database.

Example query to fetch all prescriptions for a user:

```graphql
query {
  prescriptions {
    id
    user
    medication
    dosage
    date
  }
}
```

### Mutating Prescription Data

To mutate prescription data, you can use the GraphQL endpoint with a mutation operation. This allows you to add, update, or delete prescriptions.

Example mutation to add a new prescription:

```graphql
mutation {
  addPrescription(user: "admin", medication: "Ibuprofen", dosage: "200mg", date: "2023-10-01") {
    id
    user
    medication
    dosage
    date
  }
}
```

## Database Operations

The application uses SQLAlchemy to manage database operations. The `app/app.py` file initializes the database and defines the necessary ORM models for prescriptions. The GraphQL schema is built on top of these models to provide a seamless interface for querying and mutating data.

### Example Database Initialization

The following code snippet initializes the database and adds some sample prescriptions:

```python
from app import db, Prescription

# Query the user with the username 'admin' and password '!@ED#'
user = User.query.filter_by(username='admin', password='!@ED#').first()

# Check if there are any prescriptions for this user
if not user.prescriptions:
    # Add 89 prescriptions to the database
    for i in range(1, 90):
        prescription = Prescription(
            user=user,
            medication=f"Medication {i}",
            dosage=f"100mg",
            date=f"2023-10-0{i}",
            special_flag=os.getenv('SPECIAL_FLAG') if i == 43 else None
        )
        db.session.add(prescription)
    db.session.commit()
```

## Security Considerations

The GraphQL endpoint is protected by user authentication, ensuring that only authenticated users can perform queries and mutations. The application uses JWT (JSON Web Tokens) for session management and OAuth for handling user authentication.

### Environment Variables

The application uses environment variables for configuration, including security-related settings. For example, the `SPECIAL_FLAG` environment variable is used to add a special flag to a specific prescription.

## Conclusion

The GraphQL API in the application provides a robust and flexible way to interact with prescription data. By leveraging Flask, SQLAlchemy, and GraphQL, the application ensures secure and efficient data management. Authenticated users can perform complex queries and mutations to manage their prescriptions effectively.

---