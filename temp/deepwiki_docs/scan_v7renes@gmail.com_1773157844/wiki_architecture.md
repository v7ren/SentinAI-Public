# Architecture and Data Flow

## Overview

The project is a web server built using the Bun framework, which serves several endpoints for file uploads, secret handling, and visiting URLs. The server leverages Redis for session management and file storage, Puppeteer for browser automation, and mkcert for certificate creation. The server is configured to use HTTPS with a self-signed certificate.

## Main Architectural Components

### 1. **Web Server (Bun)**
- **File**: `test/index.ts`
- **Role**: The main entry point of the application, responsible for setting up the web server and defining the HTTP routes.
- **Key Functions**:
  - `createServer`: Sets up the web server using Bun.
  - `routes`: Defines the HTTP endpoints and their corresponding handlers.

### 2. **Redis**
- **Role**: Used for session management and file storage.
- **Key Functions**:
  - `redisClient`: Manages the connection to the Redis server.
  - `storeFileMetadata`: Stores file metadata in Redis.
  - `retrieveFile`: Retrieves file metadata from Redis.

### 3. **Puppeteer**
- **Role**: Used for browser automation, specifically for visiting URLs.
- **Key Functions**:
  - `visitUrl`: Launches a headless browser to visit a specified URL.

### 4. **mkcert**
- **Role**: Used to create a self-signed certificate for HTTPS.
- **Key Functions**:
  - `createCA`: Sets up a Certificate Authority (CA).
  - `generateCertificate`: Generates a self-signed certificate.

## Data and Control Flow

### 1. **Initialization and Configuration**
- **File**: `test/index.ts`
- **Flow**:
  - The application starts by setting up a Certificate Authority (CA) and generating a self-signed certificate using `mkcert`.
  - Chrome policies are configured to trust the self-signed certificate.
  - A Redis client is initialized to manage sessions and file storage.
  - The web server is configured to use HTTPS with the generated certificate.

### 2. **HTTP Endpoints**
- **File**: `test/index.ts`
- **Endpoints**:
  - **`/` (GET)**:
    - **Function**: `serveForm`
    - **Flow**: Serves a simple HTML form for file uploads.
  - **`/upload` (POST)**:
    - **Function**: `handleFileUpload`
    - **Flow**: Handles file uploads, stores the file metadata in Redis, and returns a success response.
  - **`/paper/:id` (GET)**:
    - **Function**: `serveFile`
    - **Flow**: Retrieves and serves a file from Redis based on the provided ID.
  - **`/secret` (GET)**:
    - **Function**: `serveSecret`
    - **Flow**: Serves a page with a secret value and an optional payload.
  - **`/flag` (GET)**:
    - **Function**: `validateSecret`
    - **Flow**: Checks a provided secret against the stored secret in Redis and returns a flag if they match.
  - **`/visit/:id` (GET)**:
    - **Function**: `visitUrl`
    - **Flow**: Visits a URL using Puppeteer if the browser is not already open.

### 3. **Redis Operations**
- **File**: `test/index.ts`
- **Functions**:
  - **`storeFileMetadata`**:
    - **Flow**: Stores the metadata of an uploaded file in Redis.
  - **`retrieveFile`**:
    - **Flow**: Retrieves the metadata of a file from Redis based on the provided ID.

### 4. **Puppeteer Operations**
- **File**: `test/index.ts`
- **Function**: `visitUrl`
- **Flow**:
  - Launches a headless browser using Puppeteer.
  - Visits the specified URL.
  - Closes the browser after the visit.

## Important Patterns

### 1. **Client/Server Architecture**
- The application follows a client/server architecture where the web server (Bun) serves HTTP requests from clients.
- The server handles various operations such as file uploads, secret management, and URL visits.

### 2. **Layered Architecture**
- The application is structured in layers:
  - **Presentation Layer**: Handles HTTP requests and responses.
  - **Business Logic Layer**: Manages file uploads, secret validation, and URL visits.
  - **Data Access Layer**: Interacts with Redis for session management and file storage.

### 3. **Event-Driven Architecture**
- The application uses event-driven patterns for handling HTTP requests and responses.
- Puppeteer operations are also event-driven, where the browser launches and visits URLs based on incoming requests.

## Conclusion

The architecture of the project is designed to handle file uploads, secret management, and URL visits efficiently. It leverages modern technologies like Bun, Redis, and Puppeteer to provide a robust and secure web server. The client/server and layered architecture ensure clear separation of concerns, while event-driven patterns enable efficient handling of requests and responses.