# Authentication and Security

This section provides an overview of the authentication mechanisms in the application, including JWT token handling and user permissions. The authentication system is designed to ensure secure access to company profiles and job listings.

## Overview

The application uses a combination of FastAPI for the web framework, SQLAlchemy for database operations, and JWT (JSON Web Tokens) for authentication. The key components involved in the authentication and security mechanisms are:

- **Database Models**: Defined in `app\models.py`.
- **CRUD Operations**: Implemented in `app\crud.py`.
- **Pydantic Models**: Defined in `app\schemas.py`.
- **FastAPI Endpoints**: Defined in `app\main.py`.

## Database Models

The `app\models.py` file defines the SQLAlchemy ORM models for the application. The key models related to authentication and security are:

- **Company**: Represents a company in the database. It includes fields for `ID`, `name`, `hashed_password`, and `admin_status`. The `hashed_password` field stores the hashed version of the company's password, and `admin_status` indicates whether the company has admin privileges.
- **Job**: Represents a job listing associated with a company. It includes fields for `ID`, `title`, `description`, `company_id`, and `privacy_status`. The `privacy_status` field indicates whether the job listing is public or private.

### Example: Company Model

```python
# app\models.py
class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    admin_status = Column(Boolean, default=False)
    jobs = relationship("Job", back_populates="company")
```

## CRUD Operations

The `app\crud.py` file contains functions for creating, retrieving, and deleting companies and jobs. These functions are used to manage the data in the database and are crucial for the authentication and security mechanisms.

### Key Functions

- **get_company**: Retrieves a company by its ID.
- **get_company_by_name**: Retrieves a company by its name.
- **create_company**: Creates a new company with a hashed password and adds it to the database.
- **create_job**: Creates a new job associated with a company and adds it to the database.
- **get_jobs**: Retrieves jobs for a specific company, optionally including private jobs.
- **delete_all**: Deletes all jobs and companies from the database.

### Example: Creating a Company

```python
# app\crud.py
def create_company(db: Session, company: schemas.CompanyCreate):
    hashed_password = get_password_hash(company.password)
    db_company = models.Company(
        name=company.name,
        hashed_password=hashed_password,
        admin_status=company.admin_status
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company
```

## Pydantic Models

The `app\schemas.py` file defines Pydantic models for data validation and serialization. These models are used to ensure that the data conforms to the specified schema and are crucial for the authentication and security mechanisms.

### Key Models

- **Token**: Represents the structure of a token, including the access token and token type.
- **TokenData**: Represents the data contained in a token, specifically the username.
- **CompanyBase**: Base model for company information, including the company name.
- **CompanyCreate**: Model for creating a new company, including name, admin status, and password.
- **Company**: Model for a company, including ID and admin status, with ORM mode enabled.
- **JobBase**: Base model for job listings, including title, description, and privacy status.
- **JobCreate**: Model for creating a new job listing, inheriting from `JobBase`.
- **Job**: Model for a job listing, including ID and company ID, with ORM mode enabled.

### Example: Token Model

```python
# app\schemas.py
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
```

## FastAPI Endpoints

The `app\main.py` file sets up the FastAPI application and defines the endpoints for authentication, job listing display, and profile editing. The key endpoints related to authentication and security are:

- **login_for_access_token**: Handles the login process and returns an access token upon successful authentication.
- **login**: Renders the login page.
- **show_jobs**: Displays job listings for a specific company, with optional private job listings for admin users.
- **ping**: A simple health check endpoint that returns a 'pong' response.
- **edit_profile**: Renders the profile editing page for a specific company.
- **update_profile**: Handles the update of a company's profile information.

### Example: Login Endpoint

```python
# app\main.py
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    company = crud.get_company_by_name(db, form_data.username)
    if not company:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(form_data.password, company.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": company.name})
    return {"access_token": access_token, "token_type": "bearer"}
```

### Example: Job Listing Endpoint

```python
# app\main.py
@app.get("/company/{company_id}/jobs", response_model=List[schemas.Job])
async def show_jobs(company_id: int, admin: bool = False, db: Session = Depends(get_db)):
    jobs = crud.get_jobs(db, company_id=company_id, admin=admin)
    return jobs
```

## Authentication Flow

1. **User Login**:
   - The user submits their credentials (username and password) via the `/token` endpoint.
   - The `login_for_access_token` function verifies the credentials by checking the hashed password in the database.
   - If the credentials are valid, a JWT token is generated and returned to the user.

2. **Accessing Protected Endpoints**:
   - The user includes the JWT token in the `Authorization` header for subsequent requests.
   - The FastAPI application uses the `Depends` mechanism to validate the token and extract the user's identity.
   - Based on the user's identity and admin status, the application grants or denies access to specific endpoints.

3. **Job Listing Display**:
   - The `show_jobs` endpoint retrieves job listings for a specific company.
   - If the user is an admin, they can view private job listings as well.

4. **Profile Editing**:
   - The `edit_profile` endpoint renders the profile editing page for a specific company.
   - The `update_profile` endpoint handles the update of a company's profile information.

## Security Considerations

- **Password Hashing**: Passwords are hashed using a secure algorithm before being stored in the database. This ensures that even if the database is compromised, the actual passwords remain protected.
- **JWT Tokens**: JWT tokens are used for authentication, providing a stateless and secure way to manage user sessions.
- **Access Control**: Admin users have additional privileges, such as viewing private job listings and editing company profiles. These permissions are enforced at the endpoint level.

By following these mechanisms, the application ensures that only authorized users can access and modify sensitive data.