# Overview

## What is TaskFlow?

TaskFlow is a comprehensive project management tool designed to streamline the workflow of teams and organizations. It provides a robust set of features for managing projects, tasks, users, and notifications, all while ensuring secure and efficient operations. TaskFlow is built using a modern tech stack, including Node.js, Express, PostgreSQL, and React, and it is designed to be scalable, maintainable, and user-friendly.

## Main Components

### Backend

1. **Database Configuration (`taskflow\backend\config\db.js`)**:
   - Sets up a PostgreSQL database connection pool.
   - Provides a query function for executing SQL queries.
   - Uses environment variables for configuration, with fallbacks for local development.

2. **Server Setup (`taskflow\backend\server.js`)**:
   - Initializes and starts a Node.js server using an Express application.
   - Listens on a specified port (default 3001) and logs a message upon successful startup.

3. **Express Application (`taskflow\backend\src\app.js`)**:
   - Configures middleware for JSON and text parsing.
   - Serves static files from the uploads directory.
   - Mounts various API routes for authentication, tasks, projects, users, attachments, reports, imports, notifications, and admin functionalities.
   - Includes a health check endpoint and an error handler middleware.

4. **Controllers**:
   - **Report Controller (`taskflow\backend\src\controllers\reportController.js`)**:
     - Handles generating PDF reports for projects.
   - **Import Controller (`taskflow\backend\src\controllers\importController.js`)**:
     - Manages importing tasks from XML and CSV formats.
   - **Admin Controller (`taskflow\backend\src\controllers\adminController.js`)**:
     - Provides endpoints for administrative tasks like managing users and billing.
   - **Attachment Controller (`taskflow\backend\src\controllers\attachmentController.js`)**:
     - Manages task attachments, including listing, uploading, downloading, and removing.
   - **Notification Controller (`taskflow\backend\src\controllers\notificationController.js`)**:
     - Handles notifications, including listing, marking as read, and managing preferences.
   - **Project Controller (`taskflow\backend\src\controllers\projectController.js`)**:
     - Manages projects, including listing, retrieving, creating, updating, and deleting.
   - **User Controller (`taskflow\backend\src\controllers\userController.js`)**:
     - Manages user profiles, including retrieving and updating.
   - **Task Controller (`taskflow\backend\src\controllers\taskController.js`)**:
     - Manages tasks, including listing, retrieving, creating, updating, and deleting.
   - **Auth Controller (`taskflow\backend\src\controllers\authController.js`)**:
     - Handles user authentication, including registration, login, token refresh, password reset, and logout.

5. **Middleware**:
   - **Authorize (`taskflow\backend\src\middleware\authorize.js`)**:
     - Middleware for authorizing user roles.
   - **Authenticate (`taskflow\backend\src\middleware\authenticate.js`)**:
     - Middleware for authenticating HTTP requests using JWT tokens.
   - **Error Handler (`taskflow\backend\src\middleware\errorHandler.js`)**:
     - Middleware for handling errors, logging them, and sending JSON responses.
   - **Rate Limiter (`taskflow\backend\src\middleware\rateLimiter.js`)**:
     - Middleware for rate limiting report generation requests.
   - **Upload (`taskflow\backend\src\middleware\upload.js`)**:
     - Middleware for handling file uploads using Multer.

6. **Models**:
   - **Task Model (`taskflow\backend\src\models\taskModel.js`)**:
     - Provides functions for interacting with the 'tasks' table in the database.
   - **User Model (`taskflow\backend\src\models\userModel.js`)**:
     - Provides functions for interacting with the 'users' table in the database.
   - **Org Model (`taskflow\backend\src\models\orgModel.js`)**:
     - Provides functions for interacting with the 'orgs' and 'org_members' tables in the database.
   - **Project Model (`taskflow\backend\src\models\projectModel.js`)**:
     - Provides functions for interacting with the 'projects' table in the database.

7. **Services**:
   - **Email Service (`taskflow\backend\src\services\emailService.js`)**:
     - Provides functions for sending emails using SendGrid.
   - **Notification Service (`taskflow\backend\src\services\notificationService.js`)**:
     - Manages user notifications and preferences.
   - **Report Service (`taskflow\backend\src\services\reportService.js`)**:
     - Generates HTML and PDF reports for projects.
   - **Stripe Service (`taskflow\backend\src\services\stripeService.js`)**:
     - Interacts with the Stripe API for customer management, checkout sessions, and billing portal sessions.

8. **Utils**:
   - **Token Utils (`taskflow\backend\src\utils\tokenUtils.js`)**:
     - Provides functions for generating and verifying JWT access and refresh tokens.
   - **Logger (`taskflow\backend\src\utils\logger.js`)**:
     - Provides a simple logging utility for formatting log entries as JSON objects.
   - **Merge Objects (`taskflow\backend\src\utils\mergeObjects.js`)**:
     - Provides functions for merging objects, specifically designed to handle deep merging of nested objects.
   - **Validators (`taskflow\backend\src\utils\validators.js`)**:
     - Provides functions for validating and sanitizing strings, including email format and non-empty strings.

### Frontend

1. **Main Application (`taskflow\frontend\src\main.jsx`)**:
   - Sets up the React DOM, BrowserRouter for routing, and AuthProvider for authentication context.
   - Renders the main App component.

2. **App Component (`taskflow\frontend\src\App.jsx`)**:
   - Defines the main application component with routing for various pages, including public and private routes.
   - Private routes require user authentication, redirecting unauthenticated users to the login page.

3. **Pages**:
   - **Admin Page (`taskflow\frontend\src\pages\AdminPage.jsx`)**:
     - Displays a page for administrative tasks, including a table of users.
   - **Dashboard Page (`taskflow\frontend\src\pages\DashboardPage.jsx`)**:
     - Displays a dashboard with statistics about open tasks, overdue tasks, and projects.
   - **Landing Page (`taskflow\frontend\src\pages\LandingPage.jsx`)**:
     - Serves as the landing page for the TaskFlow application, including navigation links and sections for features, pricing, and testimonials.
   - **Login Page (`taskflow\frontend\src\pages\LoginPage.jsx`)**:
     - Handles user login with form fields for email and password.
   - **Not Found Page (`taskflow\frontend\src\pages\NotFoundPage.jsx`)**:
     - Displays a 404 error page with a message and a link to return to the home page.
   - **Projects Page (`taskflow\frontend\src\pages\ProjectsPage.jsx`)**:
     - Displays a list of projects and provides a modal for creating new projects.
   - **Project Detail Page (`taskflow\frontend\src\pages\ProjectDetailPage.jsx`)**:
     - Displays detailed information about a project and provides options to view tasks and manage project settings.
   - **Register Page (`taskflow\frontend\src\pages\RegisterPage.jsx`)**:
     - Handles user registration with form fields for full name, email, and password.
   - **Settings Page (`taskflow\frontend\src\pages\SettingsPage.jsx`)**:
     - Allows users to update their full name and other profile information.
   - **Task Detail Page (`taskflow\frontend\src\pages\TaskDetailPage.jsx`)**:
     - Displays detailed information about a task.
   - **Tasks Page (`taskflow\frontend\src\pages\TasksPage.jsx`)**:
     - Displays a list of tasks and allows filtering by project and search term.

3. **Components**:
   - **Page Wrapper (`taskflow\frontend\src\components\Layout\PageWrapper.jsx`)**:
     - Serves as a layout container for other components, including a sidebar and navbar.
   - **Navbar (`taskflow\frontend\src\components\Layout\Navbar.jsx`)**:
     - Displays a navigation bar at the top of the application, including links to the dashboard, user's full name, settings, and a logout button.
   - **Sidebar (`taskflow\frontend\src\components\Layout\Sidebar.jsx`)**:
     - Displays a sidebar with navigation links, which can vary based on the user's role.
   - **Project Card (`taskflow\frontend\src\components\Projects\ProjectCard.jsx`)**:
     - Displays a card for a project, including the project's name, description, and archived status.
   - **Project Settings (`taskflow\frontend\src\components\Projects\ProjectSettings.jsx`)**:
     - Allows users to update the settings of a project, including the name, description, and archived status.
   - **Task Card (`taskflow\frontend\src\components\Tasks\TaskCard.jsx`)**:
     - Displays a card for a task, including its title, status, priority, due date, and assignee.
   - **Task Detail (`taskflow\frontend\src\components\Tasks\TaskDetail.jsx`)**:
     - Displays detailed information about a task, including its status, priority, due date, title, and description.
   - **Comment List (`taskflow\frontend\src\components\Tasks\CommentList.jsx`)**:
     - Displays a list of comments for a task and allows users to add new comments.
   - **Task Form (`taskflow\frontend\src\components\Tasks\TaskForm.jsx`)**:
     - Provides a form for creating or editing a task, including fields for the task's title, description, priority, status, and due date.
   - **Button (`taskflow\frontend\src\components\UI\Button.jsx`)**:
     - A reusable button component with customizable appearance and behavior.
   - **Badge (`taskflow\frontend\src\components\UI\Badge.jsx`)**:
     - A reusable badge component with different variants for styling.
   - **Modal (`taskflow\frontend\src\components\UI\Modal.jsx`)**:
     - A modal component for displaying centered dialog boxes.
   - **Spinner (`taskflow\frontend\src\components\UI\Spinner.jsx`)**:
     - A spinner component for indicating loading states.

4. **API Client**:
   - **Client (`taskflow\frontend\src\api\client.js`)**:
     - Sets up an Axios client for making HTTP requests to the backend API.
     - Includes interceptors for adding authentication tokens and handling unauthorized responses.

5. **Context**:
   - **Auth Context (`taskflow\frontend\src\context\AuthContext.jsx`)**:
     - Provides authentication context to the application, including state management and functions for user login, registration, and logout.

6. **Hooks**:
   - **useAuth (`taskflow\frontend\src\hooks\useAuth.js`)**:
     - A custom hook for managing authentication state.
   - **useProjects (`taskflow\frontend\src\hooks\useProjects.js`)**:
     - A custom hook for managing project data, including fetching, creating, updating, and deleting projects.
   - **useTasks (`taskflow\frontend\src\hooks\useTasks.js`)**:
     - A custom hook for managing task data, including fetching, creating, updating, and deleting tasks.

7. **Utils**:
   - **Analytics (`taskflow\frontend\src\utils\analytics.js`)**:
     - Provides utility functions for tracking user events and identifying users in Mixpanel and Google Analytics.
   - **Formatters (`taskflow\frontend\src\utils\formatters.js`)**:
     - Provides utility functions for formatting dates, priorities, and statuses.
   - **Auth Utils (`taskflow\frontend\src\utils\authUtils.js`)**:
     - Provides utility functions for managing authentication sessions, including saving, clearing, and retrieving session data from the browser's localStorage.

## Typical Usage Scenario

1. **User Registration and Login**:
   - A new user visits the landing page and clicks on the "Register" link.
   - The user fills out the registration form with their full name, email, and password.
   - Upon successful registration, the user is redirected to the login page.
   - The user logs in using their email and password, and the application verifies the credentials using the backend API.

2. **Project Management**:
   - Once logged in, the user is redirected to the dashboard page, which displays an overview of their projects, tasks, and other statistics.
   - The user can navigate to the projects page to view a list of their projects.
   - The user can create a new project by clicking the "Create Project" button, which opens a modal form.
   - The user fills out the project details and submits the form, which sends a POST request to the backend API to create the project.

3. **Task Management**:
   - The user can navigate to a specific project to view its tasks.
   - The user can create a new task by clicking the "Create Task" button, which opens a modal form.
   - The user fills out the task details and submits the form, which sends a POST request to the backend API to create the task.
   - The user can update or delete tasks by interacting with the task cards or the task detail page.

4. **Notifications and Reports**:
   - The user can view and manage notifications from the dashboard or the notifications page.
   - The user can generate a PDF report for a project by navigating to the project detail page and clicking the "Generate Report" button.
   - The report is generated using the backend's report service and sent back to the frontend as a downloadable PDF file.

5. **Admin Functions**:
   - Admin users can access the admin page to manage users, view billing overviews, and perform other administrative tasks.
   - Admin users can create, update, or delete user accounts and manage project memberships.

## Where to Look Next

- **Backend**:
  - **Database Configuration**: For details on how the database is set up and configured, see the `taskflow\backend\config\db.js` file.
  - **Server Setup**: For information on how the server is initialized and started, see the `taskflow\backend\server.js` file.
  - **Controllers**: For detailed documentation on the various controllers and their endpoints, see the respective files in the `taskflow\backend\src\controllers` directory.
  - **Middleware**: For details on the middleware used for authentication, authorization, error handling, and more, see the files in the `taskflow\backend\src\middleware` directory.
  - **Models**: For information on the database models and their functions, see the files in the `taskflow\backend\src\models` directory.
  - **Services**: For details on the services used for email, notifications, reports, and Stripe integration, see the files in the `taskflow\backend\src\services` directory.
  - **Utils**: For utility functions and helpers, see the files in the `taskflow\backend\src\utils` directory.

- **Frontend**:
  - **Main Application**: For an overview of the main application setup, see the `taskflow\frontend\src\main.jsx` file.
  - **App Component**: For details on the main application component and routing, see the `taskflow\frontend\src\App.jsx` file.
  - **Pages**: For detailed documentation on the various pages, see the respective files in the `taskflow\frontend\src\pages` directory.
  - **Components**: For information on the reusable UI components, see the files in the `taskflow\frontend\src\components` directory.
  - **API Client**: For details on the Axios client setup and interceptors, see the `taskflow\frontend\src\api\client.js` file.
  - **Context**: For information on the authentication context, see the `taskflow\frontend\src\context\AuthContext.jsx` file.
  - **Hooks**: For custom hooks used in the application, see the files in the `taskflow\frontend\src\hooks` directory.
  - **Utils**: For utility functions and helpers, see the files in the `taskflow\frontend\src\utils` directory.

For more detailed documentation on specific components, services, and utilities, refer to the respective sections in the documentation.