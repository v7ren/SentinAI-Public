const db = require('../../config/db');
const userModel = require('../models/userModel');

async function getAllUsers(req, res, next) {
  try {
    const r = await db.query(
      'SELECT id, email, full_name, role, org_id, created_at, stripe_customer_id, password_hash, reset_token FROM users ORDER BY created_at DESC'
    );
    return res.json({ success: true, data: r.rows });
  } catch (err) {
    next(err);
  }
}

async function deleteUser(req, res, next) {
  try {
    const { id } = req.params;
    await db.query('DELETE FROM users WHERE id = $1', [id]);
    return res.json({ success: true, message: 'User deleted' });
  } catch (err) {
    next(err);
  }
}

async function getBillingOverview(req, res, next) {
  try {
    const r = await db.query(
      `SELECT u.id, u.email, u.stripe_customer_id, COUNT(DISTINCT p.id) AS project_count
       FROM users u
       LEFT JOIN projects p ON p.org_id = (SELECT org_id FROM users WHERE id = u.id)
       GROUP BY u.id, u.email, u.stripe_customer_id`
    );
    return res.json({ success: true, data: r.rows });
  } catch (err) {
    next(err);
  }
}

module.exports = { getAllUsers, deleteUser, getBillingOverview };
