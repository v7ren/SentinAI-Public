# Browser Automation

This section details how Puppeteer is used for browser automation and URL visiting within the project. The primary focus is on the `test/index.ts` file, which sets up a web server using the Bun framework and integrates Puppeteer for browser automation tasks.

## Overview

The `test/index.ts` file serves as the main entry point for the web server. It sets up various endpoints for file uploads, secret handling, and URL visiting. Puppeteer is used to automate browser actions, particularly for visiting URLs.

## Key Components

### 1. Server Setup
- **Framework**: Bun
- **Security**: Uses Redis for session management and file storage.
- **TLS**: Configured to use HTTPS with a self-signed certificate created using `mkcert`.

### 2. Puppeteer Integration
- **Browser Launch**: Puppeteer is used to launch a headless browser.
- **URL Visiting**: The `/visit/:id` endpoint uses Puppeteer to visit a specified URL if the browser is not already open.

## File: `test/index.ts`

### Server Initialization
- **CA Configuration**: Sets up a Certificate Authority (CA) and configures Chrome policies.
- **Redis Client**: Initializes a Redis client for session management and file storage.
- **HTTP Routes**: Defines several HTTP endpoints for file upload, retrieval, secret management, and URL visiting.

### HTTP Endpoints

#### 1. File Upload and Retrieval
- **Endpoint**: `/`
  - **Method**: GET
  - **Details**: Serves a simple HTML form for file uploads.
- **Endpoint**: `/upload`
  - **Method**: POST
  - **Details**: Handles file uploads and stores file metadata in Redis.
- **Endpoint**: `/paper/:id`
  - **Method**: GET
  - **Details**: Retrieves and serves a file from Redis based on the provided ID.

#### 2. Secret Management
- **Endpoint**: `/secret`
  - **Method**: GET
  - **Details**: Serves a page with a secret value and an optional payload.
- **Endpoint**: `/flag`
  - **Method**: GET
  - **Details**: Checks a provided secret against the stored secret in Redis and returns a flag if they match.

#### 3. URL Visiting
- **Endpoint**: `/visit/:id`
  - **Method**: GET
  - **Details**: Visits a URL using Puppeteer if the browser is not already open.

### Puppeteer Usage

#### Browser Launch
- **Function**: `visit`
  - **Details**: This function is responsible for launching a headless browser using Puppeteer. It checks if the browser is already open and, if not, launches a new instance.
  - **Example**:
    ```typescript
    async function visit(url: string) {
      if (!browser) {
        browser = await puppeteer.launch({ headless: true });
      }
      const page = await browser.newPage();
      await page.goto(url);
      // Additional actions can be performed on the page
    }
    ```

#### URL Visiting
- **Endpoint**: `/visit/:id`
  - **Details**: This endpoint calls the `visit` function to navigate to the specified URL.
  - **Example**:
    ```typescript
    app.get('/visit/:id', async (req, res) => {
      const url = req.params.id;
      try {
        await visit(url);
        res.send(`Visited URL: ${url}`);
      } catch (error) {
        res.status(500).send(`Error visiting URL: ${error.message}`);
      }
    });
    ```

## Security Considerations

- **TLS Configuration**: The server is configured to use HTTPS with a self-signed certificate created using `mkcert`.
- **Session Management**: Redis is used for session management, ensuring secure handling of user sessions and file metadata.

## Conclusion

The `test/index.ts` file demonstrates a comprehensive setup for a web server that integrates Puppeteer for browser automation. The server handles file uploads, secret management, and URL visiting, all while ensuring security through TLS and Redis session management. The `/visit/:id` endpoint is a key component for automating browser actions, making it a crucial part of the browser automation workflow.