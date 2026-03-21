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