# Overtime line-score fixtures

These table fragments were retrieved on November 8, 2026 using the existing
Cloudscraper helper and its 10-second delay. They retain the original header
and scoring-cell attributes and are wrapped in HTML comments to exercise the
normal boxscore retrieval path.

- `nba-overtime.html`: https://www.basketball-reference.com/boxscores/202611070GSW.html
  (one overtime; header `OT`, scoring-cell attribute `1OT`).
- `ncaam-overtime.html`: https://www.sports-reference.com/cbb/boxscores/2026-11-06-00-purdue.html
  (two overtimes; headers and scoring-cell attributes `OT`, `2OT`).

The dataframe tests insert these fragments into the existing complete boxscore
fixtures to check overtime parsing without adding network requests.
