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