# Overview

## What is TaskFlow?

TaskFlow is a project management tool designed to help organizations and teams efficiently manage their tasks, projects, and resources. It provides a comprehensive set of features for task tracking, project collaboration, user management, and reporting. TaskFlow is built using a modern tech stack, including Node.js, Express, PostgreSQL, and React.

## Main Components

### Backend
The backend of TaskFlow is built using Node.js and Express. It provides a RESTful API for various functionalities and is responsible for handling HTTP requests, interacting with the database, and managing user authentication and authorization.

- **Database Configuration (`taskflow/backend/config/db.js`)**: Sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries.
- **Server Setup (`taskflow/backend/server.js`)**: Configures and starts the Node.js server, listening on a specified port.
- **Express Application (`taskflow/backend/src/app.js`)**: Sets up the Express application, including middleware for JSON and text parsing, static file serving, and mounting various API routes.
- **Controllers**: Handle specific business logic and HTTP requests.
  - **Authentication (`taskflow/backend/src/controllers/authController.js`)**: Manages user registration, login, token refresh, password reset, and logout.
  - **Projects (`taskflow/backend/src/controllers/projectController.js`)**: Manages CRUD operations for projects.
  - **Tasks (`taskflow/backend/src/controllers/taskController.js`)**: Manages CRUD operations for tasks and task comments.
  - **Attachments (`taskflow/backend/src/controllers/attachmentController.js`)**: Manages file attachments for tasks.
  - **Reports (`taskflow/backend/src/controllers/reportController.js`)**: Generates PDF reports for projects.
  - **Imports (`taskflow/backend/src/controllers/importController.js`)**: Imports tasks from XML and CSV files.
  - **Admin (`taskflow/backend/src/controllers/adminController.js`)**: Manages administrative tasks like user management and billing.
  - **Notifications (`taskflow/backend/src/controllers/notificationController.js`)**: Manages user notifications and preferences.
  - **Users (`taskflow/backend/src/controllers/userController.js`)**: Manages user profiles.
- **Models**: Define the database schema and provide methods for interacting with the database.
  - **Organizations (`taskflow/backend/src/models/orgModel.js`)**: Manages organization data.
  - **Projects (`taskflow/backend/src/models/projectModel.js`)**: Manages project data.
  - **Tasks (`taskflow/backend/src/models/taskModel.js`)**: Manages task data.
  - **Users (`taskflow/backend/src/models/userModel.js`)**: Manages user data.
- **Middleware**: Handles cross-cutting concerns like authentication, authorization, error handling, and file uploads.
  - **Authentication (`taskflow/backend/src/middleware/authenticate.js`)**: Verifies JWT tokens.
  - **Authorization (`taskflow/backend/src/middleware/authorize.js`)**: Checks user roles.
  - **Error Handling (`taskflow/backend/src/middleware/errorHandler.js`)**: Logs and responds to errors.
  - **File Uploads (`taskflow/backend/src/middleware/upload.js`)**: Configures file upload handling.
  - **Rate Limiting (`taskflow/backend/src/middleware/rateLimiter.js`)**: Limits the rate of report generation requests.
- **Services**: Provide utility functions for common tasks.
  - **Email (`taskflow/backend/src/services/emailService.js`)**: Sends emails using SendGrid.
  - **Notifications (`taskflow/backend/src/services/notificationService.js`)**: Manages user notifications.
  - **Reports (`taskflow/backend/src/services/reportService.js`)**: Generates HTML and PDF reports.
  - **Stripe (`taskflow/backend/src/services/stripeService.js`)**: Interacts with the Stripe API for billing.
- **Utilities**: Provides helper functions for various tasks.
  - **Token Management (`taskflow/backend/src/utils/tokenUtils.js`)**: Generates and verifies JWT tokens.
  - **Object Merging (`taskflow/backend/src/utils/mergeObjects.js`)**: Merges objects deeply.
  - **Logging (`taskflow/backend/src/utils/logger.js`)**: Logs application events.
  - **Validators (`taskflow/backend/src/utils/validators.js`)**: Validates and sanitizes strings.

### Frontend
The frontend of TaskFlow is built using React and provides a user-friendly interface for interacting with the backend API.

- **Main Application (`taskflow/frontend/src/App.jsx`)**: Sets up routing for various pages and handles authentication.
- **API Client (`taskflow/frontend/src/api/client.js`)**: Configures an Axios client for making HTTP requests to the backend API.
- **Pages**: React components for different pages in the application.
  - **Landing Page (`taskflow/frontend/src/pages/LandingPage.jsx`)**: The initial landing page for the application.
  - **Login Page (`taskflow/frontend/src/pages/LoginPage.jsx`)**: Handles user login.
  - **Register Page (`taskflow/frontend/src/pages/RegisterPage.jsx`)**: Handles user registration.
  - **Dashboard Page (`taskflow/frontend/src/pages/DashboardPage.jsx`)**: Displays a dashboard with project and task statistics.
  - **Projects Page (`taskflow/frontend/src/pages/ProjectsPage.jsx`)**: Lists projects and allows creating new projects.
  - **Project Detail Page (`taskflow/frontend/src/pages/ProjectDetailPage.jsx`)**: Displays detailed information about a project.
  - **Tasks Page (`taskflow/frontend/src/pages/TasksPage.jsx`)**: Lists tasks and allows creating new tasks.
  - **Task Detail Page (`taskflow/frontend/src/pages/TaskDetailPage.jsx`)**: Displays detailed information about a task.
  - **Settings Page (`taskflow/frontend/src/pages/SettingsPage.jsx`)**: Allows users to update their profile.
  - **Admin Page (`taskflow/frontend/src/pages/AdminPage.jsx`)**: Manages administrative tasks.
  - **Not Found Page (`taskflow/frontend/src/pages/NotFoundPage.jsx`)**: Displays a 404 error page.
- **Components**: Reusable UI components.
  - **Navbar (`taskflow/frontend/src/components/Layout/Navbar.jsx`)**: Navigation bar with user information and links.
  - **Sidebar (`taskflow/frontend/src/components/Layout/Sidebar.jsx`)**: Navigation sidebar based on user role.
  - **Page Wrapper (`taskflow/frontend/src/components/Layout/PageWrapper.jsx`)**: Provides a consistent layout for pages.
  - **Project Card (`taskflow/frontend/src/components/Projects/ProjectCard.jsx`)**: Displays a card for a project.
  - **Task Card (`taskflow/frontend/src/components/Tasks/TaskCard.jsx`)**: Displays a card for a task.
  - **Task Detail (`taskflow/frontend/src/components/Tasks/TaskDetail.jsx`)**: Displays detailed information about a task.
  - **Comment List (`taskflow/frontend/src/components/Tasks/CommentList.jsx`)**: Displays and manages comments for a task.
  - **Task Form (`taskflow/frontend/src/components/Tasks/TaskForm.jsx`)**: Form for creating or editing a task.
  - **User Table (`taskflow/frontend/src/components/Admin/UserTable.jsx`)**: Displays a table of users.
  - **Button (`taskflow/frontend/src/components/UI/Button.jsx`)**: Reusable button component.
  - **Badge (`taskflow/frontend/src/components/UI/Badge.jsx`)**: Reusable badge component.
  - **Spinner (`taskflow/frontend/src/components/UI/Spinner.jsx`)**: Loading spinner component.
  - **Modal (`taskflow/frontend/src/components/UI/Modal.jsx`)**: Modal dialog component.
- **Hooks**: Custom React hooks for state management and side effects.
  - **useAuth (`taskflow/frontend/src/hooks/useAuth.js`)**: Manages authentication state.
  - **useProjects (`taskflow/frontend/src/hooks/useProjects.js`)**: Manages project data.
  - **useTasks (`taskflow/frontend/src/hooks/useTasks.js`)**: Manages task data.
- **Context**: Provides global state management.
  - **AuthContext (`taskflow/frontend/src/context/AuthContext.jsx`)**: Provides authentication context.
- **Utilities**: Helper functions for various tasks.
  - **Analytics (`taskflow/frontend/src/utils/analytics.js`)**: Tracks events and identifies users in analytics services.
  - **AuthUtils (`taskflow/frontend/src/utils/authUtils.js`)**: Manages authentication sessions in local storage.
  - **Formatters (`taskflow/frontend/src/utils/formatters.js`)**: Formats dates and labels.
- **Configuration**: Configuration files for the frontend.
  - **Vite Configuration (`taskflow/frontend/vite.config.js`)**: Configures the Vite development server.
  - **PostCSS Configuration (`taskflow/frontend/postcss.config.js`)**: Configures PostCSS and Tailwind CSS.

## Typical Usage Scenario

1. **User Registration and Login**:
   - A new user visits the landing page and clicks on the "Register" link.
   - The user fills out the registration form with their full name, email, and password.
   - Upon successful registration, the user is redirected to the login page.
   - The user logs in using their email and password, and the application verifies the credentials with the backend.

2. **Project Management**:
   - After logging in, the user is redirected to the dashboard, which displays an overview of their projects and tasks.
   - The user can navigate to the "Projects" page to view a list of all projects.
   - The user can create a new project by clicking the "Create Project" button, which opens a modal form.
   - Once a project is created, the user can navigate to the project detail page to view and manage tasks within the project.

3. **Task Management**:
   - On the project detail page, the user can see a list of tasks associated with the project.
   - The user can create a new task by clicking the "Create Task" button, which opens a modal form.
   - The user can update the status, priority, and due date of a task.
   - The user can add comments to a task and view comments from other team members.

4. **Admin Functions**:
   - Admin users can navigate to the admin page to manage users and billing.
   - The admin can view a list of all users, delete users, and view a billing overview.

5. **Notifications**:
   - Users receive notifications for important events, such as new tasks, comments, and project updates.
   - Users can manage their notification preferences in the settings page.

6. **Reporting**:
   - Users can generate PDF reports for projects by navigating to the project detail page and clicking the "Generate Report" button.
   - The report includes a summary of the project and its tasks, and is sent as a downloadable PDF.

## Where to Look Next

- **Backend**:
  - **Database Configuration**: `taskflow/backend/config/db.js`
  - **Server Setup**: `taskflow/backend/server.js`
  - **Controllers**: `taskflow/backend/src/controllers/*.js`
  - **Models**: `taskflow/backend/src/models/*.js`
  - **Middleware**: `taskflow/backend/src/middleware/*.js`
  - **Services**: `taskflow/backend/src/services/*.js`
  - **Utilities**: `taskflow/backend/src/utils/*.js`

- **Frontend**:
  - **Main Application**: `taskflow/frontend/src/App.jsx`
  - **API Client**: `taskflow/frontend/src/api/client.js`
  - **Pages**: `taskflow/frontend/src/pages/*.jsx`
  - **Components**: `taskflow/frontend/src/components/*.jsx`
  - **Hooks**: `taskflow/frontend/src/hooks/*.js`
  - **Context**: `taskflow/frontend/src/context/*.jsx`
  - **Utilities**: `taskflow/frontend/src/utils/*.js`
  - **Configuration**: `taskflow/frontend/vite.config.js`, `taskflow/frontend/postcss.config.js`

For more detailed information on specific components and functionalities, refer to the corresponding sections in the documentation.

---

# Architecture and Data Flow

## Overview

The TaskFlow application is a web-based project management tool built using a combination of Node.js, Express, PostgreSQL, and React. The architecture is designed to be modular, scalable, and maintainable, with clear separation of concerns between different components. This section provides an overview of the main architectural components, data flow, and important patterns used in the application.

## Main Architectural Components

### Backend

1. **Database Layer**
   - **File:** `taskflow/backend/config/db.js`
   - **Description:** Sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries.
   - **Key Functions:**
     - `query`: Executes SQL queries using the configured database pool.

2. **Express Application**
   - **File:** `taskflow/backend/src/app.js`
   - **Description:** Sets up an Express application, configures middleware, and mounts various API routes.
   - **Key Functions:**
     - Middleware for JSON and text parsing, serving static files, and error handling.
     - Mounts routes for authentication, tasks, projects, users, attachments, reports, imports, notifications, and admin functionalities.

3. **Server**
   - **File:** `taskflow/backend/server.js`
   - **Description:** Sets up and starts the Node.js server using the Express application.
   - **Key Functions:**
     - `app.listen`: Starts the Express application and listens on the specified port.

4. **Controllers**
   - **Files:**
     - `taskflow/backend/src/controllers/reportController.js`
     - `taskflow/backend/src/controllers/adminController.js`
     - `taskflow/backend/src/controllers/importController.js`
     - `taskflow/backend/src/controllers/attachmentController.js`
     - `taskflow/backend/src/controllers/notificationController.js`
     - `taskflow/backend/src/controllers/projectController.js`
     - `taskflow/backend/src/controllers/authController.js`
     - `taskflow/backend/src/controllers/taskController.js`
     - `taskflow/backend/src/controllers/userController.js`
   - **Description:** Handle HTTP requests and interact with the database or other services to perform business logic.
   - **Key Functions:**
     - `generatePdf`, `getAllUsers`, `importXml`, `list`, `markRead`, `create`, `register`, `addComment`, `updateProfile`, etc.

5. **Models**
   - **Files:**
     - `taskflow/backend/src/models/orgModel.js`
     - `taskflow/backend/src/models/projectModel.js`
     - `taskflow/backend/src/models/taskModel.js`
     - `taskflow/backend/src/models/userModel.js`
   - **Description:** Define the structure and operations for interacting with the database.
   - **Key Functions:**
     - `findById`, `create`, `update`, `remove`, etc.

6. **Services**
   - **Files:**
     - `taskflow/backend/src/services/notificationService.js`
     - `taskflow/backend/src/services/emailService.js`
     - `taskflow/backend/src/services/reportService.js`
     - `taskflow/backend/src/services/stripeService.js`
   - **Description:** Provide higher-level business logic and interact with external services.
   - **Key Functions:**
     - `createNotification`, `sendInvite`, `generateReportHtml`, `createCustomer`, etc.

7. **Middlewares**
   - **Files:**
     - `taskflow/backend/src/middleware/authenticate.js`
     - `taskflow/backend/src/middleware/authorize.js`
     - `taskflow/backend/src/middleware/errorHandler.js`
     - `taskflow/backend/src/middleware/upload.js`
     - `taskflow/backend/src/middleware/rateLimiter.js`
   - **Description:** Handle cross-cutting concerns such as authentication, authorization, error handling, file uploads, and rate limiting.
   - **Key Functions:**
     - `authenticate`, `authorize`, `errorHandler`, `upload`, `reportLimiter`, etc.

### Frontend

1. **React Application**
   - **File:** `taskflow/frontend/src/main.jsx`
   - **Description:** The entry point for the React application, setting up the React DOM, routing, and authentication context.
   - **Key Components:**
     - `AuthProvider`: Provides authentication context to the application.
     - `BrowserRouter`: Configures routing for the application.

2. **Pages**
   - **Files:**
     - `taskflow/frontend/src/pages/AdminPage.jsx`
     - `taskflow/frontend/src/pages/DashboardPage.jsx`
     - `taskflow/frontend/src/pages/NotFoundPage.jsx`
     - `taskflow/frontend/src/pages/LandingPage.jsx`
     - `taskflow/frontend/src/pages/LoginPage.jsx`
     - `taskflow/frontend/src/pages/ProjectDetailPage.jsx`
     - `taskflow/frontend/src/pages/TaskDetailPage.jsx`
     - `taskflow/frontend/src/pages/ProjectsPage.jsx`
     - `taskflow/frontend/src/pages/SettingsPage.jsx`
     - `taskflow/frontend/src/pages/TasksPage.jsx`
     - `taskflow/frontend/src/pages/RegisterPage.jsx`
   - **Description:** Define the main pages of the application, handling user interactions and displaying data.
   - **Key Components:**
     - `AdminPage`, `DashboardPage`, `NotFoundPage`, `LandingPage`, `LoginPage`, `ProjectDetailPage`, `TaskDetailPage`, `ProjectsPage`, `SettingsPage`, `TasksPage`, `RegisterPage`, etc.

3. **Components**
   - **Files:**
     - `taskflow/frontend/src/components/Admin/UserTable.jsx`
     - `taskflow/frontend/src/components/Layout/Navbar.jsx`
     - `taskflow/frontend/src/components/Layout/Sidebar.jsx`
     - `taskflow/frontend/src/components/Layout/PageWrapper.jsx`
     - `taskflow/frontend/src/components/Projects/ProjectCard.jsx`
     - `taskflow/frontend/src/components/Tasks/TaskCard.jsx`
     - `taskflow/frontend/src/components/Projects/ProjectSettings.jsx`
     - `taskflow/frontend/src/components/Tasks/CommentList.jsx`
     - `taskflow/frontend/src/components/Tasks/TaskDetail.jsx`
     - `taskflow/frontend/src/components/UI/Badge.jsx`
     - `taskflow/frontend/src/components/UI/Button.jsx`
     - `taskflow/frontend/src/components/Tasks/TaskForm.jsx`
     - `taskflow/frontend/src/components/UI/Spinner.jsx`
     - `taskflow/frontend/src/components/UI/Modal.jsx`
   - **Description:** Reusable UI components for building the application's user interface.
   - **Key Components:**
     - `UserTable`, `Navbar`, `Sidebar`, `PageWrapper`, `ProjectCard`, `TaskCard`, `ProjectSettings`, `CommentList`, `TaskDetail`, `Badge`, `Button`, `TaskForm`, `Spinner`, `Modal`, etc.

4. **API Client**
   - **File:** `taskflow/frontend/src/api/client.js`
   - **Description:** Sets up an Axios client for making HTTP requests to the backend API.
   - **Key Functions:**
     - `client`: Configured Axios instance with interceptors for adding authentication tokens and handling unauthorized responses.

5. **API Services**
   - **Files:**
     - `taskflow/frontend/src/api/admin.js`
     - `taskflow/frontend/src/api/auth.js`
     - `taskflow/frontend/src/api/projects.js`
     - `taskflow/frontend/src/api/tasks.js`
   - **Description:** Define functions for making HTTP requests to the backend API.
   - **Key Functions:**
     - `getAllUsers`, `login`, `list`, `getOne`, `create`, `update`, `remove`, etc.

6. **Contexts and Hooks**
   - **Files:**
     - `taskflow/frontend/src/context/AuthContext.jsx`
     - `taskflow/frontend/src/hooks/useAuth.js`
     - `taskflow/frontend/src/hooks/useProjects.js`
     - `taskflow/frontend/src/hooks/useTasks.js`
   - **Description:** Provide state management and reusable logic for the application.
   - **Key Functions:**
     - `AuthProvider`, `useAuth`, `useProjects`, `useTasks`, etc.

## Data and Control Flow

### Backend

1. **Request Handling**
   - **Entry Point:** `taskflow/backend/server.js`
   - **Flow:**
     1. The server starts and listens for incoming HTTP requests.
     2. Requests are routed to the appropriate controller based on the URL and HTTP method.
     3. Controllers handle the business logic, interact with the database or other services, and return responses.

2. **Authentication and Authorization**
   - **Middlewares:**
     - `authenticate`: Verifies the JWT token in the Authorization header and attaches user information to the request object.
     - `authorize`: Checks if the user has the required role to access the resource.
   - **Flow:**
     1. The `authenticate` middleware is applied to protected routes.
     2. If the token is valid, the user information is attached to the request.
     3. The `authorize` middleware checks if the user has the required role.
     4. If the user is authorized, the request is passed to the controller.

3. **Database Operations**
   - **Models:**
     - `orgModel`, `projectModel`, `taskModel`, `userModel`
   - **Flow:**
     1. Controllers call model functions to perform database operations.
     2. Model functions execute SQL queries using the database connection pool.
     3. Results are returned to the controllers, which format and send the responses.

4. **Service Interactions**
   - **Services:**
     - `notificationService`, `emailService`, `reportService`, `stripeService`
   - **Flow:**
     1. Controllers call service functions to perform higher-level business logic.
     2. Service functions interact with external services or other parts of the application.
     3. Results are returned to the controllers, which format and send the responses.

### Frontend

1. **Application Initialization**
   - **Entry Point:** `taskflow/frontend/src/main.jsx`
   - **Flow:**
     1. The React application is initialized and the `AuthProvider` is set up.
     2. Routing is configured using `BrowserRouter`.
     3. The main component (`App`) is rendered.

2. **Routing and Page Rendering**
   - **Pages:**
     - `AdminPage`, `DashboardPage`, `NotFoundPage`, `LandingPage`, `LoginPage`, `ProjectDetailPage`, `TaskDetailPage`, `ProjectsPage`, `SettingsPage`, `TasksPage`, `RegisterPage`
   - **Flow:**
     1. The router matches the URL to the appropriate page component.
     2. Page components are rendered, and data is fetched from the API if necessary.
     3. User interactions trigger state changes and API calls.

3. **API Requests**
   - **API Client:**
     - `client`
   - **Flow:**
     1. Page components or custom hooks call API functions to fetch or update data.
     2. The API client adds authentication tokens to the requests.
     3. Responses are handled and state is updated accordingly.

4. **State Management**
   - **Contexts and Hooks:**
     - `AuthProvider`, `useAuth`, `useProjects`, `useTasks`
   - **Flow:**
     1. The `AuthProvider` provides authentication state to the application.
     2. Custom hooks (`useAuth`, `useProjects`, `useTasks`) manage state and side effects for specific features.
     3. Components use these hooks to access and update state.

## Important Patterns

1. **Model-View-Controller (MVC)**
   - **Controllers:** Handle HTTP requests and business logic.
   - **Models:** Define the structure and operations for interacting with the database.
   - **Views:** Render the user interface and handle user interactions.

2. **Middleware Pattern**
   - **Express Middleware:** Handles cross-cutting concerns such as authentication, authorization, error handling, and file uploads.
   - **Custom Middleware:** Provides additional functionality like rate limiting and logging.

3. **Service Layer**
   - **Services:** Encapsulate higher-level business logic and interactions with external services.
   - **Separation of Concerns:** Keeps controllers and models focused on their primary responsibilities.

4. **Context and Hooks**
   - **React Context:** Provides a way to manage global state and share it across components.
   - **Custom Hooks:** Encapsulate reusable logic and state management for specific features.

5. **API Client**
   - **Axios Client:** Configured with interceptors for adding authentication tokens and handling unauthorized responses.
   - **Centralized API Calls:** Simplifies making HTTP requests and handling responses.

By following these patterns and maintaining a clear separation of concerns, the TaskFlow application is designed to be modular, scalable, and easy to maintain.

---

# Key Components

This section details the main components of the TaskFlow application, including the backend server, database, and frontend. Each component plays a crucial role in the overall functionality and architecture of the application.

## Backend Server

### Server Setup
- **File**: `taskflow/backend/server.js`
- **Summary**: This file sets up and starts a Node.js server using an Express application defined in `./src/app`. It configures the server to listen on a specified port, defaulting to 3001 if not provided in the environment variables.
- **Key Functions**:
  - `app.listen`: Starts the Express application and listens on the specified port.

### Express Application
- **File**: `taskflow/backend/src/app.js`
- **Summary**: This file sets up an Express application, configures middleware for JSON and text parsing, serves static files from the uploads directory, and mounts various API routes for authentication, tasks, projects, users, attachments, reports, imports, notifications, and admin functionalities. It also includes a health check endpoint and an error handler middleware.
- **Key Routes**:
  - `/api/v1/health`: Health check endpoint that returns a JSON object with a status and timestamp.
  - Various API routes for different functionalities (e.g., `/api/v1/auth`, `/api/v1/projects`, `/api/v1/tasks`, etc.).

## Database

### Database Configuration
- **File**: `taskflow/backend/config/db.js`
- **Summary**: This file sets up a PostgreSQL database connection pool and provides a query function to execute SQL queries. It uses environment variables for configuration, with fallbacks for local development.
- **Key Functions**:
  - `query`: A function that executes SQL queries using the configured database pool.

### Models
- **Files**: `taskflow/backend/src/models/*.js`
- **Summary**: These files define asynchronous functions for interacting with the database tables, including `orgs`, `projects`, `tasks`, `users`, and `notifications`.
- **Key Models**:
  - `orgModel`: Functions for managing organizations and their members.
  - `projectModel`: Functions for managing projects.
  - `taskModel`: Functions for managing tasks.
  - `userModel`: Functions for managing users.
  - `notificationModel`: Functions for managing notifications.

## Frontend

### Main Application
- **File**: `taskflow/frontend/src/main.jsx`
- **Summary**: This file is the entry point for the React application. It sets up the React DOM, configures routing with `BrowserRouter`, and provides authentication context to the application through `AuthProvider`.
- **Key Components**:
  - `AuthProvider`: Provides authentication context to its children.
  - `App`: The main entry point of the application, which renders the routing configuration.

### Authentication
- **File**: `taskflow/frontend/src/context/AuthContext.jsx`
- **Summary**: This file defines an authentication context for a React application, providing state management and functions for user login, registration, and logout. It uses a custom API for authentication and utility functions to manage session storage.
- **Key Functions**:
  - `AuthProvider`: Provides authentication context to its children.
  - `useAuth`: A custom hook that allows components to access the authentication context.

### API Client
- **File**: `taskflow/frontend/src/api/client.js`
- **Summary**: This file sets up an Axios client for making HTTP requests to a backend API. It includes interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to the login page.
- **Key Functions**:
  - `client`: The Axios client instance configured with interceptors.

### Pages
- **Files**: `taskflow/frontend/src/pages/*.jsx`
- **Summary**: These files define React components for various pages in the application, including the landing page, login page, registration page, dashboard, project detail page, task detail page, and settings page.
- **Key Pages**:
  - `LandingPage`: The landing page of the application.
  - `LoginPage`: The login page for user authentication.
  - `RegisterPage`: The registration page for new users.
  - `DashboardPage`: The dashboard page displaying project and task statistics.
  - `ProjectDetailPage`: The page for viewing detailed information about a project.
  - `TaskDetailPage`: The page for viewing detailed information about a task.
  - `SettingsPage`: The page for updating user settings.

### Components
- **Files**: `taskflow/frontend/src/components/*.jsx`
- **Summary**: These files define reusable React components for various UI elements, including navigation, project and task cards, modals, buttons, and badges.
- **Key Components**:
  - `Navbar`: The navigation bar for the application.
  - `Sidebar`: The sidebar for navigation links.
  - `PageWrapper`: A layout component that includes a sidebar, navbar, and main content area.
  - `ProjectCard`: A card component for displaying project information.
  - `TaskCard`: A card component for displaying task information.
  - `Modal`: A modal dialog component.
  - `Button`: A reusable button component.
  - `Badge`: A badge component for displaying status and priority.

### Custom Hooks
- **Files**: `taskflow/frontend/src/hooks/*.js`
- **Summary**: These files define custom React hooks for managing state and side effects, including project and task data.
- **Key Hooks**:
  - `useAuth`: A hook for managing authentication state.
  - `useProjects`: A hook for managing project data.
  - `useTasks`: A hook for managing task data.

### Utilities
- **Files**: `taskflow/frontend/src/utils/*.js`
- **Summary**: These files contain utility functions for various tasks, including authentication, date formatting, and analytics.
- **Key Utilities**:
  - `authUtils`: Functions for managing authentication sessions in local storage.
  - `formatters`: Functions for formatting dates and labels.
  - `analytics`: Functions for tracking events and identifying users in Mixpanel and Google Analytics.

### Vite Configuration
- **File**: `taskflow/frontend/vite.config.js`
- **Summary**: This file configures the Vite development server for the React application, setting up port 3000 and proxying API and uploads requests to a backend server running on port 3001.
- **Key Configuration**:
  - Port 3000 for the development server.
  - Proxy configuration for API and uploads routes.

By understanding these key components, you can better navigate and maintain the TaskFlow application, ensuring that each part works seamlessly together to provide a robust and efficient project management tool.

---

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

---

# Frontend

The frontend of the TaskFlow application is built using React and follows a structured architecture to manage components, routing, state, and UI elements. This section covers the key components, routing, state management, and UI elements used in the TaskFlow frontend.

## Components

### Main Application Component
- **File**: `taskflow\frontend\src\App.jsx`
- **Description**: The main entry point of the React application. It sets up routing for various pages, including public and private routes. Private routes require user authentication, redirecting unauthenticated users to the login page.
- **Key Features**:
  - **Routing**: Uses `react-router-dom` to define routes for landing, login, registration, dashboard, projects, tasks, settings, admin, and a not found page.
  - **Authentication**: Protects certain routes using a `PrivateRoute` component that checks user authentication.

### Layout Components
- **Navbar**
  - **File**: `taskflow\frontend\src\components\Layout\Navbar.jsx`
  - **Description**: Displays a navigation bar with links to the dashboard, user settings, and a logout button. It uses the `useAuth` hook to manage authentication state.
- **Sidebar**
  - **File**: `taskflow\frontend\src\components\Layout\Sidebar.jsx`
  - **Description**: Displays navigation links based on the user's role. It uses the `useAuth` hook to determine if the user is an admin and conditionally adds an admin link.
- **PageWrapper**
  - **File**: `taskflow\frontend\src\components\Layout\PageWrapper.jsx`
  - **Description**: Provides a consistent layout with a sidebar, navbar, and a main content area. It accepts children and title as props.

### Page Components
- **LandingPage**
  - **File**: `taskflow\frontend\src\pages\LandingPage.jsx`
  - **Description**: The landing page for the TaskFlow application, including navigation links, a hero section, features, pricing, and testimonials.
- **LoginPage**
  - **File**: `taskflow\frontend\src\pages\LoginPage.jsx`
  - **Description**: Handles user login, including form fields for email and password, and redirects upon successful authentication.
- **RegisterPage**
  - **File**: `taskflow\frontend\src\pages\RegisterPage.jsx`
  - **Description**: Handles user registration, including form fields for full name, email, and password, and redirects upon successful registration.
- **DashboardPage**
  - **File**: `taskflow\frontend\src\pages\DashboardPage.jsx`
  - **Description**: Displays a dashboard with statistics about open tasks, overdue tasks, and projects. It also shows a list of recent tasks and provides a button to navigate to the task creation page.
- **ProjectsPage**
  - **File**: `taskflow\frontend\src\pages\ProjectsPage.jsx`
  - **Description**: Displays a list of projects and provides a modal for creating new projects. It uses the `useProjects` hook to fetch and manage project data.
- **ProjectDetailPage**
  - **File**: `taskflow\frontend\src\pages\ProjectDetailPage.jsx`
  - **Description**: Displays details of a specific project, including settings. It fetches project data from an API and handles loading and error states.
- **TasksPage**
  - **File**: `taskflow\frontend\src\pages\TasksPage.jsx`
  - **Description**: Displays a list of tasks, allows filtering by project and search term, and includes a modal for creating new tasks.
- **TaskDetailPage**
  - **File**: `taskflow\frontend\src\pages\TaskDetailPage.jsx`
  - **Description**: Displays detailed information about a specific task, including its status, priority, due date, title, and description. It fetches the task data from an API endpoint.
- **SettingsPage**
  - **File**: `taskflow\frontend\src\pages\SettingsPage.jsx`
  - **Description**: Allows users to update their profile information, specifically their full name. It uses React hooks for state management and authentication, and makes an API call to update the user's profile.
- **AdminPage**
  - **File**: `taskflow\frontend\src\pages\AdminPage.jsx`
  - **Description**: Displays a table of users using the `UserTable` component, wrapped in a `PageWrapper` component.

### UI Components
- **Badge**
  - **File**: `taskflow\frontend\src\components\UI\Badge.jsx`
  - **Description**: Displays a badge with different styles based on the variant prop.
- **Button**
  - **File**: `taskflow\frontend\src\components\UI\Button.jsx`
  - **Description**: A reusable button component that accepts props for customizing the button's appearance and behavior.
- **Spinner**
  - **File**: `taskflow\frontend\src\components\UI\Spinner.jsx`
  - **Description**: Displays a spinning circle to indicate loading states.
- **Modal**
  - **File**: `taskflow\frontend\src\components\UI\Modal.jsx`
  - **Description**: Displays a modal dialog when the `open` prop is true, and can be closed by clicking outside the dialog or by clicking the close button.

### Task and Project Components
- **ProjectCard**
  - **File**: `taskflow\frontend\src\components\Projects\ProjectCard.jsx`
  - **Description**: Displays a card for a project, including the project's name, a truncated description, and an archived status if applicable. The card is a clickable link that navigates to the project's detail page.
- **ProjectSettings**
  - **File**: `taskflow\frontend\src\components\Projects\ProjectSettings.jsx`
  - **Description**: Allows users to update the name, description, and archived status of a project. It uses the `useProjects` hook to handle project updates and provides a form for user input.
- **TaskCard**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskCard.jsx`
  - **Description**: Displays a card for a task, including the task's title, status, priority, due date, and assignee name. It uses badges to visually represent the status and priority of the task. The card is a clickable link that navigates to the task's detail page.
- **TaskForm**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskForm.jsx`
  - **Description**: Used to create or edit a task, including form fields for the task's title, description, priority, status, and due date. The form can be submitted to save the task or canceled to close the form.
- **TaskDetail**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskDetail.jsx`
  - **Description**: Displays detailed information about a specific task, including its status, priority, due date, title, and description. It fetches the task data from an API endpoint and handles loading and error states.
- **CommentList**
  - **File**: `taskflow\frontend\src\components\Tasks\CommentList.jsx`
  - **Description**: Displays a list of comments for a given task and allows users to add new comments. It fetches comments from an API and updates the list when new comments are posted.

## Routing

- **Main Application Entry Point**
  - **File**: `taskflow\frontend\src\main.jsx`
  - **Description**: Sets up the React application, including the root component, routing with `BrowserRouter`, and provides authentication context to the application through `AuthProvider`.

## State Management

- **useAuth**
  - **File**: `taskflow\frontend\src\hooks\useAuth.js`
  - **Description**: A React hook for managing authentication state, re-exported from `AuthContext`.
- **useProjects**
  - **File**: `taskflow\frontend\src\hooks\useProjects.js`
  - **Description**: A custom React hook that provides state management and API interaction for projects data. It includes functions to fetch, create, update, and delete projects.
- **useTasks**
  - **File**: `taskflow\frontend\src\hooks\useTasks.js`
  - **Description**: A custom React hook that provides state management and API interaction for tasks within a project. It includes functions to fetch, create, update, and delete tasks.

## API Client

- **API Client**
  - **File**: `taskflow\frontend\src\api\client.js`
  - **Description**: Sets up an Axios client for making HTTP requests to a backend API. It includes interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to the login page.

## Authentication Context

- **AuthContext**
  - **File**: `taskflow\frontend\src\context\AuthContext.jsx`
  - **Description**: Provides authentication context to the application, including state management and functions for user login, registration, and logout. It uses a custom API for authentication and utility functions to manage session storage.

## Utilities

- **Formatters**
  - **File**: `taskflow\frontend\src\utils\formatters.js`
  - **Description**: Contains utility functions for formatting dates and labels, including functions to format dates in a specific locale, format dates relative to the current time, and format priority and status labels.
- **AuthUtils**
  - **File**: `taskflow\frontend\src\utils\authUtils.js`
  - **Description**: Contains utility functions for managing authentication sessions in local storage, including saving, clearing, and retrieving session tokens and user data.
- **Analytics**
  - **File**: `taskflow\frontend\src\utils\analytics.js`
  - **Description**: Contains utility functions for tracking events and identifying users in Mixpanel and Google Analytics.

## Development Configuration

- **Vite Configuration**
  - **File**: `taskflow\frontend\vite.config.js`
  - **Description**: Configures the Vite development server for the React application, setting up port 3000 and proxying API and uploads requests to a backend server running on port 3001.

This structured approach ensures that the frontend of the TaskFlow application is modular, maintainable, and scalable, providing a seamless user experience with robust state management and authentication.

---