# Vacation-window findings (model, not a booking guarantee)

As of 2026-11-25, the strict model treats every NFL regular-season/playoff date, every MLB spring-training/regular/postseason range, and Stanford/Cal football regular/bowl ranges as a caution period. That is deliberately conservative: the complete schedule-by-schedule dataset is not collected, and the season windows after 2026 are estimates.

| Year | Longest modeled candidate gap | 7-day / 14-day / 21-day candidate? | Confidence |
|---|---|---|---|
| 2027 | Feb 15–18, 4 days | No / No / No | Estimated. NFL 2026–27 postseason and 2027 MLB spring training boundaries are not fully verified. |
| 2028 | Jan 11–14, 4 days; Feb 14–17, 4 days | No / No / No | Estimated. NFL 2027–28 postseason, NCAAF bowl range and 2028 MLB spring training dates are estimates. |
| 2029 | Feb 12–15, 4 days; Jan 10–12, 3 days | No / No / No | Estimated. 2028–29 postseason, college bowls and 2029 MLB preseason dates are estimates. |

**Practical conclusion:** Current model does not identify any 1-, 2- or 3-week fully-clear vacation in 2027–2029. Its best candidates are short 3–4 day winter gaps. Do not book these as confirmed free: the ranges are constructed from broad season estimates, local AM/FM carriage has not been exhaustively matched, and other live sports may be broadcast locally.

## Computation

For each date, the model checks if it is within any MLB/NFL/NCAAF season window, or has a known specific event. A run is a consecutive series of dates outside all those windows and events. Windows are inclusive. The model does not infer individual game times; date-level candidate runs are not the same as verified minute-level availability.

## Schedule coverage boundary

The event file includes a sample of the official MLB March 25, 2027 schedule (14 rows), selected forthcoming 2026 team-football events, 2026 Stanford/Cal last regular-season games, and the upcoming Westwood One schedule visible through Jan 10, 2027. It does **not** contain every game for all MLB clubs or all NFL games. This gap is posted on the site’s Flagged for Review page.
