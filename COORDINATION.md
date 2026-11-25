# COORDINATION.md — Freetime2 Shared Task Board

> **Protocol:** Before starting, every session reads this file. Claim a task by writing your
> session ID and file scope, then commit and push that claim immediately. Never start a task
> another session has claimed. Keep scopes non-overlapping. If a task requires changing a file
> owned by another session, log the request here instead of editing it. Make small, frequent
> commits; run `git pull --rebase` before every push. When a task is finished, record sources,
> verification, and irregularities, then mark it done. Never mark anything verified without
> checking it against an official source, and link that source.

## Sessions

| Session ID | Branch | Scope (files) | Status |
|---|---|---|---|
| 1427c27a | `arena/1427c27a-freetime2` | `COORDINATION.md`, `README.md`, `index.html`, `calendar.html`, `mlb.html`, `nfl.html`, `ncaaf.html`, `radio.html`, `methodology.html`, `flagged.html`, `assets/*`, `data/*`, `.nojekyll` | **active — sole session; claimed all tasks below** |

## Task board

| # | Task | Status | Owner | Files touched | Sources / verification | Irregularities |
|---|---|---|---|---|---|---|
| 1 | Research official 2026 schedules (MLB, NFL, Stanford, Cal, Westwood One, KNBR) | done | 1427c27a | `assets/data.js`, `data/schedules.json`, `methodology.html` | MLB.com press releases (2026 schedule Aug 26 2025; spring training Jan 21 2026; All-Star page; World Series FAQ); media.nfl.com 2026 schedule (May 14 2026); 49ers.com schedule; gostanford.com 2026 schedule; calbears.com 2026 schedule; westwoodonesports.com NFL schedule; thesportsleader.com KNBR schedules; mlb.com Giants/Athletics broadcast partners | See Flagged for Review page |
| 2 | Research 2027–2029 status (released vs. estimated) | done | 1427c27a | `assets/data.js`, `flagged.html` | MLB 2027 announced Jul 16 2026 (mlb.com press releases); MLB 2028/2029 not announced (mlbschedule.net status check Oct 2026; MLB 2029 154-game plan is a bargaining proposal only, AP Oct 8 2026); NFL 2027 not released (status check Nov 24 2026; May 2027 projected) | 2028/2029 all ESTIMATED |
| 3 | Research game durations + halftimes | done | 1427c27a | `methodology.html`, `assets/data.js` | MLB 2:38 avg 2025 (MLB pace-of-play report via Lines.com); NFL 3:12 avg; NCAAF 3:27 avg 2024 FBS; NFL halftime 12 min; NCAA halftime 20 min | User estimates (150/180) updated to verified averages |
| 4 | Build GitHub Pages site (landing + subpages, tables, calendar scoreboard) | in progress | 1427c27a | `*.html`, `assets/*` | All rows carry official source links; unverified left blank + flagged | — |
| 5 | Vacation-window analysis 2027–2029 (1/2/3-week free windows) | in progress | 1427c27a | `index.html`, `calendar.html` | Derived from verified season windows; estimates labeled | Spring-training treatment documented |
| 6 | Final integration: re-verify, check links/build, enable Pages, PR to main, merge | pending | 1427c27a | all | — | — |

## Handoff / conflict log

- 2026-11-25 — Session 1427c27a created this board and claimed all tasks (sole session).
  No other sessions active. No conflicts.
