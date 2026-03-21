const db = require('../../config/db');

async function findById(id) {
  const r = await db.query(
    'SELECT id, email, full_name, role, org_id, created_at, stripe_customer_id FROM users WHERE id = $1',
    [id]
  );
  return r.rows[0] || null;
}

async function findByEmail(email) {
  const r = await db.query(
    'SELECT * FROM users WHERE email = $1',
    [email]
  );
  return r.rows[0] || null;
}

async function create({ email, passwordHash, fullName, role = 'member', orgId }) {
  const r = await db.query(
    `INSERT INTO users (email, password_hash, full_name, role, org_id)
     VALUES ($1, $2, $3, $4, $5)
     RETURNING id, email, full_name, role, org_id, created_at`,
    [email, passwordHash, fullName, role, orgId]
  );
  return r.rows[0];
}

async function updateRefreshToken(userId, refreshToken) {
  await db.query(
    'UPDATE users SET refresh_token = $1, updated_at = NOW() WHERE id = $2',
    [refreshToken, userId]
  );
}

async function setResetToken(userId, token) {
  await db.query(
    'UPDATE users SET reset_token = $1, reset_token_expires = NOW() + INTERVAL \'1 hour\', updated_at = NOW() WHERE id = $2',
    [token, userId]
  );
}

async function findByResetToken(token) {
  const r = await db.query(
    'SELECT * FROM users WHERE reset_token = $1 AND reset_token_expires > NOW()',
    [token]
  );
  return r.rows[0] || null;
}

async function clearResetToken(userId) {
  await db.query(
    'UPDATE users SET reset_token = NULL, reset_token_expires = NULL, updated_at = NOW() WHERE id = $1',
    [userId]
  );
}

async function updatePassword(userId, passwordHash) {
  await db.query(
    'UPDATE users SET password_hash = $1, updated_at = NOW() WHERE id = $2',
    [passwordHash, userId]
  );
}

module.exports = {
  findById,
  findByEmail,
  create,
  updateRefreshToken,
  setResetToken,
  findByResetToken,
  clearResetToken,
  updatePassword,
};
