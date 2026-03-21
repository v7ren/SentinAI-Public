# HTTP Endpoints

This section provides a detailed list and description of all the HTTP endpoints provided by the web server. The server is built using Bun and serves several endpoints for file uploads, secret handling, and visiting URLs. It also manages a Redis client for session and file data storage and uses Puppeteer to control a headless browser for visiting URLs and setting cookies.

## Overview

The web server is configured to use a self-signed certificate for secure communication over HTTPS. The main endpoints are:

- **File Uploads**: For uploading files and storing metadata.
- **File Retrieval**: For retrieving uploaded files.
- **Secret Handling**: For managing and verifying secrets.
- **URL Visiting**: For visiting URLs using a headless browser.

## Endpoints

### Root Endpoint
- **Path**: `/`
- **Method**: GET
- **Description**: Serves a simple HTML form for file uploads.
- **File**: `test/index.ts`
- **Details**: This endpoint provides a user interface for uploading files. The form allows users to select a file and submit it to the server.

### File Upload Endpoint
- **Path**: `/upload`
- **Method**: POST
- **Description**: Handles file uploads, stores file metadata in Redis, and redirects to a paper URL.
- **File**: `test/index.ts`
- **Details**: When a file is uploaded, the server stores the file metadata in Redis and then redirects the user to a paper URL. This endpoint is responsible for handling the file upload process and ensuring that the file data is stored securely.

### File Retrieval Endpoint
- **Path**: `/paper/:id`
- **Method**: GET
- **Description**: Retrieves and serves a file from Redis based on the provided ID.
- **File**: `test/index.ts`
- **Details**: This endpoint allows users to retrieve files that have been previously uploaded. The file is identified by its unique ID, which is passed as a parameter in the URL. The server fetches the file metadata from Redis and serves the file to the user.

### Secret Endpoint
- **Path**: `/secret`
- **Method**: GET
- **Description**: Returns a secret value and an optional payload in an HTML response.
- **File**: `test/index.ts`
- **Details**: This endpoint serves a secret value along with an optional payload. The secret value is returned in an HTML response, which can be used for various purposes such as authentication or verification.

### Flag Endpoint
- **Path**: `/flag`
- **Method**: GET
- **Description**: Checks a guessed secret against the stored secret in Redis and returns a flag if correct.
- **File**: `test/index.ts`
- **Details**: This endpoint is used to verify a guessed secret. If the guessed secret matches the stored secret in Redis, a flag is returned. This can be used for security challenges or other verification processes.

### URL Visiting Endpoint
- **Path**: `/visit/:id`
- **Method**: GET
- **Description**: Visits a URL using Puppeteer if the browser is not already open and the file exists in Redis.
- **File**: `test/index.ts`
- **Details**: This endpoint uses Puppeteer to visit a URL. The URL is associated with a file ID, and the server checks if the file exists in Redis and if the browser is already open. If the conditions are met, the URL is visited using a headless browser.

## Security and Configuration

- **Self-Signed Certificate**: The server is configured to use a self-signed certificate for secure communication over HTTPS.
- **Redis Client**: A Redis client is used for session and file data storage.
- **Puppeteer**: Puppeteer is used to control a headless browser for visiting URLs and setting cookies.

## Example Usage

### Uploading a File
1. Navigate to the root endpoint (`/`).
2. Use the HTML form to select and upload a file.
3. The server will store the file metadata in Redis and redirect you to a paper URL.

### Retrieving a File
1. Use the file ID to access the file retrieval endpoint (`/paper/:id`).
2. The server will fetch the file metadata from Redis and serve the file.

### Verifying a Secret
1. Access the secret endpoint (`/secret`).
2. The server will return a secret value and an optional payload in an HTML response.

### Checking a Flag
1. Access the flag endpoint (`/flag`).
2. Provide the guessed secret as a query parameter.
3. If the guessed secret matches the stored secret, a flag will be returned.

### Visiting a URL
1. Access the URL visiting endpoint (`/visit/:id`).
2. Provide the file ID as a parameter.
3. The server will use Puppeteer to visit the associated URL if the conditions are met.

By following these steps, you can interact with the various endpoints provided by the web server.