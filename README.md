# Freetime2 — Bay Area Sports Radio Free-Time Planner

Planning tool for finding vacation windows in the San Francisco Bay Area (Outer Sunset, 94122) when no high-priority live sports are likely/known to be on AM/FM radio.

## Scope
High-priority conflicts (any of these on air = not free):
- **MLB**: San Francisco Giants, Oakland Athletics (flagged high priority); all 30 MLB clubs shown
- **NFL**: San Francisco 49ers preseason/regular/postseason (high priority); Westwood One Sports national NFL radio broadcasts
- **NCAAF**: Stanford Cardinal, California Golden Bears (high priority)

## What this repo contains
- `docs/` — GitHub Pages static site (executive summary, schedule/windows, radio sources, methodology, flagged-for-review)
- `data/sources.json` — source registry with official URLs and verification status
- `data/windows_2026_2029.json` — structured vacation-window analysis (verified where published, estimated where not)
- `VERIFICATION.md` — line-by-line verification log and irregularities
- `COORDINATION.md` — shared task board for parallel agent sessions

## Key caveats
- **2026**: Partial official schedules exist (MLB season schedule published; NFL/49ers schedule published; Stanford/Cal 2026 schedules published; Westwood One NFL schedule shows selected national games). Game times/TBD items are flagged.
- **2027 MLB**: MLB clubs announced 2027 regular-season schedules (official press releases, e.g. Opening Day Mar 25 2027). Full game-by-game/team-by-team details require per-team/MLB schedule pages; this repo records verified season boundaries and flags game-level details as needing per-game source verification.
- **2027-2029 NFL, NCAAF, MLB (beyond published structure)**: **No official game-by-game schedules released at build time.** Windows for these years are **ESTIMATES** based on official league season-structure patterns and historical calendar norms. They are explicitly labeled `ESTIMATED` and must not be treated as confirmed conflict-free periods.

## Official sources (primary)
See `data/sources.json` and the site "Sources / Methodology" page for full citations.

## GitHub Pages
Site is served from `docs/` (configure Pages to deploy from `main` / `docs`).
