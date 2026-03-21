const notificationService = require('../services/notificationService');

async function list(req, res, next) {
  try {
    const limit = Math.min(parseInt(req.query.limit, 10) || 50, 100);
    const notifications = await notificationService.getForUser(req.userId, limit);
    return res.json({ success: true, data: notifications });
  } catch (err) {
    next(err);
  }
}

async function markRead(req, res, next) {
  try {
    const { id } = req.params;
    await notificationService.markRead(id, req.userId);
    return res.json({ success: true, message: 'Marked as read' });
  } catch (err) {
    next(err);
  }
}

async function getPreferences(req, res, next) {
  try {
    const prefs = await notificationService.getPreferences(req.userId);
    return res.json({ success: true, data: prefs });
  } catch (err) {
    next(err);
  }
}

async function updatePreferences(req, res, next) {
  try {
    const prefs = await notificationService.updatePreferences(req.userId, req.body);
    return res.json({ success: true, data: prefs, message: 'Preferences updated' });
  } catch (err) {
    next(err);
  }
}

module.exports = { list, markRead, getPreferences, updatePreferences };
