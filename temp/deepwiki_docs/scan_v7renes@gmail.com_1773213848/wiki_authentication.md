# Authentication and Authorization

This section covers the authentication and authorization mechanisms used in the TaskFlow application, including user registration, login, token management, and role-based access control.

## Overview

The authentication and authorization system in TaskFlow is designed to ensure secure access to the application's resources. It includes the following key components:

- **User Registration and Login**: Users can register and log in using their email and password.
- **Token Management**: JSON Web Tokens (JWT) are used for session management.
- **Role-Based Access Control (RBAC)**: Different user roles (e.g., admin, regular user) have different levels of access to resources.
- **Middleware**: Middleware functions handle authentication and authorization checks for protected routes.

## User Registration and Login

### User Registration

- **File**: `taskflow\backend\src\controllers\authController.js`
- **Function**: `register`
- **Endpoint**: `POST /api/register`
- **Description**: Handles user registration by validating the input, hashing the password, and creating a new user and organization record in the database.

### User Login

- **File**: `taskflow\backend\src\controllers\authController.js`
- **Function**: `login`
- **Endpoint**: `POST /api/login`
- **Description**: Handles user login by validating the credentials, generating a JWT access token, and returning it to the client.

### Token Refresh

- **File**: `taskflow\backend\src\controllers\authController.js`
- **Function**: `refresh`
- **Endpoint**: `POST /api/refresh`
- **Description**: Handles token refresh by validating the refresh token and generating a new access token.

### Password Reset

- **File**: `taskflow\backend\src\controllers\authController.js`
- **Functions**: `forgotPassword`, `resetPassword`
- **Endpoints**: 
  - `POST /api/forgot-password`
  - `POST /api/reset-password`
- **Description**: Handles password reset requests by sending a reset link to the user's email and updating the user's password.

### User Logout

- **File**: `taskflow\backend\src\controllers\authController.js`
- **Function**: `logout`
- **Endpoint**: `POST /api/logout`
- **Description**: Handles user logout by invalidating the refresh token.

## Token Management

### Token Utilities

- **File**: `taskflow\backend\src\utils\tokenUtils.js`
- **Functions**: `signToken`, `verifyToken`
- **Description**: Provides utility functions for signing and verifying JWT tokens.

### Authentication Middleware

- **File**: `taskflow\backend\src\middleware\authenticate.js`
- **Function**: `authenticate`
- **Description**: Middleware function that checks the authorization header and verifies the JWT token. If the token is valid, it attaches user information to the request object; otherwise, it returns a 401 Unauthorized response.

### Authorization Middleware

- **File**: `taskflow\backend\src\middleware\authorize.js`
- **Function**: `authorize`
- **Description**: Middleware function that checks if the user has the required roles to access a resource. It returns a 401 status if the user is not authenticated, and a 403 status if the user does not have sufficient permissions.

## Role-Based Access Control (RBAC)

### Admin Routes

- **File**: `taskflow\backend\src\routes\adminRoutes.js`
- **Endpoints**:
  - `GET /admin/users` - Fetches all users.
  - `DELETE /admin/users/:id` - Deletes a user by ID.
  - `GET /admin/billing` - Fetches a billing overview.
- **Description**: These routes are protected by authentication and require admin role to access.

### User Routes

- **File**: `taskflow\backend\src\routes\userRoutes.js`
- **Endpoints**:
  - `GET /profile` - Retrieves the user's profile information.
  - `PATCH /profile` - Updates the user's profile information.
- **Description**: These routes are protected by authentication and allow users to manage their own profiles.

### Project Routes

- **File**: `taskflow\backend\src\routes\projectRoutes.js`
- **Endpoints**:
  - `GET /projects` - Lists all projects.
  - `GET /projects/:projectId` - Retrieves a single project by ID.
  - `POST /projects` - Creates a new project.
  - `PUT /projects/:projectId` - Updates an existing project.
  - `DELETE /projects/:projectId` - Deletes a project.
- **Description**: These routes are protected by authentication and allow users to manage projects within their organization.

### Task Routes

- **File**: `taskflow\backend\src\routes\taskRoutes.js`
- **Endpoints**:
  - `GET /tasks` - Lists all tasks.
  - `GET /tasks/:taskId` - Retrieves a single task by ID.
  - `POST /tasks` - Creates a new task.
  - `PUT /tasks/:taskId` - Updates an existing task.
  - `DELETE /tasks/:taskId` - Deletes a task.
- **Description**: These routes are protected by authentication and allow users to manage tasks within their projects.

### Notification Routes

- **File**: `taskflow\backend\src\routes\notificationRoutes.js`
- **Endpoints**:
  - `GET /notifications` - Lists all notifications for the authenticated user.
  - `POST /notifications/:id/read` - Marks a specific notification as read.
  - `GET /notifications/preferences` - Retrieves the notification preferences for the authenticated user.
  - `PATCH /notifications/preferences` - Updates the notification preferences for the authenticated user.
- **Description**: These routes are protected by authentication and allow users to manage their notifications and preferences.

## Frontend Authentication

### Authentication Context

- **File**: `taskflow\frontend\src\context\AuthContext.jsx`
- **Components**: `AuthProvider`, `useAuth`
- **Description**: Provides authentication state and functions to the React application. It includes functions for logging in, registering, and logging out, which interact with the authentication API and local storage.

### Authentication Pages

- **Login Page**

  - **File**: `taskflow\frontend\src\pages\LoginPage.jsx`
  - **Component**: `LoginPage`
  - **Description**: A React component for the login page, including form fields for email and password, and handling the submission of login credentials to authenticate the user.

- **Register Page**

  - **File**: `taskflow\frontend\src\pages\RegisterPage.jsx`
  - **Component**: `RegisterPage`
  - **Description**: A React component for the registration page, including form fields for full name, email, and password, and handling the submission of registration credentials.

### Axios Client

- **File**: `taskflow\frontend\src\api\client.js`
- **Component**: `client`
- **Description**: An Axios client configured with interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to the login page.

### Authentication Utilities

- **File**: `taskflow\frontend\src\utils\authUtils.js`
- **Functions**: `saveSession`, `clearSession`, `getToken`, `getRefreshToken`, `getStoredUser`
- **Description**: Utility functions for managing authentication sessions in local storage, including saving, clearing, and retrieving session tokens and user data.

## Conclusion

The authentication and authorization system in TaskFlow is robust and ensures that only authenticated and authorized users can access the application's resources. The use of JWT tokens, middleware functions, and role-based access control provides a secure and flexible way to manage user sessions and permissions.