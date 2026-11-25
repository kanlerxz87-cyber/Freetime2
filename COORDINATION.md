# COORDINATION — FREE TIME VACATION (`kanlerxz87-cyber/Freetime2`)

Last updated: **2026-11-25 (UTC)**  
Active session branch: `arena/5db889e3-freetime2` (branched from `main` @ `a6bb9988a242e5ddaaee78933e646fe54ff18834`)  
GitHub Pages live target: `https://kanlerxz87-cyber.github.io/Freetime2/` (legacy deploy from `main` `/`)

## Task Board

| ID | Task | Owner / Branch | Status | Notes |
| --- | --- | --- | --- | --- |
| T1 | Primary-source research & verification (MLB 2027 Stats API all 30 clubs + Giants 195 + A's 193, NFL 2026–27 Weeks 12–18 & Playoffs, Westwood One NFL radio, Stanford & Cal NCAAF 2026–2029, Outer Sunset SF 94122 AM/FM radio, avg durations/halftimes) | `arena/5db889e3-freetime2` | DONE | All 2026–2027 verified dates/times sourced directly from official primary sources; unreleased 2027 NFL/Postseason, 2028 & 2029 schedules clearly flagged as estimated. |
| T2 | Build reproducible Python data pipeline (`scripts/build_mlb_2027.py`, `scripts/build_dataset.py`) & normalized PST JSON datasets (`data/*.json`) | `arena/5db889e3-freetime2` | DONE | 2,238 events, 1,133 contiguous PST days (2026-11-25 to 2029-12-31), exact PST free/busy intervals, 2027–2029 vacation windows, 11 audit flags. |
| T3 | Build GitHub Pages static dashboard (`index.html`, `scoreboard.html`, `vacation-windows.html`, `schedules.html`, `radio-bayarea.html`, `flagged-review.html`, `assets/*`, `.nojekyll`) | `arena/5db889e3-freetime2` | DONE | Executive Summary, interactive PST Daily Scoreboard & Calendar (Yesterday/Today/Tomorrow + +30m radio buffer toggle), 12-month year heatmaps, CSV export, 94122 AM/FM directory, Flagged for Review page. |
| T4 | Automated verification (`scripts/verify_site.py`, JS syntax check, DOM ID audit, HTTP smoke test), PR to `main`, merge, & GitHub Pages deployment check | `arena/5db889e3-freetime2` | DONE | All local checks passed (0 errors); PR #8 created and ready for merge to `main`. |

## Verification Summary (2026-11-25)

- `python3 scripts/build_mlb_2027.py`: Verified **195** official 2027 SF Giants games, **193** official 2027 Athletics games (**380** unique Bay Area games + **16** marquee MLB games), and **2,905** total official 2027 MLB games across all 30 clubs (`2027-02-19` to `2027-09-26`).
- `python3 scripts/build_dataset.py`: Generated 10 JSON datasets covering **1,133 contiguous PST days** (`2026-11-25` through `2029-12-31`) and **2,238 events**.
- `python3 scripts/verify_site.py`: **0 errors** — 100% of rows carry valid `https://` official source URLs, 100% of TBD/estimated events have blank `officialTimePST`, 100% of days satisfy `freeMinutes + busyMinutes == 1440`, 39 internal links verified, HTTP 200 on all pages/assets.
- `node --check assets/*.js` & DOM ID consistency audit: **PASS** across all 6 HTML pages and 7 JS modules.

## Pull Request & Merge Record

- PR URL: https://github.com/kanlerxz87-cyber/Freetime2/pull/8
- Merge Status: Merging PR #8 into `main`
- GitHub Pages Deploy Target: https://kanlerxz87-cyber.github.io/Freetime2/
