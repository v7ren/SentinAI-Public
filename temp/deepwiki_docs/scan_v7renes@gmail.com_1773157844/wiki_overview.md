# Overview

## What the Project Is and What Problem It Solves

This project is a web server built using the Bun framework. It provides a set of endpoints for handling file uploads, secret management, and URL visits. The server uses Redis for session management and file storage, Puppeteer for browser automation, and mkcert for generating self-signed certificates to enable HTTPS. The primary problems this project addresses include:

- **File Upload and Retrieval**: Users can upload files and later retrieve them using a unique identifier.
- **Secret Management**: The server can serve pages with secret values and validate user-provided secrets.
- **URL Visiting**: The server can visit URLs using a headless browser, which is useful for automated web interactions.

## Main Components or Modules

### Web Server
- **Framework**: Bun
- **Endpoints**:
  - **`/`**: Serves a simple HTML form for file uploads.
  - **`/upload`**: Handles file uploads and stores file metadata in Redis.
  - **`/paper/:id`**: Retrieves and serves a file from Redis based on the provided ID.
  - **`/secret`**: Serves a page with a secret value and an optional payload.
  - **`/flag`**: Checks a provided secret against the stored secret in Redis and returns a flag if they match.
  - **`/visit/:id`**: Visits a URL using Puppeteer if the browser is not already open.

### Redis
- **Session Management**: Manages user sessions and authentication.
- **File Storage**: Stores file metadata and content.

### Puppeteer
- **Browser Automation**: Used to visit URLs in a headless browser.

### mkcert
- **Certificate Creation**: Generates self-signed certificates for HTTPS.

## Typical Usage or Runtime Scenario

1. **User Interaction**:
   - A user visits the root endpoint (`/`) and is presented with a form to upload a file.
   - The user uploads a file via the `/upload` endpoint. The server stores the file metadata in Redis and returns a unique identifier.
   - The user can later retrieve the uploaded file using the `/paper/:id` endpoint by providing the unique identifier.

2. **Secret Management**:
   - The user visits the `/secret` endpoint to view a page with a secret value and an optional payload.
   - The user can validate a secret by visiting the `/flag` endpoint and providing the secret. If the secret matches the stored secret in Redis, a flag is returned.

3. **URL Visiting**:
   - The user can request the server to visit a specific URL by accessing the `/visit/:id` endpoint. The server uses Puppeteer to open a headless browser and visit the URL if the browser is not already open.

## Where to Look Next

For deeper details on specific components and functionalities, refer to the following sections:

- **File Upload and Retrieval**: Detailed information on how file uploads are handled and stored in Redis.
- **Secret Management**: Explanation of how secrets are managed and validated.
- **URL Visiting**: Description of the process for visiting URLs using Puppeteer.
- **Security and Configuration**: Details on the setup of HTTPS with self-signed certificates and other security configurations.

These sections will provide more in-depth insights into the implementation and usage of each component.