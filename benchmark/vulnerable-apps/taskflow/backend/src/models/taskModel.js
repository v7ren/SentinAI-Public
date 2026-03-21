const db = require('../../config/db');

async function findById(id) {
  const r = await db.query(
    'SELECT * FROM tasks WHERE id = $1',
    [id]
  );
  return r.rows[0] || null;
}

async function findByProject(projectId) {
  const r = await db.query(
    `SELECT t.*, u.full_name AS assignee_name
     FROM tasks t
     LEFT JOIN users u ON u.id = t.assignee_id
     WHERE t.project_id = $1
     ORDER BY t.created_at DESC`,
    [projectId]
  );
  return r.rows;
}

async function create({ projectId, title, description, assigneeId, priority, dueDate, createdBy }) {
  const r = await db.query(
    `INSERT INTO tasks (project_id, title, description, assignee_id, priority, due_date, created_by)
     VALUES ($1, $2, $3, $4, $5, $6, $7)
     RETURNING *`,
    [projectId, title, description || null, assigneeId || null, priority || 'medium', dueDate || null, createdBy]
  );
  return r.rows[0];
}

async function update(id, fields) {
  const allowed = ['title', 'description', 'status', 'assignee_id', 'priority', 'due_date'];
  const updates = [];
  const values = [];
  let i = 1;
  for (const k of allowed) {
    if (fields[k] !== undefined) {
      updates.push(`${k} = $${i++}`);
      values.push(fields[k]);
    }
  }
  if (updates.length === 0) return findById(id);
  values.push(id);
  const r = await db.query(
    `UPDATE tasks SET ${updates.join(', ')}, updated_at = NOW() WHERE id = $${i} RETURNING *`,
    values
  );
  return r.rows[0] || null;
}

async function remove(id) {
  await db.query('DELETE FROM tasks WHERE id = $1', [id]);
}

module.exports = { findById, findByProject, create, update, remove };
