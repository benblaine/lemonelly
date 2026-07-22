# lemonelly

Landing page for lemonelly — fresh, fast websites for local businesses. Proudly built in Cape Town.

One static page, no build step, no dependencies, zero external requests.

## Preview locally

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000/

## Illustration slots (replace with Grok output)

The page ships with placeholder flat illustrations. To swap in your own art (e.g. generated
with Grok), just replace these files — exact same filenames, no code changes:

| File | Used | Spec |
|---|---|---|
| `assets/pattern.png` | Hero + contact backgrounds, 404 page | **Seamless/tileable** square, ~360×720px works too, transparent background (the page behind it is mint `#44C593`) |
| `assets/hero-lemon.png` | Hero illustration | ~640×480px, **transparent background** (PNG) |

Suggested Grok prompts:

- **pattern.png**: "Seamless repeating pattern tile of flat vector lemon slices, bright yellow
  `#FFD335` slices with cream `#FFF9E3` rind, subtle soft shadows, on a transparent background,
  minimal flat illustration style, evenly spaced polka-dot layout, perfectly tileable"
- **hero-lemon.png**: "Single whole lemon with a green leaf, flat vector illustration style,
  bright yellow `#FFD335` body with subtle speckles, green `#2E9B70` leaf, soft drop shadow,
  transparent background, minimal and playful"

Keep each file under ~150KB. If a file is missing, the page degrades gracefully (plain mint
background / no hero image).

## Team photos

The real headshots live at `assets/veronica.jpg` and `assets/ben.jpg`. To swap either one,
just replace the file (roughly square crop, ≥800px, under ~150KB) — no code changes needed.
If a photo file is missing, the page falls back to styled initials automatically.

## Deploy

Any static host works (Cloudflare Pages, Netlify, GitHub Pages, plain nginx). Upload the
repo contents as-is; `404.html` is picked up automatically by most static hosts.
