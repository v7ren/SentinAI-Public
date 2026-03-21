# Data Management

This section explains the data models and database interactions in the TaskFlow application, including how projects, tasks, users, and other entities are managed and queried.

## Database Configuration

### File: `taskflow/backend/config/db.js`

The database configuration is handled in `taskflow/backend/config/db.js`. This file sets up a PostgreSQL database connection pool using the `pg` library. It configures the pool with environment variables or fallback values for local development. The file exports two main entities:

- **`pool`**: A PostgreSQL connection pool instance that can be used to execute queries.
- **`query`**: A function that takes SQL text and parameters, and executes the query using the connection pool.

```javascript
// taskflow/backend/config/db.js
const { Pool } = require('pg');

const pool = new Pool({
  user: process.env.DB_USER || 'defaultUser',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'taskflow',
  password: process.env.DB_PASSWORD || 'defaultPassword',
  port: process.env.DB_PORT || 5432,
});

const query = (text, params) => pool.query(text, params);

module.exports = { pool, query };
```

## Data Models

### Project Model

### File: `taskflow/backend/src/models/projectModel.js`

The `projectModel.js` file defines a set of asynchronous functions for interacting with the `projects` table in the database. These functions include:

- **`find`**: Finds projects based on specified criteria.
- **`create`**: Creates a new project.
- **`update`**: Updates an existing project.
- **`remove`**: Deletes a project.

```javascript
// taskflow/backend/src/models/projectModel.js
const { query } = require('../config/db');

const find = async (criteria) => {
  const result = await query('SELECT * FROM projects WHERE $1', [criteria]);
  return result.rows;
};

const create = async (project) => {
  const result = await query('INSERT INTO projects (name, description, organization_id) VALUES ($1, $2, $3) RETURNING *', [project.name, project.description, project.organization_id]);
  return result.rows[0];
};

const update = async (id, updates) => {
  const result = await query('UPDATE projects SET name = $1, description = $2 WHERE id = $3 RETURNING *', [updates.name, updates.description, id]);
  return result.rows[0];
};

const remove = async (id) => {
  await query('DELETE FROM projects WHERE id = $1', [id]);
};

module.exports = { find, create, update, remove };
```

### Task Model

### File: `taskflow/backend/src/models/taskModel.js`

The `taskModel.js` file defines a set of asynchronous functions for interacting with the `tasks` table in the database. These functions include:

- **`find`**: Finds tasks based on specified criteria.
- **`create`**: Creates a new task.
- **`update`**: Updates an existing task.
- **`remove`**: Deletes a task.

```javascript
// taskflow/backend/src/models/taskModel.js
const { query } = require('../config/db');

const find = async (criteria) => {
  const result = await query('SELECT * FROM tasks WHERE $1', [criteria]);
  return result.rows;
};

const create = async (task) => {
  const result = await query('INSERT INTO tasks (title, description, project_id, status, priority, due_date) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *', [task.title, task.description, task.project_id, task.status, task.priority, task.due_date]);
  return result.rows[0];
};

const update = async (id, updates) => {
  const result = await query('UPDATE tasks SET title = $1, description = $2, status = $3, priority = $4, due_date = $5 WHERE id = $6 RETURNING *', [updates.title, updates.description, updates.status, updates.priority, updates.due_date, id]);
  return result.rows[0];
};

const remove = async (id) => {
  await query('DELETE FROM tasks WHERE id = $1', [id]);
};

module.exports = { find, create, update, remove };
```

### User Model

### File: `taskflow/backend/src/models/userModel.js`

The `userModel.js` file defines a set of asynchronous functions for interacting with the `users` table in the database. These functions include:

- **`find`**: Finds users based on specified criteria.
- **`create`**: Creates a new user.
- **`update`**: Updates an existing user.
- **`remove`**: Deletes a user.

```javascript
// taskflow/backend/src/models/userModel.js
const { query } = require('../config/db');

const find = async (criteria) => {
  const result = await query('SELECT * FROM users WHERE $1', [criteria]);
  return result.rows;
};

const create = async (user) => {
  const result = await query('INSERT INTO users (email, password, name) VALUES ($1, $2, $3) RETURNING *', [user.email, user.password, user.name]);
  return result.rows[0];
};

const update = async (id, updates) => {
  const result = await query('UPDATE users SET email = $1, name = $2 WHERE id = $3 RETURNING *', [updates.email, updates.name, id]);
  return result.rows[0];
};

const remove = async (id) => {
  await query('DELETE FROM users WHERE id = $1', [id]);
};

module.exports = { find, create, update, remove };
```

### Organization Model

### File: `taskflow/backend/src/models/orgModel.js`

The `orgModel.js` file defines a set of functions for interacting with the `orgs` and `org_members` tables in the database. These functions include:

- **`findById`**: Finds an organization by its ID.
- **`create`**: Creates a new organization.
- **`addMember`**: Adds a member to an organization.
- **`getMembers`**: Retrieves the members of an organization.

```javascript
// taskflow/backend/src/models/orgModel.js
const { query } = require('../config/db');

const findById = async (id) => {
  const result = await query('SELECT * FROM orgs WHERE id = $1', [id]);
  return result.rows[0];
};

const create = async (org) => {
  const result = await query('INSERT INTO orgs (name) VALUES ($1) RETURNING *', [org.name]);
  return result.rows[0];
};

const addMember = async (orgId, userId) => {
  await query('INSERT INTO org_members (org_id, user_id) VALUES ($1, $2)', [orgId, userId]);
};

const getMembers = async (orgId) => {
  const result = await query('SELECT users.* FROM users JOIN org_members ON users.id = org_members.user_id WHERE org_members.org_id = $1', [orgId]);
  return result.rows;
};

module.exports = { findById, create, addMember, getMembers };
```

## Data Management Controllers

### Project Controller

### File: `taskflow/backend/src/controllers/projectController.js`

The `projectController.js` file contains controller functions for managing projects. These functions interact with the `projectModel` to perform database operations and return appropriate HTTP responses. The functions include:

- **`list`**: Lists projects for a specific organization.
- **`getOne`**: Retrieves a single project by ID.
- **`create`**: Creates a new project.
- **`update`**: Updates an existing project.
- **`remove`**: Deletes a project.

```javascript
// taskflow/backend/src/controllers/projectController.js
const { find, create, update, remove } = require('../models/projectModel');

const list = async (req, res) => {
  const projects = await find({ organization_id: req.user.organization_id });
  res.json(projects);
};

const getOne = async (req, res) => {
  const project = await find({ id: req.params.projectId, organization_id: req.user.organization_id });
  if (!project) return res.status(404).json({ message: 'Project not found' });
  res.json(project);
};

const create = async (req, res) => {
  const project = await create({ name: req.body.name, description: req.body.description, organization_id: req.user.organization_id });
  res.status(201).json(project);
};

const update = async (req, res) => {
  const project = await find({ id: req.params.projectId, organization_id: req.user.organization_id });
  if (!project) return res.status(404).json({ message: 'Project not found' });
  const updatedProject = await update(req.params.projectId, req.body);
  res.json(updatedProject);
};

const remove = async (req, res) => {
  const project = await find({ id: req.params.projectId, organization_id: req.user.organization_id });
  if (!project) return res.status(404).json({ message: 'Project not found' });
  await remove(req.params.projectId);
  res.json({ message: 'Project deleted' });
};

module.exports = { list, getOne, create, update, remove };
```

### Task Controller

### File: `taskflow/backend/src/controllers/taskController.js`

The `taskController.js` file contains controller functions for managing tasks. These functions interact with the `taskModel` to perform database operations and return appropriate HTTP responses. The functions include:

- **`list`**: Lists tasks for a specific project or across an organization.
- **`getOne`**: Retrieves a single task by ID.
- **`create`**: Creates a new task.
- **`update`**: Updates an existing task.
- **`remove`**: Deletes a task.

```javascript
// taskflow/backend/src/controllers/taskController.js
const { find, create, update, remove } = require('../models/taskModel');

const list = async (req, res) => {
  const tasks = await find({ project_id: req.params.projectId });
  res.json(tasks);
};

const getOne = async (req, res) => {
  const task = await find({ id: req.params.taskId });
  if (!task) return res.status(404).json({ message: 'Task not found' });
  res.json(task);
};

const create = async (req, res) => {
  const task = await create({ title: req.body.title, description: req.body.description, project_id: req.params.projectId, status: req.body.status, priority: req.body.priority, due_date: req.body.due_date });
  res.status(201).json(task);
};

const update = async (req, res) => {
  const task = await find({ id: req.params.taskId });
  if (!task) return res.status(404).json({ message: 'Task not found' });
  const updatedTask = await update(req.params.taskId, req.body);
  res.json(updatedTask);
};

const remove = async (req, res) => {
  const task = await find({ id: req.params.taskId });
  if (!task) return res.status(404).json({ message: 'Task not found' });
  await remove(req.params.taskId);
  res.json({ message: 'Task deleted' });
};

module.exports = { list, getOne, create, update, remove };
```

### User Controller

### File: `taskflow/backend/src/controllers/userController.js`

The `userController.js` file contains controller functions for managing user profiles. These functions interact with the `userModel` to perform database operations and return appropriate HTTP responses. The functions include:

- **`getProfile`**: Retrieves a user's profile information.
- **`updateProfile`**: Updates a user's profile information.

```javascript
// taskflow/backend/src/controllers/userController.js
const { find, update } = require('../models/userModel');

const getProfile = async (req, res) => {
  const user = await find({ id: req.user.id });
  if (!user) return res.status(404).json({ message: 'User not found' });
  res.json(user);
};

const updateProfile = async (req, res) => {
  const user = await find({ id: req.user.id });
  if (!user) return res.status(404).json({ message: 'User not found' });
  const updatedUser = await update(req.user.id, req.body);
  res.json(updatedUser);
};

module.exports = { getProfile, updateProfile };
```

## Data Management Routes

### Project Routes

### File: `taskflow/backend/src/routes/projectRoutes.js`

The `projectRoutes.js` file sets up an Express router for project-related endpoints. All routes require authentication. The routes include:

- **`GET /`**: Lists all projects.
- **`GET /:projectId`**: Retrieves a single project by ID.
- **`POST /`**: Creates a new project.
- **`PUT /:projectId`**: Updates an existing project by ID.
- **`DELETE /:projectId`**: Deletes a project by ID.

```javascript
// taskflow/backend/src/routes/projectRoutes.js
const express = require('express');
const router = express.Router();
const { authenticate, authorize } = require('../middleware/authenticate');
const { list, getOne, create, update, remove } = require('../controllers/projectController');

router.use(authenticate);

router.get('/', list);
router.get('/:projectId', getOne);
router.post('/', create);
router.put('/:projectId', update);
router.delete('/:projectId', remove);

module.exports = router;
```

### Task Routes

### File: `taskflow/backend/src/routes/taskRoutes.js`

The `taskRoutes.js` file sets up an Express router for task-related endpoints. All routes require authentication. The routes include:

- **`GET /`**: Lists all tasks.
- **`GET /:taskId/comments`**: Retrieves comments for a specific task.
- **`POST /:taskId/comments`**: Adds a comment to a specific task.
- **`GET /:taskId`**: Retrieves a single task by ID.
- **`POST /`**: Creates a new task.
- **`PUT /:taskId`**: Updates an existing task by ID.
- **`DELETE /:taskId`**: Deletes a task by ID.

```javascript
// taskflow/backend/src/routes/taskRoutes.js
const express = require('express');
const router = express.Router();
const { authenticate, authorize } = require('../middleware/authenticate');
const { list, getComments, addComment, getOne, create, update, remove } = require('../controllers/taskController');

router.use(authenticate);

router.get('/', list);
router.get('/:taskId/comments', getComments);
router.post('/:taskId/comments', addComment);
router.get('/:taskId', getOne);
router.post('/', create);
router.put('/:taskId', update);
router.delete('/:taskId', remove);

module.exports = router;
```

### User Routes

### File: `taskflow/backend/src/routes/userRoutes.js`

The `userRoutes.js` file sets up an Express router for user-related endpoints. All routes require authentication. The routes include:

- **`GET /profile`**: Retrieves the user's profile information.
- **`PATCH /profile`**: Updates the user's profile information.

```javascript
// taskflow/backend/src/routes/userRoutes.js
const express = require('express');
const router = express.Router();
const { authenticate } = require('../middleware/authenticate');
const { getProfile, updateProfile } = require('../controllers/userController');

router.use(authenticate);

router.get('/profile', getProfile);
router.patch('/profile', updateProfile);

module.exports = router;
```

## Data Management Services

### Notification Service

### File: `taskflow/backend/src/services/notificationService.js`

The `notificationService.js` file defines a service for managing user notifications and preferences. It provides functions to create notifications, retrieve notifications for a user, mark notifications as read, get user notification preferences, and update those preferences.

```javascript
// taskflow/backend/src/services/notificationService.js
const { query } = require('../config/db');

const create = async (userId, message) => {
  const result = await query('INSERT INTO notifications (user_id, message) VALUES ($1, $2) RETURNING *', [userId, message]);
  return result.rows[0];
};

const getForUser = async (userId, limit = 10) => {
  const result = await query('SELECT * FROM notifications WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2', [userId, limit]);
  return result.rows;
};

const markRead = async (userId, notificationId) => {
  await query('UPDATE notifications SET read = true WHERE user_id = $1 AND id = $2', [userId, notificationId]);
};

const getPreferences = async (userId) => {
  const result = await query('SELECT * FROM notification_preferences WHERE user_id = $1', [userId]);
  return result.rows[0] || { email: true, sms: false };
};

const updatePreferences = async (userId, preferences) => {
  await query('INSERT INTO notification_preferences (user_id, email, sms) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO UPDATE SET email = $2, sms = $3', [userId, preferences.email, preferences.sms]);
  return { email: preferences.email, sms: preferences.sms };
};

module.exports = { create, getForUser, markRead, getPreferences, updatePreferences };
```

### Report Service

### File: `taskflow/backend/src/services/reportService.js`

The `reportService.js` file contains functions for generating HTML and PDF reports from task data. It uses file system operations to create and delete temporary files and executes a command-line tool (wkhtmltopdf) to convert HTML to PDF.

```javascript
// taskflow/backend/src/services/reportService.js
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const generateReportHtml = async (tasks) => {
  const html = tasks.map(task => `<div>${task.title} - ${task.status}</div>`).join('');
  return html;
};

const generatePdf = async (html) => {
  const tempHtmlPath = path.join(__dirname, 'temp', 'report.html');
  const tempPdfPath = path.join(__dirname, 'temp', 'report.pdf');

  fs.writeFileSync(tempHtmlPath, html);

  await new Promise((resolve, reject) => {
    exec(`wkhtmltopdf ${tempHtmlPath} ${tempPdfPath}`, (err) => {
      if (err) return reject(err);
      resolve();
    });
  });

  const pdfBuffer = fs.readFileSync(tempPdfPath);
  fs.unlinkSync(tempHtmlPath);
  fs.unlinkSync(tempPdfPath);

  return pdfBuffer;
};

module.exports = { generateReportHtml, generatePdf };
```

## Data Management Middleware

### Authentication Middleware

### File: `taskflow/backend/src/middleware/authenticate.js`

The `authenticate.js` file defines a middleware function for authenticating HTTP requests by verifying a JWT token in the authorization header. It attaches user information to the request object