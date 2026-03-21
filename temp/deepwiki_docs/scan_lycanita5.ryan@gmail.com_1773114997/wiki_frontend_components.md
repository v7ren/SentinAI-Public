# Frontend Components

This section provides an overview of the key React components used in the frontend of the TaskFlow application. It covers the components' props, state, and interactions with the backend.

## Main Application Component

### `App.jsx`
- **Description**: The main entry point of the application, which sets up routing for various pages, including public and private routes. Private routes require user authentication, redirecting unauthenticated users to the login page.
- **Props**: None
- **State**: None
- **Interactions**:
  - **Routing**: Uses `react-router-dom` to define routes for different pages.
  - **Authentication**: Manages user authentication and redirects unauthenticated users to the login page.

## Layout Components

### `PageWrapper.jsx`
- **Description**: A layout container for other components, including a sidebar and a navbar. It can display a title and children components within the main content area.
- **Props**:
  - `children`: React nodes to be rendered within the main content area.
  - `title`: A string to be displayed as the page title.
- **State**: None
- **Interactions**:
  - **Sidebar and Navbar**: Integrates the `Sidebar` and `Navbar` components to provide navigation and user information.

### `Navbar.jsx`
- **Description**: Displays a navigation bar at the top of the application, including links to the dashboard, settings, and a logout button.
- **Props**: None
- **State**: None
- **Interactions**:
  - **Authentication**: Uses the `useAuth` hook to manage authentication state and handle logout actions.

### `Sidebar.jsx`
- **Description**: Displays a sidebar with navigation links to different sections of the app. The sidebar shows the user's email and additional links based on the user's role.
- **Props**: None
- **State**: None
- **Interactions**:
  - **Navigation**: Uses `react-router-dom` to create navigation links.
  - **Authentication**: Uses the `useAuth` hook to manage user authentication and display role-based links.

## Page Components

### `AdminPage.jsx`
- **Description**: A page for administrative tasks, including a table of users and actions to manage them.
- **Props**: None
- **State**: None
- **Interactions**:
  - **User Table**: Integrates the `UserTable` component to display and manage user data.
  - **Authentication**: Requires user authentication and admin role to access.

### `DashboardPage.jsx`
- **Description**: Displays a dashboard with statistics about open tasks, overdue tasks, and projects. It also shows a list of recent tasks and provides a button to navigate to the task creation page.
- **Props**: None
- **State**: None
- **Interactions**:
  - **Data Fetching**: Uses the `useTasks` and `useProjects` hooks to fetch and manage task and project data.
  - **Navigation**: Provides links to create new tasks and navigate to project details.

### `LandingPage.jsx`
- **Description**: The landing page of the TaskFlow application, including navigation, a main section with a call to action, a features section, a pricing section, and testimonials from users.
- **Props**: None
- **State**: None
- **Interactions**:
  - **Navigation**: Uses `react-router-dom` to navigate to login and registration pages.

### `LoginPage.jsx`
- **Description**: A page for user login, including form fields for email and password, and a submit button to authenticate the user.
- **Props**: None
- **State**:
  - `email`: The user's email address.
  - `password`: The user's password.
  - `loading`: A boolean indicating whether the login request is in progress.
- **Interactions**:
  - **Form Submission**: Handles form submission to authenticate the user using the `authApi` module.
  - **Navigation**: Redirects the user to the dashboard upon successful login.

### `NotFoundPage.jsx`
- **Description**: Displays a 404 error page with a message and a link to return to the home page.
- **Props**: None
- **State**: None
- **Interactions**: None

### `ProjectsPage.jsx`
- **Description**: Displays a list of projects and provides a modal for creating new projects.
- **Props**: None
- **State**:
  - `projects`: An array of project objects.
  - `isModalOpen`: A boolean indicating whether the project creation modal is open.
- **Interactions**:
  - **Data Fetching**: Uses the `useProjects` hook to fetch and manage project data.
  - **Modal**: Manages the state of the project creation modal and handles form submission to create new projects.

### `ProjectDetailPage.jsx`
- **Description**: Displays details of a project and provides options to view tasks and manage project settings.
- **Props**: None
- **State**:
  - `project`: The project object.
  - `loading`: A boolean indicating whether the project data is being fetched.
  - `error`: An error object if the project data fetch fails.
- **Interactions**:
  - **Data Fetching**: Fetches project data from the API using the `projectsApi` module.
  - **Navigation**: Provides links to tasks and project settings.

### `RegisterPage.jsx`
- **Description**: A page for user registration, including form fields for full name, email, and password, and a submit button to register the user.
- **Props**: None
- **State**:
  - `fullName`: The user's full name.
  - `email`: The user's email address.
  - `password`: The user's password.
  - `loading`: A boolean indicating whether the registration request is in progress.
- **Interactions**:
  - **Form Submission**: Handles form submission to register the user using the `authApi` module.
  - **Navigation**: Redirects the user to the dashboard upon successful registration.

### `SettingsPage.jsx`
- **Description**: Allows users to update their full name. It uses a custom hook for authentication and makes an API call to update the user's profile.
- **Props**: None
- **State**:
  - `fullName`: The user's full name.
  - `loading`: A boolean indicating whether the update request is in progress.
- **Interactions**:
  - **Data Fetching**: Uses the `useAuth` hook to manage user authentication and fetch the current user's profile.
  - **Form Submission**: Handles form submission to update the user's profile using the `authApi` module.

### `TaskDetailPage.jsx`
- **Description**: Displays detailed information about a specific task, including its status, priority, due date, title, and description. It fetches the task data from an API endpoint using the `taskId` obtained from the URL parameters.
- **Props**: None
- **State**:
  - `task`: The task object.
  - `loading`: A boolean indicating whether the task data is being fetched.
  - `error`: An error object if the task data fetch fails.
- **Interactions**:
  - **Data Fetching**: Fetches task data from the API using the `tasksApi` module.
  - **Comments**: Integrates the `CommentList` component to display and manage comments for the task.

### `TasksPage.jsx`
- **Description**: Displays a list of tasks and allows users to filter tasks by project and search term. It also provides a modal form for creating new tasks.
- **Props**: None
- **State**:
  - `tasks`: An array of task objects.
  - `isModalOpen`: A boolean indicating whether the task creation modal is open.
  - `searchTerm`: A string to filter tasks by title.
  - `selectedProject`: The ID of the selected project to filter tasks.
- **Interactions**:
  - **Data Fetching**: Uses the `useTasks` hook to fetch and manage task data.
  - **Modal**: Manages the state of the task creation modal and handles form submission to create new tasks.
  - **Filtering**: Provides options to filter tasks by project and search term.

## Task and Project Components

### `ProjectCard.jsx`
- **Description**: Displays a card for a project, including the project's name, a truncated description, and an archived status if applicable. The card is a clickable link that navigates to the project's detail page.
- **Props**:
  - `project`: The project object.
- **State**: None
- **Interactions**:
  - **Navigation**: Links to the project's detail page using `react-router-dom`.

### `ProjectSettings.jsx`
- **Description**: Displays and updates the settings of a project, including fields for the project's name, description, and archived status. It uses a form to collect user input and calls an `updateProject` function to save changes.
- **Props**:
  - `project`: The project object.
  - `onUpdate`: A callback function to handle project updates.
- **State**:
  - `name`: The project's name.
  - `description`: The project's description.
  - `archived`: A boolean indicating whether the project is archived.
- **Interactions**:
  - **Form Submission**: Handles form submission to update the project using the `projectsApi` module.

### `TaskCard.jsx`
- **Description**: Displays a card for a task, including its title, status, priority, due date, and assignee. The card is a clickable link that navigates to the task's detail page.
- **Props**:
  - `task`: The task object.
- **State**: None
- **Interactions**:
  - **Navigation**: Links to the task's detail page using `react-router-dom`.

### `TaskDetail.jsx`
- **Description**: Displays detailed information about a specific task, including its status, priority, due date, title, and description. It fetches the task data from an API endpoint using the `taskId` obtained from the URL parameters.
- **Props**: None
- **State**:
  - `task`: The task object.
  - `loading`: A boolean indicating whether the task data is being fetched.
  - `error`: An error object if the task data fetch fails.
- **Interactions**:
  - **Data Fetching**: Fetches task data from the API using the `tasksApi` module.
  - **Comments**: Integrates the `CommentList` component to display and manage comments for the task.

### `TaskForm.jsx`
- **Description**: A form for creating or editing a task, including fields for the task's title, description, priority, status, and due date. It handles form submission and provides a cancel button to close the form.
- **Props**:
  - `initialValues`: An object containing initial values for the form fields.
  - `onSubmit`: A callback function to handle form submission.
  - `onCancel`: A callback function to handle form cancellation.
- **State**:
  - `title`: The task's title.
  - `description`: The task's description.
  - `priority`: The task's priority.
  - `status`: The task's status.
  - `dueDate`: The task's due date.
- **Interactions**:
  - **Form Submission**: Handles form submission to create or update a task using the `tasksApi` module.

### `CommentList.jsx`
- **Description**: Displays a list of comments for a given task and allows users to add new comments. It fetches comments from an API and updates the list when new comments are posted.
- **Props**:
  - `taskId`: The ID of the task.
- **State**:
  - `comments`: An array of comment objects.
  - `newComment`: The text of the new comment being added.
  - `loading`: A boolean indicating whether the comments are being fetched.
  - `error`: An error object if the comments fetch fails.
- **Interactions**:
  - **Data Fetching**: Fetches comments from the API using the `tasksApi` module.
  - **Form Submission**: Handles form submission to add new comments using the `tasksApi` module.

## UI Components

### `Button.jsx`
- **Description**: A reusable button component that can be styled with different variants and sizes.
- **Props**:
  - `children`: The content to be displayed inside the button.
  - `variant`: The variant of the button (e.g., primary, secondary).
  - `size`: The size of the button (e.g., small, medium, large).
  - `className`: Additional class names to be applied to the button.
- **State**: None
- **Interactions**: None

### `Badge.jsx`
- **Description**: A reusable badge component that can be styled with different variants such as default, success, warning, danger, and info.
- **Props**:
  - `children`: The content to be displayed inside the badge.
  - `variant`: The variant of the badge (e.g., default, success, warning, danger, info).
- **State**: None
- **Interactions**: None

### `Modal.jsx`
- **Description**: A modal component that displays a centered dialog when the `open` prop is true. It includes a close button and a title, and can render any children components passed to it.
- **Props**:
  - `open`: A boolean indicating whether the modal is open.
  - `title`: The title of the modal.
  - `children`: The content to be displayed inside the modal.
  - `onClose`: A callback function to handle the modal close event.
- **State**: None
- **Interactions**:
  - **Close Button**: Closes the modal when the close button is clicked.
  - **Outside Click**: Closes the modal when the user clicks outside the modal content.

### `Spinner.jsx`
- **Description**: A spinner component that displays a spinning circle to indicate loading states. It accepts a `className` prop to allow for additional styling.
- **Props**:
  - `className`: Additional class names to be applied to the spinner.
- **State**: None
- **Interactions**: None

## Utility Components

### `authUtils.js`
- **Description**: Utility functions for managing authentication sessions in the frontend application.
- **Functions**:
  - `saveSession`: Saves the authentication token, user object, and refresh token to `localStorage`.
  - `clearSession`: Clears the authentication token, user object, and refresh token from `localStorage`.
  - `getToken`: Retrieves the authentication token from `localStorage`.
  - `getRefreshToken`: Retrieves the refresh token from `localStorage`.
  - `getStoredUser`: Retrieves the user object from `localStorage`, parsing it from JSON if it exists.

### `formatters.js`
- **Description**: Utility functions for formatting dates, priorities, and statuses.
- **Functions**:
  - `formatDate`: Formats a given date object or string into a short date format.
  - `formatRelative`: Formats a given date object or string into a relative time format based on the current time.
  - `priorityLabel`: Formats a given priority string, capitalizing the first letter and defaulting to 'Medium' if undefined.
  - `statusLabel`: Formats a given status string, replacing underscores with spaces, capitalizing each word, and defaulting to 'Open' if undefined.

### `analytics.js`
- **Description**: Utility functions for tracking user events and identifying users in Mixpanel and Google Analytics.
- **Functions**:
  - `trackEvent`: Tracks an event in Mixpanel and Google Analytics, checking if the window object and analytics libraries are available.
  - `identify`: Identifies a user in Mixpanel and Google Analytics, checking if the window object and analytics libraries are available.

This overview covers the key React components used in the frontend of the TaskFlow application, including their props, state, and interactions with the backend. Each component plays a crucial role in providing a seamless and functional user experience.