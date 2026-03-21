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