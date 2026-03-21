# Security

This section provides an overview of the security measures implemented in the application, focusing on JWT authentication and password hashing.

## JWT Authentication

The application uses JSON Web Tokens (JWT) for authentication. JWTs are a secure way to authenticate users and manage sessions without storing session data on the server. The following components are involved in the JWT authentication process:

### Token Models

- **File:** `app/schemas.py`
- **Models:**
  - `Token`: Represents the access token.
  - `TokenData`: Represents the data structure of the token, including the username.

These models are used to validate and serialize token data in the application.

### Authentication Endpoints

- **File:** `app/main.py`
- **Endpoints:**
  - `login_for_access_token` (POST `/token`): This endpoint handles user login and returns an access token. It validates the user's credentials and generates a JWT token.
  - `login` (GET `/`): This endpoint renders the login page.

### Token Generation and Validation

- **File:** `app/main.py`
- **Functions:**
  - `create_access_token`: Generates a JWT token for a given user.
  - `get_current_user`: Validates the JWT token and retrieves the current user.

These functions are used to create and validate JWT tokens, ensuring that only authenticated users can access protected endpoints.

## Password Hashing

Password hashing is a critical security measure to protect user credentials. The application uses a secure hashing algorithm to store and verify passwords.

### Password Hashing in CRUD Operations

- **File:** `app/crud.py`
- **Functions:**
  - `create_company`: This function creates a new company and hashes the provided password before storing it in the database.

### Company Model

- **File:** `app/models.py`
- **Model:**
  - `Company`: This SQLAlchemy ORM model includes a `hashed_password` field to store the hashed password.

### Example Flow

1. **User Registration:**
   - The user submits a registration form with their username and password.
   - The `create_company` function in `app/crud.py` hashes the password using a secure hashing algorithm.
   - The hashed password is stored in the `Company` model in the database.

2. **User Login:**
   - The user submits their username and password to the `login_for_access_token` endpoint.
   - The endpoint verifies the password by comparing the hashed password stored in the database with the hashed version of the provided password.
   - If the passwords match, a JWT token is generated and returned to the user.

3. **Accessing Protected Endpoints:**
   - The user includes the JWT token in the `Authorization` header of subsequent requests.
   - The `get_current_user` function in `app/main.py` validates the token and retrieves the user's information.
   - If the token is valid, the user is allowed to access the protected endpoint.

## Database Security

The application uses SQLAlchemy for database operations, ensuring that all interactions with the database are secure and efficient.

### Database Connection

- **File:** `app/database.py`
- **Components:**
  - `SessionLocal`: A session factory for creating database sessions.
  - `Base`: The base class for declarative models.

### ORM Models

- **File:** `app/models.py`
- **Models:**
  - `Company`: Represents a company in the database, including fields for `id`, `name`, `hashed_password`, and `is_admin`.
  - `Job`: Represents a job listing in the database, including fields for `id`, `title`, `description`, `company_id`, and `is_private`.

### CRUD Operations

- **File:** `app/crud.py`
- **Functions:**
  - `get_company`: Retrieves a company by its ID.
  - `get_company_by_name`: Retrieves a company by its name.
  - `create_company`: Creates a new company with a hashed password.
  - `create_job`: Creates a new job for a specific company.
  - `get_jobs`: Retrieves jobs for a specific company, optionally including private jobs.
  - `delete_all`: Deletes all jobs and companies from the database.

These functions ensure that all database operations are performed securely and efficiently, maintaining the integrity and confidentiality of the data.

## Summary

The application implements robust security measures, including JWT authentication and password hashing, to protect user data and ensure secure access to protected endpoints. The use of SQLAlchemy for database operations further enhances the security and reliability of the application.