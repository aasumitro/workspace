# Indexing Reference

An index is a write cost and a maintenance liability justified by a real query. No speculative
indexes; no index without the query it serves written next to it (in the migration or the
plan).

## What to index

1. FK columns (PG does **not** auto-index FKs; SQLite doesn't either) — joins and cascades
   need them.
2. Columns in hot `WHERE` equality/range predicates — most selective patterns first.
3. The exact `ORDER BY` of paginated queries (`(organization_id, created_at DESC, id DESC)`) —
   lets the engine read rows pre-sorted instead of sorting.
4. `UNIQUE` for every uniqueness rule (this is a constraint that happens to be an index).

## Composite index rules

- **Leftmost prefix**: `(org_id, status, created_at)` serves `org_id`, `org_id+status`,
  `org_id+status+created_at` — not `status` alone.
- Order: equality columns first, then the range/sort column last
  (`WHERE org_id = $1 AND status = $2 ORDER BY created_at` → `(org_id, status, created_at)`).
- The tenant key leads almost every index in a multi-tenant schema.
- One good composite beats three single-column indexes the planner must bitmap-combine.

## PostgreSQL specials

- **Partial indexes** — index only the rows queries touch:

```sql
CREATE UNIQUE INDEX uq_files_live_path ON files (organization_id, path)
WHERE deleted_at IS NULL;                    -- uniqueness among the living
CREATE INDEX idx_invoices_pending ON invoices (organization_id, created_at)
WHERE status = 'pending';                    -- tiny, hot
```

- **Expression indexes** — `CREATE INDEX ... ON users (lower(email));` then query
  `WHERE lower(email) = $1` (expression must match exactly).
- **Covering** — `INCLUDE (columns)` for index-only scans on hot reads.
- **GIN** for `jsonb` containment (`@>`) and full-text (`tsvector`); **GiST** for ranges/
  geometric; **BRIN** for huge append-only tables ordered by time.
- `CREATE INDEX CONCURRENTLY` in production migrations (`migrations.md`) — plain CREATE INDEX
  locks writes.
- UUIDv7 PKs index like sequences (time-ordered) — random UUIDv4 PKs fragment B-trees; prefer
  v7 (native in 18).

## SQLite specials

- Partial indexes: supported (`WHERE` clause) — same soft-delete trick works.
- Expression indexes: supported — including on JSON extracts:
  `CREATE INDEX idx_settings_tz ON orgs (json_extract(settings, '$.timezone'));`
- `WITHOUT ROWID` tables for large composite-PK join tables (saves the rowid indirection).
- Run `PRAGMA optimize;` on connection close (maintains stats); `ANALYZE` after bulk loads.

## Reading plans — the review step for any new hot query

- PG: `EXPLAIN (ANALYZE, BUFFERS) <query>` — red flags: `Seq Scan` on a big table in a hot
  path, `Rows Removed by Filter` huge vs returned, sorts spilling to disk, nested loops over
  large outer sets. Estimated-vs-actual row counts wildly off → stale stats (`ANALYZE`) or a
  non-sargable predicate.
- SQLite: `EXPLAIN QUERY PLAN <query>` — want `SEARCH ... USING INDEX`, not `SCAN` on big
  tables.

## Sargability — why an index gets ignored

The predicate must expose the bare column: `WHERE lower(email) = $1` ignores an index on
`email` (index the expression instead); `WHERE created_at + interval '1 day' > now()` ignores
`created_at` (rewrite as `created_at > now() - interval '1 day'`); implicit type casts
(`text_col = 123`) disable index use silently. Leading-wildcard `LIKE '%x'` can't use a B-tree.

## Hygiene

Drop unused indexes (PG: `pg_stat_user_indexes.idx_scan = 0` over a representative window) —
every one taxes every write. Duplicate/prefix-redundant indexes (`(a)` alongside `(a, b)`) —
keep the composite.
