# /start lead capture → Google Sheet

The `/start` onboarding form used to end on a screen that asked the prospect to
*manually* fire their brief off via WhatsApp or email — an easy place to lose a
lead. It now sends the finished brief straight to a Google Sheet and shows a
"we've got it" confirmation. WhatsApp/email stay as a silent fallback if the
network call ever fails.

There are two ways to receive submissions. **Option A (Google Form) is the
recommended one** — it needs no Google login and can't be blocked. Option B
(Apps Script) is kept for reference but hits a "This app is blocked" screen on
Workspace / high-security accounts, so skip it unless A doesn't suit you.

---

## Option A — Google Form → your sheet (recommended)

A Google Form accepts submissions anonymously and drops every response into a
linked sheet. No script, no authorization, nothing to be blocked. We just POST
the brief to the form's URL behind the scenes.

### 1. Build the form

1. Go to <https://forms.google.com> → **Blank form**. Name it e.g. "lemonelly leads".
2. Add these **Short answer** questions (exact names don't matter, order does not
   matter — we map them by ID). Make the last one **Paragraph**:
   - First name
   - Last name
   - Business
   - Email
   - Phone
   - Brief *(Paragraph — this holds the full formatted brief)*
3. **Responses** tab → **Link to Sheets** → *Select existing spreadsheet* →
   pick your leads sheet (or let it create one). Responses now flow into it.

### 2. Grab the form's action URL + field IDs

Easiest way, no code:

1. Top-right **⋮ → Get pre-filled link**.
2. Type a throwaway value into every field (e.g. `A`, `B`, `C`, `D`, `E`, `F`),
   then **Get link** → **Copy link**.
3. Paste that link somewhere you can read it. It looks like:
   ```
   https://docs.google.com/forms/d/e/1FAIpQL…/viewform?entry.111111=A&entry.222222=B&…
   ```
   Each `entry.NNNN` is a field ID, in the same order as your questions.

**Or just paste that pre-filled link to me and I'll wire the IDs in for you.**

### 3. Fill in `start/index.html`

Near the top of the `<script>`, set `FORM_ACTION` to the form URL with
`/viewform...` replaced by `/formResponse`, and map each `entry.NNNN` to a field:

```js
var FORM_ACTION = 'https://docs.google.com/forms/d/e/1FAIpQL…/formResponse';
var FORM_FIELDS = {
  'entry.111111': 'firstName',
  'entry.222222': 'lastName',
  'entry.333333': 'businessName',
  'entry.444444': 'email',
  'entry.555555': 'phone',
  'entry.666666': 'brief'
};
```

The `brief` field receives the whole formatted brief (style, domain, pages,
story, deep-dive answers, etc.) as one block of text, so nothing is lost even
though the form only has a handful of questions. Commit, let Vercel deploy, run
through `/start` and submit — a new row should appear in the sheet.

### Email alerts (optional)

On the linked sheet: **Tools → Notification settings → Any changes → Email right
away**. Or in the Form: **Responses → ⋮ → Get email notifications for new
responses**. Either is permission-free.

### Available fields to map

`firstName`, `lastName`, `businessName`, `email`, `phone`, `region`, `style`,
`styleTag`, `domain`, `pages`, `story`, `colors`, `assets`, `extras`,
`powerups`, `ddIdeal`, `ddDiff`, `ddJobs`, `ddTone`, `monthly`, `termsAgreed`,
`brief`. Map as many or as few as you like — the six above are plenty since
`brief` already contains everything in readable form.

---

## Option B — Apps Script web app (fallback)

Logs the full structured brief with one column per field. The catch: deploying
it makes Google ask you to authorize the script, and Workspace or
high-security personal accounts return a hard **"This app is blocked"** screen
with no way past it. If that happens, use Option A instead.

1. Open the sheet → **Extensions → Apps Script**, paste [`Code.gs`](./Code.gs), save.
2. **Deploy → New deployment → Web app**, *Execute as: Me*, *Who has access:
   Anyone*, authorize.
3. Copy the `/exec` URL into `SHEET_ENDPOINT` in `start/index.html` (leave
   `FORM_ACTION` blank). Commit.

`Code.gs` only touches this one spreadsheet — it deliberately doesn't send email
(that would request a sensitive Gmail permission and guarantee the block); use
the sheet's own notification rules for alerts.

---

## Notes

- **CORS:** the page posts with `mode: 'no-cors'`, so the browser can't read the
  response. It treats a completed request as success and only falls back to the
  manual send screen on a true network error. This is the standard, reliable
  pattern for a static site talking to Google Forms / Apps Script.
- Leave both `FORM_ACTION` and `SHEET_ENDPOINT` blank and the form keeps the old
  manual WhatsApp/email send screen — nothing breaks.
