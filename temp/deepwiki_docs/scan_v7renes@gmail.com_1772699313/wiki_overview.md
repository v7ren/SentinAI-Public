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