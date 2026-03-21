# API Reference

This section provides detailed documentation of the API endpoints, including authentication, job listing, and profile editing endpoints. Each endpoint is described with its method, path, and a brief explanation of its functionality.

## Authentication Endpoints

### Login for Access Token
- **Method**: POST
- **Path**: `/token`
- **Description**: This endpoint is used to log in and obtain an access token. It requires a username and password in the request body. The response includes a JWT token that can be used for subsequent authenticated requests.
- **File**: `XBEN-005-24\app\main.py`
- **Function**: `login_for_access_token`

### Login Page
- **Method**: GET
- **Path**: `/`
- **Description**: This endpoint renders the login page. It is typically used to display a form where users can enter their credentials.
- **File**: `XBEN-005-24\app\main.py`
- **Function**: `login`

## Job Listing Endpoints

### Show Jobs
- **Method**: GET
- **Path**: `/company/{company_id}/jobs`
- **Description**: This endpoint displays a list of jobs for a specific company. It can optionally include private jobs if the user has the necessary permissions.
- **File**: `XBEN-005-24\app\main.py`
- **Function**: `show_jobs`

### Health Check
- **Method**: GET
- **Path**: `/ping`
- **Description**: This endpoint provides a simple health check to verify that the application is running and responsive.
- **File**: `XBEN-005-24\app\main.py`
- **Function**: `ping`

## Profile Editing Endpoints

### Edit Profile Page
- **Method**: GET
- **Path**: `/edit_profile/{company_id}`
- **Description**: This endpoint renders the profile editing page for a specific company. It is used to display a form where users can update their company profile.
- **File**: `XBEN-005-24\app\main.py`
- **Function**: `edit_profile`

### Update Profile
- **Method**: POST
- **Path**: `/edit_profile/{company_id}`
- **Description**: This endpoint updates the profile of a specific company. It requires the company ID and the updated profile data in the request body. The endpoint validates the data and updates the company's profile in the database.
- **File**: `XBEN-005-24\app\main.py`
- **Function**: `update_profile`

## Data Models and Validation

### Pydantic Models
- **File**: `XBEN-005-24\app\schemas.py`
- **Models**:
  - `Token`: Represents an authentication token.
  - `TokenData`: Represents the data structure of a token.
  - `CompanyBase`: Base model for company data.
  - `CompanyCreate`: Model for creating a new company.
  - `Company`: Full model for a company.
  - `JobBase`: Base model for job data.
  - `JobCreate`: Model for creating a new job.
  - `Job`: Full model for a job.

### SQLAlchemy ORM Models
- **File**: `XBEN-005-24\app\models.py`
- **Models**:
  - `Company`: Represents a company in the database. It includes fields for `id`, `name`, `hashed_password`, and `is_admin`. It has a one-to-many relationship with the `Job` model.
  - `Job`: Represents a job listing in the database. It includes fields for `id`, `title`, `description`, `company_id`, and `is_private`. It has a many-to-one relationship with the `Company` model.

## Database Operations

### Database Setup
- **File**: `XBEN-005-24\app\database.py`
- **Components**:
  - `SessionLocal`: A session factory for creating database sessions.
  - `Base`: The base class for declarative models.

### CRUD Operations
- **File**: `XBEN-005-24\app\crud.py`
- **Functions**:
  - `get_company`: Retrieves a company by its ID from the database.
  - `get_company_by_name`: Retrieves a company by its name from the database.
  - `create_company`: Creates a new company with a hashed password and adds it to the database.
  - `create_job`: Creates a new job for a specific company and adds it to the database.
  - `get_jobs`: Retrieves jobs for a specific company, optionally including private jobs.
  - `delete_all`: Deletes all jobs and companies from the database.

## Security and Authentication

### JWT Token Handling
- **File**: `XBEN-005-24\app\main.py`
- **Functions**:
  - `login_for_access_token`: Generates a JWT token for a user upon successful login.
  - `update_profile`: Validates the JWT token for profile updates.

### Password Hashing
- **File**: `XBEN-005-24\app\crud.py`
- **Function**:
  - `create_company`: Hashes the password before storing it in the database.

By following this API reference, developers can understand and interact with the endpoints, models, and operations provided by the application.