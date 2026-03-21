# Architecture and Data Flow

This section provides an overview of the main architectural components of the project, how data and control flow between them, and the key patterns used in the design.

## Main Architectural Components

### Web Server
- **File**: `test/index.ts`
- **Description**: The web server is built using Bun, a fast JavaScript runtime. It serves several endpoints for file uploads, secret handling, and visiting URLs. The server is configured to use TLS with a dynamically created certificate.
- **Key Functions/Classes**:
  - `setupServer()`: Configures the server, including TLS and Redis session management.
  - `visitUrl(url: string)`: Uses Puppeteer to control a headless browser for visiting URLs and setting cookies.

### Redis
- **Description**: Redis is used for session management and data storage. It stores file metadata, session information, and secrets.
- **Key Functions/Classes**:
  - `storeFileMetadata(fileMetadata: object)`: Stores file metadata in Redis.
  - `retrieveFileMetadata(id: string)`: Retrieves file metadata from Redis.
  - `storeSecret(secret: string)`: Stores a secret in Redis.
  - `checkSecret(secret: string)`: Checks a secret against a stored value in Redis.

### Puppeteer
- **Description**: Puppeteer is a Node library that provides a high-level API to control Chrome or Chromium over the DevTools Protocol. It is used to visit URLs and set cookies.
- **Key Functions/Classes**:
  - `visitUrl(url: string)`: Visits a URL using Puppeteer and sets a cookie with a secret.

## Data and Control Flow

### File Upload and Retrieval
1. **File Upload**:
   - **Endpoint**: `/upload` (POST)
   - **Flow**:
     - The client sends a file upload request to the `/upload` endpoint.
     - The server processes the file, stores its metadata in Redis, and redirects the client to a paper URL.
   - **Key Functions**:
     - `handleFileUpload(req: Request, res: Response)`: Handles the file upload request, stores metadata in Redis, and redirects the client.

2. **File Retrieval**:
   - **Endpoint**: `/paper/:id` (GET)
   - **Flow**:
     - The client requests a file by providing its ID in the URL.
     - The server retrieves the file metadata from Redis and serves the file.
   - **Key Functions**:
     - `handleFileRetrieval(req: Request, res: Response)`: Retrieves file metadata from Redis and serves the file.

### Secret Handling
1. **Secret Page**:
   - **Endpoint**: `/secret` (GET)
   - **Flow**:
     - The client requests a page with a secret and an optional payload parameter.
     - The server serves the page with the secret.
   - **Key Functions**:
     - `handleSecretPage(req: Request, res: Response)`: Serves the secret page.

2. **Flag Challenge**:
   - **Endpoint**: `/flag` (GET)
   - **Flow**:
     - The client provides a secret to the `/flag` endpoint.
     - The server checks the secret against a stored value in Redis and returns a flag if the secret matches.
   - **Key Functions**:
     - `handleFlagChallenge(req: Request, res: Response)`: Checks the secret and returns a flag if it matches.

### URL Visiting
1. **Visit URL**:
   - **Endpoint**: `/visit/:id` (GET)
   - **Flow**:
     - The client requests to visit a URL by providing its ID in the URL.
     - The server uses Puppeteer to visit the URL if the browser is not already open and sets a cookie with a secret.
   - **Key Functions**:
     - `handleVisitUrl(req: Request, res: Response)`: Visits the URL using Puppeteer and sets a cookie with a secret.

## Important Patterns

### Client/Server Pattern
- The web server acts as the server, handling HTTP requests from clients. The server processes these requests, interacts with Redis for data storage, and uses Puppeteer for browser automation.

### Event-Driven Architecture
- The server is event-driven, responding to HTTP requests and triggering actions such as file storage, secret handling, and URL visiting. Redis is used to store and retrieve data, and Puppeteer is used to perform browser actions based on these events.

### Layered Architecture
- The architecture is layered, with the web server at the top layer handling client requests, the Redis layer for data storage and session management, and the Puppeteer layer for browser automation.

### Security Considerations
- **TLS Configuration**: The server is configured to use TLS with a dynamically created certificate to ensure secure communication.
- **Session Management**: Redis is used for session management, storing session information securely.
- **Secret Handling**: Secrets are stored and checked against Redis to ensure they are handled securely.

By understanding these components and their interactions, you can better navigate and maintain the project.