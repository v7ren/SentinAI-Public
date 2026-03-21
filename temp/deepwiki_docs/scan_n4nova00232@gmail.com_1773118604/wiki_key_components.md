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