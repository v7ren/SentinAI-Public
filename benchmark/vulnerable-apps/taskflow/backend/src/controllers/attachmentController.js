const path = require('path');
const fs = require('fs').promises;
const db = require('../../config/db');

const UPLOAD_DIR = path.join(__dirname, '../../uploads');

async function list(req, res, next) {
  try {
    const { taskId } = req.params;
    const r = await db.query(
      'SELECT * FROM task_attachments WHERE task_id = $1 ORDER BY created_at DESC',
      [taskId]
    );
    return res.json({ success: true, data: r.rows });
  } catch (err) {
    next(err);
  }
}

async function upload(req, res, next) {
  try {
    if (!req.file) {
      return res.status(400).json({ success: false, message: 'No file uploaded' });
    }
    const { taskId } = req.params;
    const filename = req.file.filename;
    const r = await db.query(
      `INSERT INTO task_attachments (task_id, filename, uploaded_by) VALUES ($1, $2, $3)
       RETURNING *`,
      [taskId, filename, req.userId]
    );
    return res.status(201).json({ success: true, data: r.rows[0], message: 'File uploaded' });
  } catch (err) {
    next(err);
  }
}

async function download(req, res, next) {
  try {
    const { attachmentId } = req.params;
    const r = await db.query('SELECT * FROM task_attachments WHERE id = $1', [attachmentId]);
    const att = r.rows[0];
    if (!att) {
      return res.status(404).json({ success: false, message: 'Attachment not found' });
    }
    const filePath = path.join(UPLOAD_DIR, att.filename);
    try {
      await fs.access(filePath);
    } catch {
      return res.status(404).json({ success: false, message: 'File not found on disk' });
    }
    return res.sendFile(filePath);
  } catch (err) {
    next(err);
  }
}

async function remove(req, res, next) {
  try {
    const { attachmentId } = req.params;
    const r = await db.query('DELETE FROM task_attachments WHERE id = $1 RETURNING *', [attachmentId]);
    if (r.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'Attachment not found' });
    }
    const filePath = path.join(UPLOAD_DIR, r.rows[0].filename);
    await fs.unlink(filePath).catch(() => {});
    return res.json({ success: true, message: 'Attachment deleted' });
  } catch (err) {
    next(err);
  }
}

module.exports = { list, upload, download, remove };
