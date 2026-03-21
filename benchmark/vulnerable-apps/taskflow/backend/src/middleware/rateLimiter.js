const rateLimit = require('express-rate-limit');

// only applied to report generation to avoid abuse of PDF export
const reportLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 10,
  message: { success: false, message: 'Too many report requests, try again later' },
});

module.exports = { reportLimiter };
