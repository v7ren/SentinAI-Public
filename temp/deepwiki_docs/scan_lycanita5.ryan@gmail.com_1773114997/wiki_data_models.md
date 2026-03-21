# Data Models

This section provides detailed descriptions of the database models used in the TaskFlow application. The models define the structure of the database tables, their relationships, and schema definitions.

## Database Configuration

The database configuration is set up in the file `taskflow/backend/config/db.js`. This file initializes a PostgreSQL database connection pool using the `pg` library. The connection pool is configured with environment variables or fallbacks for local development. The pool and a query function for executing SQL queries are exported for use in other parts of the application.

### Key Entities
- **Database Pool**: Manages database connections.
- **Query Function**: Executes SQL queries using the configured database pool.

### Example Usage
```javascript
const { query } = require('./config/db');

query('SELECT * FROM users').then(result => {
  console.log(result.rows);
});
```

## User Model

The user model is defined in `taskflow/backend/src/models/userModel.js`. It provides methods to interact with the `users` table in the database, including finding, creating, and updating user records. The model also handles refresh tokens, reset tokens, and password updates.

### Key Methods
- **`findByEmail(email)`**: Finds a user by email.
- **`create(user)`**: Creates a new user record.
- **`updateRefreshToken(userId, token)`**: Updates the refresh token for a user.
- **`setResetToken(userId, token)`**: Sets a password reset token for a user.
- **`clearResetToken(userId)`**: Clears the password reset token for a user.
- **`updatePassword(userId, password)`**: Updates the user's password.

### Example Usage
```javascript
const { findByEmail, create } = require('./models/userModel');

findByEmail('user@example.com').then(user => {
  if (!user) {
    create({ email: 'user@example.com', password: 'hashedPassword' });
  }
});
```

## Task Model

The task model is defined in `taskflow/backend/src/models/taskModel.js`. It provides methods to interact with the `tasks` table in the database, including finding tasks by ID or project, creating new tasks, updating existing tasks, and removing tasks.

### Key Methods
- **`findById(taskId)`**: Finds a task by its ID.
- **`findByProject(projectId)`**: Finds tasks associated with a specific project.
- **`create(task)`**: Creates a new task.
- **`update(taskId, data)`**: Updates an existing task.
- **`remove(taskId)`**: Deletes a task.

### Example Usage
```javascript
const { findById, create, update, remove } = require('./models/taskModel');

findById(1).then(task => {
  if (task) {
    update(1, { title: 'Updated Task' });
  } else {
    create({ projectId: 1, title: 'New Task' });
  }
});
```

## Project Model

The project model is defined in `taskflow/backend/src/models/projectModel.js`. It provides methods to interact with the `projects` table in the database, including finding, creating, updating, and deleting project records. The model also supports finding projects by organization ID.

### Key Methods
- **`findById(projectId)`**: Finds a project by its ID.
- **`findByOrg(orgId, includeArchived = false)`**: Finds projects by organization ID, optionally including archived projects.
- **`create(project)`**: Creates a new project.
- **`update(projectId, data)`**: Updates an existing project.
- **`remove(projectId)`**: Deletes a project.

### Example Usage
```javascript
const { findById, create, update, remove } = require('./models/projectModel');

findById(1).then(project => {
  if (project) {
    update(1, { name: 'Updated Project' });
  } else {
    create({ orgId: 1, name: 'New Project' });
  }
});
```

## Organization Model

The organization model is defined in `taskflow/backend/src/models/orgModel.js`. It provides methods to interact with the `orgs` and `org_members` tables in the database, including finding an organization by ID, creating a new organization, adding a member to an organization, and retrieving the members of an organization.

### Key Methods
- **`findById(orgId)`**: Finds an organization by its ID.
- **`create(org)`**: Creates a new organization.
- **`addMember(orgId, userId, role)`**: Adds a member to an organization with a specified role.
- **`getMembers(orgId)`**: Retrieves the members of an organization, including their user details and role within the organization.

### Example Usage
```javascript
const { findById, create, addMember, getMembers } = require('./models/orgModel');

findById(1).then(org => {
  if (!org) {
    create({ name: 'New Organization' }).then(newOrg => {
      addMember(newOrg.id, 1, 'admin');
    });
  }
});

getMembers(1).then(members => {
  console.log(members);
});
```

## Attachment Model

The attachment model is defined in `taskflow/backend/src/controllers/attachmentController.js`. It provides methods to manage task attachments, including listing, uploading, downloading, and removing attachments. The model interacts with the database and the file system to perform these operations.

### Key Methods
- **`list(taskId)`**: Lists attachments for a specific task.
- **`upload(taskId, file)`**: Uploads a file as an attachment to a specific task.
- **`download(attachmentId)`**: Downloads an attachment by its ID.
- **`remove(attachmentId)`**: Removes an attachment by its ID.

### Example Usage
```javascript
const { list, upload, download, remove } = require('./controllers/attachmentController');

list(1).then(attachments => {
  console.log(attachments);
});

upload(1, file).then(attachment => {
  console.log(attachment);
});
```

## Notification Model

The notification model is defined in `taskflow/backend/src/controllers/notificationController.js` and `taskflow/backend/src/services/notificationService.js`. It provides methods to manage user notifications, including listing notifications, marking them as read, and managing user preferences.

### Key Methods
- **`list(userId, limit)`**: Lists notifications for a user, with an optional limit.
- **`markRead(userId, notificationId)`**: Marks a specific notification as read for a user.
- **`getPreferences(userId)`**: Retrieves the notification preferences for a user.
- **`updatePreferences(userId, preferences)`**: Updates the notification preferences for a user.

### Example Usage
```javascript
const { list, markRead, getPreferences, updatePreferences } = require('./controllers/notificationController');

list(1, 10).then(notifications => {
  console.log(notifications);
});

markRead(1, 1).then(() => {
  console.log('Notification marked as read');
});

getPreferences(1).then(preferences => {
  console.log(preferences);
});

updatePreferences(1, { email: true, sms: false }).then(() => {
  console.log('Preferences updated');
});
```

## Summary

The data models in the TaskFlow application are designed to provide a robust and flexible way to manage user, task, project, organization, attachment, and notification data. Each model includes methods for common database operations, ensuring that the application can efficiently interact with the PostgreSQL database. The models are used throughout the application to handle data retrieval, creation, updating, and deletion, forming the core of the application's data management layer.