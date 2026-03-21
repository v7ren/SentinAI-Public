# Overview

## What is TaskFlow?

TaskFlow is a comprehensive project management tool designed to streamline task and project management for teams and organizations. It provides a robust set of features to manage projects, tasks, user profiles, and notifications, all while ensuring secure and efficient operations.

## Main Components

### Backend
- **Server Setup (`server.js`)**: Sets up and starts a Node.js server using Express. It listens on a specified port (default 3001) and configures middleware and routes.
- **Database Connection (`db.js`)**: Manages the PostgreSQL database connection pool and provides a query function for executing SQL queries.
- **Controllers**: Handle specific business logic and HTTP requests.
  - **Project Controller (`projectController.js`)**: Manages CRUD operations for projects.
  - **Task Controller (`taskController.js`)**: Manages CRUD operations for tasks, including comments.
  - **User Controller (`userController.js`)**: Handles user profile retrieval and updates.
  - **Auth Controller (`authController.js`)**: Manages user authentication, registration, and password reset.
  - **Report Controller (`reportController.js`)**: Generates PDF reports for projects.
  - **Import Controller (`importController.js`)**: Imports tasks from XML and CSV files.
  - **Admin Controller (`adminController.js`)**: Provides administrative functionalities like managing users and billing.
  - **Notification Controller (`notificationController.js`)**: Manages user notifications and preferences.
  - **Attachment Controller (`attachmentController.js`)**: Manages task attachments, including uploading, downloading, and deleting.
- **Models**: Define database schemas and operations.
  - **Project Model (`projectModel.js`)**: Manages project data.
  - **User Model (`userModel.js`)**: Manages user data.
  - **Task Model (`taskModel.js`)**: Manages task data.
  - **Org Model (`orgModel.js`)**: Manages organization and member data.
- **Services**: Provide utility functions for specific tasks.
  - **Email Service (`emailService.js`)**: Sends emails using SendGrid.
  - **Notification Service (`notificationService.js`)**: Manages user notifications.
  - **Report Service (`reportService.js`)**: Generates HTML and PDF reports.
  - **Stripe Service (`stripeService.js`)**: Interacts with the Stripe API for billing.
- **Middlewares**: Handle cross-cutting concerns like authentication, rate limiting, and error handling.
  - **Authenticate (`authenticate.js`)**: Verifies JWT tokens and attaches user information to the request.
  - **Authorize (`authorize.js`)**: Checks user roles and authorizes access.
  - **Rate Limiter (`rateLimiter.js`)**: Limits the rate of report generation requests.
  - **Error Handler (`errorHandler.js`)**: Logs errors and sends JSON responses.
  - **Upload (`upload.js`)**: Configures file upload using Multer.
- **Utils**: Provide utility functions for common tasks.
  - **Logger (`logger.js`)**: Formats and logs messages.
  - **Token Utils (`tokenUtils.js`)**: Generates and verifies JWT tokens.
  - **Validators (`validators.js`)**: Validates and sanitizes strings.
  - **Merge Objects (`mergeObjects.js`)**: Merges objects deeply.
  - **Formatters (`formatters.js`)**: Formats dates and labels.
  - **Auth Utils (`authUtils.js`)**: Manages authentication sessions in local storage.

### Frontend
- **Main Application (`App.jsx`)**: Sets up routing for various pages, including public and private routes.
- **API Client (`client.js`)**: Configures an Axios client for making HTTP requests to the backend API.
- **Components**: Reusable UI elements.
  - **Navbar (`Navbar.jsx`)**: Displays a navigation bar with links and a logout button.
  - **Sidebar (`Sidebar.jsx`)**: Displays navigation links and user information.
  - **Page Wrapper (`PageWrapper.jsx`)**: Combines a sidebar, navbar, and main content area.
  - **Project Card (`ProjectCard.jsx`)**: Displays a card for a project.
  - **Task Card (`TaskCard.jsx`)**: Displays a card for a task.
  - **Task Form (`TaskForm.jsx`)**: Form for creating or editing tasks.
  - **Task Detail (`TaskDetail.jsx`)**: Displays detailed information about a task.
  - **Comment List (`CommentList.jsx`)**: Displays a list of comments for a task.
  - **Button (`Button.jsx`)**: Reusable button component.
  - **Spinner (`Spinner.jsx`)**: Displays a loading spinner.
  - **Badge (`Badge.jsx`)**: Displays a styled badge.
  - **Modal (`Modal.jsx`)**: Displays a modal dialog.
- **Pages**: Top-level components for different routes.
  - **Dashboard Page (`DashboardPage.jsx`)**: Displays a dashboard with project and task statistics.
  - **Login Page (`LoginPage.jsx`)**: Handles user login.
  - **Register Page (`RegisterPage.jsx`)**: Handles user registration.
  - **Admin Page (`AdminPage.jsx`)**: Displays administrative functionalities.
  - **Project Detail Page (`ProjectDetailPage.jsx`)**: Displays detailed information about a project.
  - **Projects Page (`ProjectsPage.jsx`)**: Displays a list of projects.
  - **Settings Page (`SettingsPage.jsx`)**: Allows users to update their profile.
  - **Task Detail Page (`TaskDetailPage.jsx`)**: Displays detailed information about a task.
  - **Tasks Page (`TasksPage.jsx`)**: Displays a list of tasks.
  - **Landing Page (`LandingPage.jsx`)**: Main landing page with navigation and features.
  - **Not Found Page (`NotFoundPage.jsx`)**: Displays a 404 error message.
- **Hooks**: Custom hooks for state management and API interactions.
  - **useAuth (`useAuth.js`)**: Manages authentication state.
  - **useProjects (`useProjects.js`)**: Manages project state and API interactions.
  - **useTasks (`useTasks.js`)**: Manages task state and API interactions.
- **Context**: Provides global state management.
  - **Auth Context (`AuthContext.jsx`)**: Manages authentication state and functions.
- **Utils**: Utility functions for frontend tasks.
  - **Analytics (`analytics.js`)**: Tracks user events and identifies users in Mixpanel and Google Analytics.
  - **Auth Utils (`authUtils.js`)**: Manages authentication sessions in local storage.

## Typical Usage Scenario

1. **User Registration and Login**:
   - A new user visits the landing page and clicks on the "Register" link.
   - The user fills out the registration form and submits it.
   - The `RegisterPage` component sends a POST request to the backend's `authController` to create a new user and organization.
   - Upon successful registration, the user is redirected to the login page.
   - The user logs in using the `LoginPage` component, which sends a POST request to the backend's `authController` to authenticate the user and obtain access and refresh tokens.

2. **Project Management**:
   - After logging in, the user is redirected to the dashboard.
   - The `DashboardPage` component fetches project and task statistics from the backend using the `useProjects` hook.
   - The user navigates to the projects page to view a list of projects.
   - The `ProjectsPage` component fetches project data from the backend using the `useProjects` hook and displays a list of project cards.
   - The user clicks on a project card to view detailed information about the project.
   - The `ProjectDetailPage` component fetches project data from the backend and displays it, including a list of tasks and project settings.

3. **Task Management**:
   - The user navigates to the tasks page to view a list of tasks.
   - The `TasksPage` component fetches task data from the backend using the `useTasks` hook and displays a list of task cards.
   - The user clicks on a task card to view detailed information about the task.
   - The `TaskDetailPage` component fetches task data from the backend and displays it, including comments and a form to add new comments.
   - The user can create new tasks or update existing tasks using the `TaskForm` component.

4. **Admin Functions**:
   - An admin user navigates to the admin page to manage users and billing.
   - The `AdminPage` component fetches user data from the backend using the `useAuth` hook and displays a table of users.
   - The admin can delete users or view a billing overview using the `adminController` endpoints.

## Where to Look Next

- **Backend**:
  - **Controllers**: For detailed information on how specific business logic is handled, see the controller files like `projectController.js`, `taskController.js`, and `authController.js`.
  - **Models**: For database schema and operations, see the model files like `projectModel.js`, `userModel.js`, and `taskModel.js`.
  - **Services**: For utility functions and external API interactions, see the service files like `emailService.js`, `notificationService.js`, and `stripeService.js`.
  - **Middlewares**: For cross-cutting concerns, see the middleware files like `authenticate.js`, `authorize.js`, and `errorHandler.js`.
  - **Utils**: For common utility functions, see the utils files like `logger.js`, `tokenUtils.js`, and `validators.js`.

- **Frontend**:
  - **Components**: For reusable UI elements, see the component files like `Navbar.jsx`, `Sidebar.jsx`, and `TaskCard.jsx`.
  - **Pages**: For top-level components for different routes, see the page files like `DashboardPage.jsx`, `LoginPage.jsx`, and `ProjectsPage.jsx`.
  - **Hooks**: For custom hooks for state management and API interactions, see the hook files like `useAuth.js`, `useProjects.js`, and `useTasks.js`.
  - **Context**: For global state management, see the context file `AuthContext.jsx`.
  - **Utils**: For utility functions, see the utils files like `analytics.js` and `authUtils.js`.

For more detailed documentation on specific components and functionalities, refer to the respective sections in the documentation.

---

# Architecture and Data Flow

## Main Architectural Components

The TaskFlow application is built using a client-server architecture, with a React-based frontend and a Node.js backend. The main components of the system are:

### Backend Components

1. **Server**
   - **File**: `taskflow\backend\server.js`
   - **Description**: Sets up and starts a Node.js server using an Express application. It configures the server to listen on a specified port (default 3001) and initializes the application.
   - **Key Functions**:
     - `app.listen`: Starts the Express application and listens on the specified port.

2. **Database Configuration**
   - **File**: `taskflow\backend\config\db.js`
   - **Description**: Sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries. It uses environment variables for configuration, with fallbacks for local development.
   - **Key Functions**:
     - `pool`: A PostgreSQL connection pool instance.
     - `query`: A function that takes SQL text and parameters, and executes the query using the connection pool.

3. **Controllers**
   - **Project Controller**
     - **File**: `taskflow\backend\src\controllers\projectController.js`
     - **Description**: Manages project-related operations such as listing, retrieving, creating, updating, and deleting projects.
     - **Key Endpoints**:
       - `GET /projects`: Lists projects for a specific organization.
       - `GET /projects/:projectId`: Retrieves a single project by ID.
       - `POST /projects`: Creates a new project.
       - `PUT /projects/:projectId`: Updates an existing project.
       - `DELETE /projects/:projectId`: Deletes a project.
   - **Task Controller**
     - **File**: `taskflow\backend\src\controllers\taskController.js`
     - **Description**: Manages task-related operations such as listing, retrieving, creating, updating, and deleting tasks, as well as managing comments.
     - **Key Endpoints**:
       - `GET /tasks`: Lists tasks for a specific project or across an organization.
       - `GET /tasks/:taskId`: Retrieves a single task by ID.
       - `POST /tasks`: Creates a new task.
       - `PUT /tasks/:taskId`: Updates an existing task.
       - `DELETE /tasks/:taskId`: Deletes a task.
   - **Report Controller**
     - **File**: `taskflow\backend\src\controllers\reportController.js`
     - **Description**: Handles the generation of PDF reports for projects.
     - **Key Endpoints**:
       - `GET /api/reports/:projectId/pdf`: Generates a PDF report for a specific project.
   - **Import Controller**
     - **File**: `taskflow\backend\src\controllers\importController.js`
     - **Description**: Manages the import of tasks from XML and CSV formats into a project.
     - **Key Endpoints**:
       - `POST /api/projects/:projectId/import/xml`: Imports tasks from XML data.
       - `POST /api/projects/:projectId/import/csv`: Imports tasks from CSV data.
   - **Admin Controller**
     - **File**: `taskflow\backend\src\controllers\adminController.js`
     - **Description**: Manages administrative tasks such as retrieving all users, deleting a user, and getting a billing overview.
     - **Key Endpoints**:
       - `GET /admin/users`: Retrieves all users.
       - `DELETE /admin/users/:id`: Deletes a user by ID.
       - `GET /admin/billing`: Retrieves a billing overview.
   - **Notification Controller**
     - **File**: `taskflow\backend\src\controllers\notificationController.js`
     - **Description**: Manages notifications, including listing notifications, marking them as read, and managing user preferences.
     - **Key Endpoints**:
       - `GET /notifications`: Lists notifications for a user.
       - `PUT /notifications/:id/read`: Marks a specific notification as read.
       - `GET /notifications/preferences`: Retrieves notification preferences for a user.
       - `POST /notifications/preferences`: Updates notification preferences for a user.
   - **User Controller**
     - **File**: `taskflow\backend\src\controllers\userController.js`
     - **Description**: Manages user profile operations such as retrieving and updating user profiles.
     - **Key Endpoints**:
       - `GET /profile`: Retrieves the user profile for the authenticated user.
       - `PUT /profile`: Updates the user profile for the authenticated user.
   - **Attachment Controller**
     - **File**: `taskflow\backend\src\controllers\attachmentController.js`
     - **Description**: Manages task attachments, including listing, uploading, downloading, and removing attachments.
     - **Key Endpoints**:
       - `GET /api/tasks/:taskId/attachments`: Lists all attachments for a given task ID.
       - `POST /api/tasks/:taskId/attachments`: Uploads a new attachment for a given task ID.
       - `GET /api/tasks/:taskId/attachments/:attachmentId`: Downloads an attachment by its ID.
       - `DELETE /api/tasks/:taskId/attachments/:attachmentId`: Removes an attachment by its ID.

4. **Middleware**
   - **Authentication Middleware**
     - **File**: `taskflow\backend\src\middleware\authenticate.js`
     - **Description**: Authenticates HTTP requests by verifying a JWT token in the authorization header.
     - **Key Functions**:
       - `authenticate`: Middleware function that checks the authorization header for a valid JWT token and attaches user information to the request object.
   - **Authorization Middleware**
     - **File**: `taskflow\backend\src\middleware\authorize.js`
     - **Description**: Authorizes user roles in an HTTP request handling chain.
     - **Key Functions**:
       - `authorize`: Middleware function that checks if the user has the required roles to access a resource.
   - **Error Handler Middleware**
     - **File**: `taskflow\backend\src\middleware\errorHandler.js`
     - **Description**: Handles errors in the Express.js application by logging them and sending a JSON response.
     - **Key Functions**:
       - `errorHandler`: Middleware function that logs the error and sends a JSON response with the error details and status code.
   - **Rate Limiter Middleware**
     - **File**: `taskflow\backend\src\middleware\rateLimiter.js`
     - **Description**: Limits the rate of report generation requests to prevent abuse of the PDF export feature.
     - **Key Functions**:
       - `reportLimiter`: Middleware to limit the rate of report generation requests to 10 per minute.
   - **File Upload Middleware**
     - **File**: `taskflow\backend\src\middleware\upload.js`
     - **Description**: Configures and exports a multer middleware for handling file uploads.
     - **Key Functions**:
       - `upload`: Multer middleware instance configured for file uploads, setting the upload directory and file naming.

5. **Models**
   - **Project Model**
     - **File**: `taskflow\backend\src\models\projectModel.js`
     - **Description**: Defines functions for interacting with the 'projects' table in the database.
     - **Key Functions**:
       - `find`, `create`, `update`, `remove`: Functions to find, create, update, and delete project records.
   - **User Model**
     - **File**: `taskflow\backend\src\models\userModel.js`
     - **Description**: Defines functions for interacting with the 'users' table in the database.
     - **Key Functions**:
       - `find`, `create`, `update`: Functions to find, create, and update user records.
   - **Task Model**
     - **File**: `taskflow\backend\src\models\taskModel.js`
     - **Description**: Defines functions for interacting with the 'tasks' table in the database.
     - **Key Functions**:
       - `find`, `create`, `update`, `remove`: Functions to find, create, update, and delete task records.
   - **Organization Model**
     - **File**: `taskflow\backend\src\models\orgModel.js`
     - **Description**: Defines functions for interacting with the 'orgs' and 'org_members' tables in the database.
     - **Key Functions**:
       - `findById`, `create`, `addMember`, `getMembers`: Functions to find an organization, create a new organization, add a member to an organization, and retrieve members of an organization.

6. **Services**
   - **Email Service**
     - **File**: `taskflow\backend\src\services\emailService.js`
     - **Description**: Provides functions for sending emails using SendGrid.
     - **Key Functions**:
       - `sendInvite`: Sends an invitation email to a user.
       - `sendPasswordReset`: Sends a password reset email to a user.
   - **Notification Service**
     - **File**: `taskflow\backend\src\services\notificationService.js`
     - **Description**: Provides functions to create, retrieve, and manage user notifications and preferences.
     - **Key Functions**:
       - `create`, `getForUser`, `markRead`, `getPreferences`, `updatePreferences`: Functions to create, retrieve, mark as read, and manage notification preferences.
   - **Report Service**
     - **File**: `taskflow\backend\src\services\reportService.js`
     - **Description**: Provides functions for generating HTML and PDF reports from task data.
     - **Key Functions**:
       - `generateReportHtml`, `generatePdf`: Functions to generate an HTML report and convert it to a PDF.
   - **Stripe Service**
     - **File**: `taskflow\backend\src\services\stripeService.js`
     - **Description**: Provides functions to interact with the Stripe API for customer management, checkout sessions, billing portal sessions, and webhook event construction.
     - **Key Functions**:
       - `createCustomer`, `createCheckoutSession`, `createBillingPortalSession`, `constructEvent`: Functions to create customers, checkout sessions, billing portal sessions, and construct webhook events.

7. **Utilities**
   - **Logger**
     - **File**: `taskflow\backend\src\utils\logger.js`
     - **Description**: Defines a simple logging utility that formats log entries as JSON objects and outputs them to the console.
     - **Key Functions**:
       - `info`, `warn`, `error`: Functions to log informational, warning, and error messages with optional metadata.
   - **Token Utilities**
     - **File**: `taskflow\backend\src\utils\tokenUtils.js`
     - **Description**: Provides functions for generating and verifying JWT access and refresh tokens.
     - **Key Functions**:
       - `tokenUtils`: Functions to sign and verify JWT access and refresh tokens.
   - **Validators**
     - **File**: `taskflow\backend\src\utils\validators.js`
     - **Description**: Contains utility functions for validating and sanitizing strings.
     - **Key Functions**:
       - `isEmail`, `isNonEmptyString`, `sanitizeString`: Functions to validate email format, check for non-empty strings, and sanitize strings.

### Frontend Components

1. **Main Application**
   - **File**: `taskflow\frontend\src\App.jsx`
   - **Description**: The main entry point of the React application, setting up routing for various pages, including public and private routes.
   - **Key Components**:
     - `App`: Main application component that sets up routing for different pages.

2. **API Client**
   - **File**: `taskflow\frontend\src\api\client.js`
   - **Description**: Sets up an Axios client for making HTTP requests to the backend API.
   - **Key Functions**:
     - `client`: Axios client instance configured with interceptors for adding authentication tokens and handling unauthorized responses.

3. **Pages**
   - **Dashboard Page**
     - **File**: `taskflow\frontend\src\pages\DashboardPage.jsx`
     - **Description**: Displays a dashboard with statistics about open tasks, overdue tasks, and projects.
   - **Login Page**
     - **File**: `taskflow\frontend\src\pages\LoginPage.jsx`
     - **Description**: Handles user login with form fields for email and password.
   - **Register Page**
     - **File**: `taskflow\frontend\src\pages\RegisterPage.jsx`
     - **Description**: Handles user registration with form fields for full name, email, and password.
   - **Admin Page**
     - **File**: `taskflow\frontend\src\pages\AdminPage.jsx`
     - **Description**: Serves as a page for administrative tasks, displaying a table of users.
   - **Project Detail Page**
     - **File**: `taskflow\frontend\src\pages\ProjectDetailPage.jsx`
     - **Description**: Displays detailed information about a specific project.
   - **Projects Page**
     - **File**: `taskflow\frontend\src\pages\ProjectsPage.jsx`
     - **Description**: Displays a list of projects and allows users to create new projects.
   - **Settings Page**
     - **File**: `taskflow\frontend\src\pages\SettingsPage.jsx`
     - **Description**: Allows users to update their full name.
   - **Task Detail Page**
     - **File**: `taskflow\frontend\src\pages\TaskDetailPage.jsx`
     - **Description**: Displays detailed information about a specific task.
   - **Tasks Page**
     - **File**: `taskflow\frontend\src\pages\TasksPage.jsx`
     - **Description**: Displays a list of tasks and allows users to filter tasks by project and search term.
   - **Landing Page**
     - **File**: `taskflow\frontend\src\pages\LandingPage.jsx`
     - **Description**: Serves as the main landing page for the TaskFlow application.
   - **Not Found Page**
     - **File**: `taskflow\frontend\src\pages\NotFoundPage.jsx`
     - **Description**: Displays a 404 error message and a link to return to the home page.

4. **Components**
   - **Navbar**
     - **File**: `taskflow\frontend\src\components\Layout\Navbar.jsx`
     - **Description**: Displays a navigation bar with links to the dashboard and settings pages, and a logout button.
   - **Sidebar**
     - **File**: `taskflow\frontend\src\components\Layout\Sidebar.jsx`
     - **Description**: Displays navigation links and user information.
   - **Page Wrapper**
     - **File**: `taskflow\frontend\src\components\Layout\PageWrapper.jsx`
     - **Description**: Serves as a layout container for other components.
   - **Project Card**
     - **File**: `taskflow\frontend\src\components\Projects\ProjectCard.jsx`
     - **Description**: Displays a card for a project with its name, description, and archived status.
   - **Task Card**
     - **File**: `taskflow\frontend\src\components\Tasks\TaskCard.jsx`
     - **Description**: Displays a card for a task with its title, status, priority, due date, and assignee.
   - **Task Detail**
     - **File**: `taskflow\frontend\src\components\Tasks\TaskDetail.jsx`
     - **Description**: Displays detailed information about a specific task, including comments.
   - **Task Form**
     - **File**: `taskflow\frontend\src\components\Tasks\TaskForm.jsx`
     - **Description**: Allows users to create or edit a task.
   - **Comment List**
     - **File**: `taskflow\frontend\src\components\Tasks\CommentList.jsx`
     - **Description**: Displays a list of comments for a given task and allows users to add new comments.
   - **Button**
     - **File**: `taskflow\frontend\src\components\UI\Button.jsx`
     - **Description**: A reusable button component.
   - **Spinner**
     - **File**: `taskflow\frontend\src\components\UI\Spinner.jsx`
     - **Description**: A reusable loading spinner component.
   - **Badge**
     - **File**: `taskflow\frontend\src\components\UI\Badge.jsx`
     - **Description**: A reusable badge component with different styles.
   - **Modal**
     - **File**: `taskflow\frontend\src\components\UI\Modal.jsx`
     - **Description**: A reusable modal dialog component.

5. **Hooks**
   - **Auth Hook**
     - **File**: `taskflow\frontend\src\hooks\useAuth.js`
     - **Description**: Manages authentication state in a React application.
   - **Tasks Hook**
     - **File**: `taskflow\frontend\src\hooks\useTasks.js`
     - **Description**: Manages the state and lifecycle of tasks for a given project.
   - **Projects Hook**
     - **File**: `taskflow\frontend\src\hooks\useProjects.js`
     - **Description**: Manages the state and lifecycle of projects data.

6. **Context**
   - **Auth Context**
     - **File**: `taskflow\frontend\src\context\AuthContext.jsx`
     - **Description**: Provides state management and functions for user login, registration, and logout.

7. **Utilities**
   - **Analytics**
     - **File**: `taskflow\frontend\src\utils\analytics.js`
     - **Description**: Contains utility functions for tracking user events and identifying users in Mixpanel and Google Analytics.
   - **Auth Utilities**
     - **File**: `taskflow\frontend\src\utils\authUtils.js`
     - **Description**: Contains utility functions for managing authentication sessions in the frontend.
   - **Formatters**
     - **File**: `taskflow\frontend\src\utils\formatters.js`
     - **Description**: Contains utility functions for formatting dates, priorities, and statuses.

## Data and Control Flow

### Backend Flow

1. **Request Handling**
   - The Node.js server listens for incoming HTTP requests.
   - Requests are routed to the appropriate controller based on the endpoint.
   - Middleware functions (authentication, authorization, error handling, rate limiting) are applied as needed.

2. **Database Interactions**
   - Controllers interact with the database using models to perform CRUD operations.
   - The `db.js` file sets up the PostgreSQL connection pool and provides a query function.
   - Models define functions for interacting with specific database tables.

3. **Service Layer**
   - Services provide additional functionality, such as generating reports, sending emails, and interacting with external APIs (e.g., Stripe).
   - Controllers can call service functions to perform these tasks.

4. **Response Handling**
   - Controllers handle the business logic and prepare the response data.
   - The response is sent back to the client with the appropriate HTTP status code and data.

### Frontend Flow

1. **Application Initialization**
   - The `App` component sets up routing and authentication context.
   - The `AuthProvider` component manages the authentication state and provides authentication functions.

2. **API Interactions**
   - The Axios client is configured to handle HTTP requests to the backend API.
   - Custom hooks (e.g., `useTasks`, `useProjects`) manage the state and lifecycle of data fetched from the API.

---

# Key Components

This section provides an overview of the main components of the TaskFlow application, including the backend server, database, and frontend components. Each component plays a crucial role in the overall functionality of the application.

## Backend Server

### Server Setup
- **File**: `taskflow/backend/server.js`
- **Summary**: This file sets up and starts a Node.js server using an Express application defined in `./src/app`. It configures the server to listen on a specified port, defaulting to 3001 if not provided in the environment variables.
- **Key Functions**:
  - `app.listen`: Starts the Express application and listens on the specified port.
- **Tags**: `config`, `network`, `process`, `logging`

### Application Configuration
- **File**: `taskflow/backend/src/app.js`
- **Summary**: This file sets up an Express.js application, configures middleware for JSON and text parsing, serves static files from the `uploads` directory, and mounts various API routes for authentication, tasks, projects, users, attachments, reports, imports, notifications, and admin functionalities. It also includes a health check endpoint and an error handler middleware.
- **Key Functions**:
  - `GET /api/v1/health`: Endpoint to check the health of the application, returning a JSON object with a success status and timestamp.
- **Tags**: `network`, `file_io`, `auth`, `db`, `other`

## Database

### Database Configuration
- **File**: `taskflow/backend/config/db.js`
- **Summary**: This file sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries. It uses environment variables for configuration, with fallbacks for local development.
- **Key Functions**:
  - `pool`: A PostgreSQL connection pool instance that can be used to execute queries.
  - `query`: A function that takes SQL text and parameters, and executes the query using the connection pool.
- **Tags**: `db`, `config`

### Models
- **Project Model**
  - **File**: `taskflow/backend/src/models/projectModel.js`
  - **Summary**: Defines a set of asynchronous functions for interacting with a `projects` table in the database, including methods to find, create, update, and delete project records.
  - **Key Functions**:
    - `find`, `create`, `update`, `remove`
  - **Tags**: `db`

- **User Model**
  - **File**: `taskflow/backend/src/models/userModel.js`
  - **Summary**: Defines a set of asynchronous functions for interacting with a `users` table in the database, including operations to find, create, and update user records.
  - **Key Functions**:
    - `find`, `create`, `update`
  - **Tags**: `db`

- **Task Model**
  - **File**: `taskflow/backend/src/models/taskModel.js`
  - **Summary**: Defines a set of asynchronous functions for interacting with a `tasks` table in the database, including finding, creating, updating, and deleting tasks. It also includes a function to find tasks by project, which joins with a `users` table to include the assignee's name.
  - **Key Functions**:
    - `find`, `create`, `update`, `remove`, `findByProject`
  - **Tags**: `db`

- **Organization Model**
  - **File**: `taskflow/backend/src/models/orgModel.js`
  - **Summary**: Defines a set of functions for interacting with the `orgs` and `org_members` tables in the database. It provides methods to find an organization by ID, create a new organization, add a member to an organization, and retrieve the members of an organization.
  - **Key Functions**:
    - `findById`, `create`, `addMember`, `getMembers`
  - **Tags**: `db`

## Frontend Components

### Main Application
- **File**: `taskflow/frontend/src/App.jsx`
- **Summary**: This file defines the main application component for a React-based frontend. It sets up routing for various pages, including public and private routes. Private routes require user authentication, redirecting unauthenticated users to the login page.
- **Key Components**:
  - `App`: The main entry point of the application, which sets up routing for different pages.
- **Tags**: `auth`, `network`, `other`

### Authentication
- **File**: `taskflow/frontend/src/context/AuthContext.jsx`
- **Summary**: This file defines an authentication context for a React application, providing state management and functions for user login, registration, and logout. It uses a custom API for authentication and utility functions to manage session storage.
- **Key Functions**:
  - `AuthProvider`: A React component that provides authentication context to its children.
  - `useAuth`: A custom hook that allows components to access the authentication context.
- **Tags**: `auth`, `network`

### API Client
- **File**: `taskflow/frontend/src/api/client.js`
- **Summary**: This file sets up an Axios client for making HTTP requests to a backend API. It includes interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to a login page.
- **Key Functions**:
  - `client`: The Axios client instance that is configured with interceptors and exported for use in other parts of the application.
- **Tags**: `auth`, `network`, `logging`

### Pages
- **Dashboard Page**
  - **File**: `taskflow/frontend/src/pages/DashboardPage.jsx`
  - **Summary**: This file defines a React component named `DashboardPage`, which displays a dashboard with statistics about open tasks, overdue tasks, and projects. It also shows a list of recent tasks and provides a button to navigate to the task creation page.
  - **Key Functions**:
    - `DashboardPage`: A React component that displays a dashboard with project and task statistics.
  - **Tags**: `ui`, `state_management`, `routing`

- **Login Page**
  - **File**: `taskflow/frontend/src/pages/LoginPage.jsx`
  - **Summary**: This file defines a React component for a login page, which includes form fields for email and password, and handles the submission of login credentials to authenticate the user. Upon successful login, the user is redirected to a specified or default page.
  - **Key Functions**:
    - `LoginPage`: A React component that serves as the entry point for the login page, rendering the login form and handling user authentication.
  - **Tags**: `auth`, `network`

- **Register Page**
  - **File**: `taskflow/frontend/src/pages/RegisterPage.jsx`
  - **Summary**: This file defines a React component for a user registration page. It handles user input for full name, email, and password, and attempts to register the user with the provided credentials. Upon successful registration, the user is redirected to the dashboard.
  - **Key Functions**:
    - `RegisterPage`: A React component that serves as the registration page for the application.
  - **Tags**: `auth`, `network`

- **Projects Page**
  - **File**: `taskflow/frontend/src/pages/ProjectsPage.jsx`
  - **Summary**: This file defines a React component named `ProjectsPage`, which displays a list of projects and allows users to create new projects through a modal form. It uses the `useProjects` hook to fetch and manage project data.
  - **Key Functions**:
    - `ProjectsPage`: A React component that displays a list of projects and includes a modal for creating new projects.
  - **Tags**: `auth`, `network`, `ui`

- **Task Detail Page**
  - **File**: `taskflow/frontend/src/pages/TaskDetailPage.jsx`
  - **Summary**: This file defines a React component named `TaskDetailPage`, which serves as a page for displaying detailed information about a task. It uses a `PageWrapper` component to provide a consistent layout and a `TaskDetail` component to show the task details.
  - **Key Functions**:
    - `TaskDetailPage`: A React component that wraps a `TaskDetail` component inside a `PageWrapper` component with a title 'Task'.
  - **Tags**: `other`

### Layout and UI Components
- **Navbar**
  - **File**: `taskflow/frontend/src/components/Layout/Navbar.jsx`
  - **Summary**: This file defines a React component named `Navbar`, which is a header component displaying a navigation bar with links to the dashboard and settings pages, and a logout button. It uses the `useAuth` hook to manage authentication state.
  - **Key Functions**:
    - `Navbar`: A React component that displays a header with navigation links and a logout button.
  - **Tags**: `auth`, `ui`

- **Sidebar**
  - **File**: `taskflow/frontend/src/components/Layout/Sidebar.jsx`
  - **Summary**: This file defines a Sidebar component for a web application, which displays navigation links and user information. The component uses React and the `react-router-dom` library for routing and navigation. It also uses a custom `useAuth` hook to manage authentication and user roles.
  - **Key Functions**:
    - `Sidebar`: A React component that displays navigation links based on the user's role.
  - **Tags**: `auth`, `ui`

- **Page Wrapper**
  - **File**: `taskflow/frontend/src/components/Layout/PageWrapper.jsx`
  - **Summary**: This file defines a React component named `PageWrapper`, which serves as a layout container for other components. It includes a Sidebar and a Navbar, and it can display a title and children components within the main content area.
  - **Key Functions**:
    - `PageWrapper`: A React component that renders a sidebar, a navbar, and the main content area.
  - **Tags**: `other`

### Utility Functions
- **Formatters**
  - **File**: `taskflow/frontend/src/utils/formatters.js`
  - **Summary**: This file contains utility functions for formatting dates, priorities, and statuses. It exports functions to format dates in a specific format, to format dates relative to the current time, to format priority labels, and to format status labels.
  - **Key Functions**:
    - `formatDate`, `formatRelative`, `priorityLabel`, `statusLabel`
  - **Tags**: `other`

- **Auth Utilities**
  - **File**: `taskflow/frontend/src/utils/authUtils.js`
  - **Summary**: This file contains utility functions for managing authentication sessions in a frontend application. It provides methods to save, clear, and retrieve session data from the browser's localStorage.
  - **Key Functions**:
    - `saveSession`, `clearSession`, `getToken`, `getRefreshToken`, `getStoredUser`
  - **Tags**: `auth`, `storage`

## Conclusion

The TaskFlow application is built with a robust backend server, a PostgreSQL database, and a React-based frontend. The backend handles API requests, database interactions, and authentication, while the frontend provides a user-friendly interface with routing, authentication, and various UI components. Each component is designed to work seamlessly together to provide a comprehensive project management tool.

---

# Authentication and Authorization

This section provides a detailed guide on how authentication and authorization are implemented in the TaskFlow application. It covers the use of JWT tokens, user roles, and session management.

## Overview

The authentication and authorization system in TaskFlow is designed to secure access to various endpoints and ensure that only authenticated and authorized users can perform specific actions. The system uses JSON Web Tokens (JWT) for session management and role-based access control (RBAC) for authorization.

### Key Components

- **JWT Tokens**: Used for session management and user authentication.
- **User Roles**: Define the permissions and access levels of users.
- **Middleware**: Handles token verification, role checking, and error handling.
- **API Endpoints**: Provide functionalities for user registration, login, token refresh, and logout.

## JWT Tokens

### Token Generation and Verification

- **Token Generation**: JWT tokens are generated upon successful user registration or login. The tokens are signed using a secret key and contain the user's ID and role.
- **Token Verification**: Middleware functions verify the JWT token in the `Authorization` header of incoming requests. If the token is valid, user information is attached to the request object.

### Files Involved

- **`taskflow\backend\src\middleware\authenticate.js`**: Contains the `authenticate` middleware function that checks for a valid JWT token and attaches user information to the request object.
- **`taskflow\backend\src\utils\tokenUtils.js`**: Provides utility functions for generating and verifying JWT access and refresh tokens.

### Example Code Snippet

```javascript
// taskflow\backend\src\middleware\authenticate.js
const jwt = require('jsonwebtoken');
const { verifyAccess } = require('../utils/tokenUtils');

const authenticate = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ message: 'No token provided' });
  }

  try {
    const decoded = verifyAccess(token);
    req.user = decoded;
    next();
  } catch (err) {
    console.warn('Invalid token:', err);
    res.status(401).json({ message: 'Invalid token' });
  }
};
```

## User Roles and Authorization

### Role-Based Access Control (RBAC)

- **User Roles**: Users can have different roles such as `admin`, `member`, etc. Each role has specific permissions and access levels.
- **Role Checking**: Middleware functions check if the user has the required role to access a resource. If the user is not authenticated or does not have the required role, an appropriate error response is returned.

### Files Involved

- **`taskflow\backend\src\middleware\authorize.js`**: Contains the `authorize` middleware function that checks if the user has the required role to access a resource.

### Example Code Snippet

```javascript
// taskflow\backend\src\middleware\authorize.js
const authorize = (requiredRole) => (req, res, next) => {
  if (!req.user) {
    return res.status(401).json({ message: 'Unauthorized' });
  }

  if (req.user.role !== requiredRole) {
    return res.status(403).json({ message: 'Forbidden' });
  }

  next();
};
```

## Authentication Endpoints

### User Registration and Login

- **Registration**: Users can register by providing their full name, email, and password. Upon successful registration, a new user and organization are created, and access and refresh tokens are issued.
- **Login**: Users can log in by providing their email and password. If the credentials are valid, access and refresh tokens are issued.

### Files Involved

- **`taskflow\backend\src\controllers\authController.js`**: Contains the implementation of user registration, login, token refresh, password reset, and logout functionalities.
- **`taskflow\backend\src\routes\authRoutes.js`**: Defines the routes for user registration, login, token refresh, password reset, and logout.

### Example Code Snippet

```javascript
// taskflow\backend\src\controllers\authController.js
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { userModel, orgModel } = require('../models');
const { signAccess, signRefresh } = require('../utils/tokenUtils');

const register = async (req, res) => {
  const { fullName, email, password } = req.body;
  const hashedPassword = await bcrypt.hash(password, 10);
  const user = await userModel.create({ fullName, email, password: hashedPassword });
  const org = await orgModel.create({ name: `${fullName}'s Organization`, ownerId: user.id });

  const accessToken = signAccess({ userId: user.id, role: 'member' });
  const refreshToken = signRefresh({ userId: user.id });

  res.status(201).json({ accessToken, refreshToken });
};

const login = async (req, res) => {
  const { email, password } = req.body;
  const user = await userModel.findByEmail(email);

  if (!user || !(await bcrypt.compare(password, user.password))) {
    return res.status(401).json({ message: 'Invalid credentials' });
  }

  const accessToken = signAccess({ userId: user.id, role: user.role });
  const refreshToken = signRefresh({ userId: user.id });

  res.json({ accessToken, refreshToken });
};
```

### Token Refresh and Logout

- **Token Refresh**: Users can refresh their access token by providing a valid refresh token.
- **Logout**: Users can log out by invalidating their refresh token.

### Files Involved

- **`taskflow\backend\src\controllers\authController.js`**: Contains the implementation of token refresh and logout functionalities.
- **`taskflow\backend\src\routes\authRoutes.js`**: Defines the routes for token refresh and logout.

### Example Code Snippet

```javascript
// taskflow\backend\src\controllers\authController.js
const refresh = async (req, res) => {
  const { refreshToken } = req.body;
  const decoded = jwt.verify(refreshToken, process.env.REFRESH_SECRET);
  const user = await userModel.findById(decoded.userId);

  if (!user || user.refreshToken !== refreshToken) {
    return res.status(401).json({ message: 'Invalid refresh token' });
  }

  const accessToken = signAccess({ userId: user.id, role: user.role });
  res.json({ accessToken });
};

const logout = async (req, res) => {
  const { refreshToken } = req.body;
  const user = await userModel.findById(req.user.id);

  if (user.refreshToken === refreshToken) {
    user.refreshToken = null;
    await user.save();
  }

  res.json({ message: 'Logged out successfully' });
};
```

## Frontend Integration

### Authentication Context

- **AuthProvider**: Manages the authentication state and provides functions for user login, registration, and logout.
- **useAuth**: A custom hook that allows components to access the authentication context.

### Files Involved

- **`taskflow\frontend\src\context\AuthContext.jsx`**: Defines the `AuthProvider` and `useAuth` hook for managing authentication state.
- **`taskflow\frontend\src\hooks\useAuth.js`**: Re-exports the `useAuth` hook from `AuthContext`.

### Example Code Snippet

```javascript
// taskflow\frontend\src\context\AuthContext.jsx
import React, { createContext, useState, useEffect } from 'react';
import { authApi } from '../api';

const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        try {
          const response = await authApi.verifyToken(token);
          setUser(response.data.user);
        } catch (error) {
          console.error('Token verification failed:', error);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (credentials) => {
    const response = await authApi.login(credentials);
    localStorage.setItem('accessToken', response.data.accessToken);
    localStorage.setItem('refreshToken', response.data.refreshToken);
    setUser(response.data.user);
  };

  const logout = async () => {
    await authApi.logout();
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export { AuthContext, AuthProvider };
```

### Authentication in Routes

- **Private Routes**: Routes that require user authentication are protected using the `useAuth` hook. Unauthenticated users are redirected to the login page.

### Files Involved

- **`taskflow\frontend\src\App.jsx`**: Sets up routing for various pages, including public and private routes.
- **`taskflow\frontend\src\api\client.js`**: Configures an Axios client for making HTTP requests, including interceptors for adding authentication tokens.

### Example Code Snippet

```javascript
// taskflow\frontend\src\App.jsx
import React from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ProjectsPage from './pages/ProjectsPage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import TasksPage from './pages/TasksPage';
import TaskDetailPage from './pages/TaskDetailPage';
import SettingsPage from './pages/SettingsPage';
import AdminPage from './pages/AdminPage';
import NotFoundPage from './pages/NotFoundPage';

const PrivateRoute = ({ component: Component, ...rest }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;

  return (
    <Route
      {...rest}
      render={(props) => user ? <Component {...props} /> : <Redirect to="/login" />}
    />
  );
};

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <Switch>
          <Route path="/" exact component={LandingPage} />
          <Route path="/login" component={LoginPage} />
          <Route path="/register" component={RegisterPage} />
          <PrivateRoute path="/dashboard" component={DashboardPage} />
          <PrivateRoute path="/projects" component={ProjectsPage} />
          <PrivateRoute path="/projects/:projectId" component={ProjectDetailPage} />
          <PrivateRoute path="/tasks" component={TasksPage} />
          <PrivateRoute path="/tasks/:taskId" component={TaskDetailPage} />
          <PrivateRoute path="/settings" component={SettingsPage} />
          <PrivateRoute path="/admin" component={AdminPage} />
          <Route path="*" component={NotFoundPage} />
        </Switch>
      </Router>
    </AuthProvider>
  );
};

export default App;
```

## Conclusion

The authentication and authorization system in TaskFlow is robust and secure, leveraging JWT tokens for session management and role-based access control for authorization. The system ensures that only authenticated and authorized users can access and perform specific actions, providing a secure and user-friendly experience.

---

# Frontend

This section provides an overview of the frontend architecture of the TaskFlow application, including React components, routing, and state management.

## React Components

### Main Application Component
- **File**: `taskflow\frontend\src\App.jsx`
- **Description**: The main entry point of the application, setting up routing for various pages. It includes public and private routes, where private routes require user authentication. Unauthenticated users are redirected to the login page.
- **Key Components**:
  - **Public Routes**: Landing, Login, Registration
  - **Private Routes**: Dashboard, Projects, Tasks, Settings, Admin, Task Detail, Project Detail

### Layout Components
- **Navbar**
  - **File**: `taskflow\frontend\src\components\Layout\Navbar.jsx`
  - **Description**: A header component displaying a navigation bar with links to the dashboard and settings pages, and a logout button. It uses the `useAuth` hook to manage authentication state.
- **Sidebar**
  - **File**: `taskflow\frontend\src\components\Layout\Sidebar.jsx`
  - **Description**: A sidebar component displaying navigation links and user information. It uses the `useAuth` hook to determine if the user is an admin and conditionally adds an admin link.
- **PageWrapper**
  - **File**: `taskflow\frontend\src\components\Layout\PageWrapper.jsx`
  - **Description**: A layout container for other components, including a Sidebar, Navbar, and main content area. It accepts children and title as props.

### Project and Task Components
- **ProjectCard**
  - **File**: `taskflow\frontend\src\components\Projects\ProjectCard.jsx`
  - **Description**: A card component for displaying a project, including a link to the project's detail page, the project's name, description, and archived status.
- **ProjectSettings**
  - **File**: `taskflow\frontend\src\components\Projects\ProjectSettings.jsx`
  - **Description**: A form component for updating a project's settings, including name, description, and archived status. It uses the `useProjects` hook to handle project updates.
- **TaskCard**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskCard.jsx`
  - **Description**: A card component for displaying a task, including a link to the task's detail page, the task's title, status, priority, due date, and assignee.
- **TaskDetail**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskDetail.jsx`
  - **Description**: A component for displaying detailed information about a task, including status, priority, due date, title, and description. It fetches the task data from an API endpoint and handles loading, error, and not found states. It also includes a `CommentList` component to display comments related to the task.
- **TaskForm**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskForm.jsx`
  - **Description**: A form component for creating or editing a task, including fields for title, description, priority, status, and due date. It handles form submission and provides a cancel button to close the form.
- **CommentList**
  - **File**: `taskflow\frontend\src\components\Tasks\CommentList.jsx`
  - **Description**: A component for displaying a list of comments for a given task and allowing users to add new comments. It fetches comments from an API endpoint and updates the list when new comments are posted.

### UI Components
- **Button**
  - **File**: `taskflow\frontend\src\components\UI\Button.jsx`
  - **Description**: A reusable button component that accepts props for customizing the button's appearance and behavior, such as variant, size, and additional class names.
- **Spinner**
  - **File**: `taskflow\frontend\src\components\UI\Spinner.jsx`
  - **Description**: A component that renders a spinning circle to indicate loading states. It accepts a `className` prop to allow for additional styling.
- **Badge**
  - **File**: `taskflow\frontend\src\components\UI\Badge.jsx`
  - **Description**: A component for displaying a badge with different styles based on the variant prop. It supports variants for default, success, warning, danger, and info, each with its own background and text color.
- **Modal**
  - **File**: `taskflow\frontend\src\components\UI\Modal.jsx`
  - **Description**: A component for displaying a modal dialog when the `open` prop is true. The modal can be closed by clicking outside the dialog or by clicking the close button. It accepts props for the modal's title and content.

### Page Components
- **LandingPage**
  - **File**: `taskflow\frontend\src\pages\LandingPage.jsx`
  - **Description**: The main landing page of the TaskFlow application, including navigation, a hero section, features, pricing, and testimonials. It uses links to navigate to login and registration pages.
- **LoginPage**
  - **File**: `taskflow\frontend\src\pages\LoginPage.jsx`
  - **Description**: A page for user login, including form fields for email and password, and handling the submission of login credentials to authenticate the user. Upon successful login, the user is redirected to a specified or default page.
- **RegisterPage**
  - **File**: `taskflow\frontend\src\pages\RegisterPage.jsx`
  - **Description**: A page for user registration, including form fields for full name, email, and password, and attempting to register the user with the provided credentials. Upon successful registration, the user is redirected to the dashboard.
- **DashboardPage**
  - **File**: `taskflow\frontend\src\pages\DashboardPage.jsx`
  - **Description**: A page displaying a dashboard with statistics about open tasks, overdue tasks, and projects. It also shows a list of recent tasks and provides a button to navigate to the task creation page.
- **ProjectsPage**
  - **File**: `taskflow\frontend\src\pages\ProjectsPage.jsx`
  - **Description**: A page displaying a list of projects and allowing users to create new projects through a modal form. It uses the `useProjects` hook to fetch and manage project data.
- **ProjectDetailPage**
  - **File**: `taskflow\frontend\src\pages\ProjectDetailPage.jsx`
  - **Description**: A page for displaying detailed information about a project, including the project's name, description, and settings. It fetches project data from an API endpoint and handles loading and error states.
- **TasksPage**
  - **File**: `taskflow\frontend\src\pages\TasksPage.jsx`
  - **Description**: A page displaying a list of tasks and allowing users to filter tasks by project and search term. It also provides a modal form to create new tasks.
- **TaskDetailPage**
  - **File**: `taskflow\frontend\src\pages\TaskDetailPage.jsx`
  - **Description**: A page for displaying detailed information about a task, using a `TaskDetail` component to show the task details.
- **SettingsPage**
  - **File**: `taskflow\frontend\src\pages\SettingsPage.jsx`
  - **Description**: A page allowing a user to update their full name. It uses a custom hook for authentication and makes an API call to update the user's profile.
- **AdminPage**
  - **File**: `taskflow\frontend\src\pages\AdminPage.jsx`
  - **Description**: A page for administrative tasks, rendering a `PageWrapper` with a title 'Admin' and a `UserTable` component to display user data.
- **NotFoundPage**
  - **File**: `taskflow\frontend\src\pages\NotFoundPage.jsx`
  - **Description**: A page displaying a 404 error message and a link to return to the home page.

## Routing

### Main Application Entry Point
- **File**: `taskflow\frontend\src\main.jsx`
- **Description**: The entry point for the React application, setting up the React DOM, BrowserRouter for routing, and an `AuthProvider` for authentication context. It renders the main `App` component.

### React Router
- **File**: `taskflow\frontend\src\App.jsx`
- **Description**: The `App` component sets up routing for different pages using `react-router-dom`. It includes public and private routes, where private routes require user authentication. Unauthenticated users are redirected to the login page.

## State Management

### Custom Hooks
- **useAuth**
  - **File**: `taskflow\frontend\src\hooks\useAuth.js`
  - **Description**: A custom hook re-exported from `AuthContext` for managing authentication state.
- **useProjects**
  - **File**: `taskflow\frontend\src\hooks\useProjects.js`
  - **Description**: A custom hook that provides state management for projects, including fetching, creating, updating, and deleting projects using an API.
- **useTasks**
  - **File**: `taskflow\frontend\src\hooks\useTasks.js`
  - **Description**: A custom hook that provides state management for tasks, including fetching, creating, updating, and deleting tasks using an API.

### Authentication Context
- **File**: `taskflow\frontend\src\context\AuthContext.jsx`
- **Description**: An authentication context for managing user authentication state, including functions for logging in, registering, and logging out. It interacts with an authentication API and local storage.

## API Client

### Axios Client
- **File**: `taskflow\frontend\src\api\client.js`
- **Description**: An Axios client configured with interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to a login page.

### API Modules
- **Auth API**
  - **File**: `taskflow\frontend\src\api\auth.js`
  - **Description**: Functions for handling authentication operations such as login, registration, logout, and token refreshing.
- **Admin API**
  - **File**: `taskflow\frontend\src\api\admin.js`
  - **Description**: Functions for making HTTP requests to the admin endpoints of the API, including fetching all users, deleting a user, and getting a billing overview.
- **Projects API**
  - **File**: `taskflow\frontend\src\api\projects.js`
  - **Description**: Functions for interacting with the projects API endpoints, including listing, retrieving, creating, updating, and deleting projects.
- **Tasks API**
  - **File**: `taskflow\frontend\src\api\tasks.js`
  - **Description**: Functions for interacting with the tasks API endpoints, including listing, retrieving, creating, updating, and deleting tasks.

## Development Configuration

### Vite Configuration
- **File**: `taskflow\frontend\vite.config.js`
- **Description**: Configures the Vite development server to run on port 3000 and proxy API and uploads requests to a backend server running on port 3001.

### PostCSS Configuration
- **File**: `taskflow\frontend\postcss.config.js`
- **Description**: Configures the PostCSS setup for the frontend project, integrating Tailwind CSS. It defines the content files to be processed and extends the default theme settings.

## Utility Functions

### Authentication Utilities
- **File**: `taskflow\frontend\src\utils\authUtils.js`
- **Description**: Utility functions for managing authentication sessions, including saving, clearing, and retrieving session data from the browser's localStorage.

### Formatters
- **File**: `taskflow\frontend\src\utils\formatters.js`
- **Description**: Utility functions for formatting dates, priorities, and statuses, including functions to format dates in a short format, to format dates relative to the current time, and to format priority and status labels.

### Analytics
- **File**: `taskflow\frontend\src\utils\analytics.js`
- **Description**: Utility functions for tracking user events and identifying users in Mixpanel and Google Analytics. It exports the tracking token and measurement ID for these services.

---