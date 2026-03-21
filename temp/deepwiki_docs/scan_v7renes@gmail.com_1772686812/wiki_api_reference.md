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