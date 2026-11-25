# Freetime2 — Bay Area live-sports radio vacation planner

A static GitHub Pages dashboard for reviewing Bay Area AM/FM live-sports conflicts and possible vacation windows. The project focuses on all MLB clubs (Giants and Athletics high priority), all NFL with the 49ers high priority, Stanford and California football, and Westwood One's nationally listed NFL radio broadcasts.

## Pages

- Dashboard: `site/index.html`
- Executive summary: `site/executive-summary.html`
- Daily calendar / scoreboard: `site/calendar.html` (yesterday/tomorrow navigation)
- Vacation window finder: `site/vacation.html`
- Collected events and season windows: `site/schedule.html`
- SF radio and Westwood One: `site/radio.html`
- Sources and flagged items: `site/sources.html`, `site/flagged.html`

## Status and limitations

The site intentionally separates **verified**, **TBD**, and **estimated** data. It is an initial, incomplete research build, not a booking-grade guarantee: all 2027–2029 game rows are not collected, 2028–2029 schedules are largely unreleased, exact local station carriage has not been confirmed for every event, and candidate vacation ranges inherit broad season-window estimates. See the published Flagged for Review page before relying on any date.

Elapsed-time defaults: MLB 2:38 (2025 official MLB regular-season average), NFL 3:04 (secondary play-by-play average, with NFL rules linked), and NCAA FBS 3:27 (2024 secondary report). These are averages, not guaranteed end times. Details and citations: `analysis/duration-assumptions.md`.

## Local preview

Open `site/index.html` or run a static web server from the repository root:

```sh
python3 -m http.server 8000 --directory site
```

## Existing project deployment

The repository already has an integrated GitHub Pages planner on `main` at <https://kanlerxz87-cyber.github.io/Freetime2/>. This branch is based on an earlier commit; the separate `site/` prototype is not the Pages deployment source and should not replace the existing root/docs/scoreboard sites.
