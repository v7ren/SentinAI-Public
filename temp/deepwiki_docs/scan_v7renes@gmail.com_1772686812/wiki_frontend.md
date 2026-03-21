# Frontend

This section details the frontend implementation of the project, which is built using Next.js, React, and Tailwind CSS. The frontend is responsible for rendering the user interface, handling user interactions, and communicating with the backend API.

## Project Structure

### Configuration Files

#### `tailwind.config.ts`
- **Location**: `vulnerable-server\frontend\tailwind.config.ts`
- **Purpose**: Configures the Tailwind CSS setup for the frontend application.
- **Key Features**:
  - Specifies the file paths to scan for CSS class usage.
  - Extends the default theme with custom background images.
- **Usage**:
  - The configuration object is exported as the default export and is used by Tailwind CSS to generate the final CSS.

#### `next-env.d.ts`
- **Location**: `vulnerable-server\frontend\next-env.d.ts`
- **Purpose**: Provides type definitions for the Next.js framework and its image component.
- **Key Features**:
  - Not intended to be edited.
  - Used by the TypeScript compiler to provide type definitions for the Next.js framework.
- **Usage**:
  - This file is automatically included by the TypeScript compiler to ensure type safety in the Next.js application.

### Layout and Pages

#### `layout.tsx`
- **Location**: `vulnerable-server\frontend\src\app\layout.tsx`
- **Purpose**: Defines the root layout for the Next.js application.
- **Key Features**:
  - Sets up the basic HTML structure and metadata for the application.
  - Includes a title and description for the metadata.
  - Provides a container for rendering child components.
- **Usage**:
  - This component wraps all pages in the Next.js application, ensuring a consistent structure and metadata.

#### `page.tsx`
- **Location**: `vulnerable-server\frontend\src\app\page.tsx`
- **Purpose**: Defines the landing page for the TaskFlow project management application.
- **Key Features**:
  - Includes a navigation bar, hero section, features, social proof, pricing, and footer.
  - Contains a scroll effect for the navigation bar.
  - Runs client-side analytics based on URL parameters.
- **Usage**:
  - The landing page is the main entry point for users and provides an overview of the application's features and pricing.

### Authentication Pages

#### `login\page.tsx`
- **Location**: `vulnerable-server\frontend\src\app\login\page.tsx`
- **Purpose**: Defines a React component for the login page.
- **Key Features**:
  - Includes a form for users to enter their email and password.
  - Handles form submission and displays errors.
  - Redirects to the dashboard upon successful login.
  - Provides links to register and reset the password.
- **API Interaction**:
  - Submits form data to the `/api/auth/login` endpoint.
- **Usage**:
  - This component serves as the entry point for the login page and handles user authentication.

#### `register\page.tsx`
- **Location**: `vulnerable-server\frontend\src\app\register\page.tsx`
- **Purpose**: Defines a React component for the user registration page.
- **Key Features**:
  - Handles form input for user details, including name, email, password, and an optional company field.
  - Submits form data to a backend API for user registration.
  - Redirects to the login page upon successful registration.
  - Includes error handling to display any issues that occur during the registration process.
- **API Interaction**:
  - Submits form data to the `/api/auth/register` endpoint.
- **Usage**:
  - This component serves as the entry point for the user registration page and handles user registration.

### Dashboard and Admin Pages

#### `dashboard\page.tsx`
- **Location**: `vulnerable-server\frontend\src\app\dashboard\page.tsx`
- **Purpose**: Defines a React component for the dashboard page in the task management application.
- **Key Features**:
  - Manages tasks, projects, and documents.
  - Handles user settings.
  - Fetches data from a backend API.
  - Provides options for creating, importing, and exporting tasks.
  - Includes a modal for creating new tasks and a sidebar for navigation.
- **API Interactions**:
  - Fetches project and scan data from `/api/projects/:userId` and `/api/scans/:userId/:projectId`.
  - Submits tasks to `/api/tasks`.
  - Uploads documents to `/api/documents/upload`.
  - Processes bulk data via `/api/bulk/process`.
- **Usage**:
  - This component serves as the main interface for users to manage their tasks and projects.

#### `admin\page.tsx`
- **Location**: `vulnerable-server\frontend\src\app\admin\page.tsx`
- **Purpose**: Defines a React component for the admin panel.
- **Key Features**:
  - Includes user management, system status, system logs, database query execution, network diagnostics, external data synchronization, and maintenance mode toggling.
  - Fetches data from a backend API and updates the UI accordingly.
- **API Interactions**:
  - Fetches user data from `/api/admin/users`.
  - Fetches system status from `/api/admin/status`.
  - Fetches logs from `/api/admin/logs`.
  - Runs diagnostics via `/api/admin/diagnostics`.
  - Executes custom queries via `/api/admin/query`.
  - Syncs external data via `/api/admin/sync`.
  - Processes data via `/api/admin/process`.
- **Usage**:
  - This component serves as the main interface for administrators to manage the system and perform various administrative tasks.

## Summary

The frontend of the project is built using Next.js, React, and Tailwind CSS. It consists of several key components, including the root layout, landing page, authentication pages, dashboard, and admin panel. Each component is designed to handle specific user interactions and communicate with the backend API to fetch and update data. The configuration files ensure that the application is properly set up and styled, providing a consistent and user-friendly experience.