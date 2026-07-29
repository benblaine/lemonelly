/**
 * lemonelly — draft-page visit tracking → Google Sheet
 *
 * Bound to the visits sheet:
 * https://docs.google.com/spreadsheets/d/1cDNNxqy1a_k_Eu_Y5GyC5nvcfDN6f0dQjuWIrSF9YFQ/
 *
 * Each draft page fires a same-origin beacon to /api/hit (api/hit.js), which
 * enriches it with user-agent + geo and POSTs the hit here as JSON; this
 * appends a row to the "Visits" tab. See README.md for the deploy steps and
 * where the resulting /exec URL goes.
 *
 * Like the lead-capture script, this deliberately sends NO email (that needs a
 * sensitive Gmail permission and triggers the hard "This app is blocked" screen
 * on personal accounts) — use the sheet's own notification rules for alerts.
 */

var SHEET_NAME = 'Visits';

// [payload key, column header] — order defines the sheet columns.
var COLUMNS = [
  ['timestamp', 'Time'],
  ['slug',      'Draft'],
  ['ref',       'Referrer'],
  ['country',   'Country'],
  ['region',    'Region'],
  ['city',      'City'],
  ['ua',        'User agent'],
  ['path',      'Path']
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

    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

// Lets you open the /exec URL in a browser to confirm the deployment is live.
function doGet() {
  return json({ ok: true, msg: 'lemonelly visit tracking is live' });
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
