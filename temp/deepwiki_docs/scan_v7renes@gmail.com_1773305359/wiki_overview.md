# Overview

## What is TaskFlow?

TaskFlow is a comprehensive project management tool designed to streamline task and project management for teams and organizations. It provides a robust set of features to manage projects, tasks, user profiles, and notifications, all while ensuring secure and efficient operations.

## Main Components

### Backend
- **Server Setup (`server.js`)**: Sets up and starts a Node.js server using Express. It listens on a specified port (default 3001) and configures middleware and routes.
- **Database Connection (`db.js`)**: Manages the PostgreSQL database connection pool and provides a query function for executing SQL queries.
- **Controllers**: Handle specific business logic and HTTP requests.
  - **Project Controller (`projectController.js`)**: Manages CRUD operations for projects.
  - **Task Controller (`taskController.js`)**: Manages CRUD operations for tasks, including comments.
  - **User Controller (`userController.js`)**: Handles user profile retrieval and updates.
  - **Auth Controller (`authController.js`)**: Manages user authentication, registration, and password reset.
  - **Report Controller (`reportController.js`)**: Generates PDF reports for projects.
  - **Import Controller (`importController.js`)**: Imports tasks from XML and CSV files.
  - **Admin Controller (`adminController.js`)**: Provides administrative functionalities like managing users and billing.
  - **Notification Controller (`notificationController.js`)**: Manages user notifications and preferences.
  - **Attachment Controller (`attachmentController.js`)**: Manages task attachments, including uploading, downloading, and deleting.
- **Models**: Define database schemas and operations.
  - **Project Model (`projectModel.js`)**: Manages project data.
  - **User Model (`userModel.js`)**: Manages user data.
  - **Task Model (`taskModel.js`)**: Manages task data.
  - **Org Model (`orgModel.js`)**: Manages organization and member data.
- **Services**: Provide utility functions for specific tasks.
  - **Email Service (`emailService.js`)**: Sends emails using SendGrid.
  - **Notification Service (`notificationService.js`)**: Manages user notifications.
  - **Report Service (`reportService.js`)**: Generates HTML and PDF reports.
  - **Stripe Service (`stripeService.js`)**: Interacts with the Stripe API for billing.
- **Middlewares**: Handle cross-cutting concerns like authentication, rate limiting, and error handling.
  - **Authenticate (`authenticate.js`)**: Verifies JWT tokens and attaches user information to the request.
  - **Authorize (`authorize.js`)**: Checks user roles and authorizes access.
  - **Rate Limiter (`rateLimiter.js`)**: Limits the rate of report generation requests.
  - **Error Handler (`errorHandler.js`)**: Logs errors and sends JSON responses.
  - **Upload (`upload.js`)**: Configures file upload using Multer.
- **Utils**: Provide utility functions for common tasks.
  - **Logger (`logger.js`)**: Formats and logs messages.
  - **Token Utils (`tokenUtils.js`)**: Generates and verifies JWT tokens.
  - **Validators (`validators.js`)**: Validates and sanitizes strings.
  - **Merge Objects (`mergeObjects.js`)**: Merges objects deeply.
  - **Formatters (`formatters.js`)**: Formats dates and labels.
  - **Auth Utils (`authUtils.js`)**: Manages authentication sessions in local storage.

### Frontend
- **Main Application (`App.jsx`)**: Sets up routing for various pages, including public and private routes.
- **API Client (`client.js`)**: Configures an Axios client for making HTTP requests to the backend API.
- **Components**: Reusable UI elements.
  - **Navbar (`Navbar.jsx`)**: Displays a navigation bar with links and a logout button.
  - **Sidebar (`Sidebar.jsx`)**: Displays navigation links and user information.
  - **Page Wrapper (`PageWrapper.jsx`)**: Combines a sidebar, navbar, and main content area.
  - **Project Card (`ProjectCard.jsx`)**: Displays a card for a project.
  - **Task Card (`TaskCard.jsx`)**: Displays a card for a task.
  - **Task Form (`TaskForm.jsx`)**: Form for creating or editing tasks.
  - **Task Detail (`TaskDetail.jsx`)**: Displays detailed information about a task.
  - **Comment List (`CommentList.jsx`)**: Displays a list of comments for a task.
  - **Button (`Button.jsx`)**: Reusable button component.
  - **Spinner (`Spinner.jsx`)**: Displays a loading spinner.
  - **Badge (`Badge.jsx`)**: Displays a styled badge.
  - **Modal (`Modal.jsx`)**: Displays a modal dialog.
- **Pages**: Top-level components for different routes.
  - **Dashboard Page (`DashboardPage.jsx`)**: Displays a dashboard with project and task statistics.
  - **Login Page (`LoginPage.jsx`)**: Handles user login.
  - **Register Page (`RegisterPage.jsx`)**: Handles user registration.
  - **Admin Page (`AdminPage.jsx`)**: Displays administrative functionalities.
  - **Project Detail Page (`ProjectDetailPage.jsx`)**: Displays detailed information about a project.
  - **Projects Page (`ProjectsPage.jsx`)**: Displays a list of projects.
  - **Settings Page (`SettingsPage.jsx`)**: Allows users to update their profile.
  - **Task Detail Page (`TaskDetailPage.jsx`)**: Displays detailed information about a task.
  - **Tasks Page (`TasksPage.jsx`)**: Displays a list of tasks.
  - **Landing Page (`LandingPage.jsx`)**: Main landing page with navigation and features.
  - **Not Found Page (`NotFoundPage.jsx`)**: Displays a 404 error message.
- **Hooks**: Custom hooks for state management and API interactions.
  - **useAuth (`useAuth.js`)**: Manages authentication state.
  - **useProjects (`useProjects.js`)**: Manages project state and API interactions.
  - **useTasks (`useTasks.js`)**: Manages task state and API interactions.
- **Context**: Provides global state management.
  - **Auth Context (`AuthContext.jsx`)**: Manages authentication state and functions.
- **Utils**: Utility functions for frontend tasks.
  - **Analytics (`analytics.js`)**: Tracks user events and identifies users in Mixpanel and Google Analytics.
  - **Auth Utils (`authUtils.js`)**: Manages authentication sessions in local storage.

## Typical Usage Scenario

1. **User Registration and Login**:
   - A new user visits the landing page and clicks on the "Register" link.
   - The user fills out the registration form and submits it.
   - The `RegisterPage` component sends a POST request to the backend's `authController` to create a new user and organization.
   - Upon successful registration, the user is redirected to the login page.
   - The user logs in using the `LoginPage` component, which sends a POST request to the backend's `authController` to authenticate the user and obtain access and refresh tokens.

2. **Project Management**:
   - After logging in, the user is redirected to the dashboard.
   - The `DashboardPage` component fetches project and task statistics from the backend using the `useProjects` hook.
   - The user navigates to the projects page to view a list of projects.
   - The `ProjectsPage` component fetches project data from the backend using the `useProjects` hook and displays a list of project cards.
   - The user clicks on a project card to view detailed information about the project.
   - The `ProjectDetailPage` component fetches project data from the backend and displays it, including a list of tasks and project settings.

3. **Task Management**:
   - The user navigates to the tasks page to view a list of tasks.
   - The `TasksPage` component fetches task data from the backend using the `useTasks` hook and displays a list of task cards.
   - The user clicks on a task card to view detailed information about the task.
   - The `TaskDetailPage` component fetches task data from the backend and displays it, including comments and a form to add new comments.
   - The user can create new tasks or update existing tasks using the `TaskForm` component.

4. **Admin Functions**:
   - An admin user navigates to the admin page to manage users and billing.
   - The `AdminPage` component fetches user data from the backend using the `useAuth` hook and displays a table of users.
   - The admin can delete users or view a billing overview using the `adminController` endpoints.

## Where to Look Next

- **Backend**:
  - **Controllers**: For detailed information on how specific business logic is handled, see the controller files like `projectController.js`, `taskController.js`, and `authController.js`.
  - **Models**: For database schema and operations, see the model files like `projectModel.js`, `userModel.js`, and `taskModel.js`.
  - **Services**: For utility functions and external API interactions, see the service files like `emailService.js`, `notificationService.js`, and `stripeService.js`.
  - **Middlewares**: For cross-cutting concerns, see the middleware files like `authenticate.js`, `authorize.js`, and `errorHandler.js`.
  - **Utils**: For common utility functions, see the utils files like `logger.js`, `tokenUtils.js`, and `validators.js`.

- **Frontend**:
  - **Components**: For reusable UI elements, see the component files like `Navbar.jsx`, `Sidebar.jsx`, and `TaskCard.jsx`.
  - **Pages**: For top-level components for different routes, see the page files like `DashboardPage.jsx`, `LoginPage.jsx`, and `ProjectsPage.jsx`.
  - **Hooks**: For custom hooks for state management and API interactions, see the hook files like `useAuth.js`, `useProjects.js`, and `useTasks.js`.
  - **Context**: For global state management, see the context file `AuthContext.jsx`.
  - **Utils**: For utility functions, see the utils files like `analytics.js` and `authUtils.js`.

For more detailed documentation on specific components and functionalities, refer to the respective sections in the documentation.