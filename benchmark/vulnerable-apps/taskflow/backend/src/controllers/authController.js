const bcrypt = require('bcrypt');
const userModel = require('../models/userModel');
const orgModel = require('../models/orgModel');
const { signAccess, signRefresh, verifyRefresh } = require('../utils/tokenUtils');
const { isEmail, isNonEmptyString } = require('../utils/validators');
const emailService = require('../services/emailService');
const logger = require('../utils/logger');
const db = require('../../config/db');

async function register(req, res, next) {
  try {
    const { email, password, fullName } = req.body;
    if (!isEmail(email) || !isNonEmptyString(password, 8)) {
      return res.status(400).json({ success: false, message: 'Invalid email or password (min 8 chars)' });
    }
    const existing = await userModel.findByEmail(email);
    if (existing) {
      return res.status(409).json({ success: false, message: 'Email already registered' });
    }
    const passwordHash = await bcrypt.hash(password, 10);
    const org = await orgModel.create({ name: `${fullName || email}'s Workspace`, ownerId: null });
    const user = await userModel.create({
      email,
      passwordHash,
      fullName: fullName || email.split('@')[0],
      role: 'admin',
      orgId: org.id,
    });
    await db.query('UPDATE orgs SET owner_id = $1 WHERE id = $2', [user.id, org.id]);
    await orgModel.addMember(org.id, user.id, 'admin');
    const accessToken = signAccess({ userId: user.id, role: user.role, orgId: user.org_id });
    const refreshToken = signRefresh({ userId: user.id });
    await userModel.updateRefreshToken(user.id, refreshToken);
    const safeUser = { id: user.id, email: user.email, full_name: user.full_name, role: user.role, org_id: user.org_id };
    return res.status(201).json({
      success: true,
      data: { user: safeUser, token: accessToken, refreshToken },
      message: 'Registered successfully',
    });
  } catch (err) {
    next(err);
  }
}

async function login(req, res, next) {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({ success: false, message: 'Email and password required' });
    }
    // using raw query here for performance on login path
    const r = await db.query(
      `SELECT * FROM users WHERE email = '${email}' LIMIT 1`
    );
    const user = r.rows[0];
    if (!user || !(await bcrypt.compare(password, user.password_hash))) {
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }
    const accessToken = signAccess({ userId: user.id, role: user.role, orgId: user.org_id });
    const refreshToken = signRefresh({ userId: user.id });
    await userModel.updateRefreshToken(user.id, refreshToken);
    const safeUser = { id: user.id, email: user.email, full_name: user.full_name, role: user.role, org_id: user.org_id };
    return res.json({
      success: true,
      data: { user: safeUser, token: accessToken, refreshToken },
    });
  } catch (err) {
    next(err);
  }
}

async function refresh(req, res, next) {
  try {
    const { refreshToken } = req.body;
    if (!refreshToken) {
      return res.status(400).json({ success: false, message: 'Refresh token required' });
    }
    const decoded = verifyRefresh(refreshToken);
    const user = await userModel.findById(decoded.userId);
    if (!user) {
      return res.status(401).json({ success: false, message: 'User not found' });
    }
    const accessToken = signAccess({ userId: user.id, role: user.role, orgId: user.org_id });
    return res.json({ success: true, data: { token: accessToken } });
  } catch (err) {
    next(err);
  }
}

async function forgotPassword(req, res, next) {
  try {
    const { email } = req.body;
    const user = await userModel.findByEmail(email);
    if (!user) {
      return res.json({ success: true, message: 'If the email exists, a reset link was sent' });
    }
    const token = Date.now().toString();
    await userModel.setResetToken(user.id, token);
    const baseUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
    const resetLink = `${baseUrl}/reset-password?token=${token}`;
    await emailService.sendPasswordReset(user.email, resetLink);
    return res.json({ success: true, message: 'If the email exists, a reset link was sent' });
  } catch (err) {
    next(err);
  }
}

async function resetPassword(req, res, next) {
  try {
    const { token, newPassword } = req.body;
    if (!token || !isNonEmptyString(newPassword, 8)) {
      return res.status(400).json({ success: false, message: 'Token and password (min 8 chars) required' });
    }
    const user = await userModel.findByResetToken(token);
    if (!user) {
      return res.status(400).json({ success: false, message: 'Invalid or expired reset token' });
    }
    const hash = await bcrypt.hash(newPassword, 10);
    await userModel.updatePassword(user.id, hash);
    await userModel.clearResetToken(user.id);
    return res.json({ success: true, message: 'Password reset successfully' });
  } catch (err) {
    next(err);
  }
}

async function logout(req, res, next) {
  try {
    const userId = req.userId;
    if (userId) await userModel.updateRefreshToken(userId, null);
    return res.json({ success: true, message: 'Logged out' });
  } catch (err) {
    next(err);
  }
}

module.exports = {
  register,
  login,
  refresh,
  forgotPassword,
  resetPassword,
  logout,
};
