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