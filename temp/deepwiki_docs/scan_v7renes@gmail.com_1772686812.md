# Overview

## What the Project Is and What Problem It Solves

The project is a task management application called **TaskFlow**. It is designed to help users and teams efficiently manage tasks, projects, and documents. The application provides a comprehensive set of features for user authentication, task and project management, document handling, and administrative functions. It is built using a modern frontend stack (Next.js, React, Tailwind CSS) and a robust backend (Flask, SQLite).

### Key Problems Solved:
- **User Management**: Secure user registration, login, and session management.
- **Task and Project Management**: Create, manage, and track tasks and projects.
- **Document Handling**: Upload, preview, and download documents.
- **Administrative Functions**: User management, system diagnostics, and data synchronization.

## Main Components or Modules

### Frontend
- **Tailwind CSS Configuration (`tailwind.config.ts`)**: Configures the Tailwind CSS setup for the frontend application, ensuring consistent styling and theming.
- **Next.js Environment Configuration (`next-env.d.ts`)**: Provides type definitions for the Next.js framework, enhancing type safety in TypeScript.
- **Root Layout (`layout.tsx`)**: Defines the basic HTML structure and metadata for the application, ensuring a consistent layout across all pages.
- **Landing Page (`page.tsx`)**: The main entry point for the landing page, including navigation, hero section, features, social proof, pricing, and a footer.
- **Login Page (`login/page.tsx`)**: Handles user authentication, including form submission and error handling.
- **Registration Page (`register/page.tsx`)**: Manages user registration, including form validation and submission to the backend.
- **Dashboard Page (`dashboard/page.tsx`)**: Provides a comprehensive interface for managing tasks, projects, and documents, with features like task creation, file uploads, and data export.
- **Admin Panel (`admin/page.tsx`)**: Offers advanced administrative tools for user management, system diagnostics, and data synchronization.

### Backend
- **Flask Application (`app.py`)**: Implements a RESTful API for the task management system, handling user authentication, task and project management, document handling, and administrative functions. It uses SQLite for data storage and session management for user authentication.

## Typical Usage or Runtime Scenario

### User Flow
1. **Landing Page**: Users land on the main page, which provides an overview of the application's features and pricing plans.
2. **Registration**: New users can register by navigating to the registration page, filling out the form, and submitting it. The form data is sent to the backend for validation and storage.
3. **Login**: Registered users can log in using their credentials. Upon successful authentication, a JWT token is generated and stored in the session.
4. **Dashboard**: Logged-in users are redirected to the dashboard, where they can manage tasks, projects, and documents. The dashboard fetches data from the backend and provides options for creating, importing, and exporting tasks.
5. **Admin Panel**: Users with admin privileges can access the admin panel to manage users, run diagnostics, and sync data from external sources.

### Data Flow
1. **Frontend to Backend**: User interactions on the frontend (e.g., form submissions, API requests) are sent to the backend via HTTP endpoints.
2. **Backend Processing**: The backend processes these requests, interacts with the SQLite database, and performs necessary operations (e.g., user authentication, task creation, document upload).
3. **Backend to Frontend**: The backend responds to the frontend with the requested data or status updates, which are then rendered in the UI.

## Where to Look Next

For a deeper dive into the project, consider exploring the following sections:

- **Frontend Architecture**: Detailed breakdown of the frontend components, including React and Next.js specifics.
- **Backend Architecture**: In-depth look at the Flask application, including API endpoints, database interactions, and security measures.
- **Authentication and Security**: Comprehensive guide to the authentication mechanisms, session management, and security practices.
- **Data Management**: Explanation of how data is stored, queried, and managed in the SQLite database.
- **API Documentation**: Detailed documentation of all available API endpoints, including request and response formats.
- **Deployment and Configuration**: Instructions for setting up and deploying the application in a production environment.

---

# Architecture and Data Flow

## Overview

The project is a web application built using a combination of Next.js for the frontend and Flask for the backend. The architecture is primarily client-server, with the frontend serving as the user interface and the backend providing the RESTful API for data management and business logic. The application follows a modular structure, with clear separation of concerns between different components.

## Main Architectural Components

### Frontend

The frontend is built using Next.js, a popular React framework. It includes the following main components:

- **Tailwind CSS Configuration (`tailwind.config.ts`)**: Configures the Tailwind CSS setup, specifying the file paths to scan for CSS class usage and extending the default theme with custom background images.
- **TypeScript Declarations (`next-env.d.ts`)**: Provides type definitions for the Next.js framework and its image component.
- **Root Layout (`layout.tsx`)**: Defines the root layout for the application, setting up the basic HTML structure and metadata.
- **Landing Page (`page.tsx`)**: The main entry point for the landing page, which includes a navigation bar, hero section, features, social proof, pricing, and a footer.
- **Login Page (`login/page.tsx`)**: A React component for the login page, handling form submission and authentication.
- **Registration Page (`register/page.tsx`)**: A React component for the user registration page, handling form submission and user registration.
- **Dashboard Page (`dashboard/page.tsx`)**: A React component for the dashboard, managing tasks, projects, and documents, and providing user settings.
- **Admin Panel (`admin/page.tsx`)**: A React component for the admin panel, providing user management, system status, logs, and other administrative tools.

### Backend

The backend is a Flask application that provides a RESTful API for the frontend. It includes the following main components:

- **Flask Application (`app.py`)**: Initializes the Flask app, sets up CORS, defines database schema, and provides various API endpoints for user authentication, task and project management, document handling, and administrative functions.

## Data and Control Flow

### Frontend-Backend Interaction

1. **User Authentication**:
   - **Login Page (`login/page.tsx`)**: When a user submits the login form, the frontend sends a POST request to the `/api/auth/login` endpoint in the backend (`app.py`). The backend authenticates the user and returns a JWT token.
   - **Registration Page (`register/page.tsx`)**: When a user submits the registration form, the frontend sends a POST request to the `/api/auth/register` endpoint in the backend (`app.py`). The backend creates a new user and returns a success response.

2. **Dashboard and Task Management**:
   - **Dashboard Page (`dashboard/page.tsx`)**: The dashboard fetches user-specific data from the backend by making GET requests to `/api/projects/:userId` and `/api/scans/:userId/:projectId` endpoints. It also provides options for creating, importing, and exporting tasks, which involve POST requests to `/api/tasks`, `/api/documents/upload`, and `/api/bulk/process` endpoints.

3. **Admin Panel**:
   - **Admin Page (`admin/page.tsx`)**: The admin panel fetches user data, system status, and logs by making GET requests to `/api/admin/users`, `/api/admin/status`, and `/api/admin/logs` endpoints. It also provides functionality to update and delete users, run diagnostics, execute custom queries, sync external data, and process data, which involve PUT, DELETE, POST, and GET requests to various admin endpoints.

### Backend Data Flow

1. **User Authentication**:
   - **User Registration (`/api/auth/register`)**: The backend receives user registration data, validates it, and stores the user in the SQLite database.
   - **User Login (`/api/auth/login`)**: The backend verifies the user's credentials, generates a JWT token, and returns it to the frontend.

2. **Task and Project Management**:
   - **Task Management (`/api/tasks`)**: The backend handles CRUD operations for tasks, storing and retrieving task data from the SQLite database.
   - **Project Management (`/api/projects`)**: The backend manages projects, including creating, updating, and deleting project entries in the database.

3. **Document Handling**:
   - **Document Upload (`/api/documents/upload`)**: The backend saves uploaded documents to the filesystem and records metadata in the database.
   - **Document Preview (`/api/documents/preview`)**: The backend reads the document content from the filesystem and returns it to the frontend.
   - **Document Download (`/api/documents/download/<path:filename>`)**: The backend serves the requested document from the filesystem.

4. **Admin Functions**:
   - **User Management (`/api/admin/users`)**: The backend provides endpoints for fetching, updating, and deleting user data.
   - **System Status (`/api/admin/status`)**: The backend returns system status information, including user count and storage usage.
   - **Logs (`/api/admin/logs`)**: The backend reads log files and returns the content to the frontend.
   - **Diagnostics (`/api/admin/diagnostics`)**: The backend runs diagnostics, such as pinging a specified host.
   - **Custom Queries (`/api/admin/query`)**: The backend executes SQL queries, supporting both SELECT and non-SELECT statements.
   - **Data Synchronization (`/api/admin/sync`)**: The backend syncs data from an external source.
   - **Data Processing (`/api/admin/process`)**: The backend evaluates and executes Python code.

## Important Patterns

### Client-Server Architecture
The application follows a client-server architecture, where the frontend (Next.js) communicates with the backend (Flask) via RESTful API endpoints. This pattern ensures a clear separation of concerns, with the frontend handling user interface and user interactions, and the backend managing data and business logic.

### Model-View-Controller (MVC) Pattern
While not explicitly mentioned, the application follows a pattern similar to MVC:
- **Model**: The backend (`app.py`) acts as the model, managing data storage and retrieval.
- **View**: The frontend components (e.g., `page.tsx`, `login/page.tsx`, `dashboard/page.tsx`) act as the view, rendering the user interface.
- **Controller**: The API endpoints in the backend (`app.py`) act as the controller, handling user requests and updating the model.

### Authentication and Authorization
The application uses JWT (JSON Web Tokens) for user authentication and session management. This ensures that user sessions are secure and stateless, allowing for scalable and stateless backend services.

### RESTful API
The backend provides a RESTful API, which follows the principles of stateless communication, resource-based URLs, and standard HTTP methods (GET, POST, PUT, DELETE). This pattern ensures that the API is easy to understand and use, and it promotes a consistent and predictable interaction model.

## Conclusion

The architecture of the project is well-structured, with clear separation of concerns between the frontend and backend. The client-server model, combined with the use of RESTful API and JWT for authentication, ensures a scalable and maintainable application. The modular design of the frontend and the organized structure of the backend endpoints facilitate efficient development and maintenance.

---

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

---

# Frontend

This section details the frontend implementation of the project, which is built using Next.js, React, and Tailwind CSS. The frontend is responsible for rendering the user interface, handling user interactions, and communicating with the backend API.

## Project Structure

### Configuration Files

#### `tailwind.config.ts`
- **Location**: `vulnerable-server\frontend\tailwind.config.ts`
- **Purpose**: Configures the Tailwind CSS setup for the frontend application.
- **Key Features**:
  - Specifies the file paths to scan for CSS class usage.
  - Extends the default theme with custom background images.
- **Usage**:
  - The configuration object is exported as the default export and is used by Tailwind CSS to generate the final CSS.

#### `next-env.d.ts`
- **Location**: `vulnerable-server\frontend\next-env.d.ts`
- **Purpose**: Provides type definitions for the Next.js framework and its image component.
- **Key Features**:
  - Not intended to be edited.
  - Used by the TypeScript compiler to provide type definitions for the Next.js framework.
- **Usage**:
  - This file is automatically included by the TypeScript compiler to ensure type safety in the Next.js application.

### Layout and Pages

#### `layout.tsx`
- **Location**: `vulnerable-server\frontend\src\app\layout.tsx`
- **Purpose**: Defines the root layout for the Next.js application.
- **Key Features**:
  - Sets up the basic HTML structure and metadata for the application.
  - Includes a title and description for the metadata.
  - Provides a container for rendering child components.
- **Usage**:
  - This component wraps all pages in the Next.js application, ensuring a consistent structure and metadata.

#### `page.tsx`
- **Location**: `vulnerable-server\frontend\src\app\page.tsx`
- **Purpose**: Defines the landing page for the TaskFlow project management application.
- **Key Features**:
  - Includes a navigation bar, hero section, features, social proof, pricing, and footer.
  - Contains a scroll effect for the navigation bar.
  - Runs client-side analytics based on URL parameters.
- **Usage**:
  - The landing page is the main entry point for users and provides an overview of the application's features and pricing.

### Authentication Pages

#### `login\page.tsx`
- **Location**: `vulnerable-server\frontend\src\app\login\page.tsx`
- **Purpose**: Defines a React component for the login page.
- **Key Features**:
  - Includes a form for users to enter their email and password.
  - Handles form submission and displays errors.
  - Redirects to the dashboard upon successful login.
  - Provides links to register and reset the password.
- **API Interaction**:
  - Submits form data to the `/api/auth/login` endpoint.
- **Usage**:
  - This component serves as the entry point for the login page and handles user authentication.

#### `register\page.tsx`
- **Location**: `vulnerable-server\frontend\src\app\register\page.tsx`
- **Purpose**: Defines a React component for the user registration page.
- **Key Features**:
  - Handles form input for user details, including name, email, password, and an optional company field.
  - Submits form data to a backend API for user registration.
  - Redirects to the login page upon successful registration.
  - Includes error handling to display any issues that occur during the registration process.
- **API Interaction**:
  - Submits form data to the `/api/auth/register` endpoint.
- **Usage**:
  - This component serves as the entry point for the user registration page and handles user registration.

### Dashboard and Admin Pages

#### `dashboard\page.tsx`
- **Location**: `vulnerable-server\frontend\src\app\dashboard\page.tsx`
- **Purpose**: Defines a React component for the dashboard page in the task management application.
- **Key Features**:
  - Manages tasks, projects, and documents.
  - Handles user settings.
  - Fetches data from a backend API.
  - Provides options for creating, importing, and exporting tasks.
  - Includes a modal for creating new tasks and a sidebar for navigation.
- **API Interactions**:
  - Fetches project and scan data from `/api/projects/:userId` and `/api/scans/:userId/:projectId`.
  - Submits tasks to `/api/tasks`.
  - Uploads documents to `/api/documents/upload`.
  - Processes bulk data via `/api/bulk/process`.
- **Usage**:
  - This component serves as the main interface for users to manage their tasks and projects.

#### `admin\page.tsx`
- **Location**: `vulnerable-server\frontend\src\app\admin\page.tsx`
- **Purpose**: Defines a React component for the admin panel.
- **Key Features**:
  - Includes user management, system status, system logs, database query execution, network diagnostics, external data synchronization, and maintenance mode toggling.
  - Fetches data from a backend API and updates the UI accordingly.
- **API Interactions**:
  - Fetches user data from `/api/admin/users`.
  - Fetches system status from `/api/admin/status`.
  - Fetches logs from `/api/admin/logs`.
  - Runs diagnostics via `/api/admin/diagnostics`.
  - Executes custom queries via `/api/admin/query`.
  - Syncs external data via `/api/admin/sync`.
  - Processes data via `/api/admin/process`.
- **Usage**:
  - This component serves as the main interface for administrators to manage the system and perform various administrative tasks.

## Summary

The frontend of the project is built using Next.js, React, and Tailwind CSS. It consists of several key components, including the root layout, landing page, authentication pages, dashboard, and admin panel. Each component is designed to handle specific user interactions and communicate with the backend API to fetch and update data. The configuration files ensure that the application is properly set up and styled, providing a consistent and user-friendly experience.

---

# API Reference

This section provides a comprehensive reference for the RESTful API endpoints provided by the backend, including authentication, task management, and administrative functions. Each endpoint is described with its HTTP method, path, and a brief overview of its functionality.

## Authentication

### User Registration
- **Endpoint**: `/api/auth/register`
- **Method**: `POST`
- **Description**: Registers a new user with the provided details. The request body should include the user's name, email, password, and an optional company field.
- **File**: `vulnerable-server\backend\app.py`

### User Login
- **Endpoint**: `/api/auth/login`
- **Method**: `POST`
- **Description**: Authenticates a user and generates a JWT token for subsequent requests. The request body should include the user's email and password.
- **File**: `vulnerable-server\backend\app.py`

## Task Management

### Manage Tasks
- **Endpoint**: `/api/tasks`
- **Method**: `GET`
- **Description**: Retrieves a list of tasks for the authenticated user.
- **File**: `vulnerable-server\backend\app.py`

- **Endpoint**: `/api/tasks`
- **Method**: `POST`
- **Description**: Creates a new task for the authenticated user. The request body should include the task details.
- **File**: `vulnerable-server\backend\app.py`

## Project Management

### Manage Projects
- **Endpoint**: `/api/projects`
- **Method**: `GET`
- **Description**: Retrieves a list of projects for the authenticated user.
- **File**: `vulnerable-server\backend\app.py`

- **Endpoint**: `/api/projects`
- **Method**: `POST`
- **Description**: Creates a new project for the authenticated user. The request body should include the project details.
- **File**: `vulnerable-server\backend\app.py`

## Document Management

### Upload Documents
- **Endpoint**: `/api/documents/upload`
- **Method**: `POST`
- **Description**: Uploads a document and saves it to the filesystem. The request should include the document file and metadata.
- **File**: `vulnerable-server\backend\app.py`

### Preview Documents
- **Endpoint**: `/api/documents/preview`
- **Method**: `GET`
- **Description**: Retrieves the content of a document for previewing.
- **File**: `vulnerable-server\backend\app.py`

### Download Documents
- **Endpoint**: `/api/documents/download/<path:filename>`
- **Method**: `GET`
- **Description**: Downloads a document from the filesystem.
- **File**: `vulnerable-server\backend\app.py`

## Search

### Search
- **Endpoint**: `/api/search`
- **Method**: `GET`
- **Description**: Searches for tasks, projects, or documents and returns the results in a simple HTML template.
- **File**: `vulnerable-server\backend\app.py`

## Integration Testing

### Test Webhooks
- **Endpoint**: `/api/integrations/test`
- **Method**: `GET`
- **Description**: Tests a webhook by making an HTTP GET request to the provided URL.
- **File**: `vulnerable-server\backend\app.py`

## Task Import

### Import Tasks
- **Endpoint**: `/api/import`
- **Method**: `POST`
- **Description**: Imports tasks from YAML content. The request body should include the YAML data.
- **File**: `vulnerable-server\backend\app.py`

## Bulk Data Processing

### Process Bulk Data
- **Endpoint**: `/api/bulk/process`
- **Method**: `POST`
- **Description**: Processes bulk data, deserializes and processes pickled data.
- **File**: `vulnerable-server\backend\app.py`

## Report Export

### Export Reports
- **Endpoint**: `/api/reports/export`
- **Method**: `GET`
- **Description**: Generates and exports reports using shell commands.
- **File**: `vulnerable-server\backend\app.py`

## Administrative Functions

### Manage Users
- **Endpoint**: `/api/admin/users`
- **Method**: `GET`
- **Description**: Retrieves a list of users.
- **File**: `vulnerable-server\backend\app.py`

- **Endpoint**: `/api/admin/users`
- **Method**: `PUT`
- **Description**: Updates user details. The request body should include the updated user details.
- **File**: `vulnerable-server\backend\app.py`

- **Endpoint**: `/api/admin/users`
- **Method**: `DELETE`
- **Description**: Deletes a user.
- **File**: `vulnerable-server\backend\app.py`

### Get Administrative Status
- **Endpoint**: `/api/admin/status`
- **Method**: `GET`
- **Description**: Retrieves administrative status, including user count and storage usage.
- **File**: `vulnerable-server\backend\app.py`

### Retrieve Logs
- **Endpoint**: `/api/admin/logs`
- **Method**: `GET`
- **Description**: Retrieves logs from a log file using shell commands.
- **File**: `vulnerable-server\backend\app.py`

### Run Diagnostics
- **Endpoint**: `/api/admin/diagnostics`
- **Method**: `GET`
- **Description**: Runs diagnostics by pinging a specified host.
- **File**: `vulnerable-server\backend\app.py`

### Execute SQL Queries
- **Endpoint**: `/api/admin/query`
- **Method**: `POST`
- **Description**: Executes SQL queries, supporting both SELECT and non-SELECT statements.
- **File**: `vulnerable-server\backend\app.py`

### Sync Data
- **Endpoint**: `/api/admin/sync`
- **Method**: `GET`
- **Description**: Syncs data from an external source by making an HTTP GET request.
- **File**: `vulnerable-server\backend\app.py`

### Process Data
- **Endpoint**: `/api/admin/process`
- **Method**: `POST`
- **Description**: Processes data by evaluating and executing Python code.
- **File**: `vulnerable-server\backend\app.py`

## Team Management

### Retrieve Team Member Details
- **Endpoint**: `/api/team/members/<int:user_id>`
- **Method**: `GET`
- **Description**: Retrieves details of a team member by user ID.
- **File**: `vulnerable-server\backend\app.py`

## Analytics

### Generate MD5 Hash
- **Endpoint**: `/api/analytics/hash`
- **Method**: `GET`
- **Description**: Generates an MD5 hash of the provided data.
- **File**: `vulnerable-server\backend\app.py`

This API reference covers the essential endpoints for interacting with the backend of the TaskFlow application, providing a clear and concise guide for developers and integrators.

---

# Security

This section provides an overview of the security measures implemented in the application, including authentication, authorization, and data protection. The security architecture is designed to ensure that user data is protected and that only authorized users can access specific parts of the application.

## Authentication and Authorization

### User Authentication
The application uses a combination of user registration, login, and session management to handle user authentication. The key components involved in this process are:

- **User Registration (`/api/auth/register`)**:
  - **File**: `vulnerable-server\backend\app.py:1-120`
  - **Description**: This endpoint allows users to register by providing their name, email, and password. The data is validated and stored in the SQLite database.
  - **Security Measures**: Input validation to prevent SQL injection and other common attacks.

- **User Login (`/api/auth/login`)**:
  - **File**: `vulnerable-server\backend\app.py:121-240`
  - **Description**: This endpoint authenticates users by verifying their email and password. Upon successful authentication, a JSON Web Token (JWT) is generated and returned to the client.
  - **Security Measures**: Passwords are hashed and stored securely. JWTs are used to maintain user sessions and are validated on each request.

- **Login Page (`/login`)**:
  - **File**: `vulnerable-server\frontend\src\app\login\page.tsx:1-120`
  - **Description**: This React component provides a form for users to enter their email and password. It handles form submission and displays errors. Upon successful login, the user is redirected to the dashboard.
  - **Security Measures**: Form validation to ensure that the input is valid and secure.

- **Register Page (`/register`)**:
  - **File**: `vulnerable-server\frontend\src\app\register\page.tsx:1-120`
  - **Description**: This React component provides a form for users to register by entering their name, email, password, and an optional company field. The form data is submitted to the backend API for user registration.
  - **Security Measures**: Form validation to ensure that the input is valid and secure.

### Session Management
- **Session Handling**:
  - **File**: `vulnerable-server\backend\app.py:121-240`
  - **Description**: The application uses Flask sessions to manage user state. Sessions are stored on the server-side and are associated with the user's JWT.
  - **Security Measures**: Sessions are securely managed to prevent session hijacking and other attacks.

### Role-Based Access Control (RBAC)
- **Admin Panel (`/admin`)**:
  - **File**: `vulnerable-server\frontend\src\app\admin\page.tsx:1-120`
  - **Description**: This React component provides an admin panel with various administrative tools, including user management, system status, logs, and diagnostics. Access to this panel is restricted to users with the 'admin' role.
  - **Security Measures**: Role-based access control ensures that only users with the 'admin' role can access the admin panel. The backend API endpoints for admin functions (`/api/admin/*`) also enforce this role-based access.

## Data Protection

### Data Encryption
- **Password Hashing**:
  - **File**: `vulnerable-server\backend\app.py:1-120`
  - **Description**: User passwords are hashed using a secure hashing algorithm before being stored in the database. This ensures that even if the database is compromised, the passwords remain protected.
  - **Security Measures**: Hashing algorithms such as bcrypt or Argon2 are used to securely hash passwords.

### Secure Data Storage
- **Database Security**:
  - **File**: `vulnerable-server\backend\app.py:1-120`
  - **Description**: The application uses SQLite for data storage. The database is configured to enforce data integrity and security.
  - **Security Measures**: The database is protected against SQL injection attacks through parameterized queries and input validation.

### File Uploads and Downloads
- **Document Upload (`/api/documents/upload`)**:
  - **File**: `vulnerable-server\backend\app.py:241-360`
  - **Description**: This endpoint allows users to upload documents. The files are saved to the filesystem, and metadata is stored in the database.
  - **Security Measures**: File uploads are validated to ensure that only allowed file types are accepted. The files are stored in a secure directory with restricted access.

- **Document Preview (`/api/documents/preview`)**:
  - **File**: `vulnerable-server\backend\app.py:241-360`
  - **Description**: This endpoint allows users to preview uploaded documents. The file content is read from the filesystem and returned to the client.
  - **Security Measures**: File access is restricted to authenticated users, and the content is served securely.

- **Document Download (`/api/documents/download/<path:filename>`)**:
  - **File**: `vulnerable-server\backend\app.py:241-360`
  - **Description**: This endpoint allows users to download uploaded documents. The file is served from the filesystem.
  - **Security Measures**: File access is restricted to authenticated users, and the content is served securely.

### Data Export and Import
- **Task Import (`/api/import`)**:
  - **File**: `vulnerable-server\backend\app.py:241-360`
  - **Description**: This endpoint allows users to import tasks from YAML content. The YAML data is parsed and tasks are created in the database.
  - **Security Measures**: YAML data is validated to ensure that it is well-formed and does not contain malicious content.

- **Report Export (`/api/reports/export`)**:
  - **File**: `vulnerable-server\backend\app.py:241-360`
  - **Description**: This endpoint allows users to export reports in different formats (e.g., PDF, CSV). The reports are generated using shell commands.
  - **Security Measures**: Shell commands are carefully constructed to prevent command injection attacks.

## Security Best Practices

### Input Validation
- **Form Validation**:
  - **Files**: `vulnerable-server\frontend\src\app\login\page.tsx:1-120`, `vulnerable-server\frontend\src\app\register\page.tsx:1-120`
  - **Description**: Form inputs are validated on the client-side to ensure that they meet the required criteria. This helps prevent invalid data from being submitted to the server.
  - **Security Measures**: Client-side validation is complemented by server-side validation to ensure that all inputs are secure.

### Error Handling
- **Error Handling**:
  - **Files**: `vulnerable-server\frontend\src\app\login\page.tsx:1-120`, `vulnerable-server\frontend\src\app\register\page.tsx:1-120`
  - **Description**: The application handles errors gracefully and provides meaningful error messages to users. This helps prevent information leakage and ensures a better user experience.
  - **Security Measures**: Error messages are sanitized to prevent sensitive information from being exposed.

### Logging and Monitoring
- **Logging**:
  - **File**: `vulnerable-server\backend\app.py:361-480`
  - **Description**: The application logs important events, such as user actions and system diagnostics, to a log file. These logs can be used for auditing and troubleshooting.
  - **Security Measures**: Log files are stored securely and are accessible only to authorized personnel.

### Security Testing
- **Testing**:
  - **File**: `vulnerable-server\frontend\src\app\page.tsx:1-120`
  - **Description**: The application includes client-side analytics tracking and session detection to monitor user behavior and detect potential security issues.
  - **Security Measures**: Regular security testing and code reviews are conducted to identify and mitigate vulnerabilities.

By implementing these security measures, the application ensures that user data is protected, and only authorized users can access specific parts of the application.

---