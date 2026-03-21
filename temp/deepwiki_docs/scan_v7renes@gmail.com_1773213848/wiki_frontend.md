# Frontend

This section describes the frontend architecture of the TaskFlow application, including the React components, routing, state management, and API interactions.

## React Components

### Main Application Component
- **File**: `taskflow\frontend\src\App.jsx`
- **Description**: The main entry point of the application. It sets up routing using `react-router-dom` and defines public and private routes. Private routes require user authentication, and unauthenticated users are redirected to the login page.

### Layout Components
- **Navbar**
  - **File**: `taskflow\frontend\src\components\Layout\Navbar.jsx`
  - **Description**: A header component that displays navigation links to the dashboard and settings, and includes a logout button. It uses the `useAuth` hook to manage authentication state.
- **Sidebar**
  - **File**: `taskflow\frontend\src\components\Layout\Sidebar.jsx`
  - **Description**: A navigation sidebar that displays links to different sections of the application. It shows additional admin-specific links if the user has an admin role.
- **PageWrapper**
  - **File**: `taskflow\frontend\src\components\Layout\PageWrapper.jsx`
  - **Description**: A layout component that wraps the main content area, including a sidebar and a navbar. It accepts children and a title as props.

### Project Components
- **ProjectCard**
  - **File**: `taskflow\frontend\src\components\Projects\ProjectCard.jsx`
  - **Description**: A card component that displays a project's name, a truncated description, and an archived status. It is a clickable link that navigates to the project's detail page.
- **ProjectDetailPage**
  - **File**: `taskflow\frontend\src\pages\ProjectDetailPage.jsx`
  - **Description**: A page component that displays detailed information about a project, including tasks and project settings. It fetches project data from the API and handles loading and error states.
- **ProjectSettings**
  - **File**: `taskflow\frontend\src\components\Projects\ProjectSettings.jsx`
  - **Description**: A component that allows users to update a project's name, description, and archived status. It uses the `useProjects` hook to handle project updates and provides a form for user input.

### Task Components
- **TaskCard**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskCard.jsx`
  - **Description**: A card component that displays a task's title, status, priority, due date, and assignee. It includes a link to the task's detail page.
- **TaskDetailPage**
  - **File**: `taskflow\frontend\src\pages\TaskDetailPage.jsx`
  - **Description**: A page component that displays detailed information about a specific task, including its status, priority, due date, title, and description. It fetches the task data from the API and handles loading and error states.
- **TaskForm**
  - **File**: `taskflow\frontend\src\components\Tasks\TaskForm.jsx`
  - **Description**: A form component used to create or edit a task. It includes form fields for the task's title, description, priority, status, and due date. The component handles form submission and provides a callback to the parent component upon successful submission.
- **CommentList**
  - **File**: `taskflow\frontend\src\components\Tasks\CommentList.jsx`
  - **Description**: A component that displays a list of comments for a given task and allows users to add new comments. It fetches comments from the API and updates the list when new comments are posted.

### UI Components
- **Button**
  - **File**: `taskflow\frontend\src\components\UI\Button.jsx`
  - **Description**: A reusable button component that accepts props for customizing the button's appearance and behavior, such as variant, size, and additional class names.
- **Badge**
  - **File**: `taskflow\frontend\src\components\UI\Badge.jsx`
  - **Description**: A component that displays a styled badge with different variants (default, success, warning, danger, info). It accepts children and a variant prop to customize its appearance.
- **Modal**
  - **File**: `taskflow\frontend\src\components\UI\Modal.jsx`
  - **Description**: A modal dialog component that displays a modal when the `open` prop is true. It can be closed by clicking outside the dialog or by clicking the close button.
- **Spinner**
  - **File**: `taskflow\frontend\src\components\UI\Spinner.jsx`
  - **Description**: A component that renders a spinning circle to indicate loading states. It accepts a `className` prop to allow for additional styling.

### Page Components
- **AdminPage**
  - **File**: `taskflow\frontend\src\pages\AdminPage.jsx`
  - **Description**: A page component that serves as the admin section of the application. It displays a header and a table of users using the `UserTable` component.
- **DashboardPage**
  - **File**: `taskflow\frontend\src\pages\DashboardPage.jsx`
  - **Description**: A page component that displays a dashboard with statistics about open tasks, overdue tasks, and projects. It also shows a list of recent tasks and provides a button to navigate to the task creation page.
- **LoginPage**
  - **File**: `taskflow\frontend\src\pages\LoginPage.jsx`
  - **Description**: A page component for the login page, which includes form fields for email and password, and handles the submission of login credentials to authenticate the user. Upon successful login, the user is redirected to a specified or default page.
- **LandingPage**
  - **File**: `taskflow\frontend\src\pages\LandingPage.jsx`
  - **Description**: A page component for the landing page of the TaskFlow application. It includes navigation links to login and register pages, a main section with a call to action, a features section, a pricing section, and testimonials from users.
- **NotFoundPage**
  - **File**: `taskflow\frontend\src\pages\NotFoundPage.jsx`
  - **Description**: A page component that displays a 404 error page with a message and a link to return to the home page.
- **RegisterPage**
  - **File**: `taskflow\frontend\src\pages\RegisterPage.jsx`
  - **Description**: A page component for the user registration page. It handles user input for full name, email, and password, and sends a registration request to an authentication service. Upon successful registration, it redirects the user to the dashboard.
- **SettingsPage**
  - **File**: `taskflow\frontend\src\pages\SettingsPage.jsx`
  - **Description**: A page component that allows a user to update their full name. It uses a custom hook for authentication and makes an API call to update the user's profile.
- **ProjectsPage**
  - **File**: `taskflow\frontend\src\pages\ProjectsPage.jsx`
  - **Description**: A page component that displays a list of projects and provides a modal for creating new projects. It uses the `useProjects` hook to fetch and manage project data.
- **TasksPage**
  - **File**: `taskflow\frontend\src\pages\TasksPage.jsx`
  - **Description**: A page component that displays a list of tasks and allows users to filter tasks by project and search term. It also includes a modal form for creating new tasks.

## Routing

- **Main Application Component**
  - **File**: `taskflow\frontend\src\App.jsx`
  - **Description**: The `App` component sets up routing using `react-router-dom`. It defines public and private routes, where private routes require user authentication. Unauthenticated users are redirected to the login page.

## State Management

- **useAuth Hook**
  - **File**: `taskflow\frontend\src\hooks\useAuth.js`
  - **Description**: A custom React hook that provides authentication state and functions to log in, register, and log out. It interacts with an authentication API and local storage.
- **useProjects Hook**
  - **File**: `taskflow\frontend\src\hooks\useProjects.js`
  - **Description**: A custom React hook that manages the state and lifecycle of projects data. It includes functions to fetch, create, update, and delete projects, interacting with an API through the `projectsApi` module.
- **useTasks Hook**
  - **File**: `taskflow\frontend\src\hooks\useTasks.js`
  - **Description**: A custom React hook that manages the state and lifecycle of tasks for a given project. It includes functions to fetch, create, update, and delete tasks, interacting with an API through the `tasksApi` module.

## API Interactions

- **Axios Client**
  - **File**: `taskflow\frontend\src\api\client.js`
  - **Description**: An Axios client configured with interceptors for adding authentication tokens to requests and handling unauthorized responses by redirecting to the login page.
- **Admin API**
  - **File**: `taskflow\frontend\src\api\admin.js`
  - **Description**: Functions for making HTTP requests to the admin endpoints of the API, including fetching all users, deleting a user, and getting a billing overview.
- **Auth API**
  - **File**: `taskflow\frontend\src\api\auth.js`
  - **Description**: Functions for handling authentication operations such as login, registration, logout, and token refreshing. It uses the imported client to make HTTP POST requests to the corresponding API endpoints.
- **Projects API**
  - **File**: `taskflow\frontend\src\api\projects.js`
  - **Description**: Functions for interacting with the projects API, including listing, retrieving, creating, updating, and deleting projects. Each function makes an HTTP request using the imported client.
- **Tasks API**
  - **File**: `taskflow\frontend\src\api\tasks.js`
  - **Description**: Functions for interacting with the tasks API, including listing, retrieving, creating, updating, and deleting tasks. Each function makes an HTTP request using the imported client.

## Configuration

- **PostCSS Configuration**
  - **File**: `taskflow\frontend\postcss.config.js`
  - **Description**: Configures the PostCSS setup for the frontend project, integrating Tailwind CSS. It specifies the files to be processed and includes the default theme and plugins configuration.
- **Vite Configuration**
  - **File**: `taskflow\frontend\vite.config.js`
  - **Description**: Configures the Vite development server for the React application, setting up port 3000 and proxying API and uploads requests to a backend server running on port 3001.

## Utilities

- **Analytics**
  - **File**: `taskflow\frontend\src\utils\analytics.js`
  - **Description**: Utility functions for tracking events and identifying users in an analytics system, using Mixpanel and Google Analytics.
- **Auth Utilities**
  - **File**: `taskflow\frontend\src\utils\authUtils.js`
  - **Description**: Utility functions for managing authentication sessions in the frontend application. It provides methods to save, clear, and retrieve session data from the browser's local storage.
- **Formatters**
  - **File**: `taskflow\frontend\src\utils\formatters.js`
  - **Description**: Utility functions for formatting dates, priorities, and statuses. It includes functions to format dates in a specific format, format dates relative to the current time, and format priority and status labels.

This documentation provides a comprehensive overview of the frontend architecture, including the key components, routing, state management, API interactions, and utility functions. Each component and utility is mapped back to its respective file and function, ensuring clarity and ease of reference.