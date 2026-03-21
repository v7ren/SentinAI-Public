# Overview

## What is TaskFlow?

TaskFlow is a comprehensive project management tool designed to streamline the process of managing tasks, projects, and user interactions within an organization. It provides a robust backend and a user-friendly frontend to facilitate collaboration, task tracking, and reporting. TaskFlow is built using modern web technologies, including Node.js, Express, PostgreSQL, and React.

## Main Components

### Backend
- **Database Configuration (`taskflow/backend/config/db.js`)**: Sets up a PostgreSQL database connection pool and provides a query function for executing SQL queries.
- **Server Setup (`taskflow/backend/server.js`)**: Initializes and starts a Node.js server using an Express application. It listens on a specified port and logs a message upon successful startup.
- **Express Application (`taskflow/backend/src/app.js`)**: Configures middleware for JSON and text parsing, serves static files, and mounts various route handlers for different API endpoints.
- **Controllers**: Handle specific business logic and HTTP requests.
  - **Report Controller (`taskflow/backend/src/controllers/reportController.js`)**: Manages the generation of PDF reports based on project data.
  - **Import Controller (`taskflow/backend/src/controllers/importController.js`)**: Handles the import of tasks from XML and CSV formats.
  - **Admin Controller (`taskflow/backend/src/controllers/adminController.js`)**: Manages administrative tasks such as retrieving all users, deleting a user, and getting a billing overview.
  - **Notification Controller (`taskflow/backend/src/controllers/notificationController.js`)**: Manages user notifications, including listing, marking as read, and managing preferences.
  - **Attachment Controller (`taskflow/backend/src/controllers/attachmentController.js`)**: Manages task attachments, including listing, uploading, downloading, and removing attachments.
  - **Project Controller (`taskflow/backend/src/controllers/projectController.js`)**: Manages projects, including listing, retrieving, creating, updating, and deleting projects.
  - **User Controller (`taskflow/backend/src/controllers/userController.js`)**: Manages user profiles, including retrieving and updating profile information.
  - **Task Controller (`taskflow/backend/src/controllers/taskController.js`)**: Manages tasks, including listing, retrieving, creating, updating, and deleting tasks.
  - **Auth Controller (`taskflow/backend/src/controllers/authController.js`)**: Manages user authentication, including registration, login, token refresh, password reset, and logout.
- **Middleware**: Handles cross-cutting concerns such as authentication, authorization, error handling, and rate limiting.
  - **Authenticate (`taskflow/backend/src/middleware/authenticate.js`)**: Verifies JWT tokens in the authorization header.
  - **Authorize (`taskflow/backend/src/middleware/authorize.js`)**: Checks user roles and permissions.
  - **Error Handler (`taskflow/backend/src/middleware/errorHandler.js`)**: Logs errors and sends JSON responses.
  - **Upload (`taskflow/backend/src/middleware/upload.js`)**: Configures file upload using Multer.
  - **Rate Limiter (`taskflow/backend/src/middleware/rateLimiter.js`)**: Limits the rate of report generation requests.
- **Models**: Define the schema and operations for database tables.
  - **Task Model (`taskflow/backend/src/models/taskModel.js`)**: Manages tasks in the database.
  - **Project Model (`taskflow/backend/src/models/projectModel.js`)**: Manages projects in the database.
  - **Org Model (`taskflow/backend/src/models/orgModel.js`)**: Manages organizations and their members.
  - **User Model (`taskflow/backend/src/models/userModel.js`)**: Manages users in the database.
- **Services**: Provide utility functions for specific tasks.
  - **Email Service (`taskflow/backend/src/services/emailService.js`)**: Sends emails using SendGrid.
  - **Notification Service (`taskflow/backend/src/services/notificationService.js`)**: Manages user notifications and preferences.
  - **Report Service (`taskflow/backend/src/services/reportService.js`)**: Generates HTML and PDF reports.
  - **Stripe Service (`taskflow/backend/src/services/stripeService.js`)**: Interacts with the Stripe API for billing and subscriptions.
- **Utils**: Contains utility functions and constants.
  - **Logger (`taskflow/backend/src/utils/logger.js`)**: Formats and logs messages.
  - **Token Utils (`taskflow/backend/src/utils/tokenUtils.js`)**: Manages JWT token generation and verification.
  - **Validators (`taskflow/backend/src/utils/validators.js`)**: Validates and sanitizes strings.
  - **Merge Objects (`taskflow/backend/src/utils/mergeObjects.js`)**: Merges objects deeply.
  - **Formatters (`taskflow/backend/src/utils/formatters.js`)**: Formats dates and labels.

### Frontend
- **Main Application (`taskflow/frontend/src/main.jsx`)**: Sets up the React application, routing, and authentication context.
- **API Client (`taskflow/frontend/src/api/client.js`)**: Configures an Axios client for making HTTP requests to the backend API.
- **API Modules**: Provide functions for interacting with specific API endpoints.
  - **Admin API (`taskflow/frontend/src/api/admin.js`)**: Manages admin-related API calls.
  - **Auth API (`taskflow/frontend/src/api/auth.js`)**: Manages user authentication API calls.
  - **Projects API (`taskflow/frontend/src/api/projects.js`)**: Manages project-related API calls.
  - **Tasks API (`taskflow/frontend/src/api/tasks.js`)**: Manages task-related API calls.
- **Components**: Reusable UI elements.
  - **Layout Components**: Provide a consistent layout for the application.
    - **Page Wrapper (`taskflow/frontend/src/components/Layout/PageWrapper.jsx`)**: Combines a sidebar, navbar, and main content area.
    - **Navbar (`taskflow/frontend/src/components/Layout/Navbar.jsx`)**: Displays navigation links and user information.
    - **Sidebar (`taskflow/frontend/src/components/Layout/Sidebar.jsx`)**: Displays navigation links based on user role.
  - **Project Components**: Display and manage project information.
    - **Project Card (`taskflow/frontend/src/components/Projects/ProjectCard.jsx`)**: Displays a card for a project.
    - **Project Settings (`taskflow/frontend/src/components/Projects/ProjectSettings.jsx`)**: Allows users to update project settings.
    - **Project Detail Page (`taskflow/frontend/src/components/Projects/ProjectDetailPage.jsx`)**: Displays detailed information about a project.
  - **Task Components**: Display and manage task information.
    - **Task Card (`taskflow/frontend/src/components/Tasks/TaskCard.jsx`)**: Displays a card for a task.
    - **Task Detail Page (`taskflow/frontend/src/components/Tasks/TaskDetailPage.jsx`)**: Displays detailed information about a task.
    - **Task Form (`taskflow/frontend/src/components/Tasks/TaskForm.jsx`)**: Allows users to create or edit a task.
    - **Comment List (`taskflow/frontend/src/components/Tasks/CommentList.jsx`)**: Displays and manages comments for a task.
  - **UI Components**: Reusable UI elements.
    - **Button (`taskflow/frontend/src/components/UI/Button.jsx`)**: A styled button component.
    - **Badge (`taskflow/frontend/src/components/UI/Badge.jsx`)**: A styled badge component.
    - **Modal (`taskflow/frontend/src/components/UI/Modal.jsx`)**: A modal dialog component.
    - **Spinner (`taskflow/frontend/src/components/UI/Spinner.jsx`)**: A loading spinner component.
- **Pages**: Top-level components that represent different pages in the application.
  - **Admin Page (`taskflow/frontend/src/pages/AdminPage.jsx`)**: Displays a table of users and allows admin actions.
  - **Dashboard Page (`taskflow/frontend/src/pages/DashboardPage.jsx`)**: Displays a dashboard with statistics and recent tasks.
  - **Login Page (`taskflow/frontend/src/pages/LoginPage.jsx`)**: Handles user login.
  - **Landing Page (`taskflow/frontend/src/pages/LandingPage.jsx`)**: Provides an overview and links to login and registration.
  - **Not Found Page (`taskflow/frontend/src/pages/NotFoundPage.jsx`)**: Displays a 404 error page.
  - **Projects Page (`taskflow/frontend/src/pages/ProjectsPage.jsx`)**: Displays a list of projects and allows creating new projects.
  - **Project Detail Page (`taskflow/frontend/src/pages/ProjectDetailPage.jsx`)**: Displays detailed information about a project.
  - **Register Page (`taskflow/frontend/src/pages/RegisterPage.jsx`)**: Handles user registration.
  - **Settings Page (`taskflow/frontend/src/pages/SettingsPage.jsx`)**: Allows users to update their profile information.
  - **Tasks Page (`taskflow/frontend/src/pages/TasksPage.jsx`)**: Displays a list of tasks and allows creating new tasks.
- **Hooks**: Custom React hooks for state and side-effect management.
  - **useAuth (`taskflow/frontend/src/hooks/useAuth.js`)**: Manages authentication state.
  - **useProjects (`taskflow/frontend/src/hooks/useProjects.js`)**: Manages project data.
  - **useTasks (`taskflow/frontend/src/hooks/useTasks.js`)**: Manages task data.
- **Utils**: Contains utility functions and constants.
  - **Analytics (`taskflow/frontend/src/utils/analytics.js`)**: Tracks user events and identifies users in Mixpanel and Google Analytics.
  - **Auth Utils (`taskflow/frontend/src/utils/authUtils.js`)**: Manages authentication sessions in local storage.
  - **Formatters (`taskflow/frontend/src/utils/formatters.js`)**: Formats dates and labels.

## Typical Usage Scenario

1. **User Registration and Login**:
   - A new user visits the landing page and clicks on the "Register" link.
   - The user fills out the registration form with their full name, email, and password.
   - Upon successful registration, the user is redirected to the login page.
   - The user logs in using their email and password, and the application verifies the credentials with the backend.
   - Upon successful authentication, the user is redirected to the dashboard.

2. **Project Management**:
   - The user navigates to the "Projects" page, which lists all their projects.
   - The user can create a new project by clicking the "Create Project" button, which opens a modal form.
   - The user fills out the project details and submits the form, which sends a POST request to the backend to create the project.
   - The user can view detailed information about a project by clicking on the project card, which navigates to the project detail page.
   - On the project detail page, the user can manage tasks, add comments, and update project settings.

3. **Task Management**:
   - The user navigates to the "Tasks" page, which lists all their tasks.
   - The user can filter tasks by project and search term.
   - The user can create a new task by clicking the "Create Task" button, which opens a modal form.
   - The user fills out the task details and submits the form, which sends a POST request to the backend to create the task.
   - The user can view detailed information about a task by clicking on the task card, which navigates to the task detail page.
   - On the task detail page, the user can manage comments and update task details.

4. **Admin Functions**:
   - An admin user navigates to the "Admin" page, which displays a table of all users.
   - The admin can delete a user by clicking the "Delete" button next to the user's entry.
   - The admin can view a billing overview by clicking the "Billing" link, which fetches and displays billing information.

5. **Notifications and Preferences**:
   - The user can manage their notification preferences by navigating to the "Settings" page.
   - The user can update their notification preferences and save the changes, which sends a PATCH request to the backend to update the user's profile.

## Where to Look Next

- **Backend**:
  - **Database Configuration**: For details on how the database is set up and queried, see the `taskflow/backend/config/db.js` file.
  - **Controllers**: For specific business logic and HTTP request handling, explore the `taskflow/backend/src/controllers` directory.
  - **Middleware**: For cross-cutting concerns like authentication and error handling, see the `taskflow/backend/src/middleware` directory.
  - **Models**: For database schema and operations, refer to the `taskflow/backend/src/models` directory.
  - **Services**: For utility functions and external API interactions, check the `taskflow/backend/src/services` directory.
  - **Utils**: For general utility functions, see the `taskflow/backend/src/utils` directory.

- **Frontend**:
  - **Main Application**: For the entry point and routing configuration, see the `taskflow/frontend/src/main.jsx` file.
  - **API Client**: For making HTTP requests to the backend, refer to the `taskflow/frontend/src/api/client.js` file.
  - **API Modules**: For specific API interactions, explore the `taskflow/frontend/src/api` directory.
  - **Components**: For reusable UI elements, see the `taskflow/frontend/src/components` directory.
  - **Pages**: For top-level components representing different pages, refer to the `taskflow/frontend/src/pages` directory.
  - **Hooks**: For custom React hooks, check the `taskflow/frontend/src/hooks` directory.
  - **Utils**: For general utility functions, see the `taskflow/frontend/src/utils` directory.

For more detailed documentation on specific components and functionalities, refer to the corresponding sections in the documentation.