# COORDINATION.md — Freetime2 Shared Task Board

## Active Session & Scope

| Session ID | Branch | Status | Claimed Timestamp (UTC) | Scope (Files Owned) |
|---|---|---|---|---|
| `7d4f79aa` | `arena/7d4f79aa-freetime2` | `in progress` | 2026-11-25T13:45:00Z | `COORDINATION.md`, `README.md`, `docs/**`, `data/**`, `scripts/**`, `.github/workflows/**` |

> Note on parallel Arena branches: At startup, `main` (`a6bb998`) contained only `# Freetime2` in `README.md` and no `COORDINATION.md`. Other Arena evaluation branches (`arena/9636f11d-freetime2`, `arena/dffc2cac-freetime2`, `arena/1427c27a-freetime2`) were noted during branch fetch; before final PR & merge to `main`, this session will re-fetch `origin/main` and reconcile/preserve any merged upstream work without discarding other sessions' verified contributions.

## Task Board

| ID | Task | Status | Owner | Files Touched | Sources & Verification | Irregularities / Notes |
|---|---|---|---|---|---|---|
| T1 | Repo audit & coordination setup | done | `7d4f79aa` | `COORDINATION.md` | Checked `origin/main` (`a6bb998`), PRs, issues, branches | Repo started with 1-line `README.md`; prior reference sites on `buffedlizard55-lab` return 404 (logged for review) |
| T2 | Verify 2026–2029 MLB schedules (all 30 clubs, Giants & A's high priority, Spring Training, All-Star, Postseason, Special games) | in progress | `7d4f79aa` | `data/mlb.json`, `scripts/*` | Official `mlb.com` & `statsapi.mlb.com` | Pending full verification |
| T3 | Verify 2026–2029 NFL schedules (all NFL games, 49ers preseason/regular/postseason high priority, Pro Bowl/All-Star, Super Bowl) | in progress | `7d4f79aa` | `data/nfl.json`, `scripts/*` | Official `nfl.com`, `49ers.com`, `operations.nfl.com` | Pending full verification |
| T4 | Verify 2026–2029 Stanford & California (Cal) NCAAF schedules (high priority) | in progress | `7d4f79aa` | `data/ncaaf.json`, `scripts/*` | Official `gostanford.com`, `calbears.com`, `fbschedules.com` / ACC announcements | Pending full verification |
| T5 | Verify Westwood One Sports & SF Bay Area AM/FM Radio (Outer Sunset SF 94122: KNBR 680/104.5, KGMZ 95.7 The Game, KNEW 960, KSFO 810, KTCT 1050, KCBS 740/106.9, KGO, etc.) + other live radio sports | in progress | `7d4f79aa` | `data/radio.json`, `docs/radio.html` | Official `westwoodonesports.com`, `knbr.com`, `audacy.com/957thegame`, FCC/station schedules | Pending full verification |
| T6 | Verify average game durations & halftime lengths (MLB, NFL, NCAAF, NBA, NHL, MLS/USL) + PST minute-by-minute Free Time engine (Nov 2026 – Dec 2029) & 1/2/3-week Vacation Windows (2027, 2028, 2029) | unclaimed | `7d4f79aa` | `data/durations.json`, `data/vacation_windows.json`, `scripts/build_data.py` | Official league pace-of-play & rulebook sources | Pending |
| T7 | Build GitHub Pages Dashboard (`docs/` or root static site + workflow): Executive Summary, Interactive Daily Scoreboard & Calendar (Yesterday/Tomorrow PST minute-by-minute), Vacation Windows 2027–2029, Core Priority Section, MLB, NFL, NCAAF, SF Radio 94122, Flagged for Review | unclaimed | `7d4f79aa` | `docs/**`, `.github/workflows/pages.yml` | Line-by-line source links on every table row; unverified values blank & flagged | Pending |
| T8 | Final integration, link/build verification, PR to `main`, merge, confirm GitHub Pages live deployment | unclaimed | `7d4f79aa` | `COORDINATION.md`, `README.md` | `gh pr create`, `gh pr merge`, `gh api .../pages` | Pending |

## Log

- `2026-11-25T13:45:00Z` (`7d4f79aa`): Initialized `COORDINATION.md` on `arena/7d4f79aa-freetime2` and claimed initial verification tasks.
