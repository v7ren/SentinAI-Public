# Endpoints

This section documents the available HTTP endpoints in the application, including their methods, paths, and expected responses. The application is built using FastAPI and serves several key endpoints for job listings, health checks, and static content.

## Job Listings Endpoint

### Method: POST
### Path: `/jobs`

#### Description
This endpoint retrieves job listings based on the job type provided in the request. It includes basic input sanitization to prevent SQL injection.

#### Request
- **Body**: JSON object with the following fields:
  - `job_type` (string): The type of job to filter by.

#### Response
- **Status Code**: 200 OK
- **Body**: JSON array of job listings matching the provided job type.
  - Example:
    ```json
    [
      {
        "id": 1,
        "title": "Software Engineer",
        "company": "TechCorp",
        "location": "San Francisco",
        "description": "We are looking for a talented software engineer to join our team."
      }
    ]
    ```

#### Example Usage
```bash
curl -X POST "http://localhost:8000/jobs" -H "Content-Type: application/json" -d '{"job_type": "Software Engineer"}'
```

## Health Check Endpoint

### Method: GET
### Path: `/ping`

#### Description
This is a simple health check endpoint that returns a 'pong' response to indicate that the application is running and responsive.

#### Response
- **Status Code**: 200 OK
- **Body**: JSON object with a single key-value pair.
  - Example:
    ```json
    {
      "message": "pong"
    }
    ```

#### Example Usage
```bash
curl -X GET "http://localhost:8000/ping"
```

## Static HTML Endpoint

### Method: GET
### Path: `/`

#### Description
This endpoint serves a static HTML file at the root path of the application. The HTML file is served directly from the file system.

#### Response
- **Status Code**: 200 OK
- **Body**: The content of the static HTML file.

#### Example Usage
```bash
curl -X GET "http://localhost:8000/"
```

## Summary

- **Job Listings Endpoint**: `POST /jobs` - Retrieves job listings based on job type.
- **Health Check Endpoint**: `GET /ping` - Returns a 'pong' response to indicate the application is running.
- **Static HTML Endpoint**: `GET /` - Serves a static HTML file at the root path.

These endpoints are defined and managed in the `app/main.py` file, which sets up the FastAPI application and initializes the SQLite database with job data. The application also includes basic security measures to prevent SQL injection in the job listings endpoint.