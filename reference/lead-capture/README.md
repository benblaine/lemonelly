# /start lead capture → Google Sheet

The `/start` onboarding form used to end on a screen that asked the prospect to
*manually* fire their brief off via WhatsApp or email — an easy place to lose a
lead. It now POSTs the finished brief straight to a Google Sheet, then shows a
"we've got it" confirmation. WhatsApp/email stay as a silent fallback if the
network call ever fails. For an email ping on each new lead, see **Email alerts**
below — that's set up on the sheet itself, not in this script.

The site half is already wired up. The only thing left is a one-time Google
setup, because deploying an Apps Script needs your own Google login.

## One-time setup (~2 minutes)

1. Open the leads sheet:
   <https://docs.google.com/spreadsheets/d/1zpVOKFb8oDvdgSfSZLgXp458wnkxUwp4J5GhQafVbvY/edit>
2. **Extensions → Apps Script.** Delete the placeholder `myFunction`, then paste
   the entire contents of [`Code.gs`](./Code.gs). Save (the disk icon).
3. **Deploy → New deployment.** Click the gear → **Web app**. Set:
   - **Execute as:** Me
   - **Who has access:** Anyone
   Click **Deploy**, then **Authorize access** and approve. You'll see a
   "Google hasn't verified this app" notice — click **Advanced → Go to … (unsafe)**
   and allow. It only asks to manage *this* spreadsheet.
4. Copy the **Web app URL** — it ends in `/exec`.
5. In `start/index.html`, paste that URL into the `SHEET_ENDPOINT` constant near
   the top of the `<script>`:
   ```js
   var SHEET_ENDPOINT = 'https://script.google.com/macros/s/AKfy…/exec';
   ```
   Commit and let Vercel deploy. Done — submissions now land in the sheet.

### "This app is blocked" during authorize?

That hard block appears when a script asks for a *sensitive* permission (like
sending email) on a personal Gmail account. `Code.gs` deliberately only touches
this one spreadsheet, so it shouldn't happen. If you do hit it, you're almost
certainly authorizing an **older copy of the script that still had the email
line** — re-paste the current `Code.gs` (no `MailApp`), save, and deploy again.
Get email alerts via the sheet's own notifications instead (below).

## Email alerts (optional, no script permissions)

Google Sheets can email you itself — no code, nothing to authorize, can't be
blocked:

1. In the sheet: **Tools → Notification settings → Edit notifications**
   (older UI: **Tools → Notification rules**).
2. Choose **Any changes are made** → **Email – right away** → **Save**.

You'll get a "the sheet changed" email the moment a lead lands; open the sheet
to read the new row. (Google's native emails don't include the row contents —
that's the trade-off for it being permission-free.)

## Test it

- Open the `/exec` URL in a browser: you should see
  `{"ok":true,"msg":"lemonelly lead capture is live"}`.
- Run through `/start` and submit. A row should appear on the **Leads** tab.

## Notes

- **Columns** are defined by the `COLUMNS` list in `Code.gs`; the header row is
  created automatically on the first submission. Add/rename columns there.
- **CORS:** the page posts with `mode: 'no-cors'` and `text/plain`, which is the
  reliable pattern for a static site talking to Apps Script — no preflight, no
  extra config. The browser can't read the response, so the page treats a
  completed request as success and only falls back to manual send on a true
  network error.
- If you'd rather not run Apps Script at all, leave `SHEET_ENDPOINT` blank and the
  form keeps the old manual WhatsApp/email send screen — nothing breaks.
