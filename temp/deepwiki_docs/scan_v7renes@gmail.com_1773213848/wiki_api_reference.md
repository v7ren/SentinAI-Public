# API Reference

This section provides detailed documentation for the RESTful API endpoints, including request and response formats, authentication requirements, and error handling.

## Authentication

### Middleware
- **`authenticate`**: This middleware function checks the authorization header and verifies the JWT token. It attaches user information to the request object if the token is valid. If the token is invalid or missing, it returns a 401 Unauthorized response.
  - **File**: `taskflow/backend/src/middleware/authenticate.js`
  - **Tags**: `auth`, `security`, `network`

- **`authorize`**: This middleware function checks if the user is authenticated and has the required role to proceed. It returns a 401 status if the user is not authenticated, and a 403 status if the user does not have sufficient permissions.
  - **File**: `taskflow/backend/src/middleware/authorize.js`
  - **Tags**: `auth`, `security`

- **`rateLimiter`**: This middleware limits the rate of report generation requests to 10 per minute.
  - **File**: `taskflow/backend/src/middleware/rateLimiter.js`
  - **Tags**: `network`, `security`

### Error Handling
- **`errorHandler`**: This middleware function handles errors by logging them and sending a JSON response with the error message, stack trace, and status code.
  - **File**: `taskflow/backend/src/middleware/errorHandler.js`
  - **Tags**: `logging`, `network`, `security`

## Endpoints

### Authentication
- **`POST /api/register`**: Handles user registration, including validation, password hashing, and creation of user and organization records.
  - **File**: `taskflow/backend/src/controllers/authController.js`
  - **Tags**: `auth`, `db`, `crypto`, `network`, `logging`

- **`POST /api/login`**: Handles user login, including credential validation and token generation.
  - **File**: `taskflow/backend/src/controllers/authController.js`
  - **Tags**: `auth`, `db`, `network`

- **`POST /api/refresh`**: Handles token refresh, generating a new access token from a valid refresh token.
  - **File**: `taskflow/backend/src/controllers/authController.js`
  - **Tags**: `auth`, `db`, `network`

- **`POST /api/forgot-password`**: Handles password reset requests, sending a reset link to the user's email.
  - **File**: `taskflow/backend/src/controllers/authController.js`
  - **Tags**: `auth`, `db`, `network`

- **`POST /api/reset-password`**: Handles password reset, updating the user's password with a new one.
  - **File**: `taskflow/backend/src/controllers/authController.js`
  - **Tags**: `auth`, `db`, `network`

- **`POST /api/logout`**: Handles user logout, invalidating the refresh token.
  - **File**: `taskflow/backend/src/controllers/authController.js`
  - **Tags**: `auth`, `db`, `network`

### Projects
- **`GET /api/projects`**: Lists all projects for a specific organization, optionally including archived projects.
  - **File**: `taskflow/backend/src/controllers/projectController.js`
  - **Tags**: `auth`, `db`, `network`, `security`

- **`GET /api/projects/:projectId`**: Retrieves a single project by ID, with access checks to ensure the project belongs to the requesting organization.
  - **File**: `taskflow/backend/src/controllers/projectController.js`
  - **Tags**: `auth`, `db`, `network`, `security`

- **`POST /api/projects`**: Creates a new project for an organization, requiring a valid project name.
  - **File**: `taskflow/backend/src/controllers/projectController.js`
  - **Tags**: `auth`, `db`, `network`, `security`

- **`PUT /api/projects/:projectId`**: Updates an existing project, with checks to ensure the project belongs to the requesting organization.
  - **File**: `taskflow/backend/src/controllers/projectController.js`
  - **Tags**: `auth`, `db`, `network`, `security`

- **`DELETE /api/projects/:projectId`**: Deletes a project, with checks to ensure the project belongs to the requesting organization.
  - **File**: `taskflow/backend/src/controllers/projectController.js`
  - **Tags**: `auth`, `db`, `network`, `security`

### Tasks
- **`GET /api/tasks`**: Lists tasks for a specific project or across an organization.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

- **`GET /api/tasks/:taskId`**: Retrieves a single task by its ID.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

- **`POST /api/tasks`**: Creates a new task within a project.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

- **`PUT /api/tasks/:taskId`**: Updates an existing task.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

- **`DELETE /api/tasks/:taskId`**: Deletes a task.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

- **`GET /api/tasks/:taskId/comments`**: Retrieves comments for a specific task.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

- **`POST /api/tasks/:taskId/comments`**: Adds a comment to a specific task.
  - **File**: `taskflow/backend/src/controllers/taskController.js`
  - **Tags**: `auth`, `db`, `network`, `logging`

### Attachments
- **`GET /api/tasks/:taskId/attachments`**: Lists all attachments for a given task ID.
  - **File**: `taskflow/backend/src/controllers/attachmentController.js`
  - **Tags**: `auth`, `db`, `file_io`, `network`

- **`POST /api/tasks/:taskId/attachments`**: Uploads a file and stores its metadata in the database.
  - **File**: `taskflow/backend/src/controllers/attachmentController.js`
  - **Tags**: `auth`, `db`, `file_io`, `network`

- **`GET /api/tasks/:taskId/attachments/:attachmentId`**: Downloads a file based on the attachment ID.
  - **File**: `taskflow/backend/src/controllers/attachmentController.js`
  - **Tags**: `auth`, `db`, `file_io`, `network`

- **`DELETE /api/tasks/:taskId/attachments/:attachmentId`**: Deletes an attachment and its associated file from the filesystem.
  - **File**: `taskflow/backend/src/controllers/attachmentController.js`
  - **Tags**: `auth`, `db`, `file_io`, `network`

### Reports
- **`GET /api/reports/:projectId/pdf`**: Generates a PDF for a project with the specified project ID. Requires authentication and is rate-limited.
  - **File**: `taskflow/backend/src/controllers/reportController.js`
  - **Tags**: `auth`, `db`, `network`, `security`

### Admin
- **`GET /admin/users`**: Fetches all users, requires authentication.
  - **File**: `taskflow/backend/src/controllers/adminController.js`
  - **Tags**: `auth`, `db`, `network`

- **`DELETE /admin/users/:id`**: Deletes a user by ID, requires authentication.
  - **File**: `taskflow/backend/src/controllers/adminController.js`
  - **Tags**: `auth`, `db`, `network`

- **`GET /admin/billing`**: Fetches a billing overview, requires authentication.
  - **File**: `taskflow/backend/src/controllers/adminController.js`
  - **Tags**: `auth`, `db`, `network`

### Notifications
- **`GET /notifications`**: Lists all notifications for the authenticated user.
  - **File**: `taskflow/backend/src/controllers/notificationController.js`
  - **Tags**: `auth`, `db`, `network`

- **`PUT /notifications/:id/read`**: Marks a specific notification as read for the authenticated user.
  - **File**: `taskflow/backend/src/controllers/notificationController.js`
  - **Tags**: `auth`, `db`, `network`

- **`GET /notifications/preferences`**: Retrieves the notification preferences for the authenticated user.
  - **File**: `taskflow/backend/src/controllers/notificationController.js`
  - **Tags**: `auth`, `db`, `network`

- **`POST /notifications/preferences`**: Updates the notification preferences for the authenticated user.
  - **File**: `taskflow/backend/src/controllers/notificationController.js`
  - **Tags**: `auth`, `db`, `network`

### User Profile
- **`GET /profile`**: Retrieves the user's profile information.
  - **File**: `taskflow/backend/src/controllers/userController.js`
  - **Tags**: `auth`, `db`, `network`

- **`PUT /profile`**: Updates the user's profile information.
  - **File**: `taskflow/backend/src/controllers/userController.js`
  - **Tags**: `auth`, `db`, `network`

### Import
- **`POST /api/projects/:projectId/import/xml`**: Imports tasks from XML data. It parses the XML, checks the project existence and permissions, and creates tasks in the database.
  - **File**: `taskflow/backend/src/controllers/importController.js`
  - **Tags**: `auth`, `db`, `network`, `file_io`

- **`POST /api/projects/:projectId/import/csv`**: Imports tasks from CSV data. It parses the CSV, checks the project existence and permissions, and creates tasks in the database.
  - **File**: `taskflow/backend/src/controllers/importController.js`
  - **Tags**: `auth`, `db`, `network`, `file_io`

### Health Check
- **`GET /api/v1/health`**: Endpoint to check the health of the application, returning a JSON object with a status and timestamp.
  - **File**: `taskflow/backend/src/app.js`
  - **Tags**: `network`, `auth`, `db`, `file_io`, `other`

## Models

### Project Model
- **`projectModel`**: Provides database operations for the 'projects' table, such as finding, creating, updating, and deleting project records.
  - **File**: `taskflow/backend/src/models/projectModel.js`
  - **Tags**: `db`

### Task Model
- **`taskModel`**: Provides database operations for the 'tasks' table, including finding tasks by ID or project, creating new tasks, updating existing tasks, and removing tasks.
  - **File**: `taskflow/backend/src/models/taskModel.js`
  - **Tags**: `db`

### User Model
- **`userModel`**: Provides database operations for the 'users' table, including finding users by ID or email, creating new users, updating refresh tokens, setting and clearing reset tokens, and updating passwords.
  - **File**: `taskflow/backend/src/models/userModel.js`
  - **Tags**: `db`

### Organization Model
- **`orgModel`**: Provides database operations for the 'orgs' and 'org_members' tables, including finding an organization by ID, creating a new organization, adding a member to an organization, and retrieving the members of an organization.
  - **File**: `taskflow/backend/src/models/orgModel.js`
  - **Tags**: `db`

## Services

### Email Service
- **`sendInvite`**: Sends an invitation email to a user.
  - **File**: `taskflow/backend/src/services/emailService.js`
  - **Tags**: `network`, `email`

- **`sendPasswordReset`**: Sends a password reset email to a user.
  - **File**: `taskflow/backend/src/services/emailService.js`
  - **Tags**: `network`, `email`

### Notification Service
- **`create`**: Creates a new notification for a user and returns the created notification.
  - **File**: `taskflow/backend/src/services/notificationService.js`
  - **Tags**: `db`, `auth`

- **`getForUser`**: Retrieves a list of notifications for a specific user, with an optional limit.
  - **File**: `taskflow/backend/src/services/notificationService.js`
  - **Tags**: `db`, `auth`

- **`markRead`**: Marks a specific notification as read for a user.
  - **File**: `taskflow/backend/src/services/notificationService.js`
  - **Tags**: `db`, `auth`

- **`getPreferences`**: Retrieves the notification preferences for a user, merging with default preferences if necessary.
  - **File**: `taskflow/backend/src/services/notificationService.js`
  - **Tags**: `db`, `auth`

- **`updatePreferences`**: Updates the notification preferences for a user and returns the updated preferences.
  - **File**: `taskflow/backend/src/services/notificationService.js`
  - **Tags**: `db`, `auth`

### Report Service
- **`generateReportHtml`**: Generates an HTML string for a report based on task data.
  - **File**: `taskflow/backend/src/services/reportService.js`
  - **Tags**: `file_io`, `process`, `other`

- **`generatePdf`**: Generates a PDF report from an HTML string and returns it as a buffer.
  - **File**: `taskflow/backend/src/services/reportService.js`
  - **Tags**: `file_io`, `process`, `other`

### Stripe Service
- **`createCustomer`**: Creates a new customer in Stripe with the provided email and name.
  - **File**: `taskflow/backend/src/services/stripeService.js`
  - **Tags**: `network`, `process`, `security`, `other`

- **`createCheckoutSession`**: Creates a new checkout session for a subscription, linking it to a customer and specifying success and cancel URLs.
  - **File**: `taskflow/backend/src/services/stripeService.js`
  - **Tags**: `network`, `process`, `security`, `other`

- **`createBillingPortalSession`**: Creates a new billing portal session for a customer, specifying a return URL.
  - **File**: `taskflow/backend/src/services/stripeService.js`
  - **Tags**: `network`, `process`, `security`, `other`

- **`constructEvent`**: Constructs a Stripe webhook event from the provided payload, signature, and secret.
  - **File**: `taskflow/backend/src/services/stripeService.js`
  - **Tags**: `network`, `process`, `security`, `other`

## Utilities

### Token Utils
- **`tokenUtils`**: Provides functions for signing and verifying JWT access and refresh tokens.
  - **File**: `taskflow/backend/src/utils/tokenUtils.js`
  - **Tags**: `auth`, `crypto`

### Logger
- **`info`**: Logs an informational message with optional metadata.
  - **File**: `taskflow/backend/src/utils/logger.js`
  - **Tags**: `logging`

- **`warn`**: Logs a warning message with optional metadata.
  - **File**: `taskflow/backend/src/utils/logger.js`
  - **Tags**: `logging`

- **`error`**: Logs an error message with optional metadata.
  - **File**: `taskflow/backend/src/utils/logger.js`
  - **Tags**: `logging`

### Merge Objects
- **`mergeDeep`**: Performs a deep merge of two objects, preserving nested objects.
  - **File**: `taskflow/backend/src/utils/mergeObjects.js`
  - **Tags**: `other`

- **`mergeObjects`**: Merges multiple objects into a single object, using `mergeDeep` to handle deep merging.
  - **File**: `taskflow/backend/src/utils/mergeObjects.js`
  - **Tags**: `other`

### Validators
- **`isEmail`**: Validates if a string is a valid email address.
  - **File**: `taskflow/backend/src/utils/validators.js`
  - **Tags**: `other`

- **`isNonEmptyString`**: Checks if a string is non-empty and meets a minimum length requirement.
  - **File**: `taskflow/backend/src/utils/validators.js`
  - **Tags**: `other`

- **`sanitizeString`**: Sanitizes a string by trimming and limiting its length.
  - **File**: `taskflow/backend/src/utils/validators.js`
  - **Tags**: `other`

### Formatters
- **`formatDate`**: Formats a given date object or string into a short date format (e.g., 'Jan 1, 2023').
  - **File**: `taskflow/frontend/src/utils/formatters.js`
  - **Tags**: `other`

- **`formatRelative`**: Formats a given date object or string into a relative time format (e.g., 'Just now', '10m ago', '2h ago').
  - **File**: `taskflow/frontend/src/utils/formatters.js`
  - **Tags**: `other`

- **`priorityLabel`**: Capitalizes the first letter of a given priority string, defaulting to 'Medium' if no value is provided.
  - **File**: `taskflow/frontend/src/utils/formatters.js`
  - **Tags**: `other`

- **`statusLabel`**: Capitalizes the first letter of each word in a given status string, replacing underscores with spaces, defaulting to 'Open' if no value is provided.
  - **File**: `taskflow/frontend/src/utils/formatters.js`
  - **Tags**: `other`

### Auth Utils
- **`saveSession`**: Saves the authentication token, user data, and refresh token to local storage.
  - **File**: `taskflow/frontend/src/utils/authUtils.js`
  - **Tags**: `auth`, `storage`

- **`clearSession`**: Clears the authentication session data from local storage.
  - **File**: `taskflow/frontend/src/utils/authUtils.js`
  - **Tags**: `auth`, `storage`

- **`getToken`**: Retrieves the authentication token from local storage.
  - **File**: `taskflow/frontend/src/utils/authUtils.js`
  - **Tags**: `auth`, `storage`

- **`getRefreshToken`**: Retrieves the refresh token from local storage.
  - **File**: `taskflow/frontend/src/utils/authUtils.js`
  - **Tags**: `auth`, `storage`

- **`getStoredUser`**: Retrieves the user data from local storage, parsing it from JSON.
  - **File**: `taskflow/frontend/src/utils/authUtils.js`
  - **Tags**: `auth`, `storage`

### Analytics
- **`trackEvent`**: Tracks an event with optional properties using Mixpanel and Google Analytics.
  - **File**: `taskflow/frontend/src/utils/analytics.js`
  - **Tags**: `network`, `logging`

- **`identify`**: Identifies a user with optional traits using Mixpanel and Google Analytics