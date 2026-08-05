# SQL Style Reference

## Casing & naming

- Keywords **UPPERCASE** (`SELECT`, `FROM`, `WHERE`); identifiers `snake_case`, never quoted-
  mixed-case (unquoted identifiers fold — quoting `"CamelCase"` condemns every future query to
  quotes).
- Tables **plural** (`invoices`, `plan_features`); columns singular; join tables named after
  both parents (`subscription_addons`).
- PK: `id`. FKs: `<singular>_id` (`organization_id`). Booleans read as predicates
  (`is_active`, `has_trial`); timestamps end `_at` (`created_at`, `deleted_at`); dates end
  `_on`; counts end `_count`.
- Indexes `idx_<table>_<cols>`; unique `uq_`; checks `ck_`; foreign keys `fk_` — name
  constraints explicitly; auto-generated names make future drops archaeology.
- No reserved words as identifiers (`user`, `order`, `group` — use `users`, `orders`).

## Layout

One clause per line, indented continuation; commas trailing:

```sql
SELECT i.id,
       i.total_cents,
       o.name AS organization_name
FROM invoices i
JOIN organizations o ON o.id = i.organization_id
WHERE i.status = 'pending'
  AND i.created_at < $1
ORDER BY i.created_at DESC
LIMIT 50;
```

- Meaningful short aliases (`invoices i`, `organizations o`) — consistent per table across the
  codebase; never single letters that collide (`t1`, `t2`).
- Explicit `JOIN ... ON` — never comma joins; `AS` for column aliases always.
- Multi-line CTEs: one CTE per `WITH` block line, named after what it *holds*
  (`overdue_invoices`), not steps (`cte1`).

## Query-writing rules

- Name columns in `SELECT` and in `INSERT INTO t (cols...)` — positional inserts break on the
  next migration.
- Parameterize every value (`$1`/`?`); interpolation is allowed **only** for identifiers that
  cannot be parameters (table/column names from a fixed allowlist — never from input).
- `ORDER BY` on column names, not ordinals (`ORDER BY 2` breaks silently on select-list edits).
- Deterministic ordering for any paginated/limited query: always a unique tiebreaker
  (`ORDER BY created_at DESC, id DESC`).
- Booleans compared directly (`WHERE is_active`), not `= true`.
- Casts explicit (`::bigint` in PG, `CAST(... AS INTEGER)` portable) — implicit casts are where
  index usage quietly dies (`pitfalls.md`).

## Comments

`--` for line comments above the clause they explain — explain *why* (the business rule, the
planner trick), not what the SQL obviously does. In application code, keep SQL in one place per
query (constant/query file per the project's convention) — not concatenated fragments.
