# Overview

## What is TaskFlow?

TaskFlow is a comprehensive project management tool designed to streamline the process of managing tasks, projects, and user interactions within an organization. It provides a robust backend and a user-friendly frontend to facilitate collaboration, task tracking, and reporting. TaskFlow is built using modern web technologies, including Node.js, Express, PostgreSQL, and React.

## Main Components

### Backend
- **Database Configuration (`taskflow/backend/config/db.js`)**: Sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries.
- **Server Setup (`taskflow/backend/server.js`)**: Initializes and starts a Node.js server using an Express application. It listens on a specified port and logs a message upon successful startup.
- **Express Application (`taskflow/backend/src/app.js`)**: Configures middleware for JSON and text parsing, serves static files, and mounts various route handlers for different API endpoints.
- **Controllers**: Handle specific business logic and HTTP requests.
  - **Report Controller (`taskflow/backend/src/controllers/reportController.js`)**: Manages the generation of PDF reports based on project data.
  - **Import Controller (`taskflow/backend/src/controllers/importController.js`)**: Handles the import of tasks from XML and CSV formats.
  - **Admin Controller (`taskflow/backend/src/controllers/adminController.js`)**: Manages administrative tasks such as retrieving all users, deleting a user, and getting a billing overview.
  - **Notification Controller (`taskflow/backend/src/controllers/notificationController.js`)**: Manages user notifications, including listing, marking as read, and managing preferences.
  - **Attachment Controller (`taskflow/backend/src/controllers/attachmentController.js`)**: Manages task attachments, including listing, uploading, downloading, and removing attachments.
  - **Project Controller (`taskflow/backend/src/controllers/projectController.js`)**: Manages projects, including listing, retrieving, creating, updating, and deleting projects.
  - **User Controller (`taskflow/backend/src/controllers/userController.js`)**: Manages user profiles, including retrieving and updating profile information.
  - **Task Controller (`taskflow/backend/src/controllers/taskController.js`)**: Manages tasks, including listing, retrieving, creating, updating, and deleting tasks.
  - **Auth Controller (`taskflow/backend/src/controllers/authController.js`)**: Manages user authentication, including registration, login, token refresh, password reset, and logout.
- **Middleware**: Handles cross-cutting concerns such as authentication, authorization, error handling, and rate limiting.
  - **Authenticate (`taskflow/backend/src/middleware/authenticate.js`)**: Verifies JWT tokens in the authorization header.
  - **Authorize (`taskflow/backend/src/middleware/authorize.js`)**: Checks user roles and permissions.
  - **Error Handler (`taskflow/backend/src/middleware/errorHandler.js`)**: Logs errors and sends JSON responses.
  - **Upload (`taskflow/backend/src/middleware/upload.js`)**: Configures file upload using Multer.
  - **Rate Limiter (`taskflow/backend/src/middleware/rateLimiter.js`)**: Limits the rate of report generation requests.
- **Models**: Define the schema and operations for database tables.
  - **Task Model (`taskflow/backend/src/models/taskModel.js`)**: Manages tasks in the database.
  - **Project Model (`taskflow/backend/src/models/projectModel.js`)**: Manages projects in the database.
  - **Org Model (`taskflow/backend/src/models/orgModel.js`)**: Manages organizations and their members.
  - **User Model (`taskflow/backend/src/models/userModel.js`)**: Manages users in the database.
- **Services**: Provide utility functions for specific tasks.
  - **Email Service (`taskflow/backend/src/services/emailService.js`)**: Sends emails using SendGrid.
  - **Notification Service (`taskflow/backend/src/services/notificationService.js`)**: Manages user notifications and preferences.
  - **Report Service (`taskflow/backend/src/services/reportService.js`)**: Generates HTML and PDF reports.
  - **Stripe Service (`taskflow/backend/src/services/stripeService.js`)**: Interacts with the Stripe API for billing and subscriptions.
- **Utils**: Contains utility functions and constants.
  - **Logger (`taskflow/backend/src/utils/logger.js`)**: Formats and logs messages.
  - **Token Utils (`taskflow/backend/src/utils/tokenUtils.js`)**: Manages JWT token generation and verification.
  - **Validators (`taskflow/backend/src/utils/validators.js`)**: Validates and sanitizes strings.
  - **Merge Objects (`taskflow/backend/src/utils/mergeObjects.js`)**: Merges objects deeply.
  - **Formatters (`taskflow/backend/src/utils/formatters.js`)**: Formats dates and labels.

### Frontend
- **Main Application (`taskflow/frontend/src/main.jsx`)**: Sets up the React application, routing, and authentication context.
- **API Client (`taskflow/frontend/src/api/client.js`)**: Configures an Axios client for making HTTP requests to the backend API.
- **API Modules**: Provide functions for interacting with specific API endpoints.
  - **Admin API (`taskflow/frontend/src/api/admin.js`)**: Manages admin-related API calls.
  - **Auth API (`taskflow/frontend/src/api/auth.js`)**: Manages user authentication API calls.
  - **Projects API (`taskflow/frontend/src/api/projects.js`)**: Manages project-related API calls.
  - **Tasks API (`taskflow/frontend/src/api/tasks.js`)**: Manages task-related API calls.
- **Components**: Reusable UI elements.
  - **Layout Components**: Provide a consistent layout for the application.
    - **Page Wrapper (`taskflow/frontend/src/components/Layout/PageWrapper.jsx`)**: Combines a sidebar, navbar, and main content area.
    - **Navbar (`taskflow/frontend/src/components/Layout/Navbar.jsx`)**: Displays navigation links and user information.
    - **Sidebar (`taskflow/frontend/src/components/Layout/Sidebar.jsx`)**: Displays navigation links based on user role.
  - **Project Components**: Display and manage project information.
    - **Project Card (`taskflow/frontend/src/components/Projects/ProjectCard.jsx`)**: Displays a card for a project.
    - **Project Settings (`taskflow/frontend/src/components/Projects/ProjectSettings.jsx`)**: Allows users to update project settings.
    - **Project Detail Page (`taskflow/frontend/src/components/Projects/ProjectDetailPage.jsx`)**: Displays detailed information about a project.
  - **Task Components**: Display and manage task information.
    - **Task Card (`taskflow/frontend/src/components/Tasks/TaskCard.jsx`)**: Displays a card for a task.
    - **Task Detail Page (`taskflow/frontend/src/components/Tasks/TaskDetailPage.jsx`)**: Displays detailed information about a task.
    - **Task Form (`taskflow/frontend/src/components/Tasks/TaskForm.jsx`)**: Allows users to create or edit a task.
    - **Comment List (`taskflow/frontend/src/components/Tasks/CommentList.jsx`)**: Displays and manages comments for a task.
  - **UI Components**: Reusable UI elements.
    - **Button (`taskflow/frontend/src/components/UI/Button.jsx`)**: A styled button component.
    - **Badge (`taskflow/frontend/src/components/UI/Badge.jsx`)**: A styled badge component.
    - **Modal (`taskflow/frontend/src/components/UI/Modal.jsx`)**: A modal dialog component.
    - **Spinner (`taskflow/frontend/src/components/UI/Spinner.jsx`)**: A loading spinner component.
- **Pages**: Top-level components that represent different pages in the application.
  - **Admin Page (`taskflow/frontend/src/pages/AdminPage.jsx`)**: Displays a table of users and allows admin actions.
  - **Dashboard Page (`taskflow/frontend/src/pages/DashboardPage.jsx`)**: Displays a dashboard with statistics and recent tasks.
  - **Login Page (`taskflow/frontend/src/pages/LoginPage.jsx`)**: Handles user login.
  - **Landing Page (`taskflow/frontend/src/pages/LandingPage.jsx`)**: Provides an overview and links to login and registration.
  - **Not Found Page (`taskflow/frontend/src/pages/NotFoundPage.jsx`)**: Displays a 404 error page.
  - **Projects Page (`taskflow/frontend/src/pages/ProjectsPage.jsx`)**: Displays a list of projects and allows creating new projects.
  - **Project Detail Page (`taskflow/frontend/src/pages/ProjectDetailPage.jsx`)**: Displays detailed information about a project.
  - **Register Page (`taskflow/frontend/src/pages/RegisterPage.jsx`)**: Handles user registration.
  - **Settings Page (`taskflow/frontend/src/pages/SettingsPage.jsx`)**: Allows users to update their profile information.
  - **Tasks Page (`taskflow/frontend/src/pages/TasksPage.jsx`)**: Displays a list of tasks and allows creating new tasks.
- **Hooks**: Custom React hooks for state and side-effect management.
  - **useAuth (`taskflow/frontend/src/hooks/useAuth.js`)**: Manages authentication state.
  - **useProjects (`taskflow/frontend/src/hooks/useProjects.js`)**: Manages project data.
  - **useTasks (`taskflow/frontend/src/hooks/useTasks.js`)**: Manages task data.
- **Utils**: Contains utility functions and constants.
  - **Analytics (`taskflow/frontend/src/utils/analytics.js`)**: Tracks user events and identifies users in Mixpanel and Google Analytics.
  - **Auth Utils (`taskflow/frontend/src/utils/authUtils.js`)**: Manages authentication sessions in local storage.
  - **Formatters (`taskflow/frontend/src/utils/formatters.js`)**: Formats dates and labels.

## Typical Usage Scenario

1. **User Registration and Login**:
   - A new user visits the landing page and clicks on the "Register" link.
   - The user fills out the registration form with their full name, email, and password.
   - Upon successful registration, the user is redirected to the login page.
   - The user logs in using their email and password, and the application verifies the credentials with the backend.
   - Upon successful authentication, the user is redirected to the dashboard.

2. **Project Management**:
   - The user navigates to the "Projects" page, which lists all their projects.
   - The user can create a new project by clicking the "Create Project" button, which opens a modal form.
   - The user fills out the project details and submits the form, which sends a POST request to the backend to create the project.
   - The user can view detailed information about a project by clicking on the project card, which navigates to the project detail page.
   - On the project detail page, the user can manage tasks, add comments, and update project settings.

3. **Task Management**:
   - The user navigates to the "Tasks" page, which lists all their tasks.
   - The user can filter tasks by project and search term.
   - The user can create a new task by clicking the "Create Task" button, which opens a modal form.
   - The user fills out the task details and submits the form, which sends a POST request to the backend to create the task.
   - The user can view detailed information about a task by clicking on the task card, which navigates to the task detail page.
   - On the task detail page, the user can manage comments and update task details.

4. **Admin Functions**:
   - An admin user navigates to the "Admin" page, which displays a table of all users.
   - The admin can delete a user by clicking the "Delete" button next to the user's entry.
   - The admin can view a billing overview by clicking the "Billing" link, which fetches and displays billing information.

5. **Notifications and Preferences**:
   - The user can manage their notification preferences by navigating to the "Settings" page.
   - The user can update their notification preferences and save the changes, which sends a PATCH request to the backend to update the user's profile.

## Where to Look Next

- **Backend**:
  - **Database Configuration**: For details on how the database is set up and queried, see the `taskflow/backend/config/db.js` file.
  - **Controllers**: For specific business logic and HTTP request handling, explore the `taskflow/backend/src/controllers` directory.
  - **Middleware**: For cross-cutting concerns like authentication and error handling, see the `taskflow/backend/src/middleware` directory.
  - **Models**: For database schema and operations, refer to the `taskflow/backend/src/models` directory.
  - **Services**: For utility functions and external API interactions, check the `taskflow/backend/src/services` directory.
  - **Utils**: For general utility functions, see the `taskflow/backend/src/utils` directory.

- **Frontend**:
  - **Main Application**: For the entry point and routing configuration, see the `taskflow/frontend/src/main.jsx` file.
  - **API Client**: For making HTTP requests to the backend, refer to the `taskflow/frontend/src/api/client.js` file.
  - **API Modules**: For specific API interactions, explore the `taskflow/frontend/src/api` directory.
  - **Components**: For reusable UI elements, see the `taskflow/frontend/src/components` directory.
  - **Pages**: For top-level components representing different pages, refer to the `taskflow/frontend/src/pages` directory.
  - **Hooks**: For custom React hooks, check the `taskflow/frontend/src/hooks` directory.
  - **Utils**: For general utility functions, see the `taskflow/frontend/src/utils` directory.

For more detailed documentation on specific components and functionalities, refer to the corresponding sections in the documentation.

---

# Architecture and Data Flow

## Main Architectural Components

The TaskFlow application is built using a layered architecture, with clear separation of concerns between different modules and services. The main components of the architecture include:

### 1. **Backend Server**
- **Node.js and Express.js**: The backend is built using Node.js and the Express.js framework, which provides a robust set of features for building web applications.
- **Configuration**: The server is configured in `taskflow\backend\server.js`, which sets up the Express application, loads environment variables, and starts the server on a specified port (default 3001).

### 2. **Database Layer**
- **PostgreSQL**: The application uses PostgreSQL as its primary database. The database connection is managed in `taskflow\backend\config\db.js`, which sets up a connection pool and provides a query function.
- **ORM Models**: Models for interacting with the database are defined in files like `taskflow\backend\src\models\taskModel.js`, `taskflow\backend\src\models\projectModel.js`, `taskflow\backend\src\models\orgModel.js`, and `taskflow\backend\src\models\userModel.js`. These models provide functions for CRUD operations on their respective tables.

### 3. **Controllers**
- **API Endpoints**: Controllers handle HTTP requests and responses. They are responsible for business logic and interacting with the database. Key controllers include:
  - **Authentication**: `taskflow\backend\src\controllers\authController.js` handles user registration, login, token refresh, password reset, and logout.
  - **Projects**: `taskflow\backend\src\controllers\projectController.js` manages project-related operations such as listing, creating, updating, and deleting projects.
  - **Tasks**: `taskflow\backend\src\controllers\taskController.js` handles task management, including listing, creating, updating, and deleting tasks.
  - **Attachments**: `taskflow\backend\src\controllers\attachmentController.js` manages file attachments for tasks.
  - **Reports**: `taskflow\backend\src\controllers\reportController.js` generates PDF reports for projects.
  - **Imports**: `taskflow\backend\src\controllers\importController.js` handles importing tasks from XML and CSV files.
  - **Notifications**: `taskflow\backend\src\controllers\notificationController.js` manages user notifications.
  - **Admin**: `taskflow\backend\src\controllers\adminController.js` provides administrative functionalities like managing users and billing.

### 4. **Services**
- **Report Generation**: `taskflow\backend\src\services\reportService.js` generates HTML and PDF reports using file system operations and the `wkhtmltopdf` tool.
- **Email**: `taskflow\backend\src\services\emailService.js` sends emails using SendGrid for invitations and password reset links.
- **Notifications**: `taskflow\backend\src\services\notificationService.js` manages user notifications and preferences.
- **Stripe**: `taskflow\backend\src\services\stripeService.js` interacts with the Stripe API for payment processing and subscription management.

### 5. **Middleware**
- **Authentication**: `taskflow\backend\src\middleware\authenticate.js` and `taskflow\backend\src\middleware\authorize.js` handle user authentication and authorization.
- **Error Handling**: `taskflow\backend\src\middleware\errorHandler.js` logs errors and sends appropriate JSON responses.
- **File Uploads**: `taskflow\backend\src\middleware\upload.js` configures multer for handling file uploads.
- **Rate Limiting**: `taskflow\backend\src\middleware\rateLimiter.js` limits the rate of report generation requests to prevent abuse.

### 6. **Frontend Application**
- **React**: The frontend is built using React, with components and pages defined in `taskflow\frontend\src`.
- **Routing**: React Router is used for client-side routing, with private routes protected by authentication.
- **Authentication**: The `taskflow\frontend\src\context\AuthContext.jsx` provides authentication state and actions to the application.
- **API Client**: `taskflow\frontend\src\api\client.js` sets up an Axios client for making HTTP requests to the backend API, including interceptors for adding authentication tokens and handling unauthorized responses.
- **Pages**: Key pages include `taskflow\frontend\src\pages\DashboardPage.jsx`, `taskflow\frontend\src\pages\ProjectsPage.jsx`, `taskflow\frontend\src\pages\TasksPage.jsx`, and `taskflow\frontend\src\pages\SettingsPage.jsx`.
- **Components**: Reusable UI components are defined in `taskflow\frontend\src\components`, such as `Button.jsx`, `Badge.jsx`, `Modal.jsx`, and `Spinner.jsx`.

## Data and Control Flow

### 1. **User Authentication**
- **Login**: When a user logs in, the `LoginPage` component sends a POST request to the `authController` in the backend. The `authenticate` middleware verifies the JWT token, and the `authController` handles the login process.
- **Registration**: User registration is handled by the `RegisterPage` component, which sends a POST request to the `authController` to create a new user and organization.
- **Session Management**: The `authUtils` utility functions manage session data in local storage, including saving and clearing tokens and user data.

### 2. **Project Management**
- **Listing Projects**: The `ProjectsPage` component fetches a list of projects from the `projectController` using the `projectsApi` module. The `projectController` interacts with the `projectModel` to query the database.
- **Creating Projects**: When a user creates a new project, the `ProjectsPage` component sends a POST request to the `projectController`, which validates the input and creates a new project record in the database.
- **Updating Projects**: The `ProjectSettings` component allows users to update project details. It sends a PUT request to the `projectController`, which updates the project record in the database.

### 3. **Task Management**
- **Listing Tasks**: The `TasksPage` component fetches a list of tasks from the `taskController` using the `tasksApi` module. The `taskController` interacts with the `taskModel` to query the database.
- **Creating Tasks**: When a user creates a new task, the `TaskForm` component sends a POST request to the `taskController`, which validates the input and creates a new task record in the database.
- **Updating Tasks**: The `TaskDetailPage` component allows users to update task details. It sends a PUT request to the `taskController`, which updates the task record in the database.

### 4. **Attachments**
- **Uploading Attachments**: The `TaskForm` component allows users to upload attachments. The `attachmentController` handles the file upload, storing the file in the filesystem and creating an attachment record in the database.
- **Downloading Attachments**: The `TaskDetailPage` component provides a link to download attachments. The `attachmentController` serves the file from the filesystem.

### 5. **Reports**
- **Generating Reports**: The `ReportController` handles requests to generate PDF reports for projects. It uses the `reportService` to generate an HTML report and convert it to PDF using `wkhtmltopdf`.

### 6. **Notifications**
- **Listing Notifications**: The `NotificationController` handles requests to list notifications for a user. It interacts with the `notificationService` to fetch and manage notifications.
- **Marking as Read**: The `NotificationController` also handles requests to mark notifications as read.

### 7. **Admin Functions**
- **Managing Users**: The `AdminPage` component allows administrators to manage users. It fetches user data from the `adminController` and provides actions to delete users.
- **Billing Overview**: The `AdminPage` also provides a billing overview, which is fetched from the `adminController`.

### 8. **Error Handling**
- **Global Error Handling**: The `errorHandler` middleware in the backend logs errors and sends appropriate JSON responses. The frontend uses the `error` utility function to log errors and display error messages to the user.

### 9. **Security**
- **Rate Limiting**: The `rateLimiter` middleware limits the rate of report generation requests to prevent abuse.
- **Authorization**: The `authorize` middleware ensures that only users with the appropriate roles can access certain resources.

## Important Patterns
- **Model-View-Controller (MVC)**: The application follows the MVC pattern, with models handling database interactions, views (React components) rendering the UI, and controllers handling business logic and HTTP requests.
- **Middleware**: Middleware functions in Express.js are used to handle cross-cutting concerns like authentication, error handling, and rate limiting.
- **Service Layer**: Services encapsulate business logic and interact with external systems like email services and payment gateways.
- **State Management**: React hooks like `useProjects` and `useTasks` manage state and side effects for fetching and updating data.

By following this architecture, the TaskFlow application ensures a clear separation of concerns, maintainability, and scalability.

---

# Key Components

This section details the main components of the TaskFlow application, including the backend server, database, authentication system, and frontend components.

## Backend Server

### Server Setup
- **File**: `taskflow/backend/server.js`
- **Description**: Sets up and starts a Node.js server using an Express application defined in `./src/app`. It listens on a specified port, defaulting to 3001 if not defined in the environment variables.
- **Key Entities**:
  - `app.listen`: Starts the server and listens on the specified port, logging a message to the console upon successful startup.

### Express Application
- **File**: `taskflow/backend/src/app.js`
- **Description**: Sets up an Express.js application, configures middleware for JSON and text parsing, serves static files from the uploads directory, and mounts various route handlers for different API endpoints.
- **Key Entities**:
  - **Middleware**:
    - JSON and text parsing
    - Serving static files from the uploads directory
  - **Routes**:
    - Health check endpoint: `GET /api/v1/health`
    - Multiple API endpoints for authentication, tasks, projects, users, attachments, reports, imports, notifications, and admin functionalities.

## Database

### Database Configuration
- **File**: `taskflow/backend/config/db.js`
- **Description**: Sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries. It uses environment variables for configuration, with fallbacks for local development.
- **Key Entities**:
  - `pool`: A PostgreSQL connection pool instance that can be used to execute queries.
  - `query`: A function that takes SQL text and parameters, and executes the query using the connection pool.

### Models
- **Task Model**
  - **File**: `taskflow/backend/src/models/taskModel.js`
  - **Description**: Defines functions for interacting with the 'tasks' table in the database, including finding tasks by ID or project ID, creating new tasks, updating existing tasks, and removing tasks.
- **Project Model**
  - **File**: `taskflow/backend/src/models/projectModel.js`
  - **Description**: Defines functions for interacting with the 'projects' table in the database, including finding, creating, updating, and deleting project records.
- **User Model**
  - **File**: `taskflow/backend/src/models/userModel.js`
  - **Description**: Defines functions for interacting with the 'users' table in the database, including finding users by ID or email, creating new users, updating refresh tokens, setting and clearing reset tokens, and updating passwords.
- **Organization Model**
  - **File**: `taskflow/backend/src/models/orgModel.js`
  - **Description**: Defines functions for interacting with the 'orgs' and 'org_members' tables in the database, including finding an organization by ID, creating a new organization, adding a member to an organization, and retrieving the members of an organization.

## Authentication System

### Authentication Middleware
- **File**: `taskflow/backend/src/middleware/authenticate.js`
- **Description**: Defines a middleware function for authenticating HTTP requests by verifying a JWT token in the authorization header. It attaches user information to the request object if the token is valid, or returns a 401 Unauthorized response if the token is missing, invalid, or expired.
- **Key Entities**:
  - `authenticate`: Middleware function that checks the authorization header and verifies the JWT token.

### Authorization Middleware
- **File**: `taskflow/backend/src/middleware/authorize.js`
- **Description**: Defines a middleware function for authorizing user roles in an HTTP request handling chain. It checks if the user is authenticated and if their role is among the allowed roles for the requested resource.
- **Key Entities**:
  - `authorize`: Middleware function that can be used in HTTP routes to check user authentication and role permissions.

### Authentication Controller
- **File**: `taskflow/backend/src/controllers/authController.js`
- **Description**: Contains the implementation of authentication-related endpoints, including user registration, login, token refresh, password reset, and logout functionalities. It interacts with user and organization models, handles password hashing, and manages JWT tokens.
- **Key Entities**:
  - `register`: Handles user registration.
  - `login`: Handles user login.
  - `refresh`: Handles token refresh.
  - `forgotPassword`: Handles password reset requests.
  - `resetPassword`: Handles password reset.
  - `logout`: Handles user logout.

### Token Utilities
- **File**: `taskflow/backend/src/utils/tokenUtils.js`
- **Description**: Contains utility functions for generating and verifying JWT access and refresh tokens. It uses the 'jsonwebtoken' library and environment variables for secrets.
- **Key Entities**:
  - `tokenUtils`: Provides functions to sign and verify access and refresh tokens.

## Frontend Components

### Main Application Component
- **File**: `taskflow/frontend/src/App.jsx`
- **Description**: Defines the main application component for a React-based frontend. It sets up routing for various pages, including public and private routes. Private routes require user authentication, redirecting unauthenticated users to the login page.
- **Key Entities**:
  - `App`: The main entry point of the application, which renders the routing configuration.

### Layout Components
- **Page Wrapper**
  - **File**: `taskflow/frontend/src/components/Layout/PageWrapper.jsx`
  - **Description**: Serves as a layout container for other components. It includes a Sidebar and a Navbar, and it can display a title and children components within the main content area.
- **Navbar**
  - **File**: `taskflow/frontend/src/components/Layout/Navbar.jsx`
  - **Description**: Displays a navigation bar at the top of the application. The navbar includes links to the dashboard and settings pages, and a logout button. It also displays the user's full name if they are authenticated.
- **Sidebar**
  - **File**: `taskflow/frontend/src/components/Layout/Sidebar.jsx`
  - **Description**: Displays navigation links based on the user's role. It uses React and the `react-router-dom` library for routing and navigation.

### Authentication Pages
- **Login Page**
  - **File**: `taskflow/frontend/src/pages/LoginPage.jsx`
  - **Description**: Handles user input for email and password, and attempts to authenticate the user. Upon successful login, the user is redirected to a specified or default page.
- **Register Page**
  - **File**: `taskflow/frontend/src/pages/RegisterPage.jsx`
  - **Description**: Handles user input for full name, email, and password, and attempts to register the user with the provided credentials. Upon successful registration, the user is redirected to the dashboard.

### Project and Task Management Pages
- **Projects Page**
  - **File**: `taskflow/frontend/src/pages/ProjectsPage.jsx`
  - **Description**: Displays a list of projects and provides a modal for creating new projects. It uses the `useProjects` hook to fetch and manage project data.
- **Project Detail Page**
  - **File**: `taskflow/frontend/src/pages/ProjectDetailPage.jsx`
  - **Description**: Displays details of a specific project. It fetches project data from an API, handles loading and error states, and provides navigation to tasks and project settings.
- **Tasks Page**
  - **File**: `taskflow/frontend/src/pages/TasksPage.jsx`
  - **Description**: Displays a list of tasks and allows users to filter tasks by project and search term. It also provides a modal form to create new tasks. The component uses hooks to manage state and fetch data.

### Admin Page
- **Admin Page**
  - **File**: `taskflow/frontend/src/pages/AdminPage.jsx`
  - **Description**: Serves as a page for administrative tasks. It renders a `PageWrapper` component with a title 'Admin' and includes a `UserTable` component to display user data.

### Utility Functions
- **Formatters**
  - **File**: `taskflow/frontend/src/utils/formatters.js`
  - **Description**: Contains utility functions for formatting dates and labels. It includes functions to format a date in a specific format, format a date relative to the current time, and format priority and status labels.
- **Authentication Utilities**
  - **File**: `taskflow/frontend/src/utils/authUtils.js`
  - **Description**: Contains utility functions for managing authentication sessions in a frontend application. It provides methods to save, clear, and retrieve session data from the browser's localStorage.

## API Clients and Services

### Axios Client
- **File**: `taskflow/frontend/src/api/client.js`
- **Description**: Sets up an Axios client for making HTTP requests to a backend API. It includes interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to the login page.
- **Key Entities**:
  - `client`: The Axios client instance that is configured with interceptors and exported for use in other parts of the application.

### API Services
- **Admin API**
  - **File**: `taskflow/frontend/src/api/admin.js`
  - **Description**: Contains functions for making API calls to the admin endpoints of a backend service. It provides methods to fetch all users, delete a user, and get a billing overview.
- **Projects API**
  - **File**: `taskflow/frontend/src/api/projects.js`
  - **Description**: Defines a set of functions for interacting with a projects API, including listing, retrieving, creating, updating, and deleting projects.
- **Tasks API**
  - **File**: `taskflow/frontend/src/api/tasks.js`
  - **Description**: Defines a set of functions for interacting with a tasks API, including listing, retrieving, creating, updating, and deleting tasks.

## Custom Hooks

### Authentication Hook
- **File**: `taskflow/frontend/src/hooks/useAuth.js`
- **Description**: Re-exports the `useAuth` hook from the `AuthContext` file, which is likely used to manage authentication state in a React application.
- **Key Entities**:
  - `useAuth`: A hook that is re-exported from `AuthContext`, used for managing authentication state.

### Projects Hook
- **File**: `taskflow/frontend/src/hooks/useProjects.js`
- **Description**: Defines a custom React hook named `useProjects` that manages the state and lifecycle of project data, including fetching, creating, updating, and deleting projects. It uses the `projectsApi` module to interact with the backend API.
- **Key Entities**:
  - `useProjects`: A custom React hook that provides state management and API interaction for project data.

### Tasks Hook
- **File**: `taskflow/frontend/src/hooks/useTasks.js`
- **Description**: Defines a custom React hook named `useTasks` that manages the state and lifecycle of tasks for a given project. It includes functions to fetch, create, update, and delete tasks, interacting with an API through the `tasksApi` module.
- **Key Entities**:
  - `useTasks`: A custom React hook that provides state management and API interaction for tasks within a project.

## Additional Services

### Email Service
- **File**: `taskflow/backend/src/services/emailService.js`
- **Description**: Contains functions for sending emails using SendGrid. It provides two main functions: one for sending invitations to join an organization and another for sending password reset links.
- **Key Entities**:
  - `sendInvite`: Function to send an invitation email to a user to join an organization.
  - `sendPasswordReset`: Function to send a password reset email to a user.

### Notification Service
- **File**: `taskflow/backend/src/services/notificationService.js`
- **Description**: Defines a notification service that interacts with a database to manage user notifications and preferences. It provides functions to create notifications, retrieve them for a user, mark them as read, and manage notification preferences.
- **Key Entities**:
  - `notificationService`: Exports functions that can be imported and used by other parts of the application to manage notifications and user preferences.

### Report Service
- **File**: `taskflow/backend/src/services/reportService.js`
- **Description**: Contains functions for generating HTML and PDF reports from task data. It uses file system operations to create and delete temporary files, and executes a command-line tool (wkhtmltopdf) to convert HTML to PDF.
- **Key Entities**:
  - `generateReportHtml`: Generates an HTML string for a report based on task data.
  - `generatePdf`: Generates a PDF report from an HTML string using wkhtmltopdf and file system operations.

### Stripe Service
- **File**: `taskflow/backend/src/services/stripeService.js`
- **Description**: Provides a set of functions to interact with the Stripe API for creating customers, checkout sessions, billing portal sessions, and constructing webhook events.
- **Key Entities**:
  - `createCustomer`: Creates a new customer in Stripe.
  - `createCheckoutSession`: Creates a new checkout session for a customer to subscribe to a price plan.
  - `createBillingPortalSession`: Creates a billing portal session for a customer to manage their subscription.
  - `constructEvent`: Constructs a Stripe webhook event from a payload and signature.

## Logging and Analytics

### Logger
- **File**: `taskflow/backend/src/utils/logger.js`
- **Description**: Defines a simple logging utility that formats log entries as JSON objects and outputs them to the console. It supports different log levels: info, warn, and error.
- **Key Entities**:
  - `info`: Logs an informational message with optional metadata.
  - `warn`: Logs a warning message with optional metadata.
  - `error`: Logs an error message with optional metadata.

### Analytics
- **File**: `taskflow/frontend/src/utils/analytics.js`
- **Description**: Contains utility functions for tracking user events and identifying users in Mixpanel and Google Analytics. It exports functions to track events and identify users, along with the Mixpanel token and Google Analytics measurement ID.
- **Key Entities**:
  - `trackEvent`: Function to track an event in Mixpanel and Google Analytics.
  - `identify`: Function to identify a user in Mixpanel and Google Analytics.

This comprehensive overview of the key components of the TaskFlow application provides a clear understanding of the main functionalities and interactions within the system.

---

# API Reference

This section provides detailed documentation for the API endpoints, including request and response formats, authentication requirements, and example usage.

## Authentication

### Authentication Middleware
- **File:** `taskflow\backend\src\middleware\authenticate.js`
- **Description:** Middleware function that checks the authorization header and verifies the JWT token.
- **Endpoints:**
  - **`authenticate`**
    - **Details:** Checks the authorization header and verifies the JWT token. Attaches user information to the request object if the token is valid, or returns a 401 Unauthorized response if the token is missing, invalid, or expired.

### Authorization Middleware
- **File:** `taskflow\backend\src\middleware\authorize.js`
- **Description:** Middleware function that checks if the user is authenticated and if their role is among the allowed roles for the requested resource.
- **Endpoints:**
  - **`authorize`**
    - **Details:** Returns a 401 status if the user is not authenticated, and a 403 status if the user does not have sufficient permissions.

### Rate Limiter Middleware
- **File:** `taskflow\backend\src\middleware\rateLimiter.js`
- **Description:** Middleware function that limits the rate of report generation requests to prevent abuse of the PDF export feature.
- **Endpoints:**
  - **`reportLimiter`**
    - **Details:** Limits the rate of report generation requests to 10 per minute.

## User Management

### User Controller
- **File:** `taskflow\backend\src\controllers\userController.js`
- **Description:** Handles HTTP requests to retrieve and update user profiles.
- **Endpoints:**
  - **`GET /api/users/profile`**
    - **Details:** Retrieves a user's profile information.
  - **`PUT /api/users/profile`**
    - **Details:** Updates a user's profile information.

### User Routes
- **File:** `taskflow\backend\src\routes\userRoutes.js`
- **Description:** Sets up routes for user-related endpoints, requiring authentication for all routes.
- **Endpoints:**
  - **`GET /profile`**
    - **Details:** Retrieves the user's profile information.
  - **`PATCH /profile`**
    - **Details:** Updates the user's profile information.

### Authentication Controller
- **File:** `taskflow\backend\src\controllers\authController.js`
- **Description:** Handles user registration, login, token refresh, password reset, and logout functionalities.
- **Endpoints:**
  - **`POST /api/register`**
    - **Details:** Handles user registration, including validation, password hashing, and creation of user and organization records.
  - **`POST /api/login`**
    - **Details:** Handles user login, including credential validation and token generation.
  - **`POST /api/refresh`**
    - **Details:** Handles token refresh, generating a new access token from a valid refresh token.
  - **`POST /api/forgot-password`**
    - **Details:** Handles password reset requests, sending a reset link to the user's email.
  - **`POST /api/reset-password`**
    - **Details:** Handles password reset, updating the user's password with a new one.
  - **`POST /logout`**
    - **Details:** Handles user logout, invalidating the refresh token.

### Authentication Routes
- **File:** `taskflow\backend\src\routes\authRoutes.js`
- **Description:** Sets up routes for authentication-related HTTP endpoints.
- **Endpoints:**
  - **`POST /register`**
    - **Details:** Handles user registration requests.
  - **`POST /login`**
    - **Details:** Handles user login requests.
  - **`POST /refresh`**
    - **Details:** Handles token refresh requests.
  - **`POST /forgot-password`**
    - **Details:** Handles forgot password requests.
  - **`POST /reset-password`**
    - **Details:** Handles password reset requests.
  - **`POST /logout`**
    - **Details:** Handles user logout requests, protected by authentication middleware.

## Project Management

### Project Controller
- **File:** `taskflow\backend\src\controllers\projectController.js`
- **Description:** Manages projects within an organization, providing endpoints for listing, retrieving, creating, updating, and deleting projects.
- **Endpoints:**
  - **`GET /projects`**
    - **Details:** Lists projects for a given organization, optionally including archived projects.
  - **`GET /projects/:projectId`**
    - **Details:** Retrieves a single project by ID, with checks for existence and organization ownership.
  - **`POST /projects`**
    - **Details:** Creates a new project for an organization, requiring a valid project name.
  - **`PUT /projects/:projectId`**
    - **Details:** Updates an existing project, with checks for existence and organization ownership.
  - **`DELETE /projects/:projectId`**
    - **Details:** Deletes a project, with checks for existence.

### Project Routes
- **File:** `taskflow\backend\src\routes\projectRoutes.js`
- **Description:** Sets up routes for project-related HTTP endpoints, requiring authentication.
- **Endpoints:**
  - **`GET /`**
    - **Details:** Lists all projects.
  - **`GET /:projectId`**
    - **Details:** Retrieves a single project by ID.
  - **`POST /`**
    - **Details:** Creates a new project.
  - **`PUT /:projectId`**
    - **Details:** Updates an existing project by ID.
  - **`DELETE /:projectId`**
    - **Details:** Deletes a project by ID.

## Task Management

### Task Controller
- **File:** `taskflow\backend\src\controllers\taskController.js`
- **Description:** Manages tasks within a project, providing endpoints for listing, retrieving, creating, updating, and deleting tasks, as well as managing task comments.
- **Endpoints:**
  - **`GET /tasks`**
    - **Details:** Lists tasks for a specific project or across an organization.
  - **`GET /tasks/:taskId/comments`**
    - **Details:** Retrieves comments for a specific task.
  - **`POST /tasks/:taskId/comments`**
    - **Details:** Adds a comment to a specific task.
  - **`GET /tasks/:taskId`**
    - **Details:** Retrieves a single task by its ID.
  - **`POST /tasks`**
    - **Details:** Creates a new task within a project.
  - **`PUT /tasks/:taskId`**
    - **Details:** Updates an existing task.
  - **`DELETE /tasks/:taskId`**
    - **Details:** Deletes a task.

### Task Routes
- **File:** `taskflow\backend\src\routes\taskRoutes.js`
- **Description:** Sets up routes for task-related endpoints, requiring authentication.
- **Endpoints:**
  - **`GET /`**
    - **Details:** Lists all tasks.
  - **`GET /:taskId/comments`**
    - **Details:** Retrieves comments for a specific task.
  - **`POST /:taskId/comments`**
    - **Details:** Adds a comment to a specific task.
  - **`GET /:taskId`**
    - **Details:** Retrieves a single task by ID.
  - **`POST /`**
    - **Details:** Creates a new task.
  - **`PUT /:taskId`**
    - **Details:** Updates a task by ID.
  - **`DELETE /:taskId`**
    - **Details:** Deletes a task by ID.

## Attachment Management

### Attachment Controller
- **File:** `taskflow\backend\src\controllers\attachmentController.js`
- **Description:** Manages task attachments, including listing, uploading, downloading, and removing attachments.
- **Endpoints:**
  - **`GET /api/tasks/:taskId/attachments`**
    - **Details:** Lists all attachments for a given task ID.
  - **`POST /api/tasks/:taskId/attachments`**
    - **Details:** Uploads a file as an attachment to a task, storing it in the filesystem and database.
  - **`GET /api/tasks/:taskId/attachments/:attachmentId`**
    - **Details:** Downloads an attachment by its ID, serving the file from the filesystem.
  - **`DELETE /api/tasks/:taskId/attachments/:attachmentId`**
    - **Details:** Deletes an attachment by its ID, removing it from the database and filesystem.

### Attachment Routes
- **File:** `taskflow\backend\src\routes\attachmentRoutes.js`
- **Description:** Sets up routes for attachment-related operations, requiring authentication.
- **Endpoints:**
  - **`GET /task/:taskId`**
    - **Details:** Lists attachments for a specific task.
  - **`POST /task/:taskId`**
    - **Details:** Uploads a new attachment for a specific task.
  - **`GET /:attachmentId`**
    - **Details:** Downloads an attachment by its ID.
  - **`DELETE /:attachmentId`**
    - **Details:** Deletes an attachment by its ID.

## Report Generation

### Report Controller
- **File:** `taskflow\backend\src\controllers\reportController.js`
- **Description:** Handles the generation of PDF reports for projects.
- **Endpoints:**
  - **`GET /api/reports/:projectId/pdf`**
    - **Details:** Endpoint for generating a PDF report of a project's tasks. It requires a project ID and checks if the project exists and if the user has access to the project.

### Report Routes
- **File:** `taskflow\backend\src\routes\reportRoutes.js`
- **Description:** Sets up routes for report-related endpoints, applying authentication and rate limiting middleware.
- **Endpoints:**
  - **`GET /project/:projectId/pdf`**
    - **Details:** Generates a PDF for a specific project ID. Requires authentication and is rate-limited.

## Import Data

### Import Controller
- **File:** `taskflow\backend\src\controllers\importController.js`
- **Description:** Handles the import of tasks from XML and CSV formats into a project.
- **Endpoints:**
  - **`POST /api/projects/:projectId/import/xml`**
    - **Details:** Endpoint for importing tasks from XML data. It checks the project existence and ownership, parses the XML, and creates tasks in the database.
  - **`POST /api/projects/:projectId/import/csv`**
    - **Details:** Endpoint for importing tasks from CSV data. It checks the project existence and ownership, parses the CSV, and creates tasks in the database.

### Import Routes
- **File:** `taskflow\backend\src\routes\importRoutes.js`
- **Description:** Sets up routes for importing data into a project, with authentication middleware applied to all routes.
- **Endpoints:**
  - **`POST /project/:projectId/xml`**
    - **Details:** Endpoint to import XML data into a project, requires authentication.
  - **`POST /project/:projectId/csv`**
    - **Details:** Endpoint to import CSV data into a project, requires authentication.

## Notification Management

### Notification Controller
- **File:** `taskflow\backend\src\controllers\notificationController.js`
- **Description:** Handles notifications, including listing notifications, marking them as read, and managing user preferences for notifications.
- **Endpoints:**
  - **`GET /notifications`**
    - **Details:** Lists notifications for a user, with a limit parameter.
  - **`PUT /notifications/:id/read`**
    - **Details:** Marks a specific notification as read for a user.
  - **`GET /notifications/preferences`**
    - **Details:** Retrieves notification preferences for a user.
  - **`POST /notifications/preferences`**
    - **Details:** Updates notification preferences for a user.

### Notification Routes
- **File:** `taskflow\backend\src\routes\notificationRoutes.js`
- **Description:** Sets up routes for notification-related HTTP requests, requiring authentication.
- **Endpoints:**
  - **`GET /`**
    - **Details:** Lists all notifications for the authenticated user.
  - **`POST /:id/read`**
    - **Details:** Marks a specific notification as read for the authenticated user.
  - **`GET /preferences`**
    - **Details:** Retrieves the notification preferences for the authenticated user.
  - **`PATCH /preferences`**
    - **Details:** Updates the notification preferences for the authenticated user.

## Admin Management

### Admin Controller
- **File:** `taskflow\backend\src\controllers\adminController.js`
- **Description:** Contains controller functions for administrative tasks, such as retrieving all users, deleting a user, and getting a billing overview.
- **Endpoints:**
  - **`GET /admin/users`**
    - **Details:** Endpoint to retrieve all users from the database.
  - **`DELETE /admin/users/:id`**
    - **Details:** Endpoint to delete a user by their ID.
  - **`GET /admin/billing`**
    - **Details:** Endpoint to get a billing overview, including user details and project counts.

### Admin Routes
- **File:** `taskflow\backend\src\routes\adminRoutes.js`
- **Description:** Sets up routes for admin-specific routes, including endpoints to manage users and view billing information.
- **Endpoints:**
  - **`GET /users`**
    - **Details:** Retrieves all users, requires authentication.
  - **`DELETE /users/:id`**
    - **Details:** Deletes a user by ID, requires authentication.
  - **`GET /billing`**
    - **Details:** Retrieves billing overview, requires authentication.

## Health Check

### Health Check Endpoint
- **File:** `taskflow\backend\src\app.js`
- **Description:** Sets up an Express.js application and includes a health check endpoint.
- **Endpoints:**
  - **`GET /api/v1/health`**
    - **Details:** A health check endpoint that returns a JSON response with a status and timestamp.

## Error Handling

### Error Handler Middleware
- **File:** `taskflow\backend\src\middleware\errorHandler.js`
- **Description:** Middleware function for handling errors in an Express.js application.
- **Endpoints:**
  - **`errorHandler`**
    - **Details:** Logs the error details and sends a JSON response with the error message, stack trace, and status code.

## File Upload

### File Upload Middleware
- **File:** `taskflow\backend\src\middleware\upload.js`
- **Description:** Configures and exports a multer middleware for handling file uploads.
- **Endpoints:**
  - **`upload`**
    - **Details:** The multer middleware instance configured for file uploads, which can be used in an Express application to handle multipart/form-data requests.

## Example Usage

### Example Request and Response

#### User Registration
- **Endpoint:** `POST /api/register`
- **Request:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword",
    "fullName": "John Doe"
  }
  ```
- **Response:**
  ```json
  {
    "message": "User registered successfully",
    "user": {
      "id": "12345",
      "email": "user@example.com",
      "fullName": "John Doe"
    }
  }
  ```

#### User Login
- **Endpoint:** `POST /api/login`
- **Request:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Login successful",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NSIsImV4cCI6MTYxNjM1NzY4MH0.GzWzXxKzXzXzXzXzXzXzXzXzXzXzXzXz"
  }
  ```

#### Create a Project
- **Endpoint:** `POST /projects`
- **Request:**
  ```json
  {
    "name": "New Project",
    "organizationId": "67890"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Project created successfully",
    "project": {
      "id": "123456",
      "name": "New Project",
      "organizationId": "67890"
    }
  }
  ```

#### Generate a PDF Report
- **Endpoint:** `GET /api/reports/:projectId/pdf`
- **Request:**
  - **Headers:**
    ```json
    {
      "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NSIsImV4cCI6MTYxNjM1NzY4MH0.GzWzXxKzXzXzXzXzXzXzXzXzXzXzXzXz"
    }
  ```
- **Response:**
  - **Content-Type:** `application/pdf`
  - **Body:** PDF file content

This API reference provides a comprehensive overview of the available endpoints, their request and response formats, and the authentication requirements. For more detailed information, refer to the specific controller and route files mentioned in each section.

---

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

---

# Data Layer

The Data Layer in the TaskFlow application is responsible for managing the database schema, models, and data management practices. This section provides an overview of the key components and their interactions.

## Database Configuration

### File: `taskflow/backend/config/db.js`

- **Purpose**: Sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries.
- **Key Entities**:
  - **`pool`**: A PostgreSQL connection pool instance that can be used to execute queries.
  - **`query`**: A function that takes SQL text and parameters, and executes the query using the connection pool.
- **Configuration**:
  - Uses environment variables for configuration, with fallbacks for local development.
  - Configures the pool with environment variables or fallbacks for local development.
  - Sets up an error handler for the pool.

## Models

### Task Model

### File: `taskflow/backend/src/models/taskModel.js`

- **Purpose**: Provides functions for database operations on the `tasks` table.
- **Key Functions**:
  - **`findTaskById`**: Finds a task by its ID.
  - **`findTasksByProjectId`**: Finds tasks by project ID.
  - **`createTask`**: Creates a new task.
  - **`updateTask`**: Updates an existing task.
  - **`removeTask`**: Deletes a task.

### Project Model

### File: `taskflow/backend/src/models/projectModel.js`

- **Purpose**: Provides functions for database operations on the `projects` table.
- **Key Functions**:
  - **`findById`**: Finds a project by its ID.
  - **`findByOrg`**: Finds projects by organization ID.
  - **`create`**: Creates a new project.
  - **`update`**: Updates an existing project.
  - **`remove`**: Deletes a project.

### Organization Model

### File: `taskflow/backend/src/models/orgModel.js`

- **Purpose**: Provides functions for database operations on the `orgs` and `org_members` tables.
- **Key Functions**:
  - **`findById`**: Finds an organization by its ID.
  - **`create`**: Creates a new organization.
  - **`addMember`**: Adds a member to an organization.
  - **`getMembers`**: Retrieves the members of an organization.

### User Model

### File: `taskflow/backend/src/models/userModel.js`

- **Purpose**: Provides functions for database operations on the `users` table.
- **Key Functions**:
  - **`findUserById`**: Finds a user by its ID.
  - **`findUserByEmail`**: Finds a user by email.
  - **`createUser`**: Creates a new user.
  - **`updateRefreshToken`**: Updates the refresh token for a user.
  - **`setResetToken`**: Sets a password reset token for a user.
  - **`clearResetToken`**: Clears the password reset token for a user.
  - **`updatePassword`**: Updates the password for a user.

## Controllers

### Task Controller

### File: `taskflow/backend/src/controllers/taskController.js`

- **Purpose**: Manages HTTP requests related to tasks.
- **Key Endpoints**:
  - **`list`**: Lists tasks for a specific project or across an organization.
  - **`getOne`**: Retrieves a single task by its ID.
  - **`create`**: Creates a new task within a project.
  - **`update`**: Updates an existing task.
  - **`remove`**: Deletes a task.
  - **`getComments`**: Retrieves comments for a specific task.
  - **`addComment`**: Adds a comment to a specific task.

### Project Controller

### File: `taskflow/backend/src/controllers/projectController.js`

- **Purpose**: Manages HTTP requests related to projects.
- **Key Endpoints**:
  - **`list`**: Lists projects for a given organization, optionally including archived projects.
  - **`getOne`**: Retrieves a single project by ID, with checks for existence and organization ownership.
  - **`create`**: Creates a new project for an organization.
  - **`update`**: Updates an existing project, with checks for existence and organization ownership.
  - **`remove`**: Deletes a project, with checks for existence.

### User Controller

### File: `taskflow/backend/src/controllers/userController.js`

- **Purpose**: Manages HTTP requests related to user profiles.
- **Key Endpoints**:
  - **`getProfile`**: Retrieves a user's profile information.
  - **`updateProfile`**: Updates a user's profile information.

### Admin Controller

### File: `taskflow/backend/src/controllers/adminController.js`

- **Purpose**: Manages administrative tasks such as retrieving all users, deleting a user, and getting a billing overview.
- **Key Endpoints**:
  - **`getAllUsers`**: Retrieves all users from the database.
  - **`deleteUser`**: Deletes a user by their ID.
  - **`getBillingOverview`**: Retrieves a billing overview, including user details and project counts.

### Notification Controller

### File: `taskflow/backend/src/controllers/notificationController.js`

- **Purpose**: Manages HTTP requests related to notifications.
- **Key Endpoints**:
  - **`list`**: Lists notifications for a user, with a limit parameter.
  - **`markRead`**: Marks a specific notification as read for a user.
  - **`getPreferences`**: Retrieves notification preferences for a user.
  - **`updatePreferences`**: Updates notification preferences for a user.

### Attachment Controller

### File: `taskflow/backend/src/controllers/attachmentController.js`

- **Purpose**: Manages HTTP requests related to task attachments.
- **Key Endpoints**:
  - **`list`**: Lists all attachments for a given task ID.
  - **`upload`**: Uploads a file as an attachment to a task, storing it in the filesystem and database.
  - **`download`**: Downloads an attachment by its ID, serving the file from the filesystem.
  - **`remove`**: Deletes an attachment by its ID, removing it from the database and filesystem.

## Services

### Notification Service

### File: `taskflow/backend/src/services/notificationService.js`

- **Purpose**: Manages user notifications and preferences.
- **Key Functions**:
  - **`createNotification`**: Creates a new notification.
  - **`getNotifications`**: Retrieves notifications for a user.
  - **`markAsRead`**: Marks a notification as read.
  - **`getPreferences`**: Retrieves notification preferences for a user.
  - **`updatePreferences`**: Updates notification preferences for a user.

### Report Service

### File: `taskflow/backend/src/services/reportService.js`

- **Purpose**: Generates HTML and PDF reports from task data.
- **Key Functions**:
  - **`generateReportHtml`**: Generates an HTML string for a report based on task data.
  - **`generatePdf`**: Generates a PDF report from an HTML string using `wkhtmltopdf` and file system operations.

## Middleware

### Authentication Middleware

### File: `taskflow/backend/src/middleware/authenticate.js`

- **Purpose**: Authenticates HTTP requests by verifying a JWT token in the authorization header.
- **Key Function**:
  - **`authenticate`**: Checks the authorization header and verifies the JWT token, attaching user information to the request object if valid.

### Authorization Middleware

### File: `taskflow/backend/src/middleware/authorize.js`

- **Purpose**: Authorizes user roles in an HTTP request handling chain.
- **Key Function**:
  - **`authorize`**: Checks if the user is authenticated and if their role is among the allowed roles for the requested resource.

### Error Handling Middleware

### File: `taskflow/backend/src/middleware/errorHandler.js`

- **Purpose**: Handles errors in an Express.js application.
- **Key Function**:
  - **`errorHandler`**: Logs the error details and sends a JSON response with the error message, stack trace, and status code.

### File Upload Middleware

### File: `taskflow/backend/src/middleware/upload.js`

- **Purpose**: Configures and exports a multer middleware for handling file uploads.
- **Key Function**:
  - **`upload`**: Configures the upload directory and file naming strategy.

### Rate Limiter Middleware

### File: `taskflow/backend/src/middleware/rateLimiter.js`

- **Purpose**: Limits the rate of report generation requests to prevent abuse.
- **Key Function**:
  - **`reportLimiter`**: Limits the rate of report generation requests to 10 per minute.

## Routes

### Task Routes

### File: `taskflow/backend/src/routes/taskRoutes.js`

- **Purpose**: Defines routes for task management.
- **Key Endpoints**:
  - **`GET /`**: Lists all tasks.
  - **`GET /:taskId/comments`**: Retrieves comments for a specific task.
  - **`POST /:taskId/comments`**: Adds a comment to a specific task.
  - **`GET /:taskId`**: Retrieves a single task by ID.
  - **`POST /`**: Creates a new task.
  - **`PUT /:taskId`**: Updates a task by ID.
  - **`DELETE /:taskId`**: Deletes a task by ID.

### Project Routes

### File: `taskflow/backend/src/routes/projectRoutes.js`

- **Purpose**: Defines routes for project management.
- **Key Endpoints**:
  - **`GET /`**: Lists all projects.
  - **`GET /:projectId`**: Retrieves a single project by ID.
  - **`POST /`**: Creates a new project.
  - **`PUT /:projectId`**: Updates an existing project by ID.
  - **`DELETE /:projectId`**: Deletes a project by ID.

### User Routes

### File: `taskflow/backend/src/routes/userRoutes.js`

- **Purpose**: Defines routes for user profile management.
- **Key Endpoints**:
  - **`GET /profile`**: Retrieves the user's profile information.
  - **`PATCH /profile`**: Updates the user's profile information.

### Admin Routes

### File: `taskflow/backend/src/routes/adminRoutes.js`

- **Purpose**: Defines routes for administrative tasks.
- **Key Endpoints**:
  - **`GET /users`**: Retrieves all users.
  - **`DELETE /users/:id`**: Deletes a user by ID.
  - **`GET /billing`**: Retrieves a billing overview.

### Notification Routes

### File: `taskflow/backend/src/routes/notificationRoutes.js`

- **Purpose**: Defines routes for notification management.
- **Key Endpoints**:
  - **`GET /`**: Lists all notifications for the authenticated user.
  - **`POST /:id/read`**: Marks a specific notification as read for the authenticated user.
  - **`GET /preferences`**: Retrieves the notification preferences for the authenticated user.
  - **`PATCH /preferences`**: Updates the notification preferences for the authenticated user.

### Attachment Routes

### File: `taskflow/backend/src/routes/attachmentRoutes.js`

- **Purpose**: Defines routes for attachment management.
- **Key Endpoints**:
  - **`GET /task/:taskId`**: Lists attachments for a specific task.
  - **`POST /task/:taskId`**: Uploads a new attachment for a specific task.
  - **`GET /:attachmentId`**: Downloads an attachment by its ID.
  - **`DELETE /:attachmentId`**: Deletes an attachment by its ID.

### Import Routes

### File: `taskflow/backend/src/routes/importRoutes.js`

- **Purpose**: Defines routes for importing data into a project.
- **Key Endpoints**:
  - **`POST /project/:projectId/xml`**: Imports XML data into a project.
  - **`POST /project/:projectId/csv`**: Imports CSV data into a project.

### Report Routes

### File: `taskflow/backend/src/routes/reportRoutes.js`

- **Purpose**: Defines routes for generating PDF reports.
- **Key Endpoints**:
  - **`GET /project/:projectId/pdf`**: Generates a PDF for a specific project ID. Requires authentication and is rate-limited.

## Summary

The Data Layer in TaskFlow is designed to handle all database interactions, ensuring that data is managed efficiently and securely. The models provide the necessary functions to interact with the database, while the controllers handle HTTP requests and responses. Middleware components ensure that requests are authenticated and authorized, and error handling is consistent. The routes define the API endpoints, and services provide additional functionality for tasks like generating reports and managing notifications.

---