# Overview

## What is TaskFlow?

TaskFlow is a project management tool designed to help organizations and teams efficiently manage their tasks, projects, and resources. It provides a comprehensive set of features for task tracking, project collaboration, user management, and reporting. TaskFlow is built using a modern tech stack, including Node.js, Express, PostgreSQL, and React.

## Main Components

### Backend
The backend of TaskFlow is built using Node.js and Express. It provides a RESTful API for various functionalities and is responsible for handling HTTP requests, interacting with the database, and managing user authentication and authorization.

- **Database Configuration (`taskflow/backend/config/db.js`)**: Sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries.
- **Server Setup (`taskflow/backend/server.js`)**: Configures and starts the Node.js server, listening on a specified port.
- **Express Application (`taskflow/backend/src/app.js`)**: Sets up the Express application, including middleware for JSON and text parsing, static file serving, and mounting various API routes.
- **Controllers**: Handle specific business logic and HTTP requests.
  - **Authentication (`taskflow/backend/src/controllers/authController.js`)**: Manages user registration, login, token refresh, password reset, and logout.
  - **Projects (`taskflow/backend/src/controllers/projectController.js`)**: Manages CRUD operations for projects.
  - **Tasks (`taskflow/backend/src/controllers/taskController.js`)**: Manages CRUD operations for tasks and task comments.
  - **Attachments (`taskflow/backend/src/controllers/attachmentController.js`)**: Manages file attachments for tasks.
  - **Reports (`taskflow/backend/src/controllers/reportController.js`)**: Generates PDF reports for projects.
  - **Imports (`taskflow/backend/src/controllers/importController.js`)**: Imports tasks from XML and CSV files.
  - **Admin (`taskflow/backend/src/controllers/adminController.js`)**: Manages administrative tasks like user management and billing.
  - **Notifications (`taskflow/backend/src/controllers/notificationController.js`)**: Manages user notifications and preferences.
  - **Users (`taskflow/backend/src/controllers/userController.js`)**: Manages user profiles.
- **Models**: Define the database schema and provide methods for interacting with the database.
  - **Organizations (`taskflow/backend/src/models/orgModel.js`)**: Manages organization data.
  - **Projects (`taskflow/backend/src/models/projectModel.js`)**: Manages project data.
  - **Tasks (`taskflow/backend/src/models/taskModel.js`)**: Manages task data.
  - **Users (`taskflow/backend/src/models/userModel.js`)**: Manages user data.
- **Middleware**: Handles cross-cutting concerns like authentication, authorization, error handling, and file uploads.
  - **Authentication (`taskflow/backend/src/middleware/authenticate.js`)**: Verifies JWT tokens.
  - **Authorization (`taskflow/backend/src/middleware/authorize.js`)**: Checks user roles.
  - **Error Handling (`taskflow/backend/src/middleware/errorHandler.js`)**: Logs and responds to errors.
  - **File Uploads (`taskflow/backend/src/middleware/upload.js`)**: Configures file upload handling.
  - **Rate Limiting (`taskflow/backend/src/middleware/rateLimiter.js`)**: Limits the rate of report generation requests.
- **Services**: Provide utility functions for common tasks.
  - **Email (`taskflow/backend/src/services/emailService.js`)**: Sends emails using SendGrid.
  - **Notifications (`taskflow/backend/src/services/notificationService.js`)**: Manages user notifications.
  - **Reports (`taskflow/backend/src/services/reportService.js`)**: Generates HTML and PDF reports.
  - **Stripe (`taskflow/backend/src/services/stripeService.js`)**: Interacts with the Stripe API for billing.
- **Utilities**: Provides helper functions for various tasks.
  - **Token Management (`taskflow/backend/src/utils/tokenUtils.js`)**: Generates and verifies JWT tokens.
  - **Object Merging (`taskflow/backend/src/utils/mergeObjects.js`)**: Merges objects deeply.
  - **Logging (`taskflow/backend/src/utils/logger.js`)**: Logs application events.
  - **Validators (`taskflow/backend/src/utils/validators.js`)**: Validates and sanitizes strings.

### Frontend
The frontend of TaskFlow is built using React and provides a user-friendly interface for interacting with the backend API.

- **Main Application (`taskflow/frontend/src/App.jsx`)**: Sets up routing for various pages and handles authentication.
- **API Client (`taskflow/frontend/src/api/client.js`)**: Configures an Axios client for making HTTP requests to the backend API.
- **Pages**: React components for different pages in the application.
  - **Landing Page (`taskflow/frontend/src/pages/LandingPage.jsx`)**: The initial landing page for the application.
  - **Login Page (`taskflow/frontend/src/pages/LoginPage.jsx`)**: Handles user login.
  - **Register Page (`taskflow/frontend/src/pages/RegisterPage.jsx`)**: Handles user registration.
  - **Dashboard Page (`taskflow/frontend/src/pages/DashboardPage.jsx`)**: Displays a dashboard with project and task statistics.
  - **Projects Page (`taskflow/frontend/src/pages/ProjectsPage.jsx`)**: Lists projects and allows creating new projects.
  - **Project Detail Page (`taskflow/frontend/src/pages/ProjectDetailPage.jsx`)**: Displays detailed information about a project.
  - **Tasks Page (`taskflow/frontend/src/pages/TasksPage.jsx`)**: Lists tasks and allows creating new tasks.
  - **Task Detail Page (`taskflow/frontend/src/pages/TaskDetailPage.jsx`)**: Displays detailed information about a task.
  - **Settings Page (`taskflow/frontend/src/pages/SettingsPage.jsx`)**: Allows users to update their profile.
  - **Admin Page (`taskflow/frontend/src/pages/AdminPage.jsx`)**: Manages administrative tasks.
  - **Not Found Page (`taskflow/frontend/src/pages/NotFoundPage.jsx`)**: Displays a 404 error page.
- **Components**: Reusable UI components.
  - **Navbar (`taskflow/frontend/src/components/Layout/Navbar.jsx`)**: Navigation bar with user information and links.
  - **Sidebar (`taskflow/frontend/src/components/Layout/Sidebar.jsx`)**: Navigation sidebar based on user role.
  - **Page Wrapper (`taskflow/frontend/src/components/Layout/PageWrapper.jsx`)**: Provides a consistent layout for pages.
  - **Project Card (`taskflow/frontend/src/components/Projects/ProjectCard.jsx`)**: Displays a card for a project.
  - **Task Card (`taskflow/frontend/src/components/Tasks/TaskCard.jsx`)**: Displays a card for a task.
  - **Task Detail (`taskflow/frontend/src/components/Tasks/TaskDetail.jsx`)**: Displays detailed information about a task.
  - **Comment List (`taskflow/frontend/src/components/Tasks/CommentList.jsx`)**: Displays and manages comments for a task.
  - **Task Form (`taskflow/frontend/src/components/Tasks/TaskForm.jsx`)**: Form for creating or editing a task.
  - **User Table (`taskflow/frontend/src/components/Admin/UserTable.jsx`)**: Displays a table of users.
  - **Button (`taskflow/frontend/src/components/UI/Button.jsx`)**: Reusable button component.
  - **Badge (`taskflow/frontend/src/components/UI/Badge.jsx`)**: Reusable badge component.
  - **Spinner (`taskflow/frontend/src/components/UI/Spinner.jsx`)**: Loading spinner component.
  - **Modal (`taskflow/frontend/src/components/UI/Modal.jsx`)**: Modal dialog component.
- **Hooks**: Custom React hooks for state management and side effects.
  - **useAuth (`taskflow/frontend/src/hooks/useAuth.js`)**: Manages authentication state.
  - **useProjects (`taskflow/frontend/src/hooks/useProjects.js`)**: Manages project data.
  - **useTasks (`taskflow/frontend/src/hooks/useTasks.js`)**: Manages task data.
- **Context**: Provides global state management.
  - **AuthContext (`taskflow/frontend/src/context/AuthContext.jsx`)**: Provides authentication context.
- **Utilities**: Helper functions for various tasks.
  - **Analytics (`taskflow/frontend/src/utils/analytics.js`)**: Tracks events and identifies users in analytics services.
  - **AuthUtils (`taskflow/frontend/src/utils/authUtils.js`)**: Manages authentication sessions in local storage.
  - **Formatters (`taskflow/frontend/src/utils/formatters.js`)**: Formats dates and labels.
- **Configuration**: Configuration files for the frontend.
  - **Vite Configuration (`taskflow/frontend/vite.config.js`)**: Configures the Vite development server.
  - **PostCSS Configuration (`taskflow/frontend/postcss.config.js`)**: Configures PostCSS and Tailwind CSS.

## Typical Usage Scenario

1. **User Registration and Login**:
   - A new user visits the landing page and clicks on the "Register" link.
   - The user fills out the registration form with their full name, email, and password.
   - Upon successful registration, the user is redirected to the login page.
   - The user logs in using their email and password, and the application verifies the credentials with the backend.

2. **Project Management**:
   - After logging in, the user is redirected to the dashboard, which displays an overview of their projects and tasks.
   - The user can navigate to the "Projects" page to view a list of all projects.
   - The user can create a new project by clicking the "Create Project" button, which opens a modal form.
   - Once a project is created, the user can navigate to the project detail page to view and manage tasks within the project.

3. **Task Management**:
   - On the project detail page, the user can see a list of tasks associated with the project.
   - The user can create a new task by clicking the "Create Task" button, which opens a modal form.
   - The user can update the status, priority, and due date of a task.
   - The user can add comments to a task and view comments from other team members.

4. **Admin Functions**:
   - Admin users can navigate to the admin page to manage users and billing.
   - The admin can view a list of all users, delete users, and view a billing overview.

5. **Notifications**:
   - Users receive notifications for important events, such as new tasks, comments, and project updates.
   - Users can manage their notification preferences in the settings page.

6. **Reporting**:
   - Users can generate PDF reports for projects by navigating to the project detail page and clicking the "Generate Report" button.
   - The report includes a summary of the project and its tasks, and is sent as a downloadable PDF.

## Where to Look Next

- **Backend**:
  - **Database Configuration**: `taskflow/backend/config/db.js`
  - **Server Setup**: `taskflow/backend/server.js`
  - **Controllers**: `taskflow/backend/src/controllers/*.js`
  - **Models**: `taskflow/backend/src/models/*.js`
  - **Middleware**: `taskflow/backend/src/middleware/*.js`
  - **Services**: `taskflow/backend/src/services/*.js`
  - **Utilities**: `taskflow/backend/src/utils/*.js`

- **Frontend**:
  - **Main Application**: `taskflow/frontend/src/App.jsx`
  - **API Client**: `taskflow/frontend/src/api/client.js`
  - **Pages**: `taskflow/frontend/src/pages/*.jsx`
  - **Components**: `taskflow/frontend/src/components/*.jsx`
  - **Hooks**: `taskflow/frontend/src/hooks/*.js`
  - **Context**: `taskflow/frontend/src/context/*.jsx`
  - **Utilities**: `taskflow/frontend/src/utils/*.js`
  - **Configuration**: `taskflow/frontend/vite.config.js`, `taskflow/frontend/postcss.config.js`

For more detailed information on specific components and functionalities, refer to the corresponding sections in the documentation.