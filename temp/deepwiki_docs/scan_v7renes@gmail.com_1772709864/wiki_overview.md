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