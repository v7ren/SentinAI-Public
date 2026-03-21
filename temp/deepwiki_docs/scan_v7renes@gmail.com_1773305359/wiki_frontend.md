# Frontend

This section provides an overview of the frontend architecture of the TaskFlow application, including React components, routing, and state management.

## React Components

### Main Application Component
- **File**: `taskflow\frontend\src\App.jsx`
- **Description**: The main entry point of the application, setting up routing for various pages. It includes public and private routes, where private routes require user authentication. Unauthenticated users are redirected to the login page.
- **Key Components**:
  - **Public Routes**: Landing, Login, Registration
  - **Private Routes**: Dashboard, Projects, Tasks, Settings, Admin, Task Detail, Project Detail

### Layout Components
- **Navbar**
  - **File**: `taskflow\frontend\src\components\Layout\Navbar.jsx`
  - **Description**: A header component displaying a navigation bar with links to the dashboard and settings pages, and a logout button. It uses the `useAuth` hook to manage authentication state.
- **Sidebar**
  - **File**: `taskflow\frontend\src\components\Layout\Sidebar.jsx`
  - **Description**: A sidebar component displaying navigation links and user information. It uses the `useAuth` hook to determine if the user is an admin and conditionally adds an admin link.
- **PageWrapper**
  - **File**: `taskflow\frontend\src\components\Layout\PageWrapper.jsx`
  - **Description**: A layout container for other components, including a Sidebar, Navbar, and main content area. It accepts children and title as props.

### Project and Task Components
- **ProjectCard**
  - **File**: `taskflow\frontend\src\components\Projects\ProjectCard.jsx`
  - **Description**: A card component for displaying a project, including a link to the project's detail page, the project's name, description, and archived status.
- **ProjectSettings**
  - **File**: `taskflow\frontend\src\components\Projects\ProjectSettings.jsx`
  - **Description**: A form component for updating a project's settings, including name, description, and archived status. It uses the `useProjects` hook to handle project updates.
- **TaskCard**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskCard.jsx`
  - **Description**: A card component for displaying a task, including a link to the task's detail page, the task's title, status, priority, due date, and assignee.
- **TaskDetail**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskDetail.jsx`
  - **Description**: A component for displaying detailed information about a task, including status, priority, due date, title, and description. It fetches the task data from an API endpoint and handles loading, error, and not found states. It also includes a `CommentList` component to display comments related to the task.
- **TaskForm**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskForm.jsx`
  - **Description**: A form component for creating or editing a task, including fields for title, description, priority, status, and due date. It handles form submission and provides a cancel button to close the form.
- **CommentList**
  - **File**: `taskflow\frontend\src\components\Tasks\CommentList.jsx`
  - **Description**: A component for displaying a list of comments for a given task and allowing users to add new comments. It fetches comments from an API endpoint and updates the list when new comments are posted.

### UI Components
- **Button**
  - **File**: `taskflow\frontend\src\components\UI\Button.jsx`
  - **Description**: A reusable button component that accepts props for customizing the button's appearance and behavior, such as variant, size, and additional class names.
- **Spinner**
  - **File**: `taskflow\frontend\src\components\UI\Spinner.jsx`
  - **Description**: A component that renders a spinning circle to indicate loading states. It accepts a `className` prop to allow for additional styling.
- **Badge**
  - **File**: `taskflow\frontend\src\components\UI\Badge.jsx`
  - **Description**: A component for displaying a badge with different styles based on the variant prop. It supports variants for default, success, warning, danger, and info, each with its own background and text color.
- **Modal**
  - **File**: `taskflow\frontend\src\components\UI\Modal.jsx`
  - **Description**: A component for displaying a modal dialog when the `open` prop is true. The modal can be closed by clicking outside the dialog or by clicking the close button. It accepts props for the modal's title and content.

### Page Components
- **LandingPage**
  - **File**: `taskflow\frontend\src\pages\LandingPage.jsx`
  - **Description**: The main landing page of the TaskFlow application, including navigation, a hero section, features, pricing, and testimonials. It uses links to navigate to login and registration pages.
- **LoginPage**
  - **File**: `taskflow\frontend\src\pages\LoginPage.jsx`
  - **Description**: A page for user login, including form fields for email and password, and handling the submission of login credentials to authenticate the user. Upon successful login, the user is redirected to a specified or default page.
- **RegisterPage**
  - **File**: `taskflow\frontend\src\pages\RegisterPage.jsx`
  - **Description**: A page for user registration, including form fields for full name, email, and password, and attempting to register the user with the provided credentials. Upon successful registration, the user is redirected to the dashboard.
- **DashboardPage**
  - **File**: `taskflow\frontend\src\pages\DashboardPage.jsx`
  - **Description**: A page displaying a dashboard with statistics about open tasks, overdue tasks, and projects. It also shows a list of recent tasks and provides a button to navigate to the task creation page.
- **ProjectsPage**
  - **File**: `taskflow\frontend\src\pages\ProjectsPage.jsx`
  - **Description**: A page displaying a list of projects and allowing users to create new projects through a modal form. It uses the `useProjects` hook to fetch and manage project data.
- **ProjectDetailPage**
  - **File**: `taskflow\frontend\src\pages\ProjectDetailPage.jsx`
  - **Description**: A page for displaying detailed information about a project, including the project's name, description, and settings. It fetches project data from an API endpoint and handles loading and error states.
- **TasksPage**
  - **File**: `taskflow\frontend\src\pages\TasksPage.jsx`
  - **Description**: A page displaying a list of tasks and allowing users to filter tasks by project and search term. It also provides a modal form to create new tasks.
- **TaskDetailPage**
  - **File**: `taskflow\frontend\src\pages\TaskDetailPage.jsx`
  - **Description**: A page for displaying detailed information about a task, using a `TaskDetail` component to show the task details.
- **SettingsPage**
  - **File**: `taskflow\frontend\src\pages\SettingsPage.jsx`
  - **Description**: A page allowing a user to update their full name. It uses a custom hook for authentication and makes an API call to update the user's profile.
- **AdminPage**
  - **File**: `taskflow\frontend\src\pages\AdminPage.jsx`
  - **Description**: A page for administrative tasks, rendering a `PageWrapper` with a title 'Admin' and a `UserTable` component to display user data.
- **NotFoundPage**
  - **File**: `taskflow\frontend\src\pages\NotFoundPage.jsx`
  - **Description**: A page displaying a 404 error message and a link to return to the home page.

## Routing

### Main Application Entry Point
- **File**: `taskflow\frontend\src\main.jsx`
- **Description**: The entry point for the React application, setting up the React DOM, BrowserRouter for routing, and an `AuthProvider` for authentication context. It renders the main `App` component.

### React Router
- **File**: `taskflow\frontend\src\App.jsx`
- **Description**: The `App` component sets up routing for different pages using `react-router-dom`. It includes public and private routes, where private routes require user authentication. Unauthenticated users are redirected to the login page.

## State Management

### Custom Hooks
- **useAuth**
  - **File**: `taskflow\frontend\src\hooks\useAuth.js`
  - **Description**: A custom hook re-exported from `AuthContext` for managing authentication state.
- **useProjects**
  - **File**: `taskflow\frontend\src\hooks\useProjects.js`
  - **Description**: A custom hook that provides state management for projects, including fetching, creating, updating, and deleting projects using an API.
- **useTasks**
  - **File**: `taskflow\frontend\src\hooks\useTasks.js`
  - **Description**: A custom hook that provides state management for tasks, including fetching, creating, updating, and deleting tasks using an API.

### Authentication Context
- **File**: `taskflow\frontend\src\context\AuthContext.jsx`
- **Description**: An authentication context for managing user authentication state, including functions for logging in, registering, and logging out. It interacts with an authentication API and local storage.

## API Client

### Axios Client
- **File**: `taskflow\frontend\src\api\client.js`
- **Description**: An Axios client configured with interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to a login page.

### API Modules
- **Auth API**
  - **File**: `taskflow\frontend\src\api\auth.js`
  - **Description**: Functions for handling authentication operations such as login, registration, logout, and token refreshing.
- **Admin API**
  - **File**: `taskflow\frontend\src\api\admin.js`
  - **Description**: Functions for making HTTP requests to the admin endpoints of the API, including fetching all users, deleting a user, and getting a billing overview.
- **Projects API**
  - **File**: `taskflow\frontend\src\api\projects.js`
  - **Description**: Functions for interacting with the projects API endpoints, including listing, retrieving, creating, updating, and deleting projects.
- **Tasks API**
  - **File**: `taskflow\frontend\src\api\tasks.js`
  - **Description**: Functions for interacting with the tasks API endpoints, including listing, retrieving, creating, updating, and deleting tasks.

## Development Configuration

### Vite Configuration
- **File**: `taskflow\frontend\vite.config.js`
- **Description**: Configures the Vite development server to run on port 3000 and proxy API and uploads requests to a backend server running on port 3001.

### PostCSS Configuration
- **File**: `taskflow\frontend\postcss.config.js`
- **Description**: Configures the PostCSS setup for the frontend project, integrating Tailwind CSS. It defines the content files to be processed and extends the default theme settings.

## Utility Functions

### Authentication Utilities
- **File**: `taskflow\frontend\src\utils\authUtils.js`
- **Description**: Utility functions for managing authentication sessions, including saving, clearing, and retrieving session data from the browser's localStorage.

### Formatters
- **File**: `taskflow\frontend\src\utils\formatters.js`
- **Description**: Utility functions for formatting dates, priorities, and statuses, including functions to format dates in a short format, to format dates relative to the current time, and to format priority and status labels.

### Analytics
- **File**: `taskflow\frontend\src\utils\analytics.js`
- **Description**: Utility functions for tracking user events and identifying users in Mixpanel and Google Analytics. It exports the tracking token and measurement ID for these services.