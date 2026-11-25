# VERIFICATION.md — Line-by-line verification log

Build date: 2026-11-25. Rule applied: every table row must trace to an official source; anything not confirmable is left blank/flagged as unverified; estimated future blocks are labeled ESTIMATED and never presented as confirmed.

## Verified (official primary source fetched/checked)
- 2026 MLB Opening Night Mar 25 (Giants vs Yankees), Opening Day Mar 26, Athletics Mar 27 — MLB.com news article (MLB-2026-OPENING).
- 2026 Spring Training begins Feb 20, 2026 — MLB.com press release (MLB-2026-SPRING).
- 2027 MLB Opening Day Mar 25, 2027; 2027 final series Sep 24-26, 2027 — MLB.com club press releases (Orioles, Brewers, Rays) (MLB-2027-*).
- 2026 49ers regular-season dates/opponents/times (Weeks 1-17) — 49ers.com/schedule/ (49ERS-2026). Week 8 bye confirmed.
- 2026 Stanford dates/opponents — gostanford.com/sports/football/schedule + Jan 26 2026 news release (STANFORD-2026*).
- 2026 Cal dates/opponents/times — calbears.com/sports/football/schedule/text + Jan 26 2026 news release (CAL-2026*).
- Westwood One 2026 NFL national radio slate (selected games incl. Thanksgiving/Christmas tripleheaders, TNF/MNF/SNF, TBA Week 16-18 slots) — westwoodonesports.com/nfl-schedule/ (WWO-NFL). Full season list is paginated; site links each event page.
- KNBR 680 AM / 104.5 FM San Francisco, Westwood One Sports affiliate, Giants/49ers radio home — thesportsleader.com (KNBR).
- 2026-27 CFP quarterfinals/semifinals + National Championship Jan 25, 2027 (Las Vegas) — collegefootballplayoff.com (CFP-2026-27).

## Partial / secondary (cross-checked, not primary)
- 2026 NFL league-wide kickoff Sep 9, 2026; Week 18 Jan 9-10, 2027; playoffs from Jan 16, 2027 — secondary summaries of NFL May 14, 2026 release (NFL-2026). Confirm on NFL.com / operations.nfl.com before citing as primary.
- Super Bowl dates LX Feb 8 2026 / LXI Feb 14 2027 / LXII Feb 13 2028 / LXIII Feb 11 2029 — Wikipedia upcoming-games table + secondary corroboration (SB-DATES). Confirm on NFL.com host-city announcements.
- 2026 MLB regular-season finale Sep 27, postseason Sep 29-Oct 31 — secondary summaries of MLB master/postseason schedules. Confirm on MLB.com.
- Average durations (MLB ~170 min; NFL ~192 min; NCAAF ~204 min; halftimes 12/20 min) — secondary research summaries (DUR-*). Used only for daily free-time estimates, clearly labeled as averages.

## Unverified / flagged (do NOT rely on)
- 49ers Week 18 2026 opponent/date/time (TBD at fetch time) — FLAGGED-UNVERIFIED.
- 49ers 2026 preseason dates/times (Aug 13/20/27) — secondary summary only; confirm on 49ers.com printable schedule.
- Stanford/Cal 2026 kickoff times marked TBA at announcement — later published on official schedule pages; check gostanford.com / calbears.com for final times.
- Pro Bowl Games 2026-2029 dates — not verified in this build; treat early-February as potentially busy until confirmed.
- All 2027-2029 NFL, NCAAF, and MLB (beyond 2027 Opening Day/final-series boundaries) game-by-game schedules — NOT RELEASED; site shows ESTIMATED season blocks only.
- Reference sites supplied by user (VacationSchedule, ScheduleFreeTime, RADIOSF) — not fetchable from this environment (connection failure); no data taken from them. Re-check manually via links in README/site.

## Irregularities for review
1. Super Bowl LXI date conflict: Feb 14, 2027 (Wikipedia table + most secondaries) vs Feb 15, 2027 (one secondary summary of NFL release). Site uses Feb 14 and flags the conflict. Resolve on NFL.com.
2. 2026 MLB postseason end depends on series lengths (World Series Game 7 if needed Oct 31). Site shows the full possible span as busy; actual end may be earlier.
3. Westwood One schedule page shows duplicate Upcoming/Past listings and TBA slots for Weeks 16-18; site records only named games as verified and flags TBA slots.
4. User-suggested durations (MLB 150 min, football 180 min) are shorter than researched averages; site uses researched averages and shows both for transparency.

## How to re-verify
Re-run the official URLs in data/sources.json; update data/*.json; re-run scripts/build_site.py; check site links; update this file. Never mark a row verified without an official-source link.
