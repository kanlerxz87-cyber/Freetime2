# Coordination

| Task | Status | Session | Scope |
|---|---|---|---|
| Source audit, planner, final integration and Pages | needs review | 9636f11d | README.md, index.html, .nojekyll, docs/, scripts/ |
| Verified-data pages + windows + verification log | needs review | b1591c47 | data/, docs/*.html, docs/assets/, VERIFICATION.md, scripts/build_site.py |
| Scoreboard site: verified snapshot, MLB live feed, category pages, Flagged for Review page, build check | needs review (F1–F13 on the page) | a2ab7210 | scoreboard/**, scripts/check-links.mjs |
| Cross-session merge and dataset cross-check | done (see log) | a2ab7210 | COORDINATION.md, README.md |

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

### Verification performed (session a2ab7210, 2026-11-25)

| Item | Official source | Result |
|---|---|---|
| Westwood One NFL radio, Nov 25 2026 – Jan 10 2027 | https://www.westwoodonesports.com/nfl-schedule/ | 35 national games; each row links to its event page |
| 49ers 2026 | https://www.49ers.com/schedule/ | Weeks 12–18 and preseason/regular results; radio KSAN 107.7 / KNBR 104.5 / 680 AM |
| Stanford 2026 | https://gostanford.com/sports/football/schedule | Full season with results; Nov 28 vs SMU open |
| Stanford radio team (names KNBR/KTCT 1050 AM) | https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced | Conflicts with KNBR 680 (F3) |
| Cal 2026 | https://calbears.com/sports/football/schedule/text and https://calbears.com/news/2026/11/15/football-2026-big-game-week-events | Results loaded; Nov 28 time conflict (F4) |
| MLB 2027 released | https://www.mlb.com/press-release/press-release-orioles-announce-2027-regular-season-schedule (and Brewers, Pirates, Nationals, Jul 16–17 2026) | Released; Opening Day Thu Mar 25 2027 |
| MLB 30 clubs | https://statsapi.mlb.com/api/v1/teams?sportId=1 | 30 clubs |
| MLB 2027 Giants and Athletics | https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=137&season=2027 (and teamId=133) | Games present in the official feed |
| MLB average game 2025 | https://www.mlb.com/press-release/press-release-mlb-attendance-reaches-71-4-million-three-straight-years-of-growth-for-first-time-since-2007 | 2:38 (official) |
| NFL average game 2025 | https://nflanalytic.com/explainer-how-long-is-an-nfl-game.html (third party) | 3:03 average, 3:02 median (F9) |
| College average | https://www.underarmour.com/en-us/t/playbooks/football/the-real-length-of-a-football-game/ (third party) | 3:27 (F9) |

### Irregularities (open; listed on the site's Flagged for Review page)

F1 NFL kickoff times differ between Westwood One and NFL.com (Nov 26 Bears, Chiefs; Nov 27 Broncos) · F2 49ers times differ between 49ers.com and Westwood One (Dec 17, Jan 3) · F3 Stanford radio name vs KNBR 680 · F4 RESOLVED: Cal vs Pittsburgh is 4:30 PM PT on Cal's official schedule · F5 RESOLVED: Big Game result agrees on both school sites · F6 CollegeFootballNetwork conflicts with Stanford official (not used) · F7 NFL 2027 schedule not released · F8 MLB TBD start times (estimate 6:40 PM PT) · F9 NFL and college durations are third party · F10 Athletics Bay Area flagship unverified · F11 Outer Sunset (94122) reception unverified · F12 RADIOSF and VacationSchedule reference sites did not load; ScheduleFreeTime not fetched · F13 repository had no prior content · F14 Stanford kickoff times for Oct 3, Oct 31 and Nov 14 not published on the official page (left blank).

### Merge with other sessions (integration)

- 2026-11-25 · a2ab7210 · `origin/main` already contained PRs #1–#4 from sessions 9636f11d and b1591c47 (root planner, `docs/` verified-data pages, `data/`, `VERIFICATION.md`). Those files were kept unchanged. The scoreboard site was moved from `docs/` to `scoreboard/` so no file collided. The README and this board were merged by keeping the other sessions' content and adding this section.
- Overlap noted: the root planner (9636f11d) and `scoreboard/` (a2ab7210) both implement a 2026–2029 daily view with MLB live data. Both are kept. Each states its own coverage limits. The two datasets are cross-checked below.

### Cross-check against the other sessions' data

Compared line by line with `data/schedules_2026.json` (session b1591c47) and `docs/*` on `main`.

| Item | This session (official page) | Other session | Result |
|---|---|---|---|
| 49ers Wk 1–18 games and days | 49ers.com | matches | agree |
| 49ers Wk 15 Dec 17 / Wk 17 Jan 3 times | 49ers.com 5:15 / 5:20 PM PT | same | agree (Westwood One 4:30 PM PT conflicts, F2) |
| 49ers Wk 18 date | 49ers.com: TBD | 2027-01-10 | **their date is not on 49ers.com; blank here** |
| 49ers Wk 1, 3, 7, 11 times | 49ers.com shows FINAL, no time | 5:35 PM, 1:05 PM, 10:00 AM, 5:20 PM | **not confirmed on the fetched page; left as theirs, not verified here** |
| Preseason Aug 13, 20, 27 | 49ers.com: L 13-19, W 41-17, W 18-12 | theirs has Aug 13/20/27 with no results | added the results (Aug 20 and 27 were missing here) |
| Stanford results Aug 29–Nov 14 | gostanford.com | — | verified; my earlier draft had kickoff times for Oct 3, Oct 31 and Nov 14 that I could not confirm, now blank (F14) |
| Stanford Oct 17, Oct 23 times | not on fetched page | 4:30 PM / 7:30 PM PT | agree with theirs; kept |
| Cal full 2026 incl. Nov 28 | calbears.com text schedule | Nov 28 4:30 PM | agree; F4 resolved |
| Westwood One named games | westwoodonesports.com (ET) | 27 games listed | agree on every game checked; both sets use the same ET→PT conversion |
| NFL.com Bears / Chiefs / Broncos | NFL.com (1:00 PM / 8:20 PM / 3:00 PM ET) | Westwood One | conflict (F1) |

Correction made in this session: the first draft of F1 listed NFL.com times for Packers at Rams and Eagles at Cowboys that were never fetched. Those were removed. Both values are now labelled as not compared.

## Log · a2ab7210

- 2026-11-25 · a2ab7210 · T1 claimed; repo reviewed (README only). Shared board created.
- 2026-11-25 · a2ab7210 · Scoreboard site built on this branch and tested in Node (busy blocks, free gaps, midnight wrap, Pacific conversion, TBD estimates, coverage rules). A headless browser is not available in this sandbox, so the live MLB load was not tested in a real browser. Flagged.
- 2026-11-25 · a2ab7210 · The two 49ers games also on Westwood One (Dec 17, Jan 3) are marked `dup_of` so each is counted once.
- 2026-11-25 · a2ab7210 · Coverage rule: a day is never shown as FREE. It shows GAMES ON THIS DAY, NO GAMES LISTED (not verified free), or UNKNOWN. NFL and NCAAF coverage is partial, so no day is verified free.
- 2026-11-25 · a2ab7210 · PR from `arena/a2ab7210-freetime2` to `main`: first attempt (#5) could not merge because `main` had moved. Resolved by merging `origin/main` into this branch (no files discarded), moving the site to `scoreboard/`, and merging the two COORDINATION and README files.
- 2026-11-25 · a2ab7210 · **Integration result.** PR #5 (`arena/a2ab7210-freetime2` → `main`) merged with a merge commit at 2026-11-25T13:56:00Z; main is now `29f4148`. Merge was clean after `main` was merged into the branch (no files deleted).
- 2026-11-25 · a2ab7210 · **Pages deploy confirmed.** GitHub Pages API: latest build `built` for commit `29f4148`; source `main` `/`; site https://kanlerxz87-cyber.github.io/Freetime2/ (root planner and `/docs/` pages from other sessions). The `/scoreboard/` pages are in the same build. Live URLs could not be fetched from this sandbox (`github.io` is not on the outbound allowlist), so the build status is the confirmation available here.
- 2026-11-25 · a2ab7210 · Status of this board: T1–T5 done (needs review on F1–F3, F6–F14); T6 done. This log entry was committed on the branch and then merged to `main` by a follow-up docs-only PR, because pushing to `main` directly is not allowed for this session.
