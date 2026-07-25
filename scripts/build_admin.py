#!/usr/bin/env python3
"""Generate reference/DRAFTS.md and reference/leads.csv — private indexes of
every client draft.

Scans draft/<slug>/ pages and their reference/clients/<slug>.md fact sheets and
writes two artifacts:
  - reference/DRAFTS.md  — a human-readable Markdown table (company, live URL,
    status, contact).
  - reference/leads.csv  — the machine-owned factual columns for the outreach
    CRM sheet: Slug, Company, Owner, Draft URL, Original Site, Phone, Email,
    Address, Verify notes. This is the "data feed" half of the CRM; the human-
    owned columns (Outreach Status / Date Contacted / Owner notes) live only in
    the sheet and are never generated here, so a refresh never clobbers them.

Run it after adding or updating a draft:  python3 scripts/build_admin.py

Lives under reference/ (and scripts/), which .vercelignore keeps OUT of the
deployed site — this list of prospects is never published on lemonelly.com.
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFT_DIR = ROOT / "draft"
CLIENTS_DIR = ROOT / "reference" / "clients"
OUT = ROOT / "reference" / "DRAFTS.md"
OUT_CSV = ROOT / "reference" / "leads.csv"
LIVE_BASE = "https://lemonelly.com/draft"


def first(pattern, text, default=""):
    m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else default


def clean(value):
    """Strip markdown bold and trailing source/provenance notes."""
    value = value.replace("**", "")
    # cut at an em/en dash, ". Source", "Source:", "(source", "(home", "(2026"
    value = re.split(
        r"\s+[—–]\s+|\.\s*Source|\s+Source:|\s*\(source|\s*\(home|\s*\(2026",
        value,
        flags=re.IGNORECASE,
    )[0]
    return value.strip().rstrip(".")


def title_company(slug):
    idx = DRAFT_DIR / slug / "index.html"
    if not idx.exists():
        return slug
    t = first(r"<title>(.*?)(?:\s*\||</title>)", idx.read_text(encoding="utf-8"))
    return t or slug


def original_site(text):
    """First http(s) URL under the '## Sources' heading — the prospect's live site."""
    m = re.search(r"^##\s+Sources\s*$(.*?)(?=^##\s|\Z)", text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if not m:
        return "—"
    u = first(r"^-\s*(https?://\S+)", m.group(1))
    return u or "—"


def parse(slug):
    fact = CLIENTS_DIR / f"{slug}.md"
    company, phone, email, status, owner, site = title_company(slug), "", "", "drafted?", "—", "—"
    if fact.exists():
        text = fact.read_text(encoding="utf-8")
        h = first(r"^#\s+(.*)$", text)
        if h:
            company = clean(re.split(r"\s+[—–]\s+", h)[0])
        phone = clean(first(r"^-?\s*Phone[^:]*:\s*(.+)$", text)) or "—"
        email = clean(first(r"^-?\s*Email[^:]*:\s*(.+)$", text)) or "—"
        status = first(r"^Status:\s*(.+)$", text) or "drafted?"
        owner = first(r"^Assigned:\s*(.+)$", text) or "—"
        site = original_site(text)
    return company, owner, phone, email, status, site


# --- CSV ("data feed") extraction -------------------------------------------
# The Markdown table above intentionally truncates phone/email at the first
# provenance note (via clean()). The CSV wants the fuller, sheet-ready values,
# so it re-parses the fact sheet with wrap-aware helpers below.

# Parenthetical/trailer content that is provenance or a caveat, not part of the
# contact detail itself — stripped from the Phone/Email cells.
PROVENANCE = re.compile(
    r"20\d\d|\bsite\b|\bsource\b|\bhome\b|\bcontact\b|\bpage\b|\.htm|footer|"
    r"verif|decod|obfuscat|cloak|differ|typo|plain text|\bNOTE\b|\bfax\b|"
    r"Cloudflare|Joomla|Trustpilot|\bdomain\b|broken|published|as published|"
    r"formatting|likely",
    re.IGNORECASE,
)
# The subset of the above worth surfacing to a human before they make contact.
CAVEAT = re.compile(
    r"verif|decod|obfuscat|cloak|differ|typo|Cloudflare|Joomla|\bdomain\b|"
    r"broken|likely",
    re.IGNORECASE,
)


def tidy_note(s):
    """Strip a leading 'NOTE:'/'CAUTION:' or 'site, 2026-… —' provenance prefix
    from a harvested caveat so the Verify-notes cell reads cleanly."""
    s = re.sub(r"^(?:NOTE|CAUTION)\b[:\s]+", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^(?:site|source)\b[^—–]*[—–]\s*", "", s, flags=re.IGNORECASE)
    return s.strip(" —–.:")


def logical_value(label, text):
    """Full value after a '- Label:' bullet, including wrapped continuation
    lines, with runs of whitespace collapsed to single spaces."""
    m = re.search(
        rf"^-?\s*{label}[^:]*:\s*(.+?)(?=\n-\s|\n\n|\n##\s|\Z)",
        text,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    return " ".join(m.group(1).replace("**", "").split()) if m else ""


def split_contact(value):
    """Split a raw phone/email value into (clean_contact, [caveat_notes]).

    Parentheticals that read as provenance ('(site, 2026-07-24)') or caveats
    ('(decoded from Cloudflare — verify)') are removed from the contact; the
    caveat ones are harvested into notes. Short qualifiers such as '(office)'
    or '(mobile)' are kept in place."""
    notes = []

    def repl(m):
        inner = m.group(0)[1:-1].strip()
        if PROVENANCE.search(inner):
            if CAVEAT.search(inner):
                notes.append(inner.strip(" —–"))
            return ""
        return m.group(0)

    # Drop provenance/caveat parentheticals (supports one level of nesting,
    # e.g. capitalroofing's "(… published as +44 (0)20 …)").
    contact = re.sub(r"\((?:[^()]|\([^()]*\))*\)", repl, value)
    # A trailing provenance clause written outside parentheses, introduced by
    # ' — ', '. Source', or ' Source:' (e.g. mattboyd's ". Source: https://…").
    m = re.search(r"\s+[—–]\s+|\.\s+Source\b|\s+Source:\s*", contact, re.IGNORECASE)
    if m and PROVENANCE.search(contact[m.start():]):
        tail = contact[m.end():]
        if CAVEAT.search(contact[m.start():]):
            notes.append(tail.strip(" —–.:"))
        contact = contact[: m.start()]
    contact = " ".join(contact.split()).strip(" ,.;").strip()
    return contact, notes


def flag_lines(text):
    """Explicit 'NOTE:' / 'CAUTION:' lines authors added to a fact sheet."""
    out = []
    for m in re.finditer(
        r"^-?\s*(?:NOTE|CAUTION)\b[:\s]\s*(.+?)(?=\n-\s|\n\n|\n##\s|\Z)",
        text,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    ):
        out.append(" ".join(m.group(1).split()))
    return out


def csv_row(slug):
    """Machine-owned factual columns for one draft, for the CRM data feed."""
    company, owner, _, _, _, site = parse(slug)
    phone = email = address = ""
    notes = []
    fact = CLIENTS_DIR / f"{slug}.md"
    if fact.exists():
        text = fact.read_text(encoding="utf-8")
        phone, pnotes = split_contact(logical_value("Phone", text))
        email, enotes = split_contact(logical_value("Email", text))
        # Some fact sheets put phone and email on one line ("… · Email: x@y").
        # If no dedicated Email bullet was found, lift the email out of phone.
        if not email:
            m = re.search(r"[\w.+-]+@[\w.-]+\.\w+", phone)
            if m:
                email = m.group(0)
                phone = re.split(r"\s*(?:·|\|)?\s*Email\s*:?|\s+" + re.escape(email),
                                 phone, maxsplit=1)[0].strip(" ·|")
        # Postal address, with provenance parens/tails ("(site, 2026-07-24)",
        # "— source: …") stripped the same way as phone/email.
        address, _ = split_contact(logical_value("Address", text))
        notes = pnotes + enotes + flag_lines(text)
    seen, verify = set(), []
    for n in (tidy_note(n) for n in notes):
        if n and n not in seen:
            seen.add(n)
            verify.append(n)
    return {
        "Slug": slug,
        "Company": company,
        "Owner": owner,
        "Draft URL": f"{LIVE_BASE}/{slug}",
        "Original Site": site if site != "—" else "",
        "Phone": phone,
        "Email": email,
        "Address": address,
        "Verify notes": " · ".join(verify),
    }


def write_csv(slugs):
    cols = [
        "Slug", "Company", "Owner", "Draft URL", "Original Site",
        "Phone", "Email", "Address", "Verify notes",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for slug in slugs:
            w.writerow(csv_row(slug))


def main():
    slugs = sorted(p.name for p in DRAFT_DIR.iterdir() if (p / "index.html").exists())
    rows = []
    counts = {}
    for slug in slugs:
        company, owner, phone, email, status, site = parse(slug)
        key = status.split()[0].lower() if status else "unknown"
        counts[key] = counts.get(key, 0) + 1
        url = f"{LIVE_BASE}/{slug}"
        site_cell = f"[{site.split('//', 1)[-1].rstrip('/')}]({site})" if site != "—" else "—"
        rows.append(
            f"| {company} | {owner} | [`/draft/{slug}`]({url}) | {status} | {phone} | {email} | {site_cell} |"
        )

    summary = " · ".join(f"{n} {k}" for k, n in sorted(counts.items()))
    lines = [
        "# Client drafts — tracker",
        "",
        "_Generated by `python3 scripts/build_admin.py` — do not hand-edit._",
        "Private: `reference/` is excluded from the deployed site via `.vercelignore`.",
        "To change a draft's status or owner, edit the `Status:` / `Assigned:` line "
        "in its `reference/clients/<slug>.md`, then re-run the script.",
        "",
        f"**{len(slugs)} drafts** — {summary}",
        "",
        "| Company | Owner | Draft URL | Status | Phone | Email | Original Site |",
        "|---|---|---|---|---|---|---|",
        *rows,
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    write_csv(slugs)
    print(
        f"Wrote {OUT.relative_to(ROOT)} and {OUT_CSV.relative_to(ROOT)} "
        f"({len(slugs)} drafts)"
    )


if __name__ == "__main__":
    main()
