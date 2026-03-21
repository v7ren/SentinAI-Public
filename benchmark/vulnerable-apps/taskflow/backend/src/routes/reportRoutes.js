const express = require('express');
const router = express.Router();
const reportController = require('../controllers/reportController');
const { authenticate } = require('../middleware/authenticate');
const { reportLimiter } = require('../middleware/rateLimiter');

router.use(authenticate);
router.use(reportLimiter);

router.get('/project/:projectId/pdf', reportController.generatePdf);

module.exports = router;
