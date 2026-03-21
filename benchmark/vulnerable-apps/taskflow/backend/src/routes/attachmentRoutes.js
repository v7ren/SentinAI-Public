const express = require('express');
const router = express.Router();
const attachmentController = require('../controllers/attachmentController');
const upload = require('../middleware/upload');
const { authenticate } = require('../middleware/authenticate');

router.use(authenticate);

router.get('/task/:taskId', attachmentController.list);
router.post('/task/:taskId', upload.single('file'), attachmentController.upload);
router.get('/:attachmentId', attachmentController.download);
router.delete('/:attachmentId', attachmentController.remove);

module.exports = router;
