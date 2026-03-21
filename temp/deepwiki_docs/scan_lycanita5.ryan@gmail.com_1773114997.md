# Overview

## What is TaskFlow?

TaskFlow is a comprehensive project management tool designed to streamline the workflow of teams and organizations. It provides a robust set of features for managing projects, tasks, users, and notifications, all while ensuring secure and efficient operations. TaskFlow is built using a modern tech stack, including Node.js, Express, PostgreSQL, and React, and it is designed to be scalable, maintainable, and user-friendly.

## Main Components

### Backend

1. **Database Configuration (`taskflow\backend\config\db.js`)**:
   - Sets up a PostgreSQL database connection pool.
   - Provides a query function for executing SQL queries.
   - Uses environment variables for configuration, with fallbacks for local development.

2. **Server Setup (`taskflow\backend\server.js`)**:
   - Initializes and starts a Node.js server using an Express application.
   - Listens on a specified port (default 3001) and logs a message upon successful startup.

3. **Express Application (`taskflow\backend\src\app.js`)**:
   - Configures middleware for JSON and text parsing.
   - Serves static files from the uploads directory.
   - Mounts various API routes for authentication, tasks, projects, users, attachments, reports, imports, notifications, and admin functionalities.
   - Includes a health check endpoint and an error handler middleware.

4. **Controllers**:
   - **Report Controller (`taskflow\backend\src\controllers\reportController.js`)**:
     - Handles generating PDF reports for projects.
   - **Import Controller (`taskflow\backend\src\controllers\importController.js`)**:
     - Manages importing tasks from XML and CSV formats.
   - **Admin Controller (`taskflow\backend\src\controllers\adminController.js`)**:
     - Provides endpoints for administrative tasks like managing users and billing.
   - **Attachment Controller (`taskflow\backend\src\controllers\attachmentController.js`)**:
     - Manages task attachments, including listing, uploading, downloading, and removing.
   - **Notification Controller (`taskflow\backend\src\controllers\notificationController.js`)**:
     - Handles notifications, including listing, marking as read, and managing preferences.
   - **Project Controller (`taskflow\backend\src\controllers\projectController.js`)**:
     - Manages projects, including listing, retrieving, creating, updating, and deleting.
   - **User Controller (`taskflow\backend\src\controllers\userController.js`)**:
     - Manages user profiles, including retrieving and updating.
   - **Task Controller (`taskflow\backend\src\controllers\taskController.js`)**:
     - Manages tasks, including listing, retrieving, creating, updating, and deleting.
   - **Auth Controller (`taskflow\backend\src\controllers\authController.js`)**:
     - Handles user authentication, including registration, login, token refresh, password reset, and logout.

5. **Middleware**:
   - **Authorize (`taskflow\backend\src\middleware\authorize.js`)**:
     - Middleware for authorizing user roles.
   - **Authenticate (`taskflow\backend\src\middleware\authenticate.js`)**:
     - Middleware for authenticating HTTP requests using JWT tokens.
   - **Error Handler (`taskflow\backend\src\middleware\errorHandler.js`)**:
     - Middleware for handling errors, logging them, and sending JSON responses.
   - **Rate Limiter (`taskflow\backend\src\middleware\rateLimiter.js`)**:
     - Middleware for rate limiting report generation requests.
   - **Upload (`taskflow\backend\src\middleware\upload.js`)**:
     - Middleware for handling file uploads using Multer.

6. **Models**:
   - **Task Model (`taskflow\backend\src\models\taskModel.js`)**:
     - Provides functions for interacting with the 'tasks' table in the database.
   - **User Model (`taskflow\backend\src\models\userModel.js`)**:
     - Provides functions for interacting with the 'users' table in the database.
   - **Org Model (`taskflow\backend\src\models\orgModel.js`)**:
     - Provides functions for interacting with the 'orgs' and 'org_members' tables in the database.
   - **Project Model (`taskflow\backend\src\models\projectModel.js`)**:
     - Provides functions for interacting with the 'projects' table in the database.

7. **Services**:
   - **Email Service (`taskflow\backend\src\services\emailService.js`)**:
     - Provides functions for sending emails using SendGrid.
   - **Notification Service (`taskflow\backend\src\services\notificationService.js`)**:
     - Manages user notifications and preferences.
   - **Report Service (`taskflow\backend\src\services\reportService.js`)**:
     - Generates HTML and PDF reports for projects.
   - **Stripe Service (`taskflow\backend\src\services\stripeService.js`)**:
     - Interacts with the Stripe API for customer management, checkout sessions, and billing portal sessions.

8. **Utils**:
   - **Token Utils (`taskflow\backend\src\utils\tokenUtils.js`)**:
     - Provides functions for generating and verifying JWT access and refresh tokens.
   - **Logger (`taskflow\backend\src\utils\logger.js`)**:
     - Provides a simple logging utility for formatting log entries as JSON objects.
   - **Merge Objects (`taskflow\backend\src\utils\mergeObjects.js`)**:
     - Provides functions for merging objects, specifically designed to handle deep merging of nested objects.
   - **Validators (`taskflow\backend\src\utils\validators.js`)**:
     - Provides functions for validating and sanitizing strings, including email format and non-empty strings.

### Frontend

1. **Main Application (`taskflow\frontend\src\main.jsx`)**:
   - Sets up the React DOM, BrowserRouter for routing, and AuthProvider for authentication context.
   - Renders the main App component.

2. **App Component (`taskflow\frontend\src\App.jsx`)**:
   - Defines the main application component with routing for various pages, including public and private routes.
   - Private routes require user authentication, redirecting unauthenticated users to the login page.

3. **Pages**:
   - **Admin Page (`taskflow\frontend\src\pages\AdminPage.jsx`)**:
     - Displays a page for administrative tasks, including a table of users.
   - **Dashboard Page (`taskflow\frontend\src\pages\DashboardPage.jsx`)**:
     - Displays a dashboard with statistics about open tasks, overdue tasks, and projects.
   - **Landing Page (`taskflow\frontend\src\pages\LandingPage.jsx`)**:
     - Serves as the landing page for the TaskFlow application, including navigation links and sections for features, pricing, and testimonials.
   - **Login Page (`taskflow\frontend\src\pages\LoginPage.jsx`)**:
     - Handles user login with form fields for email and password.
   - **Not Found Page (`taskflow\frontend\src\pages\NotFoundPage.jsx`)**:
     - Displays a 404 error page with a message and a link to return to the home page.
   - **Projects Page (`taskflow\frontend\src\pages\ProjectsPage.jsx`)**:
     - Displays a list of projects and provides a modal for creating new projects.
   - **Project Detail Page (`taskflow\frontend\src\pages\ProjectDetailPage.jsx`)**:
     - Displays detailed information about a project and provides options to view tasks and manage project settings.
   - **Register Page (`taskflow\frontend\src\pages\RegisterPage.jsx`)**:
     - Handles user registration with form fields for full name, email, and password.
   - **Settings Page (`taskflow\frontend\src\pages\SettingsPage.jsx`)**:
     - Allows users to update their full name and other profile information.
   - **Task Detail Page (`taskflow\frontend\src\pages\TaskDetailPage.jsx`)**:
     - Displays detailed information about a task.
   - **Tasks Page (`taskflow\frontend\src\pages\TasksPage.jsx`)**:
     - Displays a list of tasks and allows filtering by project and search term.

3. **Components**:
   - **Page Wrapper (`taskflow\frontend\src\components\Layout\PageWrapper.jsx`)**:
     - Serves as a layout container for other components, including a sidebar and navbar.
   - **Navbar (`taskflow\frontend\src\components\Layout\Navbar.jsx`)**:
     - Displays a navigation bar at the top of the application, including links to the dashboard, user's full name, settings, and a logout button.
   - **Sidebar (`taskflow\frontend\src\components\Layout\Sidebar.jsx`)**:
     - Displays a sidebar with navigation links, which can vary based on the user's role.
   - **Project Card (`taskflow\frontend\src\components\Projects\ProjectCard.jsx`)**:
     - Displays a card for a project, including the project's name, description, and archived status.
   - **Project Settings (`taskflow\frontend\src\components\Projects\ProjectSettings.jsx`)**:
     - Allows users to update the settings of a project, including the name, description, and archived status.
   - **Task Card (`taskflow\frontend\src\components\Tasks\TaskCard.jsx`)**:
     - Displays a card for a task, including its title, status, priority, due date, and assignee.
   - **Task Detail (`taskflow\frontend\src\components\Tasks\TaskDetail.jsx`)**:
     - Displays detailed information about a task, including its status, priority, due date, title, and description.
   - **Comment List (`taskflow\frontend\src\components\Tasks\CommentList.jsx`)**:
     - Displays a list of comments for a task and allows users to add new comments.
   - **Task Form (`taskflow\frontend\src\components\Tasks\TaskForm.jsx`)**:
     - Provides a form for creating or editing a task, including fields for the task's title, description, priority, status, and due date.
   - **Button (`taskflow\frontend\src\components\UI\Button.jsx`)**:
     - A reusable button component with customizable appearance and behavior.
   - **Badge (`taskflow\frontend\src\components\UI\Badge.jsx`)**:
     - A reusable badge component with different variants for styling.
   - **Modal (`taskflow\frontend\src\components\UI\Modal.jsx`)**:
     - A modal component for displaying centered dialog boxes.
   - **Spinner (`taskflow\frontend\src\components\UI\Spinner.jsx`)**:
     - A spinner component for indicating loading states.

4. **API Client**:
   - **Client (`taskflow\frontend\src\api\client.js`)**:
     - Sets up an Axios client for making HTTP requests to the backend API.
     - Includes interceptors for adding authentication tokens and handling unauthorized responses.

5. **Context**:
   - **Auth Context (`taskflow\frontend\src\context\AuthContext.jsx`)**:
     - Provides authentication context to the application, including state management and functions for user login, registration, and logout.

6. **Hooks**:
   - **useAuth (`taskflow\frontend\src\hooks\useAuth.js`)**:
     - A custom hook for managing authentication state.
   - **useProjects (`taskflow\frontend\src\hooks\useProjects.js`)**:
     - A custom hook for managing project data, including fetching, creating, updating, and deleting projects.
   - **useTasks (`taskflow\frontend\src\hooks\useTasks.js`)**:
     - A custom hook for managing task data, including fetching, creating, updating, and deleting tasks.

7. **Utils**:
   - **Analytics (`taskflow\frontend\src\utils\analytics.js`)**:
     - Provides utility functions for tracking user events and identifying users in Mixpanel and Google Analytics.
   - **Formatters (`taskflow\frontend\src\utils\formatters.js`)**:
     - Provides utility functions for formatting dates, priorities, and statuses.
   - **Auth Utils (`taskflow\frontend\src\utils\authUtils.js`)**:
     - Provides utility functions for managing authentication sessions, including saving, clearing, and retrieving session data from the browser's localStorage.

## Typical Usage Scenario

1. **User Registration and Login**:
   - A new user visits the landing page and clicks on the "Register" link.
   - The user fills out the registration form with their full name, email, and password.
   - Upon successful registration, the user is redirected to the login page.
   - The user logs in using their email and password, and the application verifies the credentials using the backend API.

2. **Project Management**:
   - Once logged in, the user is redirected to the dashboard page, which displays an overview of their projects, tasks, and other statistics.
   - The user can navigate to the projects page to view a list of their projects.
   - The user can create a new project by clicking the "Create Project" button, which opens a modal form.
   - The user fills out the project details and submits the form, which sends a POST request to the backend API to create the project.

3. **Task Management**:
   - The user can navigate to a specific project to view its tasks.
   - The user can create a new task by clicking the "Create Task" button, which opens a modal form.
   - The user fills out the task details and submits the form, which sends a POST request to the backend API to create the task.
   - The user can update or delete tasks by interacting with the task cards or the task detail page.

4. **Notifications and Reports**:
   - The user can view and manage notifications from the dashboard or the notifications page.
   - The user can generate a PDF report for a project by navigating to the project detail page and clicking the "Generate Report" button.
   - The report is generated using the backend's report service and sent back to the frontend as a downloadable PDF file.

5. **Admin Functions**:
   - Admin users can access the admin page to manage users, view billing overviews, and perform other administrative tasks.
   - Admin users can create, update, or delete user accounts and manage project memberships.

## Where to Look Next

- **Backend**:
  - **Database Configuration**: For details on how the database is set up and configured, see the `taskflow\backend\config\db.js` file.
  - **Server Setup**: For information on how the server is initialized and started, see the `taskflow\backend\server.js` file.
  - **Controllers**: For detailed documentation on the various controllers and their endpoints, see the respective files in the `taskflow\backend\src\controllers` directory.
  - **Middleware**: For details on the middleware used for authentication, authorization, error handling, and more, see the files in the `taskflow\backend\src\middleware` directory.
  - **Models**: For information on the database models and their functions, see the files in the `taskflow\backend\src\models` directory.
  - **Services**: For details on the services used for email, notifications, reports, and Stripe integration, see the files in the `taskflow\backend\src\services` directory.
  - **Utils**: For utility functions and helpers, see the files in the `taskflow\backend\src\utils` directory.

- **Frontend**:
  - **Main Application**: For an overview of the main application setup, see the `taskflow\frontend\src\main.jsx` file.
  - **App Component**: For details on the main application component and routing, see the `taskflow\frontend\src\App.jsx` file.
  - **Pages**: For detailed documentation on the various pages, see the respective files in the `taskflow\frontend\src\pages` directory.
  - **Components**: For information on the reusable UI components, see the files in the `taskflow\frontend\src\components` directory.
  - **API Client**: For details on the Axios client setup and interceptors, see the `taskflow\frontend\src\api\client.js` file.
  - **Context**: For information on the authentication context, see the `taskflow\frontend\src\context\AuthContext.jsx` file.
  - **Hooks**: For custom hooks used in the application, see the files in the `taskflow\frontend\src\hooks` directory.
  - **Utils**: For utility functions and helpers, see the files in the `taskflow\frontend\src\utils` directory.

For more detailed documentation on specific components, services, and utilities, refer to the respective sections in the documentation.

---

# Architecture and Data Flow

## Overview

The TaskFlow application is a web-based project management tool built using a combination of Node.js, Express, PostgreSQL, and React. The architecture is designed to be modular, scalable, and maintainable, with clear separation of concerns between different components. This section provides an overview of the main architectural components, data flow, and important patterns used in the application.

## Main Architectural Components

### Backend

1. **Database Layer**
   - **File:** `taskflow/backend/config/db.js`
   - **Description:** Sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries. It uses environment variables for configuration, with fallbacks for local development.
   - **Key Entities:**
     - `query`: A function that executes SQL queries using the configured database pool.

2. **Server**
   - **File:** `taskflow/backend/server.js`
   - **Description:** Sets up and starts a Node.js server using an Express application defined in `./src/app`. It listens on a specified port, defaulting to 3001 if not defined in the environment variables.
   - **Key Entities:**
     - `app.listen`: Starts the server and listens on the specified port, logging a message to the console upon successful startup.

3. **Express Application**
   - **File:** `taskflow/backend/src/app.js`
   - **Description:** Sets up an Express.js application, configures middleware for JSON and text parsing, serves static files from the uploads directory, and mounts various API routes for different functionalities.
   - **Key Entities:**
     - Middleware: JSON and text parsing, static file serving, error handling.
     - Routes: Authentication, tasks, projects, users, attachments, reports, imports, notifications, and admin functionalities.
     - Health Check Endpoint: `/api/v1/health`

4. **Controllers**
   - **Files:** `taskflow/backend/src/controllers/*.js`
   - **Description:** Handle HTTP requests and interact with the database or other services to perform business logic.
   - **Key Entities:**
     - `reportController`: Generates PDF reports for projects.
     - `importController`: Imports tasks from XML and CSV formats.
     - `adminController`: Manages administrative tasks like user management and billing.
     - `attachmentController`: Manages task attachments.
     - `notificationController`: Handles notifications and user preferences.
     - `projectController`: Manages projects.
     - `userController`: Manages user profiles.
     - `taskController`: Manages tasks and task comments.
     - `authController`: Handles user authentication, registration, and password management.

5. **Models**
   - **Files:** `taskflow/backend/src/models/*.js`
   - **Description:** Define database operations for interacting with the database tables.
   - **Key Entities:**
     - `taskModel`: Manages tasks.
     - `userModel`: Manages users.
     - `orgModel`: Manages organizations and their members.
     - `projectModel`: Manages projects.

6. **Middlewares**
   - **Files:** `taskflow/backend/src/middleware/*.js`
   - **Description:** Handle cross-cutting concerns like authentication, rate limiting, and error handling.
   - **Key Entities:**
     - `authorize`: Checks user roles and authorizes access.
     - `authenticate`: Verifies JWT tokens.
     - `errorHandler`: Logs errors and sends JSON responses.
     - `rateLimiter`: Limits the rate of report generation requests.
     - `upload`: Configures file upload middleware using Multer.

7. **Services**
   - **Files:** `taskflow/backend/src/services/*.js`
   - **Description:** Provide utility functions for common tasks like sending emails, generating reports, and managing notifications.
   - **Key Entities:**
     - `emailService`: Sends invitation and password reset emails using SendGrid.
     - `reportService`: Generates HTML and PDF reports.
     - `notificationService`: Manages user notifications and preferences.
     - `stripeService`: Interacts with the Stripe API for billing and subscriptions.

8. **Utils**
   - **Files:** `taskflow/backend/src/utils/*.js`
   - **Description:** Contains utility functions for common tasks like logging, token generation, and data validation.
   - **Key Entities:**
     - `logger`: Logs messages with different levels (info, warn, error).
     - `tokenUtils`: Generates and verifies JWT access and refresh tokens.
     - `validators`: Validates and sanitizes strings.

### Frontend

1. **Main Application**
   - **File:** `taskflow/frontend/src/main.jsx`
   - **Description:** Sets up the React application, including the root component, routing, and authentication context.
   - **Key Entities:**
     - `ReactDOM.createRoot`: Renders the main App component into the DOM.
     - `BrowserRouter`: Manages routing.
     - `AuthProvider`: Provides authentication context.

2. **App Component**
   - **File:** `taskflow/frontend/src/App.jsx`
   - **Description:** Defines the main application component with routing for various pages, including public and private routes.
   - **Key Entities:**
     - Routes: Landing, Login, Registration, Dashboard, Projects, Tasks, Settings, Admin, and a Not Found page.

3. **Layout Components**
   - **Files:** `taskflow/frontend/src/components/Layout/*.jsx`
   - **Description:** Provide layout components like PageWrapper, Navbar, and Sidebar.
   - **Key Entities:**
     - `PageWrapper`: Acts as a layout wrapper, integrating a sidebar, navbar, and main content area.
     - `Navbar`: Displays navigation links and user information.
     - `Sidebar`: Displays navigation links based on user role.

4. **Pages**
   - **Files:** `taskflow/frontend/src/pages/*.jsx`
   - **Description:** Define React components for different pages in the application.
   - **Key Entities:**
     - `AdminPage`: Displays user data and admin actions.
     - `DashboardPage`: Shows statistics and recent tasks.
     - `LandingPage`: Serves as the landing page with navigation links.
     - `LoginPage`: Handles user login.
     - `NotFoundPage`: Displays a 404 error message.
     - `ProjectsPage`: Displays a list of projects and a modal for creating new projects.
     - `ProjectDetailPage`: Displays detailed information about a project.
     - `RegisterPage`: Handles user registration.
     - `SettingsPage`: Allows users to update their profile.
     - `TasksPage`: Displays a list of tasks and a modal for creating new tasks.
     - `TaskDetailPage`: Displays detailed information about a task.

5. **API Client**
   - **File:** `taskflow/frontend/src/api/client.js`
   - **Description:** Sets up an Axios client for making HTTP requests to the backend API.
   - **Key Entities:**
     - `client`: The Axios client instance configured with a base URL and interceptors for authentication and response handling.

6. **API Services**
   - **Files:** `taskflow/frontend/src/api/*.js`
   - **Description:** Provide functions for interacting with the backend API.
   - **Key Entities:**
     - `auth`: Handles authentication operations.
     - `admin`: Manages admin-related endpoints.
     - `projects`: Manages project-related endpoints.
     - `tasks`: Manages task-related endpoints.

7. **Context and Hooks**
   - **Files:** `taskflow/frontend/src/context/*.jsx`, `taskflow/frontend/src/hooks/*.js`
   - **Description:** Provide state management and utility hooks.
   - **Key Entities:**
     - `AuthContext`: Manages user authentication state.
     - `useAuth`: Custom hook for accessing authentication state.
     - `useProjects`: Custom hook for managing project data.
     - `useTasks`: Custom hook for managing task data.

8. **Utils**
   - **Files:** `taskflow/frontend/src/utils/*.js`
   - **Description:** Contains utility functions for common tasks like analytics, formatters, and authentication.
   - **Key Entities:**
     - `analytics`: Tracks user events and identifies users in Mixpanel and Google Analytics.
     - `formatters`: Formats dates, priorities, and statuses.
     - `authUtils`: Manages authentication sessions in local storage.

## Data and Control Flow

### Backend

1. **Request Handling**
   - **Entry Point:** `taskflow/backend/server.js`
   - **Flow:**
     - The server listens for incoming HTTP requests.
     - Requests are routed to the appropriate controller based on the URL and HTTP method.
     - Middleware functions (e.g., authentication, rate limiting) are applied as needed.

2. **Controller Actions**
   - **Example: `reportController.generatePdf`**
     - **Flow:**
       - The `generatePdf` endpoint is called with a project ID.
       - The controller checks for project existence and user access.
       - It retrieves tasks associated with the project from the database using `taskModel`.
       - The `reportService` generates an HTML report and converts it to a PDF.
       - The PDF is sent as a response.

3. **Database Interactions**
   - **Example: `taskModel.create`**
     - **Flow:**
       - The `create` function is called with task data.
       - It executes an SQL query to insert the task into the `tasks` table.
       - The new task ID is returned.

4. **Service Functions**
   - **Example: `emailService.sendInvite`**
     - **Flow:**
       - The `sendInvite` function is called with user data.
       - It constructs an email message and sends it using the SendGrid API.

### Frontend

1. **Application Initialization**
   - **Entry Point:** `taskflow/frontend/src/main.jsx`
   - **Flow:**
     - The React application is rendered into the DOM.
     - The `AuthProvider` provides authentication context to the application.
     - The `BrowserRouter` sets up routing for different pages.

2. **Page Rendering**
   - **Example: `ProjectsPage`**
     - **Flow:**
       - The `ProjectsPage` component is rendered as part of a route.
       - The `useProjects` hook fetches project data from the backend API.
       - The fetched data is displayed in a list, and a modal is provided for creating new projects.

3. **API Requests**
   - **Example: `auth.login`**
     - **Flow:**
       - The `login` function is called with user credentials.
       - It sends a POST request to the `/api/v1/auth/login` endpoint.
       - The response includes an access token and user data.
       - The token and user data are stored in local storage using `authUtils`.

4. **State Management**
   - **Example: `useAuth`**
     - **Flow:**
       - The `useAuth` hook provides authentication state to components.
       - It checks the local storage for the authentication token and user data.
       - It provides functions to log in, log out, and refresh the token.

5. **Event Handling**
   - **Example: `TaskDetailPage`**
     - **Flow:**
       - The `TaskDetailPage` component displays detailed information about a task.
       - User interactions (e.g., updating task status) trigger API requests to update the task data.
       - The updated data is fetched and displayed in the component.

## Important Patterns

1. **Model-View-Controller (MVC)**
   - **Backend:**
     - **Models:** Handle database operations.
     - **Controllers:** Handle business logic and HTTP requests.
     - **Views:** Not explicitly defined, but the API responses can be considered as views.
   - **Frontend:**
     - **Models:** State management using hooks like `useProjects` and `useTasks`.
     - **Views:** React components that display data.
     - **Controllers:** Functions in API services that handle API requests and responses.

2. **Middleware Pattern**
   - **Backend:**
     - Middleware functions like `authenticate` and `authorize` handle cross-cutting concerns like authentication and authorization.
   - **Frontend:**
     - Axios interceptors in `client.js` handle adding authentication tokens to requests and handling unauthorized responses.

3. **Service Layer**
   - **Backend:**
     - Service functions in `services` handle common tasks like sending emails, generating reports, and managing notifications.
   - **Frontend:**
     - API services in `api` handle interactions with the backend API.

4. **Context and Hooks**
   - **Frontend:**
     - Context providers like `AuthProvider` and custom hooks like `useAuth` and `useProjects` manage state and provide utility functions to components.

5. **Error Handling**
   - **Backend:**
     - The `errorHandler` middleware logs errors and sends JSON responses.
   - **Frontend:**
     - Error states are handled in components, and error messages are displayed to the user.

By following these patterns and maintaining a clear separation of concerns, the TaskFlow application is designed to be modular, scalable, and easy to maintain.

---

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

---

# API Reference

This section provides a comprehensive reference for the API endpoints, including request and response formats, authentication requirements, and error handling. Each endpoint is described in detail, mapping back to the relevant files and functions in the codebase.

## Authentication

### Authentication Middleware
- **File**: `taskflow\backend\src\middleware\authenticate.js`
- **Function**: `authenticate`
- **Description**: Authenticates HTTP requests by verifying a JWT token in the authorization header. Attaches user information to the request object if the token is valid. Returns a 401 Unauthorized response if the token is missing, invalid, or expired.
- **Tags**: `auth`, `security`, `logging`

### Authorization Middleware
- **File**: `taskflow\backend\src\middleware\authorize.js`
- **Function**: `authorize`
- **Description**: Checks if the user has the required roles to access a resource. Returns a 401 Unauthorized status if the user is not authenticated, and a 403 Forbidden status if the user does not have sufficient permissions.
- **Tags**: `auth`, `security`

### Rate Limiter Middleware
- **File**: `taskflow\backend\src\middleware\rateLimiter.js`
- **Function**: `reportLimiter`
- **Description**: Limits the rate of report generation requests to 10 per minute to prevent abuse of the PDF export feature.
- **Tags**: `network`, `security`

## User Management

### User Registration
- **File**: `taskflow\backend\src\controllers\authController.js`
- **Endpoint**: `POST /api/register`
- **Function**: `register`
- **Description**: Handles user registration, including validation, password hashing, and creation of user and organization records.
- **Tags**: `auth`, `db`, `network`, `logging`

### User Login
- **File**: `taskflow\backend\src\controllers\authController.js`
- **Endpoint**: `POST /api/login`
- **Function**: `login`
- **Description**: Handles user login, including credential validation and token generation.
- **Tags**: `auth`, `db`, `network`, `logging`

### Token Refresh
- **File**: `taskflow\backend\src\controllers\authController.js`
- **Endpoint**: `POST /api/refresh`
- **Function**: `refresh`
- **Description**: Handles token refresh, generating a new access token from a valid refresh token.
- **Tags**: `auth`, `db`, `network`, `logging`

### Password Reset Request
- **File**: `taskflow\backend\src\controllers\authController.js`
- **Endpoint**: `POST /api/forgot-password`
- **Function**: `forgotPassword`
- **Description**: Handles password reset requests, sending a reset link to the user's email if the email exists.
- **Tags**: `auth`, `db`, `network`, `logging`

### Password Reset
- **File**: `taskflow\backend\src\controllers\authController.js`
- **Endpoint**: `POST /api/reset-password`
- **Function**: `resetPassword`
- **Description**: Handles password reset, updating the user's password with a new hashed password.
- **Tags**: `auth`, `db`, `network`, `logging`

### User Logout
- **File**: `taskflow\backend\src\controllers\authController.js`
- **Endpoint**: `POST /api/logout`
- **Function**: `logout`
- **Description**: Handles user logout, invalidating the user's refresh token.
- **Tags**: `auth`, `db`, `network`, `logging`

### Get User Profile
- **File**: `taskflow\backend\src\controllers\userController.js`
- **Endpoint**: `GET /api/users/profile`
- **Function**: `getProfile`
- **Description**: Retrieves the user's profile information.
- **Tags**: `auth`, `db`, `network`, `security`

### Update User Profile
- **File**: `taskflow\backend\src\controllers\userController.js`
- **Endpoint**: `PUT /api/users/profile`
- **Function**: `updateProfile`
- **Description**: Updates the user's profile information.
- **Tags**: `auth`, `db`, `network`, `security`

## Project Management

### List Projects
- **File**: `taskflow\backend\src\controllers\projectController.js`
- **Endpoint**: `GET /api/projects`
- **Function**: `list`
- **Description**: Lists projects for a given organization, optionally including archived projects.
- **Tags**: `auth`, `db`, `network`, `security`

### Get Project by ID
- **File**: `taskflow\backend\src\controllers\projectController.js`
- **Endpoint**: `GET /api/projects/:projectId`
- **Function**: `getOne`
- **Description**: Retrieves a single project by ID, checking for existence and organization ownership.
- **Tags**: `auth`, `db`, `network`, `security`

### Create Project
- **File**: `taskflow\backend\src\controllers\projectController.js`
- **Endpoint**: `POST /api/projects`
- **Function**: `create`
- **Description**: Creates a new project, validating the project name and associating it with the organization.
- **Tags**: `auth`, `db`, `network`, `security`

### Update Project
- **File**: `taskflow\backend\src\controllers\projectController.js`
- **Endpoint**: `PUT /api/projects/:projectId`
- **Function**: `update`
- **Description**: Updates an existing project, ensuring the project belongs to the organization.
- **Tags**: `auth`, `db`, `network`, `security`

### Delete Project
- **File**: `taskflow\backend\src\controllers\projectController.js`
- **Endpoint**: `DELETE /api/projects/:projectId`
- **Function**: `remove`
- **Description**: Deletes a project, verifying its existence and organization ownership.
- **Tags**: `auth`, `db`, `network`, `security`

## Task Management

### List Tasks
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `GET /api/tasks`
- **Function**: `list`
- **Description**: Lists tasks for a specific project or across an organization.
- **Tags**: `auth`, `db`, `network`, `logging`

### Get Task by ID
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `GET /api/tasks/:taskId`
- **Function**: `getOne`
- **Description**: Retrieves a single task by its ID.
- **Tags**: `auth`, `db`, `network`, `logging`

### Create Task
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `POST /api/tasks`
- **Function**: `create`
- **Description**: Creates a new task within a project.
- **Tags**: `auth`, `db`, `network`, `logging`

### Update Task
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `PUT /api/tasks/:taskId`
- **Function**: `update`
- **Description**: Updates an existing task.
- **Tags**: `auth`, `db`, `network`, `logging`

### Delete Task
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `DELETE /api/tasks/:taskId`
- **Function**: `remove`
- **Description**: Deletes a task by its ID.
- **Tags**: `auth`, `db`, `network`, `logging`

### Add Comment to Task
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `POST /api/tasks/:taskId/comments`
- **Function**: `addComment`
- **Description**: Adds a comment to a specific task.
- **Tags**: `auth`, `db`, `network`, `logging`

### Get Comments for Task
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `GET /api/tasks/:taskId/comments`
- **Function**: `getComments`
- **Description**: Retrieves comments for a specific task.
- **Tags**: `auth`, `db`, `network`, `logging`

## Report Generation

### Generate PDF Report
- **File**: `taskflow\backend\src\controllers\reportController.js`
- **Endpoint**: `GET /api/reports/:projectId/pdf`
- **Function**: `generatePdf`
- **Description**: Generates a PDF report for a project's tasks. It requires a project ID as a parameter and checks for project existence and user access before generating the report.
- **Tags**: `auth`, `db`, `network`, `file_io`, `security`

## Attachment Management

### List Attachments for Task
- **File**: `taskflow\backend\src\controllers\attachmentController.js`
- **Endpoint**: `GET /api/tasks/:taskId/attachments`
- **Function**: `list`
- **Description**: Lists attachments for a specific task.
- **Tags**: `auth`, `db`, `network`, `file_io`

### Upload Attachment
- **File**: `taskflow\backend\src\controllers\attachmentController.js`
- **Endpoint**: `POST /api/tasks/:taskId/attachments`
- **Function**: `upload`
- **Description**: Uploads a file as an attachment to a specific task.
- **Tags**: `auth`, `db`, `network`, `file_io`

### Download Attachment
- **File**: `taskflow\backend\src\controllers\attachmentController.js`
- **Endpoint**: `GET /api/tasks/attachments/:attachmentId`
- **Function**: `download`
- **Description**: Downloads an attachment by its ID.
- **Tags**: `auth`, `db`, `network`, `file_io`

### Remove Attachment
- **File**: `taskflow\backend\src\controllers\attachmentController.js`
- **Endpoint**: `DELETE /api/tasks/attachments/:attachmentId`
- **Function**: `remove`
- **Description**: Removes an attachment by its ID.
- **Tags**: `auth`, `db`, `network`, `file_io`

## Notification Management

### List Notifications
- **File**: `taskflow\backend\src\controllers\notificationController.js`
- **Endpoint**: `GET /api/notifications`
- **Function**: `list`
- **Description**: Lists notifications for a user, with a limit parameter.
- **Tags**: `auth`, `db`, `network`, `security`

### Mark Notification as Read
- **File**: `taskflow\backend\src\controllers\notificationController.js`
- **Endpoint**: `PUT /api/notifications/:id/read`
- **Function**: `markRead`
- **Description**: Marks a specific notification as read for a user.
- **Tags**: `auth`, `db`, `network`, `security`

### Get Notification Preferences
- **File**: `taskflow\backend\src\controllers\notificationController.js`
- **Endpoint**: `GET /api/notifications/preferences`
- **Function**: `getPreferences`
- **Description**: Retrieves notification preferences for a user.
- **Tags**: `auth`, `db`, `network`, `security`

### Update Notification Preferences
- **File**: `taskflow\backend\src\controllers\notificationController.js`
- **Endpoint**: `POST /api/notifications/preferences`
- **Function**: `updatePreferences`
- **Description**: Updates notification preferences for a user.
- **Tags**: `auth`, `db`, `network`, `security`

## Admin Management

### Get All Users
- **File**: `taskflow\backend\src\controllers\adminController.js`
- **Endpoint**: `GET /api/admin/users`
- **Function**: `getAllUsers`
- **Description**: Retrieves all users from the database.
- **Tags**: `auth`, `db`, `network`, `security`

### Delete User
- **File**: `taskflow\backend\src\controllers\adminController.js`
- **Endpoint**: `DELETE /api/admin/users/:id`
- **Function**: `deleteUser`
- **Description**: Deletes a user by their ID.
- **Tags**: `auth`, `db`, `network`, `security`

### Get Billing Overview
- **File**: `taskflow\backend\src\controllers\adminController.js`
- **Endpoint**: `GET /api/admin/billing`
- **Function**: `getBillingOverview`
- **Description**: Retrieves a billing overview, including user details and project counts.
- **Tags**: `auth`, `db`, `network`, `security`

## Import Management

### Import Tasks from XML
- **File**: `taskflow\backend\src\controllers\importController.js`
- **Endpoint**: `POST /api/import/xml/:projectId`
- **Function**: `importXml`
- **Description**: Imports tasks from XML data. Validates the project, parses the XML, and creates tasks in the database.
- **Tags**: `auth`, `db`, `network`, `file_io`

### Import Tasks from CSV
- **File**: `taskflow\backend\src\controllers\importController.js`
- **Endpoint**: `POST /api/import/csv/:projectId`
- **Function**: `importCsv`
- **Description**: Imports tasks from CSV data. Validates the project, parses the CSV, and creates tasks in the database.
- **Tags**: `auth`, `db`, `network`, `file_io`

## Health Check

### Health Check Endpoint
- **File**: `taskflow\backend\src\app.js`
- **Endpoint**: `GET /api/v1/health`
- **Function**: `GET /api/v1/health`
- **Description**: Endpoint to check the health of the application, returning a JSON object with a success status and timestamp.
- **Tags**: `network`, `auth`, `db`, `file_io`, `security`

## Error Handling

### Error Handler Middleware
- **File**: `taskflow\backend\src\middleware\errorHandler.js`
- **Function**: `errorHandler`
- **Description**: Middleware function that handles errors by logging them and sending a JSON response.
- **Tags**: `logging`, `network`, `security`

## File Upload

### File Upload Middleware
- **File**: `taskflow\backend\src\middleware\upload.js`
- **Function**: `upload`
- **Description**: Configures and exports a multer middleware for handling file uploads. Sets the upload directory and defines how files are stored, including the destination and filename formatting.
- **Tags**: `file_io`

## Database Models

### Task Model
- **File**: `taskflow\backend\src\models\taskModel.js`
- **Functions**: `findById`, `findByProject`, `create`, `update`, `remove`
- **Description**: Provides methods to find, create, update, and remove tasks in the database.
- **Tags**: `db`

### User Model
- **File**: `taskflow\backend\src\models\userModel.js`
- **Functions**: `findById`, `findByEmail`, `create`, `updateRefreshToken`, `setResetToken`, `clearResetToken`, `updatePassword`
- **Description**: Provides methods to find, create, and update user records, including handling of refresh tokens, reset tokens, and password updates.
- **Tags**: `db`

### Organization Model
- **File**: `taskflow\backend\src\models\orgModel.js`
- **Functions**: `findById`, `create`, `addMember`, `getMembers`
- **Description**: Provides methods to find an organization by ID, create a new organization, add a member to an organization, and retrieve the members of an organization.
- **Tags**: `db`

### Project Model
- **File**: `taskflow\backend\src\models\projectModel.js`
- **Functions**: `findById`, `findByOrg`, `create`, `update`, `remove`
- **Description**: Provides methods to find, create, update, and delete project records, as well as to find projects by organization ID.
- **Tags**: `db`

## Utility Functions

### Token Utilities
- **File**: `taskflow\backend\src\utils\tokenUtils.js`
- **Functions**: `signToken`, `verifyToken`
- **Description**: Provides functions to sign and verify JWT access and refresh tokens.
- **Tags**: `auth`, `crypto`, `security`

### Validators
- **File**: `taskflow\backend\src\utils\validators.js`
- **Functions**: `isEmail`, `isNonEmptyString`, `sanitizeString`
- **Description**: Provides utility functions for validating and sanitizing strings, specifically for email format, non-empty strings, and string sanitization with a maximum length.
- **Tags**: `other`

### Formatters
- **File**: `taskflow\frontend\src\utils\formatters.js`
- **Functions**: `formatDate`, `formatRelative`, `priorityLabel`, `statusLabel`
- **Description**: Provides utility functions for formatting dates, relative times, priority labels, and status labels.
- **Tags**: `other`

### Analytics
- **File**: `taskflow\frontend\src\utils\analytics.js`
- **Functions**: `trackEvent`, `identify`
- **Description**: Provides utility functions for tracking user events and identifying users in Mixpanel and Google Analytics.
- **Tags**: `network`, `logging`

### Authentication Utilities
- **File**: `taskflow\frontend\src\utils\authUtils.js`
- **Functions**: `saveSession`, `clearSession`, `getToken`, `getRefreshToken`, `getStoredUser`
- **Description**: Provides utility functions for managing authentication sessions in a frontend application, including saving and clearing session data, and retrieving the authentication token and user information.
- **Tags**: `auth`, `storage`

## Frontend API Client

### Axios Client
- **File**: `taskflow\frontend\src\api\client.js`
- **Function**: `client`
- **Description**: Sets up an Axios client for making HTTP requests to a backend API. Includes interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to the login page.
- **Tags**: `auth`, `network`, `logging`, `security`

## Frontend Routes

### Admin Routes
- **File**: `taskflow\frontend\src\api\admin.js`
- **Functions**: `getAllUsers`, `deleteUser`, `getBillingOverview`
- **Description**: Provides functions to fetch all users, delete a user, and get a billing overview from the admin API endpoint.
- **Tags**: `network`, `auth`

### Project Routes
- **File**: `taskflow\frontend\src\api\projects.js`
- **Functions**: `list`, `getOne`, `create`, `update`, `remove`
- **Description**: Provides functions to list, retrieve, create, update, and delete projects from the API.
- **Tags**: `network`

### Task Routes
- **File**: `taskflow\frontend\src\api\tasks.js`
- **Functions**: `list`, `getOne`, `create`, `update`, `remove`
- **Description**: Provides functions to list, retrieve, create, update, and delete tasks from the API.
- **Tags**: `network`, `api`

### Authentication Routes
- **File**: `taskflow\frontend\src\api\auth.js`
- **Functions**: `login`, `register`, `logout`, `refreshToken`
- **Description**: Provides functions to handle login, registration, logout,

---

# Data Models

This section provides detailed descriptions of the database models used in the TaskFlow application. The models define the structure of the database tables, their relationships, and schema definitions.

## Database Configuration

The database configuration is set up in the file `taskflow/backend/config/db.js`. This file initializes a PostgreSQL database connection pool using the `pg` library. The connection pool is configured with environment variables or fallbacks for local development. The pool and a query function for executing SQL queries are exported for use in other parts of the application.

### Key Entities
- **Database Pool**: Manages database connections.
- **Query Function**: Executes SQL queries using the configured database pool.

### Example Usage
```javascript
const { query } = require('./config/db');

query('SELECT * FROM users').then(result => {
  console.log(result.rows);
});
```

## User Model

The user model is defined in `taskflow/backend/src/models/userModel.js`. It provides methods to interact with the `users` table in the database, including finding, creating, and updating user records. The model also handles refresh tokens, reset tokens, and password updates.

### Key Methods
- **`findByEmail(email)`**: Finds a user by email.
- **`create(user)`**: Creates a new user record.
- **`updateRefreshToken(userId, token)`**: Updates the refresh token for a user.
- **`setResetToken(userId, token)`**: Sets a password reset token for a user.
- **`clearResetToken(userId)`**: Clears the password reset token for a user.
- **`updatePassword(userId, password)`**: Updates the user's password.

### Example Usage
```javascript
const { findByEmail, create } = require('./models/userModel');

findByEmail('user@example.com').then(user => {
  if (!user) {
    create({ email: 'user@example.com', password: 'hashedPassword' });
  }
});
```

## Task Model

The task model is defined in `taskflow/backend/src/models/taskModel.js`. It provides methods to interact with the `tasks` table in the database, including finding tasks by ID or project, creating new tasks, updating existing tasks, and removing tasks.

### Key Methods
- **`findById(taskId)`**: Finds a task by its ID.
- **`findByProject(projectId)`**: Finds tasks associated with a specific project.
- **`create(task)`**: Creates a new task.
- **`update(taskId, data)`**: Updates an existing task.
- **`remove(taskId)`**: Deletes a task.

### Example Usage
```javascript
const { findById, create, update, remove } = require('./models/taskModel');

findById(1).then(task => {
  if (task) {
    update(1, { title: 'Updated Task' });
  } else {
    create({ projectId: 1, title: 'New Task' });
  }
});
```

## Project Model

The project model is defined in `taskflow/backend/src/models/projectModel.js`. It provides methods to interact with the `projects` table in the database, including finding, creating, updating, and deleting project records. The model also supports finding projects by organization ID.

### Key Methods
- **`findById(projectId)`**: Finds a project by its ID.
- **`findByOrg(orgId, includeArchived = false)`**: Finds projects by organization ID, optionally including archived projects.
- **`create(project)`**: Creates a new project.
- **`update(projectId, data)`**: Updates an existing project.
- **`remove(projectId)`**: Deletes a project.

### Example Usage
```javascript
const { findById, create, update, remove } = require('./models/projectModel');

findById(1).then(project => {
  if (project) {
    update(1, { name: 'Updated Project' });
  } else {
    create({ orgId: 1, name: 'New Project' });
  }
});
```

## Organization Model

The organization model is defined in `taskflow/backend/src/models/orgModel.js`. It provides methods to interact with the `orgs` and `org_members` tables in the database, including finding an organization by ID, creating a new organization, adding a member to an organization, and retrieving the members of an organization.

### Key Methods
- **`findById(orgId)`**: Finds an organization by its ID.
- **`create(org)`**: Creates a new organization.
- **`addMember(orgId, userId, role)`**: Adds a member to an organization with a specified role.
- **`getMembers(orgId)`**: Retrieves the members of an organization, including their user details and role within the organization.

### Example Usage
```javascript
const { findById, create, addMember, getMembers } = require('./models/orgModel');

findById(1).then(org => {
  if (!org) {
    create({ name: 'New Organization' }).then(newOrg => {
      addMember(newOrg.id, 1, 'admin');
    });
  }
});

getMembers(1).then(members => {
  console.log(members);
});
```

## Attachment Model

The attachment model is defined in `taskflow/backend/src/controllers/attachmentController.js`. It provides methods to manage task attachments, including listing, uploading, downloading, and removing attachments. The model interacts with the database and the file system to perform these operations.

### Key Methods
- **`list(taskId)`**: Lists attachments for a specific task.
- **`upload(taskId, file)`**: Uploads a file as an attachment to a specific task.
- **`download(attachmentId)`**: Downloads an attachment by its ID.
- **`remove(attachmentId)`**: Removes an attachment by its ID.

### Example Usage
```javascript
const { list, upload, download, remove } = require('./controllers/attachmentController');

list(1).then(attachments => {
  console.log(attachments);
});

upload(1, file).then(attachment => {
  console.log(attachment);
});
```

## Notification Model

The notification model is defined in `taskflow/backend/src/controllers/notificationController.js` and `taskflow/backend/src/services/notificationService.js`. It provides methods to manage user notifications, including listing notifications, marking them as read, and managing user preferences.

### Key Methods
- **`list(userId, limit)`**: Lists notifications for a user, with an optional limit.
- **`markRead(userId, notificationId)`**: Marks a specific notification as read for a user.
- **`getPreferences(userId)`**: Retrieves the notification preferences for a user.
- **`updatePreferences(userId, preferences)`**: Updates the notification preferences for a user.

### Example Usage
```javascript
const { list, markRead, getPreferences, updatePreferences } = require('./controllers/notificationController');

list(1, 10).then(notifications => {
  console.log(notifications);
});

markRead(1, 1).then(() => {
  console.log('Notification marked as read');
});

getPreferences(1).then(preferences => {
  console.log(preferences);
});

updatePreferences(1, { email: true, sms: false }).then(() => {
  console.log('Preferences updated');
});
```

## Summary

The data models in the TaskFlow application are designed to provide a robust and flexible way to manage user, task, project, organization, attachment, and notification data. Each model includes methods for common database operations, ensuring that the application can efficiently interact with the PostgreSQL database. The models are used throughout the application to handle data retrieval, creation, updating, and deletion, forming the core of the application's data management layer.

---

# Frontend Components

This section provides an overview of the key React components used in the frontend of the TaskFlow application. It covers the components' props, state, and interactions with the backend.

## Main Application Component

### `App.jsx`
- **Description**: The main entry point of the application, which sets up routing for various pages, including public and private routes. Private routes require user authentication, redirecting unauthenticated users to the login page.
- **Props**: None
- **State**: None
- **Interactions**:
  - **Routing**: Uses `react-router-dom` to define routes for different pages.
  - **Authentication**: Manages user authentication and redirects unauthenticated users to the login page.

## Layout Components

### `PageWrapper.jsx`
- **Description**: A layout container for other components, including a sidebar and a navbar. It can display a title and children components within the main content area.
- **Props**:
  - `children`: React nodes to be rendered within the main content area.
  - `title`: A string to be displayed as the page title.
- **State**: None
- **Interactions**:
  - **Sidebar and Navbar**: Integrates the `Sidebar` and `Navbar` components to provide navigation and user information.

### `Navbar.jsx`
- **Description**: Displays a navigation bar at the top of the application, including links to the dashboard, settings, and a logout button.
- **Props**: None
- **State**: None
- **Interactions**:
  - **Authentication**: Uses the `useAuth` hook to manage authentication state and handle logout actions.

### `Sidebar.jsx`
- **Description**: Displays a sidebar with navigation links to different sections of the app. The sidebar shows the user's email and additional links based on the user's role.
- **Props**: None
- **State**: None
- **Interactions**:
  - **Navigation**: Uses `react-router-dom` to create navigation links.
  - **Authentication**: Uses the `useAuth` hook to manage user authentication and display role-based links.

## Page Components

### `AdminPage.jsx`
- **Description**: A page for administrative tasks, including a table of users and actions to manage them.
- **Props**: None
- **State**: None
- **Interactions**:
  - **User Table**: Integrates the `UserTable` component to display and manage user data.
  - **Authentication**: Requires user authentication and admin role to access.

### `DashboardPage.jsx`
- **Description**: Displays a dashboard with statistics about open tasks, overdue tasks, and projects. It also shows a list of recent tasks and provides a button to navigate to the task creation page.
- **Props**: None
- **State**: None
- **Interactions**:
  - **Data Fetching**: Uses the `useTasks` and `useProjects` hooks to fetch and manage task and project data.
  - **Navigation**: Provides links to create new tasks and navigate to project details.

### `LandingPage.jsx`
- **Description**: The landing page of the TaskFlow application, including navigation, a main section with a call to action, a features section, a pricing section, and testimonials from users.
- **Props**: None
- **State**: None
- **Interactions**:
  - **Navigation**: Uses `react-router-dom` to navigate to login and registration pages.

### `LoginPage.jsx`
- **Description**: A page for user login, including form fields for email and password, and a submit button to authenticate the user.
- **Props**: None
- **State**:
  - `email`: The user's email address.
  - `password`: The user's password.
  - `loading`: A boolean indicating whether the login request is in progress.
- **Interactions**:
  - **Form Submission**: Handles form submission to authenticate the user using the `authApi` module.
  - **Navigation**: Redirects the user to the dashboard upon successful login.

### `NotFoundPage.jsx`
- **Description**: Displays a 404 error page with a message and a link to return to the home page.
- **Props**: None
- **State**: None
- **Interactions**: None

### `ProjectsPage.jsx`
- **Description**: Displays a list of projects and provides a modal for creating new projects.
- **Props**: None
- **State**:
  - `projects`: An array of project objects.
  - `isModalOpen`: A boolean indicating whether the project creation modal is open.
- **Interactions**:
  - **Data Fetching**: Uses the `useProjects` hook to fetch and manage project data.
  - **Modal**: Manages the state of the project creation modal and handles form submission to create new projects.

### `ProjectDetailPage.jsx`
- **Description**: Displays details of a project and provides options to view tasks and manage project settings.
- **Props**: None
- **State**:
  - `project`: The project object.
  - `loading`: A boolean indicating whether the project data is being fetched.
  - `error`: An error object if the project data fetch fails.
- **Interactions**:
  - **Data Fetching**: Fetches project data from the API using the `projectsApi` module.
  - **Navigation**: Provides links to tasks and project settings.

### `RegisterPage.jsx`
- **Description**: A page for user registration, including form fields for full name, email, and password, and a submit button to register the user.
- **Props**: None
- **State**:
  - `fullName`: The user's full name.
  - `email`: The user's email address.
  - `password`: The user's password.
  - `loading`: A boolean indicating whether the registration request is in progress.
- **Interactions**:
  - **Form Submission**: Handles form submission to register the user using the `authApi` module.
  - **Navigation**: Redirects the user to the dashboard upon successful registration.

### `SettingsPage.jsx`
- **Description**: Allows users to update their full name. It uses a custom hook for authentication and makes an API call to update the user's profile.
- **Props**: None
- **State**:
  - `fullName`: The user's full name.
  - `loading`: A boolean indicating whether the update request is in progress.
- **Interactions**:
  - **Data Fetching**: Uses the `useAuth` hook to manage user authentication and fetch the current user's profile.
  - **Form Submission**: Handles form submission to update the user's profile using the `authApi` module.

### `TaskDetailPage.jsx`
- **Description**: Displays detailed information about a specific task, including its status, priority, due date, title, and description. It fetches the task data from an API endpoint using the `taskId` obtained from the URL parameters.
- **Props**: None
- **State**:
  - `task`: The task object.
  - `loading`: A boolean indicating whether the task data is being fetched.
  - `error`: An error object if the task data fetch fails.
- **Interactions**:
  - **Data Fetching**: Fetches task data from the API using the `tasksApi` module.
  - **Comments**: Integrates the `CommentList` component to display and manage comments for the task.

### `TasksPage.jsx`
- **Description**: Displays a list of tasks and allows users to filter tasks by project and search term. It also provides a modal form for creating new tasks.
- **Props**: None
- **State**:
  - `tasks`: An array of task objects.
  - `isModalOpen`: A boolean indicating whether the task creation modal is open.
  - `searchTerm`: A string to filter tasks by title.
  - `selectedProject`: The ID of the selected project to filter tasks.
- **Interactions**:
  - **Data Fetching**: Uses the `useTasks` hook to fetch and manage task data.
  - **Modal**: Manages the state of the task creation modal and handles form submission to create new tasks.
  - **Filtering**: Provides options to filter tasks by project and search term.

## Task and Project Components

### `ProjectCard.jsx`
- **Description**: Displays a card for a project, including the project's name, a truncated description, and an archived status if applicable. The card is a clickable link that navigates to the project's detail page.
- **Props**:
  - `project`: The project object.
- **State**: None
- **Interactions**:
  - **Navigation**: Links to the project's detail page using `react-router-dom`.

### `ProjectSettings.jsx`
- **Description**: Displays and updates the settings of a project, including fields for the project's name, description, and archived status. It uses a form to collect user input and calls an `updateProject` function to save changes.
- **Props**:
  - `project`: The project object.
  - `onUpdate`: A callback function to handle project updates.
- **State**:
  - `name`: The project's name.
  - `description`: The project's description.
  - `archived`: A boolean indicating whether the project is archived.
- **Interactions**:
  - **Form Submission**: Handles form submission to update the project using the `projectsApi` module.

### `TaskCard.jsx`
- **Description**: Displays a card for a task, including its title, status, priority, due date, and assignee. The card is a clickable link that navigates to the task's detail page.
- **Props**:
  - `task`: The task object.
- **State**: None
- **Interactions**:
  - **Navigation**: Links to the task's detail page using `react-router-dom`.

### `TaskDetail.jsx`
- **Description**: Displays detailed information about a specific task, including its status, priority, due date, title, and description. It fetches the task data from an API endpoint using the `taskId` obtained from the URL parameters.
- **Props**: None
- **State**:
  - `task`: The task object.
  - `loading`: A boolean indicating whether the task data is being fetched.
  - `error`: An error object if the task data fetch fails.
- **Interactions**:
  - **Data Fetching**: Fetches task data from the API using the `tasksApi` module.
  - **Comments**: Integrates the `CommentList` component to display and manage comments for the task.

### `TaskForm.jsx`
- **Description**: A form for creating or editing a task, including fields for the task's title, description, priority, status, and due date. It handles form submission and provides a cancel button to close the form.
- **Props**:
  - `initialValues`: An object containing initial values for the form fields.
  - `onSubmit`: A callback function to handle form submission.
  - `onCancel`: A callback function to handle form cancellation.
- **State**:
  - `title`: The task's title.
  - `description`: The task's description.
  - `priority`: The task's priority.
  - `status`: The task's status.
  - `dueDate`: The task's due date.
- **Interactions**:
  - **Form Submission**: Handles form submission to create or update a task using the `tasksApi` module.

### `CommentList.jsx`
- **Description**: Displays a list of comments for a given task and allows users to add new comments. It fetches comments from an API and updates the list when new comments are posted.
- **Props**:
  - `taskId`: The ID of the task.
- **State**:
  - `comments`: An array of comment objects.
  - `newComment`: The text of the new comment being added.
  - `loading`: A boolean indicating whether the comments are being fetched.
  - `error`: An error object if the comments fetch fails.
- **Interactions**:
  - **Data Fetching**: Fetches comments from the API using the `tasksApi` module.
  - **Form Submission**: Handles form submission to add new comments using the `tasksApi` module.

## UI Components

### `Button.jsx`
- **Description**: A reusable button component that can be styled with different variants and sizes.
- **Props**:
  - `children`: The content to be displayed inside the button.
  - `variant`: The variant of the button (e.g., primary, secondary).
  - `size`: The size of the button (e.g., small, medium, large).
  - `className`: Additional class names to be applied to the button.
- **State**: None
- **Interactions**: None

### `Badge.jsx`
- **Description**: A reusable badge component that can be styled with different variants such as default, success, warning, danger, and info.
- **Props**:
  - `children`: The content to be displayed inside the badge.
  - `variant`: The variant of the badge (e.g., default, success, warning, danger, info).
- **State**: None
- **Interactions**: None

### `Modal.jsx`
- **Description**: A modal component that displays a centered dialog when the `open` prop is true. It includes a close button and a title, and can render any children components passed to it.
- **Props**:
  - `open`: A boolean indicating whether the modal is open.
  - `title`: The title of the modal.
  - `children`: The content to be displayed inside the modal.
  - `onClose`: A callback function to handle the modal close event.
- **State**: None
- **Interactions**:
  - **Close Button**: Closes the modal when the close button is clicked.
  - **Outside Click**: Closes the modal when the user clicks outside the modal content.

### `Spinner.jsx`
- **Description**: A spinner component that displays a spinning circle to indicate loading states. It accepts a `className` prop to allow for additional styling.
- **Props**:
  - `className`: Additional class names to be applied to the spinner.
- **State**: None
- **Interactions**: None

## Utility Components

### `authUtils.js`
- **Description**: Utility functions for managing authentication sessions in the frontend application.
- **Functions**:
  - `saveSession`: Saves the authentication token, user object, and refresh token to `localStorage`.
  - `clearSession`: Clears the authentication token, user object, and refresh token from `localStorage`.
  - `getToken`: Retrieves the authentication token from `localStorage`.
  - `getRefreshToken`: Retrieves the refresh token from `localStorage`.
  - `getStoredUser`: Retrieves the user object from `localStorage`, parsing it from JSON if it exists.

### `formatters.js`
- **Description**: Utility functions for formatting dates, priorities, and statuses.
- **Functions**:
  - `formatDate`: Formats a given date object or string into a short date format.
  - `formatRelative`: Formats a given date object or string into a relative time format based on the current time.
  - `priorityLabel`: Formats a given priority string, capitalizing the first letter and defaulting to 'Medium' if undefined.
  - `statusLabel`: Formats a given status string, replacing underscores with spaces, capitalizing each word, and defaulting to 'Open' if undefined.

### `analytics.js`
- **Description**: Utility functions for tracking user events and identifying users in Mixpanel and Google Analytics.
- **Functions**:
  - `trackEvent`: Tracks an event in Mixpanel and Google Analytics, checking if the window object and analytics libraries are available.
  - `identify`: Identifies a user in Mixpanel and Google Analytics, checking if the window object and analytics libraries are available.

This overview covers the key React components used in the frontend of the TaskFlow application, including their props, state, and interactions with the backend. Each component plays a crucial role in providing a seamless and functional user experience.

---