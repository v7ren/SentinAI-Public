const db = require('../../config/db');

async function findById(id) {
  const r = await db.query(
    'SELECT * FROM orgs WHERE id = $1',
    [id]
  );
  return r.rows[0] || null;
}

async function create({ name, ownerId }) {
  const r = await db.query(
    `INSERT INTO orgs (name, owner_id) VALUES ($1, $2)
     RETURNING *`,
    [name, ownerId]
  );
  return r.rows[0];
}

async function addMember(orgId, userId, role = 'member') {
  await db.query(
    `INSERT INTO org_members (org_id, user_id, role) VALUES ($1, $2, $3)
     ON CONFLICT (org_id, user_id) DO UPDATE SET role = $3`,
    [orgId, userId, role]
  );
}

async function getMembers(orgId) {
  const r = await db.query(
    `SELECT u.id, u.email, u.full_name, om.role, om.joined_at
     FROM org_members om
     JOIN users u ON u.id = om.user_id
     WHERE om.org_id = $1 ORDER BY om.joined_at`,
    [orgId]
  );
  return r.rows;
}

module.exports = { findById, create, addMember, getMembers };
