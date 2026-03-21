# Data Layer

This section provides an overview of the database setup, ORM models, and CRUD operations for managing company and job data in the application.

## Database Setup

The database setup is handled in the `app/database.py` file. This file initializes the connection to the database using SQLAlchemy and sets up the necessary components for ORM operations.

### Key Components

- **Database URL**: The connection string for the database.
- **Engine**: The SQLAlchemy engine used to connect to the database.
- **Session Factory**: A session factory for creating database sessions.
- **Base Class**: The base class for declarative models.

### Code Snippet

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"  # Example URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

## ORM Models

The ORM models are defined in the `app/models.py` file. These models represent the entities in the database and their relationships.

### Models

- **Company**: Represents a company in the database.
  - Fields: `id`, `name`, `hashed_password`, `is_admin`
  - Relationships: One-to-many relationship with the `Job` model.

- **Job**: Represents a job listing in the database.
  - Fields: `id`, `title`, `description`, `company_id`, `is_private`
  - Relationships: Many-to-one relationship with the `Company` model.

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

## CRUD Operations

The CRUD operations for managing companies and jobs are defined in the `app/crud.py` file. These functions use SQLAlchemy ORM to interact with the database.

### Key Functions

- **get_company**: Retrieves a company by its ID.
- **get_company_by_name**: Retrieves a company by its name.
- **create_company**: Creates a new company with a hashed password.
- **create_job**: Creates a new job associated with a company.
- **get_jobs**: Retrieves jobs for a specific company, optionally including private jobs.
- **delete_all**: Deletes all jobs and companies from the database.

### Code Snippet

```python
# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def get_company(db: Session, company_id: int):
    return db.query(models.Company).filter(models.Company.id == company_id).first()

def get_company_by_name(db: Session, name: str):
    return db.query(models.Company).filter(models.Company.name == name).first()

def create_company(db: Session, company: schemas.CompanyCreate):
    hashed_password = get_password_hash(company.password)
    db_company = models.Company(name=company.name, hashed_password=hashed_password, is_admin=company.is_admin)
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
    if include_private:
        return db.query(models.Job).filter(models.Job.company_id == company_id).all()
    return db.query(models.Job).filter(models.Job.company_id == company_id, models.Job.is_private == False).all()

def delete_all(db: Session):
    db.query(models.Job).delete()
    db.query(models.Company).delete()
    db.commit()
```

## Data Validation and Serialization

The `app/schemas.py` file defines Pydantic models for data validation and serialization. These models ensure that the data conforms to the specified schema and are used in conjunction with the ORM models.

### Models

- **Token**: Represents a token data structure.
- **TokenData**: Represents the data structure for token data.
- **CompanyBase**: Base model for company information.
- **CompanyCreate**: Model for creating a new company.
- **Company**: Model for a company, including ORM mode.
- **JobBase**: Base model for job listings.
- **JobCreate**: Model for creating a new job listing.
- **Job**: Model for a job listing, including ORM mode.

### Code Snippet

```python
# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class CompanyBase(BaseModel):
    name: str

class CompanyCreate(CompanyBase):
    name: str
    is_admin: bool
    password: str

class Company(CompanyBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True

class JobBase(BaseModel):
    title: str
    description: str
    is_private: bool

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    company_id: int

    class Config:
        orm_mode = True
```

## Integration with FastAPI

The `app/main.py` file sets up a FastAPI application and defines endpoints for managing company profiles and job listings. These endpoints use the CRUD functions and ORM models to interact with the database.

### Endpoints

- **/token**: Handles the login process and returns an access token upon successful authentication.
- **/**: Renders the login page.
- **/company/{company_id}/jobs**: Displays job listings for a specific company, with optional private job listings for admin users.
- **/ping**: A simple health check endpoint that returns a 'pong' response.
- **/edit_profile/{company_id}**: Renders the profile editing page for a specific company.
- **/edit_profile/{company_id}**: Handles the update of a company's profile information.

### Code Snippet

```python
# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine

app = FastAPI()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.name})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/company/{company_id}/jobs")
def show_jobs(company_id: int, include_private: bool = False, db: Session = Depends(get_db)):
    jobs = crud.get_jobs(db, company_id, include_private)
    return jobs

@app.get("/ping")
def ping():
    return "pong"

@app.get("/edit_profile/{company_id}")
def edit_profile(company_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@app.post("/edit_profile/{company_id}")
def update_profile(company_id: int, company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    db_company = crud.get_company(db, company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    db_company.name = company.name
    db_company.is_admin = company.is_admin
    db.commit()
    db.refresh(db_company)
    return db_company
```

This section provides a comprehensive overview of the data layer, including the database setup, ORM models, CRUD operations, and integration with the FastAPI application.