# API Reference

This section provides a comprehensive reference for the API endpoints, including request and response formats, authentication requirements, and error handling. Each endpoint is described in detail, mapping back to the relevant files and functions in the codebase.

## Authentication

### Authentication Middleware
- **File**: `taskflow\backend\src\middleware\authenticate.js`
- **Function**: `authenticate`
- **Description**: Authenticates HTTP requests by verifying a JWT token in the authorization header. Attaches user information to the request object if the token is valid. Returns a 401 Unauthorized response if the token is missing, invalid, or expired.
- **Tags**: `auth`, `security`, `logging`

### Authorization Middleware
- **File**: `taskflow\backend\src\middleware\authorize.js`
- **Function**: `authorize`
- **Description**: Checks if the user has the required roles to access a resource. Returns a 401 Unauthorized status if the user is not authenticated, and a 403 Forbidden status if the user does not have sufficient permissions.
- **Tags**: `auth`, `security`

### Rate Limiter Middleware
- **File**: `taskflow\backend\src\middleware\rateLimiter.js`
- **Function**: `reportLimiter`
- **Description**: Limits the rate of report generation requests to 10 per minute to prevent abuse of the PDF export feature.
- **Tags**: `network`, `security`

## User Management

### User Registration
- **File**: `taskflow\backend\src\controllers\authController.js`
- **Endpoint**: `POST /api/register`
- **Function**: `register`
- **Description**: Handles user registration, including validation, password hashing, and creation of user and organization records.
- **Tags**: `auth`, `db`, `network`, `logging`

### User Login
- **File**: `taskflow\backend\src\controllers\authController.js`
- **Endpoint**: `POST /api/login`
- **Function**: `login`
- **Description**: Handles user login, including credential validation and token generation.
- **Tags**: `auth`, `db`, `network`, `logging`

### Token Refresh
- **File**: `taskflow\backend\src\controllers\authController.js`
- **Endpoint**: `POST /api/refresh`
- **Function**: `refresh`
- **Description**: Handles token refresh, generating a new access token from a valid refresh token.
- **Tags**: `auth`, `db`, `network`, `logging`

### Password Reset Request
- **File**: `taskflow\backend\src\controllers\authController.js`
- **Endpoint**: `POST /api/forgot-password`
- **Function**: `forgotPassword`
- **Description**: Handles password reset requests, sending a reset link to the user's email if the email exists.
- **Tags**: `auth`, `db`, `network`, `logging`

### Password Reset
- **File**: `taskflow\backend\src\controllers\authController.js`
- **Endpoint**: `POST /api/reset-password`
- **Function**: `resetPassword`
- **Description**: Handles password reset, updating the user's password with a new hashed password.
- **Tags**: `auth`, `db`, `network`, `logging`

### User Logout
- **File**: `taskflow\backend\src\controllers\authController.js`
- **Endpoint**: `POST /api/logout`
- **Function**: `logout`
- **Description**: Handles user logout, invalidating the user's refresh token.
- **Tags**: `auth`, `db`, `network`, `logging`

### Get User Profile
- **File**: `taskflow\backend\src\controllers\userController.js`
- **Endpoint**: `GET /api/users/profile`
- **Function**: `getProfile`
- **Description**: Retrieves the user's profile information.
- **Tags**: `auth`, `db`, `network`, `security`

### Update User Profile
- **File**: `taskflow\backend\src\controllers\userController.js`
- **Endpoint**: `PUT /api/users/profile`
- **Function**: `updateProfile`
- **Description**: Updates the user's profile information.
- **Tags**: `auth`, `db`, `network`, `security`

## Project Management

### List Projects
- **File**: `taskflow\backend\src\controllers\projectController.js`
- **Endpoint**: `GET /api/projects`
- **Function**: `list`
- **Description**: Lists projects for a given organization, optionally including archived projects.
- **Tags**: `auth`, `db`, `network`, `security`

### Get Project by ID
- **File**: `taskflow\backend\src\controllers\projectController.js`
- **Endpoint**: `GET /api/projects/:projectId`
- **Function**: `getOne`
- **Description**: Retrieves a single project by ID, checking for existence and organization ownership.
- **Tags**: `auth`, `db`, `network`, `security`

### Create Project
- **File**: `taskflow\backend\src\controllers\projectController.js`
- **Endpoint**: `POST /api/projects`
- **Function**: `create`
- **Description**: Creates a new project, validating the project name and associating it with the organization.
- **Tags**: `auth`, `db`, `network`, `security`

### Update Project
- **File**: `taskflow\backend\src\controllers\projectController.js`
- **Endpoint**: `PUT /api/projects/:projectId`
- **Function**: `update`
- **Description**: Updates an existing project, ensuring the project belongs to the organization.
- **Tags**: `auth`, `db`, `network`, `security`

### Delete Project
- **File**: `taskflow\backend\src\controllers\projectController.js`
- **Endpoint**: `DELETE /api/projects/:projectId`
- **Function**: `remove`
- **Description**: Deletes a project, verifying its existence and organization ownership.
- **Tags**: `auth`, `db`, `network`, `security`

## Task Management

### List Tasks
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `GET /api/tasks`
- **Function**: `list`
- **Description**: Lists tasks for a specific project or across an organization.
- **Tags**: `auth`, `db`, `network`, `logging`

### Get Task by ID
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `GET /api/tasks/:taskId`
- **Function**: `getOne`
- **Description**: Retrieves a single task by its ID.
- **Tags**: `auth`, `db`, `network`, `logging`

### Create Task
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `POST /api/tasks`
- **Function**: `create`
- **Description**: Creates a new task within a project.
- **Tags**: `auth`, `db`, `network`, `logging`

### Update Task
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `PUT /api/tasks/:taskId`
- **Function**: `update`
- **Description**: Updates an existing task.
- **Tags**: `auth`, `db`, `network`, `logging`

### Delete Task
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `DELETE /api/tasks/:taskId`
- **Function**: `remove`
- **Description**: Deletes a task by its ID.
- **Tags**: `auth`, `db`, `network`, `logging`

### Add Comment to Task
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `POST /api/tasks/:taskId/comments`
- **Function**: `addComment`
- **Description**: Adds a comment to a specific task.
- **Tags**: `auth`, `db`, `network`, `logging`

### Get Comments for Task
- **File**: `taskflow\backend\src\controllers\taskController.js`
- **Endpoint**: `GET /api/tasks/:taskId/comments`
- **Function**: `getComments`
- **Description**: Retrieves comments for a specific task.
- **Tags**: `auth`, `db`, `network`, `logging`

## Report Generation

### Generate PDF Report
- **File**: `taskflow\backend\src\controllers\reportController.js`
- **Endpoint**: `GET /api/reports/:projectId/pdf`
- **Function**: `generatePdf`
- **Description**: Generates a PDF report for a project's tasks. It requires a project ID as a parameter and checks for project existence and user access before generating the report.
- **Tags**: `auth`, `db`, `network`, `file_io`, `security`

## Attachment Management

### List Attachments for Task
- **File**: `taskflow\backend\src\controllers\attachmentController.js`
- **Endpoint**: `GET /api/tasks/:taskId/attachments`
- **Function**: `list`
- **Description**: Lists attachments for a specific task.
- **Tags**: `auth`, `db`, `network`, `file_io`

### Upload Attachment
- **File**: `taskflow\backend\src\controllers\attachmentController.js`
- **Endpoint**: `POST /api/tasks/:taskId/attachments`
- **Function**: `upload`
- **Description**: Uploads a file as an attachment to a specific task.
- **Tags**: `auth`, `db`, `network`, `file_io`

### Download Attachment
- **File**: `taskflow\backend\src\controllers\attachmentController.js`
- **Endpoint**: `GET /api/tasks/attachments/:attachmentId`
- **Function**: `download`
- **Description**: Downloads an attachment by its ID.
- **Tags**: `auth`, `db`, `network`, `file_io`

### Remove Attachment
- **File**: `taskflow\backend\src\controllers\attachmentController.js`
- **Endpoint**: `DELETE /api/tasks/attachments/:attachmentId`
- **Function**: `remove`
- **Description**: Removes an attachment by its ID.
- **Tags**: `auth`, `db`, `network`, `file_io`

## Notification Management

### List Notifications
- **File**: `taskflow\backend\src\controllers\notificationController.js`
- **Endpoint**: `GET /api/notifications`
- **Function**: `list`
- **Description**: Lists notifications for a user, with a limit parameter.
- **Tags**: `auth`, `db`, `network`, `security`

### Mark Notification as Read
- **File**: `taskflow\backend\src\controllers\notificationController.js`
- **Endpoint**: `PUT /api/notifications/:id/read`
- **Function**: `markRead`
- **Description**: Marks a specific notification as read for a user.
- **Tags**: `auth`, `db`, `network`, `security`

### Get Notification Preferences
- **File**: `taskflow\backend\src\controllers\notificationController.js`
- **Endpoint**: `GET /api/notifications/preferences`
- **Function**: `getPreferences`
- **Description**: Retrieves notification preferences for a user.
- **Tags**: `auth`, `db`, `network`, `security`

### Update Notification Preferences
- **File**: `taskflow\backend\src\controllers\notificationController.js`
- **Endpoint**: `POST /api/notifications/preferences`
- **Function**: `updatePreferences`
- **Description**: Updates notification preferences for a user.
- **Tags**: `auth`, `db`, `network`, `security`

## Admin Management

### Get All Users
- **File**: `taskflow\backend\src\controllers\adminController.js`
- **Endpoint**: `GET /api/admin/users`
- **Function**: `getAllUsers`
- **Description**: Retrieves all users from the database.
- **Tags**: `auth`, `db`, `network`, `security`

### Delete User
- **File**: `taskflow\backend\src\controllers\adminController.js`
- **Endpoint**: `DELETE /api/admin/users/:id`
- **Function**: `deleteUser`
- **Description**: Deletes a user by their ID.
- **Tags**: `auth`, `db`, `network`, `security`

### Get Billing Overview
- **File**: `taskflow\backend\src\controllers\adminController.js`
- **Endpoint**: `GET /api/admin/billing`
- **Function**: `getBillingOverview`
- **Description**: Retrieves a billing overview, including user details and project counts.
- **Tags**: `auth`, `db`, `network`, `security`

## Import Management

### Import Tasks from XML
- **File**: `taskflow\backend\src\controllers\importController.js`
- **Endpoint**: `POST /api/import/xml/:projectId`
- **Function**: `importXml`
- **Description**: Imports tasks from XML data. Validates the project, parses the XML, and creates tasks in the database.
- **Tags**: `auth`, `db`, `network`, `file_io`

### Import Tasks from CSV
- **File**: `taskflow\backend\src\controllers\importController.js`
- **Endpoint**: `POST /api/import/csv/:projectId`
- **Function**: `importCsv`
- **Description**: Imports tasks from CSV data. Validates the project, parses the CSV, and creates tasks in the database.
- **Tags**: `auth`, `db`, `network`, `file_io`

## Health Check

### Health Check Endpoint
- **File**: `taskflow\backend\src\app.js`
- **Endpoint**: `GET /api/v1/health`
- **Function**: `GET /api/v1/health`
- **Description**: Endpoint to check the health of the application, returning a JSON object with a success status and timestamp.
- **Tags**: `network`, `auth`, `db`, `file_io`, `security`

## Error Handling

### Error Handler Middleware
- **File**: `taskflow\backend\src\middleware\errorHandler.js`
- **Function**: `errorHandler`
- **Description**: Middleware function that handles errors by logging them and sending a JSON response.
- **Tags**: `logging`, `network`, `security`

## File Upload

### File Upload Middleware
- **File**: `taskflow\backend\src\middleware\upload.js`
- **Function**: `upload`
- **Description**: Configures and exports a multer middleware for handling file uploads. Sets the upload directory and defines how files are stored, including the destination and filename formatting.
- **Tags**: `file_io`

## Database Models

### Task Model
- **File**: `taskflow\backend\src\models\taskModel.js`
- **Functions**: `findById`, `findByProject`, `create`, `update`, `remove`
- **Description**: Provides methods to find, create, update, and remove tasks in the database.
- **Tags**: `db`

### User Model
- **File**: `taskflow\backend\src\models\userModel.js`
- **Functions**: `findById`, `findByEmail`, `create`, `updateRefreshToken`, `setResetToken`, `clearResetToken`, `updatePassword`
- **Description**: Provides methods to find, create, and update user records, including handling of refresh tokens, reset tokens, and password updates.
- **Tags**: `db`

### Organization Model
- **File**: `taskflow\backend\src\models\orgModel.js`
- **Functions**: `findById`, `create`, `addMember`, `getMembers`
- **Description**: Provides methods to find an organization by ID, create a new organization, add a member to an organization, and retrieve the members of an organization.
- **Tags**: `db`

### Project Model
- **File**: `taskflow\backend\src\models\projectModel.js`
- **Functions**: `findById`, `findByOrg`, `create`, `update`, `remove`
- **Description**: Provides methods to find, create, update, and delete project records, as well as to find projects by organization ID.
- **Tags**: `db`

## Utility Functions

### Token Utilities
- **File**: `taskflow\backend\src\utils\tokenUtils.js`
- **Functions**: `signToken`, `verifyToken`
- **Description**: Provides functions to sign and verify JWT access and refresh tokens.
- **Tags**: `auth`, `crypto`, `security`

### Validators
- **File**: `taskflow\backend\src\utils\validators.js`
- **Functions**: `isEmail`, `isNonEmptyString`, `sanitizeString`
- **Description**: Provides utility functions for validating and sanitizing strings, specifically for email format, non-empty strings, and string sanitization with a maximum length.
- **Tags**: `other`

### Formatters
- **File**: `taskflow\frontend\src\utils\formatters.js`
- **Functions**: `formatDate`, `formatRelative`, `priorityLabel`, `statusLabel`
- **Description**: Provides utility functions for formatting dates, relative times, priority labels, and status labels.
- **Tags**: `other`

### Analytics
- **File**: `taskflow\frontend\src\utils\analytics.js`
- **Functions**: `trackEvent`, `identify`
- **Description**: Provides utility functions for tracking user events and identifying users in Mixpanel and Google Analytics.
- **Tags**: `network`, `logging`

### Authentication Utilities
- **File**: `taskflow\frontend\src\utils\authUtils.js`
- **Functions**: `saveSession`, `clearSession`, `getToken`, `getRefreshToken`, `getStoredUser`
- **Description**: Provides utility functions for managing authentication sessions in a frontend application, including saving and clearing session data, and retrieving the authentication token and user information.
- **Tags**: `auth`, `storage`

## Frontend API Client

### Axios Client
- **File**: `taskflow\frontend\src\api\client.js`
- **Function**: `client`
- **Description**: Sets up an Axios client for making HTTP requests to a backend API. Includes interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to the login page.
- **Tags**: `auth`, `network`, `logging`, `security`

## Frontend Routes

### Admin Routes
- **File**: `taskflow\frontend\src\api\admin.js`
- **Functions**: `getAllUsers`, `deleteUser`, `getBillingOverview`
- **Description**: Provides functions to fetch all users, delete a user, and get a billing overview from the admin API endpoint.
- **Tags**: `network`, `auth`

### Project Routes
- **File**: `taskflow\frontend\src\api\projects.js`
- **Functions**: `list`, `getOne`, `create`, `update`, `remove`
- **Description**: Provides functions to list, retrieve, create, update, and delete projects from the API.
- **Tags**: `network`

### Task Routes
- **File**: `taskflow\frontend\src\api\tasks.js`
- **Functions**: `list`, `getOne`, `create`, `update`, `remove`
- **Description**: Provides functions to list, retrieve, create, update, and delete tasks from the API.
- **Tags**: `network`, `api`

### Authentication Routes
- **File**: `taskflow\frontend\src\api\auth.js`
- **Functions**: `login`, `register`, `logout`, `refreshToken`
- **Description**: Provides functions to handle login, registration, logout,