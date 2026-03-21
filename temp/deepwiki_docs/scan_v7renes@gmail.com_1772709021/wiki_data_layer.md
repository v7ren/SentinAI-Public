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