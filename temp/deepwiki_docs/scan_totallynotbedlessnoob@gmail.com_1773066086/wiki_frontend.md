# Frontend

The frontend of the TaskFlow application is built using React and follows a structured architecture to manage components, routing, state, and UI elements. This section covers the key components, routing, state management, and UI elements used in the TaskFlow frontend.

## Components

### Main Application Component
- **File**: `taskflow\frontend\src\App.jsx`
- **Description**: The main entry point of the React application. It sets up routing for various pages, including public and private routes. Private routes require user authentication, redirecting unauthenticated users to the login page.
- **Key Features**:
  - **Routing**: Uses `react-router-dom` to define routes for landing, login, registration, dashboard, projects, tasks, settings, admin, and a not found page.
  - **Authentication**: Protects certain routes using a `PrivateRoute` component that checks user authentication.

### Layout Components
- **Navbar**
  - **File**: `taskflow\frontend\src\components\Layout\Navbar.jsx`
  - **Description**: Displays a navigation bar with links to the dashboard, user settings, and a logout button. It uses the `useAuth` hook to manage authentication state.
- **Sidebar**
  - **File**: `taskflow\frontend\src\components\Layout\Sidebar.jsx`
  - **Description**: Displays navigation links based on the user's role. It uses the `useAuth` hook to determine if the user is an admin and conditionally adds an admin link.
- **PageWrapper**
  - **File**: `taskflow\frontend\src\components\Layout\PageWrapper.jsx`
  - **Description**: Provides a consistent layout with a sidebar, navbar, and a main content area. It accepts children and title as props.

### Page Components
- **LandingPage**
  - **File**: `taskflow\frontend\src\pages\LandingPage.jsx`
  - **Description**: The landing page for the TaskFlow application, including navigation links, a hero section, features, pricing, and testimonials.
- **LoginPage**
  - **File**: `taskflow\frontend\src\pages\LoginPage.jsx`
  - **Description**: Handles user login, including form fields for email and password, and redirects upon successful authentication.
- **RegisterPage**
  - **File**: `taskflow\frontend\src\pages\RegisterPage.jsx`
  - **Description**: Handles user registration, including form fields for full name, email, and password, and redirects upon successful registration.
- **DashboardPage**
  - **File**: `taskflow\frontend\src\pages\DashboardPage.jsx`
  - **Description**: Displays a dashboard with statistics about open tasks, overdue tasks, and projects. It also shows a list of recent tasks and provides a button to navigate to the task creation page.
- **ProjectsPage**
  - **File**: `taskflow\frontend\src\pages\ProjectsPage.jsx`
  - **Description**: Displays a list of projects and provides a modal for creating new projects. It uses the `useProjects` hook to fetch and manage project data.
- **ProjectDetailPage**
  - **File**: `taskflow\frontend\src\pages\ProjectDetailPage.jsx`
  - **Description**: Displays details of a specific project, including settings. It fetches project data from an API and handles loading and error states.
- **TasksPage**
  - **File**: `taskflow\frontend\src\pages\TasksPage.jsx`
  - **Description**: Displays a list of tasks, allows filtering by project and search term, and includes a modal for creating new tasks.
- **TaskDetailPage**
  - **File**: `taskflow\frontend\src\pages\TaskDetailPage.jsx`
  - **Description**: Displays detailed information about a specific task, including its status, priority, due date, title, and description. It fetches the task data from an API endpoint.
- **SettingsPage**
  - **File**: `taskflow\frontend\src\pages\SettingsPage.jsx`
  - **Description**: Allows users to update their profile information, specifically their full name. It uses React hooks for state management and authentication, and makes an API call to update the user's profile.
- **AdminPage**
  - **File**: `taskflow\frontend\src\pages\AdminPage.jsx`
  - **Description**: Displays a table of users using the `UserTable` component, wrapped in a `PageWrapper` component.

### UI Components
- **Badge**
  - **File**: `taskflow\frontend\src\components\UI\Badge.jsx`
  - **Description**: Displays a badge with different styles based on the variant prop.
- **Button**
  - **File**: `taskflow\frontend\src\components\UI\Button.jsx`
  - **Description**: A reusable button component that accepts props for customizing the button's appearance and behavior.
- **Spinner**
  - **File**: `taskflow\frontend\src\components\UI\Spinner.jsx`
  - **Description**: Displays a spinning circle to indicate loading states.
- **Modal**
  - **File**: `taskflow\frontend\src\components\UI\Modal.jsx`
  - **Description**: Displays a modal dialog when the `open` prop is true, and can be closed by clicking outside the dialog or by clicking the close button.

### Task and Project Components
- **ProjectCard**
  - **File**: `taskflow\frontend\src\components\Projects\ProjectCard.jsx`
  - **Description**: Displays a card for a project, including the project's name, a truncated description, and an archived status if applicable. The card is a clickable link that navigates to the project's detail page.
- **ProjectSettings**
  - **File**: `taskflow\frontend\src\components\Projects\ProjectSettings.jsx`
  - **Description**: Allows users to update the name, description, and archived status of a project. It uses the `useProjects` hook to handle project updates and provides a form for user input.
- **TaskCard**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskCard.jsx`
  - **Description**: Displays a card for a task, including the task's title, status, priority, due date, and assignee name. It uses badges to visually represent the status and priority of the task. The card is a clickable link that navigates to the task's detail page.
- **TaskForm**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskForm.jsx`
  - **Description**: Used to create or edit a task, including form fields for the task's title, description, priority, status, and due date. The form can be submitted to save the task or canceled to close the form.
- **TaskDetail**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskDetail.jsx`
  - **Description**: Displays detailed information about a specific task, including its status, priority, due date, title, and description. It fetches the task data from an API endpoint and handles loading and error states.
- **CommentList**
  - **File**: `taskflow\frontend\src\components\Tasks\CommentList.jsx`
  - **Description**: Displays a list of comments for a given task and allows users to add new comments. It fetches comments from an API and updates the list when new comments are posted.

## Routing

- **Main Application Entry Point**
  - **File**: `taskflow\frontend\src\main.jsx`
  - **Description**: Sets up the React application, including the root component, routing with `BrowserRouter`, and provides authentication context to the application through `AuthProvider`.

## State Management

- **useAuth**
  - **File**: `taskflow\frontend\src\hooks\useAuth.js`
  - **Description**: A React hook for managing authentication state, re-exported from `AuthContext`.
- **useProjects**
  - **File**: `taskflow\frontend\src\hooks\useProjects.js`
  - **Description**: A custom React hook that provides state management and API interaction for projects data. It includes functions to fetch, create, update, and delete projects.
- **useTasks**
  - **File**: `taskflow\frontend\src\hooks\useTasks.js`
  - **Description**: A custom React hook that provides state management and API interaction for tasks within a project. It includes functions to fetch, create, update, and delete tasks.

## API Client

- **API Client**
  - **File**: `taskflow\frontend\src\api\client.js`
  - **Description**: Sets up an Axios client for making HTTP requests to a backend API. It includes interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to the login page.

## Authentication Context

- **AuthContext**
  - **File**: `taskflow\frontend\src\context\AuthContext.jsx`
  - **Description**: Provides authentication context to the application, including state management and functions for user login, registration, and logout. It uses a custom API for authentication and utility functions to manage session storage.

## Utilities

- **Formatters**
  - **File**: `taskflow\frontend\src\utils\formatters.js`
  - **Description**: Contains utility functions for formatting dates and labels, including functions to format dates in a specific locale, format dates relative to the current time, and format priority and status labels.
- **AuthUtils**
  - **File**: `taskflow\frontend\src\utils\authUtils.js`
  - **Description**: Contains utility functions for managing authentication sessions in local storage, including saving, clearing, and retrieving session tokens and user data.
- **Analytics**
  - **File**: `taskflow\frontend\src\utils\analytics.js`
  - **Description**: Contains utility functions for tracking events and identifying users in Mixpanel and Google Analytics.

## Development Configuration

- **Vite Configuration**
  - **File**: `taskflow\frontend\vite.config.js`
  - **Description**: Configures the Vite development server for the React application, setting up port 3000 and proxying API and uploads requests to a backend server running on port 3001.

This structured approach ensures that the frontend of the TaskFlow application is modular, maintainable, and scalable, providing a seamless user experience with robust state management and authentication.