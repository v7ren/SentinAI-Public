# Overview

## What the Project Is and What Problem It Solves

The project is a web application built using Flask, SQLAlchemy, and GraphQL. It provides a secure platform for managing prescription data, including user authentication, database operations, and a GraphQL API for querying and mutating prescription records. The primary problem it solves is the need for a centralized and secure system to manage prescription data, ensuring that only authenticated users can access and modify their prescriptions.

## Main Components or Modules

### Flask Application
- **File**: `app/app.py`
- **Description**: This file sets up the Flask application, including user authentication, database operations, and GraphQL endpoints. It defines several routes for user interactions and initializes the database with default users and prescriptions.

### User Authentication
- **Endpoints**:
  - **Home (`/`)**: Redirects to the login page.
  - **Login (`/login`)**: Handles user login by checking credentials and authenticating the user.
  - **Logout (`/logout`)**: Logs out the current user and redirects to the login page.

### Prescription Management
- **Endpoints**:
  - **Add Prescription (`/add_prescription`)**: Renders the add prescription page for authenticated users.
  - **View Prescriptions (`/view_prescriptions`)**: Renders the view prescriptions page for authenticated users.

### GraphQL API
- **Endpoint**:
  - **GraphQL (`/graphql`)**: Provides a GraphQL endpoint for querying and mutating prescription data.

### Database Initialization
- **Initialization**:
  - The application initializes the database and adds default users and prescriptions if none exist.

## Typical Usage or Runtime Scenario

1. **User Access**:
   - A user navigates to the home page (`/`), which redirects them to the login page (`/login`).
   - The user enters their credentials and submits the form. The application checks the credentials and authenticates the user.

2. **Prescription Management**:
   - Once authenticated, the user can navigate to the add prescription page (`/add_prescription`) to add new prescriptions.
   - The user can also view their existing prescriptions by navigating to the view prescriptions page (`/view_prescriptions`).

3. **GraphQL Queries and Mutations**:
   - For more advanced interactions, the user can use the GraphQL endpoint (`/graphql`) to query and mutate prescription data programmatically.

4. **Logout**:
   - When the user is done, they can log out by navigating to the logout page (`/logout`), which logs them out and redirects them back to the login page.

## Where to Look Next

- **Authentication and Security**: For more details on how user authentication and security are implemented, refer to the **Authentication** section.
- **Database Operations**: For a deeper dive into the database models and operations, see the **Database** section.
- **GraphQL API**: To understand the GraphQL schema and how to use the GraphQL endpoint, check the **GraphQL API** section.
- **Configuration and Initialization**: For information on how the application is configured and initialized, including the setup of default users and prescriptions, see the **Configuration** section.

---

# Architecture and Data Flow

## Main Architectural Components

The application is built using a combination of Flask, SQLAlchemy, and GraphQL. The main components and their roles are as follows:

- **Flask Application (`app.py`)**: This is the core of the application, responsible for setting up the web server, handling HTTP requests, and managing user sessions.
- **User Authentication**: The application uses JWT (JSON Web Tokens) for user authentication and session management.
- **Database Operations**: SQLAlchemy is used as the ORM (Object-Relational Mapping) tool to interact with the database. It handles CRUD (Create, Read, Update, Delete) operations for user and prescription data.
- **GraphQL Endpoint**: A GraphQL endpoint is provided for querying and mutating prescription data, allowing for flexible and efficient data retrieval and modification.

## Data and Control Flow

### User Authentication and Session Management

1. **Home Page (`/`)**:
   - The home page is a simple redirect to the login page.
   - **File**: `app.py`
   - **Function**: `home`

2. **Login (`/login`)**:
   - The login endpoint handles user authentication. It checks the provided credentials and, if valid, generates a JWT token and sets it in the session.
   - **File**: `app.py`
   - **Function**: `login`

3. **Logout (`/logout`)**:
   - The logout endpoint invalidates the current session and redirects the user back to the login page.
   - **File**: `app.py`
   - **Function**: `logout`

### Prescription Management

4. **Add Prescription (`/add_prescription`)**:
   - This endpoint renders a form for authenticated users to add new prescriptions.
   - **File**: `app.py`
   - **Function**: `add_prescription`

5. **View Prescriptions (`/view_prescriptions`)**:
   - This endpoint renders a page displaying the prescriptions for the authenticated user.
   - **File**: `app.py`
   - **Function**: `view_prescriptions`

### GraphQL Endpoint (`/graphql`)

6. **GraphQL Endpoint**:
   - The GraphQL endpoint allows clients to query and mutate prescription data. It provides a flexible and efficient way to interact with the database.
   - **File**: `app.py`
   - **Function**: `graphql`

### Database Initialization

7. **Database Initialization**:
   - The application initializes the database with default users and prescriptions during startup. It checks if there are any prescriptions for a specific user and, if not, adds 89 prescriptions to the database.
   - **File**: `app.py`
   - **Function**: `__main__`

## Important Patterns

- **Model-View-Controller (MVC)**:
  - The application follows a MVC pattern, where:
    - **Model**: SQLAlchemy models represent the database schema.
    - **View**: Flask routes and templates handle the presentation layer.
    - **Controller**: Flask routes and functions manage the business logic and data flow.

- **Event-Driven**:
  - The application is event-driven in the sense that it responds to HTTP requests and user actions, triggering specific functions to handle these events.

- **Layered Architecture**:
  - The application is structured in layers:
    - **Presentation Layer**: Flask routes and templates.
    - **Business Logic Layer**: Functions in `app.py` that handle user authentication, prescription management, and database operations.
    - **Data Access Layer**: SQLAlchemy models and database sessions.

## Key Files and Functions

- **`app.py`**:
  - **Initialization**: `__main__` - Initializes the database and starts the Flask application.
  - **Routes**:
    - `home`: Redirects to the login page.
    - `login`: Handles user login.
    - `logout`: Logs out the current user.
    - `add_prescription`: Renders the add prescription page.
    - `view_prescriptions`: Renders the view prescriptions page.
    - `graphql`: Provides a GraphQL endpoint for data operations.

By understanding these components and their interactions, you can effectively navigate and extend the application.

---

# Authentication and Security

This section details the authentication mechanisms, including user login, session management, and security practices implemented in the application.

## Overview

The application uses Flask for web development, SQLAlchemy for database operations, and JWT (JSON Web Tokens) for session management. The main entry points for authentication and security are defined in `app.py`.

## User Authentication

### Login and Logout

- **Login (`/login`)**:
  - **Endpoint**: `POST /login`
  - **Function**: `login`
  - **Description**: This endpoint handles user login by checking the provided credentials against the database. If the credentials are valid, a JWT token is generated and returned to the user.
  - **File**: `app.py`

- **Logout (`/logout`)**:
  - **Endpoint**: `GET /logout`
  - **Function**: `logout`
  - **Description**: This endpoint logs out the current user by invalidating the session and redirecting the user to the login page.
  - **File**: `app.py`

### Session Management

- **JWT Tokens**:
  - The application uses JWT tokens to manage user sessions. Upon successful login, a JWT token is generated and sent to the client. This token is used to authenticate subsequent requests.
  - **File**: `app.py`

## Database Operations

- **User and Prescription Models**:
  - The application uses SQLAlchemy to define and interact with the database. User and prescription models are defined to manage user data and prescription records.
  - **File**: `app.py`

- **Initialization**:
  - The application initializes the database with default users and prescriptions during startup. This ensures that there is data available for testing and development.
  - **Function**: `__main__`
  - **File**: `app.py`

## Security Practices

- **Password Handling**:
  - User passwords are securely stored and verified using appropriate hashing algorithms.
  - **File**: `app.py`

- **Input Validation**:
  - The application validates user input to prevent common security vulnerabilities such as SQL injection and cross-site scripting (XSS).
  - **File**: `app.py`

- **Access Control**:
  - Access to certain routes, such as adding and viewing prescriptions, is restricted to authenticated users. The application checks the JWT token to ensure that only authenticated users can access these routes.
  - **Routes**: `/add_prescription`, `/view_prescriptions`
  - **File**: `app.py`

## GraphQL Endpoint

- **GraphQL (`/graphql`)**:
  - **Endpoint**: `GET /graphql`
  - **Function**: `graphql`
  - **Description**: This endpoint provides a GraphQL interface for querying and mutating prescription data. It allows authenticated users to perform operations on prescription records.
  - **File**: `app.py`

## Initialization and Configuration

- **Database Initialization**:
  - The application initializes the database with default users and prescriptions during startup. This is done in the `__main__` function.
  - **Function**: `__main__`
  - **File**: `app.py`

- **Flask Application**:
  - The Flask application is set up and configured in `app.py`. It includes the necessary configurations for user authentication, database operations, and GraphQL endpoints.
  - **File**: `app.py`

By following these practices, the application ensures a secure and robust authentication and security framework.

---

# Database and Data Models

This section provides an overview of the database schema, ORM models, and data initialization processes used in the application. The primary components involved are the Flask application, SQLAlchemy for database operations, and the initialization of default users and prescriptions.

## Database Schema

The database schema is managed using SQLAlchemy, an Object-Relational Mapping (ORM) library. The schema is defined in the `app.py` file, where the Flask application is set up. The schema includes models for users and prescriptions, which are used to store and manage data.

### Key Models

- **User Model**: Represents the users of the application. This model includes fields such as username, password, and other user-specific information.
- **Prescription Model**: Represents the prescriptions in the application. This model includes fields such as user ID, prescription details, and timestamps.

## ORM Models

The ORM models are defined within the Flask application setup in `app.py`. These models are used to interact with the database, perform CRUD operations, and manage relationships between entities.

### User Model

The `User` model is defined to handle user authentication and authorization. It includes methods for checking credentials and managing user sessions.

### Prescription Model

The `Prescription` model is defined to handle the storage and retrieval of prescription data. It includes methods for adding, updating, and querying prescriptions.

## Data Initialization

The data initialization process is handled in the `app.py` file. This process ensures that the database is set up with default users and prescriptions when the application starts.

### Initialization Process

1. **Database Initialization**:
   - The database is initialized using SQLAlchemy. This involves creating the necessary tables and setting up the database schema.
   - The initialization function is called in the `__main__` block of `app.py`.

2. **Default Users**:
   - The application checks if there are any existing users in the database.
   - If no users are found, default users are added to the database. This ensures that the application has at least one user to start with.

3. **Default Prescriptions**:
   - For each default user, the application checks if there are any prescriptions.
   - If no prescriptions are found, a set of default prescriptions (89 in this case) is added to the database for each user.

### Code Snippet

```python
# XBEN-007-24\app\app.py:121-145
def initialize_database():
    # Initialize the database
    db.create_all()

    # Check if there are any users
    if not User.query.first():
        # Add default users
        default_user = User(username='default_user', password='default_password')
        db.session.add(default_user)
        db.session.commit()

        # Add default prescriptions for the user
        for i in range(89):
            prescription = Prescription(user_id=default_user.id, details=f'Prescription {i+1}')
            db.session.add(prescription)
        db.session.commit()

if __name__ == '__main__':
    initialize_database()
    app.run()
```

## Database Operations

The application uses SQLAlchemy to perform various database operations, including querying, adding, updating, and deleting records.

### Key Operations

- **Querying Users**:
  - The `User.query.first()` method is used to check if there are any users in the database.
  - The `User.query.filter_by(username='username').first()` method is used to retrieve a user by username.

- **Adding Users**:
  - The `User` model is instantiated with the required fields, and the user is added to the session using `db.session.add(user)`.
  - The changes are committed to the database using `db.session.commit()`.

- **Adding Prescriptions**:
  - The `Prescription` model is instantiated with the required fields, and the prescription is added to the session using `db.session.add(prescription)`.
  - The changes are committed to the database using `db.session.commit()`.

## GraphQL Endpoint

The application includes a GraphQL endpoint for querying and mutating prescription data. This endpoint is defined in `app.py` and allows clients to interact with the database using GraphQL queries and mutations.

### GraphQL Endpoint

- **Path**: `/graphql`
- **Methods**: `GET`, `POST`

The GraphQL endpoint provides a flexible and powerful way to query and manipulate prescription data. It supports various operations, including fetching prescriptions for a specific user, adding new prescriptions, and updating existing prescriptions.

## Conclusion

The database and data models in this application are designed to support user authentication, prescription management, and data initialization. The use of SQLAlchemy and GraphQL ensures efficient and flexible data handling, making the application robust and scalable.

---

# GraphQL API

This section provides an overview of the GraphQL API endpoint in the application, including how to query and mutate prescription data. The GraphQL endpoint is integrated into a Flask application and is accessible via the `/graphql` route.

## Overview

The GraphQL API is designed to provide a flexible and efficient way to interact with prescription data. It allows clients to specify exactly what data they need, reducing the amount of data transferred and improving performance. The API is secured with user authentication, ensuring that only authenticated users can access and modify prescription data.

## Setup and Initialization

The GraphQL API is set up in the `app.py` file, which initializes a Flask application and configures the necessary components:

- **User Authentication**: The application uses JWT (JSON Web Tokens) for user authentication. Users must log in to access the GraphQL endpoint.
- **Database Operations**: SQLAlchemy is used for database operations, including querying and mutating prescription data.
- **Routes**: The application defines several routes for user authentication and prescription management:
  - `GET /`: Redirects to the login page.
  - `GET /login`: Renders the login page.
  - `POST /login`: Handles user login, checking credentials and authenticating the user.
  - `GET /logout`: Logs out the current user and redirects to the login page.
  - `GET /add_prescription`: Renders the add prescription page for authenticated users.
  - `GET /view_prescriptions`: Renders the view prescriptions page for authenticated users.
  - `GET /graphql`: Provides the GraphQL endpoint for querying and mutating prescription data.

## GraphQL Endpoint

The GraphQL endpoint is accessible at the `/graphql` route. It supports both query and mutation operations.

### Querying Prescription Data

To query prescription data, you can use the following GraphQL query:

```graphql
query {
  prescriptions {
    id
    patientName
    medication
    dosage
    datePrescribed
  }
}
```

This query retrieves a list of prescriptions, including their ID, patient name, medication, dosage, and date prescribed.

### Mutating Prescription Data

To add a new prescription, you can use the following GraphQL mutation:

```graphql
mutation {
  addPrescription(input: {
    patientName: "John Doe",
    medication: "Ibuprofen",
    dosage: "200mg",
    datePrescribed: "2023-10-01"
  }) {
    id
    patientName
    medication
    dosage
    datePrescribed
  }
}
```

This mutation adds a new prescription to the database and returns the created prescription's details.

### Example Usage

Here is an example of how to use the GraphQL endpoint to query and mutate prescription data using a GraphQL client:

#### Query Example

```http
GET /graphql
Content-Type: application/json

{
  "query": "query { prescriptions { id, patientName, medication, dosage, datePrescribed } }"
}
```

#### Mutation Example

```http
POST /graphql
Content-Type: application/json

{
  "query": "mutation { addPrescription(input: { patientName: \"John Doe\", medication: \"Ibuprofen\", dosage: \"200mg\", datePrescribed: \"2023-10-01\" }) { id, patientName, medication, dosage, datePrescribed } }"
}
```

## Security and Authentication

The GraphQL endpoint is protected by user authentication. Users must be logged in to access the endpoint. The authentication process involves the following steps:

1. **Login**: Users send a POST request to the `/login` endpoint with their username and password.
2. **Token Generation**: Upon successful authentication, the server generates a JWT token and returns it to the client.
3. **Token Verification**: For subsequent requests to the GraphQL endpoint, the client must include the JWT token in the `Authorization` header.

Example of a login request:

```http
POST /login
Content-Type: application/json

{
  "username": "user",
  "password": "password"
}
```

Upon successful login, the server responds with a JWT token:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

For subsequent requests to the GraphQL endpoint, include the token in the `Authorization` header:

```http
GET /graphql
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

{
  "query": "query { prescriptions { id, patientName, medication, dosage, datePrescribed } }"
}
```

## Initialization and Configuration

The application initializes the database and sets up default users and prescriptions during startup. This is handled in the `app.py` file:

- **Database Initialization**: The application checks if there are any users in the database. If not, it adds a default user.
- **Prescription Initialization**: If the default user has no prescriptions, the application adds 89 sample prescriptions to the database.

This ensures that the application is ready to use with some initial data.

## Conclusion

The GraphQL API in this application provides a powerful and flexible way to interact with prescription data. It is secured with user authentication and integrates seamlessly with the Flask application and SQLAlchemy for database operations. By following the examples and guidelines provided, you can effectively query and mutate prescription data using the GraphQL endpoint.

---