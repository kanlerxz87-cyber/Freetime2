# Coordination

Read this board before work. Claim a non-overlapping file scope with session ID and timestamp; commit and push the claim. Do not edit another session's files; log requests here. Make small commits and pull --rebase before pushing. Resolve and record conflicts without discarding others' work. Claims idle for 60 minutes without a commit can be taken over with a handoff note. Record official sources, verification and irregularities, and publish needs-review items on the Flagged for Review page. Shared outputs belong to the integration session.

| Task | Status | Owner | Scope | Sources / verification / irregularities |
|---|---|---|---|---|
| Integration and research prototype | needs review | 1427c27a (claimed 2026-11-25) | README.md, COORDINATION.md, *.html, assets/*, .nojekyll | Source links appear alongside transcribed rows. Selected 49ers kickoffs checked against [49ers](https://www.49ers.com/schedule/), national on-air listings checked against [Westwood One](https://www.westwoodonesports.com/nfl-schedule/). Date, time, matchup and priority were checked for each of these transcribed rows. Westwood One local carriage is not verified. |
| Complete all MLB, NFL and college games; local radio survey; vacation windows | needs review | 1427c27a | same integration scope | Not complete. [MLB](https://www.mlb.com/schedule), [NFL](https://www.nfl.com/schedules/), [Stanford](https://gostanford.com/sports/football/schedule), [Cal](https://calbears.com/sports/football/schedule). No free days or 1/2/3-week windows verified. No fabricated fixtures. Duration references are nonofficial. See Flagged for Review. |
| Site validation / publishing | in progress | 1427c27a | same integration scope | Local static links and JS syntax checked; external links, automated visual tests, final Pages deployment need verification. |

## Handoff / conflict log

- 2026-11-25: Session 1427c27a claimed integration and all tasks. Current Arena branch is fixed; separate session-named branches cannot be created. No conflicts observed. Claim pushed in commit 597f66e.
- This is a deliberately incomplete research prototype, not a verified comprehensive schedule. Source changes and flex scheduling require periodic re-verification.
