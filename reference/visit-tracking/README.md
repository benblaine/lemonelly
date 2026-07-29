# Draft-page visit tracking → Google Sheet

Logs an anonymous page view every time someone opens a `/draft/<slug>` page, so
you can see which prospects have looked at their draft. Data lands in **your**
sheet and never expires:

<https://docs.google.com/spreadsheets/d/1cDNNxqy1a_k_Eu_Y5GyC5nvcfDN6f0dQjuWIrSF9YFQ/>

## How it works (no third-party tracker)

1. Each draft page runs a tiny script that fires a **same-origin** beacon to
   `lemonelly.com/api/hit` — the draft never contacts Google, Vercel Analytics,
   or any third-party host, so the "zero external requests" rule still holds.
   (It uses `navigator.sendBeacon`, with a 1×1 `<img>` pixel fallback.)
2. `api/hit.js` (a Vercel serverless function) adds the visitor's user-agent and
   Vercel's geo headers (country / region / city — no precise IP is stored) and
   POSTs the hit to the Apps Script web app below.
3. `Code.gs`, bound to the sheet, appends one row per visit to a **Visits** tab
   (auto-created on the first hit): Time · Draft · Referrer · Country · Region ·
   City · User agent · Path.

Because the beacon needs JavaScript, Gmail/Apple-Mail image proxies (which
prefetch `<img>`s but don't run JS) **don't** create phantom hits — a logged row
means a real browser opened the page.

## Setup (~3 minutes, one-time)

1. **Add the script to the sheet.** Open the visits sheet →
   **Extensions → Apps Script** → replace the contents with
   [`Code.gs`](./Code.gs) → **Save**.
2. **Deploy it as a web app.** **Deploy → New deployment** → gear ⚙ →
   **Web app**. Set **Execute as: Me** and **Who has access: Anyone** →
   **Deploy** → authorize when prompted → **copy the `/exec` URL**.
   - You can paste that `/exec` URL into a browser tab to sanity-check it — it
     should return `{"ok":true,"msg":"lemonelly visit tracking is live"}`.
3. **Give the URL to the site.** In **Vercel → the lemonelly project →
   Settings → Environment Variables**, add:
   - `VISIT_SHEET_ENDPOINT` — the `/exec` URL from step 2 (tick **Production**
     and **Preview**).
4. **Redeploy** (Vercel → Deployments → ⋮ → **Redeploy**, or just push any
   commit) so the function picks up the new variable.

That's it. Open any `https://lemonelly.com/draft/<slug>` page yourself and a row
should appear in the **Visits** tab within a few seconds.

> Until `VISIT_SHEET_ENDPOINT` is set, `/api/hit` simply returns nothing and
> logs nowhere — the drafts keep working exactly as before, so there's no rush
> and nothing to break in the meantime.

## Reading the data

- **Per-draft counts:** in the sheet, insert a pivot table (Insert → Pivot
  table) with **Draft** as rows and **COUNTA of Draft** as values — that's your
  "visits per prospect" table. Add **Time** as a filter for a date range.
- **Filter bots:** most non-human traffic never runs the beacon, but you can
  still eyeball the **User agent** column and exclude obvious crawlers.
- **Unique-ish visitors:** the sheet logs every page view (not deduped). For a
  rough "did they open it at all", a non-zero count per Draft is the signal.

## Notes

- No cookies, no login, no precise IP — only coarse geo from Vercel's edge
  headers, stored in a sheet you own.
- The beacon lives in `template/draft.template.html`, so every **future** draft
  built via the `/draft` skill is tracked automatically — no per-page wiring.
- `reference/` is excluded from the deployed site via `.vercelignore`, so this
  script and README are never published on lemonelly.com.
