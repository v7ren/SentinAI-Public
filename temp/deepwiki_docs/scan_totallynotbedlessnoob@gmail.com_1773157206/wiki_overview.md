# Overview

## What the Project Is and What Problem It Solves

This project is a web server built using Bun, a fast JavaScript runtime. The server provides several endpoints for handling file uploads, secret management, and URL visits. It is designed to solve the following problems:

- **File Management**: Users can upload files, and the server stores metadata and the files themselves in Redis.
- **Secret Handling**: The server can manage and validate secrets, which can be used for authentication or other security purposes.
- **URL Visits**: The server can visit URLs using a headless browser (Puppeteer) and set cookies, which is useful for automating web interactions.

## Main Components or Modules

### 1. **Web Server Setup**
- **File**: `test/index.ts`
- **Description**: The main entry point of the application. It sets up the web server using Bun and configures it to use a self-signed certificate for secure connections (TLS).

### 2. **Redis Client**
- **File**: `test/index.ts`
- **Description**: Manages session and file data storage. Redis is used to store file metadata, secrets, and session information.

### 3. **Puppeteer Integration**
- **File**: `test/index.ts`
- **Description**: Uses Puppeteer to control a headless browser for visiting URLs and setting cookies. This is particularly useful for automating web interactions.

### 4. **HTTP Endpoints**
- **File**: `test/index.ts`
- **Endpoints**:
  - **`/`**: Serves a simple HTML form for file uploads.
  - **`/upload`**: Handles file uploads, stores file metadata in Redis, and redirects to a paper URL.
  - **`/paper/:id`**: Retrieves and serves a file from Redis based on the provided ID.
  - **`/secret`**: Returns a secret value and an optional payload in an HTML response.
  - **`/flag`**: Checks a guessed secret against the stored secret in Redis and returns a flag if correct.
  - **`/visit/:id`**: Visits a URL using Puppeteer if the browser is not already open and the file exists in Redis.

## Typical Usage or Runtime Scenario

1. **User Interaction**:
   - A user visits the root endpoint (`/`) and is presented with a form to upload a file.
   - The user uploads a file via the `/upload` endpoint. The server stores the file metadata in Redis and redirects the user to a paper URL.

2. **File Retrieval**:
   - The user can retrieve a previously uploaded file by visiting the `/paper/:id` endpoint, where `:id` is the unique identifier of the file stored in Redis.

3. **Secret Management**:
   - The user can access a secret value by visiting the `/secret` endpoint. This endpoint can also return an optional payload.
   - The user can attempt to guess a secret by visiting the `/flag` endpoint. If the guessed secret matches the stored secret in Redis, a flag is returned.

4. **URL Visits**:
   - The user can trigger a URL visit by visiting the `/visit/:id` endpoint. The server uses Puppeteer to open a headless browser, visit the specified URL, and set cookies if necessary.

## Where to Look Next

For deeper details on specific components and functionalities, refer to the following sections:

- **File Management**: Detailed information on how files are uploaded, stored, and retrieved.
- **Secret Handling**: Explanation of the secret management system, including how secrets are stored and validated.
- **URL Visits**: Step-by-step guide on how the server uses Puppeteer to visit URLs and set cookies.
- **Security and Configuration**: Insights into the security measures, such as TLS configuration and Redis session management.

These sections will provide a more granular understanding of the project's architecture and implementation.