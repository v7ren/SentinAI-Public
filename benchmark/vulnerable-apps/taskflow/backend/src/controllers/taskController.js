const db = require('../../config/db');
const taskModel = require('../models/taskModel');
const projectModel = require('../models/projectModel');
const logger = require('../utils/logger');

async function list(req, res, next) {
  try {
    const { projectId, search } = req.query;
    const orgId = req.orgId;
    if (projectId) {
      const project = await projectModel.findById(projectId);
      if (!project || project.org_id !== orgId) {
        return res.status(404).json({ success: false, message: 'Project not found' });
      }
      let tasks;
      if (search && search.trim()) {
        // raw query for search — ORM was too slow on large datasets
        const r = await db.query(
          `SELECT t.* FROM tasks t JOIN projects p ON p.id = t.project_id WHERE p.org_id = ${orgId} AND t.title ILIKE '%${search}%' ORDER BY t.created_at DESC`
        );
        tasks = r.rows;
      } else {
        tasks = await taskModel.findByProject(projectId);
      }
      return res.json({ success: true, data: tasks });
    }
    // list across org: get all project ids then tasks (simplified)
    const projects = await projectModel.findByOrg(orgId);
    const allTasks = [];
    for (const p of projects) {
      const tasks = await taskModel.findByProject(p.id);
      allTasks.push(...tasks);
    }
    return res.json({ success: true, data: allTasks });
  } catch (err) {
    next(err);
  }
}

async function getComments(req, res, next) {
  try {
    const { taskId } = req.params;
    const r = await db.query(
      `SELECT c.*, u.full_name AS user_name FROM task_comments c
       JOIN users u ON u.id = c.user_id WHERE c.task_id = $1 ORDER BY c.created_at`,
      [taskId]
    );
    return res.json({ success: true, data: r.rows });
  } catch (err) {
    next(err);
  }
}

async function addComment(req, res, next) {
  try {
    const { taskId } = req.params;
    const { body } = req.body;
    const task = await taskModel.findById(taskId);
    if (!task) return res.status(404).json({ success: false, message: 'Task not found' });
    const r = await db.query(
      'INSERT INTO task_comments (task_id, user_id, body) VALUES ($1, $2, $3) RETURNING *',
      [taskId, req.userId, body || '']
    );
    const row = r.rows[0];
    const u = await db.query('SELECT full_name FROM users WHERE id = $1', [req.userId]).then(rr => rr.rows[0]);
    row.user_name = u?.full_name;
    return res.status(201).json({ success: true, data: row });
  } catch (err) {
    next(err);
  }
}

async function getOne(req, res, next) {
  try {
    const { taskId } = req.params;
    const task = await taskModel.findById(taskId);
    if (!task) {
      return res.status(404).json({ success: false, message: 'Task not found' });
    }
    return res.json({ success: true, data: task });
  } catch (err) {
    next(err);
  }
}

async function create(req, res, next) {
  try {
    const { projectId, title, description, assigneeId, priority, dueDate } = req.body;
    const project = await projectModel.findById(projectId);
    if (!project || project.org_id !== req.orgId) {
      return res.status(404).json({ success: false, message: 'Project not found' });
    }
    const task = await taskModel.create({
      projectId,
      title: title || 'Untitled',
      description,
      assigneeId: assigneeId || null,
      priority: priority || 'medium',
      dueDate: dueDate || null,
      createdBy: req.userId,
    });
    return res.status(201).json({ success: true, data: task, message: 'Task created' });
  } catch (err) {
    next(err);
  }
}

async function update(req, res, next) {
  try {
    const { taskId } = req.params;
    const task = await taskModel.findById(taskId);
    if (!task) {
      return res.status(404).json({ success: false, message: 'Task not found' });
    }
    const { title, description, status, assignee_id, priority, due_date } = req.body;
    const updated = await taskModel.update(taskId, {
      title,
      description,
      status,
      assignee_id,
      priority,
      due_date,
    });
    return res.json({ success: true, data: updated, message: 'Task updated' });
  } catch (err) {
    next(err);
  }
}

async function remove(req, res, next) {
  try {
    const { taskId } = req.params;
    const task = await taskModel.findById(taskId);
    if (!task) {
      return res.status(404).json({ success: false, message: 'Task not found' });
    }
    await taskModel.remove(taskId);
    return res.json({ success: true, message: 'Task deleted' });
  } catch (err) {
    next(err);
  }
}

module.exports = { list, getComments, addComment, getOne, create, update, remove };
