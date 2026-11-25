# Free Time Vacation

**Bay Area over-the-air sports radio, 2026–2029: when is the dial empty?**

Live site: **https://kanlerxz87-cyber.github.io/Freetime2/**

This project maps every MLB game (all 30 clubs — spring training, regular season, All-Star, postseason), every NFL game (preseason, regular season, playoffs, Pro Bowl, Super Bowl), Stanford/Cal NCAAF, and every Westwood One national NFL radio broadcast — day by day, 2026 through 2029 — and computes the days with **zero** live games on San Francisco AM/FM radio.

## Straight answer

There is **no 2–3-week fully-free vacation window** in 2026, 2027, 2028 or 2029. The only strict gaps are the February islands between the Super Bowl and MLB Spring Training (4–11 days, 2026 boundaries verified; future years estimated). The best practical (Bay Area/national-only) break is the **January → mid-February lull, ~40 days** each year (e.g., **Jan 11 → Feb 19, 2027**).

## How to use

- **[Executive Summary](https://kanlerxz87-cyber.github.io/Freetime2/docs/executive-summary.html)** — the answer, windows ranked, free days by month.
- **[Scoreboard Calendar](https://kanlerxz87-cyber.github.io/Freetime2/docs/calendar.html)** — pick any day 2026–2029 (prev/today/next + month grid); PT busy blocks, free-time ranges, every game that day.
- **[MLB tables](https://kanlerxz87-cyber.github.io/Freetime2/docs/mlb.html)** · **[NFL](https://kanlerxz87-cyber.github.io/Freetime2/docs/nfl.html)** · **[NCAAF](https://kanlerxz87-cyber.github.io/Freetime2/docs/ncaaf.html)** · **[Westwood One](https://kanlerxz87-cyber.github.io/Freetime2/docs/westwood.html)** · **[AM/FM 94122 dial audit](https://kanlerxz87-cyber.github.io/Freetime2/docs/radio.html)**
- **[Vacation Windows](https://kanlerxz87-cyber.github.io/Freetime2/docs/windows.html)** · **[Sources](https://kanlerxz87-cyber.github.io/Freetime2/docs/sources.html)** · **[Methodology](https://kanlerxz87-cyber.github.io/Freetime2/docs/methodology.html)** · **[VERIFIED 2026 tables](https://kanlerxz87-cyber.github.io/Freetime2/docs/schedules.html)**
- **[Flagged for Review](https://kanlerxz87-cyber.github.io/Freetime2/docs/flagged.html)** — every estimated/TBD/irregular row, consolidated. **Read it before booking anything.**

## Honesty rules

- **VERIFIED** = row traced to an official source (link in-row or on the Sources page).
- **ESTIMATED** = deterministic reconstruction anchored to verified season boundaries. 2026/2027 MLB game-level rows are ESTIMATED (official master schedules exist but could not be machine-imported in the build environment); **all 2028/2029 rows are ESTIMATED** because those schedules are not released.
- **TBD** = unpublished; deliberately never filled in.
- See [VERIFICATION.md](./VERIFICATION.md) for the line-by-line log and [COORDINATION.md](./COORDINATION.md) for the task board.

## Reproduce / develop

```bash
python3 tools/generate_schedules.py   # regenerates data/games-*.json + vacation_analysis.json + meta.json (deterministic)
python3 -m http.server 8000           # then open http://127.0.0.1:8000/
```

No build step; static site. Pages source: repository root of `main`.

## Key caveats

- Durations: MLB ~158 min, NFL ~183 min, NCAAF ~207 min (researched averages — see Sources).
- March → October: a game airs nearly every day — "free" means before first pitch / between / after last out, per-day only.
- Westwood One national windows are a subset of NFL dates; KNBR pre-emption by 49ers local rights is assumed but not programmatically verified.
- Times are Pacific (America/Los_Angeles); “PST” in the UI means PT.
