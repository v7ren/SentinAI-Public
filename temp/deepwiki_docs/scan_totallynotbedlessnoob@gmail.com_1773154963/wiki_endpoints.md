# HTTP Endpoints

This section documents the available HTTP endpoints in the project, including their methods, paths, and functionalities. The web server is built using Bun and is configured to use TLS with a dynamically created certificate. Redis is used for session management and data storage.

## Overview

The project provides several endpoints for file uploads, secret handling, and URL visits. The server is designed to handle both simple and complex interactions, leveraging Redis for session management and Puppeteer for browser automation.

## Endpoints

### Root (`/`)

- **Method**: GET
- **Path**: `/`
- **Functionality**: Serves a simple HTML form for file uploads.
- **File**: `test/index.ts`

### File Upload (`/upload`)

- **Method**: POST
- **Path**: `/upload`
- **Functionality**: Handles POST requests for file uploads. It stores file metadata in Redis and redirects to a paper URL.
- **File**: `test/index.ts`

### Paper Retrieval (`/paper/:id`)

- **Method**: GET
- **Path**: `/paper/:id`
- **Functionality**: Retrieves and serves a file from Redis based on the provided ID.
- **File**: `test/index.ts`

### Secret Page (`/secret`)

- **Method**: GET
- **Path**: `/secret`
- **Functionality**: Serves a page with a secret and an optional payload parameter.
- **File**: `test/index.ts`

### Flag Challenge (`/flag`)

- **Method**: GET
- **Path**: `/flag`
- **Functionality**: Checks a secret against a stored value in Redis and returns a flag if the secret matches.
- **File**: `test/index.ts`

### Visit Tracker (`/visit/:id`)

- **Method**: GET
- **Path**: `/visit/:id`
- **Functionality**: Visits a URL using Puppeteer if the browser is not already open, and sets a cookie with a secret.
- **File**: `test/index.ts`

## Interaction Flows

### File Upload and Retrieval

1. **Upload Form**: The root endpoint (`/`) serves an HTML form for file uploads.
2. **File Upload**: When a user submits the form, a POST request is sent to the `/upload` endpoint. This endpoint processes the file, stores its metadata in Redis, and redirects the user to a paper URL.
3. **Paper Retrieval**: The user can access the uploaded file by visiting the `/paper/:id` endpoint, where `:id` is the unique identifier for the file stored in Redis.

### Secret Handling

1. **Secret Page**: The `/secret` endpoint serves a page containing a secret and an optional payload parameter.
2. **Flag Challenge**: The `/flag` endpoint checks the provided secret against a stored value in Redis. If the secret matches, it returns a flag.

### URL Visits

1. **Visit Tracker**: The `/visit/:id` endpoint is used to visit a URL using Puppeteer. If the browser is not already open, it will be started. The endpoint sets a cookie with a secret and then visits the specified URL.

## Configuration and Security

- **TLS Configuration**: The server is configured to use TLS with a dynamically created certificate.
- **Session Management**: Redis is used for session management, ensuring that user sessions are securely stored and managed.
- **Puppeteer**: Puppeteer is used to control a headless browser for visiting URLs and setting cookies.

By following these endpoints and their interactions, you can understand how the web server handles file uploads, secret handling, and URL visits in a secure and efficient manner.