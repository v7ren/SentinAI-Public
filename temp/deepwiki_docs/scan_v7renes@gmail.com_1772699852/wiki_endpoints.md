# API Endpoints

This section provides a detailed list and description of the available API endpoints for interacting with the system. These endpoints are part of a FastAPI application and are used for managing company profiles and job listings, as well as handling authentication and profile editing.

## Authentication Endpoints

### POST /token
- **Description**: Handles the login process and returns an access token upon successful authentication.
- **Request Body**: 
  - `username` (string): The company name.
  - `password` (string): The company password.
- **Response**:
  - `access_token` (string): The JWT token for authenticated requests.
  - `token_type` (string): The type of token, typically "bearer".
- **Example**:
  ```json
  {
    "username": "example_company",
    "password": "securepassword"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    "token_type": "bearer"
  }
  ```

### GET /
- **Description**: Renders the login page.
- **Response**: HTML content for the login page.

## Job Listing Endpoints

### GET /company/{company_id}/jobs
- **Description**: Displays job listings for a specific company. Admin users can optionally view private job listings.
- **Path Parameters**:
  - `company_id` (integer): The ID of the company.
- **Query Parameters**:
  - `include_private` (boolean, optional): If true, includes private job listings.
- **Response**: A list of job listings.
- **Example**:
  ```json
  {
    "jobs": [
      {
        "id": 1,
        "title": "Software Engineer",
        "description": "We are looking for a talented software engineer.",
        "company_id": 1,
        "is_private": false
      },
      {
        "id": 2,
        "title": "Data Scientist",
        "description": "We need a data scientist to join our team.",
        "company_id": 1,
        "is_private": true
      }
    ]
  }
  ```

## Health Check Endpoint

### GET /ping
- **Description**: A simple health check endpoint that returns a 'pong' response.
- **Response**:
  ```json
  {
    "message": "pong"
  }
  ```

## Profile Management Endpoints

### GET /edit_profile/{company_id}
- **Description**: Renders the profile editing page for a specific company.
- **Path Parameters**:
  - `company_id` (integer): The ID of the company.
- **Response**: HTML content for the profile editing page.

### POST /edit_profile/{company_id}
- **Description**: Handles the update of a company's profile information.
- **Path Parameters**:
  - `company_id` (integer): The ID of the company.
- **Request Body**:
  - `name` (string): The new company name.
  - `admin` (boolean): The new admin status.
- **Response**: A success message or an error message.
- **Example**:
  ```json
  {
    "name": "Updated Company Name",
    "admin": true
  }
  ```
- **Response**:
  ```json
  {
    "message": "Profile updated successfully"
  }
  ```

## Summary

The API endpoints provided in this section enable various operations such as authentication, job listing management, and company profile editing. These endpoints are crucial for the functionality of the application and are built using FastAPI, SQLAlchemy for database operations, and JWT for authentication. Each endpoint is designed to handle specific tasks and ensure secure and efficient interactions with the system.