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