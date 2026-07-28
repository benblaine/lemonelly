/**
 * lemonelly — /start onboarding → Google Sheet + email alert
 *
 * Bound to the leads sheet:
 * https://docs.google.com/spreadsheets/d/1zpVOKFb8oDvdgSfSZLgXp458wnkxUwp4J5GhQafVbvY/
 *
 * The /start page POSTs each finished brief here as JSON; this appends a row to
 * the "Leads" tab and (optionally) emails a copy. See README.md for the 2-minute
 * deploy steps and where to paste the resulting URL.
 */

var SHEET_NAME = 'Leads';

// Where to email each new lead. Set to '' to turn email alerts off.
var NOTIFY_EMAIL = 'hello@lemonelly.com';

// [payload key, column header] — order defines the sheet columns.
var COLUMNS = [
  ['timestamp',    'Submitted'],
  ['firstName',    'First name'],
  ['lastName',     'Last name'],
  ['businessName', 'Business'],
  ['email',        'Email'],
  ['phone',        'Phone'],
  ['region',       'Region'],
  ['style',        'Style'],
  ['styleTag',     'Style tag'],
  ['domain',       'Domain'],
  ['pages',        'Pages'],
  ['story',        'Story'],
  ['colors',       'Brand colours'],
  ['assets',       'Assets'],
  ['extras',       'Extras'],
  ['powerups',     'Power-ups'],
  ['ddIdeal',      'Ideal customer'],
  ['ddDiff',       'Different because'],
  ['ddJobs',       'Wants more of'],
  ['ddTone',       'Tone'],
  ['monthly',      'Monthly price'],
  ['termsAgreed',  'Terms agreed'],
  ['brief',        'Full brief']
];

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);

    if (sheet.getLastRow() === 0) {
      sheet.appendRow(COLUMNS.map(function (c) { return c[1]; }));
      sheet.setFrozenRows(1);
    }

    data.timestamp = new Date();
    sheet.appendRow(COLUMNS.map(function (c) {
      return data[c[0]] != null ? data[c[0]] : '';
    }));

    if (NOTIFY_EMAIL) {
      MailApp.sendEmail({
        to: NOTIFY_EMAIL,
        subject: 'New lemonelly lead: ' + (data.businessName || data.firstName || 'website'),
        replyTo: data.email || undefined,
        body: data.brief || JSON.stringify(data, null, 2)
      });
    }

    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

// Lets you open the /exec URL in a browser to confirm the deployment is live.
function doGet() {
  return json({ ok: true, msg: 'lemonelly lead capture is live' });
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
