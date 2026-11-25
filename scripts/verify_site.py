#!/usr/bin/env python3
"""
Automated end-to-end verification suite for FREE TIME VACATION (Freetime2).
Checks:
  1. All required static pages, assets, data JSONs, and .nojekyll exist.
  2. 100% of rows across all datasets carry a valid https:// official sourceUrl.
  3. Zero fabricated official times: every TBD / ESTIMATED event has blank officialTimePST.
  4. Contiguous 1,133-day PST daily summary with exact free+busy=1440 math.
  5. Zero broken internal href/src/loadJSON links across all HTML and JS files.
  6. Local HTTP server returns HTTP 200 for every HTML, CSS, JS, and JSON file.
"""

import http.server
import json
import re
import socketserver
import sys
import threading
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    ".nojekyll",
    "README.md",
    "COORDINATION.md",
    "index.html",
    "scoreboard.html",
    "vacation-windows.html",
    "schedules.html",
    "radio-bayarea.html",
    "flagged-review.html",
    "assets/styles.css",
    "assets/common.js",
    "assets/home.js",
    "assets/scoreboard.js",
    "assets/vacation.js",
    "assets/schedules.js",
    "assets/radio.js",
    "assets/flagged.js",
    "data/metadata.json",
    "data/radio_stations.json",
    "data/westwood_one_2026.json",
    "data/mlb_2027_bayarea.json",
    "data/mlb_2027_daily_counts.json",
    "data/nfl_2026_remaining.json",
    "data/ncaaf_stanford_cal.json",
    "data/projections_2027_2029.json",
    "data/all_events.json",
    "data/daily_summary.json",
    "data/vacation_windows.json",
    "data/flagged_items.json",
]

errors = []


def fail(msg):
    errors.append(msg)
    print(f"FAIL: {msg}")


def check_files():
    for rel in REQUIRED_FILES:
        p = ROOT / rel
        if not p.exists():
            fail(f"Missing required file: {rel}")
        elif rel != ".nojekyll" and p.stat().st_size == 0:
            fail(f"Empty required file: {rel}")


def check_json_integrity():
    all_events = json.loads((ROOT / "data/all_events.json").read_text())["events"]
    daily = json.loads((ROOT / "data/daily_summary.json").read_text())["days"]
    stations = json.loads((ROOT / "data/radio_stations.json").read_text())["stations"]
    ww1 = json.loads((ROOT / "data/westwood_one_2026.json").read_text())["broadcasts"]
    meta = json.loads((ROOT / "data/metadata.json").read_text())
    flags = json.loads((ROOT / "data/flagged_items.json").read_text())["items"]
    mlb = json.loads((ROOT / "data/mlb_2027_bayarea.json").read_text())

    # 1. MLB official counts
    if mlb["giantsCount"] != 195:
        fail(f"Expected 195 Giants games, got {mlb['giantsCount']}")
    if mlb["athleticsCount"] != 193:
        fail(f"Expected 193 Athletics games, got {mlb['athleticsCount']}")

    # 2. Every single row has valid official https:// sourceUrl
    for i, ev in enumerate(all_events):
        url = ev.get("sourceUrl", "")
        if not url.startswith("https://"):
            fail(f"all_events[{i}] ({ev.get('id')}) missing https sourceUrl: {url!r}")
        if ev["status"] == "ESTIMATED" and ev.get("officialTimePST"):
            fail(f"Estimated event {ev['id']} must have blank officialTimePST, got {ev['officialTimePST']!r}")
        if ev.get("startTimeTBD") and ev.get("officialTimePST"):
            fail(f"TBD event {ev['id']} must have blank officialTimePST, got {ev['officialTimePST']!r}")
        if ev["status"] == "VERIFIED" and not ev.get("officialTimePST", "").endswith(" PST"):
            fail(f"Verified event {ev['id']} missing PST officialTimePST: {ev.get('officialTimePST')!r}")

    for s in stations:
        if not s.get("sourceUrl", "").startswith("https://"):
            fail(f"Radio station {s.get('callSign')} missing https sourceUrl")
    for b in ww1:
        if not b.get("sourceUrl", "").startswith("https://"):
            fail(f"Westwood One broadcast {b.get('date')} missing https sourceUrl")
    for d in meta["durations"]:
        if not d.get("sourceUrl", "").startswith("https://"):
            fail(f"Duration row {d.get('category')} missing https sourceUrl")
    for fl in flags:
        if not fl.get("sourceUrl", "").startswith("https://"):
            fail(f"Flagged item {fl.get('id')} missing https sourceUrl")

    # 3. Contiguous daily summary 2026-11-25 through 2029-12-31 + exact PST interval math
    cur = date(2026, 11, 25)
    end = date(2029, 12, 31)
    expected_days = (end - cur).days + 1
    if len(daily) != expected_days:
        fail(f"Expected {expected_days} daily records, got {len(daily)}")

    for idx, rec in enumerate(daily):
        exp_iso = (cur + timedelta(days=idx)).isoformat()
        if rec["date"] != exp_iso:
            fail(f"Daily date mismatch at index {idx}: expected {exp_iso}, got {rec['date']}")
        if rec["freeMinutes"] + rec["busyMinutes"] != 1440:
            fail(f"Minute sum != 1440 on {rec['date']}: free={rec['freeMinutes']} busy={rec['busyMinutes']}")
        busy_sum = sum(b[1] - b[0] for b in rec["busyIntervalsPST"])
        free_sum = sum(f[1] - f[0] for f in rec["freeIntervalsPST"])
        if busy_sum != rec["busyMinutes"] or free_sum != rec["freeMinutes"]:
            fail(f"Interval sum mismatch on {rec['date']}")

    print(f"OK: Verified {len(all_events)} events, {len(daily)} contiguous PST days, {len(stations)} radio stations, {len(ww1)} WW1 broadcasts, {len(flags)} audit flags.")


def check_internal_links():
    html_files = list(ROOT.glob("*.html"))
    js_files = list((ROOT / "assets").glob("*.js"))

    href_re = re.compile(r'(?:href|src)="([^"]+)"')
    json_re = re.compile(r'loadJSON\("([^"]+)"\)')

    checked = 0
    for hf in html_files:
        txt = hf.read_text()
        for target in href_re.findall(txt):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            path_part = target.split("?")[0].split("#")[0]
            if not path_part:
                continue
            checked += 1
            if not (ROOT / path_part).exists():
                fail(f"Broken local link in {hf.name}: {target}")

    for jf in js_files:
        txt = jf.read_text()
        for target in json_re.findall(txt):
            checked += 1
            if not (ROOT / target).exists():
                fail(f"Broken JSON fetch in {jf.name}: {target}")
        for target in href_re.findall(txt):
            if target.startswith(("http://", "https://", "#", "mailto:")) or "${" in target:
                continue
            path_part = target.split("?")[0].split("#")[0]
            if not path_part:
                continue
            checked += 1
            if not (ROOT / path_part).exists():
                fail(f"Broken local link in {jf.name}: {target}")

    print(f"OK: Checked {checked} internal HTML/JS links and JSON fetches — zero broken links.")


def check_http_smoke():
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT), **kwargs)

        def log_message(self, format, *args):
            pass

    with socketserver.TCPServer(("127.0.0.1", 0), QuietHandler) as httpd:
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            for rel in REQUIRED_FILES:
                if rel in ("COORDINATION.md", "README.md", ".nojekyll"):
                    continue
                url = f"http://127.0.0.1:{port}/{rel}"
                with urllib.request.urlopen(url, timeout=5) as resp:
                    if resp.status != 200:
                        fail(f"HTTP {resp.status} for {rel}")
                    body = resp.read()
                    if len(body) < 10:
                        fail(f"Unexpectedly small HTTP body ({len(body)} bytes) for {rel}")
            print(f"OK: Local HTTP smoke test passed (HTTP 200 on all web pages, JS, CSS, and JSON assets).")
        finally:
            httpd.shutdown()


def main():
    check_files()
    check_json_integrity()
    check_internal_links()
    check_http_smoke()
    if errors:
        print(f"\nVERIFICATION FAILED with {len(errors)} error(s).")
        sys.exit(1)
    print("\nALL VERIFICATION CHECKS PASSED (0 errors).")


if __name__ == "__main__":
    main()
