# API Endpoints

This section provides a reference guide to the available API endpoints, including their methods, paths, and functionalities. The endpoints are part of a FastAPI application that manages company and job data, with authentication and database interactions.

## Authentication

### Login
- **Method**: GET
- **Path**: `/`
- **Description**: Renders the login page.
- **File**: `app/main.py`

### Login for Access Token
- **Method**: POST
- **Path**: `/token`
- **Description**: Handles the login form submission and returns a JWT token upon successful authentication.
- **File**: `app/main.py`

## Job Listings

### Show Jobs
- **Method**: GET
- **Path**: `/company/{company_id}/jobs`
- **Description**: Displays a list of jobs for a specific company. Admin users can optionally view private jobs.
- **File**: `app/main.py`

## Company Profile Management

### Edit Profile
- **Method**: GET
- **Path**: `/edit_profile/{company_id}`
- **Description**: Renders the edit profile page for a company.
- **File**: `app/main.py`

### Update Profile
- **Method**: POST
- **Path**: `/edit_profile/{company_id}`
- **Description**: Handles the form submission to update a company's profile.
- **File**: `app/main.py`

## Health Check

### Ping
- **Method**: GET
- **Path**: `/ping`
- **Description**: A simple health check endpoint that returns a 'pong' response.
- **File**: `app/main.py`

## Endpoint Interactions

### Authentication Flow
1. **Login Page**: The user navigates to the login page by accessing the `/` endpoint.
2. **Login Form Submission**: The user submits the login form, which triggers the `/token` endpoint. This endpoint validates the credentials, generates a JWT token, and returns it to the user.
3. **Token Usage**: The JWT token is used to authenticate subsequent requests to protected endpoints.

### Job Listing Flow
1. **Access Job List**: The user accesses the `/company/{company_id}/jobs` endpoint to view a list of jobs for a specific company.
2. **Admin Access**: If the user is an admin, they can view private jobs by including the appropriate query parameter.

### Company Profile Management Flow
1. **Edit Profile Page**: The user navigates to the `/edit_profile/{company_id}` endpoint to view the edit profile page for a specific company.
2. **Update Profile**: The user submits the form to update the company's profile, which triggers the `/edit_profile/{company_id}` endpoint. The endpoint validates the input, updates the company's data in the database, and returns a success response.

### Health Check Flow
1. **Ping Request**: The user or a monitoring system sends a GET request to the `/ping` endpoint.
2. **Pong Response**: The endpoint returns a 'pong' response, indicating that the application is running and responsive.

## Key Files and Functions

### `app/main.py`
- **Main Application Setup**: Sets up the FastAPI application and defines the routes.
- **Authentication**: Handles user authentication and token generation.
- **Job Listings**: Manages the retrieval and display of job listings.
- **Company Profile Management**: Handles the editing and updating of company profiles.
- **Health Check**: Provides a simple health check endpoint.

### `app/database.py`
- **Database Connection**: Sets up the database connection using SQLAlchemy.
- **Session Management**: Defines the session factory and base class for declarative models.

### `app/models.py`
- **ORM Models**: Defines SQLAlchemy ORM models for `Company` and `Job`.
- **Relationships**: Establishes a one-to-many relationship between `Company` and `Job`.

### `app/crud.py`
- **CRUD Operations**: Contains functions for creating, retrieving, and deleting companies and jobs.
- **Password Hashing**: Includes password hashing for company creation.

### `app/schemas.py`
- **Pydantic Models**: Defines Pydantic models for data validation and serialization.
- **Token Models**: Includes models for representing authentication tokens.
- **Company and Job Models**: Defines models for company and job data, with ORM mode enabled for database interactions.

By understanding these endpoints and their interactions, you can effectively use the API to manage company and job data in the application.