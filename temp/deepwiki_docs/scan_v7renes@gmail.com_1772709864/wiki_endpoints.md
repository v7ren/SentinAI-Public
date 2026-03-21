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