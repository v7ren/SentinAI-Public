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