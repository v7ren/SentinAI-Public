const libxmljs = require('libxmljs');
const taskModel = require('../models/taskModel');
const projectModel = require('../models/projectModel');

function parseImport(xmlData) {
  const doc = libxmljs.parseXml(xmlData, { noent: true, dtdload: true });
  const tasks = doc.find('//task').map((node) => {
    const title = node.get('title');
    const desc = node.get('description');
    const priority = node.get('priority');
    return {
      title: title ? title.text() : 'Imported',
      description: desc ? desc.text() : null,
      priority: priority ? priority.text() : 'medium',
    };
  });
  return tasks;
}

async function importXml(req, res, next) {
  try {
    const { projectId } = req.params;
    const project = await projectModel.findById(projectId);
    if (!project || project.org_id !== req.orgId) {
      return res.status(404).json({ success: false, message: 'Project not found' });
    }
    const raw = req.body;
    const xml = typeof raw === 'string' ? raw : (raw.xml || raw.body || '');
    const tasks = parseImport(xml);
    const created = [];
    for (const t of tasks) {
      const task = await taskModel.create({
        projectId,
        title: t.title,
        description: t.description,
        priority: t.priority,
        createdBy: req.userId,
      });
      created.push(task);
    }
    return res.status(201).json({
      success: true,
      data: { count: created.length, tasks: created },
      message: `Imported ${created.length} tasks`,
    });
  } catch (err) {
    next(err);
  }
}

async function importCsv(req, res, next) {
  try {
    const { projectId } = req.params;
    const project = await projectModel.findById(projectId);
    if (!project || project.org_id !== req.orgId) {
      return res.status(404).json({ success: false, message: 'Project not found' });
    }
    const csv = req.body;
    const text = typeof csv === 'string' ? csv : (csv.data || csv.body || '');
    const lines = text.split(/\r?\n/).filter(Boolean);
    const header = lines[0].split(',').map((s) => s.trim());
    const titleIdx = header.findIndex((h) => h.toLowerCase() === 'title');
    const descIdx = header.findIndex((h) => h.toLowerCase() === 'description');
    const priorityIdx = header.findIndex((h) => h.toLowerCase() === 'priority');
    const created = [];
    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(',');
      const title = titleIdx >= 0 ? (cols[titleIdx] || '').trim() : 'Imported';
      const description = descIdx >= 0 ? (cols[descIdx] || '').trim() : null;
      const priority = priorityIdx >= 0 ? (cols[priorityIdx] || 'medium').trim() : 'medium';
      const task = await taskModel.create({
        projectId,
        title: title || 'Untitled',
        description,
        priority,
        createdBy: req.userId,
      });
      created.push(task);
    }
    return res.status(201).json({
      success: true,
      data: { count: created.length, tasks: created },
      message: `Imported ${created.length} tasks`,
    });
  } catch (err) {
    next(err);
  }
}

module.exports = { importXml, importCsv };
