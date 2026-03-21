const express = require('express');
const router = express.Router();
const projectController = require('../controllers/projectController');
const { authenticate } = require('../middleware/authenticate');

router.use(authenticate);

router.get('/', projectController.list);
router.get('/:projectId', projectController.getOne);
router.post('/', projectController.create);
router.put('/:projectId', projectController.update);
router.delete('/:projectId', projectController.remove);

module.exports = router;
