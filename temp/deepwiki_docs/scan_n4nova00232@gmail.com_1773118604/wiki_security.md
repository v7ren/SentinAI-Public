# Security

This section covers the security measures implemented in the TaskFlow application, including authentication, authorization, and data protection. The security architecture is designed to ensure that only authorized users can access and manipulate data, and that sensitive information is protected.

## Authentication

### JWT Token Management
- **File:** `taskflow/backend/src/utils/tokenUtils.js`
- **Description:** This file contains utility functions for generating and verifying JWT (JSON Web Token) access and refresh tokens. It uses the `jsonwebtoken` library and environment variables for secrets.
- **Key Functions:**
  - `signAccess`: Generates an access token.
  - `signRefresh`: Generates a refresh token.
  - `verifyAccess`: Verifies an access token.
  - `verifyRefresh`: Verifies a refresh token.

### Authentication Middleware
- **File:** `taskflow/backend/src/middleware/authenticate.js`
- **Description:** This middleware function checks the authorization header for a valid Bearer token and verifies the JWT token using the `verifyAccess` function from `tokenUtils`. If the token is valid, it attaches user information to the request object; otherwise, it returns a 401 Unauthorized response.
- **Key Function:**
  - `authenticate`: Middleware function for token verification.

### Frontend Authentication
- **File:** `taskflow/frontend/src/api/auth.js`
- **Description:** This file provides functions for user authentication, including login, registration, logout, and token refresh. It uses an Axios client to make HTTP POST requests to the corresponding API endpoints.
- **Key Functions:**
  - `login`: Sends a POST request to the login endpoint.
  - `register`: Sends a POST request to the register endpoint.
  - `logout`: Sends a POST request to the logout endpoint.
  - `refreshToken`: Sends a POST request to the refresh token endpoint.

### Authentication Context
- **File:** `taskflow/frontend/src/context/AuthContext.jsx`
- **Description:** This file defines a React context for managing authentication state, including user login, registration, and logout. It provides a context provider and a custom hook to access the context.
- **Key Components:**
  - `AuthProvider`: React component that provides authentication state and actions to its children.
  - `useAuth`: Custom hook that allows components to access the authentication context.

## Authorization

### Role-Based Access Control
- **File:** `taskflow/backend/src/middleware/authorize.js`
- **Description:** This middleware function checks if the user is authenticated and if their role is among the allowed roles for the requested resource. It returns a 401 status if the user is not authenticated, and a 403 status if the user does not have sufficient permissions.
- **Key Function:**
  - `authorize`: Middleware function for role-based access control.

### Admin Routes
- **File:** `taskflow/backend/src/routes/adminRoutes.js`
- **Description:** This file defines an Express router for admin-specific routes, including endpoints to manage users and view billing information. All routes require authentication.
- **Key Endpoints:**
  - `GET /users`: Retrieves all users.
  - `DELETE /users/:id`: Deletes a user by ID.
  - `GET /billing`: Retrieves a billing overview.

### User Routes
- **File:** `taskflow/backend/src/routes/userRoutes.js`
- **Description:** This file sets up an Express router for user-related endpoints, requiring authentication for all routes. It defines routes for retrieving and updating a user's profile.
- **Key Endpoints:**
  - `GET /profile`: Retrieves the user's profile information.
  - `PATCH /profile`: Updates the user's profile information.

## Data Protection

### Database Security
- **File:** `taskflow/backend/config/db.js`
- **Description:** This file sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries. It uses environment variables for configuration, with fallbacks for local development.
- **Key Functions:**
  - `pool`: A PostgreSQL connection pool instance.
  - `query`: A function that takes SQL text and parameters, and executes the query using the connection pool.

### Rate Limiting
- **File:** `taskflow/backend/src/middleware/rateLimiter.js`
- **Description:** This file sets up a rate limiter middleware for an Express application, specifically for limiting the number of report generation requests to prevent abuse of the PDF export feature.
- **Key Function:**
  - `reportLimiter`: Middleware function that limits the rate of report generation requests to 10 per minute.

### Error Handling
- **File:** `taskflow/backend/src/middleware/errorHandler.js`
- **Description:** This file defines a middleware function for handling errors in an Express.js application. It logs the error details and sends a JSON response with the error message, stack trace, and status code.
- **Key Function:**
  - `errorHandler`: Middleware function that handles errors by logging them and sending a JSON response.

### File Upload Security
- **File:** `taskflow/backend/src/middleware/upload.js`
- **Description:** This file configures and exports a multer middleware for handling file uploads. It sets the upload directory and defines how files are stored, including their destination and naming conventions.
- **Key Function:**
  - `upload`: Multer middleware instance configured for file uploads.

### Logging
- **File:** `taskflow/backend/src/utils/logger.js`
- **Description:** This file defines a simple logging utility that formats log entries as JSON objects and outputs them to the console. It supports different log levels: info, warn, and error.
- **Key Functions:**
  - `info`: Logs an informational message with optional metadata.
  - `warn`: Logs a warning message with optional metadata.
  - `error`: Logs an error message with optional metadata.

### Frontend API Client
- **File:** `taskflow/frontend/src/api/client.js`
- **Description:** This file sets up an Axios client for making HTTP requests to a backend API. It includes interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to the login page.
- **Key Function:**
  - `client`: Axios client instance configured with interceptors.

## Conclusion

The TaskFlow application implements a robust security architecture to ensure that only authorized users can access and manipulate data. Key components include JWT token management, role-based access control, database security, rate limiting, error handling, and secure file uploads. These measures collectively help protect sensitive information and maintain the integrity of the application.