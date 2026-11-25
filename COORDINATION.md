# COORDINATION — shared task board

Shared task board for parallel agent sessions. Read before starting; claim before editing.

Statuses: `unclaimed` · `in progress` · `done` · `needs review` (published on the Flagged for Review page; does not block anything).

Branch note: this session works only on `arena/a2ab7210-freetime2` (branched from `main` @ a6bb998). Per Arena rules, the `session-<id>/<task>` naming is not used because the session is fixed to its current branch.

## Task board

| # | Task | Status | Owner (session) | Branch | Files in scope |
|---|------|--------|-----------------|--------|----------------|
| T1 | Repo review + COORDINATION board | done | a2ab7210 | arena/a2ab7210-freetime2 | `COORDINATION.md`, `README.md` |
| T2 | Official schedule data: MLB 2027 (SF & ATH games + all 30 clubs), NFL 2026 national radio, 49ers, Stanford, Cal | done (needs review on flagged rows) | a2ab7210 | arena/a2ab7210-freetime2 | `docs/data/snapshot.json`, `docs/data/mlb-teams.json` |
| T3 | Radio station research (KNBR, KSAN, Stanford, A's, Westwood One) | done (needs review: F3, F10, F11) | a2ab7210 | arena/a2ab7210-freetime2 | `docs/radio.html` |
| T4 | Game-duration research (MLB / NFL / college) | done (needs review: F9) | a2ab7210 | arena/a2ab7210-freetime2 | `docs/research.html` |
| T5 | Site: landing, scoreboard calendar, category pages, Flagged for Review page | done | a2ab7210 | arena/a2ab7210-freetime2 | `docs/**` |
| T6 | Integration: link check, build check, PR to `main`, merge, Pages deploy | in progress | a2ab7210 | arena/a2ab7210-freetime2 | `scripts/check-links.mjs`, `docs/.nojekyll` |

Only one session is active on this branch right now. Another remote branch, `arena/9636f11d-freetime2`, exists on origin and was not touched.

## Claims log

- 2026-11-25 · a2ab7210 · claimed T1–T5 on `arena/a2ab7210-freetime2`. Scope: files listed above only.
- 2026-11-25 · a2ab7210 · claimed T6 (integration). No other session is active on this branch, so this session is also the integration session.

## Sources, verification and irregularities

Sources are logged per task as they are verified. Every data row in `docs/data/snapshot.json` carries its own `source_url`.

### Verification log (session a2ab7210, 2026-11-25)

| Item checked | Official source | Result |
|---|---|---|
| Westwood One NFL radio slate, Nov 25 2026 – Jan 10 2027 | https://www.westwoodonesports.com/nfl-schedule/ | 35 national-broadcast entries loaded; each row links to its westwoodonesports.com event page |
| 49ers 2026 schedule (regular season) | https://www.49ers.com/schedule/ | Weeks 12–18 loaded; radio flagship listed as KSAN 107.7 FM / KNBR 104.5 FM / 680 AM |
| Stanford 2026 football | https://gostanford.com/sports/football/schedule | Full season and results loaded; Nov 28 vs SMU open |
| Stanford 2026 radio team | https://gostanford.com/news/2026/07/30/2026-football-radio-broadcast-team-announced | States "KNBR/KTCT 1050 AM" |
| Cal 2026 football | https://calbears.com/sports/football/schedule/text and https://calbears.com/news/2026/11/15/football-2026-big-game-week-events | Schedule and results loaded; Nov 28 Pitt time conflicts (see flags) |
| MLB 2027 regular season released | https://www.mlb.com/press-release/press-release-orioles-announce-2027-regular-season-schedule (and Brewers, Pirates, Nationals releases dated Jul 16–17 2026) | Confirmed released; Opening Day Thu Mar 25 2027 |
| MLB team list (30 clubs) | https://statsapi.mlb.com/api/v1/teams?sportId=1 | 30 clubs loaded with venue and division |
| MLB 2027 Giants / Athletics games | https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId=137&season=2027 and teamId=133 | Present in the official feed; the site fetches the full feed live (see Flagged for Review) |
| MLB average game time 2025 | https://www.mlb.com/press-release/press-release-mlb-attendance-reaches-71-4-million-three-straight-years-of-growth-for-first-time-since-2007 | 2:38 |
| NFL average game time 2025 | Not official (third-party analysis of nflverse play-by-play: https://nflanalytic.com/explainer-how-long-is-an-nfl-game.html) | 3:02 median / 3:03 average. NFL official figure not located. |
| College football average game time | Not official (https://www.underarmour.com/en-us/t/playbooks/football/the-real-length-of-a-football-game/) | 3:27 cited. No official NCAA figure located. |
| KNBR station facts | https://en.wikipedia.org/wiki/KNBR_(AM) (secondary) and 49ers.com (primary for 49ers flagship) | 680 AM, 50 kW, Giants and 49ers affiliate |
| Athletics Bay Area flagship | Not confirmed by an official A's source in this session | Conflicting secondary sources; left unverified |
| Cal radio flagship | Not checked | Unverified |
| Reference site https://buffedlizard55-lab.github.io/RADIOSF/ | fetch failed | Not verified |
| Reference site https://buffedlizard55-lab.github.io/ScheduleFreeTime/ | not fetched | Not verified |
| Reference site https://buffedlizard55-lab.github.io/VacationSchedule/site/ | fetch failed | Not verified |

### Irregularities (flagged, not resolved)

1. **Kickoff time conflicts, NFL.com vs Westwood One** (Nov 25, Nov 26 ×3, Nov 27). Westwood One and NFL.com show different start times for the same games. Both are shown on the Flagged for Review page.
2. **49ers time conflicts** — 49ers.com lists 5:15 PM PT at Chargers (Dec 17) and 5:20 PM PT vs Eagles (Jan 3). Westwood One lists 7:30 PM ET (4:30 PM PT) for both.
3. **Stanford radio naming** — the official Stanford release names "KNBR/KTCT 1050 AM", while the 49ers and KNBR use KNBR 680 AM / 104.5 FM. Not resolved.
4. **Cal vs Pitt (Nov 28)** — the Cal scoreboard snippet shows 4:30 PM, while the Cal text schedule lists no time. Not confirmed.
5. **Stanford vs Cal (Nov 21)** — Stanford's official schedule shows a final result (W 44-28). Cal's text schedule shows no result. Stanford's score is used.
6. **CollegeFootballNetwork.com** (third party) shows a 2026 Stanford date and time for Nov 27 (Fri) and TBA for Nov 28. Official Stanford data shows Sat Nov 28, 12:30 PM PT. Third-party data not used.
7. **NFL 2027 schedule** — not on nfl.com in this session. Third-party sites state it is expected May 2027. Not treated as released.
8. **MLB 2027 start times** — many games are `startTimeTBD` in the official feed. Estimated times are labelled as estimates.
9. **Duration figures for NFL and college** come from non-official analysis sites. Flagged.
10. **Athletics flagship station** — secondary sources conflict (KNEW 960 / Bloomberg 960 / KGMZ 95.7). Left blank and flagged.
11. **Outer Sunset (94122) AM/FM reception** — no official reception data was located. Not claimed.
12. **Reference sites** — two of the three referenced GitHub Pages sites failed to fetch. Their contents are not used.
13. **Repository state on arrival** — the repo contained only a README. No prior data, no site, no coordination board existed.

## Log

- 2026-11-25 · a2ab7210 · T1 claimed; repo reviewed (README only). Shared board created.
- 2026-11-25 · a2ab7210 · T2–T5 built on this branch: `docs/` site (8 pages), `docs/data/snapshot.json` (76 hand-verified rows, 13 flags), `docs/data/mlb-teams.json` (30 clubs), `scripts/check-links.mjs` (build check, passing).
- 2026-11-25 · a2ab7210 · Calendar logic tested in Node against the snapshot and a sample of the MLB feed. A headless browser is not available in this sandbox, so the live MLB load was not tested in a real browser. Flagged for review.
- 2026-11-25 · a2ab7210 · Calendar de-duplication: the two 49ers games also on Westwood One (Dec 17, Jan 3) are marked `dup_of` so each game is counted once.
- 2026-11-25 · a2ab7210 · Coverage rule: a day is never shown as FREE. It shows GAMES ON THIS DAY, NO GAMES LISTED (not verified free), or UNKNOWN. NFL and NCAAF coverage is partial, so no day is verified free.
