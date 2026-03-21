# Architecture and Data Flow

## Overview

The project is a web application built using the Bun framework, which serves several endpoints for file uploads, secret management, and visiting URLs. It leverages Redis for session and file data storage and uses a self-signed certificate for secure communication. The architecture is primarily client-server, with a focus on handling HTTP requests and responses.

## Main Architectural Components

### 1. Web Server
- **File**: `test/index.ts`
- **Description**: The main entry point of the application. It sets up the web server using the Bun framework and defines various HTTP endpoints.
- **Key Functions**:
  - `setupServer()`: Initializes the server, sets up routes, and configures TLS.
  - `visitUrl(url: string)`: Uses Puppeteer to visit a URL if the browser is not already open.
  - `createHttpHeaders()`: Generates HTTP headers for responses.

### 2. Redis Client
- **File**: `test/index.ts`
- **Description**: Manages session and file data storage using Redis.
- **Key Functions**:
  - `initializeRedisClient()`: Sets up the Redis client.
  - `storeFileMetadata(fileId: string, metadata: object)`: Stores file metadata in Redis.
  - `retrieveFileMetadata(fileId: string)`: Retrieves file metadata from Redis.

### 3. File Upload and Retrieval
- **File**: `test/index.ts`
- **Description**: Handles file uploads and retrieval operations.
- **Endpoints**:
  - `GET /`: Serves a simple HTML form for file uploads.
  - `POST /upload`: Handles file uploads and stores file metadata in Redis.
  - `GET /paper/:id`: Retrieves and serves a file from Redis based on the provided ID.

### 4. Secret Management
- **File**: `test/index.ts`
- **Description**: Manages secret values and provides endpoints for accessing and validating them.
- **Endpoints**:
  - `GET /secret`: Serves a page with a secret value and an optional payload.
  - `GET /flag`: Checks a guessed secret against the stored secret and returns a flag if correct.

### 5. URL Visiting
- **File**: `test/index.ts`
- **Description**: Uses Puppeteer to visit URLs and track visits.
- **Endpoints**:
  - `GET /visit/:id`: Visits a URL using Puppeteer if the browser is not already open.

## Data and Control Flow

### 1. Client-Server Interaction
- **Client**: Sends HTTP requests to the server.
- **Server**: Processes the requests and sends appropriate responses.
- **Endpoints**:
  - `GET /`: The client requests the file upload form.
  - `POST /upload`: The client uploads a file, and the server stores the file metadata in Redis.
  - `GET /paper/:id`: The client requests a file, and the server retrieves and serves the file from Redis.
  - `GET /secret`: The client requests a secret page.
  - `GET /flag`: The client submits a guessed secret, and the server validates it.
  - `GET /visit/:id`: The client requests a URL visit, and the server uses Puppeteer to visit the URL.

### 2. Redis Data Storage
- **File Upload**:
  - The server receives a file upload request.
  - The server stores the file metadata in Redis using the `storeFileMetadata` function.
- **File Retrieval**:
  - The server receives a file retrieval request.
  - The server retrieves the file metadata from Redis using the `retrieveFileMetadata` function.
- **Secret Management**:
  - The server stores a secret value in Redis.
  - The server retrieves and validates the secret value when a client submits a guess.

### 3. URL Visiting
- **URL Visit**:
  - The server receives a URL visit request.
  - The server checks if the browser is already open.
  - If the browser is not open, the server uses Puppeteer to visit the URL.

## Important Patterns

### 1. Client-Server Architecture
- The application follows a client-server architecture, where the client sends HTTP requests to the server, and the server processes these requests and sends appropriate responses.

### 2. Layered Architecture
- The application is structured in layers:
  - **Presentation Layer**: Handles HTTP requests and responses.
  - **Business Logic Layer**: Manages file uploads, secret management, and URL visiting.
  - **Data Access Layer**: Interacts with Redis for data storage and retrieval.

### 3. Event-Driven Architecture
- The application uses event-driven patterns for handling HTTP requests and responses, as well as for managing file uploads and URL visits.

### 4. Security
- The server is configured to use TLS with a self-signed certificate to ensure secure communication.
- Secret management involves storing and validating secret values, which are used for authentication and authorization purposes.

## Conclusion

The architecture of the project is designed to handle file uploads, secret management, and URL visiting efficiently and securely. The use of Redis for data storage and the Bun framework for the web server ensures a robust and scalable solution. The client-server and layered architecture patterns provide a clear separation of concerns, making the application easy to maintain and extend.