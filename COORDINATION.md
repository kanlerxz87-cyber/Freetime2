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
| T1 Research & data collection (MLB/NFL/NCAAF/Westwood One/SF radio) | in progress | arena/ab74423d-freetime2 | `data/**`, `sources/**`, `COORDINATION.md` (this row) | 2026-11-25T00:00:00Z | 2026-11-25T00:00:00Z | Collect official/verified schedules 2026-2029; flag estimates where no official schedule exists. |
| T2 Free-time analysis & executive summary | in progress | arena/ab74423d-freetime2 | `analysis/**`, `docs/executive-summary.*` | 2026-11-25T00:00:00Z | 2026-11-25T00:00:00Z | Analysis uses broad, explicitly estimated seasonal windows where full schedules are unavailable. |
| T3 Site build (GitHub Pages) | in progress | arena/ab74423d-freetime2 | `site/**`, `.github/workflows/**`, `README.md` | 2026-11-25T00:00:00Z | 2026-11-25T00:00:00Z | Landing page, dashboard, calendar, category subpages, source and flagged-review pages. |
| T4 Final integration, PR, merge, deploy | unclaimed | | all (integration only after T1-T3 done) | | | Merge, re-verify, PR to main, merge, confirm Pages deploy. |

## Log

- 2026-11-25T00:00:00Z `arena/ab74423d-freetime2`: Created COORDINATION.md. Claimed T1. Repo was initial commit only.
- 2026-11-25T00:00:00Z `arena/ab74423d-freetime2`: Claimed unowned T2 (analysis/docs) and T3 (site/workflow/README) after checking the board; same fixed Arena branch is used to comply with session branch restrictions.
