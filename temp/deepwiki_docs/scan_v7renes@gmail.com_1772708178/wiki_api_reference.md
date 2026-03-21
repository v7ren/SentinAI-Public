# API Reference

This section provides detailed documentation of the API endpoints, including authentication, job listing, and profile editing. Each endpoint is described with its method, path, and a brief explanation of its functionality.

## Authentication

### Login
- **Method**: GET
- **Path**: `/`
- **Description**: Renders the login page where users can enter their credentials.

### Login for Access Token
- **Method**: POST
- **Path**: `/token`
- **Description**: Handles the login form submission and returns an access token. This endpoint is used to authenticate users and generate a JWT token for subsequent requests.
- **Request Body**:
  - `username`: The username of the company.
  - `password`: The password of the company.
- **Response**:
  - `access_token`: The JWT token for authenticated requests.
  - `token_type`: The type of token, typically "bearer".

## Job Listing

### Show Jobs
- **Method**: GET
- **Path**: `/company/{company_id}/jobs`
- **Description**: Displays a list of jobs for a specific company. Admin users can optionally view private job listings.
- **Path Parameters**:
  - `company_id`: The ID of the company.
- **Query Parameters**:
  - `include_private`: A boolean flag to include private jobs (default: `false`).
- **Response**:
  - A list of job objects, each containing:
    - `id`: The ID of the job.
    - `title`: The title of the job.
    - `description`: The description of the job.
    - `is_private`: A boolean indicating if the job is private.

## Profile Editing

### Edit Profile
- **Method**: GET
- **Path**: `/edit_profile/{company_id}`
- **Description**: Renders the profile editing page for a company. This page allows companies to update their profile information.
- **Path Parameters**:
  - `company_id`: The ID of the company.

### Update Profile
- **Method**: POST
- **Path**: `/edit_profile/{company_id}`
- **Description**: Handles the form submission for updating a company's profile. This endpoint updates the company's information in the database.
- **Path Parameters**:
  - `company_id`: The ID of the company.
- **Request Body**:
  - `name`: The new name of the company.
  - `hashed_password`: The new hashed password of the company.
- **Response**:
  - A success message indicating that the profile has been updated.

## Health Check

### Ping
- **Method**: GET
- **Path**: `/ping`
- **Description**: A simple health check endpoint that returns a 'pong' response to indicate that the server is running.
- **Response**:
  - `message`: "pong"

## Internal Functions and Models

### Database Setup
- **File**: `app/database.py`
- **Description**: Sets up the database connection and session management using SQLAlchemy for a SQLite database.
- **Key Entities**:
  - `SessionLocal`: A session factory for creating database sessions.
  - `Base`: Base class for declarative ORM models.

### Pydantic Models
- **File**: `app/schemas.py`
- **Description**: Defines Pydantic models for data validation and serialization.
- **Key Models**:
  - `Token`: Model for authentication tokens.
  - `TokenData`: Model for token data.
  - `CompanyBase`: Base model for company information.
  - `CompanyCreate`: Model for creating new companies.
  - `Company`: Model for company information.
  - `JobBase`: Base model for job listings.
  - `JobCreate`: Model for creating new job listings.
  - `Job`: Model for job listings.

### SQLAlchemy ORM Models
- **File**: `app/models.py`
- **Description**: Defines SQLAlchemy ORM models for the 'Company' and 'Job' entities.
- **Key Models**:
  - `Company`: ORM model for the 'companies' table, representing a company entity.
  - `Job`: ORM model for the 'jobs' table, representing a job listing entity.

### CRUD Operations
- **File**: `app/crud.py`
- **Description**: Contains functions for creating, retrieving, and deleting companies and jobs using SQLAlchemy ORM.
- **Key Functions**:
  - `get_company`: Retrieves a company by its ID.
  - `get_company_by_name`: Retrieves a company by its name.
  - `create_company`: Creates a new company with a hashed password.
  - `create_job`: Creates a new job associated with a company.
  - `get_jobs`: Retrieves jobs for a specific company, optionally including private jobs.
  - `delete_all`: Deletes all jobs and companies from the database.

### FastAPI Application
- **File**: `app/main.py`
- **Description**: Sets up a FastAPI application for a company management system, including routes for authentication, job listing, and profile editing.
- **Key Endpoints**:
  - `login`: Renders the login page.
  - `login_for_access_token`: Handles the login form submission and returns an access token.
  - `show_jobs`: Displays a list of jobs for a specific company.
  - `ping`: A simple health check endpoint.
  - `edit_profile`: Renders the profile editing page.
  - `update_profile`: Handles the form submission for updating a company's profile.

This API reference provides a comprehensive overview of the available endpoints and their functionalities, helping developers understand and integrate with the company management system effectively.