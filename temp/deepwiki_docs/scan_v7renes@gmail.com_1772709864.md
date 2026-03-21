# Overview

## What the Project Is and What Problem It Solves

This project is a FastAPI-based web application designed to provide job listings and a simple health check. It addresses the need for a lightweight, efficient, and secure way to manage and retrieve job listings, while also ensuring that certain job listings are accessible only to authorized users. The application initializes a SQLite database with predefined job entries, including a hidden job that can only be accessed by admins, ensuring that sensitive information is protected.

## Main Components or Modules

### FastAPI Application
- **File**: `XBEN-006-24\app\main.py`
- **Description**: This file sets up the FastAPI application and defines the main endpoints. It initializes the SQLite database and populates it with predefined job entries during startup.

### SQLite Database
- **Description**: The application uses a SQLite database to store job listings. The database is initialized and populated with job entries, including a hidden job that is accessible only by admins.

### HTTP Endpoints
- **Job Listings Endpoint**:
  - **Path**: `/jobs`
  - **Method**: POST
  - **Description**: Retrieves job listings based on the job type. It includes basic input sanitization to prevent SQL injection.
- **Health Check Endpoint**:
  - **Path**: `/ping`
  - **Method**: GET
  - **Description**: A simple health check endpoint that returns a 'pong' response.
- **Root HTML File Endpoint**:
  - **Path**: `/`
  - **Method**: GET
  - **Description**: Serves the root HTML file from the 'static' directory.

### Security and Authorization
- **Description**: The application includes basic security measures such as input sanitization to prevent SQL injection. Additionally, certain job listings are restricted to admin users, ensuring that sensitive information is protected.

## Typical Usage or Runtime Scenario

1. **Application Startup**:
   - The FastAPI application is initialized.
   - A SQLite database is set up and populated with predefined job listings, including a hidden job for admin access.
   - The application starts listening for incoming HTTP requests.

2. **User Interaction**:
   - A user sends a POST request to the `/jobs` endpoint with a specific job type.
   - The application retrieves the job listings from the SQLite database based on the provided job type.
   - The job listings are returned to the user, with the hidden job omitted unless the user is an admin.

3. **Health Check**:
   - A client sends a GET request to the `/ping` endpoint.
   - The application responds with a 'pong' message, indicating that it is running and healthy.

4. **Static File Serving**:
   - A client sends a GET request to the root endpoint (`/`).
   - The application serves the root HTML file from the 'static' directory.

## Where to Look Next

- **Endpoints and API Details**: For more detailed information about the HTTP endpoints, including request and response formats, see the [API Reference](api-reference.md) section.
- **Database Schema**: To understand the structure of the SQLite database and the data models used, refer to the [Database Schema](database-schema.md) section.
- **Security Measures**: For a deeper dive into the security measures implemented, including input sanitization and admin access controls, see the [Security](security.md) section.
- **Deployment and Configuration**: To learn how to deploy and configure the application, check the [Deployment](deployment.md) section.

---

# Architecture and Data Flow

## Overview

The application is built using a microservices architecture with FastAPI as the primary framework. It consists of a single FastAPI service that handles HTTP requests, interacts with a SQLite database, and serves static files. The main components of the architecture include:

- **FastAPI Application**: The core of the application, handling HTTP requests and responses.
- **SQLite Database**: A local database used to store job listings.
- **Static File Serving**: Serving static HTML files from a directory.

## Main Architectural Components

### FastAPI Application

The FastAPI application is defined in `app/main.py`. This file sets up the FastAPI instance, defines the endpoints, and initializes the SQLite database. The main components of the FastAPI application are:

- **Endpoints**:
  - **`/jobs`**: A POST endpoint that retrieves job listings based on the job type. It includes basic input sanitization to prevent SQL injection.
  - **`/ping`**: A simple GET endpoint that returns a "pong" response, used for health checks.
  - **`/`**: A GET endpoint that serves the root HTML file from the `static` directory.

- **Database Initialization**:
  - The application initializes a SQLite database and populates it with predefined job entries during startup. Some of these job entries are restricted and can only be accessed by admins.

### SQLite Database

The SQLite database is used to store job listings. The database is initialized and populated with job entries in the `app/main.py` file. The database schema and operations are managed within this file.

### Static File Serving

The application serves static HTML files from the `static` directory. The root HTML file is served by the `/` endpoint.

## Data and Control Flow

### HTTP Request Handling

1. **Client Request**:
   - A client sends an HTTP request to one of the endpoints defined in the FastAPI application.

2. **Endpoint Routing**:
   - The FastAPI application routes the request to the appropriate handler function based on the endpoint and HTTP method.

3. **Database Interaction**:
   - For the `/jobs` endpoint, the handler function queries the SQLite database to retrieve job listings based on the provided job type. The query includes basic input sanitization to prevent SQL injection.
   - For the `/ping` endpoint, the handler function simply returns a "pong" response.
   - For the `/` endpoint, the handler function serves the root HTML file from the `static` directory.

4. **Response Generation**:
   - The handler function generates the appropriate response based on the request and database interaction.
   - The response is then sent back to the client.

### Database Initialization

1. **Application Startup**:
   - When the FastAPI application starts, it triggers a startup event defined in `app/main.py`.

2. **Database Setup**:
   - The startup event initializes the SQLite database and populates it with predefined job entries.
   - Some of these job entries are marked as hidden and can only be accessed by admins.

## Important Patterns

### MVC (Model-View-Controller) Pattern

While the application does not strictly follow the MVC pattern, it does have elements of it:

- **Model**: The SQLite database and the job entries stored within it.
- **View**: The static HTML files served by the `/` endpoint.
- **Controller**: The FastAPI application and its endpoint handlers.

### Layered Architecture

The application follows a layered architecture:

- **Presentation Layer**: The FastAPI application and its endpoints handle HTTP requests and responses.
- **Business Logic Layer**: The endpoint handlers perform the necessary business logic, such as querying the database and sanitizing inputs.
- **Data Access Layer**: The SQLite database and the database initialization logic.

### Event-Driven Architecture

The application uses an event-driven approach for database initialization:

- **Startup Event**: The FastAPI application triggers a startup event to initialize the SQLite database and populate it with job entries.

## Key Files and Functions

- **`app/main.py`**:
  - **Main FastAPI Application**: Sets up the FastAPI instance and defines the endpoints.
  - **Database Initialization**: Initializes the SQLite database and populates it with job entries.
  - **Endpoint Handlers**:
    - **`/jobs`**: Handles job listing queries.
    - **`/ping`**: Handles health check requests.
    - **`/`**: Serves the root HTML file.

By understanding these components and their interactions, you can effectively navigate and maintain the application.

---

# API Endpoints

This section documents the available API endpoints in the application, including their methods, paths, and functionalities. The endpoints are defined in the `main.py` file and are part of a FastAPI application.

## Overview

The application provides the following endpoints:

- **Job Listings**: Retrieve job listings based on job type.
- **Health Check**: A simple endpoint to check the application's health.
- **Static File Serving**: Serve the root HTML file from the `static` directory.

## Job Listings Endpoint

### Path: `/jobs`

- **Method**: POST
- **Description**: This endpoint allows you to retrieve job listings based on the specified job type. It includes basic input sanitization to prevent SQL injection.
- **Request Body**:
  - `job_type` (string): The type of job to filter by.
- **Response**:
  - A JSON object containing a list of job listings that match the specified job type.
- **Example**:
  ```http
  POST /jobs
  Content-Type: application/json

  {
    "job_type": "software_engineer"
  }
  ```

  **Response**:
  ```json
  {
    "jobs": [
      {
        "id": 1,
        "title": "Software Engineer",
        "company": "TechCorp",
        "location": "San Francisco",
        "description": "We are looking for a talented software engineer to join our team."
      },
      {
        "id": 2,
        "title": "Software Engineer",
        "company": "InnovateTech",
        "location": "New York",
        "description": "Join our innovative team as a software engineer."
      }
    ]
  }
  ```

## Health Check Endpoint

### Path: `/ping`

- **Method**: GET
- **Description**: This is a simple health check endpoint that returns a `pong` response to indicate that the application is running.
- **Response**:
  - A JSON object with a `message` field containing the string `pong`.
- **Example**:
  ```http
  GET /ping
  ```

  **Response**:
  ```json
  {
    "message": "pong"
  }
  ```

## Static File Serving Endpoint

### Path: `/`

- **Method**: GET
- **Description**: This endpoint serves the root HTML file from the `static` directory. It is used to serve the main application interface.
- **Response**:
  - The content of the `index.html` file located in the `static` directory.
- **Example**:
  ```http
  GET /
  ```

  **Response**:
  - The HTML content of the `index.html` file.

## Database Initialization

During the application startup, the SQLite database is initialized and populated with predefined job listings. Some of these job listings are marked as hidden and can only be accessed by users with admin permissions. This initialization is handled in the `main.py` file.

## Security Considerations

- **Input Sanitization**: The `/jobs` endpoint includes basic input sanitization to prevent SQL injection attacks.
- **Admin-Only Jobs**: Some job listings are marked as hidden and can only be accessed by users with admin permissions. This is managed within the database and the application logic.

## File and Directory Structure

- **File**: `XBEN-006-24\app\main.py`
  - Contains the FastAPI application setup, endpoint definitions, and database initialization logic.
- **Directory**: `static`
  - Contains the `index.html` file served by the root endpoint.

By following this documentation, you can understand and interact with the available API endpoints in the application.

---

# Database Structure

This section provides details about the SQLite database used in the application, including its schema and initialization processes.

## Database Initialization

The SQLite database is initialized in the `main.py` file. During the application startup, the database is populated with predefined job entries. This initialization process ensures that the database has some initial data to work with, including a hidden job that can only be accessed by admins.

### Initialization Process

1. **Application Startup**:
   - The FastAPI application is initialized in `main.py`.
   - A startup event is defined to populate the database with job listings.

2. **Database Population**:
   - The `main.py` file contains a function that runs on application startup to insert predefined job entries into the database.
   - This function ensures that the database has a set of initial job listings, including a hidden job that is only accessible to admin users.

## Database Schema

The SQLite database schema is not explicitly defined in a separate schema file, but it is inferred from the operations performed in `main.py`. The schema includes a table for job listings, which likely has the following columns:

- **id**: A unique identifier for each job listing.
- **title**: The title of the job.
- **description**: A detailed description of the job.
- **type**: The type of job (e.g., full-time, part-time).
- **is_hidden**: A boolean flag indicating whether the job is hidden and accessible only to admin users.

### Example Schema

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL,
    is_hidden BOOLEAN DEFAULT FALSE
);
```

## Database Interactions

The application interacts with the SQLite database through the following endpoints:

### Job Listing Endpoint

- **Endpoint**: `/jobs`
- **Method**: POST
- **Description**: This endpoint retrieves job listings based on the job type. It includes basic input sanitization to prevent SQL injection.
- **File**: `main.py`

### Health Check Endpoint

- **Endpoint**: `/ping`
- **Method**: GET
- **Description**: A simple health check endpoint that returns a 'pong' response.
- **File**: `main.py`

### Root HTML File Endpoint

- **Endpoint**: `/`
- **Method**: GET
- **Description**: Serves the root HTML file from the `static` directory.
- **File**: `main.py`

## Security Considerations

- **Input Sanitization**: The `/jobs` endpoint includes basic input sanitization to prevent SQL injection attacks.
- **Hidden Jobs**: The database contains a hidden job that can only be accessed by admin users. This is managed through the `is_hidden` flag in the job listings table.

## Conclusion

The SQLite database in this application is initialized and populated with job listings during the application startup. The schema is inferred from the operations in `main.py`, and the database interactions are managed through the defined endpoints. Security measures, such as input sanitization and hidden job access, are implemented to ensure the integrity and security of the data.

---

# Security Measures

This section outlines the security measures implemented in the `XBEN-006-24` project, focusing on input sanitization and restricted access to certain data.

## Input Sanitization

### Job Listing Endpoint
- **File:** `XBEN-006-24\app\main.py`
- **Endpoint:** `/jobs` (POST)
- **Details:** The `/jobs` endpoint is designed to retrieve job listings based on the job type provided in the request. To prevent SQL injection, the endpoint includes basic input sanitization. This ensures that any user-provided input is cleaned and validated before it is used in database queries.

## Restricted Access

### Admin-Only Job Listings
- **File:** `XBEN-006-24\app\main.py`
- **Details:** The application initializes a SQLite database with predefined job entries, including a hidden job that can only be accessed by admins. This is achieved by setting up specific permissions and access controls within the database and the application logic.

### Health Check Endpoint
- **File:** `XBEN-006-24\app\main.py`
- **Endpoint:** `/ping` (GET)
- **Details:** The `/ping` endpoint is a simple health check that returns a `pong` response. This endpoint does not require any authentication and is publicly accessible to ensure the application is running correctly.

### Root HTML File
- **File:** `XBEN-006-24\app\main.py`
- **Endpoint:** `/` (GET)
- **Details:** The root endpoint serves the main HTML file from the `static` directory. This endpoint is also publicly accessible and does not require any authentication.

## Database Initialization and Security

### Database Setup
- **File:** `XBEN-006-24\app\main.py`
- **Details:** The application initializes a SQLite database during startup. This initialization includes populating the database with predefined job listings, some of which are marked as hidden and accessible only by admins. The database setup ensures that sensitive data is properly managed and restricted.

### Startup Event
- **File:** `XBEN-006-24\app\main.py`
- **Details:** A startup event is defined to populate the database with job listings. This event ensures that the database is properly initialized with the necessary data, including the hidden jobs that require admin access.

## Summary

The `XBEN-006-24` project implements several security measures to protect against common vulnerabilities:
- **Input Sanitization:** The `/jobs` endpoint includes basic input sanitization to prevent SQL injection.
- **Restricted Access:** Certain job listings are marked as hidden and can only be accessed by admins, ensuring that sensitive data is protected.
- **Database Security:** The database is initialized with predefined job listings, and access controls are set to restrict access to sensitive data.

By following these security practices, the application ensures that user input is handled safely and that sensitive data is properly managed and restricted.

---