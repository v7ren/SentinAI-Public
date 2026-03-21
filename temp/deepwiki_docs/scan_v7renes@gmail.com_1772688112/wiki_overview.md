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