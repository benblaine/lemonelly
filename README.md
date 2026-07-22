# lemonelly

Landing page for lemonelly — fresh, fast websites for local businesses. Proudly built in Cape Town.

One static page, no build step, no dependencies, zero external requests.

## Preview locally

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000/

## Team photos

The real headshots live at `assets/veronica.jpg` and `assets/ben.jpg`. To swap either one,
just replace the file (roughly square crop, ≥800px, under ~150KB) — no code changes needed.
If a photo file is missing, the page falls back to styled initials automatically.

## Deploy

Any static host works (Cloudflare Pages, Netlify, GitHub Pages, plain nginx). Upload the
repo contents as-is; `404.html` is picked up automatically by most static hosts.
