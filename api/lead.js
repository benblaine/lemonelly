// Serverless endpoint: emails homepage callback requests and /start briefs.
//
// Uses a Gmail app password (SMTP), NOT OAuth — so it sidesteps the
// "This app is blocked" consent screen entirely. The password lives only in
// Vercel's env vars, never in the page. Set these in the Vercel project:
//   GMAIL_USER          the Gmail address that sends (and, by default, receives)
//   GMAIL_APP_PASSWORD  a 16-char app password from myaccount.google.com/apppasswords
//   LEAD_TO             optional — where to deliver leads (defaults to GMAIL_USER)
// See reference/lead-capture/README.md.

const nodemailer = require('nodemailer');

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  const user = process.env.GMAIL_USER;
  const pass = process.env.GMAIL_APP_PASSWORD;
  if (!user || !pass) {
    // Diagnostic only — reports which vars are present and any mail-related
    // key NAMES the runtime can see (never values), so a misconfig is obvious.
    return res.status(500).json({
      ok: false,
      error: 'Email not configured',
      has: { GMAIL_USER: !!user, GMAIL_APP_PASSWORD: !!pass },
      seen: Object.keys(process.env).filter(function (k) {
        return /GMAIL|LEAD|MAIL|SMTP/i.test(k);
      })
    });
  }

  let data = req.body;
  if (typeof data === 'string') { try { data = JSON.parse(data); } catch (e) { data = {}; } }
  if (!data || typeof data !== 'object') data = {};

  const to = process.env.LEAD_TO || user;
  const isCallback = data.type === 'callback';
  const whoBit = data.whoLabel || data.who;
  const subject = isCallback
    ? (data.stage === 'details'
        ? ('Callback confirmed: ' + (whoBit ? whoBit + ' · ' : '') + (data.phone || 'website'))
        : ('Callback: ' + (data.phone || 'website')))
    : ('New lemonelly lead: ' + (data.businessName || data.firstName || 'website'));
  const text = data.brief || JSON.stringify(data, null, 2);

  try {
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: { user: user, pass: pass }
    });
    const mail = {
      from: 'lemonelly onboarding <' + user + '>',
      to: to,
      subject: subject,
      text: text
    };
    if (data.email) mail.replyTo = String(data.email).slice(0, 200);
    await transporter.sendMail(mail);
    return res.status(200).json({ ok: true });
  } catch (err) {
    return res.status(500).json({ ok: false, error: String((err && err.message) || err) });
  }
};
