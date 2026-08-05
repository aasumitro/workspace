# SQL Pitfalls

## NULL three-valued logic (the #1 source of wrong results)

- `NULL = NULL` is not true — it's NULL. `WHERE x <> 'a'` silently drops rows where `x IS
  NULL`.
- **`NOT IN` with a NULL in the list returns zero rows, always:**

```sql
WHERE id NOT IN (SELECT ref_id FROM t)   -- one NULL ref_id ⇒ empty result
```

  Use `NOT EXISTS` (NULL-safe) or filter the subquery `WHERE ref_id IS NOT NULL`.
- Aggregates skip NULLs (`COUNT(col)` vs `COUNT(*)` differ); `SUM` of no rows is NULL, not 0 —
  wrap `COALESCE(SUM(x), 0)`.
- Null-safe comparison: `IS [NOT] DISTINCT FROM` (both engines).
- `UNIQUE` treats NULLs as distinct — a nullable unique column admits many NULL rows (PG 15+:
  `UNIQUE NULLS NOT DISTINCT` if you don't want that).

## Lost updates

`SELECT` → compute in app → `UPDATE` without a guard: two concurrent requests both succeed,
one overwrites the other. Guard with `FOR UPDATE`, optimistic `WHERE version = $n`, or make
the update self-contained (`SET value = value + $1`). Read-committed does **not** save you.

## Implicit casts kill indexes silently

`WHERE text_col = 123` / comparing across types works — by casting, which disables the index
and occasionally changes semantics. Match parameter types to column types; cast explicitly.

## Non-sargable predicates

Function-wrapped columns (`WHERE lower(email) = $1`, `date(created_at) = $1`) ignore plain
indexes — index the expression, or rewrite as a range
(`created_at >= $day AND created_at < $day + 1`). Leading-wildcard `LIKE '%term'` can't use a
B-tree (FTS is the answer to search).

## JOIN fan-out multiplies aggregates

Joining one-to-many then `SUM`/`COUNT` counts each parent once *per child* — pre-aggregate in
a subquery/CTE, then join (`query-patterns.md`). The same fan-out silently duplicates rows
into an `UPDATE ... FROM` — dedupe the source.

## WHERE vs ON for LEFT JOINs

A filter on the right table in `WHERE` turns a LEFT JOIN into an INNER JOIN (NULLs fail the
predicate). Filter the right side in the `ON` clause:

```sql
LEFT JOIN payments p ON p.invoice_id = i.id AND p.status = 'settled'
```

## Unstable pagination

`LIMIT/OFFSET` without a unique `ORDER BY` tiebreaker returns rows in whatever order the plan
felt like — pages overlap and skip. Always `ORDER BY <sort_col>, id` (and prefer keyset
pagination anyway).

## Engine-specific traps

**PostgreSQL**
- `count(*)` is a real scan — don't sprinkle totals on hot paths; estimate or cache.
- Idle-in-transaction connections block vacuum and hold locks — commit or roll back; never hold
  a tx across an external call.
- `NUMERIC` math is exact but slow in hot loops; integers where possible.
- DDL waits queue everyone behind them (`lock_timeout` in migrations — `migrations.md`).
- Sequences gap on rollback — by design; don't reconcile them.

**SQLite**
- Foreign keys are OFF unless the connection sets `PRAGMA foreign_keys = ON` — every FK you
  wrote is decoration otherwise.
- Type affinity accepts `'banana'` into INTEGER columns on non-STRICT tables (`sqlite.md` —
  use STRICT).
- `SQLITE_BUSY` mid-transaction = you started `BEGIN` (deferred) then wrote; start write
  transactions `BEGIN IMMEDIATE` and set `busy_timeout`.
- Autocommit-per-statement bulk inserts are ~100x slower — wrap batches in one transaction.
- Integer division truncates (`5/2 = 2`) — cast one side (`5/2.0`) when you mean fractions
  (PG: same trap).

## Injection is a query-construction property

Parameterize values, always. Identifiers that must vary (sort column) come from a hardcoded
allowlist mapping — never concatenated user input, "escaped" or not. This applies to internal
tools and one-off scripts exactly as much as to public endpoints — that's where the incidents
live.

## Schema drift between environments

A migration edited after teammates ran it forks reality (`migrations.md`: append, don't edit).
Comparing prod to schema files by eye fails — diff actual dumps (`pg_dump --schema-only`,
`.schema`) in CI if drift bites twice.
