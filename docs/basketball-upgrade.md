# Basketball ingestion upgrade

This fork's maintained ingestion paths are NCAA men's basketball (`ncaab` in
Python) and NBA. Python 3.12 with numpy 1.26.4 and pandas 2.2.2 is the tested
application baseline. Package installation requires Python 3.10 or newer.

## Overtime counts

Both `sportsipy.nba.boxscore.Boxscore` and
`sportsipy.ncaab.boxscore.Boxscore` expose `overtimes` and append an `overtimes`
column to `dataframe`. Existing column names and the boxscore URI index remain
unchanged. Values are:

- `0`: a complete regulation line score.
- A positive integer: the number of overtime periods played.
- `None` (a null in dataframe/SQL ingestion): the period count is unknown.

The parser uses the line score already in the boxscore response, including
tables inside HTML comments. It recognizes `OT`, `1OT`, `2OT`, `OT1`, `OT2`,
and subsequent numbered periods, and checks matching period sequences and score totals for both
teams. Missing or malformed line scores do not silently become zero overtime.
Period scores remain available through `summary`; overtime parsing adds no
requests. NCAA schedule `Game.overtimes` retains its existing behavior.

```python
from sportsipy.nba.boxscore import Boxscore

game = Boxscore('202611070GSW')
assert game.overtimes == 1
print(game.dataframe[['home_points', 'away_points', 'overtimes']])
```

## Fetching and caching

Cloudscraper is retained. Sessions and cookies are reused within each thread,
and recreated after a process fork. All calls through the shared fetch helper,
including URL-existence checks, share a filesystem lock and cooldown. The next
request waits at least 10 seconds after the previous attempt finishes. NBA and
NCAA requests share the same limiter, even in separate subprocesses. Timeouts
and failed HTTP responses also preserve the cooldown.

HTTP 429 and selected transient server errors, timeouts, and connection errors
receive at most two retries by default. `Retry-After` seconds and HTTP dates are
honored. Exhausted failures propagate so ingestion can retry the job; HTTP 404
still indicates a missing page. A rate limit or server error is not treated as
a nonexistent season. Recognized HTTP-200 challenge pages are rejected.

Successful HTML is cached in memory for 60 seconds, with a maximum of 128 URLs
per process. Each consumer receives a fresh PyQuery tree. This avoids a second
GET after a URL check and can reuse repeated schedule downloads within a job.
There is no persistent response cache; restarting a job always starts fresh.

| Environment variable | Default | Meaning |
| --- | --- | --- |
| `SPORTSIPY_REQUEST_INTERVAL` | `10` | Minimum cooldown in seconds; values below 10 do not reduce it. |
| `SPORTSIPY_REQUEST_TIMEOUT` | `30` | Requests timeout in seconds for connection/read operations. |
| `SPORTSIPY_REQUEST_RETRIES` | `2` | Additional attempts after a transient failure. |
| `SPORTSIPY_CACHE_TTL` | `60` | In-memory cache lifetime in seconds; `0` disables reuse. |
| `SPORTSIPY_RATE_LIMIT_DIR` | `<system temp>/sportsipy-rate-limit` | Directory for shared lock and cooldown state. |

The default directory coordinates subprocesses in one container or host using
the same temporary directory. Separate containers need the same mounted lock
directory and configuration to coordinate. Separate machines and calls made
directly by the application outside sportsipy are not coordinated. Do not
delete the lock directory while workers are active.

## Application migration instructions

No changes to `yaherewego` or its database are made by this repository. Prepare
and apply an additive database migration **before deploying the new library**:

```sql
BEGIN;
ALTER TABLE nba.games ADD COLUMN IF NOT EXISTS overtimes INTEGER;
ALTER TABLE ncaam.games ADD COLUMN IF NOT EXISTS overtimes INTEGER;
COMMIT;
```

Keep these columns nullable, without a zero default: old records have unknown
counts until backfilled. If the application's migration system already defines
either column, verify its type and nullability rather than assuming
`IF NOT EXISTS` validates them.

Add `overtimes = Column(Integer, nullable=True)` to both application game models,
with the appropriate SQLAlchemy import, and include it in any explicit response
schema or field selection where it should be exposed. The current ingestion
passes dataframe columns through to SQL, so it needs no dataframe renaming.
Its existing `save_games` deletes matching IDs before appending; deploying the
dataframe column before the database migration could make that append fail
after deletion. Deploy the migration first and verify the schema.

Then rebuild the application's data image with this version of the fork (pin
the reviewed commit for repeatable builds). Validate a regulation game and both
known overtime examples before running the full season update:

| League | Boxscore URI | Expected overtimes |
| --- | --- | --- |
| NBA | `202611070GSW` | 1 |
| NCAA men's | `2026-11-06-00-purdue` | 2 |

The existing incremental update starts from the most recent stored game, so it
does not automatically revisit the entire season. Use an explicit season date
range in your planned application backfill, then resume normal updates. You
can set `SPORTSIPY_CACHE_TTL=0` for a fully fresh run; the default short cache
does not survive a prior job. Do not replace unknown counts with zero.

```sql
SELECT id, overtimes FROM nba.games WHERE id = '202611070GSW';
SELECT id, overtimes FROM ncaam.games
WHERE id = '2026-11-06-00-purdue';
```

## Offline validation

```sh
python -m pip install -r requirements-dev.txt
python -m tests.run_basketball -q
```

The push workflow runs the basketball/shared regression suite with saved HTML
and blocks network access. A real two-process test checks the shared 10-second
cooldown using simulated responses. Live exhaustive checks are manual only.
The preexisting fork behavior of zeroed NCAA boxscore records and null NBA
dataframe abbreviation fields is preserved; the application already resolves
NBA abbreviations from daily game listings.
