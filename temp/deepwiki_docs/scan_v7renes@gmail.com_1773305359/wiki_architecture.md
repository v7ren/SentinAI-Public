# Architecture and Data Flow

## Main Architectural Components

The TaskFlow application is built using a client-server architecture, with a React-based frontend and a Node.js backend. The main components of the system are:

### Backend Components

1. **Server**
   - **File**: `taskflow\backend\server.js`
   - **Description**: Sets up and starts a Node.js server using an Express application. It configures the server to listen on a specified port (default 3001) and initializes the application.
   - **Key Functions**:
     - `app.listen`: Starts the Express application and listens on the specified port.

2. **Database Configuration**
   - **File**: `taskflow\backend\config\db.js`
   - **Description**: Sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries. It uses environment variables for configuration, with fallbacks for local development.
   - **Key Functions**:
     - `pool`: A PostgreSQL connection pool instance.
     - `query`: A function that takes SQL text and parameters, and executes the query using the connection pool.

3. **Controllers**
   - **Project Controller**
     - **File**: `taskflow\backend\src\controllers\projectController.js`
     - **Description**: Manages project-related operations such as listing, retrieving, creating, updating, and deleting projects.
     - **Key Endpoints**:
       - `GET /projects`: Lists projects for a specific organization.
       - `GET /projects/:projectId`: Retrieves a single project by ID.
       - `POST /projects`: Creates a new project.
       - `PUT /projects/:projectId`: Updates an existing project.
       - `DELETE /projects/:projectId`: Deletes a project.
   - **Task Controller**
     - **File**: `taskflow\backend\src\controllers\taskController.js`
     - **Description**: Manages task-related operations such as listing, retrieving, creating, updating, and deleting tasks, as well as managing comments.
     - **Key Endpoints**:
       - `GET /tasks`: Lists tasks for a specific project or across an organization.
       - `GET /tasks/:taskId`: Retrieves a single task by ID.
       - `POST /tasks`: Creates a new task.
       - `PUT /tasks/:taskId`: Updates an existing task.
       - `DELETE /tasks/:taskId`: Deletes a task.
   - **Report Controller**
     - **File**: `taskflow\backend\src\controllers\reportController.js`
     - **Description**: Handles the generation of PDF reports for projects.
     - **Key Endpoints**:
       - `GET /api/reports/:projectId/pdf`: Generates a PDF report for a specific project.
   - **Import Controller**
     - **File**: `taskflow\backend\src\controllers\importController.js`
     - **Description**: Manages the import of tasks from XML and CSV formats into a project.
     - **Key Endpoints**:
       - `POST /api/projects/:projectId/import/xml`: Imports tasks from XML data.
       - `POST /api/projects/:projectId/import/csv`: Imports tasks from CSV data.
   - **Admin Controller**
     - **File**: `taskflow\backend\src\controllers\adminController.js`
     - **Description**: Manages administrative tasks such as retrieving all users, deleting a user, and getting a billing overview.
     - **Key Endpoints**:
       - `GET /admin/users`: Retrieves all users.
       - `DELETE /admin/users/:id`: Deletes a user by ID.
       - `GET /admin/billing`: Retrieves a billing overview.
   - **Notification Controller**
     - **File**: `taskflow\backend\src\controllers\notificationController.js`
     - **Description**: Manages notifications, including listing notifications, marking them as read, and managing user preferences.
     - **Key Endpoints**:
       - `GET /notifications`: Lists notifications for a user.
       - `PUT /notifications/:id/read`: Marks a specific notification as read.
       - `GET /notifications/preferences`: Retrieves notification preferences for a user.
       - `POST /notifications/preferences`: Updates notification preferences for a user.
   - **User Controller**
     - **File**: `taskflow\backend\src\controllers\userController.js`
     - **Description**: Manages user profile operations such as retrieving and updating user profiles.
     - **Key Endpoints**:
       - `GET /profile`: Retrieves the user profile for the authenticated user.
       - `PUT /profile`: Updates the user profile for the authenticated user.
   - **Attachment Controller**
     - **File**: `taskflow\backend\src\controllers\attachmentController.js`
     - **Description**: Manages task attachments, including listing, uploading, downloading, and removing attachments.
     - **Key Endpoints**:
       - `GET /api/tasks/:taskId/attachments`: Lists all attachments for a given task ID.
       - `POST /api/tasks/:taskId/attachments`: Uploads a new attachment for a given task ID.
       - `GET /api/tasks/:taskId/attachments/:attachmentId`: Downloads an attachment by its ID.
       - `DELETE /api/tasks/:taskId/attachments/:attachmentId`: Removes an attachment by its ID.

4. **Middleware**
   - **Authentication Middleware**
     - **File**: `taskflow\backend\src\middleware\authenticate.js`
     - **Description**: Authenticates HTTP requests by verifying a JWT token in the authorization header.
     - **Key Functions**:
       - `authenticate`: Middleware function that checks the authorization header for a valid JWT token and attaches user information to the request object.
   - **Authorization Middleware**
     - **File**: `taskflow\backend\src\middleware\authorize.js`
     - **Description**: Authorizes user roles in an HTTP request handling chain.
     - **Key Functions**:
       - `authorize`: Middleware function that checks if the user has the required roles to access a resource.
   - **Error Handler Middleware**
     - **File**: `taskflow\backend\src\middleware\errorHandler.js`
     - **Description**: Handles errors in the Express.js application by logging them and sending a JSON response.
     - **Key Functions**:
       - `errorHandler`: Middleware function that logs the error and sends a JSON response with the error details and status code.
   - **Rate Limiter Middleware**
     - **File**: `taskflow\backend\src\middleware\rateLimiter.js`
     - **Description**: Limits the rate of report generation requests to prevent abuse of the PDF export feature.
     - **Key Functions**:
       - `reportLimiter`: Middleware to limit the rate of report generation requests to 10 per minute.
   - **File Upload Middleware**
     - **File**: `taskflow\backend\src\middleware\upload.js`
     - **Description**: Configures and exports a multer middleware for handling file uploads.
     - **Key Functions**:
       - `upload`: Multer middleware instance configured for file uploads, setting the upload directory and file naming.

5. **Models**
   - **Project Model**
     - **File**: `taskflow\backend\src\models\projectModel.js`
     - **Description**: Defines functions for interacting with the 'projects' table in the database.
     - **Key Functions**:
       - `find`, `create`, `update`, `remove`: Functions to find, create, update, and delete project records.
   - **User Model**
     - **File**: `taskflow\backend\src\models\userModel.js`
     - **Description**: Defines functions for interacting with the 'users' table in the database.
     - **Key Functions**:
       - `find`, `create`, `update`: Functions to find, create, and update user records.
   - **Task Model**
     - **File**: `taskflow\backend\src\models\taskModel.js`
     - **Description**: Defines functions for interacting with the 'tasks' table in the database.
     - **Key Functions**:
       - `find`, `create`, `update`, `remove`: Functions to find, create, update, and delete task records.
   - **Organization Model**
     - **File**: `taskflow\backend\src\models\orgModel.js`
     - **Description**: Defines functions for interacting with the 'orgs' and 'org_members' tables in the database.
     - **Key Functions**:
       - `findById`, `create`, `addMember`, `getMembers`: Functions to find an organization, create a new organization, add a member to an organization, and retrieve members of an organization.

6. **Services**
   - **Email Service**
     - **File**: `taskflow\backend\src\services\emailService.js`
     - **Description**: Provides functions for sending emails using SendGrid.
     - **Key Functions**:
       - `sendInvite`: Sends an invitation email to a user.
       - `sendPasswordReset`: Sends a password reset email to a user.
   - **Notification Service**
     - **File**: `taskflow\backend\src\services\notificationService.js`
     - **Description**: Provides functions to create, retrieve, and manage user notifications and preferences.
     - **Key Functions**:
       - `create`, `getForUser`, `markRead`, `getPreferences`, `updatePreferences`: Functions to create, retrieve, mark as read, and manage notification preferences.
   - **Report Service**
     - **File**: `taskflow\backend\src\services\reportService.js`
     - **Description**: Provides functions for generating HTML and PDF reports from task data.
     - **Key Functions**:
       - `generateReportHtml`, `generatePdf`: Functions to generate an HTML report and convert it to a PDF.
   - **Stripe Service**
     - **File**: `taskflow\backend\src\services\stripeService.js`
     - **Description**: Provides functions to interact with the Stripe API for customer management, checkout sessions, billing portal sessions, and webhook event construction.
     - **Key Functions**:
       - `createCustomer`, `createCheckoutSession`, `createBillingPortalSession`, `constructEvent`: Functions to create customers, checkout sessions, billing portal sessions, and construct webhook events.

7. **Utilities**
   - **Logger**
     - **File**: `taskflow\backend\src\utils\logger.js`
     - **Description**: Defines a simple logging utility that formats log entries as JSON objects and outputs them to the console.
     - **Key Functions**:
       - `info`, `warn`, `error`: Functions to log informational, warning, and error messages with optional metadata.
   - **Token Utilities**
     - **File**: `taskflow\backend\src\utils\tokenUtils.js`
     - **Description**: Provides functions for generating and verifying JWT access and refresh tokens.
     - **Key Functions**:
       - `tokenUtils`: Functions to sign and verify JWT access and refresh tokens.
   - **Validators**
     - **File**: `taskflow\backend\src\utils\validators.js`
     - **Description**: Contains utility functions for validating and sanitizing strings.
     - **Key Functions**:
       - `isEmail`, `isNonEmptyString`, `sanitizeString`: Functions to validate email format, check for non-empty strings, and sanitize strings.

### Frontend Components

1. **Main Application**
   - **File**: `taskflow\frontend\src\App.jsx`
   - **Description**: The main entry point of the React application, setting up routing for various pages, including public and private routes.
   - **Key Components**:
     - `App`: Main application component that sets up routing for different pages.

2. **API Client**
   - **File**: `taskflow\frontend\src\api\client.js`
   - **Description**: Sets up an Axios client for making HTTP requests to the backend API.
   - **Key Functions**:
     - `client`: Axios client instance configured with interceptors for adding authentication tokens and handling unauthorized responses.

3. **Pages**
   - **Dashboard Page**
     - **File**: `taskflow\frontend\src\pages\DashboardPage.jsx`
     - **Description**: Displays a dashboard with statistics about open tasks, overdue tasks, and projects.
   - **Login Page**
     - **File**: `taskflow\frontend\src\pages\LoginPage.jsx`
     - **Description**: Handles user login with form fields for email and password.
   - **Register Page**
     - **File**: `taskflow\frontend\src\pages\RegisterPage.jsx`
     - **Description**: Handles user registration with form fields for full name, email, and password.
   - **Admin Page**
     - **File**: `taskflow\frontend\src\pages\AdminPage.jsx`
     - **Description**: Serves as a page for administrative tasks, displaying a table of users.
   - **Project Detail Page**
     - **File**: `taskflow\frontend\src\pages\ProjectDetailPage.jsx`
     - **Description**: Displays detailed information about a specific project.
   - **Projects Page**
     - **File**: `taskflow\frontend\src\pages\ProjectsPage.jsx`
     - **Description**: Displays a list of projects and allows users to create new projects.
   - **Settings Page**
     - **File**: `taskflow\frontend\src\pages\SettingsPage.jsx`
     - **Description**: Allows users to update their full name.
   - **Task Detail Page**
     - **File**: `taskflow\frontend\src\pages\TaskDetailPage.jsx`
     - **Description**: Displays detailed information about a specific task.
   - **Tasks Page**
     - **File**: `taskflow\frontend\src\pages\TasksPage.jsx`
     - **Description**: Displays a list of tasks and allows users to filter tasks by project and search term.
   - **Landing Page**
     - **File**: `taskflow\frontend\src\pages\LandingPage.jsx`
     - **Description**: Serves as the main landing page for the TaskFlow application.
   - **Not Found Page**
     - **File**: `taskflow\frontend\src\pages\NotFoundPage.jsx`
     - **Description**: Displays a 404 error message and a link to return to the home page.

4. **Components**
   - **Navbar**
     - **File**: `taskflow\frontend\src\components\Layout\Navbar.jsx`
     - **Description**: Displays a navigation bar with links to the dashboard and settings pages, and a logout button.
   - **Sidebar**
     - **File**: `taskflow\frontend\src\components\Layout\Sidebar.jsx`
     - **Description**: Displays navigation links and user information.
   - **Page Wrapper**
     - **File**: `taskflow\frontend\src\components\Layout\PageWrapper.jsx`
     - **Description**: Serves as a layout container for other components.
   - **Project Card**
     - **File**: `taskflow\frontend\src\components\Projects\ProjectCard.jsx`
     - **Description**: Displays a card for a project with its name, description, and archived status.
   - **Task Card**
     - **File**: `taskflow\frontend\src\components\Tasks\TaskCard.jsx`
     - **Description**: Displays a card for a task with its title, status, priority, due date, and assignee.
   - **Task Detail**
     - **File**: `taskflow\frontend\src\components\Tasks\TaskDetail.jsx`
     - **Description**: Displays detailed information about a specific task, including comments.
   - **Task Form**
     - **File**: `taskflow\frontend\src\components\Tasks\TaskForm.jsx`
     - **Description**: Allows users to create or edit a task.
   - **Comment List**
     - **File**: `taskflow\frontend\src\components\Tasks\CommentList.jsx`
     - **Description**: Displays a list of comments for a given task and allows users to add new comments.
   - **Button**
     - **File**: `taskflow\frontend\src\components\UI\Button.jsx`
     - **Description**: A reusable button component.
   - **Spinner**
     - **File**: `taskflow\frontend\src\components\UI\Spinner.jsx`
     - **Description**: A reusable loading spinner component.
   - **Badge**
     - **File**: `taskflow\frontend\src\components\UI\Badge.jsx`
     - **Description**: A reusable badge component with different styles.
   - **Modal**
     - **File**: `taskflow\frontend\src\components\UI\Modal.jsx`
     - **Description**: A reusable modal dialog component.

5. **Hooks**
   - **Auth Hook**
     - **File**: `taskflow\frontend\src\hooks\useAuth.js`
     - **Description**: Manages authentication state in a React application.
   - **Tasks Hook**
     - **File**: `taskflow\frontend\src\hooks\useTasks.js`
     - **Description**: Manages the state and lifecycle of tasks for a given project.
   - **Projects Hook**
     - **File**: `taskflow\frontend\src\hooks\useProjects.js`
     - **Description**: Manages the state and lifecycle of projects data.

6. **Context**
   - **Auth Context**
     - **File**: `taskflow\frontend\src\context\AuthContext.jsx`
     - **Description**: Provides state management and functions for user login, registration, and logout.

7. **Utilities**
   - **Analytics**
     - **File**: `taskflow\frontend\src\utils\analytics.js`
     - **Description**: Contains utility functions for tracking user events and identifying users in Mixpanel and Google Analytics.
   - **Auth Utilities**
     - **File**: `taskflow\frontend\src\utils\authUtils.js`
     - **Description**: Contains utility functions for managing authentication sessions in the frontend.
   - **Formatters**
     - **File**: `taskflow\frontend\src\utils\formatters.js`
     - **Description**: Contains utility functions for formatting dates, priorities, and statuses.

## Data and Control Flow

### Backend Flow

1. **Request Handling**
   - The Node.js server listens for incoming HTTP requests.
   - Requests are routed to the appropriate controller based on the endpoint.
   - Middleware functions (authentication, authorization, error handling, rate limiting) are applied as needed.

2. **Database Interactions**
   - Controllers interact with the database using models to perform CRUD operations.
   - The `db.js` file sets up the PostgreSQL connection pool and provides a query function.
   - Models define functions for interacting with specific database tables.

3. **Service Layer**
   - Services provide additional functionality, such as generating reports, sending emails, and interacting with external APIs (e.g., Stripe).
   - Controllers can call service functions to perform these tasks.

4. **Response Handling**
   - Controllers handle the business logic and prepare the response data.
   - The response is sent back to the client with the appropriate HTTP status code and data.

### Frontend Flow

1. **Application Initialization**
   - The `App` component sets up routing and authentication context.
   - The `AuthProvider` component manages the authentication state and provides authentication functions.

2. **API Interactions**
   - The Axios client is configured to handle HTTP requests to the backend API.
   - Custom hooks (e.g., `useTasks`, `useProjects`) manage the state and lifecycle of data fetched from the API.

