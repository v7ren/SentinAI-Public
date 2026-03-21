# Database Structure

This section provides details about the SQLite database used in the application, including its schema and initialization processes.

## Database Initialization

The SQLite database is initialized in the `main.py` file. During the application startup, the database is populated with predefined job entries. This initialization process ensures that the database has some initial data to work with, including a hidden job that can only be accessed by admins.

### Initialization Process

1. **Application Startup**:
   - The FastAPI application is initialized in `main.py`.
   - A startup event is defined to populate the database with job listings.

2. **Database Population**:
   - The `main.py` file contains a function that runs on application startup to insert predefined job entries into the database.
   - This function ensures that the database has a set of initial job listings, including a hidden job that is only accessible to admin users.

## Database Schema

The SQLite database schema is not explicitly defined in a separate schema file, but it is inferred from the operations performed in `main.py`. The schema includes a table for job listings, which likely has the following columns:

- **id**: A unique identifier for each job listing.
- **title**: The title of the job.
- **description**: A detailed description of the job.
- **type**: The type of job (e.g., full-time, part-time).
- **is_hidden**: A boolean flag indicating whether the job is hidden and accessible only to admin users.

### Example Schema

```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL,
    is_hidden BOOLEAN DEFAULT FALSE
);
```

## Database Interactions

The application interacts with the SQLite database through the following endpoints:

### Job Listing Endpoint

- **Endpoint**: `/jobs`
- **Method**: POST
- **Description**: This endpoint retrieves job listings based on the job type. It includes basic input sanitization to prevent SQL injection.
- **File**: `main.py`

### Health Check Endpoint

- **Endpoint**: `/ping`
- **Method**: GET
- **Description**: A simple health check endpoint that returns a 'pong' response.
- **File**: `main.py`

### Root HTML File Endpoint

- **Endpoint**: `/`
- **Method**: GET
- **Description**: Serves the root HTML file from the `static` directory.
- **File**: `main.py`

## Security Considerations

- **Input Sanitization**: The `/jobs` endpoint includes basic input sanitization to prevent SQL injection attacks.
- **Hidden Jobs**: The database contains a hidden job that can only be accessed by admin users. This is managed through the `is_hidden` flag in the job listings table.

## Conclusion

The SQLite database in this application is initialized and populated with job listings during the application startup. The schema is inferred from the operations in `main.py`, and the database interactions are managed through the defined endpoints. Security measures, such as input sanitization and hidden job access, are implemented to ensure the integrity and security of the data.