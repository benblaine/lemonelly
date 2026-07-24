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
     to the nearest passing shade if needed.
   - Redraw the SVG wordmark with their name; replace ALL Kestrel content from
     the fact sheet.
   - Prune/reshape sections to fit reality: no testimonials → drop that
     section; 4 services → 2×2 grid. Don't pad with filler.
   - Images: prefer the prospect's own photos (copy to `assets/draft/<slug>/`,
     compressed to spec) when quality allows; otherwise pick from
     `assets/draft/stock/` by READING the images and matching service
     semantics. Spec: hero ≤1600px/≤250KB, cards ≤1000px/≤160KB, page total
     ≤1.5MB; `loading="lazy"` below the fold, `fetchpriority="high"` on the
     hero, width/height attributes on all imgs.
   - Hero copy from their actual positioning: trade + town ("Roofers in
     Harrogate"). Localize phone format, spelling, terms (Velux vs skylights).
   - Badge links to the matching regional page (UK company → /uk, etc.).
   - Title: `<Company> | <trade> in <Town> · Draft by lemonelly`. Fill og
     tags (og:image = the hero image, absolute URL). Keep both disclaimers.
   - HARD RULE: never invent reviews, stats, certifications, or "our work"
     claims. Stats band uses verifiable facts only; stock-filled galleries stay
     framed as "the kind of work we handle".

6. **QA checklist** (all must pass):
   - `grep -ri kestrel draft/<slug>/` → nothing.
   - Every tel:/mailto: matches the fact sheet.
   - No external requests: `grep -oE '(src|href)="https?://[^"]*"' draft/<slug>/index.html`
     shows only lemonelly.com URLs.
   - All referenced local assets exist; summed image payload ≤1.5MB.
   - `noindex, nofollow` meta present; `git diff sitemap.xml` empty;
     `robots.txt` still has `Disallow: /draft/`.

7. **Preview:** `python3 -m http.server 8000` → check `/draft/<slug>/` (and
   that `/` is unaffected) at desktop and ~375px widths.

8. **Ship:** branch → commit page + fact sheet + per-company assets → push →
   draft PR → Ben eyeballs the Vercel preview → merge → live.

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
