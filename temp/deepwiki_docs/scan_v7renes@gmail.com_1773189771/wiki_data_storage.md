# Data Storage

This section provides an overview of how data is stored and managed within the project, with a particular focus on the use of Redis for session and file metadata.

## Overview

The project uses Redis as the primary data store for session management and file metadata. Redis is a fast, in-memory data store that supports various data structures, making it suitable for this application's needs. The following sections detail how Redis is integrated into the application and the specific data it manages.

## Redis Configuration

### Initialization

The Redis client is initialized in the `test/index.ts` file. This setup is crucial for establishing a connection to the Redis server and ensuring that the application can read from and write to the database.

```typescript
// test/index.ts:1-120
import { createClient } from 'redis';

const redisClient = createClient({
  url: 'redis://localhost:6379',
});

redisClient.connect().then(() => {
  console.log('Connected to Redis');
}).catch((error) => {
  console.error('Failed to connect to Redis:', error);
});
```

## Data Storage and Management

### Session Management

The application uses Redis to manage user sessions. When a user logs in or performs actions that require session management, session data is stored in Redis. This ensures that session information is persistent and can be accessed across different parts of the application.

### File Metadata

File metadata is stored in Redis when files are uploaded to the server. This metadata includes information such as the file ID, name, and any other relevant details. The metadata is used to retrieve and serve files when requested by the client.

#### File Upload

When a file is uploaded, the metadata is stored in Redis. The `/upload` endpoint handles this process:

```typescript
// test/index.ts:121-183
app.post('/upload', async (req, res) => {
  const file = req.files.file;
  const fileId = generateFileId();
  const metadata = {
    id: fileId,
    name: file.name,
    size: file.size,
  };

  await redisClient.set(`file:${fileId}`, JSON.stringify(metadata));
  res.json({ id: fileId });
});
```

#### File Retrieval

When a file is requested, the metadata is retrieved from Redis and used to serve the file. The `/paper/:id` endpoint handles this process:

```typescript
// test/index.ts:121-183
app.get('/paper/:id', async (req, res) => {
  const fileId = req.params.id;
  const metadata = await redisClient.get(`file:${fileId}`);

  if (metadata) {
    const fileMetadata = JSON.parse(metadata);
    // Serve the file based on the metadata
    res.json(fileMetadata);
  } else {
    res.status(404).json({ error: 'File not found' });
  }
});
```

## Security Considerations

### TLS Configuration

The web server is configured to use TLS with a self-signed certificate. This ensures that data transmitted between the client and server is encrypted, providing an additional layer of security.

```typescript
// test/index.ts:1-120
import { createServer } from 'https';
import fs from 'fs';

const ca = createCA();
const key = fs.readFileSync('path/to/private/key.pem');
const cert = fs.readFileSync('path/to/certificate.pem');

const server = createServer({ ca, key, cert }, app);
server.listen(3000, () => {
  console.log('Server running on https://localhost:3000');
});
```

## Summary

In summary, Redis plays a crucial role in the data storage and management of this application. It is used for session management and storing file metadata, ensuring that data is persistent and accessible. The application is also configured to use TLS for secure data transmission. By leveraging Redis and TLS, the application provides a robust and secure data management solution.