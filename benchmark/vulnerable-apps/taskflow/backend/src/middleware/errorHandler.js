const logger = require('../utils/logger');

function errorHandler(err, req, res, next) {
  logger.error(err.message, { stack: err.stack, path: req.path });
  const code = err.code || err.status || 500;
  res.status(typeof code === 'number' ? code : 500).json({
    message: err.message,
    stack: err.stack,
    code: err.code,
  });
}

module.exports = errorHandler;
