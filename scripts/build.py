#!/usr/bin/env python3
"""Generate the root page and the four regional pages from one template.

    python3 scripts/build.py

Edit template/index.template.html (layout/copy) or regions.json (per-region
values), then re-run and commit the generated pages alongside your edit.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGION_ORDER = ["za", "us", "uk", "eu"]

template = (ROOT / "template" / "index.template.html").read_text()
regions = json.loads((ROOT / "regions.json").read_text())


def region_nav(active_code):
    links = []
    for key in REGION_ORDER:
        r = regions[key]
        current = ' aria-current="true"' if r["code"] == active_code else ""
        links.append(f'<a href="/{r["path"]}"{current}>{r["code"]}</a>')
    return ('<span class="region-nav" role="group" aria-label="Choose your region">'
            + "".join(links) + "</span>")


urls = []
for key, r in regions.items():
    html = template
    values = {
        "TITLE": r["title"],
        "META_DESC": r["meta_desc"],
        "OG_TITLE": r["og_title"],
        "OG_DESC": r["og_desc"],
        "CANONICAL": r["canonical"],
        "SETUP": r["setup"],
        "MONTHLY": r["monthly"],
        "LEDE_AUDIENCE": r["lede_audience"],
        "TRADES": r["trades"],
        "AREA_SERVED": r["area_served"],
        "REGION_NAV": region_nav(r["code"]),
    }
    for k, v in values.items():
        html = html.replace("{{" + k + "}}", v)
    if "{{" in html:
        start = html.index("{{")
        sys.exit(f"unresolved placeholder near: {html[start:start+40]!r}")

    out = ROOT / r["path"] / "index.html" if r["path"] else ROOT / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    urls.append(r["canonical"])
    print(f"wrote {out.relative_to(ROOT)}")

sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sitemap += [f"  <url><loc>{u}</loc></url>" for u in urls]
sitemap.append("</urlset>")
(ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n")
print("wrote sitemap.xml")
