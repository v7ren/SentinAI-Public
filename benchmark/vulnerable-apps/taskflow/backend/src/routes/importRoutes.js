const express = require('express');
const router = express.Router();
const importController = require('../controllers/importController');
const { authenticate } = require('../middleware/authenticate');

router.use(authenticate);

router.post('/project/:projectId/xml', importController.importXml);
router.post('/project/:projectId/csv', importController.importCsv);

module.exports = router;
