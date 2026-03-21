# Data Layer

The Data Layer in the TaskFlow application is responsible for managing the database schema, models, and data management practices. This section provides an overview of the key components and their interactions.

## Database Configuration

### File: `taskflow/backend/config/db.js`

- **Purpose**: Sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries.
- **Key Entities**:
  - **`pool`**: A PostgreSQL connection pool instance that can be used to execute queries.
  - **`query`**: A function that takes SQL text and parameters, and executes the query using the connection pool.
- **Configuration**:
  - Uses environment variables for configuration, with fallbacks for local development.
  - Configures the pool with environment variables or fallbacks for local development.
  - Sets up an error handler for the pool.

## Models

### Task Model

### File: `taskflow/backend/src/models/taskModel.js`

- **Purpose**: Provides functions for database operations on the `tasks` table.
- **Key Functions**:
  - **`findTaskById`**: Finds a task by its ID.
  - **`findTasksByProjectId`**: Finds tasks by project ID.
  - **`createTask`**: Creates a new task.
  - **`updateTask`**: Updates an existing task.
  - **`removeTask`**: Deletes a task.

### Project Model

### File: `taskflow/backend/src/models/projectModel.js`

- **Purpose**: Provides functions for database operations on the `projects` table.
- **Key Functions**:
  - **`findById`**: Finds a project by its ID.
  - **`findByOrg`**: Finds projects by organization ID.
  - **`create`**: Creates a new project.
  - **`update`**: Updates an existing project.
  - **`remove`**: Deletes a project.

### Organization Model

### File: `taskflow/backend/src/models/orgModel.js`

- **Purpose**: Provides functions for database operations on the `orgs` and `org_members` tables.
- **Key Functions**:
  - **`findById`**: Finds an organization by its ID.
  - **`create`**: Creates a new organization.
  - **`addMember`**: Adds a member to an organization.
  - **`getMembers`**: Retrieves the members of an organization.

### User Model

### File: `taskflow/backend/src/models/userModel.js`

- **Purpose**: Provides functions for database operations on the `users` table.
- **Key Functions**:
  - **`findUserById`**: Finds a user by its ID.
  - **`findUserByEmail`**: Finds a user by email.
  - **`createUser`**: Creates a new user.
  - **`updateRefreshToken`**: Updates the refresh token for a user.
  - **`setResetToken`**: Sets a password reset token for a user.
  - **`clearResetToken`**: Clears the password reset token for a user.
  - **`updatePassword`**: Updates the password for a user.

## Controllers

### Task Controller

### File: `taskflow/backend/src/controllers/taskController.js`

- **Purpose**: Manages HTTP requests related to tasks.
- **Key Endpoints**:
  - **`list`**: Lists tasks for a specific project or across an organization.
  - **`getOne`**: Retrieves a single task by its ID.
  - **`create`**: Creates a new task within a project.
  - **`update`**: Updates an existing task.
  - **`remove`**: Deletes a task.
  - **`getComments`**: Retrieves comments for a specific task.
  - **`addComment`**: Adds a comment to a specific task.

### Project Controller

### File: `taskflow/backend/src/controllers/projectController.js`

- **Purpose**: Manages HTTP requests related to projects.
- **Key Endpoints**:
  - **`list`**: Lists projects for a given organization, optionally including archived projects.
  - **`getOne`**: Retrieves a single project by ID, with checks for existence and organization ownership.
  - **`create`**: Creates a new project for an organization.
  - **`update`**: Updates an existing project, with checks for existence and organization ownership.
  - **`remove`**: Deletes a project, with checks for existence.

### User Controller

### File: `taskflow/backend/src/controllers/userController.js`

- **Purpose**: Manages HTTP requests related to user profiles.
- **Key Endpoints**:
  - **`getProfile`**: Retrieves a user's profile information.
  - **`updateProfile`**: Updates a user's profile information.

### Admin Controller

### File: `taskflow/backend/src/controllers/adminController.js`

- **Purpose**: Manages administrative tasks such as retrieving all users, deleting a user, and getting a billing overview.
- **Key Endpoints**:
  - **`getAllUsers`**: Retrieves all users from the database.
  - **`deleteUser`**: Deletes a user by their ID.
  - **`getBillingOverview`**: Retrieves a billing overview, including user details and project counts.

### Notification Controller

### File: `taskflow/backend/src/controllers/notificationController.js`

- **Purpose**: Manages HTTP requests related to notifications.
- **Key Endpoints**:
  - **`list`**: Lists notifications for a user, with a limit parameter.
  - **`markRead`**: Marks a specific notification as read for a user.
  - **`getPreferences`**: Retrieves notification preferences for a user.
  - **`updatePreferences`**: Updates notification preferences for a user.

### Attachment Controller

### File: `taskflow/backend/src/controllers/attachmentController.js`

- **Purpose**: Manages HTTP requests related to task attachments.
- **Key Endpoints**:
  - **`list`**: Lists all attachments for a given task ID.
  - **`upload`**: Uploads a file as an attachment to a task, storing it in the filesystem and database.
  - **`download`**: Downloads an attachment by its ID, serving the file from the filesystem.
  - **`remove`**: Deletes an attachment by its ID, removing it from the database and filesystem.

## Services

### Notification Service

### File: `taskflow/backend/src/services/notificationService.js`

- **Purpose**: Manages user notifications and preferences.
- **Key Functions**:
  - **`createNotification`**: Creates a new notification.
  - **`getNotifications`**: Retrieves notifications for a user.
  - **`markAsRead`**: Marks a notification as read.
  - **`getPreferences`**: Retrieves notification preferences for a user.
  - **`updatePreferences`**: Updates notification preferences for a user.

### Report Service

### File: `taskflow/backend/src/services/reportService.js`

- **Purpose**: Generates HTML and PDF reports from task data.
- **Key Functions**:
  - **`generateReportHtml`**: Generates an HTML string for a report based on task data.
  - **`generatePdf`**: Generates a PDF report from an HTML string using `wkhtmltopdf` and file system operations.

## Middleware

### Authentication Middleware

### File: `taskflow/backend/src/middleware/authenticate.js`

- **Purpose**: Authenticates HTTP requests by verifying a JWT token in the authorization header.
- **Key Function**:
  - **`authenticate`**: Checks the authorization header and verifies the JWT token, attaching user information to the request object if valid.

### Authorization Middleware

### File: `taskflow/backend/src/middleware/authorize.js`

- **Purpose**: Authorizes user roles in an HTTP request handling chain.
- **Key Function**:
  - **`authorize`**: Checks if the user is authenticated and if their role is among the allowed roles for the requested resource.

### Error Handling Middleware

### File: `taskflow/backend/src/middleware/errorHandler.js`

- **Purpose**: Handles errors in an Express.js application.
- **Key Function**:
  - **`errorHandler`**: Logs the error details and sends a JSON response with the error message, stack trace, and status code.

### File Upload Middleware

### File: `taskflow/backend/src/middleware/upload.js`

- **Purpose**: Configures and exports a multer middleware for handling file uploads.
- **Key Function**:
  - **`upload`**: Configures the upload directory and file naming strategy.

### Rate Limiter Middleware

### File: `taskflow/backend/src/middleware/rateLimiter.js`

- **Purpose**: Limits the rate of report generation requests to prevent abuse.
- **Key Function**:
  - **`reportLimiter`**: Limits the rate of report generation requests to 10 per minute.

## Routes

### Task Routes

### File: `taskflow/backend/src/routes/taskRoutes.js`

- **Purpose**: Defines routes for task management.
- **Key Endpoints**:
  - **`GET /`**: Lists all tasks.
  - **`GET /:taskId/comments`**: Retrieves comments for a specific task.
  - **`POST /:taskId/comments`**: Adds a comment to a specific task.
  - **`GET /:taskId`**: Retrieves a single task by ID.
  - **`POST /`**: Creates a new task.
  - **`PUT /:taskId`**: Updates a task by ID.
  - **`DELETE /:taskId`**: Deletes a task by ID.

### Project Routes

### File: `taskflow/backend/src/routes/projectRoutes.js`

- **Purpose**: Defines routes for project management.
- **Key Endpoints**:
  - **`GET /`**: Lists all projects.
  - **`GET /:projectId`**: Retrieves a single project by ID.
  - **`POST /`**: Creates a new project.
  - **`PUT /:projectId`**: Updates an existing project by ID.
  - **`DELETE /:projectId`**: Deletes a project by ID.

### User Routes

### File: `taskflow/backend/src/routes/userRoutes.js`

- **Purpose**: Defines routes for user profile management.
- **Key Endpoints**:
  - **`GET /profile`**: Retrieves the user's profile information.
  - **`PATCH /profile`**: Updates the user's profile information.

### Admin Routes

### File: `taskflow/backend/src/routes/adminRoutes.js`

- **Purpose**: Defines routes for administrative tasks.
- **Key Endpoints**:
  - **`GET /users`**: Retrieves all users.
  - **`DELETE /users/:id`**: Deletes a user by ID.
  - **`GET /billing`**: Retrieves a billing overview.

### Notification Routes

### File: `taskflow/backend/src/routes/notificationRoutes.js`

- **Purpose**: Defines routes for notification management.
- **Key Endpoints**:
  - **`GET /`**: Lists all notifications for the authenticated user.
  - **`POST /:id/read`**: Marks a specific notification as read for the authenticated user.
  - **`GET /preferences`**: Retrieves the notification preferences for the authenticated user.
  - **`PATCH /preferences`**: Updates the notification preferences for the authenticated user.

### Attachment Routes

### File: `taskflow/backend/src/routes/attachmentRoutes.js`

- **Purpose**: Defines routes for attachment management.
- **Key Endpoints**:
  - **`GET /task/:taskId`**: Lists attachments for a specific task.
  - **`POST /task/:taskId`**: Uploads a new attachment for a specific task.
  - **`GET /:attachmentId`**: Downloads an attachment by its ID.
  - **`DELETE /:attachmentId`**: Deletes an attachment by its ID.

### Import Routes

### File: `taskflow/backend/src/routes/importRoutes.js`

- **Purpose**: Defines routes for importing data into a project.
- **Key Endpoints**:
  - **`POST /project/:projectId/xml`**: Imports XML data into a project.
  - **`POST /project/:projectId/csv`**: Imports CSV data into a project.

### Report Routes

### File: `taskflow/backend/src/routes/reportRoutes.js`

- **Purpose**: Defines routes for generating PDF reports.
- **Key Endpoints**:
  - **`GET /project/:projectId/pdf`**: Generates a PDF for a specific project ID. Requires authentication and is rate-limited.

## Summary

The Data Layer in TaskFlow is designed to handle all database interactions, ensuring that data is managed efficiently and securely. The models provide the necessary functions to interact with the database, while the controllers handle HTTP requests and responses. Middleware components ensure that requests are authenticated and authorized, and error handling is consistent. The routes define the API endpoints, and services provide additional functionality for tasks like generating reports and managing notifications.