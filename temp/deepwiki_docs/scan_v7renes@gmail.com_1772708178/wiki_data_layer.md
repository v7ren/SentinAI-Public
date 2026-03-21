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