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

---

# Architecture and Data Flow

This section provides an overview of the main architectural components of the application, how data and control flow between them, and the important patterns used in the design.

## Main Architectural Components

### 1. **Database Layer**
- **File:** `app/database.py`
- **Components:**
  - **SessionLocal**: A session factory for creating database sessions using SQLAlchemy.
  - **Base**: Base class for declarative ORM models.
- **Functionality:**
  - Manages the connection to a SQLite database.
  - Provides session management for database operations.

### 2. **Data Validation and Serialization**
- **File:** `app/schemas.py`
- **Components:**
  - **Pydantic Models**: `Token`, `TokenData`, `CompanyBase`, `CompanyCreate`, `Company`, `JobBase`, `JobCreate`, `Job`
- **Functionality:**
  - Defines data schemas for request validation and response serialization.
  - Ensures data integrity and consistency across the application.

### 3. **ORM Models**
- **File:** `app/models.py`
- **Components:**
  - **Company**: ORM model for the 'companies' table.
  - **Job**: ORM model for the 'jobs' table.
- **Functionality:**
  - Represents the structure of the database tables.
  - Defines relationships between models (e.g., a company can have multiple jobs).

### 4. **CRUD Operations**
- **File:** `app/crud.py`
- **Components:**
  - **Functions**: `get_company`, `get_company_by_name`, `create_company`, `create_job`, `get_jobs`, `delete_all`
- **Functionality:**
  - Provides functions for creating, retrieving, updating, and deleting records in the database.
  - Includes password hashing for company creation to ensure security.

### 5. **Application Layer**
- **File:** `app/main.py`
- **Components:**
  - **FastAPI Application**: Sets up the FastAPI application.
  - **Endpoints**: `login`, `login_for_access_token`, `show_jobs`, `ping`, `edit_profile`, `update_profile`
- **Functionality:**
  - Handles HTTP requests and responses.
  - Manages authentication and authorization using JWT tokens.
  - Provides routes for company management, job listing, and profile editing.

## Data and Control Flow

### 1. **User Interaction**
- **Login Flow:**
  - **Endpoint**: `POST /token`
  - **Process**:
    - The user submits a login form.
    - The `login_for_access_token` function validates the credentials.
    - If valid, a JWT token is generated and returned to the user.
- **Job Listing:**
  - **Endpoint**: `GET /company/{company_id}/jobs`
  - **Process**:
    - The user requests a list of jobs for a specific company.
    - The `show_jobs` function retrieves the jobs from the database using the `get_jobs` function from `app/crud.py`.
    - The response is serialized using the `Job` Pydantic model from `app/schemas.py`.

### 2. **Database Interaction**
- **Session Management:**
  - **File**: `app/database.py`
  - **Process**:
    - A database session is created using `SessionLocal`.
    - This session is used to perform database operations in the CRUD functions.
- **CRUD Operations:**
  - **File**: `app/crud.py`
  - **Process**:
    - Functions like `create_company` and `create_job` use the session to add new records to the database.
    - Functions like `get_company` and `get_jobs` use the session to query the database.
    - The session is committed or rolled back as needed to ensure data integrity.

### 3. **Data Validation and Serialization**
- **Request Validation:**
  - **File**: `app/schemas.py`
  - **Process**:
    - Pydantic models are used to validate incoming request data.
    - For example, the `CompanyCreate` model ensures that the required fields are present and valid when creating a new company.
- **Response Serialization:**
  - **File**: `app/schemas.py`
  - **Process**:
    - Pydantic models are used to serialize data before sending it in the response.
    - For example, the `Job` model ensures that the job data is formatted correctly when returned to the user.

## Important Patterns

### 1. **Model-View-Controller (MVC)**
- **Model**: Defined in `app/models.py` and `app/schemas.py`.
  - Represents the data structure and business logic.
- **View**: Defined in `app/main.py`.
  - Handles user interactions and renders responses.
- **Controller**: Defined in `app/crud.py`.
  - Manages the business logic and interacts with the model.

### 2. **Layered Architecture**
- **Presentation Layer**: `app/main.py`
  - Handles user requests and responses.
- **Business Logic Layer**: `app/crud.py`
  - Manages the application's core functionality.
- **Data Access Layer**: `app/database.py` and `app/models.py`
  - Manages database interactions and data storage.

### 3. **Event-Driven Architecture**
- **Authentication**: JWT Tokens
  - The application uses JWT tokens for authentication and authorization.
  - Tokens are generated and validated in the `login_for_access_token` function.

### 4. **Dependency Injection**
- **Session Management**: `app/database.py`
  - The `SessionLocal` session factory is used to create database sessions.
  - These sessions are passed to the CRUD functions to perform database operations.

By following these patterns and components, the application ensures a clean separation of concerns, maintainability, and scalability.

---

# Data Layer

This section provides an overview of the database schema, ORM models, and CRUD operations for managing companies and jobs in the application. The data layer is built using SQLAlchemy, a powerful ORM for Python, and is designed to handle the storage and retrieval of company and job data efficiently.

## Database Setup

### `app/database.py`

- **Database Connection and Session Management**:
  - The file `app/database.py` sets up the database connection and session management using SQLAlchemy.
  - **SessionLocal**: A session factory for creating database sessions.
  - **Base**: The base class for declarative ORM models.

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

## ORM Models

### `app/models.py`

- **Company Model**:
  - The `Company` model represents a company entity in the database.
  - Fields: `id`, `name`, `hashed_password`, `is_admin`.
  - Relationships: One-to-many relationship with the `Job` model.

- **Job Model**:
  - The `Job` model represents a job listing entity in the database.
  - Fields: `id`, `title`, `description`, `company_id`, `is_private`.
  - Relationships: Many-to-one relationship back to the `Company` model.

```python
# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    jobs = relationship("Job", back_populates="company")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    is_private = Column(Boolean, default=False)
    company = relationship("Company", back_populates="jobs")
```

## Data Validation and Serialization

### `app/schemas.py`

- **Pydantic Models**:
  - The file `app/schemas.py` defines Pydantic models for data validation and serialization.
  - **Token, TokenData**: Models for authentication tokens.
  - **CompanyBase, CompanyCreate, Company**: Models for company information.
  - **JobBase, JobCreate, Job**: Models for job listings.

```python
# app/schemas.py
from pydantic import BaseModel
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class CompanyBase(BaseModel):
    name: str

class CompanyCreate(CompanyBase):
    password: str

class Company(CompanyBase):
    id: int
    is_admin: bool
    jobs: List[Job] = []

    class Config:
        orm_mode = True

class JobBase(BaseModel):
    title: str
    description: str

class JobCreate(JobBase):
    is_private: bool = False

class Job(JobBase):
    id: int
    company_id: int

    class Config:
        orm_mode = True
```

## CRUD Operations

### `app/crud.py`

- **CRUD Functions**:
  - The file `app/crud.py` contains functions for creating, retrieving, and deleting companies and jobs using SQLAlchemy ORM.
  - **get_company**: Retrieves a company by its ID.
  - **get_company_by_name**: Retrieves a company by its name.
  - **create_company**: Creates a new company with a hashed password.
  - **create_job**: Creates a new job associated with a company.
  - **get_jobs**: Retrieves jobs for a specific company, optionally including private jobs.
  - **delete_all**: Deletes all jobs and companies from the database.

```python
# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_company(db: Session, company_id: int):
    return db.query(models.Company).filter(models.Company.id == company_id).first()

def get_company_by_name(db: Session, name: str):
    return db.query(models.Company).filter(models.Company.name == name).first()

def create_company(db: Session, company: schemas.CompanyCreate):
    hashed_password = pwd_context.hash(company.password)
    db_company = models.Company(name=company.name, hashed_password=hashed_password)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def create_job(db: Session, job: schemas.JobCreate, company_id: int):
    db_job = models.Job(**job.dict(), company_id=company_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_jobs(db: Session, company_id: int, include_private: bool = False):
    query = db.query(models.Job).filter(models.Job.company_id == company_id)
    if not include_private:
        query = query.filter(models.Job.is_private == False)
    return query.all()

def delete_all(db: Session):
    db.query(models.Job).delete()
    db.query(models.Company).delete()
    db.commit()
```

## Interaction with the Data Layer

### `app/main.py`

- **FastAPI Application**:
  - The file `app/main.py` sets up a FastAPI application for a company management system.
  - **Routes**:
    - **login**: Renders the login page.
    - **login_for_access_token**: Handles the login form submission and returns an access token.
    - **show_jobs**: Displays a list of jobs for a specific company, with optional private job listings for admin users.
    - **ping**: A simple health check endpoint that returns a 'pong' response.
    - **edit_profile**: Renders the profile editing page for a company.
    - **update_profile**: Handles the form submission for updating a company's profile.

```python
# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_company_by_name(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.name}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/company/{company_id}/jobs")
async def show_jobs(company_id: int, include_private: bool = False, db: Session = Depends(get_db)):
    jobs = crud.get_jobs(db, company_id, include_private)
    return jobs

@app.get("/ping")
async def ping():
    return "pong"

@app.get("/edit_profile/{company_id}")
async def edit_profile(company_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company

@app.post("/edit_profile/{company_id}")
async def update_profile(company_id: int, company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    db_company = crud.get_company(db, company_id)
    if not db_company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    db_company.name = company.name
    db_company.hashed_password = pwd_context.hash(company.password)
    db.commit()
    db.refresh(db_company)
    return db_company
```

### Summary

The data layer of the application is designed to manage companies and jobs efficiently using SQLAlchemy for ORM and Pydantic for data validation. The `app/database.py` file sets up the database connection, `app/models.py` defines the ORM models, `app/schemas.py` provides data validation and serialization, and `app/crud.py` contains the CRUD operations. The FastAPI application in `app/main.py` interacts with the data layer to provide endpoints for authentication, job listing, and profile editing.

---

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

---

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

---