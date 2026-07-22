# lemonelly

Landing page for lemonelly — fresh, fast websites for local businesses. Proudly built in Cape Town.

One static page, no build step, no dependencies, zero external requests.

## Preview locally

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000/

## Team photos

The team section works without photos (styled initials show instead). To add the real
headshots, drop these two files into `assets/` — no code changes needed:

| File | Who | Spec |
|---|---|---|
| `assets/veronica.jpg` | Veronica Kotze | square crop, ≥800×800px, under ~150KB |
| `assets/ben.jpg` | Ben Blaine | square crop, ≥800×800px, under ~150KB |

## Before launch

- [ ] Replace the placeholder WhatsApp number in `index.html` (search for `wa.me`) with the
      real number in international format (e.g. `https://wa.me/2782xxxxxxx`).
- [ ] Add the two team photos (see above).

## Deploy

Any static host works (Cloudflare Pages, Netlify, GitHub Pages, plain nginx). Upload the
repo contents as-is; `404.html` is picked up automatically by most static hosts.
