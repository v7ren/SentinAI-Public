function isEmail(str) {
  if (typeof str !== 'string') return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str.trim());
}

function isNonEmptyString(str, minLen = 1) {
  return typeof str === 'string' && str.trim().length >= minLen;
}

function sanitizeString(str, maxLen = 1000) {
  if (str == null) return '';
  return String(str).trim().slice(0, maxLen);
}

module.exports = { isEmail, isNonEmptyString, sanitizeString };
