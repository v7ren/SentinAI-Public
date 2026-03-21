# Authentication and Authorization

This section provides an overview of the authentication and authorization mechanisms used in the TaskFlow application. It covers the use of JWT tokens, user roles, and session management.

## Overview

### JWT Tokens
The TaskFlow application uses JSON Web Tokens (JWT) for authentication. JWTs are used to securely transmit information between the client and the server. The tokens are generated upon successful login and are required for accessing protected routes.

### User Roles
User roles are used to manage permissions and access levels within the application. The application supports different roles, such as `admin` and `user`, which determine the actions a user can perform.

### Session Management
Session management is handled using JWT tokens stored in the client's local storage. The tokens are validated on each request to ensure the user is authenticated and has the necessary permissions.

## Key Files and Components

### Authentication Middleware

#### `taskflow/backend/src/middleware/authenticate.js`
- **Summary**: This file defines a middleware function for authenticating HTTP requests by verifying a JWT token in the authorization header.
- **Key Functions**:
  - `authenticate`: Verifies the JWT token and attaches user information to the request object. If the token is missing, invalid, or expired, it responds with a 401 Unauthorized status.
- **Tags**: `auth`, `security`, `logging`

#### `taskflow/backend/src/middleware/authorize.js`
- **Summary**: This file defines a middleware function for authorizing user roles in an HTTP request handling chain.
- **Key Functions**:
  - `authorize`: Checks if the user has the required roles to access a resource. It returns a 401 status if the user is not authenticated, and a 403 status if the user does not have sufficient permissions.
- **Tags**: `auth`, `security`

### Authentication Controller

#### `taskflow/backend/src/controllers/authController.js`
- **Summary**: This file contains the implementation of authentication-related endpoints, including user registration, login, token refresh, password reset, and logout functionalities.
- **Key Endpoints**:
  - `register`: Handles user registration, including validation, password hashing, and creation of user and organization records.
  - `login`: Handles user login, including credential validation and token generation.
  - `refresh`: Handles token refresh, generating a new access token from a valid refresh token.
  - `forgotPassword`: Handles password reset requests, sending a reset link to the user's email if the email exists.
  - `resetPassword`: Handles password reset, updating the user's password with a new hashed password.
  - `logout`: Handles user logout, invalidating the user's refresh token.
- **Tags**: `auth`, `db`, `crypto`, `network`, `logging`

### User Model

#### `taskflow/backend/src/models/userModel.js`
- **Summary**: This file contains a set of asynchronous functions for interacting with the `users` table in the database.
- **Key Functions**:
  - `findUserById`: Finds a user by their ID.
  - `findUserByEmail`: Finds a user by their email.
  - `createUser`: Creates a new user record.
  - `updateRefreshToken`: Updates the user's refresh token.
  - `setResetToken`: Sets a reset token for the user.
  - `clearResetToken`: Clears the reset token for the user.
  - `updatePassword`: Updates the user's password.
- **Tags**: `db`

### Token Utilities

#### `taskflow/backend/src/utils/tokenUtils.js`
- **Summary**: This file contains utility functions for generating and verifying JWT access and refresh tokens.
- **Key Functions**:
  - `signToken`: Generates a JWT access token.
  - `signRefreshToken`: Generates a JWT refresh token.
  - `verifyToken`: Verifies a JWT access token.
  - `verifyRefreshToken`: Verifies a JWT refresh token.
- **Tags**: `auth`, `crypto`, `security`

### Authentication Routes

#### `taskflow/backend/src/routes/authRoutes.js`
- **Summary**: This file defines an Express router for handling authentication-related routes such as registration, login, password management, and logout.
- **Key Endpoints**:
  - `POST /register`: Handles user registration.
  - `POST /login`: Handles user login.
  - `POST /refresh`: Handles token refresh.
  - `POST /forgot-password`: Handles password reset requests.
  - `POST /reset-password`: Handles password reset.
  - `POST /logout`: Handles user logout, with authentication middleware.
- **Tags**: `auth`, `network`

### Frontend Authentication

#### `taskflow/frontend/src/context/AuthContext.jsx`
- **Summary**: This file defines an authentication context for a React application, providing state management and functions for user login, registration, and logout.
- **Key Functions**:
  - `AuthProvider`: Provides authentication context to its children, including user state and authentication functions.
  - `useAuth`: A custom hook that allows components to access the authentication context provided by `AuthProvider`.
- **Tags**: `auth`, `network`

#### `taskflow/frontend/src/api/auth.js`
- **Summary**: This file contains functions for handling authentication operations such as login, registration, logout, and token refreshing.
- **Key Functions**:
  - `login`: Sends a POST request to the login endpoint with email and password.
  - `register`: Sends a POST request to the register endpoint with email, password, and full name.
  - `logout`: Sends a POST request to the logout endpoint.
  - `refreshToken`: Sends a POST request to the refresh token endpoint with the refresh token.
- **Tags**: `auth`, `network`

### Frontend Authentication Utilities

#### `taskflow/frontend/src/utils/authUtils.js`
- **Summary**: This file contains utility functions for managing authentication sessions in a frontend application.
- **Key Functions**:
  - `saveSession`: Saves the authentication token, user object, and refresh token to localStorage.
  - `clearSession`: Clears the authentication token, user object, and refresh token from localStorage.
  - `getToken`: Retrieves the authentication token from localStorage.
  - `getRefreshToken`: Retrieves the refresh token from localStorage.
  - `getStoredUser`: Retrieves the user object from localStorage, parsing it from JSON if it exists.
- **Tags**: `auth`, `storage`

### Frontend Authentication Pages

#### `taskflow/frontend/src/pages/LoginPage.jsx`
- **Summary**: This file defines a React component for a login page, which includes form fields for email and password, and handles the submission of login credentials to authenticate a user.
- **Key Functions**:
  - `handleLogin`: Handles form submission to authenticate the user.
- **Tags**: `auth`, `ui`

#### `taskflow/frontend/src/pages/RegisterPage.jsx`
- **Summary**: This file defines a React component for a user registration page.
- **Key Functions**:
  - `handleRegister`: Handles form submission to register the user.
- **Tags**: `auth`, `ui`

### Frontend Protected Routes

#### `taskflow/frontend/src/App.jsx`
- **Summary**: This file defines the main application component for a React-based frontend. It sets up routing for various pages, including public and private routes. Private routes require user authentication, redirecting unauthenticated users to the login page.
- **Key Functions**:
  - `PrivateRoute`: A higher-order component that checks if the user is authenticated before rendering the protected route.
- **Tags**: `auth`, `network`, `other`

### Frontend API Client

#### `taskflow/frontend/src/api/client.js`
- **Summary**: This file sets up an Axios client for making HTTP requests to a backend API. It includes interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to the login page.
- **Key Functions**:
  - `client`: The Axios client instance configured with a base URL and interceptors for authentication and response handling.
- **Tags**: `auth`, `network`, `logging`, `security`

### Frontend Navigation and Layout

#### `taskflow/frontend/src/components/Layout/Navbar.jsx`
- **Summary**: This file defines a React component named Navbar, which is used to display a navigation bar at the top of the application.
- **Key Functions**:
  - `useAuth`: Manages authentication state and provides a logout button.
- **Tags**: `auth`, `ui`

#### `taskflow/frontend/src/components/Layout/Sidebar.jsx`
- **Summary**: This file defines a Sidebar component for a React application. It uses the `react-router-dom` package to create navigation links and the `useAuth` custom hook to manage user authentication.
- **Key Functions**:
  - `useAuth`: Manages authentication state and provides navigation links based on the user's role.
- **Tags**: `auth`, `ui`

### Frontend User Management

#### `taskflow/frontend/src/pages/AdminPage.jsx`
- **Summary**: This file defines a React component named AdminPage, which serves as a page for administrative tasks. It renders a `PageWrapper` component with a title 'Admin' and includes a `UserTable` component to display user data.
- **Key Functions**:
  - `useAuth`: Manages authentication state and ensures only admin users can access this page.
- **Tags**: `auth`, `ui`

#### `taskflow/frontend/src/components/Admin/UserTable.jsx`
- **Summary**: This file defines a React component named UserTable, which displays a table of users fetched from an API. It includes functionality to load users, display them, and delete a user with confirmation.
- **Key Functions**:
  - `fetchUsers`: Fetches user data from the API.
  - `handleDelete`: Handles the deletion of a user.
- **Tags**: `network`, `ui`

### Frontend User Settings

#### `taskflow/frontend/src/pages/SettingsPage.jsx`
- **Summary**: This file defines a React component named SettingsPage, which allows users to update their full name. It uses a custom hook for authentication and makes an API call to update the user's profile.
- **Key Functions**:
  - `useAuth`: Manages authentication state.
  - `handleUpdate`: Handles the update of the user's profile.
- **Tags**: `auth`, `network`, `ui`

### Frontend Project and Task Management

#### `taskflow/frontend/src/pages/ProjectsPage.jsx`
- **Summary**: This file defines a React component named ProjectsPage, which displays a list of projects and provides a modal for creating new projects. It uses the `useProjects` hook to fetch and manage project data.
- **Key Functions**:
  - `useProjects`: Manages project state and API interactions.
- **Tags**: `auth`, `network`, `ui`

#### `taskflow/frontend/src/pages/TasksPage.jsx`
- **Summary**: This file defines a React component named TasksPage, which displays a list of tasks and allows users to filter tasks by project and search term. It also provides a modal for creating new tasks.
- **Key Functions**:
  - `useTasks`: Manages task state and API interactions.
- **Tags**: `auth`, `network`, `ui`

### Frontend Task Detail Page

#### `taskflow/frontend/src/pages/TaskDetailPage.jsx`
- **Summary**: This file defines a React component named TaskDetailPage, which serves as a page for displaying detailed information about a task. It uses a `PageWrapper` component to set the page title and a `TaskDetail` component to render the task details.
- **Key Functions**:
  - `useTasks`: Manages task state and API interactions.
- **Tags**: `ui`, `state`, `api`

### Frontend Project Detail Page

#### `taskflow/frontend/src/pages/ProjectDetailPage.jsx`
- **Summary**: This file defines a React component named ProjectDetailPage, which displays details of a project and provides options to view tasks and manage project settings. It fetches project data from an API and handles loading and error states.
- **Key Functions**:
  - `useProjects`: Manages project state and API interactions.
- **Tags**: `network`, `ui`

### Frontend Task Form

#### `taskflow/frontend/src/components/Tasks/TaskForm.jsx`
- **Summary**: This file defines a React component named TaskForm, which is used to create or edit a task. It includes form fields for the task's title, description, priority, status, and due date. The component handles form submission and provides a cancel button to close the form.
- **Key Functions**:
  - `handleSubmit`: Handles form submission.
- **Tags**: `ui`, `form`, `react`

### Frontend Task Detail

#### `taskflow/frontend/src/components/Tasks/TaskDetail.jsx`
- **Summary**: This file defines a React component named TaskDetail, which displays detailed information about a specific task, including its status, priority, due date, title, and description. It fetches the task data from an API endpoint using the task ID from the URL parameters. The component also handles loading and error states, and displays a list of comments associated with the task.
- **Key Functions**:
  - `useTasks`: Manages task state and API interactions.
- **Tags**: `network`, `ui`

### Frontend Comment List

#### `taskflow/frontend/src/components/Tasks/CommentList.jsx`
- **Summary**: This file defines a React component named CommentList, which displays a list of comments for a given task and allows users to add new comments. It fetches comments from an API and updates the list when new comments are posted.
- **Key Functions**:
  - `fetchComments`: Fetches comments from the API.
  - `handleAddComment`: Handles the addition of a new comment.
- **Tags**: `network`, `ui`

### Frontend Project Settings

#### `taskflow/frontend/src/components/Projects/ProjectSettings.jsx`
- **Summary**: This file defines a React component named ProjectSettings, which is used to display and update the settings of a project. It includes fields for the project's name, description, and archived status. The component uses a form to collect user input and calls an `updateProject` function to save changes.
- **Key Functions**:
  - `useProjects`: Manages project state and API interactions.
- **Tags**: `auth`, `db`, `network`, `other`

### Frontend Task Card

#### `taskflow/frontend/src/components/Tasks/TaskCard.jsx`
- **Summary**: This file defines a React component named TaskCard, which displays a card for a task with its title, status, priority, due date, and assignee. The card is a clickable link that navigates to the task's detail page.
- **Key Functions**:
  - `formatPriority`: Formats the priority label.
  - `formatStatus`: Formats the status label.
- **Tags**: `ui`, `react`

### Frontend Project Card

#### `taskflow/frontend/src/components/Projects/ProjectCard.jsx`
- **Summary**: This file defines a React component named ProjectCard, which is used to display a card for a project. The card includes the project's name, a truncated description, and an archived status if applicable. The card is a clickable link that navigates to the project's detail page.
- **Key Functions**:
  - `formatDate`: Formats the project's creation date.
- **Tags**: `other`

### Frontend Formatters

#### `taskflow/frontend/src/utils/formatters.js`
- **Summary**: This file contains utility functions for formatting dates, priorities, and statuses.
- **Key Functions**:
  - `formatDate`: Formats a given date object or string into a short date format.
  - `formatRelative`: Formats a given date object or string into a relative time format based on the current time.
  - `priorityLabel`: Formats a given priority string, capitalizing the first letter and defaulting to 'Medium' if undefined.
  - `statusLabel`: Formats a given status string, replacing underscores with spaces, capitalizing each word, and defaulting to 'Open' if undefined.
- **Tags**: `other`

### Frontend Analytics

#### `taskflow/frontend/src/utils/analytics.js`
- **Summary**: This file contains utility functions for tracking user events and identifying users in Mixpanel and Google Analytics.
- **Key Functions**:
  - `trackEvent`: Tracks an event in Mixpanel and Google Analytics.
  - `identify`: Identifies a user in Mixpanel and Google Analytics.
- **Tags**: `network`, `logging`

### Frontend Vite Configuration

#### `taskflow/frontend/vite.config.js`
- **Summary**: This file configures the Vite development server for a React application, setting up plugins and proxy settings for API and uploads.
- **Key Functions**:
  - `server`: Configures the Vite development server to run on port 3000 and proxy requests to `/api` and `/uploads` to `http://localhost:3001`.
- **Tags**: `config`, `network`

## Conclusion

The authentication and authorization mechanisms in the TaskFlow application are robust and well-integrated across both the backend and frontend. JWT tokens are used for secure authentication, and user roles are enforced to ensure proper access control. The application provides a seamless user experience with protected routes, session management, and user management functionalities.