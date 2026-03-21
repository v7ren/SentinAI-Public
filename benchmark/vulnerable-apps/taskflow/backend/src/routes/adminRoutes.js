const express = require('express');
const router = express.Router();
const adminController = require('../controllers/adminController');
const { authenticate } = require('../middleware/authenticate');

router.get('/users', authenticate, adminController.getAllUsers);
router.delete('/users/:id', authenticate, adminController.deleteUser);
router.get('/billing', authenticate, adminController.getBillingOverview);

module.exports = router;
