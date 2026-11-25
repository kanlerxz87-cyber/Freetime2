# Free Time Vacation

[Open the GitHub Pages planner](https://kanlerxz87-cyber.github.io/Freetime2/).

The planner shows vacation candidates, a 2026–2029 daily scoreboard in Pacific time, an AM/FM reference for San Francisco ZIP 94122, and a coverage audit. It does not certify game-free days. The strongest preliminary candidate is February 15–18, 2027, between the published Super Bowl and listed spring games. A full week is not verified.

The scoreboard reads MLB's official Stats API directly in the browser and keeps a sourced snapshot of selected football dates and Westwood One network listings. It separates confirmed starts from estimated ends and does not assume local radio carriage. Unverified times are blank; unknown starts and incomplete coverage are called out. See **Flagged for Review** before making travel decisions.

Run `node scripts/test.mjs` and `node --check docs/app.mjs` locally, then serve the repository root over HTTP to preview. No build dependencies are required.

## Supplementary verified-data pages (session b1591c47)

- `docs/index.html` — dashboard + source registry (official sources with links)
- `docs/executive-summary.html` — strict vs practical vacation windows
- `docs/windows.html` — 2026–2029 windows + busy blocks
- `docs/schedules.html` — 2026 49ers / Stanford / Cal tables (official sources)
- `docs/radio.html` — KNBR 680/104.5 + Westwood One 2026 slate
- `docs/methodology.html` — Day Planner (yesterday/tomorrow, PT free-time math)
- `docs/flagged.html` — Flagged for Review
- `data/sources.json`, `data/schedules_2026.json`, `data/windows_2026_2029.json` — structured data
- `VERIFICATION.md` — line-by-line verification log

Key caveat: 2027–2029 NFL/NCAAF/MLB game-by-game schedules were not released at build time; future blocks are ESTIMATED and must be re-verified. See `VERIFICATION.md`.

## Scoreboard site, verified snapshot (session a2ab7210)

A second, self-contained site lives in `scoreboard/` (served at [`/Freetime2/scoreboard/`](https://kanlerxz87-cyber.github.io/Freetime2/scoreboard/)):

- `scoreboard/index.html`: executive summary, verified facts and open items, live 2027 MLB runs with no Giants/Athletics game
- `scoreboard/schedule.html`: day-by-day scoreboard (yesterday / today / tomorrow) with PT timeline and free blocks; a day is never shown as FREE unless every category is covered
- `scoreboard/mlb.html`, `nfl.html`, `ncaaf.html`, `radio.html`, `research.html`, `flagged.html`
- `scoreboard/data/snapshot.json`: 76 hand-verified rows, each with a source link, and 13 flags
- Build check: `node scripts/check-links.mjs` (internal links, JSON/JS parse, every row has a source)

Coordination board: `COORDINATION.md`.
