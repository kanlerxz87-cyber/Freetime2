# FREE TIME VACATION — SF Bay Area Live Sports Radio Calendar (2026–2029)

Live GitHub Pages Dashboard: **https://kanlerxz87-cyber.github.io/Freetime2/**

A verified, source-linked static dashboard for **Outer Sunset, San Francisco (ZIP 94122)** that identifies exact **PST (UTC-8)** daily free-time windows and optimal **2027, 2028, and 2029** vacation stretches when **zero tracked live Bay Area AM/FM radio sports** are on air.

## Executive Summary (Verified Nov 25, 2026)

- **Regular Season + Postseason Only (Skipping MLB Spring Training Exhibitions):**
  - **2027 (VERIFIED OFFICIAL DATES):** **Mon, Feb 15 – Tue, Mar 23, 2027 = 37 consecutive game-free days (5+ weeks)** between Super Bowl LXI (Sun, Feb 14, 2027) and MLB Opening Night (Wed, Mar 24, 2027).
  - **2028 (ESTIMATED):** **Mon, Feb 14 – Wed, Mar 22, 2028 = ~38 consecutive days** (pending official 2028 MLB & Super Bowl LXII date confirmation; **note:** SF Giants officially host the **2028 MLB All-Star Game at Oracle Park in July 2028** alongside the **2028 LA Summer Olympics**!).
  - **2029 (ESTIMATED):** **Mon, Feb 12 – Wed, Mar 28, 2029 = ~45 consecutive days** (after Super Bowl LXIII in Las Vegas).
- **Strictest All-Sports Mode (Counting All 30 MLB Teams' Spring Training + NFL Playoffs + Pro Bowl):**
  - Because Super Bowl LXI (Feb 14, 2027) ends just **4 days** before MLB Spring Training begins (Feb 19, 2027), there is **no continuous 14-day or 21-day 100% zero-game streak** in 2027–2029.
  - Best strict low-impact 2–3 week window in 2027: **Feb 1 – Feb 18, 2027** (18 days with **16 zero-game days**, interrupted only by Pro Bowl Games & Super Bowl LXI), including **13 consecutive days (Feb 1–13)** with zero High-Priority Bay Area / Westwood One broadcasts.

## Primary Dashboard Pages (Session `5db889e3`, Repo Root `/`)

- **`index.html`** — Executive Summary, 2027–2029 vacation KPI cards, today's PST free-time snapshot, and researched average game durations/halftimes table.
- **`scoreboard.html`** — Interactive MLB/NFL-style Daily Scoreboard & Monthly Calendar (Nov 25, 2026 – Dec 31, 2029) with Yesterday/Today/Tomorrow buttons, visual 24-hour PST timeline, exact PST free-time windows, filter modes, and optional +30m pre/post radio buffer.
- **`vacation-windows.html`** — Deep 2027, 2028, and 2029 Vacation Window Finder with 1-week, 2-week, and 3-week rankings and a clickable 12-month calendar heatmap.
- **`schedules.html`** — Searchable, filterable, CSV-exportable master schedule tables covering all 2,238 verified & estimated events (including all 195 SF Giants + 193 Athletics + 2,905 all-MLB 2027 daily counts, all remaining 2026 NFL Weeks 12–18 & Playoffs, Westwood One, Stanford & Cal) with per-row official source links.
- **`radio-bayarea.html`** — Outer Sunset SF (94122) AM/FM Sports Radio Reception Directory (KNBR 680/104.5, KSAN 107.7, KTCT 1050, KSFO 810, KNEW 960, KGMZ 95.7, etc.) and verified 2026–27 Westwood One Sports NFL schedule.
- **`flagged-review.html`** — Transparent verification audit listing all 11 flagged irregularities, unreleased future schedules, TBD start times, historical NCAAF press-release conflicts, and radio reception caveats.

## Companion Multi-Session Views (Preserved Intact)

- **`planner.html`** (Session `9636f11d`) — Browser-live MLB Stats API single-page planner (`docs/app.mjs`, `docs/model.mjs`, `docs/data.mjs`).
- **`docs/index.html`** (Session `b1591c47`) — Supplementary verified-data pages (`docs/executive-summary.html`, `windows.html`, `schedules.html`, `radio.html`, `methodology.html`, `flagged.html`, `VERIFICATION.md`).
- **`scoreboard/index.html`** (Session `a2ab7210`) — Self-contained scoreboard with verified snapshot (`scoreboard/data/snapshot.json`, `scoreboard/schedule.html`, `mlb.html`, `nfl.html`, `ncaaf.html`, `radio.html`, `research.html`, `flagged.html`).

## Reproducing & Verifying Locally

```bash
python3 scripts/build_mlb_2027.py
python3 scripts/build_dataset.py
python3 scripts/verify_site.py
node scripts/test.mjs
node scripts/check-links.mjs
```

Coordination board: `COORDINATION.md`.

## Deep-Dive Verified Data Library (`docs/` — extended by this session)

The `docs/` library now also ships a parallel full dataset build (`tools/generate_schedules.py`, deterministic) and pages:

- **`docs/calendar.html`** — MLB/NFL-style scoreboard calendar (2026–2029): month grid, prev/today/next day navigation, per-day PT busy blocks with exact free-time ranges, hour-by-hour busy grid, click any day for every game + radio call + source link.
- **`docs/mlb.html`** — all 30 clubs 2026–2029 (~2,900 game rows/season) with high-priority flags + CSV export. **2027 SF Giants & Athletics fixtures (and 16 marquee games) are VERIFIED official rows from the MLB Stats API** (ingested from `data/mlb_2027_bayarea.json`); all other generated rows are labeled ESTIMATED.
- **`docs/nfl.html`**, **`docs/ncaaf.html`**, **`docs/westwood.html`** — same pattern; verified SF 49ers 2026 + officially remaining 2026 NFL weeks 12–18 and 2026–27 playoffs/Super Bowl LXI (from `data/nfl_2026_remaining.json` / `data/all_events.json`) appear as VERIFIED rows.
- **`docs/executive-summary.html` / `docs/windows.html`** — computed from `data/vacation_analysis.json`.
- **`docs/sources.html` / `docs/methodology.html` / `docs/flagged.html`** — source registry, model card, consolidated flags.
- **`docs/live-planner.html`** — preserved browser-live MLB Stats API planner.

Rebuild: `python3 tools/generate_schedules.py` (deterministic; imports the verified official overlays from this repo where present).
