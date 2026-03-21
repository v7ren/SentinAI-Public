# HTTP Endpoints

This section documents the available HTTP endpoints in the project, including their methods, paths, and functionalities. The endpoints are implemented using the Bun web server framework and are configured to use TLS with a self-signed certificate. The server also interacts with a Redis client for session and file data storage.

## Overview

The following HTTP endpoints are defined in the `test/index.ts` file:

- **Root (`/`)**: Serves a simple HTML form for file uploads.
- **File Upload (`/upload`)**: Handles file uploads and stores file metadata in Redis.
- **File Retrieval (`/paper/:id`)**: Retrieves and serves a file from Redis based on the provided ID.
- **Secret Page (`/secret`)**: Serves a page with a secret value and an optional payload.
- **Flag Challenge (`/flag`)**: Checks a guessed secret against the stored secret and returns a flag if correct.
- **Visit URL (`/visit/:id`)**: Visits a URL using Puppeteer if the browser is not already open.

## Endpoint Details

### Root (`/`)

- **Method**: GET
- **Path**: `/`
- **Functionality**: Serves a simple HTML form for file uploads.
- **Implementation**: Defined in `test/index.ts:1-120`.

### File Upload (`/upload`)

- **Method**: POST
- **Path**: `/upload`
- **Functionality**: Handles file uploads and stores file metadata in Redis.
- **Implementation**: Defined in `test/index.ts:1-120`.

### File Retrieval (`/paper/:id`)

- **Method**: GET
- **Path**: `/paper/:id`
- **Functionality**: Retrieves and serves a file from Redis based on the provided ID.
- **Implementation**: Defined in `test/index.ts:1-120`.

### Secret Page (`/secret`)

- **Method**: GET
- **Path**: `/secret`
- **Functionality**: Serves a page with a secret value and an optional payload.
- **Implementation**: Defined in `test/index.ts:121-183`.

### Flag Challenge (`/flag`)

- **Method**: GET
- **Path**: `/flag`
- **Functionality**: Checks a guessed secret against the stored secret and returns a flag if correct.
- **Implementation**: Defined in `test/index.ts:121-183`.

### Visit URL (`/visit/:id`)

- **Method**: GET
- **Path**: `/visit/:id`
- **Functionality**: Visits a URL using Puppeteer if the browser is not already open.
- **Implementation**: Defined in `test/index.ts:121-183`.

## Interactions and Flows

### File Upload and Retrieval

1. **File Upload (`/upload`)**:
   - The client sends a POST request to `/upload` with the file data.
   - The server processes the file, stores the metadata in Redis, and returns a success response.

2. **File Retrieval (`/paper/:id`)**:
   - The client sends a GET request to `/paper/:id` with the file ID.
   - The server retrieves the file metadata from Redis and serves the file to the client.

### Secret and Flag Management

1. **Secret Page (`/secret`)**:
   - The client sends a GET request to `/secret`.
   - The server retrieves the secret value and any optional payload from Redis and serves the page to the client.

2. **Flag Challenge (`/flag`)**:
   - The client sends a GET request to `/flag` with a guessed secret.
   - The server checks the guessed secret against the stored secret in Redis.
   - If the guess is correct, the server returns a flag; otherwise, it returns an error message.

### URL Visiting

1. **Visit URL (`/visit/:id`)**:
   - The client sends a GET request to `/visit/:id` with the URL ID.
   - The server checks if the Puppeteer browser is already open.
   - If the browser is not open, it initializes Puppeteer and visits the URL.
   - The server then returns the result of the visit.

## Security and Configuration

- **TLS Configuration**: The server is configured to use TLS with a self-signed certificate, ensuring secure communication.
- **Redis Client**: The server uses a Redis client to manage session and file data storage, providing a persistent and efficient data store.

By following these endpoints and their interactions, you can understand the core functionalities and data flows within the web server.