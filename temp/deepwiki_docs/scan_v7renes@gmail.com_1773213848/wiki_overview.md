# Overview

## What is TaskFlow?

TaskFlow is a project management application designed to help organizations and teams efficiently manage their tasks and projects. It provides a comprehensive set of features for task tracking, project management, user authentication, and reporting. The application is built using a modern tech stack, including Node.js, Express, PostgreSQL, and React.

## Main Components

### Backend

1. **Database Configuration (`taskflow/backend/config/db.js`)**:
   - Sets up a PostgreSQL database connection pool.
   - Provides a query function for executing SQL queries.
   - Uses environment variables for configuration, with fallbacks for local development.

2. **Server Setup (`taskflow/backend/server.js`)**:
   - Sets up and starts a Node.js server using an Express application.
   - Listens on a specified port, defaulting to 3001 if not defined in the environment variables.

3. **Express Application (`taskflow/backend/src/app.js`)**:
   - Configures middleware for JSON and text parsing.
   - Serves static files from an uploads directory.
   - Mounts various API routes for authentication, tasks, projects, users, attachments, reports, imports, notifications, and admin functionalities.
   - Includes a health check endpoint and an error handler middleware.

4. **Controllers**:
   - **Report Controller (`taskflow/backend/src/controllers/reportController.js`)**:
     - Handles the generation of PDF reports based on project data.
   - **Admin Controller (`taskflow/backend/src/controllers/adminController.js`)**:
     - Manages administrative tasks such as retrieving users, deleting users, and getting a billing overview.
   - **Import Controller (`taskflow/backend/src/controllers/importController.js`)**:
     - Handles importing tasks from XML and CSV formats.
   - **Notification Controller (`taskflow/backend/src/controllers/notificationController.js`)**:
     - Manages notifications, including listing, marking as read, and managing preferences.
   - **Attachment Controller (`taskflow/backend/src/controllers/attachmentController.js`)**:
     - Manages task attachments, including listing, uploading, downloading, and removing.
   - **Project Controller (`taskflow/backend/src/controllers/projectController.js`)**:
     - Manages projects, including listing, retrieving, creating, updating, and deleting.
   - **User Controller (`taskflow/backend/src/controllers/userController.js`)**:
     - Manages user profiles, including retrieving and updating.
   - **Auth Controller (`taskflow/backend/src/controllers/authController.js`)**:
     - Handles user registration, login, token refresh, password reset, and logout.

5. **Middlewares**:
   - **Authentication Middleware (`taskflow/backend/src/middleware/authenticate.js`)**:
     - Verifies JWT tokens in the authorization header.
   - **Rate Limiter Middleware (`taskflow/backend/src/middleware/rateLimiter.js`)**:
     - Limits the rate of report generation requests to 10 per minute.
   - **Error Handler Middleware (`taskflow/backend/src/middleware/errorHandler.js`)**:
     - Logs errors and sends JSON responses with error details.
   - **Authorization Middleware (`taskflow/backend/src/middleware/authorize.js`)**:
     - Checks user roles and permissions.
   - **File Upload Middleware (`taskflow/backend/src/middleware/upload.js`)**:
     - Configures multer for handling file uploads.

6. **Models**:
   - **Project Model (`taskflow/backend/src/models/projectModel.js`)**:
     - Provides database operations for the 'projects' table.
   - **Organization Model (`taskflow/backend/src/models/orgModel.js`)**:
     - Manages organization and member data.
   - **Task Model (`taskflow/backend/src/models/taskModel.js`)**:
     - Provides database operations for the 'tasks' table.
   - **User Model (`taskflow/backend/src/models/userModel.js`)**:
     - Manages user data, including authentication and password management.

7. **Services**:
   - **Email Service (`taskflow/backend/src/services/emailService.js`)**:
     - Sends invitation and password reset emails using SendGrid.
   - **Notification Service (`taskflow/backend/src/services/notificationService.js`)**:
     - Manages user notifications and preferences.
   - **Report Service (`taskflow/backend/src/services/reportService.js`)**:
     - Generates HTML and PDF reports from task data.
   - **Stripe Service (`taskflow/backend/src/services/stripeService.js`)**:
     - Interacts with the Stripe API for customer management and billing.

8. **Utils**:
   - **Logger (`taskflow/backend/src/utils/logger.js`)**:
     - Provides a simple logging utility for info, warn, and error messages.
   - **Token Utils (`taskflow/backend/src/utils/tokenUtils.js`)**:
     - Contains functions for generating and verifying JWT tokens.
   - **Merge Objects (`taskflow/backend/src/utils/mergeObjects.js`)**:
     - Provides functions for deep merging of objects.
   - **Validators (`taskflow/backend/src/utils/validators.js`)**:
     - Contains functions for validating and sanitizing strings.

### Frontend

1. **Main Application (`taskflow/frontend/src/App.jsx`)**:
   - Sets up routing for various pages, including public and private routes.
   - Private routes require user authentication, redirecting unauthenticated users to the login page.

2. **API Client (`taskflow/frontend/src/api/client.js`)**:
   - Sets up an Axios client for making HTTP requests to the backend API.
   - Includes interceptors for adding authentication tokens and handling unauthorized responses.

3. **Components**:
   - **User Table (`taskflow/frontend/src/components/Admin/UserTable.jsx`)**:
     - Displays a table of users fetched from the API.
   - **Navbar (`taskflow/frontend/src/components/Layout/Navbar.jsx`)**:
     - Displays a navigation bar with links to the dashboard and settings, and a logout button.
   - **Page Wrapper (`taskflow/frontend/src/components/Layout/PageWrapper.jsx`)**:
     - Provides a consistent layout for pages, including a sidebar and navbar.
   - **Project Card (`taskflow/frontend/src/components/Projects/ProjectCard.jsx`)**:
     - Displays a card for a project with its name, description, and archived status.
   - **Project Settings (`taskflow/frontend/src/components/Projects/ProjectSettings.jsx`)**:
     - Allows users to update project settings.
   - **Task Card (`taskflow/frontend/src/components/Tasks/TaskCard.jsx`)**:
     - Displays a card for a task with its title, status, priority, due date, and assignee.
   - **Comment List (`taskflow/frontend/src/components/Tasks/CommentList.jsx`)**:
     - Displays a list of comments for a task and allows users to add new comments.
   - **Task Detail (`taskflow/frontend/src/components/Tasks/TaskDetail.jsx`)**:
     - Displays detailed information about a specific task.
   - **Task Form (`taskflow/frontend/src/components/Tasks/TaskForm.jsx`)**:
     - Provides a form for creating or editing a task.
   - **UI Components**:
     - **Badge (`taskflow/frontend/src/components/UI/Badge.jsx`)**:
     - **Button (`taskflow/frontend/src/components/UI/Button.jsx`)**:
     - **Modal (`taskflow/frontend/src/components/UI/Modal.jsx`)**:
     - **Spinner (`taskflow/frontend/src/components/UI/Spinner.jsx`)**:

4. **Hooks**:
   - **useAuth (`taskflow/frontend/src/hooks/useAuth.js`)**:
     - Manages authentication state.
   - **useProjects (`taskflow/frontend/src/hooks/useProjects.js`)**:
     - Manages the state and lifecycle of projects data.
   - **useTasks (`taskflow/frontend/src/hooks/useTasks.js`)**:
     - Manages the state and lifecycle of tasks data.

5. **Context**:
   - **AuthContext (`taskflow/frontend/src/context/AuthContext.jsx`)**:
     - Provides authentication state and functions to its children.

6. **Pages**:
   - **Admin Page (`taskflow/frontend/src/pages/AdminPage.jsx`)**:
     - Displays a table of users.
   - **Dashboard Page (`taskflow/frontend/src/pages/DashboardPage.jsx`)**:
     - Displays a dashboard with statistics about open tasks, overdue tasks, and projects.
   - **Login Page (`taskflow/frontend/src/pages/LoginPage.jsx`)**:
     - Handles user login.
   - **Landing Page (`taskflow/frontend/src/pages/LandingPage.jsx`)**:
     - Displays the landing page with navigation to login and registration pages.
   - **Not Found Page (`taskflow/frontend/src/pages/NotFoundPage.jsx`)**:
     - Displays a 404 error page.
   - **Project Detail Page (`taskflow/frontend/src/pages/ProjectDetailPage.jsx`)**:
     - Displays detailed information about a project.
   - **Task Detail Page (`taskflow/frontend/src/pages/TaskDetailPage.jsx`)**:
     - Displays detailed information about a task.
   - **Register Page (`taskflow/frontend/src/pages/RegisterPage.jsx`)**:
     - Handles user registration.
   - **Settings Page (`taskflow/frontend/src/pages/SettingsPage.jsx`)**:
     - Allows users to update their profile.
   - **Projects Page (`taskflow/frontend/src/pages/ProjectsPage.jsx`)**:
     - Displays a list of projects and allows creating new projects.
   - **Tasks Page (`taskflow/frontend/src/pages/TasksPage.jsx`)**:
     - Displays a list of tasks and allows creating new tasks.

7. **Utils**:
   - **Analytics (`taskflow/frontend/src/utils/analytics.js`)**:
     - Tracks events and identifies users in an analytics system using Mixpanel and Google Analytics.
   - **Auth Utils (`taskflow/frontend/src/utils/authUtils.js`)**:
     - Manages authentication sessions in local storage.
   - **Formatters (`taskflow/frontend/src/utils/formatters.js`)**:
     - Provides functions for formatting dates, priorities, and statuses.

8. **Configuration**:
   - **Vite Configuration (`taskflow/frontend/vite.config.js`)**:
     - Configures the Vite development server to run on port 3000 and proxy API and uploads requests to the backend server.

## Typical Usage Scenario

1. **User Registration and Login**:
   - A new user visits the landing page and clicks on the "Register" link.
   - The user fills out the registration form with their full name, email, and password.
   - Upon successful registration, the user is redirected to the login page.
   - The user logs in using their email and password, and the application verifies the credentials with the backend.

2. **Project Management**:
   - Once logged in, the user is redirected to the dashboard page.
   - The dashboard displays statistics about open tasks, overdue tasks, and projects.
   - The user can navigate to the projects page to view a list of projects.
   - The user can create a new project by clicking the "Create Project" button, which opens a modal form.
   - After creating a project, the user can navigate to the project detail page to view and manage tasks.

3. **Task Management**:
   - On the project detail page, the user can see a list of tasks and add new tasks by clicking the "Create Task" button.
   - The user can update task details, add comments, and mark tasks as completed.
   - The user can also view detailed information about a specific task by clicking on the task card.

4. **Admin Functions**:
   - Admin users can navigate to the admin page to manage users and view billing overviews.
   - The admin page displays a table of users, and the admin can delete users or manage their roles.

5. **Reporting**:
   - Users can generate PDF reports of projects by navigating to the report page.
   - The report generation is rate-limited to prevent abuse.

## Where to Look Next

- **Backend**:
  - **Database Configuration**: `taskflow/backend/config/db.js`
  - **Server Setup**: `taskflow/backend/server.js`
  - **Express Application**: `taskflow/backend/src/app.js`
  - **Controllers**: `taskflow/backend/src/controllers/*.js`
  - **Middlewares**: `taskflow/backend/src/middleware/*.js`
  - **Models**: `taskflow/backend/src/models/*.js`
  - **Services**: `taskflow/backend/src/services/*.js`
  - **Utils**: `taskflow/backend/src/utils/*.js`

- **Frontend**:
  - **Main Application**: `taskflow/frontend/src/App.jsx`
  - **API Client**: `taskflow/frontend/src/api/client.js`
  - **Components**: `taskflow/frontend/src/components/*.jsx`
  - **Hooks**: `taskflow/frontend/src/hooks/*.js`
  - **Context**: `taskflow/frontend/src/context/*.jsx`
  - **Pages**: `taskflow/frontend/src/pages/*.jsx`
  - **Utils**: `taskflow/frontend/src/utils/*.js`
  - **Configuration**: `taskflow/frontend/vite.config.js`

For more detailed information on specific components and functionalities, refer to the corresponding sections in the documentation.