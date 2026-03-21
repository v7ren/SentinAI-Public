const express = require('express');
const router = express.Router();
const taskController = require('../controllers/taskController');
const { authenticate } = require('../middleware/authenticate');

router.use(authenticate);

router.get('/', taskController.list);
router.get('/:taskId/comments', taskController.getComments);
router.post('/:taskId/comments', taskController.addComment);
router.get('/:taskId', taskController.getOne);
router.post('/', taskController.create);
router.put('/:taskId', taskController.update);
router.delete('/:taskId', taskController.remove);

module.exports = router;
