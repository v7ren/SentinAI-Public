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

---

# Architecture and Data Flow

## Main Architectural Components

The project is structured around a web server built using the Bun framework. The main components and their responsibilities are as follows:

- **Web Server**: The web server is the central component, handling HTTP requests and responses. It is set up in `test/index.ts` and serves several endpoints.
- **TLS Configuration**: The server is configured to use TLS for secure communication. A CA certificate is generated and configured in the same file.
- **Redis**: Redis is used for session management and data storage. It stores file metadata, session information, and secret values.
- **Filesystem Operations**: The server interacts with the filesystem to manage temporary directories and files, primarily for file uploads and retrievals.
- **Headless Browser**: Puppeteer is used to control a headless browser for visiting URLs. This is useful for tasks that require browser automation.

## Data and Control Flow

### Web Server Initialization

1. **TLS Configuration**: The server is configured to use TLS by generating a CA certificate and setting up Chrome policies. This is done in the first chunk of `test/index.ts` (lines 1-120).
2. **Redis Client Setup**: A Redis client is initialized to handle session management and data storage.
3. **Route Definitions**: Several HTTP endpoints are defined to handle various requests. These routes are set up in the second chunk of `test/index.ts` (lines 121-183).

### HTTP Endpoints

1. **File Upload (`/upload`)**:
   - **Request**: The client sends a POST request to `/upload` with a file.
   - **Processing**: The server receives the file, stores it in a temporary directory, and saves metadata (e.g., file ID) in Redis.
   - **Response**: The server returns a success message or an error if the upload fails.

2. **File Retrieval (`/paper/:id`)**:
   - **Request**: The client sends a GET request to `/paper/:id` with a file ID.
   - **Processing**: The server retrieves the file metadata from Redis and serves the file from the filesystem.
   - **Response**: The server returns the file or an error if the file is not found.

3. **Secret Page (`/secret`)**:
   - **Request**: The client sends a GET request to `/secret`.
   - **Processing**: The server retrieves a secret value from Redis and serves a page with the secret and an optional payload.
   - **Response**: The server returns the secret page or an error if the secret is not found.

4. **Flag Challenge (`/flag`)**:
   - **Request**: The client sends a GET request to `/flag` with a guessed secret.
   - **Processing**: The server checks the guessed secret against the stored secret in Redis.
   - **Response**: The server returns a flag if the guess is correct or an error if it is incorrect.

5. **URL Visitation (`/visit/:id`)**:
   - **Request**: The client sends a GET request to `/visit/:id` with a URL ID.
   - **Processing**: The server checks if a headless browser is already open. If not, it opens a new browser instance using Puppeteer and visits the specified URL.
   - **Response**: The server returns a success message or an error if the URL cannot be visited.

### Redis Interactions

- **Session Management**: Redis is used to manage user sessions, ensuring that session data is securely stored and retrieved.
- **Data Storage**: File metadata, secret values, and other data are stored in Redis. This allows for efficient retrieval and management of data across different endpoints.

### Filesystem Operations

- **Temporary Directories**: The server creates temporary directories to store uploaded files. These directories are managed and cleaned up as needed.
- **File Uploads and Retrievals**: Files are uploaded to and retrieved from the filesystem based on the metadata stored in Redis.

### Headless Browser Automation

- **Puppeteer**: Puppeteer is used to control a headless browser. This is particularly useful for tasks that require browser automation, such as visiting URLs and performing actions on web pages.

## Important Patterns

- **Client/Server Architecture**: The web server acts as the central server, handling requests from clients and providing responses. This is a typical client/server pattern.
- **Event-Driven**: The server is event-driven, responding to HTTP requests and triggering actions based on the request type and data.
- **Layered Architecture**: The architecture is layered, with the web server at the top layer, handling HTTP requests and responses, and interacting with lower layers for data storage (Redis) and filesystem operations.

By understanding these components and their interactions, you can better navigate and maintain the codebase.

---

# Key Components

This section provides an overview of the main components of the system, including the web server, Redis, and the headless browser. Each component plays a crucial role in the overall functionality of the application.

## Web Server

The web server is implemented using the Bun framework and is responsible for handling various HTTP endpoints. The server is configured to use TLS with a generated certificate for secure communication. Key functionalities include:

- **File Uploads and Retrieval:**
  - **Endpoint:** `/`
    - **Method:** GET
    - **Description:** Serves a simple HTML form for file uploads.
  - **Endpoint:** `/upload`
    - **Method:** POST
    - **Description:** Handles file uploads and stores file metadata in Redis.
  - **Endpoint:** `/paper/:id`
    - **Method:** GET
    - **Description:** Retrieves and serves a file from Redis based on the provided ID.

- **Secret Handling:**
  - **Endpoint:** `/secret`
    - **Method:** GET
    - **Description:** Serves a page with a secret value and an optional payload.
  - **Endpoint:** `/flag`
    - **Method:** GET
    - **Description:** Checks a guessed secret against the stored secret in Redis and returns a flag if correct.

- **URL Visiting:**
  - **Endpoint:** `/visit/:id`
    - **Method:** GET
    - **Description:** Visits a URL using a headless browser if the browser is not already open.

### File: `test\index.ts`

The web server setup and endpoint definitions are primarily found in `test\index.ts`. This file also includes the configuration for the CA certificate, Chrome policies, and the Redis client.

## Redis

Redis is used for session management and data storage. It plays a critical role in the following functionalities:

- **Session Management:**
  - Manages user sessions and authentication.
  - Stores session data securely.

- **Data Storage:**
  - Stores file metadata and secret values.
  - Provides a fast and efficient way to retrieve and manage data.

### Key Functions

- **Redis Client Initialization:**
  - Initializes the Redis client for interaction with the Redis server.
  - Configures the client to handle session data and file metadata.

- **Data Operations:**
  - Stores and retrieves file metadata.
  - Manages secret values and session data.

### File: `test\index.ts`

The Redis client and data operations are defined in `test\index.ts`. The file includes functions for setting and retrieving data from Redis, which are used by the web server endpoints.

## Headless Browser

The headless browser is implemented using Puppeteer and is used to visit URLs as requested by the web server. This component is essential for tasks that require browser automation, such as visiting web pages and performing actions on them.

### Key Functions

- **Visit Function:**
  - Opens a URL in a headless browser.
  - Ensures that the browser is not already open to prevent multiple instances.

### File: `test\index.ts`

The headless browser setup and the visit function are defined in `test\index.ts`. The visit function is used by the `/visit/:id` endpoint to open URLs in the headless browser.

## Interaction Flow

1. **User Interaction:**
   - Users interact with the web server through the defined endpoints.
   - For example, a user can upload a file using the `/upload` endpoint.

2. **Data Storage:**
   - The web server stores file metadata and other data in Redis.
   - For example, file metadata is stored when a file is uploaded.

3. **Secret Handling:**
   - The web server handles secret values and session data using Redis.
   - For example, the `/secret` endpoint serves a page with a secret value.

4. **URL Visiting:**
   - The web server uses the headless browser to visit URLs.
   - For example, the `/visit/:id` endpoint triggers the visit function to open a URL in the headless browser.

By understanding these key components and their interactions, you can better navigate and maintain the system.

---

# Security

This section details the security measures implemented in the project, including TLS, session management, and secret handling. The security features are primarily managed in the `test/index.ts` file, which sets up the web server and defines various endpoints.

## TLS Configuration

The web server is configured to use TLS (Transport Layer Security) to ensure secure communication between the client and the server. This is achieved by generating a CA (Certificate Authority) certificate and configuring the server to use it.

### Key Files and Functions
- **File:** `test/index.ts`
- **Function:** `setupTLS()`
  - **Description:** This function generates a CA certificate and configures the server to use it for TLS. It ensures that all data transmitted between the client and the server is encrypted.

### Example Code Snippet
```typescript
// Generate CA certificate
const ca = generateCA();

// Configure server to use TLS
const server = Bun.serve({
  port: 443,
  fetch: (req) => {
    // Handle requests
  },
  tls: {
    key: fs.readFileSync('path/to/private/key.pem'),
    cert: fs.readFileSync('path/to/certificate.pem'),
  },
});
```

## Session Management

Session management is handled using Redis, a fast in-memory data store. Redis is used to store session data, ensuring that user sessions are securely managed and can be efficiently accessed.

### Key Files and Functions
- **File:** `test/index.ts`
- **Function:** `createRedisClient()`
  - **Description:** This function initializes a Redis client that is used to store and retrieve session data.

### Example Code Snippet
```typescript
// Initialize Redis client
const redis = createRedisClient();

// Store session data
redis.set('session:' + sessionId, JSON.stringify(sessionData));

// Retrieve session data
const sessionData = JSON.parse(await redis.get('session:' + sessionId));
```

## Secret Handling

Secrets are managed securely within the application. The server provides endpoints to handle secrets, including serving a secret page and verifying guessed secrets.

### Key Files and Functions
- **File:** `test/index.ts`
- **Endpoints:**
  - **`/secret`**
    - **Description:** Serves a page with a secret value and an optional payload.
  - **`/flag`**
    - **Description:** Checks a guessed secret against the stored secret in Redis and returns a flag if correct.

### Example Code Snippet
```typescript
// Serve secret page
app.get('/secret', (req, res) => {
  const secret = getSecretFromRedis();
  res.send(`<h1>Secret: ${secret}</h1>`);
});

// Verify guessed secret
app.get('/flag', (req, res) => {
  const guessedSecret = req.query.guess;
  const storedSecret = getSecretFromRedis();
  if (guessedSecret === storedSecret) {
    res.send('Flag: Correct!');
  } else {
    res.send('Flag: Incorrect!');
  }
});
```

## File Upload and Retrieval

File uploads and retrievals are also managed securely, with metadata stored in Redis to ensure data integrity and access control.

### Key Files and Functions
- **File:** `test/index.ts`
- **Endpoints:**
  - **`/upload`**
    - **Description:** Handles file uploads and stores file metadata in Redis.
  - **`/paper/:id`**
    - **Description:** Retrieves and serves a file from Redis based on the provided ID.

### Example Code Snippet
```typescript
// Handle file upload
app.post('/upload', (req, res) => {
  const file = req.files.file;
  const metadata = { name: file.name, size: file.size };
  redis.set('file:' + file.id, JSON.stringify(metadata));
  res.send('File uploaded successfully');
});

// Retrieve file
app.get('/paper/:id', (req, res) => {
  const fileId = req.params.id;
  const metadata = JSON.parse(await redis.get('file:' + fileId));
  const file = getFileFromStorage(fileId);
  res.send(file);
});
```

## Summary

The security measures implemented in this project include:
- **TLS Configuration:** Ensures secure communication between the client and the server.
- **Session Management:** Uses Redis to securely store and manage user sessions.
- **Secret Handling:** Provides secure endpoints for serving and verifying secrets.
- **File Upload and Retrieval:** Manages file metadata securely in Redis to ensure data integrity and access control.

By following these practices, the application ensures that sensitive data is protected and that user interactions are secure.

---

# HTTP Endpoints

This section provides a detailed list and description of all the HTTP endpoints provided by the web server. The server is built using the Bun framework and serves various functionalities, including file uploads, secret handling, and URL visiting. The server also uses Redis for session management and data storage.

## Root Endpoint
- **Path**: `/`
- **Method**: GET
- **Description**: Serves a simple HTML form for file uploads. This form allows users to select a file and submit it to the server.

## File Upload Endpoint
- **Path**: `/upload`
- **Method**: POST
- **Description**: Handles file uploads. When a file is uploaded, the server stores the file metadata in Redis. This endpoint is responsible for processing the uploaded file and saving relevant information to the Redis database.

## File Retrieval Endpoint
- **Path**: `/paper/:id`
- **Method**: GET
- **Description**: Retrieves and serves a file from Redis based on the provided ID. The `:id` parameter in the URL is used to identify the specific file to be retrieved.

## Secret Page Endpoint
- **Path**: `/secret`
- **Method**: GET
- **Description**: Serves a page with a secret value and an optional payload. This endpoint can be used to display sensitive information or perform actions based on the secret value.

## Flag Challenge Endpoint
- **Path**: `/flag`
- **Method**: GET
- **Description**: Checks a guessed secret against the stored secret in Redis. If the guessed secret matches the stored secret, the endpoint returns a flag. This can be used for security challenges or authentication purposes.

## URL Visit Endpoint
- **Path**: `/visit/:id`
- **Method**: GET
- **Description**: Visits a URL using a headless browser if the browser is not already open. The `:id` parameter in the URL is used to identify the specific URL to be visited. This endpoint leverages Puppeteer to control the headless browser and perform the visit.

## Additional Notes
- **Security**: The server is configured to use TLS with a generated certificate, ensuring secure communication over HTTPS.
- **Session Management**: Redis is used for session management and data storage, providing a robust and scalable solution for handling user sessions and file metadata.
- **Filesystem Operations**: The server interacts with the filesystem to manage temporary directories and files, ensuring that uploaded files are stored and retrieved correctly.

By understanding these endpoints, developers can effectively interact with the web server and leverage its functionalities for various use cases.

---