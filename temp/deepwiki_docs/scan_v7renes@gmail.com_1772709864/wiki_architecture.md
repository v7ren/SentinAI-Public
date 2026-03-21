# Architecture and Data Flow

## Overview

The application is built using a microservices architecture with FastAPI as the primary framework. It consists of a single FastAPI service that handles HTTP requests, interacts with a SQLite database, and serves static files. The main components of the architecture include:

- **FastAPI Application**: The core of the application, handling HTTP requests and responses.
- **SQLite Database**: A local database used to store job listings.
- **Static File Serving**: Serving static HTML files from a directory.

## Main Architectural Components

### FastAPI Application

The FastAPI application is defined in `app/main.py`. This file sets up the FastAPI instance, defines the endpoints, and initializes the SQLite database. The main components of the FastAPI application are:

- **Endpoints**:
  - **`/jobs`**: A POST endpoint that retrieves job listings based on the job type. It includes basic input sanitization to prevent SQL injection.
  - **`/ping`**: A simple GET endpoint that returns a "pong" response, used for health checks.
  - **`/`**: A GET endpoint that serves the root HTML file from the `static` directory.

- **Database Initialization**:
  - The application initializes a SQLite database and populates it with predefined job entries during startup. Some of these job entries are restricted and can only be accessed by admins.

### SQLite Database

The SQLite database is used to store job listings. The database is initialized and populated with job entries in the `app/main.py` file. The database schema and operations are managed within this file.

### Static File Serving

The application serves static HTML files from the `static` directory. The root HTML file is served by the `/` endpoint.

## Data and Control Flow

### HTTP Request Handling

1. **Client Request**:
   - A client sends an HTTP request to one of the endpoints defined in the FastAPI application.

2. **Endpoint Routing**:
   - The FastAPI application routes the request to the appropriate handler function based on the endpoint and HTTP method.

3. **Database Interaction**:
   - For the `/jobs` endpoint, the handler function queries the SQLite database to retrieve job listings based on the provided job type. The query includes basic input sanitization to prevent SQL injection.
   - For the `/ping` endpoint, the handler function simply returns a "pong" response.
   - For the `/` endpoint, the handler function serves the root HTML file from the `static` directory.

4. **Response Generation**:
   - The handler function generates the appropriate response based on the request and database interaction.
   - The response is then sent back to the client.

### Database Initialization

1. **Application Startup**:
   - When the FastAPI application starts, it triggers a startup event defined in `app/main.py`.

2. **Database Setup**:
   - The startup event initializes the SQLite database and populates it with predefined job entries.
   - Some of these job entries are marked as hidden and can only be accessed by admins.

## Important Patterns

### MVC (Model-View-Controller) Pattern

While the application does not strictly follow the MVC pattern, it does have elements of it:

- **Model**: The SQLite database and the job entries stored within it.
- **View**: The static HTML files served by the `/` endpoint.
- **Controller**: The FastAPI application and its endpoint handlers.

### Layered Architecture

The application follows a layered architecture:

- **Presentation Layer**: The FastAPI application and its endpoints handle HTTP requests and responses.
- **Business Logic Layer**: The endpoint handlers perform the necessary business logic, such as querying the database and sanitizing inputs.
- **Data Access Layer**: The SQLite database and the database initialization logic.

### Event-Driven Architecture

The application uses an event-driven approach for database initialization:

- **Startup Event**: The FastAPI application triggers a startup event to initialize the SQLite database and populate it with job entries.

## Key Files and Functions

- **`app/main.py`**:
  - **Main FastAPI Application**: Sets up the FastAPI instance and defines the endpoints.
  - **Database Initialization**: Initializes the SQLite database and populates it with job entries.
  - **Endpoint Handlers**:
    - **`/jobs`**: Handles job listing queries.
    - **`/ping`**: Handles health check requests.
    - **`/`**: Serves the root HTML file.

By understanding these components and their interactions, you can effectively navigate and maintain the application.