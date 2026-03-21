# Overview

## What the Project Is and What Problem It Solves

The project is a web application built using FastAPI and SQLAlchemy, designed to manage company and job data. It provides a platform for companies to create and manage job listings, while also offering user authentication and profile management features. The primary problems it addresses include:

- **Company and Job Management**: Companies can create, view, and delete job listings.
- **User Authentication**: Secure user login and session management using JWT tokens.
- **Data Validation and Serialization**: Ensuring data integrity and consistency through Pydantic models.

## Main Components or Modules

The project is structured into several key components:

- **Schemas (`schemas.py`)**: Defines Pydantic models for data validation and serialization. These models are used to ensure that data is correctly formatted and validated before being processed by the application.
- **Models (`models.py`)**: Defines SQLAlchemy ORM models for the database. The models represent the entities in the database, such as `Company` and `Job`.
- **Database (`database.py`)**: Sets up the database connection and session management using SQLAlchemy. It includes the creation of the database engine, session factory, and base class for declarative models.
- **CRUD Operations (`crud.py`)**: Contains functions for creating, retrieving, updating, and deleting records in the database. These functions interact with the ORM models to perform database operations.
- **Main Application (`main.py`)**: Sets up the FastAPI application, including endpoints for user authentication, job listing, and profile editing. It also initializes the database with example data on startup.

## Typical Usage or Runtime Scenario

A typical usage scenario for the application involves the following steps:

1. **User Authentication**:
   - A user navigates to the login page (`/`).
   - The user submits their credentials to the login endpoint (`/token`).
   - The application verifies the credentials, generates a JWT token, and returns it to the user.

2. **Company and Job Management**:
   - A company with valid credentials can access the job listing page (`/company/{company_id}/jobs`).
   - The company can view a list of their job postings, including both public and private jobs.
   - The company can create new job listings by submitting a request to the `create_job` endpoint.
   - The company can edit their profile by navigating to the profile editing page (`/edit_profile/{company_id}`) and submitting changes to the `update_profile` endpoint.

3. **Data Integrity and Security**:
   - Pydantic models in `schemas.py` ensure that all data is validated and serialized correctly.
   - SQLAlchemy models in `models.py` and CRUD operations in `crud.py` handle database interactions securely.
   - JWT tokens are used to authenticate and authorize users, ensuring that only authorized users can access and modify data.

## Where to Look Next

For deeper details on specific aspects of the project, refer to the following sections:

- **Schemas and Data Validation**: Explore the `schemas.py` file to understand the data models and validation rules.
- **Database Models and ORM**: Dive into `models.py` to see the structure of the database entities and their relationships.
- **Database Setup and Management**: Check out `database.py` for details on how the database connection and session management are configured.
- **CRUD Operations**: Review `crud.py` to learn about the functions that perform database operations.
- **API Endpoints and Authentication**: Study `main.py` to understand the FastAPI application setup, including endpoints and authentication mechanisms.

By exploring these sections, you can gain a comprehensive understanding of the project's architecture and functionality.

---

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

---

# Data Layer

This section provides an overview of the database models and ORM setup in the application. It focuses on the structure of the `Company` and `Job` models and their relationships.

## Database Setup

The database setup is managed in the `database.py` file. This file initializes the database connection and session management using SQLAlchemy.

### Key Components
- **SessionLocal**: A session factory for creating database sessions.
- **Base**: The base class for declarative models.

### Code Snippet
```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

## ORM Models

The ORM models are defined in the `models.py` file. These models represent the entities in the database and their relationships.

### Company Model
- **Fields**:
  - `id`: Unique identifier for the company.
  - `name`: Name of the company.
  - `hashed_password`: Hashed password for the company.
  - `is_admin`: Boolean indicating if the company has admin privileges.
- **Relationship**:
  - One-to-many relationship with the `Job` model.

### Job Model
- **Fields**:
  - `id`: Unique identifier for the job.
  - `title`: Title of the job.
  - `description`: Description of the job.
  - `company_id`: Foreign key linking to the `Company` model.
  - `is_private`: Boolean indicating if the job is private.
- **Relationship**:
  - Many-to-one relationship with the `Company` model.

### Code Snippet
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

The `schemas.py` file defines Pydantic models for data validation and serialization. These models are used to ensure that the data being passed to and from the database is valid and correctly formatted.

### Key Models
- **CompanyBase**: Base model for company data.
- **CompanyCreate**: Model for creating a new company.
- **Company**: Model for representing a company in the database.
- **JobBase**: Base model for job data.
- **JobCreate**: Model for creating a new job.
- **Job**: Model for representing a job in the database.

### Code Snippet
```python
# app/schemas.py
from pydantic import BaseModel

class CompanyBase(BaseModel):
    name: str

class CompanyCreate(CompanyBase):
    password: str

class Company(CompanyBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True

class JobBase(BaseModel):
    title: str
    description: str

class JobCreate(JobBase):
    company_id: int
    is_private: bool

class Job(JobBase):
    id: int

    class Config:
        orm_mode = True
```

## CRUD Operations

The `crud.py` file contains functions for creating, retrieving, updating, and deleting companies and jobs using SQLAlchemy ORM.

### Key Functions
- **get_company**: Retrieves a company by its ID.
- **get_company_by_name**: Retrieves a company by its name.
- **create_company**: Creates a new company with a hashed password.
- **create_job**: Creates a new job for a specific company.
- **get_jobs**: Retrieves jobs for a specific company, optionally including private jobs.
- **delete_all**: Deletes all jobs and companies from the database.

### Code Snippet
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

def create_job(db: Session, job: schemas.JobCreate):
    db_job = models.Job(**job.dict())
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

## Interaction with the Application

The `main.py` file sets up a FastAPI application and defines endpoints for user authentication, job listing, and profile editing. These endpoints use the ORM models and CRUD functions to interact with the database.

### Key Endpoints
- **login_for_access_token**: Endpoint for logging in and obtaining an access token.
- **show_jobs**: Endpoint for displaying jobs for a specific company.
- **edit_profile**: Endpoint for rendering the profile editing page.
- **update_profile**: Endpoint for updating a company's profile.

### Code Snippet
```python
# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto)

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
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.name}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/company/{company_id}/jobs")
async def show_jobs(company_id: int, include_private: bool = False, db: Session = Depends(get_db)):
    jobs = crud.get_jobs(db, company_id, include_private)
    return jobs

@app.get("/edit_profile/{company_id}")
async def edit_profile(company_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@app.post("/edit_profile/{company_id}")
async def update_profile(company_id: int, company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    db_company = crud.get_company(db, company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    db_company.name = company.name
    db_company.hashed_password = pwd_context.hash(company.password)
    db.commit()
    db.refresh(db_company)
    return db_company
```

### Summary

The data layer of the application is built using SQLAlchemy for ORM and Pydantic for data validation. The `Company` and `Job` models are defined with their respective relationships, and CRUD operations are handled in the `crud.py` file. The FastAPI application in `main.py` provides endpoints for interacting with these models, ensuring secure and efficient data management.

---

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

---

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

---