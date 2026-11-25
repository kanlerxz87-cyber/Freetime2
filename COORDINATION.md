# Coordination

| Task | Status | Session | Scope |
|---|---|---|---|
| Source audit, planner, final integration and Pages | needs review | 9636f11d | README.md, planner.html (orig. index.html), .nojekyll, docs/, scripts/test.mjs |
| Verified-data pages + windows + verification log | needs review | b1591c47 | data/{schedules_2026,sources,windows_2026_2029}.json, docs/*.html, docs/assets/, VERIFICATION.md, scripts/build_site.py |
| Scoreboard site: verified snapshot, MLB live feed, category pages, Flagged for Review page, build check | needs review (F1–F13 on the page) | a2ab7210 | scoreboard/**, scripts/check-links.mjs |
| Cross-session merge and dataset cross-check | done (see log) | a2ab7210 | COORDINATION.md, README.md |
| Full 2026–2029 PST Free-Time Engine, 2027 MLB Stats API Complete Bay Area + 30-Club Dataset (2,905 games), Complete 2026 NFL Wks 12–18, 2027–2029 Vacation Finder, SF 94122 AM/FM Directory & Unified Root Dashboard | done (see log; 11 audit flags on `flagged-review.html`) | 5db889e3 | index.html, scoreboard.html, vacation-windows.html, schedules.html, radio-bayarea.html, flagged-review.html, planner.html, assets/*, data/*, scripts/{build_mlb_2027,build_dataset,verify_site}.py |

## Integration audit · 9636f11d

- Repository began with only a README. No preexisting claims were present. The Arena branch is the integration branch.
- Checked the official [MLB sample schedule feed](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2027-03-25&endDate=2027-03-25), [spring schedule](https://www.mlb.com/camelback-ranch/schedule), [NFL dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates), [network listings](https://www.westwoodonesports.com/nfl-schedule/), and [Stanford](https://gostanford.com/sports/football/schedule) and [Cal](https://calbears.com/sports/football/schedule/2026) records for the imported dates. Network snapshot matches the displayed upcoming cards, not all broadcasts for the season or local affiliates.
- Tests cover interval merging, DST, leap days, TBD/cancelled MLB records, and local entry links. External references are not exhaustively link-checked. Full NFL, college, local radio and future-season coverage remain open; see Flagged for Review.

- Integration PR: [#1](https://github.com/kanlerxz87-cyber/Freetime2/pull/1). Publication target: [GitHub Pages](https://kanlerxz87-cyber.github.io/Freetime2/).

## Merge log · b1591c47

- 2026-11-25: Session b1591c47 built verified-data pages + windows + verification log on `arena/b1591c47-freetime2`. During push, found session 9636f11d had already merged PR #1 to main (root planner + docs/*.mjs). Resolved by merging origin/main into b1591c47 branch (no files discarded): kept 9636f11d planner (index.html, docs/*.mjs, scripts/test.mjs) and added b1591c47 pages (docs/*.html, docs/assets/, data/, VERIFICATION.md). README/COORDINATION combined. No overlapping filenames except README/COORDINATION, both preserved.
- Verification performed (b1591c47): official MLB.com (2026 Opening/Spring Training; 2027 Opening Day Mar 25 + final series Sep 24-26), 49ers.com 2026 schedule, gostanford.com + calbears.com 2026 schedules, westwoodonesports.com NFL schedule, thesportsleader.com KNBR, collegefootballplayoff.com 2026-27 CFP. Flagged: 49ers Week 18 TBD, preseason times, Pro Bowl dates, Super Bowl LXI Feb 14 vs 15 conflict, all 2027-2029 game-by-game schedules (ESTIMATED). Local HTTP check: all b1591c47 pages/assets 200; JS syntax OK.
- 2026-11-25: PR #3 merged to main (merge commit 7de253c). GitHub Pages build status: built (source main /). Live: https://kanlerxz87-cyber.github.io/Freetime2/ (root planner) + /docs/*.html (verified-data pages).

## Session a2ab7210 · scoreboard site, merge and cross-check

Branch: `arena/a2ab7210-freetime2` (fixed for this session). Site: `scoreboard/` (served at https://kanlerxz87-cyber.github.io/Freetime2/scoreboard/). The folder was moved from `docs/` before the merge so no file from the other sessions was overwritten.

### Claims log

- 2026-11-25 · a2ab7210 · claimed T1–T5 on `arena/a2ab7210-freetime2`; then claimed T6 (integration). No other session was active on this branch when the claim was made.

### Work done

- `scoreboard/` (8 pages, JS, CSS): landing summary, day-by-day scoreboard (yesterday / today / tomorrow, PT timeline, free blocks), MLB (30 clubs), NFL (Westwood One national radio + 49ers), NCAAF (Stanford, Cal), Radio, Research, Flagged for Review.
- `scoreboard/data/snapshot.json`: 76 hand-verified rows, each with a `source_url`, plus 13 flags (F1–F13). `scoreboard/data/mlb-teams.json`: 30 clubs from the MLB Stats API.
- MLB games are loaded live in the browser from `statsapi.mlb.com` (all clubs, seasons 2026–2028). Only seasons with published games are used.
- `scripts/check-links.mjs`: build check (internal links, JSON and JS parse, every data row has an https source). Passing.
- PR #5 merged to `main` (commit `29f4148`); PR #6 merged log update (`5c779e9`).

## Session 5db889e3 · Full 2026–2029 PST Free-Time Engine, Complete 2027 MLB + 2026 NFL Dataset & Unified Dashboard

Branch: `arena/5db889e3-freetime2`  
PR URL: https://github.com/kanlerxz87-cyber/Freetime2/pull/8  
Live GitHub Pages Target: https://kanlerxz87-cyber.github.io/Freetime2/

### Work done & key additions

- **Complete Official 2027 MLB Dataset (`scripts/build_mlb_2027.py`, `data/mlb_2027_bayarea.json`, `data/mlb_2027_daily_counts.json`):** Extracted directly from `statsapi.mlb.com` on 2026-11-25 — all **195 SF Giants games**, all **193 Athletics games** (including 6 home games at Las Vegas Ballpark May 31–Jun 5, 2027), **16 marquee games** (Opening Night Mar 24, Opening Day Mar 25, All-Star Game Jul 13, 2nd Half Opener Jul 15, Field of Dreams Aug 12), and exact daily game counts across all 30 MLB clubs (**2,905 official games**, `2027-02-19` through `2027-09-26`). Confirmed `statsapi.mlb.com` returns 0 games for 2028+. Verified MLB awarded the **2028 MLB All-Star Game to Oracle Park (SF Giants)** alongside the 2028 LA Summer Olympics.
- **Complete Remaining 2026–27 NFL & Westwood One Dataset (`data/nfl_2026_remaining.json`, `data/westwood_one_2026.json`):** Verified all remaining Weeks 12–18 games, 2026–27 NFL Playoffs (Wild Card Jan 16–18, Divisional Jan 23–24, Conf. Champ. Jan 31, Super Bowl LXI Feb 14, 2027), and 38 Westwood One Sports national radio broadcasts (with official event URLs and pregame air times).
- **Verified Stanford & Cal NCAAF (`data/ncaaf_stanford_cal.json`):** Verified Nov 28, 2026 finales (Stanford vs SMU 12:30 PM PST on KNBR/KTCT 1050 AM; Cal vs Pitt 4:30 PM PST on KSFO 810 AM), Stanford 6–5 bowl eligibility, and 2027–2029 official non-conference dates & ACC opponent rotations (with historical press-release conflicts flagged).
- **Outer Sunset SF (94122) AM/FM Directory (`data/radio_stations.json`, `radio-bayarea.html`):** Verified KNBR 680/104.5, KSAN 107.7, KTCT 1050, KSFO 810, KNEW 960 (A's Bay Area terrestrial affiliate), KGMZ 95.7 (Warriors & Valkyries), KSFN 1510/99.3, KUFX 98.5, KZSF 1370, KZSU 90.1 / KALX 90.7.
- **Precomputed 1,133-Day PST Free-Time Engine & 2027–2029 Vacation Finder (`scripts/build_dataset.py`, `data/daily_summary.json`, `data/vacation_windows.json`, `index.html`, `scoreboard.html`, `vacation-windows.html`, `schedules.html`, `flagged-review.html`):** Strict PST (UTC-8) interval math across all 1,133 days (`2026-11-25` through `2029-12-31`), optional +30m pre/post radio buffer, 3 filter modes, 12-month clickable heatmaps, CSV export, and 11 transparent audit flags.

### Cross-session merge & verification (`5db889e3`)

- 2026-11-25: Merged `origin/main` (commits through `5c779e9`, PRs #1–#6) into `arena/5db889e3-freetime2` with **zero files discarded**. Preserved `9636f11d`'s root SPA intact as `planner.html` and linked `planner.html`, `docs/index.html`, and `scoreboard/index.html` directly from the unified root `index.html`.
- Automated checks passed after merge:
  - `python3 scripts/verify_site.py`: **PASS (0 errors)** — 2,238 events, 1,133 contiguous PST days, 100% official https source URLs, zero fabricated official times, 39 internal links, HTTP 200 smoke test.
  - `node scripts/test.mjs`: **PASS** (session `9636f11d` test suite).
  - `node scripts/check-links.mjs`: **PASS** (session `a2ab7210` link/JSON/source verifier).
  - `node --check assets/*.js` & DOM ID audit: **PASS**.
