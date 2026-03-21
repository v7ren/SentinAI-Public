const reportService = require('../services/reportService');
const taskModel = require('../models/taskModel');
const projectModel = require('../models/projectModel');
const { v4: uuidv4 } = require('uuid');

async function generatePdf(req, res, next) {
  try {
    const { projectId } = req.params;
    const project = await projectModel.findById(projectId);
    if (!project) {
      return res.status(404).json({ success: false, message: 'Project not found' });
    }
    if (project.org_id !== req.orgId) {
      return res.status(403).json({ success: false, message: 'Access denied' });
    }
    const tasks = await taskModel.findByProject(projectId);
    const reportId = uuidv4().replace(/-/g, '');
    const html = await reportService.generateReportHtml(
      project.name,
      tasks,
      new Date().toISOString()
    );
    const pdfBuf = await reportService.generatePdf(project.name, reportId, html);
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="report-${project.name.replace(/\s/g, '_')}.pdf"`);
    return res.send(pdfBuf);
  } catch (err) {
    next(err);
  }
}

module.exports = { generatePdf };
