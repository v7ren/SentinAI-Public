# Architecture and Data Flow

## Overview

The TaskFlow application is a web-based project management tool built using a client-server architecture. The backend is implemented in Node.js with Express, and the frontend is built with React. The application follows a layered architecture, with clear separation of concerns between the presentation, business logic, and data access layers. Key components include the Express server, database models, controllers, and middleware.

## Main Architectural Components

### 1. **Backend Server**
- **Node.js with Express**: The backend is built using Node.js and the Express framework. The server handles HTTP requests and routes them to the appropriate controllers.
- **File**: `taskflow\backend\server.js`
- **Key Functions**:
  - `app.listen`: Starts the server and listens on the specified port (default 3001).

### 2. **Express Application Setup**
- **App Configuration**: The main Express application is set up in `app.js`. It configures middleware, serves static files, and mounts various API routes.
- **File**: `taskflow\backend\src\app.js`
- **Key Functions**:
  - Middleware for JSON and text parsing.
  - Serving static files from the uploads directory.
  - Mounting API routes for authentication, tasks, projects, users, attachments, reports, imports, notifications, and admin functionalities.
  - Health check endpoint (`/api/v1/health`).
  - Error handler middleware.

### 3. **Database Connection**
- **PostgreSQL**: The application uses a PostgreSQL database for storing data. The database connection is managed using the `pg` library.
- **File**: `taskflow\backend\config\db.js`
- **Key Functions**:
  - `pool`: A PostgreSQL connection pool instance.
  - `query`: A function to execute SQL queries using the connection pool.

### 4. **Controllers**
- **Task Management**: Handles CRUD operations for tasks.
  - **File**: `taskflow\backend\src\controllers\taskController.js`
  - **Key Endpoints**:
    - `GET /tasks`: Lists tasks.
    - `GET /tasks/:taskId`: Retrieves a single task.
    - `POST /tasks`: Creates a new task.
    - `PUT /tasks/:taskId`: Updates an existing task.
    - `DELETE /tasks/:taskId`: Deletes a task.
    - `GET /tasks/:taskId/comments`: Retrieves comments for a task.
    - `POST /tasks/:taskId/comments`: Adds a comment to a task.

- **Project Management**: Handles CRUD operations for projects.
  - **File**: `taskflow\backend\src\controllers\projectController.js`
  - **Key Endpoints**:
    - `GET /projects`: Lists projects.
    - `GET /projects/:projectId`: Retrieves a single project.
    - `POST /projects`: Creates a new project.
    - `PUT /projects/:projectId`: Updates an existing project.
    - `DELETE /projects/:projectId`: Deletes a project.

- **User Management**: Handles user-related operations.
  - **File**: `taskflow\backend\src\controllers\userController.js`
  - **Key Endpoints**:
    - `GET /profile`: Retrieves the user's profile.
    - `PUT /profile`: Updates the user's profile.

- **Authentication**: Handles user authentication, including registration, login, token refresh, password reset, and logout.
  - **File**: `taskflow\backend\src\controllers\authController.js`
  - **Key Endpoints**:
    - `POST /api/register`: Registers a new user.
    - `POST /api/login`: Logs in a user.
    - `POST /api/refresh`: Refreshes the access token.
    - `POST /api/forgot-password`: Sends a password reset link.
    - `POST /api/reset-password`: Resets the user's password.
    - `POST /logout`: Logs out the user.

- **Attachments**: Manages task attachments.
  - **File**: `taskflow\backend\src\controllers\attachmentController.js`
  - **Key Endpoints**:
    - `GET /api/tasks/:taskId/attachments`: Lists attachments for a task.
    - `POST /api/tasks/:taskId/attachments`: Uploads a new attachment.
    - `GET /api/tasks/:taskId/attachments/:attachmentId`: Downloads an attachment.
    - `DELETE /api/tasks/:taskId/attachments/:attachmentId`: Deletes an attachment.

- **Reports**: Generates PDF reports for projects.
  - **File**: `taskflow\backend\src\controllers\reportController.js`
  - **Key Endpoints**:
    - `GET /api/reports/:projectId/pdf`: Generates a PDF report for a project.

- **Imports**: Imports tasks from XML and CSV formats.
  - **File**: `taskflow\backend\src\controllers\importController.js`
  - **Key Endpoints**:
    - `POST /api/projects/:projectId/import/xml`: Imports tasks from XML.
    - `POST /api/projects/:projectId/import/csv`: Imports tasks from CSV.

- **Notifications**: Manages user notifications.
  - **File**: `taskflow\backend\src\controllers\notificationController.js`
  - **Key Endpoints**:
    - `GET /notifications`: Lists notifications.
    - `PUT /notifications/:id/read`: Marks a notification as read.
    - `GET /notifications/preferences`: Retrieves notification preferences.
    - `POST /notifications/preferences`: Updates notification preferences.

- **Admin**: Manages administrative tasks.
  - **File**: `taskflow\backend\src\controllers\adminController.js`
  - **Key Endpoints**:
    - `GET /admin/users`: Retrieves all users.
    - `DELETE /admin/users/:id`: Deletes a user.
    - `GET /admin/billing`: Retrieves a billing overview.

### 5. **Middleware**
- **Authentication**: Authenticates HTTP requests by verifying a JWT token.
  - **File**: `taskflow\backend\src\middleware\authenticate.js`
  - **Key Function**: `authenticate`

- **Authorization**: Checks user roles and permissions.
  - **File**: `taskflow\backend\src\middleware\authorize.js`
  - **Key Function**: `authorize`

- **Rate Limiter**: Limits the rate of report generation requests.
  - **File**: `taskflow\backend\src\middleware\rateLimiter.js`
  - **Key Function**: `reportLimiter`

- **Error Handler**: Handles errors and logs them.
  - **File**: `taskflow\backend\src\middleware\errorHandler.js`
  - **Key Function**: `errorHandler`

- **File Upload**: Configures multer for handling file uploads.
  - **File**: `taskflow\backend\src\middleware\upload.js`
  - **Key Function**: `upload`

### 6. **Models**
- **Project Model**: Manages project data.
  - **File**: `taskflow\backend\src\models\projectModel.js`
  - **Key Functions**:
    - `find`: Finds projects.
    - `create`: Creates a new project.
    - `update`: Updates an existing project.
    - `remove`: Deletes a project.

- **Task Model**: Manages task data.
  - **File**: `taskflow\backend\src\models\taskModel.js`
  - **Key Functions**:
    - `find`: Finds tasks.
    - `create`: Creates a new task.
    - `update`: Updates an existing task.
    - `remove`: Deletes a task.

- **User Model**: Manages user data.
  - **File**: `taskflow\backend\src\models\userModel.js`
  - **Key Functions**:
    - `find`: Finds users.
    - `create`: Creates a new user.
    - `updateRefreshToken`: Updates the refresh token.
    - `setResetToken`: Sets the password reset token.
    - `clearResetToken`: Clears the password reset token.
    - `updatePassword`: Updates the user's password.

- **Organization Model**: Manages organization data.
  - **File**: `taskflow\backend\src\models\orgModel.js`
  - **Key Functions**:
    - `findById`: Finds an organization by ID.
    - `create`: Creates a new organization.
    - `addMember`: Adds a member to an organization.
    - `getMembers`: Retrieves the members of an organization.

### 7. **Services**
- **Email Service**: Sends emails using SendGrid.
  - **File**: `taskflow\backend\src\services\emailService.js`
  - **Key Functions**:
    - `sendInvite`: Sends an invitation email.
    - `sendPasswordReset`: Sends a password reset email.

- **Notification Service**: Manages user notifications.
  - **File**: `taskflow\backend\src\services\notificationService.js`
  - **Key Functions**:
    - `create`: Creates a new notification.
    - `getForUser`: Retrieves notifications for a user.
    - `markRead`: Marks a notification as read.
    - `getPreferences`: Retrieves notification preferences.
    - `updatePreferences`: Updates notification preferences.

- **Report Service**: Generates HTML and PDF reports.
  - **File**: `taskflow\backend\src\services\reportService.js`
  - **Key Functions**:
    - `generateReportHtml`: Generates an HTML report.
    - `generatePdf`: Generates a PDF report.

- **Stripe Service**: Interacts with the Stripe API for billing.
  - **File**: `taskflow\backend\src\services\stripeService.js`
  - **Key Functions**:
    - `createCustomer`: Creates a new customer in Stripe.
    - `createCheckoutSession`: Creates a new checkout session.
    - `createBillingPortalSession`: Creates a new billing portal session.
    - `constructEvent`: Constructs a Stripe webhook event.

### 8. **Frontend**
- **React Application**: The frontend is built using React and React Router for routing.
  - **Main Entry Point**: `taskflow\frontend\src\main.jsx`
  - **Key Components**:
    - `App`: The main application component that sets up routing.
    - `Navbar`: A navigation bar component.
    - `Sidebar`: A sidebar component with navigation links.
    - `PageWrapper`: A layout component for consistent page structure.
    - `ProjectCard`: A card component for displaying projects.
    - `TaskCard`: A card component for displaying tasks.
    - `TaskDetail`: A component for displaying detailed information about a task.
    - `TaskForm`: A form component for creating or editing tasks.
    - `CommentList`: A component for displaying and managing comments.
    - `Badge`: A styled badge component.
    - `Button`: A reusable button component.
    - `Modal`: A modal dialog component.
    - `Spinner`: A loading spinner component.

- **API Client**: Manages HTTP requests to the backend API using Axios.
  - **File**: `taskflow\frontend\src\api\client.js`
  - **Key Functions**:
    - `client`: An Axios client instance with interceptors for authentication and error handling.

- **Authentication**: Manages user authentication state.
  - **File**: `taskflow\frontend\src\context\AuthContext.jsx`
  - **Key Components**:
    - `AuthProvider`: Provides authentication state and functions to its children.
    - `useAuth`: A custom hook for accessing the authentication context.

- **Pages**:
  - **LandingPage**: The landing page of the application.
  - **LoginPage**: The login page.
  - **RegisterPage**: The registration page.
  - **DashboardPage**: The dashboard page with statistics and recent tasks.
  - **ProjectsPage**: A page for listing and managing projects.
  - **TasksPage**: A page for listing and managing tasks.
  - **ProjectDetailPage**: A page for viewing detailed information about a project.
  - **TaskDetailPage**: A page for viewing detailed information about a task.
  - **SettingsPage**: A page for updating user settings.
  - **AdminPage**: An admin page for managing users and billing.

### 9. **Utils**
- **Logging**: Provides a simple logging utility.
  - **File**: `taskflow\frontend\src\utils\logger.js`
  - **Key Functions**:
    - `info`: Logs an informational message.
    - `warn`: Logs a warning message.
    - `error`: Logs an error message.

- **Token Utilities**: Manages JWT tokens.
  - **File**: `taskflow\backend\src\utils\tokenUtils.js`
  - **Key Functions**:
    - `signAccess`: Signs an access token.
    - `signRefresh`: Signs a refresh token.
    - `verifyAccess`: Verifies an access token.

- **Validators**: Provides utility functions for validating and sanitizing strings.
  - **File**: `taskflow\backend\src\utils\validators.js`
  - **Key Functions**:
    - `isEmail`: Validates if a string is a valid email address.
    - `isNonEmptyString`: Checks if a string is non-empty.
    - `sanitizeString`: Sanitizes a string by trimming and limiting its length.

- **Formatters**: Provides utility functions for formatting dates and labels.
  - **File**: `taskflow\frontend\src\utils\formatters.js`
  - **Key Functions**:
    - `formatDate`: Formats a date in a specific format.
    - `formatRelative`: Formats a date relative to the current time.
    - `priorityLabel`: Formats a priority label.
    - `statusLabel`: Formats a status label.

- **Analytics**: Tracks events and identifies users in an analytics system.
  - **File**: `taskflow\frontend\src\utils\analytics.js`
  - **Key Functions**:
    - `trackEvent`: Tracks an event with optional properties.
    - `identify`: Identifies a user with optional traits.

- **Auth Utilities**: Manages authentication sessions in local storage.
  - **File**: `taskflow\frontend\src\utils\authUtils.js`
  - **Key Functions**:
    - `saveSession`: Saves the authentication token, user data, and refresh token to local storage.
    - `clearSession`: Clears the authentication session data from local storage.
    - `getToken`: Retrieves the authentication token from local storage.
    - `getRefreshToken`: Retrieves the refresh token from local storage.
    - `getStoredUser`: Retrieves the user data from local storage.

### 10. **Development Configuration**
- **Vite Configuration**: Configures the Vite development server.
  - **File**: `taskflow\frontend\vite.config.js`
  - **Key Configuration**:
    - Runs on port 3000.
    - Proxies API and uploads requests to the backend server running on port 3001.

## Data and Control Flow

### 1. **User Interaction**
- **Frontend**: Users interact with the React application through various pages and components.
- **API Requests**: The frontend makes API requests to the backend using the Axios client.
- **Authentication**: User authentication is managed using JWT tokens. The `AuthProvider` and `useAuth` hook handle authentication state.

### 2. **Backend Processing**
- **Request Handling**: The Express server routes incoming HTTP requests to the appropriate controllers.
- **Controllers**: Controllers handle business logic and interact with models to perform database operations.
- **Models**: Models provide functions for interacting with the database, including CRUD operations.
- **Middleware**: Middleware functions handle cross-cutting concerns such as authentication, authorization, rate limiting, and error handling.

### 3. **Database Operations**
- **Database Connection**: The `db.js` file sets up a PostgreSQL connection pool and provides a query function.
- **Data Access**: Controllers use models to perform database operations, such as creating, reading, updating, and deleting records.

### 4. **External Services**
- **Email Service**: The `emailService.js` file uses SendGrid to send invitation and password reset emails.
- **Stripe Service**: The `stripeService.js` file interacts with the Stripe API for customer management, checkout sessions, and billing portal sessions.
- **Analytics**: The `analytics.js` file tracks events and identifies users in Mixpanel and Google Analytics.

### 5. **Error Handling**
- **Error Middleware**: The `errorHandler.js` file logs errors and sends a JSON response with the error details and status code.

### 6. **File Operations**
- **File Upload**: The `upload.js` file configures multer for handling file uploads, and the `attachmentController.js` file manages file operations for task attachments.
- **Report Generation**: The `reportService.js` file generates HTML and PDF reports, using file system operations to create and delete temporary files.

### 7. **Security**
- **Authentication**: The `authenticate.js` and `authorize.js` files handle user authentication and authorization.
- **Rate Limiting**: The `rateLimiter.js` file limits the rate of report generation requests.
- **Token Management**: The `tokenUtils.js` file manages JWT tokens, and the `authUtils.js` file manages authentication sessions in local storage.

### 8. **Logging**
- **Logger**: The `logger.js` file provides a simple logging utility for logging informational, warning, and error messages.

### 9. **State Management**
- **React Hooks**: Custom hooks like `useProjects` and `useTasks` manage state and side effects for projects and tasks, respectively.
- **Context**: The `AuthContext` provides authentication state and functions to the application.

### 10. **Routing**
- **React Router**: The `App.jsx` file sets up routing for various pages, including public and private routes. Private routes require user authentication.

## Conclusion

The TaskFlow application is designed with a clear separation of concerns, following a layered architecture. The backend handles data access and business logic, while the frontend provides a user-friendly interface. Middleware and services handle cross-cutting concerns, ensuring a robust and maintainable codebase. The application is well-structured, making it easy to understand and extend.