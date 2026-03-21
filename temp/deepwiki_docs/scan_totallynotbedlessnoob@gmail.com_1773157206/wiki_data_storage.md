# Data Storage

This section provides an overview of how data is stored and managed within the project, with a particular focus on the use of Redis for session and file data storage.

## Overview

The project uses Redis as the primary data store for managing session data and file metadata. Redis is a fast, in-memory data store that supports various data structures, making it suitable for this application's needs. The following sections detail how Redis is integrated into the project and the specific data storage mechanisms used.

## Redis Configuration

### File: `test/index.ts`

The Redis client is configured and initialized in the `test/index.ts` file. This file sets up the web server and defines the endpoints for file uploads, secret handling, and URL visits. The Redis client is used to store and retrieve session data and file metadata.

```typescript
// test/index.ts:1-120
import { createClient } from 'redis';
const redisClient = createClient({
  url: 'redis://localhost:6379',
});

redisClient.connect().then(() => {
  console.log('Connected to Redis');
});
```

## Data Storage Mechanisms

### File Uploads

When a user uploads a file, the file metadata is stored in Redis. The metadata includes the file ID, name, and other relevant information. The file content itself is not stored in Redis but is managed separately.

#### Endpoint: `/upload`

- **Method**: POST
- **Path**: `/upload`
- **Details**: Handles file uploads, stores file metadata in Redis, and redirects to a paper URL.

```typescript
// test/index.ts:121-183
app.post('/upload', async (req, res) => {
  const file = req.files.file;
  const fileId = generateFileId();
  await redisClient.set(`file:${fileId}`, JSON.stringify({ name: file.name, size: file.size }));
  res.redirect(`/paper/${fileId}`);
});
```

### File Retrieval

When a user requests a file, the file metadata is retrieved from Redis using the provided file ID.

#### Endpoint: `/paper/:id`

- **Method**: GET
- **Path**: `/paper/:id`
- **Details**: Retrieves and serves a file from Redis based on the provided ID.

```typescript
// test/index.ts:121-183
app.get('/paper/:id', async (req, res) => {
  const fileId = req.params.id;
  const fileMetadata = await redisClient.get(`file:${fileId}`);
  if (fileMetadata) {
    const { name, size } = JSON.parse(fileMetadata);
    res.send(`File: ${name}, Size: ${size}`);
  } else {
    res.status(404).send('File not found');
  }
});
```

### Secret Handling

The project also uses Redis to store and manage secret values. These secrets can be retrieved and verified through specific endpoints.

#### Endpoint: `/secret`

- **Method**: GET
- **Path**: `/secret`
- **Details**: Returns a secret value and an optional payload in an HTML response.

```typescript
// test/index.ts:121-183
app.get('/secret', async (req, res) => {
  const secret = await redisClient.get('secret');
  res.send(`<html><body>Secret: ${secret}</body></html>`);
});
```

#### Endpoint: `/flag`

- **Method**: GET
- **Path**: `/flag`
- **Details**: Checks a guessed secret against the stored secret in Redis and returns a flag if correct.

```typescript
// test/index.ts:121-183
app.get('/flag', async (req, res) => {
  const guessedSecret = req.query.guess;
  const storedSecret = await redisClient.get('secret');
  if (guessedSecret === storedSecret) {
    res.send('Flag: Correct!');
  } else {
    res.send('Flag: Incorrect!');
  }
});
```

### URL Visits

The project uses Redis to track URL visits. When a user requests to visit a URL, the server checks if the file exists in Redis and then uses Puppeteer to browse the URL.

#### Endpoint: `/visit/:id`

- **Method**: GET
- **Path**: `/visit/:id`
- **Details**: Visits a URL using Puppeteer if the browser is not already open and the file exists in Redis.

```typescript
// test/index.ts:1-120
async function visit(url: string) {
  if (!browser) {
    browser = await puppeteer.launch();
  }
  const page = await browser.newPage();
  await page.goto(url);
  await page.close();
}

// test/index.ts:121-183
app.get('/visit/:id', async (req, res) => {
  const fileId = req.params.id;
  const fileMetadata = await redisClient.get(`file:${fileId}`);
  if (fileMetadata) {
    const { name } = JSON.parse(fileMetadata);
    await visit(name);
    res.send('Visited URL');
  } else {
    res.status(404).send('File not found');
  }
});
```

## Conclusion

Redis plays a crucial role in the project by providing a fast and efficient way to store and manage session data and file metadata. The integration of Redis with the web server and other components ensures that data is handled securely and efficiently. The endpoints for file uploads, secret handling, and URL visits demonstrate the practical use of Redis in various aspects of the application.