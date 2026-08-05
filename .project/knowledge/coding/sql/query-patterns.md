# Query Patterns Reference

## CTEs vs subqueries vs temp mess

`WITH` names the steps — use CTEs for readability whenever a query has stages. PG 12+ inlines
CTEs (no optimization fence unless `MATERIALIZED`); SQLite inlines too. Recursive CTEs for
trees (folders, categories):

```sql
WITH RECURSIVE tree AS (
  SELECT id, parent_id, name, 0 AS depth
  FROM folders WHERE id = $1
  UNION ALL
  SELECT f.id, f.parent_id, f.name, t.depth + 1
  FROM folders f JOIN tree t ON f.parent_id = t.id
)
SELECT * FROM tree;
```

## Upsert — both engines share the syntax

```sql
INSERT INTO usage (organization_id, metric, value)
VALUES ($1, $2, $3)
ON CONFLICT (organization_id, metric)
DO UPDATE SET value = usage.value + excluded.value;
```

`excluded.*` = the row you tried to insert. `DO NOTHING` for idempotent inserts (event dedup).
The conflict target must match a unique constraint/index — design uniqueness first.

## Pagination

- **Cursor (keyset) pagination is the default** for feeds/lists: stable under inserts, O(1)
  per page:

```sql
SELECT id, created_at, ...
FROM notifications
WHERE organization_id = $1
  AND (created_at, id) < ($2, $3)      -- cursor from the previous page's last row
ORDER BY created_at DESC, id DESC
LIMIT $4;
```

  Always a unique tiebreaker in both the `ORDER BY` and the cursor. (SQLite lacks row-value
  comparison in old versions — expand to `created_at < $2 OR (created_at = $2 AND id < $3)`.)
- `OFFSET` only for small, admin-ish, jump-to-page UIs — it scans and discards, and drifts
  under concurrent writes.
- `COUNT(*)` totals are a separate, costable decision — cursor APIs typically skip `total`.

## Aggregation

- Aggregate-then-join beats join-then-aggregate for fan-out counts:

```sql
SELECT o.id, o.name, m.member_count
FROM organizations o
JOIN (
  SELECT organization_id, COUNT(*) AS member_count
  FROM memberships GROUP BY organization_id
) m ON m.organization_id = o.id;
```

- `FILTER` for conditional aggregates (both engines):
  `COUNT(*) FILTER (WHERE status = 'paid') AS paid_count`.
- Window functions for ranks/running totals/latest-per-group:

```sql
SELECT * FROM (
  SELECT s.*, ROW_NUMBER() OVER (PARTITION BY organization_id ORDER BY created_at DESC) rn
  FROM subscriptions s
) x WHERE rn = 1;      -- newest subscription per org
```

  (PG also: `DISTINCT ON (organization_id) ... ORDER BY organization_id, created_at DESC`.)

## Mutations that return

`RETURNING` on INSERT/UPDATE/DELETE (PG always; SQLite 3.35+) — one round trip, no re-select:

```sql
UPDATE invoices SET status = 'paid', paid_at = now()
WHERE id = $1 AND status = 'pending'
RETURNING id, total_cents;
```

Zero rows returned = the guard failed (already paid / not found) — that's your idempotency
check, not an error to ignore. PG 18 adds `RETURNING old.total_cents, new.total_cents` — both
sides of an update in one statement (audit trails without triggers).

## Locking & concurrency (mostly PG — SQLite serializes writers anyway)

- Read-modify-write without a race: `SELECT ... FOR UPDATE` inside the transaction (locks the
  rows you're about to change — the pattern behind "one active coupon redemption per
  subscription"-class invariants).
- Job queues: `FOR UPDATE SKIP LOCKED` + `LIMIT n` — concurrent workers each grab distinct rows.
- Optimistic alternative: `UPDATE ... WHERE id = $1 AND version = $2` — zero rows = retry.
- Keep transactions short; **never hold one across an external call** (payment gateway, HTTP) —
  commit first, call after.

## Batch operations

- Multi-row `VALUES` inserts (or `COPY` in PG for bulk) over row-at-a-time loops.
- Bulk update via join: PG `UPDATE t SET x = v.x FROM (VALUES ...) v(id, x) WHERE t.id = v.id`;
  SQLite `UPDATE ... FROM` (3.33+).
- Large deletes/updates in chunks (`... WHERE id IN (SELECT id FROM t WHERE cond LIMIT 1000)`
  loop) — one giant transaction bloats WAL/locks everything.
