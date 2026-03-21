# API Reference

This section provides detailed documentation for the API endpoints, including request and response formats, authentication requirements, and example usage.

## Authentication

### Authentication Middleware
- **File:** `taskflow\backend\src\middleware\authenticate.js`
- **Description:** Middleware function that checks the authorization header and verifies the JWT token.
- **Endpoints:**
  - **`authenticate`**
    - **Details:** Checks the authorization header and verifies the JWT token. Attaches user information to the request object if the token is valid, or returns a 401 Unauthorized response if the token is missing, invalid, or expired.

### Authorization Middleware
- **File:** `taskflow\backend\src\middleware\authorize.js`
- **Description:** Middleware function that checks if the user is authenticated and if their role is among the allowed roles for the requested resource.
- **Endpoints:**
  - **`authorize`**
    - **Details:** Returns a 401 status if the user is not authenticated, and a 403 status if the user does not have sufficient permissions.

### Rate Limiter Middleware
- **File:** `taskflow\backend\src\middleware\rateLimiter.js`
- **Description:** Middleware function that limits the rate of report generation requests to prevent abuse of the PDF export feature.
- **Endpoints:**
  - **`reportLimiter`**
    - **Details:** Limits the rate of report generation requests to 10 per minute.

## User Management

### User Controller
- **File:** `taskflow\backend\src\controllers\userController.js`
- **Description:** Handles HTTP requests to retrieve and update user profiles.
- **Endpoints:**
  - **`GET /api/users/profile`**
    - **Details:** Retrieves a user's profile information.
  - **`PUT /api/users/profile`**
    - **Details:** Updates a user's profile information.

### User Routes
- **File:** `taskflow\backend\src\routes\userRoutes.js`
- **Description:** Sets up routes for user-related endpoints, requiring authentication for all routes.
- **Endpoints:**
  - **`GET /profile`**
    - **Details:** Retrieves the user's profile information.
  - **`PATCH /profile`**
    - **Details:** Updates the user's profile information.

### Authentication Controller
- **File:** `taskflow\backend\src\controllers\authController.js`
- **Description:** Handles user registration, login, token refresh, password reset, and logout functionalities.
- **Endpoints:**
  - **`POST /api/register`**
    - **Details:** Handles user registration, including validation, password hashing, and creation of user and organization records.
  - **`POST /api/login`**
    - **Details:** Handles user login, including credential validation and token generation.
  - **`POST /api/refresh`**
    - **Details:** Handles token refresh, generating a new access token from a valid refresh token.
  - **`POST /api/forgot-password`**
    - **Details:** Handles password reset requests, sending a reset link to the user's email.
  - **`POST /api/reset-password`**
    - **Details:** Handles password reset, updating the user's password with a new one.
  - **`POST /logout`**
    - **Details:** Handles user logout, invalidating the refresh token.

### Authentication Routes
- **File:** `taskflow\backend\src\routes\authRoutes.js`
- **Description:** Sets up routes for authentication-related HTTP endpoints.
- **Endpoints:**
  - **`POST /register`**
    - **Details:** Handles user registration requests.
  - **`POST /login`**
    - **Details:** Handles user login requests.
  - **`POST /refresh`**
    - **Details:** Handles token refresh requests.
  - **`POST /forgot-password`**
    - **Details:** Handles forgot password requests.
  - **`POST /reset-password`**
    - **Details:** Handles password reset requests.
  - **`POST /logout`**
    - **Details:** Handles user logout requests, protected by authentication middleware.

## Project Management

### Project Controller
- **File:** `taskflow\backend\src\controllers\projectController.js`
- **Description:** Manages projects within an organization, providing endpoints for listing, retrieving, creating, updating, and deleting projects.
- **Endpoints:**
  - **`GET /projects`**
    - **Details:** Lists projects for a given organization, optionally including archived projects.
  - **`GET /projects/:projectId`**
    - **Details:** Retrieves a single project by ID, with checks for existence and organization ownership.
  - **`POST /projects`**
    - **Details:** Creates a new project for an organization, requiring a valid project name.
  - **`PUT /projects/:projectId`**
    - **Details:** Updates an existing project, with checks for existence and organization ownership.
  - **`DELETE /projects/:projectId`**
    - **Details:** Deletes a project, with checks for existence.

### Project Routes
- **File:** `taskflow\backend\src\routes\projectRoutes.js`
- **Description:** Sets up routes for project-related HTTP endpoints, requiring authentication.
- **Endpoints:**
  - **`GET /`**
    - **Details:** Lists all projects.
  - **`GET /:projectId`**
    - **Details:** Retrieves a single project by ID.
  - **`POST /`**
    - **Details:** Creates a new project.
  - **`PUT /:projectId`**
    - **Details:** Updates an existing project by ID.
  - **`DELETE /:projectId`**
    - **Details:** Deletes a project by ID.

## Task Management

### Task Controller
- **File:** `taskflow\backend\src\controllers\taskController.js`
- **Description:** Manages tasks within a project, providing endpoints for listing, retrieving, creating, updating, and deleting tasks, as well as managing task comments.
- **Endpoints:**
  - **`GET /tasks`**
    - **Details:** Lists tasks for a specific project or across an organization.
  - **`GET /tasks/:taskId/comments`**
    - **Details:** Retrieves comments for a specific task.
  - **`POST /tasks/:taskId/comments`**
    - **Details:** Adds a comment to a specific task.
  - **`GET /tasks/:taskId`**
    - **Details:** Retrieves a single task by its ID.
  - **`POST /tasks`**
    - **Details:** Creates a new task within a project.
  - **`PUT /tasks/:taskId`**
    - **Details:** Updates an existing task.
  - **`DELETE /tasks/:taskId`**
    - **Details:** Deletes a task.

### Task Routes
- **File:** `taskflow\backend\src\routes\taskRoutes.js`
- **Description:** Sets up routes for task-related endpoints, requiring authentication.
- **Endpoints:**
  - **`GET /`**
    - **Details:** Lists all tasks.
  - **`GET /:taskId/comments`**
    - **Details:** Retrieves comments for a specific task.
  - **`POST /:taskId/comments`**
    - **Details:** Adds a comment to a specific task.
  - **`GET /:taskId`**
    - **Details:** Retrieves a single task by ID.
  - **`POST /`**
    - **Details:** Creates a new task.
  - **`PUT /:taskId`**
    - **Details:** Updates a task by ID.
  - **`DELETE /:taskId`**
    - **Details:** Deletes a task by ID.

## Attachment Management

### Attachment Controller
- **File:** `taskflow\backend\src\controllers\attachmentController.js`
- **Description:** Manages task attachments, including listing, uploading, downloading, and removing attachments.
- **Endpoints:**
  - **`GET /api/tasks/:taskId/attachments`**
    - **Details:** Lists all attachments for a given task ID.
  - **`POST /api/tasks/:taskId/attachments`**
    - **Details:** Uploads a file as an attachment to a task, storing it in the filesystem and database.
  - **`GET /api/tasks/:taskId/attachments/:attachmentId`**
    - **Details:** Downloads an attachment by its ID, serving the file from the filesystem.
  - **`DELETE /api/tasks/:taskId/attachments/:attachmentId`**
    - **Details:** Deletes an attachment by its ID, removing it from the database and filesystem.

### Attachment Routes
- **File:** `taskflow\backend\src\routes\attachmentRoutes.js`
- **Description:** Sets up routes for attachment-related operations, requiring authentication.
- **Endpoints:**
  - **`GET /task/:taskId`**
    - **Details:** Lists attachments for a specific task.
  - **`POST /task/:taskId`**
    - **Details:** Uploads a new attachment for a specific task.
  - **`GET /:attachmentId`**
    - **Details:** Downloads an attachment by its ID.
  - **`DELETE /:attachmentId`**
    - **Details:** Deletes an attachment by its ID.

## Report Generation

### Report Controller
- **File:** `taskflow\backend\src\controllers\reportController.js`
- **Description:** Handles the generation of PDF reports for projects.
- **Endpoints:**
  - **`GET /api/reports/:projectId/pdf`**
    - **Details:** Endpoint for generating a PDF report of a project's tasks. It requires a project ID and checks if the project exists and if the user has access to the project.

### Report Routes
- **File:** `taskflow\backend\src\routes\reportRoutes.js`
- **Description:** Sets up routes for report-related endpoints, applying authentication and rate limiting middleware.
- **Endpoints:**
  - **`GET /project/:projectId/pdf`**
    - **Details:** Generates a PDF for a specific project ID. Requires authentication and is rate-limited.

## Import Data

### Import Controller
- **File:** `taskflow\backend\src\controllers\importController.js`
- **Description:** Handles the import of tasks from XML and CSV formats into a project.
- **Endpoints:**
  - **`POST /api/projects/:projectId/import/xml`**
    - **Details:** Endpoint for importing tasks from XML data. It checks the project existence and ownership, parses the XML, and creates tasks in the database.
  - **`POST /api/projects/:projectId/import/csv`**
    - **Details:** Endpoint for importing tasks from CSV data. It checks the project existence and ownership, parses the CSV, and creates tasks in the database.

### Import Routes
- **File:** `taskflow\backend\src\routes\importRoutes.js`
- **Description:** Sets up routes for importing data into a project, with authentication middleware applied to all routes.
- **Endpoints:**
  - **`POST /project/:projectId/xml`**
    - **Details:** Endpoint to import XML data into a project, requires authentication.
  - **`POST /project/:projectId/csv`**
    - **Details:** Endpoint to import CSV data into a project, requires authentication.

## Notification Management

### Notification Controller
- **File:** `taskflow\backend\src\controllers\notificationController.js`
- **Description:** Handles notifications, including listing notifications, marking them as read, and managing user preferences for notifications.
- **Endpoints:**
  - **`GET /notifications`**
    - **Details:** Lists notifications for a user, with a limit parameter.
  - **`PUT /notifications/:id/read`**
    - **Details:** Marks a specific notification as read for a user.
  - **`GET /notifications/preferences`**
    - **Details:** Retrieves notification preferences for a user.
  - **`POST /notifications/preferences`**
    - **Details:** Updates notification preferences for a user.

### Notification Routes
- **File:** `taskflow\backend\src\routes\notificationRoutes.js`
- **Description:** Sets up routes for notification-related HTTP requests, requiring authentication.
- **Endpoints:**
  - **`GET /`**
    - **Details:** Lists all notifications for the authenticated user.
  - **`POST /:id/read`**
    - **Details:** Marks a specific notification as read for the authenticated user.
  - **`GET /preferences`**
    - **Details:** Retrieves the notification preferences for the authenticated user.
  - **`PATCH /preferences`**
    - **Details:** Updates the notification preferences for the authenticated user.

## Admin Management

### Admin Controller
- **File:** `taskflow\backend\src\controllers\adminController.js`
- **Description:** Contains controller functions for administrative tasks, such as retrieving all users, deleting a user, and getting a billing overview.
- **Endpoints:**
  - **`GET /admin/users`**
    - **Details:** Endpoint to retrieve all users from the database.
  - **`DELETE /admin/users/:id`**
    - **Details:** Endpoint to delete a user by their ID.
  - **`GET /admin/billing`**
    - **Details:** Endpoint to get a billing overview, including user details and project counts.

### Admin Routes
- **File:** `taskflow\backend\src\routes\adminRoutes.js`
- **Description:** Sets up routes for admin-specific routes, including endpoints to manage users and view billing information.
- **Endpoints:**
  - **`GET /users`**
    - **Details:** Retrieves all users, requires authentication.
  - **`DELETE /users/:id`**
    - **Details:** Deletes a user by ID, requires authentication.
  - **`GET /billing`**
    - **Details:** Retrieves billing overview, requires authentication.

## Health Check

### Health Check Endpoint
- **File:** `taskflow\backend\src\app.js`
- **Description:** Sets up an Express.js application and includes a health check endpoint.
- **Endpoints:**
  - **`GET /api/v1/health`**
    - **Details:** A health check endpoint that returns a JSON response with a status and timestamp.

## Error Handling

### Error Handler Middleware
- **File:** `taskflow\backend\src\middleware\errorHandler.js`
- **Description:** Middleware function for handling errors in an Express.js application.
- **Endpoints:**
  - **`errorHandler`**
    - **Details:** Logs the error details and sends a JSON response with the error message, stack trace, and status code.

## File Upload

### File Upload Middleware
- **File:** `taskflow\backend\src\middleware\upload.js`
- **Description:** Configures and exports a multer middleware for handling file uploads.
- **Endpoints:**
  - **`upload`**
    - **Details:** The multer middleware instance configured for file uploads, which can be used in an Express application to handle multipart/form-data requests.

## Example Usage

### Example Request and Response

#### User Registration
- **Endpoint:** `POST /api/register`
- **Request:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword",
    "fullName": "John Doe"
  }
  ```
- **Response:**
  ```json
  {
    "message": "User registered successfully",
    "user": {
      "id": "12345",
      "email": "user@example.com",
      "fullName": "John Doe"
    }
  }
  ```

#### User Login
- **Endpoint:** `POST /api/login`
- **Request:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Login successful",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NSIsImV4cCI6MTYxNjM1NzY4MH0.GzWzXxKzXzXzXzXzXzXzXzXzXzXzXzXz"
  }
  ```

#### Create a Project
- **Endpoint:** `POST /projects`
- **Request:**
  ```json
  {
    "name": "New Project",
    "organizationId": "67890"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Project created successfully",
    "project": {
      "id": "123456",
      "name": "New Project",
      "organizationId": "67890"
    }
  }
  ```

#### Generate a PDF Report
- **Endpoint:** `GET /api/reports/:projectId/pdf`
- **Request:**
  - **Headers:**
    ```json
    {
      "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NSIsImV4cCI6MTYxNjM1NzY4MH0.GzWzXxKzXzXzXzXzXzXzXzXzXzXzXzXz"
    }
  ```
- **Response:**
  - **Content-Type:** `application/pdf`
  - **Body:** PDF file content

This API reference provides a comprehensive overview of the available endpoints, their request and response formats, and the authentication requirements. For more detailed information, refer to the specific controller and route files mentioned in each section.