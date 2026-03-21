# Overview

## What the Project Is and What Problem It Solves

The **Vulnerable Server SAST Test** project is a deliberately insecure web application designed to serve as a testing ground for Static Application Security Testing (SAST) tools. The project is built using a combination of React for the frontend and FastAPI for the backend. It includes a variety of security vulnerabilities across different components and endpoints, making it an ideal environment for security researchers, developers, and auditors to identify and understand common security flaws.

The primary purpose of this project is to:

- **Educate**: Provide a hands-on learning experience for developers and security professionals to understand and identify common security vulnerabilities.
- **Test**: Serve as a benchmark for SAST tools to evaluate their effectiveness in detecting security issues.
- **Research**: Offer a controlled environment for security researchers to explore and analyze various types of vulnerabilities.

## Main Components or Modules

### Frontend

The frontend of the application is built using React and is configured to run with Vite, a build tool that provides a fast development server. The main components of the frontend include:

- **Vite Configuration (`vite.config.js`)**: Configures the Vite development server to run on port 3002 and includes the React plugin.
- **Main Entry Point (`main.jsx`)**: Sets up the React DOM and renders the `App` component into the DOM element with the ID `root`.
- **App Component (`App.jsx`)**: Manages the routing and navigation of the application using `react-router-dom`. It defines routes for the Home, Login, Register, Dashboard, Admin, and Export pages.
- **Page Components**:
  - **Home (`Home.jsx`)**: A simple web page with intentional security vulnerabilities, including DOM XSS, prototype pollution, and unsafe use of `postMessage` and `eval`.
  - **Login (`Login.jsx`)**: Handles user authentication by sending a POST request to the backend and storing the token in local storage.
  - **Register (`Register.jsx`)**: Manages user registration by sending a POST request to the backend and redirecting the user to the dashboard upon successful registration.
  - **Dashboard (`Dashboard.jsx`)**: Displays user information and orders, checks for authentication, and provides a logout functionality.
  - **Admin (`Admin.jsx`)**: Provides a user interface for performing various administrative tasks, such as pinging a host, fetching a URL, retrieving logs, generating reports, and importing configuration. Each task is associated with potential security vulnerabilities.
  - **Export (`Export.jsx`)**: Allows users to export order data as a CSV file and perform open redirects based on user input.

### Backend

The backend of the application is built using FastAPI, a modern web framework for building APIs with Python. The main components of the backend include:

- **Main Application (`main.py`)**: Initializes the FastAPI application, sets up database tables, and defines JWT authentication functions. It includes a variety of API endpoints, each with deliberate security vulnerabilities such as SQL injection, command injection, insecure deserialization, and more.
  - **User Management**:
    - **Register (`/api/auth/register`)**: Endpoint for user registration with vulnerabilities like mass assignment, SQL injection, and use of MD5 for password hashing.
    - **Login (`/api/auth/login`)**: Endpoint for user login with SQL injection vulnerability in the authentication process.
    - **User Details (`/api/users/{user_id}`)**: Endpoint to retrieve user details with vulnerabilities like IDOR (Insecure Direct Object References) and SQL injection.
  - **Order Management**:
    - **List/Create Orders (`/api/orders`)**: Endpoint to list or create orders with SQL injection vulnerabilities in both SELECT and INSERT queries.
    - **Search Orders (`/api/search`)**: Endpoint to search orders with SQL injection vulnerability in the search query.
  - **Report Generation**:
    - **Generate Report (`/api/report/generate`)**: Endpoint to generate reports using Jinja2 templates with a vulnerability to Server-Side Template Injection (SSTI).
  - **Configuration Management**:
    - **Import Configuration (`/api/config/import`)**: Endpoint to import configuration data with an insecure deserialization vulnerability using pickle.
    - **Load YAML Configuration (`/api/config/yaml`)**: Endpoint to load YAML configuration data with an insecure deserialization vulnerability using unsafe YAML loading.
  - **File Operations**:
    - **Read File (`/api/file/read`)**: Endpoint to read a file with a path traversal vulnerability.
    - **Upload File (`/api/file/upload`)**: Endpoint to upload a file with no type or size checks, leading to an unrestricted upload vulnerability.
    - **Export ZIP File (`/api/export/zip`)**: Endpoint to handle ZIP file uploads with a zip slip vulnerability.
    - **Export CSV File (`/api/export/csv`)**: Endpoint to export orders as a CSV file with SQL injection and CSV formula injection vulnerabilities.
  - **Other Operations**:
    - **Ping Host (`/api/ping`)**: Endpoint to ping a host with a command injection vulnerability.
    - **Fetch URL (`/api/fetch`)**: Endpoint to fetch a URL with a Server-Side Request Forgery (SSRF) vulnerability.
    - **Redirect (`/api/redirect`)**: Endpoint to perform a redirect with an open redirect vulnerability.
    - **Process XML Payment Data (`/api/payment/xml`)**: Endpoint to process XML payment data with an XML External Entity (XXE) vulnerability.
    - **Decode JWT Tokens (`/api/token/decode`)**: Endpoint to decode JWT tokens with a vulnerability to algorithm confusion.
    - **Return Environment Variables (`/api/debug/env`)**: Endpoint to return environment variables and secrets, leading to information disclosure.
    - **Validate Regular Expressions (`/api/validate/regex`)**: Endpoint to validate regular expressions with a ReDoS (Regular Expression Denial of Service) vulnerability.
    - **Perform LDAP Searches (`/api/ldap/search`)**: Endpoint to perform LDAP searches with an LDAP injection vulnerability.
    - **Perform Audit (`/api/audit`)**: Endpoint to perform an audit with a host header injection vulnerability.

## Typical Usage or Runtime Scenario

A typical usage scenario for the **Vulnerable Server SAST Test** project involves the following steps:

1. **Development Setup**:
   - Start the Vite development server by running the command specified in `vite.config.js`. This will serve the React application on port 3002.
   - Start the FastAPI backend server by running the command specified in `main.py`. This will initialize the API endpoints and database connections.

2. **User Interaction**:
   - **Home Page**: Users can navigate to the Home page, which intentionally includes security vulnerabilities such as DOM XSS and prototype pollution.
   - **Registration**: Users can register by filling out the form on the Register page. The form data is sent to the `/api/auth/register` endpoint, which processes the registration and stores the user's token in local storage.
   - **Login**: Registered users can log in by providing their credentials on the Login page. The form data is sent to the `/api/auth/login` endpoint, which authenticates the user and stores the token in local storage.
   - **Dashboard**: Authenticated users are redirected to the Dashboard page, where they can view their user information and orders. The Dashboard component checks for authentication and provides a logout functionality.
   - **Admin Tasks**: Users with administrative privileges can access the Admin page, which provides a UI for performing various administrative tasks. Each task is associated with potential security vulnerabilities, such as command injection and server-side request forgery (SSRF).
   - **Data Export**: Users can export their order data as a CSV file by interacting with the Export page. The page sends a GET request to the `/api/export/csv` endpoint to fetch the data.

3. **Security Testing**:
   - **SAST Tool Integration**: Security researchers and developers can integrate SAST tools to scan the project's codebase and identify the deliberately introduced vulnerabilities.
   - **Manual Testing**: Users can manually test the application by attempting to exploit the known vulnerabilities and verifying the security issues.

## Where to Look Next

For deeper details and more specific information, refer to the following sections:

- **Frontend**:
  - **Configuration**: `vite.config.js` for Vite development server setup.
  - **Main Entry Point**: `main.jsx` for the React application entry point.
  - **Routing and Navigation**: `App.jsx` for the main application routing.
  - **Page Components**: `Home.jsx`, `Login.jsx`, `Register.jsx`, `Dashboard.jsx`, `Admin.jsx`, and `Export.jsx` for detailed component implementations.

- **Backend**:
  - **API Endpoints**: `main.py` for the FastAPI application and its various endpoints.
  - **Security Vulnerabilities**: Detailed descriptions of the security vulnerabilities in each endpoint, including SQL injection, command injection, and insecure deserialization.

- **Security Testing**:
  - **SAST Tool Integration**: Guidelines for integrating SAST tools to scan the project.
  - **Manual Testing**: Steps for manually testing the application and verifying the security issues.

By exploring these sections, you can gain a comprehensive understanding of the project's architecture, components, and security vulnerabilities.

---

# Architecture and Data Flow

This section provides an overview of the main architectural components, data flow, and control flow within the project. The architecture is primarily composed of a frontend React application and a backend FastAPI server, with a focus on intentional security vulnerabilities for testing purposes.

## Main Architectural Components

### Frontend
- **Vite Development Server (`vite.config.js`)**: Configures the Vite development server to run on port 3002 and includes the React plugin.
- **React Application (`main.jsx`)**: The entry point for the React application, setting up the React DOM and rendering the `App` component.
- **App Component (`App.jsx`)**: Manages routing using `react-router-dom` and defines the main navigation and routes for the application.
- **Page Components**:
  - **Home (`Home.jsx`)**: Displays a simple web page with intentional security vulnerabilities.
  - **Login (`Login.jsx`)**: Handles user authentication and form submission.
  - **Register (`Register.jsx`)**: Handles user registration and form submission.
  - **Dashboard (`Dashboard.jsx`)**: Displays user information and orders, with authentication checks.
  - **Admin (`Admin.jsx`)**: Provides a UI for administrative tasks with various security vulnerabilities.
  - **Export (`Export.jsx`)**: Allows users to export order data as a CSV file and perform open redirects.

### Backend
- **FastAPI Application (`main.py`)**: Contains the main FastAPI application with various endpoints for user management, order handling, file operations, and other functionalities. Each endpoint is intentionally designed with security vulnerabilities for testing purposes.

## Data and Control Flow

### Frontend to Backend Communication
1. **User Interaction**:
   - Users interact with the frontend React application, navigating through different pages and performing actions.
   - The `App` component manages the routing and navigation using `react-router-dom`.

2. **Form Submissions**:
   - **Login (`Login.jsx`)**: When a user submits the login form, a POST request is sent to the `/api/auth/login` endpoint.
   - **Register (`Register.jsx`)**: When a user submits the registration form, a POST request is sent to the `/api/auth/register` endpoint.
   - **Dashboard (`Dashboard.jsx`)**: The component checks for authentication and loads user orders by making a GET request to the `/api/orders` endpoint.
   - **Admin (`Admin.jsx`)**: The component performs various administrative tasks by making API calls to endpoints such as `/api/ping`, `/api/fetch`, `/api/logs`, `/api/report/generate`, and `/api/config/import`.
   - **Export (`Export.jsx`)**: The component allows users to export order data as a CSV file by making a GET request to the `/api/export/csv` endpoint.

3. **Data Handling**:
   - **Home (`Home.jsx`)**: The component interacts with the URL hash and query parameters, and listens for `postMessage` events, which can lead to DOM XSS and prototype pollution vulnerabilities.
   - **Admin (`Admin.jsx`)**: The component performs various operations that can lead to command injection, server-side request forgery (SSRF), server-side template injection (SSTI), and deserialization of untrusted data.

### Backend Processing
1. **API Endpoints**:
   - **User Management**:
     - **Register (`/api/auth/register`)**: Handles user registration with vulnerabilities like mass assignment, SQL injection, and use of MD5 for password hashing.
     - **Login (`/api/auth/login`)**: Handles user login with SQL injection vulnerabilities.
     - **User Details (`/api/users/{user_id}`)**: Retrieves user details with vulnerabilities like IDOR (Insecure Direct Object References) and SQL injection.
   - **Order Management**:
     - **List/Create Orders (`/api/orders`)**: Lists or creates orders with SQL injection vulnerabilities.
     - **Search Orders (`/api/search`)**: Searches orders with SQL injection vulnerabilities.
   - **Report Generation**:
     - **Generate Report (`/api/report/generate`)**: Generates reports using Jinja2 templates with SSTI vulnerabilities.
   - **Configuration Management**:
     - **Import Configuration (`/api/config/import`)**: Imports configuration data with insecure deserialization vulnerabilities.
     - **Load YAML Configuration (`/api/config/yaml`)**: Loads YAML configuration data with insecure deserialization vulnerabilities.
   - **File Operations**:
     - **Read File (`/api/file/read`)**: Reads files with path traversal vulnerabilities.
     - **Upload File (`/api/file/upload`)**: Uploads files with no type or size checks, leading to unrestricted upload vulnerabilities.
     - **Export ZIP File (`/api/export/zip`)**: Handles ZIP file uploads with zip slip vulnerabilities.
     - **Export CSV File (`/api/export/csv`)**: Exports orders as a CSV file with SQL injection and CSV formula injection vulnerabilities.
   - **Other Operations**:
     - **Ping Host (`/api/ping`)**: Pings a host with command injection vulnerabilities.
     - **Fetch URL (`/api/fetch`)**: Fetches a URL with SSRF vulnerabilities.
     - **Redirect (`/api/redirect`)**: Performs a redirect with open redirect vulnerabilities.
     - **Process XML Payment (`/api/payment/xml`)**: Processes XML payment data with XXE vulnerabilities.
     - **Decode JWT Token (`/api/token/decode`)**: Decodes JWT tokens with algorithm confusion vulnerabilities.
     - **Return Environment Variables (`/api/debug/env`)**: Returns environment variables and secrets, leading to information disclosure.
     - **Validate Regular Expressions (`/api/validate/regex`)**: Validates regular expressions with ReDoS vulnerabilities.
     - **Perform LDAP Search (`/api/ldap/search`)**: Performs LDAP searches with LDAP injection vulnerabilities.
     - **Perform Audit (`/api/audit`)**: Performs an audit with host header injection vulnerabilities.

### Important Patterns
- **Client/Server Architecture**: The application follows a client/server architecture, where the frontend React application communicates with the backend FastAPI server via HTTP requests.
- **Model-View-Controller (MVC)**: The frontend React application loosely follows the MVC pattern, with the `App` component acting as the controller, managing the view and model (state and routing).
- **Event-Driven**: The frontend application is event-driven, with user interactions triggering form submissions and API calls.
- **Layered Architecture**: The backend FastAPI application is layered, with API endpoints handling requests, business logic, and data access.

## Conclusion
The architecture of the project is designed to provide a clear separation of concerns between the frontend and backend, with a focus on intentional security vulnerabilities for testing purposes. The frontend React application manages user interactions and communicates with the backend FastAPI server via HTTP requests, while the backend handles various operations and data processing, each with deliberate security flaws.

---

# Frontend

This section covers the React-based frontend of the application, including the main components, routing, and user interface elements. The frontend is designed to interact with the backend API and provide a user-friendly interface for various functionalities.

## Development Environment

### Vite Configuration
- **File**: `vite.config.js`
- **Summary**: Configures the Vite development server for the React application.
- **Key Points**:
  - The server runs on port 3002.
  - The React plugin is included to support React-specific features.
- **Entry Point**:
  - **Vite Development Server**: Configured to run on port 3002, serving the React application.

## Application Entry Point

### Main Application Setup
- **File**: `src/main.jsx`
- **Summary**: Sets up the React DOM and renders the `App` component.
- **Key Points**:
  - Uses `ReactDOM.createRoot` to create a root for the React application.
  - Wraps the `App` component in a `StrictMode` container to help identify potential issues.
  - Renders the `App` component into the DOM element with the ID `root`.
- **Entry Point**:
  - **ReactDOM.createRoot**: Main entry point of the React application, where the `App` component is rendered into the DOM.

## Routing and Navigation

### Application Routing
- **File**: `src/App.jsx`
- **Summary**: Sets up routing using `react-router-dom` and defines the main navigation and routes.
- **Key Points**:
  - Defines routes for Home, Login, Register, Dashboard, Admin, and Export pages.
  - Includes a navigation bar with links to different pages.
- **Entry Point**:
  - **App**: Main entry point for the React application, which renders the navigation and routes.

## User Interface Components

### Home Page
- **File**: `src/pages/Home.jsx`
- **Summary**: Defines a React component for the Home page, which includes intentional security vulnerabilities for testing purposes.
- **Key Points**:
  - Displays a banner and a widget.
  - Contains vulnerabilities related to DOM XSS, prototype pollution, and unsafe use of `postMessage` and `eval`.
- **Entry Point**:
  - **Home**: React functional component that interacts with the URL hash and query parameters, and listens for `postMessage` events.

### Login Page
- **File**: `src/pages/Login.jsx`
- **Summary**: Defines a React component for the login page, handling user authentication.
- **Key Points**:
  - Handles form input for username and password.
  - Sends a POST request to the `/api/auth/login` endpoint to authenticate the user.
  - Stores the token and user data in `localStorage` upon successful login.
  - Supports a debug mode that can be enabled via URL parameters.
- **Entry Point**:
  - **Login**: React component that serves as the entry point for the login page, handling form submission and user authentication.

### Register Page
- **File**: `src/pages/Register.jsx`
- **Summary**: Defines a React component for user registration.
- **Key Points**:
  - Handles form input for username, password, and email.
  - Sends a POST request to the `/api/auth/register` endpoint to register the user.
  - Stores the received token in `localStorage` and redirects the user to the dashboard upon successful registration.
- **Entry Point**:
  - **Register**: React component that serves as the entry point for user registration.

### Dashboard Page
- **File**: `src/pages/Dashboard.jsx`
- **Summary**: Defines a React component for the user dashboard.
- **Key Points**:
  - Checks for authentication.
  - Loads user orders and provides a logout functionality.
- **Entry Point**:
  - **Dashboard**: React component that serves as an entry point for authenticated users, displaying user information and orders.

### Admin Page
- **File**: `src/pages/Admin.jsx`
- **Summary**: Defines a React component for performing administrative tasks.
- **Key Points**:
  - Provides a UI for pinging a host, fetching a URL, retrieving logs, generating a report, and importing configuration.
  - Each task is associated with potential security vulnerabilities, including command injection, server-side request forgery (SSRF), server-side template injection (SSTI), and deserialization of untrusted data.
- **Entry Point**:
  - **Admin**: React component that provides a UI for interacting with the backend API.

### Export Page
- **File**: `src/pages/Export.jsx`
- **Summary**: Defines a React component for exporting order data as a CSV file and performing an open redirect based on user input.
- **Key Points**:
  - Allows users to input order IDs and export them as a CSV file by making a GET request to the `/api/export/csv` endpoint.
  - Includes a feature for open redirection based on user input.
- **Entry Point**:
  - **Export**: React component that serves as an entry point for exporting CSV data and performing redirects.

## Security Considerations

### Security Vulnerabilities
- **Home Page**:
  - **DOM XSS**: Vulnerable to DOM-based cross-site scripting via `location.hash`.
  - **Prototype Pollution**: Vulnerable to prototype pollution via URL parameters.
  - **Unsafe `postMessage` and `eval`**: Uses `postMessage` and `eval` in an unsafe manner.
- **Login Page**:
  - **Authentication**: Handles user authentication and token storage.
  - **Debug Mode**: Supports a debug mode that can be enabled via URL parameters.
- **Register Page**:
  - **User Registration**: Sends user data to the backend for registration.
  - **Token Storage**: Stores the received token in `localStorage`.
- **Dashboard Page**:
  - **Authentication**: Checks for user authentication.
  - **Order Loading**: Loads user orders from the backend.
- **Admin Page**:
  - **Administrative Tasks**: Performs various administrative tasks with potential security vulnerabilities.
- **Export Page**:
  - **CSV Export**: Exports order data as a CSV file.
  - **Open Redirect**: Performs an open redirect based on user input.

## Interactions with the Backend

### API Endpoints
- **Login**:
  - **Endpoint**: `/api/auth/login` (POST)
  - **Functionality**: Authenticates the user and returns a token.
- **Register**:
  - **Endpoint**: `/api/auth/register` (POST)
  - **Functionality**: Registers a new user and returns a token.
- **Dashboard**:
  - **Endpoint**: `/api/orders` (GET)
  - **Functionality**: Retrieves user orders.
- **Admin**:
  - **Endpoints**:
    - `/api/ping` (GET): Pings a host.
    - `/api/fetch` (GET): Fetches a URL.
    - `/api/logs` (GET): Retrieves logs.
    - `/api/report/generate` (POST): Generates a report.
    - `/api/config/import` (POST): Imports configuration data.
- **Export**:
  - **Endpoint**: `/api/export/csv` (GET)
  - **Functionality**: Exports order data as a CSV file.

## Conclusion

The frontend of the application is built using React and Vite, with routing managed by `react-router-dom`. It provides a user-friendly interface for various functionalities, including user authentication, registration, dashboard access, administrative tasks, and data export. The application includes intentional security vulnerabilities for testing purposes, which should be addressed in a production environment.

---

# Backend

This section details the FastAPI backend, including the API endpoints, database interactions, and security considerations. The backend is designed to intentionally introduce various security vulnerabilities for testing purposes, making it a valuable resource for security assessments and training.

## FastAPI Application Initialization

The FastAPI application is initialized in `vulnerable-server-sast-test\backend\main.py`. This file sets up the application with a vulnerable configuration, defines database tables, and sets up JWT authentication functions. It also includes the creation of an admin user and the setup of database connections.

### Key Components
- **Database Setup**: Initializes database tables and connections.
- **JWT Authentication**: Defines functions for token creation and validation.
- **Admin User Creation**: Creates an admin user during application startup.

## API Endpoints

The backend provides a variety of API endpoints, each with deliberate security vulnerabilities. Below is a list of the endpoints, their purposes, and the associated security concerns.

### User Management
- **Endpoint**: `/api/auth/register` (POST)
  - **Purpose**: User registration.
  - **Security Concerns**: Mass assignment, SQL injection, use of MD5 for password hashing.
- **Endpoint**: `/api/auth/login` (POST)
  - **Purpose**: User login.
  - **Security Concerns**: SQL injection in the authentication process.
- **Endpoint**: `/api/users/{user_id}` (GET)
  - **Purpose**: Retrieve user details.
  - **Security Concerns**: IDOR (Insecure Direct Object References), SQL injection.

### Order Management
- **Endpoint**: `/api/orders` (GET, POST)
  - **Purpose**: List or create orders.
  - **Security Concerns**: SQL injection in both SELECT and INSERT queries.
- **Endpoint**: `/api/search` (GET)
  - **Purpose**: Search orders.
  - **Security Concerns**: SQL injection in the search query.

### Report Generation
- **Endpoint**: `/api/report/generate` (POST)
  - **Purpose**: Generate reports using Jinja2 templates.
  - **Security Concerns**: Server-Side Template Injection (SSTI).

### Configuration Management
- **Endpoint**: `/api/config/import` (POST)
  - **Purpose**: Import configuration data.
  - **Security Concerns**: Insecure deserialization using pickle.
- **Endpoint**: `/api/config/yaml` (POST)
  - **Purpose**: Load YAML configuration data.
  - **Security Concerns**: Insecure deserialization using unsafe YAML loading.

### Log Management
- **Endpoint**: `/api/logs` (GET)
  - **Purpose**: Read log files.
  - **Security Concerns**: Command injection.

### Network Operations
- **Endpoint**: `/api/ping` (GET)
  - **Purpose**: Ping a host.
  - **Security Concerns**: Command injection.
- **Endpoint**: `/api/fetch` (GET)
  - **Purpose**: Fetch a URL.
  - **Security Concerns**: Server-Side Request Forgery (SSRF).

### File Operations
- **Endpoint**: `/api/redirect` (GET)
  - **Purpose**: Perform a redirect.
  - **Security Concerns**: Open redirect vulnerability.
- **Endpoint**: `/api/file/read` (GET)
  - **Purpose**: Read a file.
  - **Security Concerns**: Path traversal vulnerability.
- **Endpoint**: `/api/file/upload` (POST)
  - **Purpose**: Upload a file.
  - **Security Concerns**: No type or size checks, leading to an unrestricted upload vulnerability.
- **Endpoint**: `/api/export/zip` (POST)
  - **Purpose**: Handle ZIP file uploads.
  - **Security Concerns**: Zip slip vulnerability.
- **Endpoint**: `/api/export/csv` (GET)
  - **Purpose**: Export orders as a CSV file.
  - **Security Concerns**: SQL injection and CSV formula injection vulnerabilities.

### Payment Processing
- **Endpoint**: `/api/payment/xml` (POST)
  - **Purpose**: Process XML payment data.
  - **Security Concerns**: XML External Entity (XXE) vulnerability.

### Token Management
- **Endpoint**: `/api/token/decode` (POST)
  - **Purpose**: Decode JWT tokens.
  - **Security Concerns**: Vulnerability to algorithm confusion.

### Debugging and Testing
- **Endpoint**: `/api/debug/env` (GET)
  - **Purpose**: Return environment variables and secrets.
  - **Security Concerns**: Information disclosure.
- **Endpoint**: `/api/validate/regex` (GET)
  - **Purpose**: Validate regular expressions.
  - **Security Concerns**: ReDoS (Regular Expression Denial of Service) vulnerability.
- **Endpoint**: `/api/ldap/search` (GET)
  - **Purpose**: Perform LDAP searches.
  - **Security Concerns**: LDAP injection vulnerability.
- **Endpoint**: `/api/audit` (GET)
  - **Purpose**: Perform an audit.
  - **Security Concerns**: Host header injection vulnerability.

## Security Considerations

The backend is intentionally designed with security vulnerabilities to serve as a testing ground for security assessments. However, it is crucial to understand and mitigate these vulnerabilities in a production environment. Key security concerns include:

- **SQL Injection**: Ensure proper input validation and parameterized queries.
- **Command Injection**: Avoid using user input directly in shell commands.
- **Insecure Deserialization**: Use safe deserialization methods and validate data.
- **Server-Side Request Forgery (SSRF)**: Restrict the URLs that can be fetched.
- **Path Traversal**: Validate file paths to prevent unauthorized access.
- **Open Redirect**: Validate redirect URLs to prevent malicious redirects.
- **XML External Entity (XXE)**: Use secure XML parsers and disable external entity resolution.
- **ReDoS**: Use regular expressions that are not prone to exponential backtracking.
- **LDAP Injection**: Validate and sanitize user input for LDAP queries.
- **Host Header Injection**: Validate and sanitize host headers.

By understanding and addressing these vulnerabilities, developers can build more secure applications.

---

# Security

This section highlights the security vulnerabilities and considerations in both the frontend and backend of the project. It covers common issues and how they are addressed, providing a clear understanding of the security landscape.

## Frontend Security

### Vite Configuration
- **File**: `vulnerable-server-sast-test\frontend\vite.config.js`
- **Summary**: Configures the Vite development server for a React application, setting the server to run on port 3002 and including the React plugin.
- **Security Concerns**: None noted.
- **Entry Points**:
  - **Vite Development Server**: Configured to run on port 3002, serving the React application.

### Main Application Entry Point
- **File**: `vulnerable-server-sast-test\frontend\src\main.jsx`
- **Summary**: Sets up the React DOM, applies a StrictMode wrapper for the application, and renders the `App` component into the DOM element with the ID `root`.
- **Security Concerns**: None noted.
- **Entry Points**:
  - **ReactDOM.createRoot**: Main entry point of the React application, where the `App` component is rendered into the DOM.

### Application Routing
- **File**: `vulnerable-server-sast-test\frontend\src\App.jsx`
- **Summary**: Sets up a React application with routing using `react-router-dom`. It defines the main navigation and routes for the application, including Home, Login, Register, Dashboard, Admin, and Export pages.
- **Security Concerns**:
  - **Authentication**: Potential issues related to login, session management, JWT, OAuth, and permissions.
  - **External HTTP Calls**: Potential vulnerabilities in API calls and webhooks.
- **Entry Points**:
  - **App**: Main entry point of the React application, which renders the navigation and routes.

### Dashboard Component
- **File**: `vulnerable-server-sast-test\frontend\src\pages\Dashboard.jsx`
- **Summary**: Displays user information and orders, checks for authentication, loads user orders, and provides a logout functionality.
- **Security Concerns**:
  - **Authentication**: Potential issues related to login, session management, JWT, OAuth, and permissions.
  - **Database Querying**: Potential SQL injection vulnerabilities.
  - **External HTTP Calls**: Potential vulnerabilities in API calls.
  - **Filesystem Operations**: Potential issues with file I/O.
  - **Message Queues**: Potential issues with Redis, Kafka, WebSockets.
- **Entry Points**:
  - **Dashboard**: Entry point for authenticated users, rendering the user dashboard.

### Home Component
- **File**: `vulnerable-server-sast-test\frontend\src\pages\Home.jsx`
- **Summary**: Displays a simple web page with intentional security vulnerabilities for testing purposes. It includes vulnerabilities related to DOM XSS, prototype pollution, and unsafe use of `postMessage` and `eval`.
- **Security Concerns**:
  - **DOM XSS**: Vulnerability via `location.hash`.
  - **Prototype Pollution**: Vulnerability via URL parameters.
  - **Unsafe Use of `postMessage` and `eval`**: Potential for code injection.
- **Entry Points**:
  - **Home**: React functional component that interacts with the URL hash and query parameters, and listens for `postMessage` events.

### Export Component
- **File**: `vulnerable-server-sast-test\frontend\src\pages\Export.jsx`
- **Summary**: Provides a user interface for exporting order data as a CSV file and performing an open redirect based on user input.
- **Security Concerns**:
  - **Authentication**: Potential issues related to login, session management, JWT, OAuth, and permissions.
  - **External HTTP Calls**: Potential vulnerabilities in API calls.
  - **Filesystem Operations**: Potential issues with file I/O.
  - **Message Queues**: Potential issues with Redis, Kafka, WebSockets.
- **Entry Points**:
  - **Export Component**: Entry point for users to export CSV data and perform redirects.
  - **API Endpoint**: `/api/export/csv` (GET)

### Register Component
- **File**: `vulnerable-server-sast-test\frontend\src\pages\Register.jsx`
- **Summary**: Handles user registration by sending a POST request to the server with form data. Upon successful registration, it stores the received token in local storage and redirects the user to the dashboard.
- **Security Concerns**:
  - **Authentication**: Potential issues related to login, session management, JWT, OAuth, and permissions.
  - **External HTTP Calls**: Potential vulnerabilities in API calls.
- **Entry Points**:
  - **Register**: Entry point for user registration.
  - **API Endpoint**: `/api/auth/register` (POST)

### Login Component
- **File**: `vulnerable-server-sast-test\frontend\src\pages\Login.jsx`
- **Summary**: Handles user authentication by sending a POST request to an API endpoint with the user's credentials. If the login is successful, it stores the token and user data in localStorage and navigates to the next page. It also has a debug mode that can display the login process and any errors.
- **Security Concerns**:
  - **Authentication**: Potential issues related to login, session management, JWT, OAuth, and permissions.
  - **External HTTP Calls**: Potential vulnerabilities in API calls.
  - **Filesystem Operations**: Potential issues with file I/O.
- **Entry Points**:
  - **Login**: Entry point for the login page.
  - **API Endpoint**: `/api/auth/login` (POST)

### Admin Component
- **File**: `vulnerable-server-sast-test\frontend\src\pages\Admin.jsx`
- **Summary**: Provides a user interface for performing various administrative tasks, such as pinging a host, fetching a URL, retrieving logs, generating a report, and importing configuration. Each task is associated with a potential security vulnerability, including command injection, server-side request forgery (SSRF), server-side template injection (SSTI), and deserialization of untrusted data.
- **Security Concerns**:
  - **External HTTP Calls**: Potential vulnerabilities in API calls.
  - **Filesystem Operations**: Potential issues with file I/O.
- **Entry Points**:
  - **Admin Component**: Entry point for administrative tasks.
  - **API Endpoints**:
    - `/api/ping` (GET)
    - `/api/fetch` (GET)
    - `/api/logs` (GET)
    - `/api/report/generate` (POST)
    - `/api/config/import` (POST)

## Backend Security

### FastAPI Application
- **File**: `vulnerable-server-sast-test\backend\main.py`
- **Summary**: Contains a FastAPI application designed to intentionally introduce various security vulnerabilities for testing purposes. It includes endpoints for user management, order handling, file operations, and other functionalities, each with deliberate security flaws.
- **Security Concerns**:
  - **Authentication**: Potential issues related to login, session management, JWT, OAuth, and permissions.
  - **Database Querying**: Potential SQL injection vulnerabilities.
  - **External HTTP Calls**: Potential vulnerabilities in API calls.
  - **Filesystem Operations**: Potential issues with file I/O.
  - **Message Queues**: Potential issues with Redis, Kafka, WebSockets.
- **Entry Points**:
  - **User Management**:
    - `/api/auth/register` (POST): Vulnerabilities like mass assignment, SQL injection, and use of MD5 for password hashing.
    - `/api/auth/login` (POST): SQL injection vulnerability in the authentication process.
    - `/api/users/{user_id}` (GET): Vulnerabilities like IDOR (Insecure Direct Object References) and SQL injection.
  - **Order Handling**:
    - `/api/orders` (GET, POST): SQL injection vulnerabilities in both SELECT and INSERT queries.
    - `/api/search` (GET): SQL injection vulnerability in the search query.
  - **Report Generation**:
    - `/api/report/generate` (POST): Vulnerability to Server-Side Template Injection (SSTI).
  - **Configuration Import**:
    - `/api/config/import` (POST): Insecure deserialization vulnerability using pickle.
    - `/api/config/yaml` (POST): Insecure deserialization vulnerability using unsafe YAML loading.
  - **Log and Host Operations**:
    - `/api/logs` (GET): Command injection vulnerability.
    - `/api/ping` (GET): Command injection vulnerability.
  - **URL Fetching**:
    - `/api/fetch` (GET): Server-Side Request Forgery (SSRF) vulnerability.
  - **Redirects**:
    - `/api/redirect` (GET): Open redirect vulnerability.
  - **File Operations**:
    - `/api/file/read` (GET): Path traversal vulnerability.
    - `/api/file/upload` (POST): Unrestricted upload vulnerability.
    - `/api/export/zip` (POST): Zip slip vulnerability.
    - `/api/export/csv` (GET): SQL injection and CSV formula injection vulnerabilities.
  - **Payment Processing**:
    - `/api/payment/xml` (POST): XML External Entity (XXE) vulnerability.
  - **Token Management**:
    - `/api/token/decode` (POST): Vulnerability to algorithm confusion.
  - **Environment and Validation**:
    - `/api/debug/env` (GET): Information disclosure vulnerability.
    - `/api/validate/regex` (GET): ReDoS (Regular Expression Denial of Service) vulnerability.
  - **LDAP and Audit**:
    - `/api/ldap/search` (GET): LDAP injection vulnerability.
    - `/api/audit` (GET): Host header injection vulnerability.

### Summary of Security Considerations
- **Authentication and Authorization**: Ensure proper handling of user sessions, JWT tokens, and permissions to prevent unauthorized access.
- **Input Validation**: Validate all user inputs to prevent SQL injection, command injection, and other injection attacks.
- **File Operations**: Implement strict file path validation and size/type checks to prevent path traversal and unrestricted file uploads.
- **API Security**: Use secure HTTP methods, validate API requests, and handle errors gracefully to prevent SSRF, XXE, and other API vulnerabilities.
- **Configuration Management**: Securely manage configuration files and avoid using unsafe deserialization methods.
- **Logging and Monitoring**: Implement robust logging and monitoring to detect and respond to security incidents.

By addressing these concerns, the application can be made more secure and resilient against common security threats.

---