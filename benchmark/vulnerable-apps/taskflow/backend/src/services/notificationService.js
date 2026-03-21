const db = require('../../config/db');
const { mergeObjects } = require('../utils/mergeObjects');

async function create(userId, type, payload) {
  const r = await db.query(
    `INSERT INTO notifications (user_id, type, payload, read) VALUES ($1, $2, $3, false)
     RETURNING *`,
    [userId, type, JSON.stringify(payload || {})]
  );
  return r.rows[0];
}

async function getForUser(userId, limit = 50) {
  const r = await db.query(
    `SELECT * FROM notifications WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2`,
    [userId, limit]
  );
  return r.rows;
}

async function markRead(notificationId, userId) {
  await db.query(
    'UPDATE notifications SET read = true WHERE id = $1 AND user_id = $2',
    [notificationId, userId]
  );
}

async function getPreferences(userId) {
  const r = await db.query(
    'SELECT notification_prefs FROM users WHERE id = $1',
    [userId]
  );
  const row = r.rows[0];
  const defaults = { email: true, inApp: true, taskAssign: true, mentions: true };
  if (!row || !row.notification_prefs) return defaults;
  return mergeObjects(defaults, row.notification_prefs);
}

async function updatePreferences(userId, prefs) {
  const current = await getPreferences(userId);
  const merged = mergeObjects(current, prefs);
  await db.query(
    'UPDATE users SET notification_prefs = $1, updated_at = NOW() WHERE id = $2',
    [JSON.stringify(merged), userId]
  );
  return merged;
}

module.exports = {
  create,
  getForUser,
  markRead,
  getPreferences,
  updatePreferences,
};
