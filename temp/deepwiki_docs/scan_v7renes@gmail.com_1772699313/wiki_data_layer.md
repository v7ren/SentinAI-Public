# Data Layer

This section provides an overview of the database setup, including the ORM models and CRUD operations used in the application.

## Database Setup

The database setup is managed in the `app/database.py` file. This file initializes the database connection and sets up the necessary components for working with SQLAlchemy, an Object-Relational Mapping (ORM) library.

### Key Components

- **Database URL**: The connection string for the database is defined here.
- **Engine**: An SQLAlchemy engine is created using the database URL.
- **Session Factory**: A session factory (`SessionLocal`) is set up to create database sessions.
- **Base Class**: A base class (`Base`) is defined for declarative models.

### Example Usage

```python
from app.database import SessionLocal, Base

# Create a session
session = SessionLocal()

# Create tables (if they don't exist)
Base.metadata.create_all(bind=engine)
```

## ORM Models

The ORM models are defined in the `app/models.py` file. These models represent the tables in the database and their relationships.

### Models

- **Company**: Represents a company in the database.
  - Fields: `id`, `name`, `hashed_password`, `is_admin`
  - Relationships: One-to-many relationship with the `Job` model.

- **Job**: Represents a job listing in the database.
  - Fields: `id`, `title`, `description`, `company_id`, `is_private`
  - Relationships: Many-to-one relationship with the `Company` model.

### Example Usage

```python
from app.models import Company, Job

# Create a new company
new_company = Company(name="Example Co", hashed_password="hashed_password", is_admin=True)
session.add(new_company)
session.commit()

# Create a new job associated with the company
new_job = Job(title="Software Engineer", description="We are looking for a software engineer.", company_id=new_company.id)
session.add(new_job)
session.commit()
```

## CRUD Operations

The CRUD operations for managing companies and jobs are defined in the `app/crud.py` file. These functions use the database session to perform create, read, update, and delete operations.

### Key Functions

- **get_company**: Retrieves a company by its ID.
- **get_company_by_name**: Retrieves a company by its name.
- **create_company**: Creates a new company with a hashed password.
- **create_job**: Creates a new job associated with a company.
- **get_jobs**: Retrieves jobs for a company, optionally including private jobs.
- **delete_all**: Deletes all jobs and companies from the database.

### Example Usage

```python
from app.crud import get_company, create_company, create_job, get_jobs

# Retrieve a company by ID
company = get_company(session, company_id=1)

# Create a new company
new_company = create_company(session, name="New Co", password="password", is_admin=False)

# Create a new job for the company
new_job = create_job(session, title="Data Scientist", description="We need a data scientist.", company_id=new_company.id)

# Retrieve jobs for the company
jobs = get_jobs(session, company_id=new_company.id, include_private=True)
```

## Data Validation and Serialization

The `app/schemas.py` file defines Pydantic models for data validation and serialization. These models are used to ensure that the data passed to and from the database is valid and consistent.

### Models

- **Token**: Represents a token with an access token and token type.
- **TokenData**: Represents token data, optionally including a username.
- **CompanyBase**: Base model for company information, including the company name.
- **CompanyCreate**: Model for creating a new company, including name, admin status, and password.
- **Company**: Model for representing a company, including an ID and admin status, with ORM mode enabled.
- **JobBase**: Base model for job listings, including title, description, and privacy status.
- **JobCreate**: Model for creating a new job listing, inheriting from `JobBase`.
- **Job**: Model for representing a job listing, including an ID and company ID, with ORM mode enabled.

### Example Usage

```python
from app.schemas import CompanyCreate, JobCreate

# Create a new company
company_data = CompanyCreate(name="New Co", password="password", is_admin=False)
new_company = create_company(session, **company_data.dict())

# Create a new job for the company
job_data = JobCreate(title="Data Scientist", description="We need a data scientist.", company_id=new_company.id)
new_job = create_job(session, **job_data.dict())
```

## Integration with FastAPI

The `app/main.py` file sets up a FastAPI application and defines the endpoints for interacting with the data layer. These endpoints handle authentication, job listings, and company profile management.

### Key Endpoints

- **/token**: Handles the login form submission and returns a JWT token upon successful authentication.
- **/company/{company_id}/jobs**: Displays a list of jobs for a specific company, with optional private job visibility for admin users.
- **/edit_profile/{company_id}**: Renders the edit profile page for a company.
- **/edit_profile/{company_id}**: Handles the form submission to update a company's profile.
- **/ping**: A simple health check endpoint that returns a 'pong' response.

### Example Usage

```python
from fastapi import FastAPI, Depends
from app.database import SessionLocal
from app.crud import get_company, get_jobs
from app.schemas import Company, Job

app = FastAPI()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to get a company's jobs
@app.get("/company/{company_id}/jobs")
def get_company_jobs(company_id: int, include_private: bool = False, db: Session = Depends(get_db)):
    company = get_company(db, company_id=company_id)
    jobs = get_jobs(db, company_id=company_id, include_private=include_private)
    return {"company": company, "jobs": jobs}
```

This section provides a comprehensive overview of the data layer, including the database setup, ORM models, CRUD operations, and integration with the FastAPI application.