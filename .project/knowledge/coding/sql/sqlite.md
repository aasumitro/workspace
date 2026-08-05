# SQLite Reference (v3)

SQLite-specific mechanics; shared material lives in the other files. Assumes 3.35+ (RETURNING,
DROP COLUMN); newer minimums flagged.

## The mental model

An embedded library, not a server: one file, in-process, zero network. Superb for local-first
apps, desktop tools (operator consoles, Electron/Wails apps), edge/mobile, tests, and modest
single-node services. The moment you need many concurrent *writers* across processes/machines,
you've outgrown it — that's PostgreSQL's job.

## Connection setup — non-negotiable pragmas

Every connection, first thing:

```sql
PRAGMA journal_mode = WAL;        -- readers don't block the writer (persistent, set once per db)
PRAGMA foreign_keys = ON;         -- FKs are OFF by default, per connection (!)
PRAGMA busy_timeout = 5000;       -- wait for the write lock instead of failing instantly
PRAGMA synchronous = NORMAL;      -- the right WAL-mode durability/speed tradeoff
```

Close cleanly and run `PRAGMA optimize;` on disconnect. One writer at a time is the law —
serialize writes in the app (a single writer connection/queue) rather than colliding on
`SQLITE_BUSY`.

## STRICT tables — use them (3.37+)

```sql
CREATE TABLE invoices (
  id          TEXT PRIMARY KEY,
  total_cents INTEGER NOT NULL,
  status      TEXT NOT NULL CHECK (status IN ('pending','paid','void')),
  created_at  INTEGER NOT NULL
) STRICT;
```

Without `STRICT`, SQLite's type *affinity* lets `'abc'` into an INTEGER column. STRICT gives
real type enforcement (INTEGER, REAL, TEXT, BLOB, ANY). New tables: always STRICT. Legacy
tables: add CHECKs (`typeof(x) = 'integer'`) where it matters.

## Types under affinity (legacy tables) & representations

- No native BOOLEAN (INTEGER 0/1 + CHECK), no native DATETIME — store **one** of: INTEGER epoch
  (`unixepoch()`, best for math/indexes) or ISO-8601 TEXT (readable, sorts correctly). Pick
  per project; never mix.
- Money: INTEGER minor units. `REAL` is IEEE float — same money rules as everywhere.
- UUIDs: TEXT (readable) or 16-byte BLOB (compact) — generated in the app; be consistent.

## JSON (3.38+ core; JSONB storage 3.45+)

`json_extract(col, '$.key')` / `->`/`->>` operators, `json_set`, `json_each` to explode arrays
into rows. Validate with `CHECK (json_valid(col))`. Index hot keys via expression indexes
(`indexing.md`). `jsonb_*` function variants (3.45+) store/operate on the binary form —
faster repeated access.

## Concurrency reality

- WAL mode: many readers + exactly one writer concurrently; readers see a stable snapshot.
- Transactions that will write should start `BEGIN IMMEDIATE` — grabbing the write lock up
  front avoids mid-transaction upgrade deadlocks (`SQLITE_BUSY` after doing work).
- Keep write transactions tiny; batch inserts inside one transaction (per-statement autocommit
  is the classic 100x slowdown).
- Backups of a live WAL db: `VACUUM INTO 'backup.db'` or the online backup API — never file-copy
  a database mid-write.

## Features you might not expect (use them)

`RETURNING` (3.35+) · `UPDATE ... FROM` (3.33+) · window functions · CTEs/recursive ·
partial + expression indexes · generated columns (3.31+) · `UPSERT` · full-text search
(**FTS5** virtual tables — the answer to "add search" before reaching for a search server) ·
`WITHOUT ROWID` tables · `ATTACH` for multi-file setups · strict `PRAGMA integrity_check` for
health checks.

## Testing & tooling

`:memory:` databases for fast isolated tests (or a `tmp` file per test for WAL fidelity);
`.dump`/`.schema` in the CLI for inspection; `EXPLAIN QUERY PLAN` before shipping any hot
query. Schema versioning via your migration tool or `PRAGMA user_version`
(`migrations.md` covers the rebuild dance for real ALTERs).
