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