# Architecture and Data Flow

This section provides an overview of the main architectural components, data flow, and important patterns used in the project. The architecture is primarily centered around a web server that handles various HTTP endpoints, interacts with Redis for session management and data storage, and uses Puppeteer to control a headless browser for visiting URLs.

## Main Architectural Components

### Web Server
- **File**: `test/index.ts`
- **Description**: The web server is built using the Bun framework. It serves multiple endpoints for file uploads, secret management, and URL visits. The server is configured to use HTTPS with a self-signed certificate.
- **Key Functions**:
  - `setupServer()`: Configures the server, including setting up the CA certificate and Chrome policies.
  - `createRedisClient()`: Initializes a Redis client for session management and data storage.
  - `visitUrl(url: string)`: Launches a headless browser to visit a given URL using Puppeteer.

### Redis
- **Description**: Redis is used for session management and storing file metadata and secrets.
- **Key Functions**:
  - `storeFileMetadata(fileId: string, metadata: any)`: Stores file metadata in Redis.
  - `retrieveFileMetadata(fileId: string)`: Retrieves file metadata from Redis.
  - `storeSecret(secret: string)`: Stores a secret value in Redis.
  - `checkSecret(guessedSecret: string)`: Checks a guessed secret against the stored secret in Redis.

### Headless Browser (Puppeteer)
- **Description**: Puppeteer is used to control a headless browser for visiting URLs.
- **Key Functions**:
  - `visitUrl(url: string)`: Launches a headless browser to visit a given URL.

## Data and Control Flow

### File Upload and Retrieval
1. **File Upload**:
   - The client sends a file upload request to the `/upload` endpoint.
   - The server receives the file, processes it, and stores the file metadata in Redis.
   - The server responds with a success message or an error if the upload fails.

2. **File Retrieval**:
   - The client sends a request to the `/paper/:id` endpoint with a file ID.
   - The server retrieves the file metadata from Redis using the provided ID.
   - The server serves the file to the client.

### Secret Management
1. **Secret Retrieval**:
   - The client sends a request to the `/secret` endpoint.
   - The server retrieves the secret value from Redis and returns it in the response body.

2. **Secret Verification**:
   - The client sends a request to the `/flag` endpoint with a guessed secret.
   - The server checks the guessed secret against the stored secret in Redis.
   - If the guessed secret matches, the server returns a flag; otherwise, it returns an error.

### URL Visiting
1. **URL Visit**:
   - The client sends a request to the `/visit/:id` endpoint with a URL ID.
   - The server checks if the headless browser is already open.
   - If the browser is not open, the server launches a headless browser using Puppeteer and visits the URL.
   - The server returns a success message or an error if the visit fails.

## Important Patterns

### Client/Server Pattern
- The web server acts as the server, handling HTTP requests from clients.
- Clients send requests to the server, which processes the requests and returns responses.

### Layered Architecture
- **Presentation Layer**: The web server handles HTTP requests and responses.
- **Business Logic Layer**: The server processes file uploads, secret management, and URL visits.
- **Data Access Layer**: Redis is used for session management and data storage.

### Event-Driven Architecture
- The server is event-driven, responding to HTTP requests and triggering actions such as file storage, secret verification, and URL visits.

### Security Patterns
- **TLS/HTTPS**: The server is configured to use HTTPS with a self-signed certificate to secure data transmission.
- **Session Management**: Redis is used to manage sessions, ensuring that user sessions are secure and stateful.

### File I/O and Network Operations
- The server interacts with the filesystem to manage temporary directories and files.
- Network operations are handled using HTTP endpoints and Puppeteer for browser control.

By understanding these components and their interactions, you can better navigate and maintain the project.