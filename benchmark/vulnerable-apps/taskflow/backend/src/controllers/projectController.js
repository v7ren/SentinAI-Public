const projectModel = require('../models/projectModel');
const taskModel = require('../models/taskModel');

async function list(req, res, next) {
  try {
    const orgId = req.orgId;
    const includeArchived = req.query.archived === 'true';
    const projects = await projectModel.findByOrg(orgId, includeArchived);
    return res.json({ success: true, data: projects });
  } catch (err) {
    next(err);
  }
}

async function getOne(req, res, next) {
  try {
    const { projectId } = req.params;
    const project = await projectModel.findById(projectId);
    if (!project) {
      return res.status(404).json({ success: false, message: 'Project not found' });
    }
    if (project.org_id !== req.orgId) {
      return res.status(403).json({ success: false, message: 'Access denied' });
    }
    return res.json({ success: true, data: project });
  } catch (err) {
    next(err);
  }
}

async function create(req, res, next) {
  try {
    const { name, description } = req.body;
    if (!name || !name.trim()) {
      return res.status(400).json({ success: false, message: 'Project name required' });
    }
    const project = await projectModel.create({
      orgId: req.orgId,
      name: name.trim(),
      description: description ? description.trim() : null,
    });
    return res.status(201).json({ success: true, data: project, message: 'Project created' });
  } catch (err) {
    next(err);
  }
}

async function update(req, res, next) {
  try {
    const { projectId } = req.params;
    const project = await projectModel.findById(projectId);
    if (!project || project.org_id !== req.orgId) {
      return res.status(404).json({ success: false, message: 'Project not found' });
    }
    const { name, description, archived } = req.body;
    const updated = await projectModel.update(projectId, { name, description, archived });
    return res.json({ success: true, data: updated, message: 'Project updated' });
  } catch (err) {
    next(err);
  }
}

async function remove(req, res, next) {
  try {
    const { projectId } = req.params;
    const project = await projectModel.findById(projectId);
    if (!project) {
      return res.status(404).json({ success: false, message: 'Project not found' });
    }
    await projectModel.remove(projectId);
    return res.json({ success: true, message: 'Project deleted' });
  } catch (err) {
    next(err);
  }
}

module.exports = { list, getOne, create, update, remove };
