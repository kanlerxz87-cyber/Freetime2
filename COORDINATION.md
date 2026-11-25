# Coordination board

| Task | Status | Session | Scope |
|---|---|---|---|
| Starter dashboard and sample source checks | needs review | dffc2cac | index.html, assets/, README.md, COORDINATION.md |
| Complete 2026–29 MLB, NFL, college and other radio game inventory and availability analysis | unclaimed | — | Future data/ingestion files; coordinate integration |
| Full line-by-line integration verification, link checks and Pages publication | unclaimed | — | Shared outputs; after inventory is complete |

## Session log
- 2026-11-25: Repository was initially empty apart from README. Claimed integration on Arena-assigned branch; remote branch did not yet exist, so rebased against origin/main before creating it.
- Created a static, explicitly incomplete dashboard, not a verified free-time calendar. Sample entries were individually checked against [49ers 2026 schedule](https://www.49ers.com/schedule/2026/), [Athletics spring training](https://www.mlb.com/athletics/tickets/spring-training), [Athletics tickets](https://www.mlb.com/athletics/tickets), [Giants tickets](https://www.mlb.com/giants/tickets/single-game-tickets), [Dodgers 2027 announcement](https://www.mlb.com/press-release/dodgers-announce-2027-schedule), and [2027 All-Star Game](https://www.mlb.com/cubs/fans/all-star-game). Arizona February MT was converted to Pacific standard time. TBD fields remain blank; duration is an explicit assumption.
- [Westwood One affiliate finder](https://www.westwoodonesports.com/station-finder/) warns that blackouts and conflicts mean affiliates may not air every broadcast. Reception in 94122 and per-game local carriage are not verified. The network schedule's listed times may represent radio coverage rather than kickoff, so no kickoff was inferred.
- The requested exhaustive game collection, other sports, future years, automatic updates, reliable free-window analysis, complete link verification, PR and deployment are not complete. All such gaps are flagged on the site. A sample cannot establish 7-, 14-, or 21-day vacation windows. No claim of full verification or publication is made.
