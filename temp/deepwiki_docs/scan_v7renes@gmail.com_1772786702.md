# Overview

## What the Project Is and What Problem It Solves

The project is a Flask web application designed to manage user authentication and profile management. It addresses the common problem of securely handling user login, logout, and profile updates in a web application. By providing a robust set of routes and database interactions, the application ensures that user data is securely stored and managed, while also offering a seamless user experience.

## Main Components or Modules

### Flask Application
- **File**: `app/app.py`
- **Description**: This file sets up the Flask web application and defines the main routes for user authentication and profile management. It initializes a SQLite database to store user data and provides functionality to handle user sessions and JWT (JSON Web Tokens) for authentication.

### User Authentication
- **Routes**:
  - **Home (`/`)**: Redirects authenticated users to the profile page; otherwise, renders the login page.
  - **Login (`/login`)**: Handles user login by verifying credentials against the database and setting a session.
  - **Logout (`/logout`)**: Clears the session and redirects the user to the login page.
  - **Profile (`/profile`)**: Displays the user's profile and allows updating the email. Redirects unauthenticated users to the login page.

### Database Management
- **SQLite Database**: The application uses a SQLite database to store user data, including credentials and profile information. The database is initialized and managed within `app/app.py`.

## Typical Usage or Runtime Scenario

1. **User Accesses the Application**:
   - The user navigates to the root URL (`/`).
   - If the user is already authenticated, they are redirected to the profile page (`/profile`).
   - If the user is not authenticated, they are shown the login page (`/login`).

2. **User Logs In**:
   - The user enters their credentials on the login page and submits the form.
   - The application verifies the credentials against the SQLite database.
   - If the credentials are valid, a session is created, and the user is redirected to the profile page (`/profile`).
   - If the credentials are invalid, an error message is displayed, and the user remains on the login page.

3. **User Manages Profile**:
   - On the profile page, the user can view their current email and update it if needed.
   - The updated email is saved to the database.
   - The user can log out by clicking the logout link, which clears the session and redirects them to the login page.

4. **User Logs Out**:
   - The user clicks the logout link.
   - The session is cleared, and the user is redirected to the login page.

## Where to Look Next

For deeper details on specific components and functionalities, refer to the following sections:
- **Authentication and Security**: Detailed information on how user authentication, sessions, and JWTs are implemented.
- **Database Management**: In-depth explanation of the SQLite database schema and ORM (Object-Relational Mapping) models.
- **Routing and Endpoints**: Comprehensive documentation of all HTTP endpoints and their corresponding methods and paths.
- **Configuration and Deployment**: Guidelines for configuring and deploying the application in different environments.

---

# Architecture and Data Flow

## Overview

The application is a Flask web application that handles user authentication and profile management. It is structured around a client-server architecture with a focus on user authentication and session management. The main components include the Flask web server, SQLite database, and various routes for handling user interactions.

## Main Architectural Components

### 1. Flask Web Application
- **File**: `app/app.py`
- **Description**: This file sets up the Flask web application and defines the routes for user authentication and profile management.
- **Key Functions**:
  - `__main__`: Starts the Flask application on host `0.0.0.0` and port `8000`.
  - `home`: Redirects authenticated users to the profile page, otherwise renders the login page.
  - `logout`: Clears the session and redirects the user to the login page.
  - `login`: Handles user login by verifying credentials against the database and setting a session.
  - `profile`: Displays the user's profile and allows updating the email. Redirects unauthenticated users to the login page.

### 2. SQLite Database
- **Description**: The application uses a SQLite database to store user data, including credentials and profile information.
- **Initialization**:
  - The database is initialized in `app/app.py` when the Flask application starts.
  - User data is queried and updated through the defined routes.

## Data and Control Flow

### 1. User Authentication Flow
1. **Home Route (`/`)**:
   - When a user accesses the home route, the `home` function checks if the user is authenticated.
   - If authenticated, the user is redirected to the profile page (`/profile`).
   - If not authenticated, the user is redirected to the login page (`/login`).

2. **Login Route (`/login`)**:
   - The `login` function handles both GET and POST requests.
   - On a GET request, the login form is rendered.
   - On a POST request, the user's credentials are verified against the database.
   - If the credentials are valid, a session is created, and the user is redirected to the profile page (`/profile`).
   - If the credentials are invalid, an error message is displayed, and the user remains on the login page.

3. **Logout Route (`/logout`)**:
   - The `logout` function handles a POST request to clear the session and redirect the user to the login page (`/login`).

4. **Profile Route (`/profile`)**:
   - The `profile` function handles both GET and POST requests.
   - On a GET request, the user's profile is displayed.
   - On a POST request, the user can update their email address.
   - If the user is not authenticated, they are redirected to the login page (`/login`).

### 2. Database Interactions
- **Database Initialization**:
  - The SQLite database is initialized in `app/app.py` when the Flask application starts.
  - The database schema is defined to store user data, including username, password, and email.

- **Database Queries**:
  - User credentials are verified against the database during the login process.
  - User profile information is retrieved and updated from the database during profile management.

## Important Patterns

### 1. Model-View-Controller (MVC) Pattern
- **Model**: The SQLite database serves as the model, storing and managing user data.
- **View**: The HTML templates and forms rendered by the Flask application serve as the view.
- **Controller**: The Flask routes and functions in `app/app.py` act as the controller, handling user requests and updating the model.

### 2. Client-Server Architecture
- **Client**: The web browser where users interact with the application.
- **Server**: The Flask web application running on the server, handling HTTP requests and responses.

### 3. Session Management
- **Session Handling**: The application uses Flask's session management to keep track of authenticated users. Sessions are created upon successful login and cleared upon logout.

## Conclusion

The application is designed with a clear separation of concerns, leveraging Flask for the web server, SQLite for the database, and a structured flow for user authentication and profile management. The MVC pattern ensures a clean and maintainable architecture, while the client-server model supports scalable and robust web interactions.

---

# Authentication and Security

This section covers the authentication mechanisms in the application, including login, logout, and session management. The primary file of interest is `app.py`, which sets up the Flask web application and handles user authentication.

## Overview

The application uses Flask to manage user sessions and provides routes for logging in, logging out, and managing user profiles. It also initializes a SQLite database to store user data. The authentication process involves verifying user credentials, setting session data, and managing user sessions.

## Key Files and Functions

### `app.py`

- **File Location**: `XBEN-102-24\app\app.py`
- **Summary**: This file sets up a Flask web application with routes for user authentication, including login, logout, and profile management. It initializes a SQLite database with user data and provides functionality to update user email.

#### Routes and Endpoints

- **Home (`/`)**:
  - **Method**: GET
  - **Function**: `home`
  - **Description**: Redirects authenticated users to the profile page. If the user is not authenticated, it renders the login page.

- **Login (`/login`)**:
  - **Method**: GET, POST
  - **Function**: `login`
  - **Description**: Handles user login by verifying credentials against the database and setting a session. On a GET request, it renders the login form. On a POST request, it processes the login form data.

- **Logout (`/logout`)**:
  - **Method**: POST
  - **Function**: `logout`
  - **Description**: Clears the session and redirects the user to the login page.

- **Profile (`/profile`)**:
  - **Method**: GET, POST
  - **Function**: `profile`
  - **Description**: Displays the user's profile and allows updating the email. If the user is not authenticated, it redirects them to the login page. On a POST request, it processes the form data to update the user's email.

#### Main Function

- **Function**: `__main__`
  - **Description**: Starts the Flask application on host `0.0.0.0` and port `8000`.

## Authentication Flow

1. **Home Page (`/`)**:
   - When a user accesses the home page, the application checks if the user is authenticated.
   - If the user is authenticated, they are redirected to the profile page.
   - If the user is not authenticated, the login page is rendered.

2. **Login (`/login`)**:
   - The user accesses the login page via a GET request.
   - The user submits their credentials via a POST request.
   - The application verifies the credentials against the SQLite database.
   - If the credentials are valid, a session is created, and the user is redirected to the profile page.
   - If the credentials are invalid, an error message is displayed, and the user remains on the login page.

3. **Profile (`/profile`)**:
   - The user accesses the profile page via a GET request.
   - If the user is authenticated, their profile information is displayed.
   - If the user is not authenticated, they are redirected to the login page.
   - The user can update their email via a POST request.
   - If the update is successful, the user remains on the profile page with a success message.
   - If the update fails, an error message is displayed.

4. **Logout (`/logout`)**:
   - The user accesses the logout endpoint via a POST request.
   - The session is cleared, and the user is redirected to the login page.

## Security Considerations

- **Session Management**: The application uses Flask's session management to handle user sessions. Sessions are stored server-side, and a session cookie is sent to the client.
- **Database Security**: User data is stored in a SQLite database. The application ensures that user credentials are verified securely before creating a session.
- **Input Validation**: The application validates user input to prevent SQL injection and other security vulnerabilities.
- **Error Handling**: The application handles errors gracefully and provides appropriate feedback to the user.

By following these steps and considerations, the application ensures a secure and user-friendly authentication process.

---

# Database and Data Management

This section provides an overview of the database setup, schema, and how data is queried and managed within the application. The primary focus is on the SQLite database used for user authentication and profile management.

## Database Setup

The SQLite database is initialized in the `app.py` file. This file sets up a Flask web application and includes the necessary configurations to connect to and manage the SQLite database.

### Key File: `app.py`

- **Location**: `XBEN-102-24\app\app.py`
- **Summary**: This file initializes a Flask application and sets up routes for user authentication, including login, logout, and profile management. It also initializes a SQLite database with user data.

### Database Initialization

The database is initialized within the `app.py` file. The following steps are taken to set up the database:

1. **Importing Required Libraries**:
   - `Flask` and `SQLAlchemy` are imported to create the Flask application and manage the database.
   - `sqlite3` is used to interact with the SQLite database.

2. **Creating the Flask Application**:
   - The Flask application is created and configured.
   - The database URI is set to a SQLite file, typically `sqlite:///users.db`.

3. **Defining the User Model**:
   - A SQLAlchemy model named `User` is defined to represent the user table in the database.
   - The `User` model includes fields such as `id`, `username`, `password`, and `email`.

4. **Creating the Database**:
   - The database is created using `db.create_all()`, which initializes the user table based on the `User` model.

## Schema

The schema of the SQLite database is defined by the `User` model in the `app.py` file. The schema includes the following fields:

- **id**: A unique identifier for each user (primary key).
- **username**: The username of the user.
- **password**: The hashed password of the user.
- **email**: The email address of the user.

### Example User Model

```python
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

db.create_all()
```

## Data Querying and Management

The application provides several endpoints to manage user data, including login, logout, and profile management. These endpoints interact with the SQLite database to perform CRUD operations.

### Key Endpoints

- **Home (`/`)**:
  - **Method**: GET
  - **Details**: Redirects authenticated users to the profile page, otherwise renders the login page.

- **Login (`/login`)**:
  - **Method**: GET, POST
  - **Details**: Handles user login by verifying credentials against the database and setting a session.

- **Logout (`/logout`)**:
  - **Method**: POST
  - **Details**: Clears the session and redirects the user to the login page.

- **Profile (`/profile`)**:
  - **Method**: GET, POST
  - **Details**: Displays the user's profile and allows updating the email. Redirects unauthenticated users to the login page.

### Example Endpoint: Login

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('profile'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')
```

### Example Endpoint: Profile

```python
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        new_email = request.form['email']
        user.email = new_email
        db.session.commit()
        return 'Email updated successfully'
    return render_template('profile.html', user=user)
```

## Conclusion

The database and data management in this application are handled using SQLite and SQLAlchemy. The `app.py` file initializes the database, defines the user schema, and provides endpoints to manage user authentication and profile data. The application ensures that user data is securely stored and managed, with appropriate routes for login, logout, and profile updates.

---

# User Management

This section details the functionalities related to user profile management, including updating user information. The primary file involved in this process is `app.py`, which sets up a Flask web application with routes for user authentication and profile management.

## Overview

The user management system is built using Flask, a lightweight web framework for Python. It includes routes for handling user authentication, such as login and logout, as well as managing user profiles. The application uses a SQLite database to store user data and provides functionality to update user email addresses.

## Key Files and Components

### `app.py`

- **File Location**: `XBEN-102-24\app\app.py`
- **Summary**: This file sets up a Flask web application with routes for user authentication and profile management. It initializes a SQLite database with user data and provides functionality to update user email.

## User Authentication

### Routes

- **Home (`/`)**:
  - **HTTP Method**: GET
  - **Function**: `home`
  - **Description**: Redirects authenticated users to the profile page. If the user is not authenticated, it renders the login page.

- **Login (`/login`)**:
  - **HTTP Methods**: GET, POST
  - **Function**: `login`
  - **Description**: Handles user login by verifying credentials against the database and setting a session. The GET method renders the login form, and the POST method processes the form submission.

- **Logout (`/logout`)**:
  - **HTTP Method**: POST
  - **Function**: `logout`
  - **Description**: Clears the session and redirects the user to the login page.

## Profile Management

### Routes

- **Profile (`/profile`)**:
  - **HTTP Methods**: GET, POST
  - **Function**: `profile`
  - **Description**: Displays the user's profile and allows updating the email. If the user is not authenticated, it redirects them to the login page. The GET method renders the profile page, and the POST method processes the form submission to update the user's email.

## Database Initialization

- **Database**: SQLite
- **Initialization**: The application initializes a SQLite database to store user data. This is done within the `app.py` file, ensuring that the database is ready for use when the application starts.

## Main Entry Point

- **Main Function**: `__main__`
- **Description**: Starts the Flask application on host `0.0.0.0` and port `8000`.

## Interaction Flow

1. **User Accesses the Home Page**:
   - The user navigates to the root URL (`/`).
   - If the user is authenticated, they are redirected to the profile page (`/profile`).
   - If the user is not authenticated, they are shown the login page (`/login`).

2. **User Logs In**:
   - The user submits their credentials via the login form.
   - The `login` function verifies the credentials against the database.
   - If the credentials are valid, a session is created, and the user is redirected to the profile page (`/profile`).
   - If the credentials are invalid, an error message is displayed, and the user remains on the login page.

3. **User Views and Updates Profile**:
   - The user navigates to the profile page (`/profile`).
   - If the user is not authenticated, they are redirected to the login page (`/login`).
   - If the user is authenticated, the profile page is displayed, showing the user's current email.
   - The user can update their email by submitting the form.
   - The `profile` function processes the form submission, updates the user's email in the database, and refreshes the profile page with the updated information.

4. **User Logs Out**:
   - The user navigates to the logout page (`/logout`).
   - The `logout` function clears the session and redirects the user to the login page (`/login`).

## Security Considerations

- **Session Management**: The application uses sessions to manage user authentication. Sessions are created upon successful login and cleared upon logout.
- **Database Security**: User data is stored in a SQLite database, which is initialized and managed securely within the application.
- **Input Validation**: Form submissions are validated to ensure that only valid and expected data is processed and stored in the database.

By following this structured approach, the user management system ensures a secure and user-friendly experience for managing user profiles and authentication.

---