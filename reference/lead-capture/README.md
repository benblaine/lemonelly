# /start lead capture → Google Sheet

The `/start` onboarding form used to end on a screen that asked the prospect to
*manually* fire their brief off via WhatsApp or email — an easy place to lose a
lead. It now sends the finished brief straight to us — by email or into a Google
Sheet, depending on which option below you set up — and shows a "we've got it"
confirmation. WhatsApp/email stay as a silent fallback if the network call ever
fails.

Three ways to receive submissions:

- **Option C — Serverless email + Gmail app password.** *(default, active now)*
  Leads land in your inbox. Uses SMTP, not OAuth, so the "This app is blocked"
  screen never appears. Just set two env vars in Vercel.
- **Option A — Google Form → your sheet.** No login at all, rows in a sheet.
- **Option B — Apps Script.** Full structured rows, but the authorize step is
  hard-blocked on Workspace / high-security accounts. Kept only as a fallback.

The page uses whichever is configured, in the order C → A → B.

---

## Option C — Serverless email via Gmail app password (default)

`start/index.html` already posts each brief to our own `/api/lead` function
(`api/lead.js`), which emails it to you. An **app password** is a Gmail login
that skips OAuth entirely, so it can't trigger the block you hit. It lives only
in Vercel's environment — never in the page.

### Setup (~3 minutes)

1. **Turn on 2-Step Verification** for the Gmail account (app passwords require
   it): <https://myaccount.google.com/security>.
2. **Create an app password:** <https://myaccount.google.com/apppasswords> →
   name it "lemonelly" → **Create** → copy the 16-character code (no spaces).
3. In **Vercel → your lemonelly project → Settings → Environment Variables**, add:
   - `GMAIL_USER` — the sending Gmail address (e.g. `hello@lemonelly.com` or your
     `@gmail.com`)
   - `GMAIL_APP_PASSWORD` — the 16-char code from step 2
   - `LEAD_TO` *(optional)* — where leads should arrive; defaults to `GMAIL_USER`
4. **Redeploy** (Vercel → Deployments → ⋮ → Redeploy, or just push) so the
   function picks up the vars.

That's it — submit a test brief through `/start` and it should hit your inbox.
Until the vars are set, `/api/lead` returns an error and the form quietly falls
back to the manual WhatsApp/email screen, so nothing breaks in the meantime.

> ⚠️ **Workspace note:** app passwords only exist if the account has 2-Step
> Verification and the option isn't disabled by a Workspace admin. If step 2
> shows no "App passwords" page, use **Option A (Google Form)** instead — it
> needs no password at all.

This gives you email only (not sheet rows). Want the data in the sheet too? Run
Option A alongside, or ask and I'll switch `/api/lead` to also write the sheet
via a service account.

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
