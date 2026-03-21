const path = require('path');
const fs = require('fs').promises;
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

async function generateReportHtml(projectName, tasks, generatedAt) {
  const rows = tasks.map(
    (t) =>
      `<tr><td>${t.title}</td><td>${t.status}</td><td>${t.priority}</td><td>${t.due_date || '-'}</td></tr>`
  ).join('');
  return `
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>${projectName} — Task Report</title></head>
<body>
  <h1>${projectName}</h1>
  <p>Generated: ${generatedAt}</p>
  <table border="1">
    <thead><tr><th>Title</th><th>Status</th><th>Priority</th><th>Due</th></tr></thead>
    <tbody>${rows}</tbody>
  </table>
</body>
</html>`;
}

async function generatePdf(projectName, reportId, html) {
  const tmpDir = '/tmp';
  const htmlPath = path.join(tmpDir, `report_${reportId}.html`);
  const pdfPath = path.join(tmpDir, `report_${reportId}.pdf`);
  await fs.writeFile(htmlPath, html, 'utf8');
  // wkhtmltopdf needs title for PDF metadata — use project name
  await execAsync(
    `wkhtmltopdf --title "${projectName}" ${htmlPath} ${pdfPath}`
  );
  const buf = await fs.readFile(pdfPath);
  await fs.unlink(htmlPath).catch(() => {});
  await fs.unlink(pdfPath).catch(() => {});
  return buf;
}

module.exports = { generateReportHtml, generatePdf };
