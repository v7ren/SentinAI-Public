# Architecture and Data Flow

## Main Architectural Components

The TaskFlow application is built using a layered architecture, with clear separation of concerns between different modules and services. The main components of the architecture include:

### 1. **Backend Server**
- **Node.js and Express.js**: The backend is built using Node.js and the Express.js framework, which provides a robust set of features for building web applications.
- **Configuration**: The server is configured in `taskflow\backend\server.js`, which sets up the Express application, loads environment variables, and starts the server on a specified port (default 3001).

### 2. **Database Layer**
- **PostgreSQL**: The application uses PostgreSQL as its primary database. The database connection is managed in `taskflow\backend\config\db.js`, which sets up a connection pool and provides a query function.
- **ORM Models**: Models for interacting with the database are defined in files like `taskflow\backend\src\models\taskModel.js`, `taskflow\backend\src\models\projectModel.js`, `taskflow\backend\src\models\orgModel.js`, and `taskflow\backend\src\models\userModel.js`. These models provide functions for CRUD operations on their respective tables.

### 3. **Controllers**
- **API Endpoints**: Controllers handle HTTP requests and responses. They are responsible for business logic and interacting with the database. Key controllers include:
  - **Authentication**: `taskflow\backend\src\controllers\authController.js` handles user registration, login, token refresh, password reset, and logout.
  - **Projects**: `taskflow\backend\src\controllers\projectController.js` manages project-related operations such as listing, creating, updating, and deleting projects.
  - **Tasks**: `taskflow\backend\src\controllers\taskController.js` handles task management, including listing, creating, updating, and deleting tasks.
  - **Attachments**: `taskflow\backend\src\controllers\attachmentController.js` manages file attachments for tasks.
  - **Reports**: `taskflow\backend\src\controllers\reportController.js` generates PDF reports for projects.
  - **Imports**: `taskflow\backend\src\controllers\importController.js` handles importing tasks from XML and CSV files.
  - **Notifications**: `taskflow\backend\src\controllers\notificationController.js` manages user notifications.
  - **Admin**: `taskflow\backend\src\controllers\adminController.js` provides administrative functionalities like managing users and billing.

### 4. **Services**
- **Report Generation**: `taskflow\backend\src\services\reportService.js` generates HTML and PDF reports using file system operations and the `wkhtmltopdf` tool.
- **Email**: `taskflow\backend\src\services\emailService.js` sends emails using SendGrid for invitations and password reset links.
- **Notifications**: `taskflow\backend\src\services\notificationService.js` manages user notifications and preferences.
- **Stripe**: `taskflow\backend\src\services\stripeService.js` interacts with the Stripe API for payment processing and subscription management.

### 5. **Middleware**
- **Authentication**: `taskflow\backend\src\middleware\authenticate.js` and `taskflow\backend\src\middleware\authorize.js` handle user authentication and authorization.
- **Error Handling**: `taskflow\backend\src\middleware\errorHandler.js` logs errors and sends appropriate JSON responses.
- **File Uploads**: `taskflow\backend\src\middleware\upload.js` configures multer for handling file uploads.
- **Rate Limiting**: `taskflow\backend\src\middleware\rateLimiter.js` limits the rate of report generation requests to prevent abuse.

### 6. **Frontend Application**
- **React**: The frontend is built using React, with components and pages defined in `taskflow\frontend\src`.
- **Routing**: React Router is used for client-side routing, with private routes protected by authentication.
- **Authentication**: The `taskflow\frontend\src\context\AuthContext.jsx` provides authentication state and actions to the application.
- **API Client**: `taskflow\frontend\src\api\client.js` sets up an Axios client for making HTTP requests to the backend API, including interceptors for adding authentication tokens and handling unauthorized responses.
- **Pages**: Key pages include `taskflow\frontend\src\pages\DashboardPage.jsx`, `taskflow\frontend\src\pages\ProjectsPage.jsx`, `taskflow\frontend\src\pages\TasksPage.jsx`, and `taskflow\frontend\src\pages\SettingsPage.jsx`.
- **Components**: Reusable UI components are defined in `taskflow\frontend\src\components`, such as `Button.jsx`, `Badge.jsx`, `Modal.jsx`, and `Spinner.jsx`.

## Data and Control Flow

### 1. **User Authentication**
- **Login**: When a user logs in, the `LoginPage` component sends a POST request to the `authController` in the backend. The `authenticate` middleware verifies the JWT token, and the `authController` handles the login process.
- **Registration**: User registration is handled by the `RegisterPage` component, which sends a POST request to the `authController` to create a new user and organization.
- **Session Management**: The `authUtils` utility functions manage session data in local storage, including saving and clearing tokens and user data.

### 2. **Project Management**
- **Listing Projects**: The `ProjectsPage` component fetches a list of projects from the `projectController` using the `projectsApi` module. The `projectController` interacts with the `projectModel` to query the database.
- **Creating Projects**: When a user creates a new project, the `ProjectsPage` component sends a POST request to the `projectController`, which validates the input and creates a new project record in the database.
- **Updating Projects**: The `ProjectSettings` component allows users to update project details. It sends a PUT request to the `projectController`, which updates the project record in the database.

### 3. **Task Management**
- **Listing Tasks**: The `TasksPage` component fetches a list of tasks from the `taskController` using the `tasksApi` module. The `taskController` interacts with the `taskModel` to query the database.
- **Creating Tasks**: When a user creates a new task, the `TaskForm` component sends a POST request to the `taskController`, which validates the input and creates a new task record in the database.
- **Updating Tasks**: The `TaskDetailPage` component allows users to update task details. It sends a PUT request to the `taskController`, which updates the task record in the database.

### 4. **Attachments**
- **Uploading Attachments**: The `TaskForm` component allows users to upload attachments. The `attachmentController` handles the file upload, storing the file in the filesystem and creating an attachment record in the database.
- **Downloading Attachments**: The `TaskDetailPage` component provides a link to download attachments. The `attachmentController` serves the file from the filesystem.

### 5. **Reports**
- **Generating Reports**: The `ReportController` handles requests to generate PDF reports for projects. It uses the `reportService` to generate an HTML report and convert it to PDF using `wkhtmltopdf`.

### 6. **Notifications**
- **Listing Notifications**: The `NotificationController` handles requests to list notifications for a user. It interacts with the `notificationService` to fetch and manage notifications.
- **Marking as Read**: The `NotificationController` also handles requests to mark notifications as read.

### 7. **Admin Functions**
- **Managing Users**: The `AdminPage` component allows administrators to manage users. It fetches user data from the `adminController` and provides actions to delete users.
- **Billing Overview**: The `AdminPage` also provides a billing overview, which is fetched from the `adminController`.

### 8. **Error Handling**
- **Global Error Handling**: The `errorHandler` middleware in the backend logs errors and sends appropriate JSON responses. The frontend uses the `error` utility function to log errors and display error messages to the user.

### 9. **Security**
- **Rate Limiting**: The `rateLimiter` middleware limits the rate of report generation requests to prevent abuse.
- **Authorization**: The `authorize` middleware ensures that only users with the appropriate roles can access certain resources.

## Important Patterns
- **Model-View-Controller (MVC)**: The application follows the MVC pattern, with models handling database interactions, views (React components) rendering the UI, and controllers handling business logic and HTTP requests.
- **Middleware**: Middleware functions in Express.js are used to handle cross-cutting concerns like authentication, error handling, and rate limiting.
- **Service Layer**: Services encapsulate business logic and interact with external systems like email services and payment gateways.
- **State Management**: React hooks like `useProjects` and `useTasks` manage state and side effects for fetching and updating data.

By following this architecture, the TaskFlow application ensures a clear separation of concerns, maintainability, and scalability.