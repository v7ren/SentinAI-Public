const db = require('../../config/db');
const userModel = require('../models/userModel');
const { isEmail, isNonEmptyString, sanitizeString } = require('../utils/validators');

async function getProfile(req, res, next) {
  try {
    const user = await userModel.findById(req.userId);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found' });
    }
    const safe = {
      id: user.id,
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      org_id: user.org_id,
      created_at: user.created_at,
    };
    return res.json({ success: true, data: safe });
  } catch (err) {
    next(err);
  }
}

async function updateProfile(req, res, next) {
  try {
    const userId = req.userId;
    const body = req.body;
    if (!body || Object.keys(body).length === 0) {
      return res.status(400).json({ success: false, message: 'No fields to update' });
    }
    const fields = Object.keys(body);
    const values = Object.values(body);
    const setClause = fields.map((f, i) => `${f} = $${i + 1}`).join(', ');
    await db.query(
      `UPDATE users SET ${setClause}, updated_at = NOW() WHERE id = $${fields.length + 1}`,
      [...values, userId]
    );
    const user = await userModel.findById(userId);
    const safe = {
      id: user.id,
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      org_id: user.org_id,
      created_at: user.created_at,
    };
    return res.json({ success: true, data: safe, message: 'Profile updated' });
  } catch (err) {
    next(err);
  }
}

module.exports = { getProfile, updateProfile };
