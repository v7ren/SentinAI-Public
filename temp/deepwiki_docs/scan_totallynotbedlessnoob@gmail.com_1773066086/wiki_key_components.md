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