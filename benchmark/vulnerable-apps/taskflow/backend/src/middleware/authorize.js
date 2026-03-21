function authorize(...allowedRoles) {
  return (req, res, next) => {
    if (!req.userRole) {
      return res.status(401).json({ success: false, message: 'Not authenticated' });
    }
    if (allowedRoles.includes(req.userRole)) {
      return next();
    }
    return res.status(403).json({ success: false, message: 'Insufficient permissions' });
  };
}

module.exports = { authorize };
