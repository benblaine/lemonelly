"""One-time: create the public Google Form the homepage ghost-posts into.

Opens a browser for Google consent (forms + drive.file). Writes
reference/lead-capture/callback-form.json with the formResponse URL and
entry IDs, then prints the snippet to paste into the homepage template.

Does not print tokens.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRET = os.path.join(ROOT, "..", "tools", "sheets-update", "client_secret.json")
TOKEN_FILE = os.path.join(ROOT, "scripts", ".callback-form-token.json")
OUT_FILE = os.path.join(ROOT, "reference", "lead-capture", "callback-form.json")

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive.file",
]

QUESTIONS = [
    ("phone", "Phone", "TEXT"),
    ("who", "Who", "TEXT"),
    ("when", "When", "TEXT"),
    ("how", "How", "TEXT"),
    ("stage", "Stage", "TEXT"),
    ("page", "Page", "TEXT"),
    ("countryCode", "Country code", "TEXT"),
    ("brief", "Brief", "PARAGRAPH_TEXT"),
]


def creds():
    c = None
    if os.path.exists(TOKEN_FILE):
        c = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not c or not c.valid:
        if c and c.expired and c.refresh_token:
            c.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            c = flow.run_local_server(port=8765, prompt="consent")
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(c.to_json())
    return c


def main():
    forms = build("forms", "v1", credentials=creds())
    created = forms.forms().create(body={"info": {"title": "lemonelly callbacks", "documentTitle": "lemonelly callbacks"}}).execute()
    form_id = created["formId"]
    print("formId", form_id)

    requests = []
    for i, (_key, title, qtype) in enumerate(QUESTIONS):
        requests.append({
            "createItem": {
                "item": {
                    "title": title,
                    "questionItem": {
                        "question": {
                            "required": False,
                            "textQuestion": {"paragraph": qtype == "PARAGRAPH_TEXT"},
                        }
                    },
                },
                "location": {"index": i},
            }
        })
    forms.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()

    try:
        forms.forms().setPublishSettings(
            formId=form_id,
            body={"publishSettings": {"publishState": {"isPublished": True, "isAcceptingResponses": True}}},
        ).execute()
    except Exception as e:
        print("setPublishSettings skipped:", type(e).__name__, str(e)[:200])

    form = forms.forms().get(formId=form_id).execute()
    responder = form.get("responderUri") or ""
    print("responderUri", responder)
    if "/viewform" not in responder:
        sys.exit("no responderUri")
    action = responder.split("?")[0].replace("/viewform", "/formResponse")

    html = urllib.request.urlopen(responder, timeout=20).read().decode("utf-8", "replace")
    entries = []
    for m in re.finditer(r"entry\.(\d+)", html):
        eid = "entry." + m.group(1)
        if eid not in entries:
            entries.append(eid)
    print("entries", entries)

    # Map in document order; Google usually emits one entry id per question.
    fields = {}
    for i, (key, _title, _t) in enumerate(QUESTIONS):
        if i < len(entries):
            fields[entries[i]] = key

    out = {"formId": form_id, "responderUri": responder, "FORM_ACTION": action, "FORM_FIELDS": fields, "entries": entries}
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("wrote", OUT_FILE)
    print("FORM_ACTION =", json.dumps(action))
    print("FORM_FIELDS =", json.dumps(fields, indent=2))


if __name__ == "__main__":
    main()
