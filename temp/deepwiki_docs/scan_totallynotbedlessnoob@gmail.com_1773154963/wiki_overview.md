# Overview

## What the Project Is and What Problem It Solves

This project is a web server built using Bun, a modern JavaScript runtime. The server provides several endpoints to handle file uploads, manage secrets, and visit URLs using a headless browser. It is designed to solve the following problems:

- **File Management**: Users can upload files, and the server stores metadata and the files themselves in Redis.
- **Secret Handling**: The server can serve pages with secrets and validate them against stored values.
- **URL Visiting**: The server can visit URLs using Puppeteer, a Node library to control Chrome or Chromium browsers, and set cookies with secrets.

## Main Components or Modules

The project is composed of several key components:

- **Web Server**: Built using Bun, the server handles HTTP requests and responses.
- **Redis**: Used for session management and data storage, including file metadata and secrets.
- **Puppeteer**: A Node library to control a headless browser for visiting URLs and setting cookies.
- **TLS Configuration**: The server is configured to use TLS with a dynamically created certificate for secure communication.
- **Endpoints**: Several HTTP endpoints are defined to handle various operations:
  - **File Uploads**: Users can upload files via a form.
  - **File Retrieval**: Users can retrieve uploaded files by their unique IDs.
  - **Secret Management**: Pages can be served with secrets, and secrets can be validated.
  - **URL Visiting**: The server can visit specified URLs and set cookies.

## Typical Usage or Runtime Scenario

A typical usage scenario for this project involves the following steps:

1. **Server Initialization**:
   - The server is started, and a CA certificate is configured for TLS.
   - Chrome policies are set up to ensure the headless browser operates correctly.
   - Redis is initialized for session management and data storage.

2. **User Interaction**:
   - **File Upload**:
     - A user visits the root endpoint (`/`) and is presented with a form to upload a file.
     - The user submits the form, and the server handles the POST request at the `/upload` endpoint.
     - The file is stored in Redis, and metadata is saved.
     - The user is redirected to a paper URL.
   - **File Retrieval**:
     - The user can access a file by visiting the `/paper/:id` endpoint, where `:id` is the unique identifier of the file.
   - **Secret Management**:
     - The user can visit the `/secret` endpoint to view a page with a secret and an optional payload parameter.
     - The user can validate a secret by visiting the `/flag` endpoint, which checks the secret against a stored value in Redis and returns a flag if the secret matches.
   - **URL Visiting**:
     - The user can visit the `/visit/:id` endpoint, where `:id` is the unique identifier of a URL to be visited.
     - If the headless browser is not already open, it is launched using Puppeteer.
     - The specified URL is visited, and a cookie with a secret is set.

## Where to Look Next

For deeper details on specific aspects of the project, you can refer to the following sections:

- **File Upload and Storage**: Detailed information on how file uploads are handled and stored in Redis.
- **Secret Management**: Explanation of how secrets are served and validated.
- **URL Visiting**: Description of the process for visiting URLs and setting cookies using Puppeteer.
- **Security and TLS Configuration**: Information on how the server is configured for secure communication using TLS.
- **Redis Integration**: Details on how Redis is used for session management and data storage.

Each section will provide more in-depth technical details and code examples to help you understand and work with the project more effectively.