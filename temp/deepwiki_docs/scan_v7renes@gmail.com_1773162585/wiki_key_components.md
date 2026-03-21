# Key Components

This section provides an overview of the main components of the system, including the web server, Redis, and the headless browser. Each component plays a crucial role in the overall functionality of the application.

## Web Server

The web server is implemented using Bun, a fast JavaScript runtime. It serves several endpoints for various operations, including file uploads, secret management, and URL visits. The server is configured to use TLS with a generated certificate for secure communication.

### Key Endpoints

- **`/`**: Serves a simple HTML form for file uploads.
- **`/upload`**: Handles file uploads and stores file metadata in Redis.
- **`/paper/:id`**: Retrieves and serves a file from Redis based on the provided ID.
- **`/secret`**: Returns a secret value and an optional payload in the response body.
- **`/flag`**: Checks a guessed secret against the stored secret in Redis and returns a flag if correct.
- **`/visit/:id`**: Visits a URL using a headless browser if the browser is not already open.

### Configuration and Security

- **CA Certificate**: The server sets up a Certificate Authority (CA) and generates a certificate for TLS.
- **Chrome Policies**: Configures Chrome policies to ensure the headless browser operates securely.
- **Redis Client**: Initializes a Redis client for session management and data storage.

### Filesystem Operations

- **Temporary Directories and Files**: The server interacts with the filesystem to manage temporary directories and files, ensuring that uploaded files are stored and retrieved correctly.

## Redis

Redis is used for session management and data storage. It stores file metadata, secrets, and other application data. The Redis client is initialized in `test/index.ts` and is used across various endpoints to manage data.

### Key Operations

- **File Metadata Storage**: When a file is uploaded, its metadata is stored in Redis.
- **Secret Management**: Secrets are stored and retrieved from Redis for the `/secret` and `/flag` endpoints.
- **Session Management**: Redis is used to manage user sessions, ensuring that authentication and authorization are handled securely.

## Headless Browser

The headless browser is implemented using Puppeteer, a Node.js library that provides a high-level API to control Chrome or Chromium over the DevTools Protocol. The browser is used to visit URLs as specified by the `/visit/:id` endpoint.

### Key Functions

- **Visit Function**: The `visit` function is defined in `test/index.ts` and is responsible for launching the headless browser and visiting the specified URL.
- **Browser Management**: The function ensures that the browser is not already open before launching a new instance, optimizing resource usage.

### Interaction with the Web Server

- **Endpoint Handling**: The `/visit/:id` endpoint triggers the `visit` function, which uses Puppeteer to control the headless browser.
- **Session and Data Storage**: The browser's actions and results are stored in Redis, ensuring that the state is persistent and can be accessed by other parts of the application.

## Summary

The system is built around a web server using Bun, which serves multiple endpoints for file uploads, secret management, and URL visits. Redis is used for session management and data storage, ensuring that the application can handle user sessions and store application data securely. The headless browser, controlled by Puppeteer, is used to visit URLs and perform actions as specified by the application's endpoints. Together, these components form a robust and secure system.