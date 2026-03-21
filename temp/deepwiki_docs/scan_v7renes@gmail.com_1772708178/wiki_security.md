# Security

This section provides an overview of the security measures in place within the application, focusing on authentication, authorization, and data protection.

## Authentication

### JWT Tokens
The application uses JSON Web Tokens (JWT) for authentication. JWT tokens are generated and validated to ensure secure access to protected routes.

- **Token Generation**: The `login_for_access_token` endpoint in `app/main.py` handles the login form submission and returns an access token upon successful authentication.
- **Token Validation**: JWT tokens are validated in the `app/main.py` file to ensure that only authenticated users can access certain routes.

### Password Hashing
To protect user passwords, the application hashes passwords before storing them in the database. This is handled in the `create_company` function in `app/crud.py`.

- **Password Hashing**: The `create_company` function hashes the provided password using a secure hashing algorithm before storing it in the database.

## Authorization

### Role-Based Access Control (RBAC)
The application implements role-based access control to manage user permissions. The `Company` model in `app/models.py` includes an `is_admin` field to distinguish between regular users and administrators.

- **Admin Access**: Admin users have additional permissions, such as viewing private job listings. This is enforced in the `show_jobs` endpoint in `app/main.py`, where the `is_private` parameter is used to filter job listings based on the user's role.

### Endpoint Protection
Several endpoints in `app/main.py` are protected to ensure that only authenticated users can access them.

- **Protected Endpoints**:
  - `show_jobs`: Displays a list of jobs for a specific company, with optional private job listings for admin users.
  - `edit_profile`: Renders the profile editing page for a company.
  - `update_profile`: Handles the form submission for updating a company's profile.

## Data Protection

### Database Security
The application uses SQLAlchemy to manage database connections and sessions, ensuring that data is securely stored and queried.

- **Database Connection**: The `app/database.py` file sets up the database connection and session management using SQLAlchemy.
- **Session Management**: The `SessionLocal` factory in `app/database.py` is used to create database sessions, ensuring that each request has a separate and isolated session.

### Data Validation
Pydantic models in `app/schemas.py` are used to validate and serialize data, ensuring that only valid and expected data is processed.

- **Pydantic Models**: Models such as `Token`, `TokenData`, `CompanyBase`, `CompanyCreate`, `Company`, `JobBase`, `JobCreate`, and `Job` are defined to validate and serialize data for API requests and responses.

### Data Encryption
Sensitive data, such as passwords, are hashed and stored securely in the database. The `Company` model in `app/models.py` includes a `hashed_password` field to store the hashed password.

- **Password Storage**: The `hashed_password` field in the `Company` model ensures that passwords are stored securely and cannot be easily accessed or read.

## Security Flows

### Authentication Flow
1. **User Login**: The user submits a login form, which is handled by the `login_for_access_token` endpoint in `app/main.py`.
2. **Token Generation**: Upon successful authentication, a JWT token is generated and returned to the user.
3. **Token Storage**: The user stores the JWT token securely, such as in a browser's local storage or a secure cookie.
4. **Token Validation**: The user includes the JWT token in subsequent requests to protected endpoints, which are validated to ensure the user is authenticated.

### Authorization Flow
1. **Access Request**: The user makes a request to a protected endpoint, such as `show_jobs` or `edit_profile`.
2. **Token Validation**: The JWT token is extracted from the request and validated.
3. **Role Check**: The user's role is checked to determine if they have the necessary permissions to access the requested resource.
4. **Resource Access**: If the user is authorized, the requested resource is returned; otherwise, an access denied response is returned.

### Data Protection Flow
1. **Data Submission**: The user submits data, such as creating a new company or job listing.
2. **Data Validation**: The data is validated using Pydantic models defined in `app/schemas.py`.
3. **Data Storage**: Validated data is stored in the database, with sensitive data (e.g., passwords) being hashed and stored securely.
4. **Data Retrieval**: When data is retrieved, it is validated and serialized using the appropriate Pydantic models to ensure data integrity and security.

By following these security measures, the application ensures that user data is protected, and only authorized users can access and modify resources.