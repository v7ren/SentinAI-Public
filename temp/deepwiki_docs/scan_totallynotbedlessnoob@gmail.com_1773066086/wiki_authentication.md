# Authentication and Authorization

This section explains the authentication and authorization mechanisms used in TaskFlow, including JWT tokens, user roles, and middleware for securing routes.

## Overview

TaskFlow uses a combination of JSON Web Tokens (JWT) and role-based access control (RBAC) to manage user authentication and authorization. The system ensures that only authenticated and authorized users can access specific resources and perform actions.

### Key Components

- **JWT Tokens**: Used for user authentication.
- **User Roles**: Define the permissions and access levels of users.
- **Middleware**: Enforces authentication and authorization rules.

## Authentication

### JWT Tokens

JWT tokens are used to authenticate users. The tokens are generated and verified using the `jsonwebtoken` library and environment variables for secrets.

- **Token Generation**: Tokens are generated during user login and registration.
- **Token Verification**: Tokens are verified on each protected route to ensure the user is authenticated.

#### Files Involved

- **`taskflow/backend/src/controllers/authController.js`**: Handles user registration, login, token refresh, password reset, and logout.
- **`taskflow/backend/src/utils/tokenUtils.js`**: Provides utility functions for signing and verifying JWT tokens.

### Authentication Middleware

The `authenticate` middleware is used to verify the JWT token in the `Authorization` header of incoming HTTP requests. If the token is valid, user information is attached to the request object. If the token is missing, invalid, or expired, a 401 Unauthorized response is returned.

#### Files Involved

- **`taskflow/backend/src/middleware/authenticate.js`**: Defines the `authenticate` middleware.

### Logout

The `logout` function invalidates the refresh token by setting it to `null` in the database.

#### Files Involved

- **`taskflow/backend/src/controllers/authController.js`**: Handles the logout process.

## Authorization

### User Roles

User roles are used to define the permissions and access levels of users. The `authorize` middleware checks if the user has the required role to access a resource.

#### Files Involved

- **`taskflow/backend/src/middleware/authorize.js`**: Defines the `authorize` middleware.

### Role-Based Access Control (RBAC)

RBAC is implemented to ensure that users can only access resources and perform actions based on their roles. For example, only admin users can manage other users and view billing information.

#### Files Involved

- **`taskflow/backend/src/controllers/adminController.js`**: Contains admin-specific operations such as retrieving all users, deleting a user, and getting a billing overview.
- **`taskflow/backend/src/routes/adminRoutes.js`**: Defines admin-specific routes, all of which require authentication and the appropriate role.

## Middleware

### Error Handling

The `errorHandler` middleware logs errors and sends a JSON response with the error message, stack trace, and status code.

#### Files Involved

- **`taskflow/backend/src/middleware/errorHandler.js`**: Defines the error handling middleware.

### Rate Limiting

The `reportLimiter` middleware limits the rate of report generation requests to prevent abuse of the PDF export feature.

#### Files Involved

- **`taskflow/backend/src/middleware/rateLimiter.js`**: Defines the rate limiter for report generation.

### File Upload

The `upload` middleware is configured to handle file uploads, setting the upload directory and defining how files are stored.

#### Files Involved

- **`taskflow/backend/src/middleware/upload.js`**: Configures the file upload middleware using Multer.

## Frontend Integration

### Authentication Context

The `AuthContext` provides authentication state and functions to the React application. It includes hooks for managing user login, registration, and logout.

#### Files Involved

- **`taskflow/frontend/src/context/AuthContext.jsx`**: Defines the authentication context and hooks.
- **`taskflow/frontend/src/hooks/useAuth.js`**: Re-exports the `useAuth` hook from `AuthContext`.

### Axios Client

The Axios client is configured with interceptors to add authentication tokens to requests and handle unauthorized responses by redirecting to the login page.

#### Files Involved

- **`taskflow/frontend/src/api/client.js`**: Sets up the Axios client with interceptors.

### Private Routes

Private routes in the frontend require user authentication. Unauthenticated users are redirected to the login page.

#### Files Involved

- **`taskflow/frontend/src/App.jsx`**: Sets up routing with private routes.

### Authentication Pages

The login and registration pages handle user input and authentication logic.

#### Files Involved

- **`taskflow/frontend/src/pages/LoginPage.jsx`**: Handles user login.
- **`taskflow/frontend/src/pages/RegisterPage.jsx`**: Handles user registration.

## Conclusion

TaskFlow's authentication and authorization mechanisms ensure that only authenticated and authorized users can access and modify resources. JWT tokens and role-based access control are the core components of this system, with middleware enforcing these rules and handling errors and rate limiting. The frontend integrates seamlessly with these mechanisms to provide a secure and user-friendly experience.