# PostgreSQL Reference (v18)

PG-specific mechanics; shared material lives in the other files. Assumes PostgreSQL 18; items
needing older floors are flagged.

## What v18 gives you (use these instead of workarounds)

- **`uuidv7()`** native — time-ordered UUID PKs with no extension and no B-tree fragmentation;
  `uuid_extract_timestamp()` to read the embedded time. Default choice for new PKs.
- **Async I/O subsystem** (`io_method = worker` default) — faster seq scans/vacuum on capable
  storage; an ops tunable, not a schema concern.
- **Virtual generated columns are the default** — `GENERATED ALWAYS AS (expr)` computes on
  read; write `STORED` explicitly when you need to index the value (or index the expression
  directly).
- **`RETURNING old.* / new.*`** — both sides of an UPDATE/DELETE/MERGE in one statement;
  audit/diff logic without a trigger.
- Temporal constraints (`WITHOUT OVERLAPS` on PKs/uniques over ranges) — bookings/validity
  windows enforced in-schema.
- Plus the recent-versions baseline you should already be on: `MERGE` (15+, `RETURNING` in
  17+), `JSON_TABLE` (17+), SQL/JSON constructors & `jsonpath`, incremental sorts, parallel
  queries.

## JSONB

- `jsonb` always (never `json` — it's just text). Operators: `->` (json), `->>` (text),
  `#>>` (path text), `@>` containment, `?` key exists, `jsonb_set` for updates.
- Index by access pattern: GIN on the column for containment queries
  (`settings @> '{"beta": true}'`); a B-tree **expression index** for one hot key
  (`(settings ->> 'timezone')`); `jsonb_path_ops` GIN when only `@>` is used (smaller/faster).
- `JSON_TABLE` to flatten arrays into rows for joins/aggregation.
- Discipline: JSONB is for open-shape data; a JSONB key that gains a CHECK, an index, and a
  WHERE clause wants to be a column (`schema-design.md`).

## Row-Level Security (RLS)

```sql
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON invoices
  USING (organization_id = current_setting('app.org_id')::uuid);
```

App sets `SET LOCAL app.org_id = '...'` per transaction. Notes: table owners and `BYPASSRLS`
roles skip policies (connect as a non-owner app role); `FORCE ROW LEVEL SECURITY` to bind the
owner too; RLS is a backstop for service-layer scoping, not a replacement — and policies cost
per-row evaluation, so keep the predicate trivial and indexed.

## Identity, sequences, defaults

`GENERATED ALWAYS AS IDENTITY` over `serial` (real constraint semantics, no implicit sequence
grants). Sequences are non-transactional — gaps are normal, never "fix" them. Per-group
sequential numbers (invoice numbering per org) need a counter table row locked
`FOR UPDATE`, not a sequence.

## Transactions & isolation

- Default `READ COMMITTED`: each statement sees the latest committed data — read-modify-write
  needs `FOR UPDATE` or optimistic versioning (`query-patterns.md`).
- `REPEATABLE READ` for consistent multi-statement reads (reports); `SERIALIZABLE` where
  invariants span rows — then handle serialization failures (`40001`) with retry.
- Advisory locks (`pg_advisory_xact_lock(key)`) for app-level mutual exclusion (cron-ish jobs,
  per-entity critical sections) without a lock table.
- Long transactions are a systemic tax (vacuum can't clean, locks pile) — keep them short;
  never idle-in-transaction across external calls.

## Maintenance you must know exists

Autovacuum handles dead tuples/stats — watch for tables that outgrow its defaults (high-churn
queues: per-table `autovacuum_vacuum_scale_factor`). `ANALYZE` after bulk loads. Bloat from
mass UPDATE/DELETE is reclaimed by vacuum but the file doesn't shrink — chunk huge rewrites.
`pg_stat_statements` is the first stop for "what's slow in production".

## Ops surface (know where the knobs live)

Logical replication / publications for CDC-ish feeds; `pg_dump --schema=<name>` for per-schema
extraction; connection pooling is mandatory at scale (pgbouncer-class) — design queries to be
pool-friendly (no session state; `SET LOCAL` over `SET`).
