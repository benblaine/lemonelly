# lemonelly

Landing page for lemonelly — websites that win trust for local businesses. Proudly built in Cape Town.

One static page, no build step, no dependencies, zero external requests.

## Design system ("corporate partner")

- Background `#FFFFFF`, alternate band `#F7F7F5`
- Ink `#111110`, secondary text `#55524A` (both ≥7:1 contrast)
- Accent green `#166548` (white text on it: 7:1), hover `#0F4F37`
- Lemon yellow `#FFD335` appears only in the logo mark
- System font stack, pill buttons, 24px-radius cards, hairline borders `#E8E6E1`

## Regional pages

The site ships five pages generated from one template: `/` (global, USD) plus `/za`, `/us`,
`/uk`, `/eu` — each with regional pricing, audience wording, and metadata. A geography
toggle in the navbar links between them, and `hreflang` tags tie them together for search.

**To change copy or layout**: edit `template/index.template.html`.
**To change a region's prices or wording**: edit `regions.json`.
Then regenerate all pages and commit the results:

```sh
python3 scripts/build.py
```

Never edit `index.html` or `za|us|uk|eu/index.html` directly — they're generated and will
be overwritten by the next build.

## Preview locally

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000/ (regional pages at /za/, /us/, /uk/, /eu/)

## Images

All swappable by replacing the file — no code changes needed:

| File | Used | Spec |
|---|---|---|
| `assets/veronica.jpg` | Hero + team | roughly square, ≥800px, <150KB |
| `assets/ben.jpg` | Hero + team | roughly square, ≥800px, <150KB |
| `assets/work-lostwax.jpg` | Work card | Lost Wax Foundry site imagery |
| `assets/work-neurabuild.jpg` | Work card | Neurabuild homepage screenshot |

If a photo file is missing, the page falls back to styled initials / a text plate automatically.

## Client drafts

Sales-pitch website redesigns for local businesses, served at
`lemonelly.com/draft/<slug>` (noindex, excluded in robots.txt, never in the
sitemap). Built by copying `template/draft.template.html` and adapting it per
company — see `.claude/skills/draft/SKILL.md` for the full workflow (`/draft <url>`).
Prospect fact sheets live in `reference/clients/`; shared stock imagery and the
self-hosted font in `assets/draft/`. `reference/`, `template/` and friends are
excluded from deploy via `.vercelignore`.

## Deploy

Vercel deploys `main` to lemonelly.com automatically. `404.html` is picked up by most static hosts.
