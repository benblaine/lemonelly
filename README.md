# lemonelly

Landing page for lemonelly — websites that win trust for local businesses. Proudly built in Cape Town.

One static page, no build step, no dependencies, zero external requests.

## Design system ("corporate partner")

- Background `#FFFFFF`, alternate band `#F7F7F5`
- Ink `#111110`, secondary text `#55524A` (both ≥7:1 contrast)
- Accent green `#166548` (white text on it: 7:1), hover `#0F4F37`
- Lemon yellow `#FFD335` appears only in the logo mark
- System font stack, pill buttons, 24px-radius cards, hairline borders `#E8E6E1`

## Preview locally

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000/

## Images

All swappable by replacing the file — no code changes needed:

| File | Used | Spec |
|---|---|---|
| `assets/veronica.jpg` | Hero + team | roughly square, ≥800px, <150KB |
| `assets/ben.jpg` | Hero + team | roughly square, ≥800px, <150KB |
| `assets/work-lostwax.jpg` | Work card | Lost Wax Foundry site imagery |
| `assets/work-neurabuild.jpg` | Work card | Neurabuild homepage screenshot |

If a photo file is missing, the page falls back to styled initials / a text plate automatically.

## Deploy

Vercel deploys `main` to lemonelly.com automatically. `404.html` is picked up by most static hosts.
