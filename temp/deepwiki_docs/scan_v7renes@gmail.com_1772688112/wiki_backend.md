# Backend

This section details the FastAPI backend, including the API endpoints, database interactions, and security considerations. The backend is designed to intentionally introduce various security vulnerabilities for testing purposes, making it a valuable resource for security assessments and training.

## FastAPI Application Initialization

The FastAPI application is initialized in `vulnerable-server-sast-test\backend\main.py`. This file sets up the application with a vulnerable configuration, defines database tables, and sets up JWT authentication functions. It also includes the creation of an admin user and the setup of database connections.

### Key Components
- **Database Setup**: Initializes database tables and connections.
- **JWT Authentication**: Defines functions for token creation and validation.
- **Admin User Creation**: Creates an admin user during application startup.

## API Endpoints

The backend provides a variety of API endpoints, each with deliberate security vulnerabilities. Below is a list of the endpoints, their purposes, and the associated security concerns.

### User Management
- **Endpoint**: `/api/auth/register` (POST)
  - **Purpose**: User registration.
  - **Security Concerns**: Mass assignment, SQL injection, use of MD5 for password hashing.
- **Endpoint**: `/api/auth/login` (POST)
  - **Purpose**: User login.
  - **Security Concerns**: SQL injection in the authentication process.
- **Endpoint**: `/api/users/{user_id}` (GET)
  - **Purpose**: Retrieve user details.
  - **Security Concerns**: IDOR (Insecure Direct Object References), SQL injection.

### Order Management
- **Endpoint**: `/api/orders` (GET, POST)
  - **Purpose**: List or create orders.
  - **Security Concerns**: SQL injection in both SELECT and INSERT queries.
- **Endpoint**: `/api/search` (GET)
  - **Purpose**: Search orders.
  - **Security Concerns**: SQL injection in the search query.

### Report Generation
- **Endpoint**: `/api/report/generate` (POST)
  - **Purpose**: Generate reports using Jinja2 templates.
  - **Security Concerns**: Server-Side Template Injection (SSTI).

### Configuration Management
- **Endpoint**: `/api/config/import` (POST)
  - **Purpose**: Import configuration data.
  - **Security Concerns**: Insecure deserialization using pickle.
- **Endpoint**: `/api/config/yaml` (POST)
  - **Purpose**: Load YAML configuration data.
  - **Security Concerns**: Insecure deserialization using unsafe YAML loading.

### Log Management
- **Endpoint**: `/api/logs` (GET)
  - **Purpose**: Read log files.
  - **Security Concerns**: Command injection.

### Network Operations
- **Endpoint**: `/api/ping` (GET)
  - **Purpose**: Ping a host.
  - **Security Concerns**: Command injection.
- **Endpoint**: `/api/fetch` (GET)
  - **Purpose**: Fetch a URL.
  - **Security Concerns**: Server-Side Request Forgery (SSRF).

### File Operations
- **Endpoint**: `/api/redirect` (GET)
  - **Purpose**: Perform a redirect.
  - **Security Concerns**: Open redirect vulnerability.
- **Endpoint**: `/api/file/read` (GET)
  - **Purpose**: Read a file.
  - **Security Concerns**: Path traversal vulnerability.
- **Endpoint**: `/api/file/upload` (POST)
  - **Purpose**: Upload a file.
  - **Security Concerns**: No type or size checks, leading to an unrestricted upload vulnerability.
- **Endpoint**: `/api/export/zip` (POST)
  - **Purpose**: Handle ZIP file uploads.
  - **Security Concerns**: Zip slip vulnerability.
- **Endpoint**: `/api/export/csv` (GET)
  - **Purpose**: Export orders as a CSV file.
  - **Security Concerns**: SQL injection and CSV formula injection vulnerabilities.

### Payment Processing
- **Endpoint**: `/api/payment/xml` (POST)
  - **Purpose**: Process XML payment data.
  - **Security Concerns**: XML External Entity (XXE) vulnerability.

### Token Management
- **Endpoint**: `/api/token/decode` (POST)
  - **Purpose**: Decode JWT tokens.
  - **Security Concerns**: Vulnerability to algorithm confusion.

### Debugging and Testing
- **Endpoint**: `/api/debug/env` (GET)
  - **Purpose**: Return environment variables and secrets.
  - **Security Concerns**: Information disclosure.
- **Endpoint**: `/api/validate/regex` (GET)
  - **Purpose**: Validate regular expressions.
  - **Security Concerns**: ReDoS (Regular Expression Denial of Service) vulnerability.
- **Endpoint**: `/api/ldap/search` (GET)
  - **Purpose**: Perform LDAP searches.
  - **Security Concerns**: LDAP injection vulnerability.
- **Endpoint**: `/api/audit` (GET)
  - **Purpose**: Perform an audit.
  - **Security Concerns**: Host header injection vulnerability.

## Security Considerations

The backend is intentionally designed with security vulnerabilities to serve as a testing ground for security assessments. However, it is crucial to understand and mitigate these vulnerabilities in a production environment. Key security concerns include:

- **SQL Injection**: Ensure proper input validation and parameterized queries.
- **Command Injection**: Avoid using user input directly in shell commands.
- **Insecure Deserialization**: Use safe deserialization methods and validate data.
- **Server-Side Request Forgery (SSRF)**: Restrict the URLs that can be fetched.
- **Path Traversal**: Validate file paths to prevent unauthorized access.
- **Open Redirect**: Validate redirect URLs to prevent malicious redirects.
- **XML External Entity (XXE)**: Use secure XML parsers and disable external entity resolution.
- **ReDoS**: Use regular expressions that are not prone to exponential backtracking.
- **LDAP Injection**: Validate and sanitize user input for LDAP queries.
- **Host Header Injection**: Validate and sanitize host headers.

By understanding and addressing these vulnerabilities, developers can build more secure applications.