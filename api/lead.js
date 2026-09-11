// Serverless endpoint: emails homepage callback requests and /start briefs.
//
// Uses a Gmail app password (SMTP), NOT OAuth — so it sidesteps the
// "This app is blocked" consent screen entirely. The password lives only in
// Vercel's env vars, never in the page. Set these in the Vercel project:
//   GMAIL_USER          the Gmail address that sends (and, by default, receives)
//   GMAIL_APP_PASSWORD  a 16-char app password from myaccount.google.com/apppasswords
//   LEAD_TO             optional — where to deliver leads (defaults to GMAIL_USER)
// Callbacks also append a row to the "lemonelly callbacks" sheet when these
// are set: GOOGLE_SHEETS_REFRESH_TOKEN, GOOGLE_SHEETS_CLIENT_ID,
// GOOGLE_SHEETS_CLIENT_SECRET, CALLBACK_SHEET_ID.
// See reference/lead-capture/README.md.

const nodemailer = require('nodemailer');

async function appendCallbackRow(data) {
  const refresh = process.env.GOOGLE_SHEETS_REFRESH_TOKEN;
  const clientId = process.env.GOOGLE_SHEETS_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_SHEETS_CLIENT_SECRET;
  const sheetId = process.env.CALLBACK_SHEET_ID;
  if (!refresh || !clientId || !clientSecret || !sheetId) return;
  const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refresh,
      client_id: clientId,
      client_secret: clientSecret
    })
  });
  const tokenJson = await tokenRes.json();
  if (!tokenJson.access_token) return;
  const row = [[
    new Date().toISOString(),
    String(data.stage || '').slice(0, 40),
    String(data.phone || '').slice(0, 40),
    String(data.countryCode || '').slice(0, 8),
    String(data.whoLabel || data.who || '').slice(0, 40),
    String(data.whenLabel || data.when || '').slice(0, 80),
    String(data.channelLabel || data.how || '').slice(0, 40),
    String(data.page || '').slice(0, 80),
    String(data.brief || '').slice(0, 8000)
  ]];
  await fetch(
    'https://sheets.googleapis.com/v4/spreadsheets/' +
      encodeURIComponent(sheetId) +
      '/values/Callbacks!A:I:append?valueInputOption=USER_ENTERED',
    {
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + tokenJson.access_token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ values: row })
    }
  );
}

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
    let mailed = false;
    let sheeted = false;
    try {
      await transporter.sendMail(mail);
      mailed = true;
    } catch (mailErr) {
      if (!isCallback) throw mailErr;
    }
    if (isCallback) {
      try { await appendCallbackRow(data); sheeted = true; } catch (e) { /* sheet must never fail the lead */ }
    }
    if (mailed || sheeted) return res.status(200).json({ ok: true, mailed: mailed, sheet: sheeted });
    return res.status(500).json({ ok: false, error: 'email and sheet both failed' });
  } catch (err) {
    return res.status(500).json({ ok: false, error: String((err && err.message) || err) });
  }
};
