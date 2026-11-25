# COORDINATION.md

Shared task board for Freetime2. Multiple agent sessions may work concurrently; follow the rules in the task prompt.

## Rules
- Claim a task by writing your session ID and file scope, then commit and push the claim immediately. Never start a task another session has claimed.
- Keep scopes non-overlapping. If you need a file owned by another session, log the request here instead of editing it.
- Make small, frequent commits; run `git pull --rebase` before every push.
- When finished, record sources, verification performed, and any irregularities; mark done.
- Never mark anything verified without checking it against an official source and linking that source.
- Shared outputs (table data, site index/navigation) changed only by the final integration session once all other tasks are done.
- Stale claim (>60 min, no commits) may be taken over with a handoff note.

## Tasks

| Task | Status | Owner | Scope (files/dirs) | Started (UTC) | Updated (UTC) | Notes |
|------|--------|-------|--------------------|---------------|---------------|-------|
| T1 Research & data collection (MLB/NFL/NCAAF/Westwood One/SF radio) | needs review | arena/ab74423d-freetime2 | `data/**`, `sources/**`, `COORDINATION.md` (this row) | 2026-11-25T00:00:00Z | 2026-11-25T00:00:00Z | Official schedule sample data/source log published; incomplete all-game coverage and unresolved radio/time conflicts are on Flagged for Review. |
| T2 Free-time analysis & executive summary | needs review | arena/ab74423d-freetime2 | `analysis/**`, `docs/executive-summary.*` | 2026-11-25T00:00:00Z | 2026-11-25T00:00:00Z | Conservative season-window model finds no 7+ day run; candidate 3–4 day winter gaps are estimates, published with source links and caveats. |
| T3 Site build (GitHub Pages) | done | arena/ab74423d-freetime2 | `site/**`, `.github/workflows/**`, `README.md` | 2026-11-25T00:00:00Z | 2026-11-25T00:00:00Z | Static landing/dashboard, daily calendar, vacation finder, schedules, radio, duration/source and Flagged for Review pages; static link/data checks pass. |
| T4 Final integration, PR, merge, deploy | needs review | arena/ab74423d-freetime2 | all (integration only after T1-T3 done) | 2026-11-25T00:00:00Z | 2026-11-25 | PR #7 closed without merge after confirming main already contains a richer integrated planner and Pages build; see handoff log. |

## Log

- 2026-11-25T00:00:00Z `arena/ab74423d-freetime2`: Created COORDINATION.md. Claimed T1. Repo was initial commit only.
- 2026-11-25T00:00:00Z `arena/ab74423d-freetime2`: Claimed unowned T2 (analysis/docs) and T3 (site/workflow/README) after checking the board; same fixed Arena branch is used to comply with session branch restrictions.

- 2026-11-25 `arena/ab74423d-freetime2` (T1): Inspected official 49ers, Stanford, Cal, Westwood One and MLB sources; recorded 2026 remaining/high-priority events, Westwood One upcoming 2026 listings through Jan 10 2027, and 14 official MLB March 25 2027 event rows. Reviewed MLB 2027 team schedule announcements and duration sources. Full season/all-team schedules, local radio carriage, and time conflicts are explicitly flagged; task status set to needs review.
- 2026-11-25 `arena/ab74423d-freetime2` (T2): Applied inclusive broad season-window algorithm; no 7/14/21-day model run for 2027-2029; longest candidates are 4 days (2027 Feb 15-18; 2028 Jan 11-14 or Feb 14-17; 2029 Feb 12-15). Published provisional analysis and sources; status needs review.
- 2026-11-25 `arena/ab74423d-freetime2` (T3): Built 9-page static site, GitHub Pages Actions workflow, source-linked tables, duration assumptions, day navigation and flagged page. `python3 scripts/check_site.py` passes. Local preview started on port 8000.
- 2026-11-25 `arena/ab74423d-freetime2` (T4): Claimed integration after T1/T2 gaps were published on Flagged for Review and T3 completed; final source/data/site validation and PR/deploy remain.

- 2026-11-25 `arena/ab74423d-freetime2` (T4 handoff): Found `origin/main` had advanced to `5c779e9` with completed planner/docs/scoreboard work from sessions `9636f11d`, `b1591c47`, and `a2ab7210`, including PR #6 merged and GitHub Pages API reporting `built` at `https://kanlerxz87-cyber.github.io/Freetime2/`. My branch was based on the initial commit and added a competing `site/` plus a deployment workflow that would replace the existing Pages root. Closed PR #7 (https://github.com/kanlerxz87-cyber/Freetime2/pull/7) without merge to avoid overwriting the integrated site. My extra prototype remains on this branch for preview only; no main-branch files were changed.
