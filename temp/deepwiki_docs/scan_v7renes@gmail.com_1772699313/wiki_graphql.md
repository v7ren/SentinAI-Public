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