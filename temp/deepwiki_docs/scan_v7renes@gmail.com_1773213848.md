# Overview

## What is TaskFlow?

TaskFlow is a project management application designed to help organizations and teams efficiently manage their tasks and projects. It provides a comprehensive set of features for task tracking, project management, user authentication, and reporting. The application is built using a modern tech stack, including Node.js, Express, PostgreSQL, and React.

## Main Components

### Backend

1. **Database Configuration (`taskflow/backend/config/db.js`)**:
   - Sets up a PostgreSQL database connection pool.
   - Provides a query function for executing SQL queries.
   - Uses environment variables for configuration, with fallbacks for local development.

2. **Server Setup (`taskflow/backend/server.js`)**:
   - Sets up and starts a Node.js server using an Express application.
   - Listens on a specified port, defaulting to 3001 if not defined in the environment variables.

3. **Express Application (`taskflow/backend/src/app.js`)**:
   - Configures middleware for JSON and text parsing.
   - Serves static files from an uploads directory.
   - Mounts various API routes for authentication, tasks, projects, users, attachments, reports, imports, notifications, and admin functionalities.
   - Includes a health check endpoint and an error handler middleware.

4. **Controllers**:
   - **Report Controller (`taskflow/backend/src/controllers/reportController.js`)**:
     - Handles the generation of PDF reports based on project data.
   - **Admin Controller (`taskflow/backend/src/controllers/adminController.js`)**:
     - Manages administrative tasks such as retrieving users, deleting users, and getting a billing overview.
   - **Import Controller (`taskflow/backend/src/controllers/importController.js`)**:
     - Handles importing tasks from XML and CSV formats.
   - **Notification Controller (`taskflow/backend/src/controllers/notificationController.js`)**:
     - Manages notifications, including listing, marking as read, and managing preferences.
   - **Attachment Controller (`taskflow/backend/src/controllers/attachmentController.js`)**:
     - Manages task attachments, including listing, uploading, downloading, and removing.
   - **Project Controller (`taskflow/backend/src/controllers/projectController.js`)**:
     - Manages projects, including listing, retrieving, creating, updating, and deleting.
   - **User Controller (`taskflow/backend/src/controllers/userController.js`)**:
     - Manages user profiles, including retrieving and updating.
   - **Auth Controller (`taskflow/backend/src/controllers/authController.js`)**:
     - Handles user registration, login, token refresh, password reset, and logout.

5. **Middlewares**:
   - **Authentication Middleware (`taskflow/backend/src/middleware/authenticate.js`)**:
     - Verifies JWT tokens in the authorization header.
   - **Rate Limiter Middleware (`taskflow/backend/src/middleware/rateLimiter.js`)**:
     - Limits the rate of report generation requests to 10 per minute.
   - **Error Handler Middleware (`taskflow/backend/src/middleware/errorHandler.js`)**:
     - Logs errors and sends JSON responses with error details.
   - **Authorization Middleware (`taskflow/backend/src/middleware/authorize.js`)**:
     - Checks user roles and permissions.
   - **File Upload Middleware (`taskflow/backend/src/middleware/upload.js`)**:
     - Configures multer for handling file uploads.

6. **Models**:
   - **Project Model (`taskflow/backend/src/models/projectModel.js`)**:
     - Provides database operations for the 'projects' table.
   - **Organization Model (`taskflow/backend/src/models/orgModel.js`)**:
     - Manages organization and member data.
   - **Task Model (`taskflow/backend/src/models/taskModel.js`)**:
     - Provides database operations for the 'tasks' table.
   - **User Model (`taskflow/backend/src/models/userModel.js`)**:
     - Manages user data, including authentication and password management.

7. **Services**:
   - **Email Service (`taskflow/backend/src/services/emailService.js`)**:
     - Sends invitation and password reset emails using SendGrid.
   - **Notification Service (`taskflow/backend/src/services/notificationService.js`)**:
     - Manages user notifications and preferences.
   - **Report Service (`taskflow/backend/src/services/reportService.js`)**:
     - Generates HTML and PDF reports from task data.
   - **Stripe Service (`taskflow/backend/src/services/stripeService.js`)**:
     - Interacts with the Stripe API for customer management and billing.

8. **Utils**:
   - **Logger (`taskflow/backend/src/utils/logger.js`)**:
     - Provides a simple logging utility for info, warn, and error messages.
   - **Token Utils (`taskflow/backend/src/utils/tokenUtils.js`)**:
     - Contains functions for generating and verifying JWT tokens.
   - **Merge Objects (`taskflow/backend/src/utils/mergeObjects.js`)**:
     - Provides functions for deep merging of objects.
   - **Validators (`taskflow/backend/src/utils/validators.js`)**:
     - Contains functions for validating and sanitizing strings.

### Frontend

1. **Main Application (`taskflow/frontend/src/App.jsx`)**:
   - Sets up routing for various pages, including public and private routes.
   - Private routes require user authentication, redirecting unauthenticated users to the login page.

2. **API Client (`taskflow/frontend/src/api/client.js`)**:
   - Sets up an Axios client for making HTTP requests to the backend API.
   - Includes interceptors for adding authentication tokens and handling unauthorized responses.

3. **Components**:
   - **User Table (`taskflow/frontend/src/components/Admin/UserTable.jsx`)**:
     - Displays a table of users fetched from the API.
   - **Navbar (`taskflow/frontend/src/components/Layout/Navbar.jsx`)**:
     - Displays a navigation bar with links to the dashboard and settings, and a logout button.
   - **Page Wrapper (`taskflow/frontend/src/components/Layout/PageWrapper.jsx`)**:
     - Provides a consistent layout for pages, including a sidebar and navbar.
   - **Project Card (`taskflow/frontend/src/components/Projects/ProjectCard.jsx`)**:
     - Displays a card for a project with its name, description, and archived status.
   - **Project Settings (`taskflow/frontend/src/components/Projects/ProjectSettings.jsx`)**:
     - Allows users to update project settings.
   - **Task Card (`taskflow/frontend/src/components/Tasks/TaskCard.jsx`)**:
     - Displays a card for a task with its title, status, priority, due date, and assignee.
   - **Comment List (`taskflow/frontend/src/components/Tasks/CommentList.jsx`)**:
     - Displays a list of comments for a task and allows users to add new comments.
   - **Task Detail (`taskflow/frontend/src/components/Tasks/TaskDetail.jsx`)**:
     - Displays detailed information about a specific task.
   - **Task Form (`taskflow/frontend/src/components/Tasks/TaskForm.jsx`)**:
     - Provides a form for creating or editing a task.
   - **UI Components**:
     - **Badge (`taskflow/frontend/src/components/UI/Badge.jsx`)**:
     - **Button (`taskflow/frontend/src/components/UI/Button.jsx`)**:
     - **Modal (`taskflow/frontend/src/components/UI/Modal.jsx`)**:
     - **Spinner (`taskflow/frontend/src/components/UI/Spinner.jsx`)**:

4. **Hooks**:
   - **useAuth (`taskflow/frontend/src/hooks/useAuth.js`)**:
     - Manages authentication state.
   - **useProjects (`taskflow/frontend/src/hooks/useProjects.js`)**:
     - Manages the state and lifecycle of projects data.
   - **useTasks (`taskflow/frontend/src/hooks/useTasks.js`)**:
     - Manages the state and lifecycle of tasks data.

5. **Context**:
   - **AuthContext (`taskflow/frontend/src/context/AuthContext.jsx`)**:
     - Provides authentication state and functions to its children.

6. **Pages**:
   - **Admin Page (`taskflow/frontend/src/pages/AdminPage.jsx`)**:
     - Displays a table of users.
   - **Dashboard Page (`taskflow/frontend/src/pages/DashboardPage.jsx`)**:
     - Displays a dashboard with statistics about open tasks, overdue tasks, and projects.
   - **Login Page (`taskflow/frontend/src/pages/LoginPage.jsx`)**:
     - Handles user login.
   - **Landing Page (`taskflow/frontend/src/pages/LandingPage.jsx`)**:
     - Displays the landing page with navigation to login and registration pages.
   - **Not Found Page (`taskflow/frontend/src/pages/NotFoundPage.jsx`)**:
     - Displays a 404 error page.
   - **Project Detail Page (`taskflow/frontend/src/pages/ProjectDetailPage.jsx`)**:
     - Displays detailed information about a project.
   - **Task Detail Page (`taskflow/frontend/src/pages/TaskDetailPage.jsx`)**:
     - Displays detailed information about a task.
   - **Register Page (`taskflow/frontend/src/pages/RegisterPage.jsx`)**:
     - Handles user registration.
   - **Settings Page (`taskflow/frontend/src/pages/SettingsPage.jsx`)**:
     - Allows users to update their profile.
   - **Projects Page (`taskflow/frontend/src/pages/ProjectsPage.jsx`)**:
     - Displays a list of projects and allows creating new projects.
   - **Tasks Page (`taskflow/frontend/src/pages/TasksPage.jsx`)**:
     - Displays a list of tasks and allows creating new tasks.

7. **Utils**:
   - **Analytics (`taskflow/frontend/src/utils/analytics.js`)**:
     - Tracks events and identifies users in an analytics system using Mixpanel and Google Analytics.
   - **Auth Utils (`taskflow/frontend/src/utils/authUtils.js`)**:
     - Manages authentication sessions in local storage.
   - **Formatters (`taskflow/frontend/src/utils/formatters.js`)**:
     - Provides functions for formatting dates, priorities, and statuses.

8. **Configuration**:
   - **Vite Configuration (`taskflow/frontend/vite.config.js`)**:
     - Configures the Vite development server to run on port 3000 and proxy API and uploads requests to the backend server.

## Typical Usage Scenario

1. **User Registration and Login**:
   - A new user visits the landing page and clicks on the "Register" link.
   - The user fills out the registration form with their full name, email, and password.
   - Upon successful registration, the user is redirected to the login page.
   - The user logs in using their email and password, and the application verifies the credentials with the backend.

2. **Project Management**:
   - Once logged in, the user is redirected to the dashboard page.
   - The dashboard displays statistics about open tasks, overdue tasks, and projects.
   - The user can navigate to the projects page to view a list of projects.
   - The user can create a new project by clicking the "Create Project" button, which opens a modal form.
   - After creating a project, the user can navigate to the project detail page to view and manage tasks.

3. **Task Management**:
   - On the project detail page, the user can see a list of tasks and add new tasks by clicking the "Create Task" button.
   - The user can update task details, add comments, and mark tasks as completed.
   - The user can also view detailed information about a specific task by clicking on the task card.

4. **Admin Functions**:
   - Admin users can navigate to the admin page to manage users and view billing overviews.
   - The admin page displays a table of users, and the admin can delete users or manage their roles.

5. **Reporting**:
   - Users can generate PDF reports of projects by navigating to the report page.
   - The report generation is rate-limited to prevent abuse.

## Where to Look Next

- **Backend**:
  - **Database Configuration**: `taskflow/backend/config/db.js`
  - **Server Setup**: `taskflow/backend/server.js`
  - **Express Application**: `taskflow/backend/src/app.js`
  - **Controllers**: `taskflow/backend/src/controllers/*.js`
  - **Middlewares**: `taskflow/backend/src/middleware/*.js`
  - **Models**: `taskflow/backend/src/models/*.js`
  - **Services**: `taskflow/backend/src/services/*.js`
  - **Utils**: `taskflow/backend/src/utils/*.js`

- **Frontend**:
  - **Main Application**: `taskflow/frontend/src/App.jsx`
  - **API Client**: `taskflow/frontend/src/api/client.js`
  - **Components**: `taskflow/frontend/src/components/*.jsx`
  - **Hooks**: `taskflow/frontend/src/hooks/*.js`
  - **Context**: `taskflow/frontend/src/context/*.jsx`
  - **Pages**: `taskflow/frontend/src/pages/*.jsx`
  - **Utils**: `taskflow/frontend/src/utils/*.js`
  - **Configuration**: `taskflow/frontend/vite.config.js`

For more detailed information on specific components and functionalities, refer to the corresponding sections in the documentation.

---

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

---

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

---

# API Reference

This section provides detailed documentation for the RESTful API endpoints, including request and response formats, authentication requirements, and error handling.

## Authentication

### Middleware
- **`authenticate`**: This middleware function checks the authorization header and verifies the JWT token. It attaches user information to the request object if the token is valid. If the token is invalid or missing, it returns a 401 Unauthorized response.
  - **File**: `taskflow/backend/src/middleware/authenticate.js`
  - **Tags**: `auth`, `security`, `network`

- **`authorize`**: This middleware function checks if the user is authenticated and has the required role to proceed. It returns a 401 status if the user is not authenticated, and a 403 status if the user does not have sufficient permissions.
  - **File**: `taskflow/backend/src/middleware/authorize.js`
  - **Tags**: `auth`, `security`

- **`rateLimiter`**: This middleware limits the rate of report generation requests to 10 per minute.
  - **File**: `taskflow/backend/src/middleware/rateLimiter.js`
  - **Tags**: `network`, `security`

### Error Handling
- **`errorHandler`**: This middleware function handles errors by logging them and sending a JSON response with the error message, stack trace, and status code.
  - **File**: `taskflow/backend/src/middleware/errorHandler.js`
  - **Tags**: `logging`, `network`, `security`

## Endpoints

### Authentication
- **`POST /api/register`**: Handles user registration, including validation, password hashing, and creation of user and organization records.
  - **File**: `taskflow/backend/src/controllers/authController.js`
  - **Tags**: `auth`, `db`, `crypto`, `network`, `logging`

- **`POST /api/login`**: Handles user login, including credential validation and token generation.
  - **File**: `taskflow/backend/src/controllers/authController.js`
  - **Tags**: `auth`, `db`, `network`

- **`POST /api/refresh`**: Handles token refresh, generating a new access token from a valid refresh token.
  - **File**: `taskflow/backend/src/controllers/authController.js`
  - **Tags**: `auth`, `db`, `network`

- **`POST /api/forgot-password`**: Handles password reset requests, sending a reset link to the user's email.
  - **File**: `taskflow/backend/src/controllers/authController.js`
  - **Tags**: `auth`, `db`, `network`

- **`POST /api/reset-password`**: Handles password reset, updating the user's password with a new one.
  - **File**: `taskflow/backend/src/controllers/authController.js`
  - **Tags**: `auth`, `db`, `network`

- **`POST /api/logout`**: Handles user logout, invalidating the refresh token.
  - **File**: `taskflow/backend/src/controllers/authController.js`
  - **Tags**: `auth`, `db`, `network`

### Projects
- **`GET /api/projects`**: Lists all projects for a specific organization, optionally including archived projects.
  - **File**: `taskflow/backend/src/controllers/projectController.js`
  - **Tags**: `auth`, `db`, `network`, `security`

- **`GET /api/projects/:projectId`**: Retrieves a single project by ID, with access checks to ensure the project belongs to the requesting organization.
  - **File**: `taskflow/backend/src/controllers/projectController.js`
  - **Tags**: `auth`, `db`, `network`, `security`

- **`POST /api/projects`**: Creates a new project for an organization, requiring a valid project name.
  - **File**: `taskflow/backend/src/controllers/projectController.js`
  - **Tags**: `auth`, `db`, `network`, `security`

- **`PUT /api/projects/:projectId`**: Updates an existing project, with checks to ensure the project belongs to the requesting organization.
  - **File**: `taskflow/backend/src/controllers/projectController.js`
  - **Tags**: `auth`, `db`, `network`, `security`

- **`DELETE /api/projects/:projectId`**: Deletes a project, with checks to ensure the project belongs to the requesting organization.
  - **File**: `taskflow/backend/src/controllers/projectController.js`
  - **Tags**: `auth`, `db`, `network`, `security`

### Tasks
- **`GET /api/tasks`**: Lists tasks for a specific project or across an organization.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

- **`GET /api/tasks/:taskId`**: Retrieves a single task by its ID.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

- **`POST /api/tasks`**: Creates a new task within a project.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

- **`PUT /api/tasks/:taskId`**: Updates an existing task.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

- **`DELETE /api/tasks/:taskId`**: Deletes a task.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

- **`GET /api/tasks/:taskId/comments`**: Retrieves comments for a specific task.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

- **`POST /api/tasks/:taskId/comments`**: Adds a comment to a specific task.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

### Attachments
- **`GET /api/tasks/:taskId/attachments`**: Lists all attachments for a given task ID.
  - **File**: `taskflow/backend/src/controllers/attachmentController.js`
  - **Tags**: `auth`, `db`, `file_io`, `network`

- **`POST /api/tasks/:taskId/attachments`**: Uploads a file and stores its metadata in the database.
  - **File**: `taskflow/backend/src/controllers/attachmentController.js`
  - **Tags**: `auth`, `db`, `file_io`, `network`

- **`GET /api/tasks/:taskId/attachments/:attachmentId`**: Downloads a file based on the attachment ID.
  - **File**: `taskflow/backend/src/controllers/attachmentController.js`
  - **Tags**: `auth`, `db`, `file_io`, `network`

- **`DELETE /api/tasks/:taskId/attachments/:attachmentId`**: Deletes an attachment and its associated file from the filesystem.
  - **File**: `taskflow/backend/src/controllers/attachmentController.js`
  - **Tags**: `auth`, `db`, `file_io`, `network`

### Reports
- **`GET /api/reports/:projectId/pdf`**: Generates a PDF for a project with the specified project ID. Requires authentication and is rate-limited.
  - **File**: `taskflow/backend/src/controllers/reportController.js`
  - **Tags**: `auth`, `db`, `network`, `security`

### Admin
- **`GET /admin/users`**: Fetches all users, requires authentication.
  - **File**: `taskflow/backend/src/controllers/adminController.js`
  - **Tags**: `auth`, `db`, `network`

- **`DELETE /admin/users/:id`**: Deletes a user by ID, requires authentication.
  - **File**: `taskflow/backend/src/controllers/adminController.js`
  - **Tags**: `auth`, `db`, `network`

- **`GET /admin/billing`**: Fetches a billing overview, requires authentication.
  - **File**: `taskflow/backend/src/controllers/adminController.js`
  - **Tags**: `auth`, `db`, `network`

### Notifications
- **`GET /notifications`**: Lists all notifications for the authenticated user.
  - **File**: `taskflow/backend/src/controllers/notificationController.js`
  - **Tags**: `auth`, `db`, `network`

- **`PUT /notifications/:id/read`**: Marks a specific notification as read for the authenticated user.
  - **File**: `taskflow/backend/src/controllers/notificationController.js`
  - **Tags**: `auth`, `db`, `network`

- **`GET /notifications/preferences`**: Retrieves the notification preferences for the authenticated user.
  - **File**: `taskflow/backend/src/controllers/notificationController.js`
  - **Tags**: `auth`, `db`, `network`

- **`POST /notifications/preferences`**: Updates the notification preferences for the authenticated user.
  - **File**: `taskflow/backend/src/controllers/notificationController.js`
  - **Tags**: `auth`, `db`, `network`

### User Profile
- **`GET /profile`**: Retrieves the user's profile information.
  - **File**: `taskflow/backend/src/controllers/userController.js`
  - **Tags**: `auth`, `db`, `network`

- **`PUT /profile`**: Updates the user's profile information.
  - **File**: `taskflow/backend/src/controllers/userController.js`
  - **Tags**: `auth`, `db`, `network`

### Import
- **`POST /api/projects/:projectId/import/xml`**: Imports tasks from XML data. It parses the XML, checks the project existence and permissions, and creates tasks in the database.
  - **File**: `taskflow/backend/src/controllers/importController.js`
  - **Tags**: `auth`, `db`, `network`, `file_io`

- **`POST /api/projects/:projectId/import/csv`**: Imports tasks from CSV data. It parses the CSV, checks the project existence and permissions, and creates tasks in the database.
  - **File**: `taskflow/backend/src/controllers/importController.js`
  - **Tags**: `auth`, `db`, `network`, `file_io`

### Health Check
- **`GET /api/v1/health`**: Endpoint to check the health of the application, returning a JSON object with a status and timestamp.
  - **File**: `taskflow/backend/src/app.js`
  - **Tags**: `network`, `auth`, `db`, `file_io`, `other`

## Models

### Project Model
- **`projectModel`**: Provides database operations for the 'projects' table, such as finding, creating, updating, and deleting project records.
  - **File**: `taskflow/backend/src/models/projectModel.js`
  - **Tags**: `db`

### Task Model
- **`taskModel`**: Provides database operations for the 'tasks' table, including finding tasks by ID or project, creating new tasks, updating existing tasks, and removing tasks.
  - **File**: `taskflow/backend/src/models/taskModel.js`
  - **Tags**: `db`

### User Model
- **`userModel`**: Provides database operations for the 'users' table, including finding users by ID or email, creating new users, updating refresh tokens, setting and clearing reset tokens, and updating passwords.
  - **File**: `taskflow/backend/src/models/userModel.js`
  - **Tags**: `db`

### Organization Model
- **`orgModel`**: Provides database operations for the 'orgs' and 'org_members' tables, including finding an organization by ID, creating a new organization, adding a member to an organization, and retrieving the members of an organization.
  - **File**: `taskflow/backend/src/models/orgModel.js`
  - **Tags**: `db`

## Services

### Email Service
- **`sendInvite`**: Sends an invitation email to a user.
  - **File**: `taskflow/backend/src/services/emailService.js`
  - **Tags**: `network`, `email`

- **`sendPasswordReset`**: Sends a password reset email to a user.
  - **File**: `taskflow/backend/src/services/emailService.js`
  - **Tags**: `network`, `email`

### Notification Service
- **`create`**: Creates a new notification for a user and returns the created notification.
  - **File**: `taskflow/backend/src/services/notificationService.js`
  - **Tags**: `db`, `auth`

- **`getForUser`**: Retrieves a list of notifications for a specific user, with an optional limit.
  - **File**: `taskflow/backend/src/services/notificationService.js`
  - **Tags**: `db`, `auth`

- **`markRead`**: Marks a specific notification as read for a user.
  - **File**: `taskflow/backend/src/services/notificationService.js`
  - **Tags**: `db`, `auth`

- **`getPreferences`**: Retrieves the notification preferences for a user, merging with default preferences if necessary.
  - **File**: `taskflow/backend/src/services/notificationService.js`
  - **Tags**: `db`, `auth`

- **`updatePreferences`**: Updates the notification preferences for a user and returns the updated preferences.
  - **File**: `taskflow/backend/src/services/notificationService.js`
  - **Tags**: `db`, `auth`

### Report Service
- **`generateReportHtml`**: Generates an HTML string for a report based on task data.
  - **File**: `taskflow/backend/src/services/reportService.js`
  - **Tags**: `file_io`, `process`, `other`

- **`generatePdf`**: Generates a PDF report from an HTML string and returns it as a buffer.
  - **File**: `taskflow/backend/src/services/reportService.js`
  - **Tags**: `file_io`, `process`, `other`

### Stripe Service
- **`createCustomer`**: Creates a new customer in Stripe with the provided email and name.
  - **File**: `taskflow/backend/src/services/stripeService.js`
  - **Tags**: `network`, `process`, `security`, `other`

- **`createCheckoutSession`**: Creates a new checkout session for a subscription, linking it to a customer and specifying success and cancel URLs.
  - **File**: `taskflow/backend/src/services/stripeService.js`
  - **Tags**: `network`, `process`, `security`, `other`

- **`createBillingPortalSession`**: Creates a new billing portal session for a customer, specifying a return URL.
  - **File**: `taskflow/backend/src/services/stripeService.js`
  - **Tags**: `network`, `process`, `security`, `other`

- **`constructEvent`**: Constructs a Stripe webhook event from the provided payload, signature, and secret.
  - **File**: `taskflow/backend/src/services/stripeService.js`
  - **Tags**: `network`, `process`, `security`, `other`

## Utilities

### Token Utils
- **`tokenUtils`**: Provides functions for signing and verifying JWT access and refresh tokens.
  - **File**: `taskflow/backend/src/utils/tokenUtils.js`
  - **Tags**: `auth`, `crypto`

### Logger
- **`info`**: Logs an informational message with optional metadata.
  - **File**: `taskflow/backend/src/utils/logger.js`
  - **Tags**: `logging`

- **`warn`**: Logs a warning message with optional metadata.
  - **File**: `taskflow/backend/src/utils/logger.js`
  - **Tags**: `logging`

- **`error`**: Logs an error message with optional metadata.
  - **File**: `taskflow/backend/src/utils/logger.js`
  - **Tags**: `logging`

### Merge Objects
- **`mergeDeep`**: Performs a deep merge of two objects, preserving nested objects.
  - **File**: `taskflow/backend/src/utils/mergeObjects.js`
  - **Tags**: `other`

- **`mergeObjects`**: Merges multiple objects into a single object, using `mergeDeep` to handle deep merging.
  - **File**: `taskflow/backend/src/utils/mergeObjects.js`
  - **Tags**: `other`

### Validators
- **`isEmail`**: Validates if a string is a valid email address.
  - **File**: `taskflow/backend/src/utils/validators.js`
  - **Tags**: `other`

- **`isNonEmptyString`**: Checks if a string is non-empty and meets a minimum length requirement.
  - **File**: `taskflow/backend/src/utils/validators.js`
  - **Tags**: `other`

- **`sanitizeString`**: Sanitizes a string by trimming and limiting its length.
  - **File**: `taskflow/backend/src/utils/validators.js`
  - **Tags**: `other`

### Formatters
- **`formatDate`**: Formats a given date object or string into a short date format (e.g., 'Jan 1, 2023').
  - **File**: `taskflow/frontend/src/utils/formatters.js`
  - **Tags**: `other`

- **`formatRelative`**: Formats a given date object or string into a relative time format (e.g., 'Just now', '10m ago', '2h ago').
  - **File**: `taskflow/frontend/src/utils/formatters.js`
  - **Tags**: `other`

- **`priorityLabel`**: Capitalizes the first letter of a given priority string, defaulting to 'Medium' if no value is provided.
  - **File**: `taskflow/frontend/src/utils/formatters.js`
  - **Tags**: `other`

- **`statusLabel`**: Capitalizes the first letter of each word in a given status string, replacing underscores with spaces, defaulting to 'Open' if no value is provided.
  - **File**: `taskflow/frontend/src/utils/formatters.js`
  - **Tags**: `other`

### Auth Utils
- **`saveSession`**: Saves the authentication token, user data, and refresh token to local storage.
  - **File**: `taskflow/frontend/src/utils/authUtils.js`
  - **Tags**: `auth`, `storage`

- **`clearSession`**: Clears the authentication session data from local storage.
  - **File**: `taskflow/frontend/src/utils/authUtils.js`
  - **Tags**: `auth`, `storage`

- **`getToken`**: Retrieves the authentication token from local storage.
  - **File**: `taskflow/frontend/src/utils/authUtils.js`
  - **Tags**: `auth`, `storage`

- **`getRefreshToken`**: Retrieves the refresh token from local storage.
  - **File**: `taskflow/frontend/src/utils/authUtils.js`
  - **Tags**: `auth`, `storage`

- **`getStoredUser`**: Retrieves the user data from local storage, parsing it from JSON.
  - **File**: `taskflow/frontend/src/utils/authUtils.js`
  - **Tags**: `auth`, `storage`

### Analytics
- **`trackEvent`**: Tracks an event with optional properties using Mixpanel and Google Analytics.
  - **File**: `taskflow/frontend/src/utils/analytics.js`
  - **Tags**: `network`, `logging`

- **`identify`**: Identifies a user with optional traits using Mixpanel and Google Analytics

---

# Data Management

This section explains the data models and database interactions in the TaskFlow application, including how projects, tasks, users, and other entities are managed and queried.

## Database Configuration

### File: `taskflow/backend/config/db.js`

The database configuration is handled in `taskflow/backend/config/db.js`. This file sets up a PostgreSQL database connection pool using the `pg` library. It configures the pool with environment variables or fallback values for local development. The file exports two main entities:

- **`pool`**: A PostgreSQL connection pool instance that can be used to execute queries.
- **`query`**: A function that takes SQL text and parameters, and executes the query using the connection pool.

```javascript
// taskflow/backend/config/db.js
const { Pool } = require('pg');

const pool = new Pool({
  user: process.env.DB_USER || 'defaultUser',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'taskflow',
  password: process.env.DB_PASSWORD || 'defaultPassword',
  port: process.env.DB_PORT || 5432,
});

const query = (text, params) => pool.query(text, params);

module.exports = { pool, query };
```

## Data Models

### Project Model

### File: `taskflow/backend/src/models/projectModel.js`

The `projectModel.js` file defines a set of asynchronous functions for interacting with the `projects` table in the database. These functions include:

- **`find`**: Finds projects based on specified criteria.
- **`create`**: Creates a new project.
- **`update`**: Updates an existing project.
- **`remove`**: Deletes a project.

```javascript
// taskflow/backend/src/models/projectModel.js
const { query } = require('../config/db');

const find = async (criteria) => {
  const result = await query('SELECT * FROM projects WHERE $1', [criteria]);
  return result.rows;
};

const create = async (project) => {
  const result = await query('INSERT INTO projects (name, description, organization_id) VALUES ($1, $2, $3) RETURNING *', [project.name, project.description, project.organization_id]);
  return result.rows[0];
};

const update = async (id, updates) => {
  const result = await query('UPDATE projects SET name = $1, description = $2 WHERE id = $3 RETURNING *', [updates.name, updates.description, id]);
  return result.rows[0];
};

const remove = async (id) => {
  await query('DELETE FROM projects WHERE id = $1', [id]);
};

module.exports = { find, create, update, remove };
```

### Task Model

### File: `taskflow/backend/src/models/taskModel.js`

The `taskModel.js` file defines a set of asynchronous functions for interacting with the `tasks` table in the database. These functions include:

- **`find`**: Finds tasks based on specified criteria.
- **`create`**: Creates a new task.
- **`update`**: Updates an existing task.
- **`remove`**: Deletes a task.

```javascript
// taskflow/backend/src/models/taskModel.js
const { query } = require('../config/db');

const find = async (criteria) => {
  const result = await query('SELECT * FROM tasks WHERE $1', [criteria]);
  return result.rows;
};

const create = async (task) => {
  const result = await query('INSERT INTO tasks (title, description, project_id, status, priority, due_date) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *', [task.title, task.description, task.project_id, task.status, task.priority, task.due_date]);
  return result.rows[0];
};

const update = async (id, updates) => {
  const result = await query('UPDATE tasks SET title = $1, description = $2, status = $3, priority = $4, due_date = $5 WHERE id = $6 RETURNING *', [updates.title, updates.description, updates.status, updates.priority, updates.due_date, id]);
  return result.rows[0];
};

const remove = async (id) => {
  await query('DELETE FROM tasks WHERE id = $1', [id]);
};

module.exports = { find, create, update, remove };
```

### User Model

### File: `taskflow/backend/src/models/userModel.js`

The `userModel.js` file defines a set of asynchronous functions for interacting with the `users` table in the database. These functions include:

- **`find`**: Finds users based on specified criteria.
- **`create`**: Creates a new user.
- **`update`**: Updates an existing user.
- **`remove`**: Deletes a user.

```javascript
// taskflow/backend/src/models/userModel.js
const { query } = require('../config/db');

const find = async (criteria) => {
  const result = await query('SELECT * FROM users WHERE $1', [criteria]);
  return result.rows;
};

const create = async (user) => {
  const result = await query('INSERT INTO users (email, password, name) VALUES ($1, $2, $3) RETURNING *', [user.email, user.password, user.name]);
  return result.rows[0];
};

const update = async (id, updates) => {
  const result = await query('UPDATE users SET email = $1, name = $2 WHERE id = $3 RETURNING *', [updates.email, updates.name, id]);
  return result.rows[0];
};

const remove = async (id) => {
  await query('DELETE FROM users WHERE id = $1', [id]);
};

module.exports = { find, create, update, remove };
```

### Organization Model

### File: `taskflow/backend/src/models/orgModel.js`

The `orgModel.js` file defines a set of functions for interacting with the `orgs` and `org_members` tables in the database. These functions include:

- **`findById`**: Finds an organization by its ID.
- **`create`**: Creates a new organization.
- **`addMember`**: Adds a member to an organization.
- **`getMembers`**: Retrieves the members of an organization.

```javascript
// taskflow/backend/src/models/orgModel.js
const { query } = require('../config/db');

const findById = async (id) => {
  const result = await query('SELECT * FROM orgs WHERE id = $1', [id]);
  return result.rows[0];
};

const create = async (org) => {
  const result = await query('INSERT INTO orgs (name) VALUES ($1) RETURNING *', [org.name]);
  return result.rows[0];
};

const addMember = async (orgId, userId) => {
  await query('INSERT INTO org_members (org_id, user_id) VALUES ($1, $2)', [orgId, userId]);
};

const getMembers = async (orgId) => {
  const result = await query('SELECT users.* FROM users JOIN org_members ON users.id = org_members.user_id WHERE org_members.org_id = $1', [orgId]);
  return result.rows;
};

module.exports = { findById, create, addMember, getMembers };
```

## Data Management Controllers

### Project Controller

### File: `taskflow/backend/src/controllers/projectController.js`

The `projectController.js` file contains controller functions for managing projects. These functions interact with the `projectModel` to perform database operations and return appropriate HTTP responses. The functions include:

- **`list`**: Lists projects for a specific organization.
- **`getOne`**: Retrieves a single project by ID.
- **`create`**: Creates a new project.
- **`update`**: Updates an existing project.
- **`remove`**: Deletes a project.

```javascript
// taskflow/backend/src/controllers/projectController.js
const { find, create, update, remove } = require('../models/projectModel');

const list = async (req, res) => {
  const projects = await find({ organization_id: req.user.organization_id });
  res.json(projects);
};

const getOne = async (req, res) => {
  const project = await find({ id: req.params.projectId, organization_id: req.user.organization_id });
  if (!project) return res.status(404).json({ message: 'Project not found' });
  res.json(project);
};

const create = async (req, res) => {
  const project = await create({ name: req.body.name, description: req.body.description, organization_id: req.user.organization_id });
  res.status(201).json(project);
};

const update = async (req, res) => {
  const project = await find({ id: req.params.projectId, organization_id: req.user.organization_id });
  if (!project) return res.status(404).json({ message: 'Project not found' });
  const updatedProject = await update(req.params.projectId, req.body);
  res.json(updatedProject);
};

const remove = async (req, res) => {
  const project = await find({ id: req.params.projectId, organization_id: req.user.organization_id });
  if (!project) return res.status(404).json({ message: 'Project not found' });
  await remove(req.params.projectId);
  res.json({ message: 'Project deleted' });
};

module.exports = { list, getOne, create, update, remove };
```

### Task Controller

### File: `taskflow/backend/src/controllers/taskController.js`

The `taskController.js` file contains controller functions for managing tasks. These functions interact with the `taskModel` to perform database operations and return appropriate HTTP responses. The functions include:

- **`list`**: Lists tasks for a specific project or across an organization.
- **`getOne`**: Retrieves a single task by ID.
- **`create`**: Creates a new task.
- **`update`**: Updates an existing task.
- **`remove`**: Deletes a task.

```javascript
// taskflow/backend/src/controllers/taskController.js
const { find, create, update, remove } = require('../models/taskModel');

const list = async (req, res) => {
  const tasks = await find({ project_id: req.params.projectId });
  res.json(tasks);
};

const getOne = async (req, res) => {
  const task = await find({ id: req.params.taskId });
  if (!task) return res.status(404).json({ message: 'Task not found' });
  res.json(task);
};

const create = async (req, res) => {
  const task = await create({ title: req.body.title, description: req.body.description, project_id: req.params.projectId, status: req.body.status, priority: req.body.priority, due_date: req.body.due_date });
  res.status(201).json(task);
};

const update = async (req, res) => {
  const task = await find({ id: req.params.taskId });
  if (!task) return res.status(404).json({ message: 'Task not found' });
  const updatedTask = await update(req.params.taskId, req.body);
  res.json(updatedTask);
};

const remove = async (req, res) => {
  const task = await find({ id: req.params.taskId });
  if (!task) return res.status(404).json({ message: 'Task not found' });
  await remove(req.params.taskId);
  res.json({ message: 'Task deleted' });
};

module.exports = { list, getOne, create, update, remove };
```

### User Controller

### File: `taskflow/backend/src/controllers/userController.js`

The `userController.js` file contains controller functions for managing user profiles. These functions interact with the `userModel` to perform database operations and return appropriate HTTP responses. The functions include:

- **`getProfile`**: Retrieves a user's profile information.
- **`updateProfile`**: Updates a user's profile information.

```javascript
// taskflow/backend/src/controllers/userController.js
const { find, update } = require('../models/userModel');

const getProfile = async (req, res) => {
  const user = await find({ id: req.user.id });
  if (!user) return res.status(404).json({ message: 'User not found' });
  res.json(user);
};

const updateProfile = async (req, res) => {
  const user = await find({ id: req.user.id });
  if (!user) return res.status(404).json({ message: 'User not found' });
  const updatedUser = await update(req.user.id, req.body);
  res.json(updatedUser);
};

module.exports = { getProfile, updateProfile };
```

## Data Management Routes

### Project Routes

### File: `taskflow/backend/src/routes/projectRoutes.js`

The `projectRoutes.js` file sets up an Express router for project-related endpoints. All routes require authentication. The routes include:

- **`GET /`**: Lists all projects.
- **`GET /:projectId`**: Retrieves a single project by ID.
- **`POST /`**: Creates a new project.
- **`PUT /:projectId`**: Updates an existing project by ID.
- **`DELETE /:projectId`**: Deletes a project by ID.

```javascript
// taskflow/backend/src/routes/projectRoutes.js
const express = require('express');
const router = express.Router();
const { authenticate, authorize } = require('../middleware/authenticate');
const { list, getOne, create, update, remove } = require('../controllers/projectController');

router.use(authenticate);

router.get('/', list);
router.get('/:projectId', getOne);
router.post('/', create);
router.put('/:projectId', update);
router.delete('/:projectId', remove);

module.exports = router;
```

### Task Routes

### File: `taskflow/backend/src/routes/taskRoutes.js`

The `taskRoutes.js` file sets up an Express router for task-related endpoints. All routes require authentication. The routes include:

- **`GET /`**: Lists all tasks.
- **`GET /:taskId/comments`**: Retrieves comments for a specific task.
- **`POST /:taskId/comments`**: Adds a comment to a specific task.
- **`GET /:taskId`**: Retrieves a single task by ID.
- **`POST /`**: Creates a new task.
- **`PUT /:taskId`**: Updates an existing task by ID.
- **`DELETE /:taskId`**: Deletes a task by ID.

```javascript
// taskflow/backend/src/routes/taskRoutes.js
const express = require('express');
const router = express.Router();
const { authenticate, authorize } = require('../middleware/authenticate');
const { list, getComments, addComment, getOne, create, update, remove } = require('../controllers/taskController');

router.use(authenticate);

router.get('/', list);
router.get('/:taskId/comments', getComments);
router.post('/:taskId/comments', addComment);
router.get('/:taskId', getOne);
router.post('/', create);
router.put('/:taskId', update);
router.delete('/:taskId', remove);

module.exports = router;
```

### User Routes

### File: `taskflow/backend/src/routes/userRoutes.js`

The `userRoutes.js` file sets up an Express router for user-related endpoints. All routes require authentication. The routes include:

- **`GET /profile`**: Retrieves the user's profile information.
- **`PATCH /profile`**: Updates the user's profile information.

```javascript
// taskflow/backend/src/routes/userRoutes.js
const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/authenticate');
const { getProfile, updateProfile } = require('../controllers/userController');

router.use(authenticate);

router.get('/profile', getProfile);
router.patch('/profile', updateProfile);

module.exports = router;
```

## Data Management Services

### Notification Service

### File: `taskflow/backend/src/services/notificationService.js`

The `notificationService.js` file defines a service for managing user notifications and preferences. It provides functions to create notifications, retrieve notifications for a user, mark notifications as read, get user notification preferences, and update those preferences.

```javascript
// taskflow/backend/src/services/notificationService.js
const { query } = require('../config/db');

const create = async (userId, message) => {
  const result = await query('INSERT INTO notifications (user_id, message) VALUES ($1, $2) RETURNING *', [userId, message]);
  return result.rows[0];
};

const getForUser = async (userId, limit = 10) => {
  const result = await query('SELECT * FROM notifications WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2', [userId, limit]);
  return result.rows;
};

const markRead = async (userId, notificationId) => {
  await query('UPDATE notifications SET read = true WHERE user_id = $1 AND id = $2', [userId, notificationId]);
};

const getPreferences = async (userId) => {
  const result = await query('SELECT * FROM notification_preferences WHERE user_id = $1', [userId]);
  return result.rows[0] || { email: true, sms: false };
};

const updatePreferences = async (userId, preferences) => {
  await query('INSERT INTO notification_preferences (user_id, email, sms) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO UPDATE SET email = $2, sms = $3', [userId, preferences.email, preferences.sms]);
  return { email: preferences.email, sms: preferences.sms };
};

module.exports = { create, getForUser, markRead, getPreferences, updatePreferences };
```

### Report Service

### File: `taskflow/backend/src/services/reportService.js`

The `reportService.js` file contains functions for generating HTML and PDF reports from task data. It uses file system operations to create and delete temporary files and executes a command-line tool (wkhtmltopdf) to convert HTML to PDF.

```javascript
// taskflow/backend/src/services/reportService.js
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const generateReportHtml = async (tasks) => {
  const html = tasks.map(task => `<div>${task.title} - ${task.status}</div>`).join('');
  return html;
};

const generatePdf = async (html) => {
  const tempHtmlPath = path.join(__dirname, 'temp', 'report.html');
  const tempPdfPath = path.join(__dirname, 'temp', 'report.pdf');

  fs.writeFileSync(tempHtmlPath, html);

  await new Promise((resolve, reject) => {
    exec(`wkhtmltopdf ${tempHtmlPath} ${tempPdfPath}`, (err) => {
      if (err) return reject(err);
      resolve();
    });
  });

  const pdfBuffer = fs.readFileSync(tempPdfPath);
  fs.unlinkSync(tempHtmlPath);
  fs.unlinkSync(tempPdfPath);

  return pdfBuffer;
};

module.exports = { generateReportHtml, generatePdf };
```

## Data Management Middleware

### Authentication Middleware

### File: `taskflow/backend/src/middleware/authenticate.js`

The `authenticate.js` file defines a middleware function for authenticating HTTP requests by verifying a JWT token in the authorization header. It attaches user information to the request object

---

# Frontend

This section describes the frontend architecture of the TaskFlow application, including the React components, routing, state management, and API interactions.

## React Components

### Main Application Component
- **File**: `taskflow\frontend\src\App.jsx`
- **Description**: The main entry point of the application. It sets up routing using `react-router-dom` and defines public and private routes. Private routes require user authentication, and unauthenticated users are redirected to the login page.

### Layout Components
- **Navbar**
  - **File**: `taskflow\frontend\src\components\Layout\Navbar.jsx`
  - **Description**: A header component that displays navigation links to the dashboard and settings, and includes a logout button. It uses the `useAuth` hook to manage authentication state.
- **Sidebar**
  - **File**: `taskflow\frontend\src\components\Layout\Sidebar.jsx`
  - **Description**: A navigation sidebar that displays links to different sections of the application. It shows additional admin-specific links if the user has an admin role.
- **PageWrapper**
  - **File**: `taskflow\frontend\src\components\Layout\PageWrapper.jsx`
  - **Description**: A layout component that wraps the main content area, including a sidebar and a navbar. It accepts children and a title as props.

### Project Components
- **ProjectCard**
  - **File**: `taskflow\frontend\src\components\Projects\ProjectCard.jsx`
  - **Description**: A card component that displays a project's name, a truncated description, and an archived status. It is a clickable link that navigates to the project's detail page.
- **ProjectDetailPage**
  - **File**: `taskflow\frontend\src\pages\ProjectDetailPage.jsx`
  - **Description**: A page component that displays detailed information about a project, including tasks and project settings. It fetches project data from the API and handles loading and error states.
- **ProjectSettings**
  - **File**: `taskflow\frontend\src\components\Projects\ProjectSettings.jsx`
  - **Description**: A component that allows users to update a project's name, description, and archived status. It uses the `useProjects` hook to handle project updates and provides a form for user input.

### Task Components
- **TaskCard**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskCard.jsx`
  - **Description**: A card component that displays a task's title, status, priority, due date, and assignee. It includes a link to the task's detail page.
- **TaskDetailPage**
  - **File**: `taskflow\frontend\src\pages\TaskDetailPage.jsx`
  - **Description**: A page component that displays detailed information about a specific task, including its status, priority, due date, title, and description. It fetches the task data from the API and handles loading and error states.
- **TaskForm**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskForm.jsx`
  - **Description**: A form component used to create or edit a task. It includes form fields for the task's title, description, priority, status, and due date. The component handles form submission and provides a callback to the parent component upon successful submission.
- **CommentList**
  - **File**: `taskflow\frontend\src\components\Tasks\CommentList.jsx`
  - **Description**: A component that displays a list of comments for a given task and allows users to add new comments. It fetches comments from the API and updates the list when new comments are posted.

### UI Components
- **Button**
  - **File**: `taskflow\frontend\src\components\UI\Button.jsx`
  - **Description**: A reusable button component that accepts props for customizing the button's appearance and behavior, such as variant, size, and additional class names.
- **Badge**
  - **File**: `taskflow\frontend\src\components\UI\Badge.jsx`
  - **Description**: A component that displays a styled badge with different variants (default, success, warning, danger, info). It accepts children and a variant prop to customize its appearance.
- **Modal**
  - **File**: `taskflow\frontend\src\components\UI\Modal.jsx`
  - **Description**: A modal dialog component that displays a modal when the `open` prop is true. It can be closed by clicking outside the dialog or by clicking the close button.
- **Spinner**
  - **File**: `taskflow\frontend\src\components\UI\Spinner.jsx`
  - **Description**: A component that renders a spinning circle to indicate loading states. It accepts a `className` prop to allow for additional styling.

### Page Components
- **AdminPage**
  - **File**: `taskflow\frontend\src\pages\AdminPage.jsx`
  - **Description**: A page component that serves as the admin section of the application. It displays a header and a table of users using the `UserTable` component.
- **DashboardPage**
  - **File**: `taskflow\frontend\src\pages\DashboardPage.jsx`
  - **Description**: A page component that displays a dashboard with statistics about open tasks, overdue tasks, and projects. It also shows a list of recent tasks and provides a button to navigate to the task creation page.
- **LoginPage**
  - **File**: `taskflow\frontend\src\pages\LoginPage.jsx`
  - **Description**: A page component for the login page, which includes form fields for email and password, and handles the submission of login credentials to authenticate the user. Upon successful login, the user is redirected to a specified or default page.
- **LandingPage**
  - **File**: `taskflow\frontend\src\pages\LandingPage.jsx`
  - **Description**: A page component for the landing page of the TaskFlow application. It includes navigation links to login and register pages, a main section with a call to action, a features section, a pricing section, and testimonials from users.
- **NotFoundPage**
  - **File**: `taskflow\frontend\src\pages\NotFoundPage.jsx`
  - **Description**: A page component that displays a 404 error page with a message and a link to return to the home page.
- **RegisterPage**
  - **File**: `taskflow\frontend\src\pages\RegisterPage.jsx`
  - **Description**: A page component for the user registration page. It handles user input for full name, email, and password, and sends a registration request to an authentication service. Upon successful registration, it redirects the user to the dashboard.
- **SettingsPage**
  - **File**: `taskflow\frontend\src\pages\SettingsPage.jsx`
  - **Description**: A page component that allows a user to update their full name. It uses a custom hook for authentication and makes an API call to update the user's profile.
- **ProjectsPage**
  - **File**: `taskflow\frontend\src\pages\ProjectsPage.jsx`
  - **Description**: A page component that displays a list of projects and provides a modal for creating new projects. It uses the `useProjects` hook to fetch and manage project data.
- **TasksPage**
  - **File**: `taskflow\frontend\src\pages\TasksPage.jsx`
  - **Description**: A page component that displays a list of tasks and allows users to filter tasks by project and search term. It also includes a modal form for creating new tasks.

## Routing

- **Main Application Component**
  - **File**: `taskflow\frontend\src\App.jsx`
  - **Description**: The `App` component sets up routing using `react-router-dom`. It defines public and private routes, where private routes require user authentication. Unauthenticated users are redirected to the login page.

## State Management

- **useAuth Hook**
  - **File**: `taskflow\frontend\src\hooks\useAuth.js`
  - **Description**: A custom React hook that provides authentication state and functions to log in, register, and log out. It interacts with an authentication API and local storage.
- **useProjects Hook**
  - **File**: `taskflow\frontend\src\hooks\useProjects.js`
  - **Description**: A custom React hook that manages the state and lifecycle of projects data. It includes functions to fetch, create, update, and delete projects, interacting with an API through the `projectsApi` module.
- **useTasks Hook**
  - **File**: `taskflow\frontend\src\hooks\useTasks.js`
  - **Description**: A custom React hook that manages the state and lifecycle of tasks for a given project. It includes functions to fetch, create, update, and delete tasks, interacting with an API through the `tasksApi` module.

## API Interactions

- **Axios Client**
  - **File**: `taskflow\frontend\src\api\client.js`
  - **Description**: An Axios client configured with interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to the login page.
- **Admin API**
  - **File**: `taskflow\frontend\src\api\admin.js`
  - **Description**: Functions for making HTTP requests to the admin endpoints of the API, including fetching all users, deleting a user, and getting a billing overview.
- **Auth API**
  - **File**: `taskflow\frontend\src\api\auth.js`
  - **Description**: Functions for handling authentication operations such as login, registration, logout, and token refreshing. It uses the imported client to make HTTP POST requests to the corresponding API endpoints.
- **Projects API**
  - **File**: `taskflow\frontend\src\api\projects.js`
  - **Description**: Functions for interacting with the projects API, including listing, retrieving, creating, updating, and deleting projects. Each function makes an HTTP request using the imported client.
- **Tasks API**
  - **File**: `taskflow\frontend\src\api\tasks.js`
  - **Description**: Functions for interacting with the tasks API, including listing, retrieving, creating, updating, and deleting tasks. Each function makes an HTTP request using the imported client.

## Configuration

- **PostCSS Configuration**
  - **File**: `taskflow\frontend\postcss.config.js`
  - **Description**: Configures the PostCSS setup for the frontend project, integrating Tailwind CSS. It specifies the files to be processed and includes the default theme and plugins configuration.
- **Vite Configuration**
  - **File**: `taskflow\frontend\vite.config.js`
  - **Description**: Configures the Vite development server for the React application, setting up port 3000 and proxying API and uploads requests to a backend server running on port 3001.

## Utilities

- **Analytics**
  - **File**: `taskflow\frontend\src\utils\analytics.js`
  - **Description**: Utility functions for tracking events and identifying users in an analytics system, using Mixpanel and Google Analytics.
- **Auth Utilities**
  - **File**: `taskflow\frontend\src\utils\authUtils.js`
  - **Description**: Utility functions for managing authentication sessions in the frontend application. It provides methods to save, clear, and retrieve session data from the browser's local storage.
- **Formatters**
  - **File**: `taskflow\frontend\src\utils\formatters.js`
  - **Description**: Utility functions for formatting dates, priorities, and statuses. It includes functions to format dates in a specific format, format dates relative to the current time, and format priority and status labels.

This documentation provides a comprehensive overview of the frontend architecture, including the key components, routing, state management, API interactions, and utility functions. Each component and utility is mapped back to its respective file and function, ensuring clarity and ease of reference.

---