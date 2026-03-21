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

---

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

---

# HTTP Endpoints

This section documents the available HTTP endpoints in the project, including their methods, paths, and functionalities. The web server is built using Bun and is configured to use TLS with a dynamically created certificate. Redis is used for session management and data storage.

## Overview

The project provides several endpoints for file uploads, secret handling, and URL visits. The server is designed to handle both simple and complex interactions, leveraging Redis for session management and Puppeteer for browser automation.

## Endpoints

### Root (`/`)

- **Method**: GET
- **Path**: `/`
- **Functionality**: Serves a simple HTML form for file uploads.
- **File**: `test/index.ts`

### File Upload (`/upload`)

- **Method**: POST
- **Path**: `/upload`
- **Functionality**: Handles POST requests for file uploads. It stores file metadata in Redis and redirects to a paper URL.
- **File**: `test/index.ts`

### Paper Retrieval (`/paper/:id`)

- **Method**: GET
- **Path**: `/paper/:id`
- **Functionality**: Retrieves and serves a file from Redis based on the provided ID.
- **File**: `test/index.ts`

### Secret Page (`/secret`)

- **Method**: GET
- **Path**: `/secret`
- **Functionality**: Serves a page with a secret and an optional payload parameter.
- **File**: `test/index.ts`

### Flag Challenge (`/flag`)

- **Method**: GET
- **Path**: `/flag`
- **Functionality**: Checks a secret against a stored value in Redis and returns a flag if the secret matches.
- **File**: `test/index.ts`

### Visit Tracker (`/visit/:id`)

- **Method**: GET
- **Path**: `/visit/:id`
- **Functionality**: Visits a URL using Puppeteer if the browser is not already open, and sets a cookie with a secret.
- **File**: `test/index.ts`

## Interaction Flows

### File Upload and Retrieval

1. **Upload Form**: The root endpoint (`/`) serves an HTML form for file uploads.
2. **File Upload**: When a user submits the form, a POST request is sent to the `/upload` endpoint. This endpoint processes the file, stores its metadata in Redis, and redirects the user to a paper URL.
3. **Paper Retrieval**: The user can access the uploaded file by visiting the `/paper/:id` endpoint, where `:id` is the unique identifier for the file stored in Redis.

### Secret Handling

1. **Secret Page**: The `/secret` endpoint serves a page containing a secret and an optional payload parameter.
2. **Flag Challenge**: The `/flag` endpoint checks the provided secret against a stored value in Redis. If the secret matches, it returns a flag.

### URL Visits

1. **Visit Tracker**: The `/visit/:id` endpoint is used to visit a URL using Puppeteer. If the browser is not already open, it will be started. The endpoint sets a cookie with a secret and then visits the specified URL.

## Configuration and Security

- **TLS Configuration**: The server is configured to use TLS with a dynamically created certificate.
- **Session Management**: Redis is used for session management, ensuring that user sessions are securely stored and managed.
- **Puppeteer**: Puppeteer is used to control a headless browser for visiting URLs and setting cookies.

By following these endpoints and their interactions, you can understand how the web server handles file uploads, secret handling, and URL visits in a secure and efficient manner.

---

# Session Management

This section provides an overview of how sessions are managed within the project, focusing on the use of Redis for session storage and the integration with the web server.

## Overview

The project uses Redis as the primary storage mechanism for session data. This includes storing session tokens, user data, and other relevant information. The web server, built using Bun, is configured to interact with Redis for session management, ensuring that session data is securely stored and efficiently accessed.

## Key Components

### Redis Configuration

- **File:** `test/index.ts`
- **Functionality:** The project sets up a Redis client to handle session storage. This client is used across various endpoints to store and retrieve session data.

### Session Management Endpoints

The web server includes several endpoints that interact with Redis for session management:

- **`/` (GET)**
  - **Description:** Serves a simple HTML form for file uploads.
  - **Session Interaction:** No direct session interaction.

- **`/upload` (POST)**
  - **Description:** Handles POST requests for file uploads, stores file metadata in Redis, and redirects to a paper URL.
  - **Session Interaction:** Stores file metadata in Redis, which can be associated with the user's session.

- **`/paper/:id` (GET)**
  - **Description:** Retrieves and serves a file from Redis based on the provided ID.
  - **Session Interaction:** Retrieves file metadata from Redis, which is linked to the user's session.

- **`/secret` (GET)**
  - **Description:** Serves a page with a secret and an optional payload parameter.
  - **Session Interaction:** May store or retrieve the secret in Redis, depending on the application logic.

- **`/flag` (GET)**
  - **Description:** Checks a secret against a stored value in Redis and returns a flag if the secret matches.
  - **Session Interaction:** Retrieves the stored secret from Redis and compares it with the provided secret.

- **`/visit/:id` (GET)**
  - **Description:** Visits a URL using Puppeteer if the browser is not already open, and sets a cookie with a secret.
  - **Session Interaction:** Sets a cookie with a secret, which can be stored in Redis for future reference.

## Session Storage and Retrieval

### Storing Session Data

- **File:** `test/index.ts`
- **Functionality:** When a user interacts with the web server, session data is stored in Redis. This includes session tokens, user data, and any other relevant information. The Redis client is used to write this data to the Redis store.

### Retrieving Session Data

- **File:** `test/index.ts`
- **Functionality:** When a user makes a request to the server, the session data is retrieved from Redis. This data is used to authenticate the user and provide personalized content or actions.

## Security Considerations

- **TLS Configuration:** The web server is configured to use TLS with a dynamically created certificate, ensuring secure communication between the client and server.
- **Session Tokens:** Session tokens are securely stored in Redis and are used to authenticate and authorize user requests.
- **Cookie Management:** Cookies are used to manage session state on the client side. These cookies are set with appropriate security flags (e.g., `HttpOnly`, `Secure`) to prevent cross-site scripting (XSS) and cross-site request forgery (CSRF) attacks.

## Example Flow

1. **User Login:**
   - The user logs in to the application.
   - A session token is generated and stored in Redis.
   - A cookie is set on the client side with the session token.

2. **File Upload:**
   - The user uploads a file via the `/upload` endpoint.
   - The file metadata is stored in Redis, associated with the user's session token.

3. **File Retrieval:**
   - The user requests a file via the `/paper/:id` endpoint.
   - The server retrieves the file metadata from Redis using the session token.
   - The file is served to the user.

4. **Secret Access:**
   - The user requests a secret via the `/secret` endpoint.
   - The server retrieves the secret from Redis and serves it to the user.

5. **Flag Challenge:**
   - The user provides a secret via the `/flag` endpoint.
   - The server retrieves the stored secret from Redis and compares it with the provided secret.
   - If the secret matches, a flag is returned to the user.

6. **URL Visit:**
   - The user requests to visit a URL via the `/visit/:id` endpoint.
   - The server uses Puppeteer to visit the URL and sets a cookie with a secret.
   - The cookie is stored in Redis for future reference.

By leveraging Redis for session management, the project ensures that session data is securely stored and efficiently accessed, providing a robust and scalable solution for managing user sessions.

---

# Security

This section details the security measures implemented in the project, focusing on TLS configuration and secret handling.

## TLS Configuration

### Overview
The project uses TLS (Transport Layer Security) to secure communication between the client and the server. This is achieved by dynamically creating and configuring a certificate for the server.

### Implementation
- **File**: `test/index.ts`
- **Chunk**: `test/index.ts:121-183`

#### Key Components
- **Certificate Creation**: The server dynamically creates a certificate for TLS. This is done to ensure secure communication over HTTPS.
- **Server Configuration**: The server is configured to use the created certificate for all HTTPS connections.

#### Code Snippet
```typescript
// Example of TLS configuration in test/index.ts
const tlsOptions = {
  key: fs.readFileSync('path/to/private/key.pem'),
  cert: fs.readFileSync('path/to/certificate.pem'),
};

const server = Bun.serve({
  port: 443,
  tls: tlsOptions,
  fetch: (req) => {
    // Handle incoming requests
  },
});
```

## Secret Handling

### Overview
The project includes mechanisms for handling secrets securely, particularly in the context of user authentication and data protection.

### Implementation
- **File**: `test/index.ts`
- **Chunk**: `test/index.ts:121-183`

#### Key Endpoints
- **Secret Page**: The `/secret` endpoint serves a page with a secret and an optional payload parameter.
- **Flag Challenge**: The `/flag` endpoint checks a secret against a stored value in Redis and returns a flag if the secret matches.
- **Visit Tracker**: The `/visit/:id` endpoint visits a URL using Puppeteer and sets a cookie with a secret.

#### Code Snippets
- **Secret Page**
  ```typescript
  app.get('/secret', (req, res) => {
    const payload = req.query.payload;
    res.send(`Secret: ${process.env.SECRET} Payload: ${payload}`);
  });
  ```

- **Flag Challenge**
  ```typescript
  app.get('/flag', (req, res) => {
    const secret = req.query.secret;
    const storedSecret = redis.get('storedSecret');
    if (secret === storedSecret) {
      res.send('Flag: ' + process.env.FLAG);
    } else {
      res.send('Invalid secret');
    }
  });
  ```

- **Visit Tracker**
  ```typescript
  app.get('/visit/:id', async (req, res) => {
    const id = req.params.id;
    const url = redis.get(`url:${id}`);
    if (!browser) {
      browser = await puppeteer.launch();
    }
    const page = await browser.newPage();
    await page.goto(url);
    await page.setCookie({ name: 'secret', value: process.env.SECRET });
    res.send('Visited URL and set cookie');
  });
  ```

### Security Considerations
- **Environment Variables**: Secrets such as the `SECRET` and `FLAG` are stored in environment variables to avoid hardcoding them in the source code.
- **Redis Storage**: Sensitive data like stored secrets and URLs are managed in Redis, which is configured to be secure and accessible only by the server.
- **Session Management**: The server uses Redis for session management, ensuring that session data is securely stored and managed.

## Conclusion
The project implements robust security measures, including TLS for secure communication and secure handling of secrets. These measures are crucial for protecting user data and ensuring the integrity of the application.

---