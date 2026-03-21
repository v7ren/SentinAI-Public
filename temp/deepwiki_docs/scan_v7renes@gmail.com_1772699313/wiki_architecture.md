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