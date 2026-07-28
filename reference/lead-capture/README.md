# /start lead capture → Google Sheet

The `/start` onboarding form used to end on a screen that asked the prospect to
*manually* fire their brief off via WhatsApp or email — an easy place to lose a
lead. It now POSTs the finished brief straight to a Google Sheet (and emails a
copy), then shows a "we've got it" confirmation. WhatsApp/email stay as a silent
fallback if the network call ever fails.

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
   Click **Deploy**, then **Authorize access** and approve the permissions
   (it needs to write the sheet and, if you keep alerts on, send email).
4. Copy the **Web app URL** — it ends in `/exec`.
5. In `start/index.html`, paste that URL into the `SHEET_ENDPOINT` constant near
   the top of the `<script>`:
   ```js
   var SHEET_ENDPOINT = 'https://script.google.com/macros/s/AKfy…/exec';
   ```
   Commit and let Vercel deploy. Done — submissions now land in the sheet.

## Test it

- Open the `/exec` URL in a browser: you should see
  `{"ok":true,"msg":"lemonelly lead capture is live"}`.
- Run through `/start` and submit. A row should appear on the **Leads** tab and
  (if `NOTIFY_EMAIL` is set) an email should arrive.

## Notes

- **Email alerts:** on by default to `hello@lemonelly.com`. Change or disable via
  the `NOTIFY_EMAIL` constant at the top of `Code.gs` (set it to `''` to turn
  email off and keep only the sheet). Re-deploy after editing:
  **Deploy → Manage deployments → Edit → New version.**
- **Columns** are defined by the `COLUMNS` list in `Code.gs`; the header row is
  created automatically on the first submission. Add/rename columns there.
- **CORS:** the page posts with `mode: 'no-cors'` and `text/plain`, which is the
  reliable pattern for a static site talking to Apps Script — no preflight, no
  extra config. The browser can't read the response, so the page treats a
  completed request as success and only falls back to manual send on a true
  network error.
- If you'd rather not run Apps Script at all, leave `SHEET_ENDPOINT` blank and the
  form keeps the old manual WhatsApp/email send screen — nothing breaks.
