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