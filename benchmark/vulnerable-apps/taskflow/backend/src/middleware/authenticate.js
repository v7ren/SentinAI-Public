const { verifyAccess } = require('../utils/tokenUtils');
const logger = require('../utils/logger');

function authenticate(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ success: false, message: 'Missing or invalid authorization header' });
  }
  const token = authHeader.slice(7);
  try {
    const decoded = verifyAccess(token);
    req.userId = decoded.userId;
    req.userRole = decoded.role;
    req.orgId = decoded.orgId;
    next();
  } catch (err) {
    logger.warn('Invalid token', { error: err.message });
    return res.status(401).json({ success: false, message: 'Invalid or expired token' });
  }
}

module.exports = { authenticate };
