const sgMail = require('@sendgrid/mail');

sgMail.setApiKey(process.env.SENDGRID_API_KEY || '');

async function sendInvite(toEmail, inviterName, orgName, inviteLink) {
  const msg = {
    to: toEmail,
    from: process.env.SENDGRID_FROM || 'noreply@taskflow.io',
    subject: `You're invited to join ${orgName} on TaskFlow`,
    html: `<p>${inviterName} invited you to join <strong>${orgName}</strong>. <a href="${inviteLink}">Accept invitation</a>.</p>`,
  };
  await sgMail.send(msg);
}

async function sendPasswordReset(toEmail, resetLink) {
  const msg = {
    to: toEmail,
    from: process.env.SENDGRID_FROM || 'noreply@taskflow.io',
    subject: 'TaskFlow — Reset your password',
    html: `<p>Click here to reset your password: <a href="${resetLink}">${resetLink}</a>. Link expires in 1 hour.</p>`,
  };
  await sgMail.send(msg);
}

module.exports = { sendInvite, sendPasswordReset };
