---
name: draft
description: Create a hosted draft website redesign for a roofing/local-trade company from their current website URL, to pitch lemonelly's services. Accepts one URL or a list. Use when Ben gives prospect website URLs and wants draft pages at lemonelly.com/draft/<slug>.
---

# /draft <url> [<url> ...] — build a pitch draft per prospect

Output per company: a page at `draft/<slug>/index.html` (live at
`https://lemonelly.com/draft/<slug>` after merge), a fact sheet at
`reference/clients/<slug>.md`, and a 3-sentence pitch-email snippet for Ben.

**Batch mode:** run steps 1–6 per company (research may fan out via subagents;
adaptation stays per-company so each draft is tailored). Ship the whole batch
on ONE branch/PR so Ben reviews everything in a single Vercel preview. Hand
back a table: company → live URL → pitch snippet.

## Steps

1. **Fetch & extract.** WebFetch the URL plus nav-linked subpages
   (about/services/contact/testimonials, ≤6 pages). Extract: trading + legal
   name, phone(s), email, address & service areas, full services list, tagline,
   years established, accreditations, testimonials (verbatim, attributed as
   shown), brand cues (logo, colors), real job photos worth reusing. Thin or
   JS-walled site → supplement with web search (Google Business / Facebook).
   Record a source URL + fetch date for every fact.

2. **Fact sheet** at `reference/clients/<slug>.md`. Headings: Business,
   Contact, Services, Areas, Proof (testimonials/accreditations), Brand,
   Sources, `Status: drafted YYYY-MM-DD`. Facts only — no sales commentary.

3. **Slug:** lowercase compact from trading name or domain (e.g.
   `roofersharrogate`); hyphens only if unreadable without. Permanent once the
   pitch email is sent.

4. **Copy** `template/draft.template.html` → `draft/<slug>/index.html`.

5. **Adapt** (the craft step — this is where the draft earns the pitch):
   - Retheme `--accent / --accent-deep / --accent-text` to their brand color.
     Contrast-check: accent-text on white ≥4.5:1, ink on accent ≥4.5:1 — shift
     to the nearest passing shade if needed. (Default is a warm construction
     orange; most roofers suit orange/red/deep-blue.)
   - Redraw the SVG wordmark with their name; replace ALL Kestrel content from
     the fact sheet.
   - Prune/reshape sections to fit reality:
     - **Services grid** defaults to 3 columns. 4 services → keep `repeat(3,1fr)`
       or switch to `repeat(4,1fr)` for one clean row; 6 → two rows of 3.
     - **Testimonial + CTA pair**: if the prospect has a real, attributable
       review, use it verbatim in the testimonial card. If NOT, replace the
       whole testimonial card with a second value/CTA panel — never invent one.
     - **Stats strip**: needs ≥3 verifiable figures (years, areas, crew size,
       "Free" quotes). If you can't fill it honestly, delete the section.
     - **Feature band** (4 columns): honest value props, not fabricated stats.
   - Images: prefer the prospect's own photos (copy to `assets/draft/<slug>/`)
     when quality allows; otherwise pick from `assets/draft/stock/` by READING
     the images and matching service semantics (filenames are descriptive:
     `hero-slate-*`, `svc-grp-*`, `svc-leadwork-*`, `work-stone-*`, etc.). Spec:
     hero ≤1600px wide, cards ≤1000px, page image total ≤1.5MB; `loading="lazy"`
     below the fold, `fetchpriority="high"` on the hero, width/height on all imgs.
   - Hero: serif H1 from their real positioning (trade + town), one italic
     `.em` emphasis word; tick-list = only real value props; badge number = a
     VERIFIABLE figure (years trading / areas covered). Localize phone format,
     spelling, terms (Velux vs skylights).
   - Badge links to the matching regional page (UK company → /uk, etc.).
   - Title (browser tab): `lemonelly · <Company> (draft)` — always lead with
     lemonelly. Fill og tags (og:image = the hero image, absolute URL). Keep
     both disclaimers AND the `.lm-draft-banner` at the top of `<body>`
     ("Draft website — for review only").
   - HARD RULE: never invent reviews, ratings, review counts, project totals,
     prices ("starting at £X"), certifications (GAF/BBB-style badges), or "our
     work" claims. Stock-filled galleries stay framed as "the kind of work we
     handle".

6. **QA checklist** (all must pass):
   - `grep -ri kestrel draft/<slug>/` → nothing.
   - Every tel:/mailto: matches the fact sheet.
   - No external requests: `grep -oE '(src|href)="https?://[^"]*"' draft/<slug>/index.html`
     shows only lemonelly.com URLs.
   - No fabricated proof: `grep -riE 'starting at|4\.9|5-star|[0-9],[0-9]{3}\+|BBB|GAF' draft/<slug>/`
     returns nothing (unless it's a real, sourced figure from the fact sheet).
   - All referenced local assets exist; summed image payload ≤1.5MB.
   - `noindex, nofollow` meta present; `git diff sitemap.xml` empty;
     `robots.txt` still has `Disallow: /draft/`.

7. **Preview:** `python3 -m http.server 8000` → check `/draft/<slug>/` (and
   that `/` is unaffected) at desktop and ~375px widths.

8. **Ship:** run `python3 scripts/build_admin.py` to refresh the private
   drafts tracker (`reference/DRAFTS.md`); then branch → commit page + fact
   sheet + per-company assets + the tracker → push → draft PR → Ben eyeballs
   the Vercel preview → merge → live.

9. **Hand back:** live URL(s) + a 3-sentence pitch-email draft per company
   (free concept, built from their real details, no strings). When Ben
   confirms he's emailed them, update the fact sheet to `Status: emailed`.

## Maintenance rules

- Restyle only via the template + `reference/inspiration/`; shipped drafts are
  frozen snapshots unless Ben asks.
- Removing a draft: delete `draft/<slug>/` + `assets/draft/<slug>/`; KEEP the
  fact sheet with an updated status; keep the robots rule.
- Never hand-edit `sitemap.xml` or the generated region pages.
- New stock goes in `assets/draft/stock/` with descriptive names
  (`svc-flat-roof-membrane.jpg`) — the filename is the index.
- Design system reference screenshots live in `reference/inspiration/`
  (`ref-summit-roofing` is the primary light/premium roofing reference the
  template is built from). Fonts are self-hosted in `assets/draft/fonts/`
  (Archivo body + Fraunces serif display, both OFL, latin variable woff2).
