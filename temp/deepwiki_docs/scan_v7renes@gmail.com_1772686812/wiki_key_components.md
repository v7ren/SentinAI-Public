# Key Components

This section provides an overview of the main components of the application, including the frontend, backend, and API endpoints. Each component is described in detail, highlighting its role and interactions within the system.

## Frontend

The frontend of the application is built using Next.js, a popular React framework. It includes several key components that handle user interactions, authentication, and data display.

### Tailwind CSS Configuration

- **File**: `vulnerable-server\frontend\tailwind.config.ts`
- **Description**: This file configures the Tailwind CSS setup for the frontend application. It specifies the file paths to scan for CSS class usage and extends the default theme with custom background images.
- **Key Entities**:
  - **Configuration Object**: Exported as the default export and used by Tailwind CSS to generate the final CSS.

### TypeScript Declarations

- **File**: `vulnerable-server\frontend\next-env.d.ts`
- **Description**: This file provides type definitions for the Next.js framework and its image component. It is used by the TypeScript compiler to ensure type safety.
- **Key Entities**:
  - **Type Definitions**: Provides type definitions for the Next.js framework and its components.

### Root Layout

- **File**: `vulnerable-server\frontend\src\app\layout.tsx`
- **Description**: This file defines the root layout for the Next.js application, setting up the basic HTML structure and metadata for the application. It includes a title and description for the metadata and a container for rendering child components.
- **Key Entities**:
  - **RootLayout Component**: Serves as the root layout component that wraps all pages in the Next.js application, providing a consistent structure and metadata.

### Login Page

- **File**: `vulnerable-server\frontend\src\app\login\page.tsx`
- **Description**: This file defines a React component for a login page, which includes a form for users to enter their email and password. It handles form submission, displays errors, and redirects to the dashboard upon successful login. It also provides links to register and to reset the password.
- **Key Entities**:
  - **LoginPage Component**: Handles user input and form submission, interacting with the backend API for authentication.
  - **API Endpoint**: `/api/auth/login` (POST)

### Registration Page

- **File**: `vulnerable-server\frontend\src\app\register\page.tsx`
- **Description**: This file defines a React component for a user registration page. It handles form input for user details, including name, email, password, and an optional company field. The form data is submitted to a backend API for user registration, and upon successful registration, the user is redirected to the login page. Error handling is included to display any issues that occur during the registration process.
- **Key Entities**:
  - **RegisterPage Component**: Handles form submission and interacts with the backend API to register a new user.
  - **API Endpoint**: `/api/auth/register` (POST)

### Landing Page

- **File**: `vulnerable-server\frontend\src\app\page.tsx`
- **Description**: This file defines a React component for the landing page of a project management application called TaskFlow. The page includes a navigation bar, a hero section, features, social proof, pricing, and a footer. It also contains a scroll effect for the navigation bar and a script to run analytics based on URL parameters.
- **Key Entities**:
  - **LandingPage Component**: Main entry point for the landing page component, which is a React functional component.
  - **Analytics Tracking**: Client-side analytics tracking and session detection.

### Admin Panel

- **File**: `vulnerable-server\frontend\src\app\admin\page.tsx`
- **Description**: This file defines a React component for an admin panel, which includes user management, system status, system logs, database query execution, network diagnostics, external data synchronization, and maintenance mode toggling. It fetches data from a backend API and updates the UI accordingly.
- **Key Entities**:
  - **AdminPage Component**: Main React component for the admin panel, which is likely rendered as a route in a Next.js application.
  - **API Endpoints**:
    - `/api/admin/users` (GET, PUT, DELETE)
    - `/api/admin/status` (GET)
    - `/api/admin/logs` (GET)
    - `/api/admin/diagnostics` (GET)
    - `/api/admin/query` (POST)
    - `/api/admin/sync` (GET)
    - `/api/admin/process` (POST)

### Dashboard

- **File**: `vulnerable-server\frontend\src\app\dashboard\page.tsx`
- **Description**: This file defines a React component for a dashboard page in a task management application. It includes functionality for managing tasks, projects, and documents, as well as user settings. The component fetches data from a backend API, handles user interactions, and provides options for creating, importing, and exporting tasks. It also includes a modal for creating new tasks and a sidebar for navigation.
- **Key Entities**:
  - **DashboardPage Component**: Main React component that serves as the entry point for the dashboard page. It handles user authentication, data fetching, and UI rendering.
  - **API Endpoints**:
    - `/api/projects/:userId` (GET)
    - `/api/scans/:userId/:projectId` (GET)
    - `/api/tasks` (POST)
    - `/api/documents/upload` (POST)
    - `/api/bulk/process` (POST)

## Backend

The backend of the application is built using Flask, a lightweight web framework for Python. It provides a RESTful API for user authentication, task and project management, document handling, and administrative functions.

### Flask Application

- **File**: `vulnerable-server\backend\app.py`
- **Description**: This file is a Flask application that provides a RESTful API for a task management system. It includes endpoints for user authentication, task and project management, document handling, and administrative functions. The application uses SQLite for data storage and session management for user authentication.
- **Key Entities**:
  - **API Endpoints**:
    - **User Authentication**:
      - `/api/auth/register` (POST)
      - `/api/auth/login` (POST)
    - **Task Management**:
      - `/api/tasks` (GET, POST)
    - **Project Management**:
      - `/api/projects` (GET, POST)
    - **Search**:
      - `/api/search` (GET)
    - **Integration Testing**:
      - `/api/integrations/test` (GET)
    - **Document Management**:
      - `/api/documents/upload` (POST)
      - `/api/documents/preview` (GET)
      - `/api/documents/download/<path:filename>` (GET)
    - **Task Import**:
      - `/api/import` (POST)
    - **Bulk Data Processing**:
      - `/api/bulk/process` (POST)
    - **Report Exporting**:
      - `/api/reports/export` (GET)
    - **Admin User Management**:
      - `/api/admin/users` (GET, PUT, DELETE)
    - **Admin Status**:
      - `/api/admin/status` (GET)
    - **Admin Logs**:
      - `/api/admin/logs` (GET)
    - **Admin Diagnostics**:
      - `/api/admin/diagnostics` (GET)
    - **Admin Query Execution**:
      - `/api/admin/query` (POST)
    - **Admin Data Synchronization**:
      - `/api/admin/sync` (GET)
    - **Admin Data Processing**:
      - `/api/admin/process` (POST)
    - **Team Member Information**:
      - `/api/team/members/<int:user_id>` (GET)
    - **Analytics**:
      - `/api/analytics/hash` (GET)

### Database and Security

- **Database**: SQLite is used for data storage.
- **Session Management**: Flask's session management is used for user authentication.
- **Security Measures**: The application includes security measures such as JWT token generation for authentication and MD5 hashing for data integrity.

## Interactions and Flows

### User Authentication Flow

1. **Registration**:
   - Users can register by visiting the registration page (`/register`).
   - The form data is submitted to the backend API endpoint `/api/auth/register` (POST).
   - Upon successful registration, the user is redirected to the login page.

2. **Login**:
   - Users can log in by visiting the login page (`/login`).
   - The form data is submitted to the backend API endpoint `/api/auth/login` (POST).
   - Upon successful login, a JWT token is generated and stored in the session.
   - The user is redirected to the dashboard page.

### Task Management Flow

1. **Dashboard**:
   - The dashboard page (`/dashboard`) fetches tasks and projects from the backend API endpoints `/api/projects/:userId` (GET) and `/api/scans/:userId/:projectId` (GET).
   - Users can create new tasks by submitting a form to the `/api/tasks` (POST) endpoint.
   - Users can upload documents by submitting a form to the `/api/documents/upload` (POST) endpoint.

2. **Admin Panel**:
   - The admin panel (`/admin`) fetches user data, system status, and logs from the backend API endpoints `/api/admin/users` (GET), `/api/admin/status` (GET), and `/api/admin/logs` (GET).
   - Admins can manage users by updating or deleting user data using the `/api/admin/users` (PUT, DELETE) endpoints.
   - Admins can run diagnostics by making a request to the `/api/admin/diagnostics` (GET) endpoint.
   - Admins can execute custom SQL queries by submitting a form to the `/api/admin/query` (POST) endpoint.

### Document Management Flow

1. **Document Upload**:
   - Users can upload documents by visiting the dashboard page and submitting a form to the `/api/documents/upload` (POST) endpoint.
   - The uploaded documents are saved to the filesystem, and metadata is recorded in the database.

2. **Document Preview and Download**:
   - Users can preview documents by visiting the dashboard page and making a request to the `/api/documents/preview` (GET) endpoint.
   - Users can download documents by visiting the dashboard page and making a request to the `/api/documents/download/<path:filename>` (GET) endpoint.

### Data Synchronization and Processing

1. **Data Synchronization**:
   - Admins can sync data from an external source by making a request to the `/api/admin/sync` (GET) endpoint.

2. **Data Processing**:
   - Admins can process data by submitting a form to the `/api/admin/process` (POST) endpoint, which evaluates and executes Python code.

### Analytics and Reporting

1. **Analytics**:
   - The landing page includes client-side analytics tracking and session detection.
   - The backend provides an endpoint `/api/analytics/hash` (GET) to generate MD5 hashes of provided data.

2. **Report Exporting**:
   - Admins can export reports by making a request to the `/api/reports/export` (GET) endpoint, which generates files using shell commands.

This overview provides a high-level understanding of the key components and their interactions within the application. Each component plays a crucial role in ensuring a seamless user experience and robust backend functionality.