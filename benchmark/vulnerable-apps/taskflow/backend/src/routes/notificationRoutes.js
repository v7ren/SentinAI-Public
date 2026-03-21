const express = require('express');
const router = express.Router();
const notificationController = require('../controllers/notificationController');
const { authenticate } = require('../middleware/authenticate');

router.use(authenticate);

router.get('/', notificationController.list);
router.post('/:id/read', notificationController.markRead);
router.get('/preferences', notificationController.getPreferences);
router.patch('/preferences', notificationController.updatePreferences);

module.exports = router;
