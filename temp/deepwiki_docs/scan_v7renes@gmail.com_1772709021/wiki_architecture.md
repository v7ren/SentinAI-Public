# Architecture and Data Flow

This section provides an overview of the main architectural components of the application, how data and control flow between them, and the important patterns used in the design.

## Main Architectural Components

### 1. **FastAPI Application (main.py)**
- **Role**: The entry point of the application, responsible for setting up the FastAPI server and defining the endpoints.
- **Key Functions**:
  - `login_for_access_token`: Handles user authentication and token generation.
  - `show_jobs`: Displays job listings for a specific company.
  - `edit_profile` and `update_profile`: Handle rendering and updating a company's profile.
  - `ping`: A simple health check endpoint.

### 2. **Database Management (database.py)**
- **Role**: Manages the database connection and session management using SQLAlchemy.
- **Key Entities**:
  - `SessionLocal`: A session factory for creating database sessions.
  - `Base`: The base class for declarative models.

### 3. **ORM Models (models.py)**
- **Role**: Defines the SQLAlchemy ORM models for the database schema.
- **Key Models**:
  - `Company`: Represents a company with fields like `id`, `name`, `hashed_password`, and `is_admin`. It has a one-to-many relationship with the `Job` model.
  - `Job`: Represents a job listing with fields like `id`, `title`, `description`, `company_id`, and `is_private`. It has a relationship back to the `Company` model.

### 4. **Data Validation and Serialization (schemas.py)**
- **Role**: Defines Pydantic models for data validation and serialization.
- **Key Models**:
  - `Token`, `TokenData`: Models for handling authentication tokens.
  - `CompanyBase`, `CompanyCreate`, `Company`: Models for company data.
  - `JobBase`, `JobCreate`, `Job`: Models for job listings.

### 5. **CRUD Operations (crud.py)**
- **Role**: Contains functions for creating, retrieving, updating, and deleting (CRUD) operations on the `Company` and `Job` models.
- **Key Functions**:
  - `get_company`: Retrieves a company by its ID.
  - `get_company_by_name`: Retrieves a company by its name.
  - `create_company`: Creates a new company with a hashed password.
  - `create_job`: Creates a new job for a specific company.
  - `get_jobs`: Retrieves jobs for a specific company, optionally including private jobs.
  - `delete_all`: Deletes all jobs and companies from the database.

## Data and Control Flow

### 1. **User Authentication and Token Generation**
- **Flow**:
  - The user sends a POST request to the `/token` endpoint in `main.py`.
  - The `login_for_access_token` function handles the request, validates the user credentials, and generates a JWT token.
  - The token is then used for subsequent authenticated requests.

### 2. **Job Listings and Company Profiles**
- **Flow**:
  - A user or company sends a GET request to the `/company/{company_id}/jobs` endpoint in `main.py`.
  - The `show_jobs` function retrieves the company by ID using the `get_company` function from `crud.py`.
  - It then fetches the jobs for that company using the `get_jobs` function from `crud.py`.
  - The job data is serialized using the `Job` Pydantic model from `schemas.py` and returned as a response.

### 3. **Profile Editing**
- **Flow**:
  - A company sends a GET request to the `/edit_profile/{company_id}` endpoint in `main.py`.
  - The `edit_profile` function retrieves the company by ID using the `get_company` function from `crud.py`.
  - The company data is serialized using the `Company` Pydantic model from `schemas.py` and rendered in the profile editing page.
  - When the company submits the updated profile, a POST request is sent to the `/edit_profile/{company_id}` endpoint.
  - The `update_profile` function updates the company's profile in the database using the `create_company` function from `crud.py`.

### 4. **Database Operations**
- **Flow**:
  - The `SessionLocal` session factory from `database.py` is used to create database sessions.
  - The `Base` class from `database.py` is used to define the declarative models in `models.py`.
  - CRUD operations in `crud.py` use these sessions to interact with the database, performing operations like querying, inserting, and deleting records.

## Important Patterns

### 1. **Model-View-Controller (MVC)**
- **Description**: The application follows a variant of the MVC pattern.
  - **Model**: Defined in `models.py` and `schemas.py`, these classes represent the data structure and validation.
  - **View**: Handled by the FastAPI endpoints in `main.py`, which render responses and handle user interactions.
  - **Controller**: Implemented in `crud.py`, these functions manage the business logic and database operations.

### 2. **Layered Architecture**
- **Description**: The application is structured in layers to separate concerns.
  - **Presentation Layer**: FastAPI endpoints in `main.py` handle HTTP requests and responses.
  - **Business Logic Layer**: Functions in `crud.py` manage the application's core logic.
  - **Data Access Layer**: SQLAlchemy models in `models.py` and session management in `database.py` handle database interactions.

### 3. **Event-Driven Authentication**
- **Description**: The application uses JWT tokens for authentication.
  - **Token Generation**: The `login_for_access_token` function in `main.py` generates a JWT token upon successful login.
  - **Token Validation**: Subsequent requests include the token, which is validated to ensure the user is authenticated.

## Conclusion

The architecture of the application is designed to be modular and maintainable, with clear separation of concerns. The use of FastAPI, SQLAlchemy, and Pydantic ensures a robust and efficient system for managing company and job data. The MVC pattern and layered architecture contribute to the application's scalability and ease of maintenance.