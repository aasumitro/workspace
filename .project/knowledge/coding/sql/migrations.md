# Migrations Reference

Applies to both engines; PG-only and SQLite-only mechanics are flagged. Use the project's
migration tool and numbering convention — this doc is the safety rules that hold regardless of
tool.

## Ground rules

- One migration = one up/down pair; the down path **actually reverses** — test both directions
  locally before review.
- Never edit a migration that has run in production/shared environments — append a new one.
  (Dev-phase edit-in-place is allowed only if the project's convention explicitly says so.)
- Schema migrations and data migrations are separate files — different risk, different
  rollback, different runtime.
- Data migrations: idempotent (safe on re-run), chunked when large, never destructive without
  an explicit plan step and human sign-off.
- Every migration runs inside a transaction where the engine allows it. PG: most DDL is
  transactional (the good news); the exceptions below are exactly the dangerous ones. SQLite:
  wrap the batch in a transaction yourself.

## Expand → migrate → contract (zero-downtime shape changes)

Never break running code with its own database. Three deploys, not one:

1. **Expand** — add the new column/table (nullable or defaulted); code writes both old and new.
2. **Migrate** — backfill in chunks; verify counts; switch reads to the new shape.
3. **Contract** — a later migration drops the old column, after no code references it.

Renames are a special case of this (add new → dual-write → backfill → switch → drop old) —
a bare `RENAME COLUMN` is only safe when you own every caller and deploy atomically.

## PostgreSQL production safety

- `CREATE INDEX CONCURRENTLY` (and `DROP ... CONCURRENTLY`) — cannot run in a transaction;
  give it its own migration marked non-transactional in your tool.
- Adding a column: `ADD COLUMN x type` (nullable, no default) is instant; since PG 11
  `DEFAULT <constant>` is also instant (no rewrite) — but a **volatile** default rewrites the
  table.
- Adding `NOT NULL` to an existing column: add a `CHECK (x IS NOT NULL) NOT VALID` →
  `VALIDATE CONSTRAINT` (scans without blocking writes) → then `SET NOT NULL` (fast, uses the
  validated check).
- Adding an FK: `NOT VALID` first, `VALIDATE CONSTRAINT` after — same trick.
- Changing a column type rewrites the table unless binary-compatible (`text`↔`varchar` fine;
  `int`→`bigint` rewrites) — treat rewrites as expand/contract instead on big tables.
- Set `lock_timeout`/`statement_timeout` for migration sessions — a DDL waiting on a lock
  queues *everything* behind it.

## SQLite production safety

- `ALTER TABLE` supports ADD COLUMN, RENAME TABLE/COLUMN, DROP COLUMN (3.35+) — everything
  else (type change, constraint change, column reorder) is the **12-step table rebuild**:
  create `new_table` → copy → drop old → rename → recreate indexes/triggers. Do it inside one
  transaction with `PRAGMA foreign_keys = OFF` for the duration, then back ON + 
  `PRAGMA foreign_key_check`.
- ADD COLUMN restrictions: cannot be `UNIQUE`/`PRIMARY KEY`; a non-constant default isn't
  applied to existing rows.
- Version tracking: your tool's table, or `PRAGMA user_version` for minimal setups.
- One writer at a time — run migrations with the app quiesced, or rely on WAL + short
  transactions for small ones.

## Review checklist for any migration

1. Down path real and tested (or explicitly declared irreversible + why + sign-off).
2. Locks: which statements block reads/writes, for how long, on how big a table?
3. Old code + new schema and new code + old schema both survive the deploy window
   (expand/contract respected)?
4. Constraints added match the business rule doc; names follow `style.md`.
5. Indexes added have their justifying query; none duplicated.
6. Data migration idempotent + chunked; row counts verified before contract.
7. FK enforcement stated (SQLite: connection PRAGMA; PG: NOT VALID/VALIDATE plan).
