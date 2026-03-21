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