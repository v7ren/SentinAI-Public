# Overview

## What the Project Is and What Problem It Solves

This project is a company management system built using FastAPI, SQLAlchemy, and Pydantic. It provides a web application for managing companies and job listings. The primary problems it solves include:

- **User Authentication and Authorization**: Securely managing user sessions and permissions.
- **Data Management**: Efficiently storing and retrieving company and job information.
- **API Endpoints**: Providing a RESTful API for interacting with the application.

## Main Components or Modules

### 1. **Database Management (`app/database.py`)**

- **Session Management**: Sets up the database connection and session management using SQLAlchemy for a SQLite database.
- **Key Entities**:
  - `SessionLocal`: A session factory for creating database sessions.
  - `Base`: Base class for declarative ORM models.

### 2. **Data Validation and Serialization (`app/schemas.py`)**

- **Pydantic Models**: Defines Pydantic models for data validation and serialization.
- **Key Models**:
  - `Token`, `TokenData`: Models for authentication tokens.
  - `CompanyBase`, `CompanyCreate`, `Company`: Models for company information.
  - `JobBase`, `JobCreate`, `Job`: Models for job listings.

### 3. **ORM Models (`app/models.py`)**

- **SQLAlchemy ORM Models**: Defines SQLAlchemy ORM models for the database.
- **Key Models**:
  - `Company`: Represents a company entity with fields like `id`, `name`, `hashed_password`, and `is_admin`.
  - `Job`: Represents a job listing entity with fields like `id`, `title`, `description`, `company_id`, and `is_private`.

### 4. **CRUD Operations (`app/crud.py`)**

- **Database Operations**: Contains functions for creating, retrieving, updating, and deleting companies and jobs.
- **Key Functions**:
  - `get_company`, `get_company_by_name`: Retrieve companies by ID or name.
  - `create_company`: Create a new company with a hashed password.
  - `create_job`: Create a new job associated with a company.
  - `get_jobs`: Retrieve jobs for a specific company, optionally including private jobs.
  - `delete_all`: Delete all jobs and companies from the database.

### 5. **FastAPI Application (`app/main.py`)**

- **Application Setup**: Sets up a FastAPI application with routes for authentication, job listing, and profile editing.
- **Key Endpoints**:
  - `login`: Renders the login page.
  - `login_for_access_token`: Handles the login form submission and returns an access token.
  - `show_jobs`: Displays a list of jobs for a specific company, with optional private job listings for admin users.
  - `ping`: A simple health check endpoint.
  - `edit_profile`: Renders the profile editing page for a company.
  - `update_profile`: Handles the form submission for updating a company's profile.

## Typical Usage or Runtime Scenario

1. **User Authentication**:
   - A user navigates to the login page (`/`).
   - The user submits their credentials via the login form.
   - The `login_for_access_token` endpoint processes the credentials, verifies them, and returns an access token.

2. **Job Listing**:
   - An authenticated user (e.g., a company admin) navigates to the job listing page (`/company/{company_id}/jobs`).
   - The `show_jobs` endpoint retrieves the list of jobs for the specified company, including private jobs if the user is an admin.

3. **Profile Editing**:
   - An authenticated user navigates to the profile editing page (`/edit_profile/{company_id}`).
   - The user updates their company profile and submits the form.
   - The `update_profile` endpoint processes the form data and updates the company's information in the database.

## Where to Look Next

- **Database Management**: For more details on how the database is set up and managed, see the [Database Management](#database-management) section.
- **Data Validation and Serialization**: For more details on the Pydantic models used for data validation and serialization, see the [Data Validation and Serialization](#data-validation-and-serialization) section.
- **ORM Models**: For more details on the SQLAlchemy ORM models, see the [ORM Models](#orm-models) section.
- **CRUD Operations**: For more details on the CRUD operations, see the [CRUD Operations](#crud-operations) section.
- **FastAPI Application**: For more details on the FastAPI application and its endpoints, see the [FastAPI Application](#fastapi-application) section.