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