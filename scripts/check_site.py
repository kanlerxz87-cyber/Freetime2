#!/usr/bin/env python3
"""Static checks for site links and schedule/source references."""
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        for key in ("href", "src"):
            val=attrs.get(key)
            if val: self.links.append(val)

errors=[]
for js in (SITE/"app.js", SITE/"data.js"):
    res=subprocess.run(["node","--check",str(js)],capture_output=True,text=True)
    if res.returncode: errors.append(f"JS syntax: {js.name}: {res.stderr.strip()}")

for html in sorted(SITE.glob("*.html")):
    parser=LinkParser(); parser.feed(html.read_text())
    for link in parser.links:
        if link.startswith(("https://","http://","mailto:","#","data:")): continue
        target=(html.parent/link.split("#",1)[0]).resolve()
        if not target.exists(): errors.append(f"Broken local link: {html.name} -> {link}")

src= (SITE/"data.js").read_text()
try:
    payload=subprocess.run(["node","-e", "const fs=require('fs');const t=fs.readFileSync(process.argv[1],'utf8');const d=new Function(t+'\\nreturn {SOURCES,MLB_TEAMS,EVENTS,SEASON_WINDOWS};')();process.stdout.write(JSON.stringify(d));",str(SITE/"data.js")],capture_output=True,text=True,check=True)
    data=json.loads(payload.stdout)
except Exception as exc:
    errors.append(f"Could not parse data.js: {exc}"); data={}

if data:
    source_ids={s["id"] for s in data["SOURCES"]}
    if len(data["MLB_TEAMS"]) != 30 or len(set(data["MLB_TEAMS"])) != 30:
        errors.append("MLB scope must contain exactly 30 unique clubs")
    for kind,rows in (("event",data["EVENTS"]),("window",data["SEASON_WINDOWS"])):
        for i,row in enumerate(rows,1):
            ids=row.get("sourceIds",[])
            if not ids: errors.append(f"{kind} row {i} has no source IDs")
            for sid in ids:
                if sid not in source_ids: errors.append(f"{kind} row {i} references missing source {sid}")
            if kind=="event" and row.get("verification")=="verified" and not row.get("date"):
                errors.append(f"verified event row {i} has blank date")
            if kind=="event" and row.get("time")=="TBD" and row.get("verification")=="verified":
                errors.append(f"event row {i} has TBD time but is labeled verified")

# Source register JSON must parse and have unique IDs.
try:
    register=json.loads((ROOT/"data/sources.json").read_text())
    ids=[s["id"] for s in register["sources"]]
    if len(ids)!=len(set(ids)): errors.append("data/sources.json has duplicate source IDs")
    if data and set(ids)!=source_ids: errors.append("JS source IDs and data/sources.json IDs do not match")
except Exception as exc: errors.append(f"data/sources.json: {exc}")

if errors:
    print("CHECK FAILED")
    print("\n".join(f"- {e}" for e in errors))
    raise SystemExit(1)
print(f"OK: {len(list(SITE.glob('*.html')))} HTML pages, JS syntax, 30 MLB clubs, and event/window sources checked.")
