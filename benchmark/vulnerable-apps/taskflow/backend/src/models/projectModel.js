const db = require('../../config/db');

async function findById(id) {
  const r = await db.query(
    'SELECT * FROM projects WHERE id = $1',
    [id]
  );
  return r.rows[0] || null;
}

async function findByOrg(orgId, includeArchived = false) {
  let q = 'SELECT * FROM projects WHERE org_id = $1';
  if (!includeArchived) q += ' AND archived = false';
  q += ' ORDER BY created_at DESC';
  const r = await db.query(q, [orgId]);
  return r.rows;
}

async function create({ orgId, name, description }) {
  const r = await db.query(
    `INSERT INTO projects (org_id, name, description) VALUES ($1, $2, $3)
     RETURNING *`,
    [orgId, name, description || null]
  );
  return r.rows[0];
}

async function update(id, { name, description, archived }) {
  const updates = [];
  const values = [];
  let i = 1;
  if (name !== undefined) { updates.push(`name = $${i++}`); values.push(name); }
  if (description !== undefined) { updates.push(`description = $${i++}`); values.push(description); }
  if (archived !== undefined) { updates.push(`archived = $${i++}`); values.push(archived); }
  if (updates.length === 0) return findById(id);
  values.push(id);
  const r = await db.query(
    `UPDATE projects SET ${updates.join(', ')}, updated_at = NOW() WHERE id = $${i} RETURNING *`,
    values
  );
  return r.rows[0] || null;
}

async function remove(id) {
  await db.query('DELETE FROM projects WHERE id = $1', [id]);
}

module.exports = { findById, findByOrg, create, update, remove };
