# Verification log (accessed 2026-11-25)

## Official schedule sources opened

- 49ers 2026 schedule: <https://www.49ers.com/schedule/>. Reviewed official schedule page chunks 0-2 for regular season through Week 18 and preseason. The page includes station affiliates in schedule entries; Week 18 date/time remains TBD. Kickoff-time conflicts with Westwood One were found for Weeks 15 and 17; those times are blanked/TBD in the dataset.
- Stanford 2026 schedule: <https://gostanford.com/sports/football/schedule>. Reviewed schedule page chunks 1-3. Nov 28 vs SMU is listed for 12:30 PM PST. The site also exposes previous 2025 rows; those were not mixed into 2026 schedule data.
- Cal 2026 schedule: <https://calbears.com/sports/football/schedule>. Reviewed schedule page chunk 0. Nov 28 vs Pittsburgh is listed for 4:30 PM; current local AM/FM carriage is not established by this page.
- Westwood One NFL schedule: <https://www.westwoodonesports.com/nfl-schedule/>. Reviewed chunks 0-1. Captured the displayed upcoming broadcasts through Jan 10, 2027 in event rows. Listings use ET; published exact times were converted to PST by subtracting three hours where dates fall in standard time. Local SF affiliate carriage is a separate, unresolved question.
- MLB official schedule pages: <https://www.mlb.com/schedule/2027-03-25> was opened; the March 25 schedule rows were transcribed (14 matchups), including listed ET start times and TBD starts. <https://www.mlb.com/schedule/2027-02-19/2027-03> displays Spring Training games Feb 19, 2027. This does not constitute a full-season extraction.
- MLB 2027 club announcements: <https://www.mlb.com/press-release/washington-nationals-announce-2027-schedule> and <https://www.mlb.com/press-release/press-release-orioles-announce-2027-regular-season-schedule>. These confirm schedules for those individual clubs, not a complete all-30-club game dataset. The broad MLB 2027 range is therefore marked estimated in the site.

## Duration research

See `analysis/duration-assumptions.md`; MLB 2:38 is from an official MLB report. NFL elapsed game duration and FBS game duration rely on secondary analyses/reports and are explicitly marked estimates. The site uses 158 minutes for MLB, 184 minutes for NFL, and 207 minutes for NCAA FBS as average-duration estimates.

## Known irregularities / non-verification

- 49ers Week 15 and Week 17 times conflict between official 49ers schedule and Westwood One listing; exact kickoff fields are blank/TBD.
- The 2027 MLB master schedule was not exhaustively transcribed, and 2028–2029 are not complete official game schedules in this build.
- No 2027–2029 Stanford/Cal schedules have been verified; season windows are estimates.
- Other sports and station-by-station SF AM/FM schedules, actual reception in Outer Sunset 94122, and local network affiliates for each national broadcast have not been comprehensively verified.
- No individual game time is inferred when a source lists TBD. Calendar and vacation findings remain provisional.
