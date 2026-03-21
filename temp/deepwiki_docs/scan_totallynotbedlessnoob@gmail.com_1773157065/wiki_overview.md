# Overview

## What the Project Is and What Problem It Solves

This project is a web server built using the Bun framework. It provides a set of endpoints to handle file uploads, manage secrets, and visit URLs using a headless browser. The server is designed to be secure, using TLS for encrypted communication and Redis for session management and data storage. It also interacts with the filesystem to manage temporary directories and files.

The primary problems this project addresses include:
- **File Management**: Handling file uploads and storing metadata securely.
- **Secret Handling**: Managing and verifying secrets.
- **URL Visiting**: Using a headless browser to visit URLs and track visits.

## Main Components or Modules

### Web Server
- **Framework**: Bun
- **TLS Configuration**: The server is configured to use a CA certificate for secure TLS connections.
- **Endpoints**:
  - **`/`**: Serves a simple HTML form for file uploads.
  - **`/upload`**: Handles file uploads and stores file metadata in Redis.
  - **`/paper/:id`**: Retrieves and serves a file from Redis based on the provided ID.
  - **`/secret`**: Serves a page with a secret value and an optional payload.
  - **`/flag`**: Checks a guessed secret against the stored secret in Redis and returns a flag if correct.
  - **`/visit/:id`**: Visits a URL using a headless browser if the browser is not already open.

### Redis
- **Session Management**: Redis is used to manage user sessions and store session data.
- **Data Storage**: File metadata and secrets are stored in Redis.

### Headless Browser
- **Puppeteer**: The server uses Puppeteer to control a headless browser for visiting URLs.

### Filesystem Operations
- **Temporary Directories**: The server manages temporary directories and files for file uploads and other operations.

## Typical Usage or Runtime Scenario

1. **User Interaction**:
   - A user visits the root endpoint (`/`) and is presented with a form to upload a file.
   - The user submits the form, and the file is uploaded to the server via the `/upload` endpoint.
   - The server stores the file metadata in Redis and provides a unique ID for the uploaded file.

2. **File Retrieval**:
   - The user can retrieve the uploaded file by visiting the `/paper/:id` endpoint with the provided ID.

3. **Secret Handling**:
   - The user can access a secret page by visiting the `/secret` endpoint.
   - The user can guess the secret by visiting the `/flag` endpoint and providing the guessed secret. If the guess is correct, a flag is returned.

4. **URL Visiting**:
   - The user can request the server to visit a URL by visiting the `/visit/:id` endpoint.
   - The server uses a headless browser to visit the URL if the browser is not already open.

## Where to Look Next

For deeper details on specific components and functionalities, refer to the following sections:
- **File Uploads and Storage**: Detailed information on how file uploads are handled and stored in Redis.
- **Secret Management**: Explanation of how secrets are managed and verified.
- **URL Visiting**: Description of the process for visiting URLs using a headless browser.
- **Security and TLS**: Information on the security measures and TLS configuration.
- **Redis Integration**: Details on how Redis is used for session management and data storage.
- **Filesystem Operations**: Explanation of the filesystem operations for managing temporary directories and files.

These sections will provide a more in-depth understanding of the project's architecture and implementation.