# Coordination

Shared task board for all agent sessions working on this repository.

| Task | Status | Session | Scope |
|---|---|---|---|
| Source audit, planner, final integration and Pages | needs review | 9636f11d | README.md, index.html, .nojekyll, docs/, scripts/ |
| Verified-data pages + windows + verification log | needs review | b1591c47 | data/, docs/*.html, docs/assets/, VERIFICATION.md, scripts/build_site.py |
| Final integration: full estimated 2026–2029 datasets (all 30 MLB clubs, all NFL, Stanford/Cal NCAAF, Westwood One national NFL radio), executive summary, calendar scoreboard, vacation-window analysis, radio reception audit, PR/merge/Pages verify | done (see log) | arena-458f184e | data/, tools/, docs/, assets/, COORDINATION.md |

## Integration audit · 9636f11d

- Repository began with only a README. No preexisting claims were present. The Arena branch is the integration branch.
- Checked the official [MLB sample schedule feed](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2027-03-25&endDate=2027-03-25), [spring schedule](https://www.mlb.com/camelback-ranch/schedule), [NFL dates](https://www.nfl.com/news/2026-27-national-football-league-important-dates), [network listings](https://www.westwoodonesports.com/nfl-schedule/), and [Stanford](https://gostanford.com/sports/football/schedule) and [Cal](https://calbears.com/sports/football/schedule/2026) records for the imported dates. Network snapshot matches the displayed upcoming cards, not all broadcasts for the season or local affiliates.
- Tests cover interval merging, DST, leap days, TBD/cancelled MLB records, and local entry links. External references are not exhaustively link-checked. Full NFL, college, local radio and future-season coverage remain open; see Flagged for Review.

- Integration PR: [#1](https://github.com/kanlerxz87-cyber/Freetime2/pull/1). Publication target: [GitHub Pages](https://kanlerxz87-cyber.github.io/Freetime2/).

## Merge log · b1591c47

- 2026-11-25: Session b1591c47 built verified-data pages + windows + verification log on `arena/b1591c47-freetime2`. During push, found session 9636f11d had already merged PR #1 to main (root planner + docs/*.mjs). Resolved by merging origin/main into b1591c47 branch (no files discarded): kept 9636f11d planner (index.html, docs/*.mjs, scripts/test.mjs) and added b1591c47 pages (docs/*.html, docs/assets/, data/, VERIFICATION.md). README/COORDINATION combined. No overlapping filenames except README/COORDINATION, both preserved.
- Verification performed (b1591c47): official MLB.com (2026 Opening/Spring Training; 2027 Opening Day Mar 25 + final series Sep 24-26), 49ers.com 2026 schedule, gostanford.com + calbears.com 2026 schedules, westwoodonesports.com NFL schedule, thesportsleader.com KNBR, collegefootballplayoff.com 2026-27 CFP. Flagged: 49ers Week 18 TBD, preseason times, Pro Bowl dates, Super Bowl LXI Feb 14 vs 15 conflict, all 2027-2029 game-by-game schedules (ESTIMATED). Local HTTP check: all b1591c47 pages/assets 200; JS syntax OK.
- 2026-11-25: PR #3 merged to main (merge commit 7de253c). GitHub Pages build status: built (source main /). Live: https://kanlerxz87-cyber.github.io/Freetime2/ (root planner) + /docs/*.html (verified-data pages).

## Session arena-458f184e · Final integration pass (2026-11-25)

**Mode:** picked up after both prior sessions merged (PRs #1, #3, #4). Rebased `arena/458f184e-freetime2` onto `ea9ec69` and combined this file (both predecessor logs preserved). No predecessor files were deleted or overwritten in scope; this session extends the site.

**What was done (this session):**
- Re-researched all official anchor dates independently (MLB 2026/2027 announcements, NFL 2026-27 postseason dates, Super Bowl LXI, CFP title games, Stanford/Cal 2026, Westwood One NFL schedule captured live 2026-11-25, Bay Area AM/FM landscape: KNBR 680/104.5, KSAN 107.7, KSFO 810, KNEW 960, KSTE 650, KTCT 1050, KIQI 1010).
- Added an estimated-schedule engine (`tools/generate_schedules.py`) producing game-level rows for **all 30 MLB clubs** (2026–2029 incl. spring training, regular season, All-Star, postseason) and **all NFL games** (2026–2029 incl. preseason, regular season, postseason; 49ers 2026 uses the officially announced times/dates) for the busy/free calendar. Rows are tagged `estimated` unless anchored to an official announcement.
- Added Westwood One national NFL radio broadcast rows (2026 list verified live) and Bay Area radio reception analysis for the Outer Sunset, 94122.
- Extended the site: calendar scoreboard (prev/next day, PT times, per-day free blocks), vacation windows 2027/2028/2029, tables per league, sources page, flagged-for-review page.
- Found and recorded irregularities (see Flagged for Review page), incl. possible MLB CBA work stoppage affecting 2027, undecided NFL 2027+ format (18-game question), stale radio call letters in third-party sources, KTCT daytimer limits.
- Corrected one premise from the brief: the 2026/2027 MLB schedules are officially released, but game-by-game rows could not be fetched in the restricted build environment, so every game row is an ESTIMATED reconstruction anchored to verified season windows; anchor dates are verified and marked as such.

## Pull request / merge record

- PRs #1 (9636f11d), #3 (b1591c47), #4 merged to main before this session. Pages live at https://kanlerxz87-cyber.github.io/Freetime2/ (verified Built by b1591c47; re-verified after this session's merge).
- (Final entry appended by arena-458f184e after this session's PR is merged.)
