# COORDINATION.md — Shared Task Board

This file coordinates work on `kanlerxz87-cyber/Freetime2` (Free Time Vacation & SF Bay Area Sports Radio Planner).

## Session Policy
- Active session branch: `arena/5db889e3-freetime2`
- Verification standard: Every table row must cite an official verified source URL. Unreleased future schedules or TBD times are kept blank in official columns, explicitly marked as estimated where projections are required, and logged on the Flagged for Review page.

## Task Board

| Task ID | Task | Status | Session ID | File Scope |
|---|---|---|---|---|
| T1 | Repository audit & coordination setup | in progress | `arena/5db889e3-freetime2` | `COORDINATION.md`, `README.md` |
| T2 | Official schedule research & verification (MLB 2026–2029, NFL 2026–2029, Stanford & Cal NCAAF 2026–2029) | in progress | `arena/5db889e3-freetime2` | `data/sources.json`, `data/schedules-*.json`, `scripts/build_data.py` |
| T3 | Bay Area AM/FM radio (Outer Sunset SF 94122) & Westwood One Sports NFL radio verification | in progress | `arena/5db889e3-freetime2` | `data/radio_stations.json`, `data/westwood_one.json` |
| T4 | Verified game duration research & PST minute-by-minute free-time engine + 2027–2029 vacation window analysis | in progress | `arena/5db889e3-freetime2` | `scripts/analyze_freetime.py`, `data/vacation_windows.json`, `data/daily_index.json` |
| T5 | GitHub Pages dashboard site (Landing/Executive Summary, Daily Scoreboard & Calendar, Vacation Windows, Schedule Tables, Bay Area Radio, Flagged for Review) | unclaimed | `arena/5db889e3-freetime2` | `index.html`, `pages/*.html`, `assets/*`, `.nojekyll` |
| T6 | Final integration, line-by-line verification, broken-link check, PR creation, merge, and GitHub Pages deploy check | unclaimed | `arena/5db889e3-freetime2` | All site files, `COORDINATION.md` |

## Session Log
- **2026-11-25** (`arena/5db889e3-freetime2`): Initialized `COORDINATION.md` and claimed T1–T4. Confirmed GitHub Pages is configured for `main` branch `/` root (`https://kanlerxz87-cyber.github.io/Freetime2/`).
