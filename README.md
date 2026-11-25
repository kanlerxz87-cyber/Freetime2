# Free Time Vacation Planner

A static GitHub Pages site (`docs/`) that shows when a Bay Area sports fan is free: which MLB, NFL and college games are on, and which Pacific-time blocks are free.

**Live site:** https://kanlerxz87-cyber.github.io/Freetime2/

## Pages

| Page | What it shows |
|---|---|
| `index.html` | Executive summary, verified facts, what is not verified, and live MLB runs with no Giants/Athletics games |
| `schedule.html` | Daily scoreboard with yesterday / today / tomorrow buttons, timeline and free-time blocks |
| `mlb.html` | All 30 MLB clubs (Giants and Athletics flagged high priority) |
| `nfl.html` | Westwood One national NFL radio slate and 49ers 2026 games |
| `ncaaf.html` | Stanford and Cal 2026 games and results |
| `radio.html` | Where games air, with verified and unverified station facts |
| `research.html` | Game-length averages, verification method and source list |
| `flagged.html` | Flagged for Review: conflicts and open items, with source links |

## Data

- `docs/data/snapshot.json`: hand-verified rows, each with `source_url`, plus the 13 flags (`irregularities`).
- `docs/data/mlb-teams.json`: the 30 MLB clubs from the MLB Stats API.
- MLB games are loaded live in the browser from `statsapi.mlb.com` (official MLB Stats API).

Nothing is inferred. A value that could not be confirmed from an official source is blank or labelled UNVERIFIED. Times are Pacific.

## Build check

```sh
node scripts/check-links.mjs
```

The check fails if any internal link is broken, any JSON or JS file does not parse, or any data row lacks an https source link.

## Coordination

Parallel sessions coordinate on `COORDINATION.md`. Read it before starting work.
