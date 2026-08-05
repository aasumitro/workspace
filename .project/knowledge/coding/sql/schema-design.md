# Schema Design Reference

## Keys

- Every table has an explicit PK. Default: UUIDv7 (`uuidv7()` native in PG 18 — time-ordered,
  so it indexes like a sequence without the coordination of one). SQLite: TEXT UUIDs generated
  in the app, or `INTEGER PRIMARY KEY` (the rowid) where locality matters.
- Identity columns where sequential integers are fine: PG
  `bigint GENERATED ALWAYS AS IDENTITY` (never `serial` in new schemas); SQLite
  `INTEGER PRIMARY KEY` (avoid `AUTOINCREMENT` unless you truly need no-reuse).
- Natural keys (slugs, codes) get `UNIQUE`, not PK — they change; PKs don't.
- Composite PKs for pure join tables (`(subscription_id, addon_id)`); surrogate `id` once the
  join row grows attributes of its own.

## Types (both engines unless noted)

| Data | Use | Not |
|---|---|---|
| Money | integer minor units (`_cents bigint`) or PG `numeric` | float/real/double — ever |
| Timestamps | PG `timestamptz` (UTC in, tz at display); SQLite integer epoch or ISO-8601 TEXT — pick ONE per project | naive local times |
| Text | PG `text` (+`CHECK` length if needed); SQLite `TEXT` | arbitrary `varchar(255)` folklore |
| Flags | `boolean NOT NULL DEFAULT false` (SQLite: `INTEGER` 0/1 + `CHECK`) | nullable booleans (three states by accident) |
| Enums | `text` + `CHECK (status IN (...))` | PG native `ENUM` (ALTERing is painful); magic ints |
| Flexible payloads | PG `jsonb`; SQLite `TEXT` + `json_valid()` CHECK (JSONB storage 3.45+) | JSON as a schema-avoidance lifestyle |

Columns for anything queried, constrained, or indexed; JSON only for genuinely open-shape data
(settings, provider payloads). If a JSON field appears in a `WHERE` on a hot path, it's asking
to become a column (or an expression index).

## Constraints — the schema is the last line of defense

- `NOT NULL` by default; nullable is a deliberate, meaningful choice ("unknown", not "false").
- `CHECK` for closed sets, ranges, and cross-column rules
  (`CHECK (trial_end IS NULL OR trial_end > created_at)`).
- `UNIQUE` for every real-world uniqueness rule — including partial/conditional in PG
  (`CREATE UNIQUE INDEX ... WHERE deleted_at IS NULL` — uniqueness among the living).
- FKs with explicit `ON DELETE`: `RESTRICT` (default stance — force the app to decide),
  `CASCADE` only for true ownership (line items of an invoice), `SET NULL` for optional links.
  SQLite: FKs are OFF per-connection unless `PRAGMA foreign_keys = ON` — enforce in the
  connection setup, not in hope.
- Follow the project's declared boundary rules on cross-module/schema references — some
  architectures (multi-tenant modular monoliths) deliberately use plain ID columns validated in
  code across module boundaries, with real FKs only inside a module. Respect whichever rule
  the project's database conventions doc states.

## Standard columns & patterns

- `created_at NOT NULL DEFAULT now()` (SQLite: `DEFAULT (unixepoch())`), `updated_at`
  maintained by the app or trigger — pick one mechanism project-wide.
- **Soft delete**: `deleted_at` timestamp (null = alive). Every query on the table filters it —
  which is why partial indexes `WHERE deleted_at IS NULL` (PG) pay for themselves. Declare who
  purges (job, lazy sweep) at design time.
- **Multi-tenancy**: `organization_id` (or the project's tenant key) on every tenant-owned
  table, `NOT NULL`, leading column of most composite indexes, and in every query — RLS (PG)
  as backstop where the project uses it.
- **Optimistic concurrency** where lost updates matter: `version int` bumped on update, `WHERE
  version = $expected` (`query-patterns.md`).
- Generated columns for derived-but-indexed values: PG 18 defaults to **virtual** (computed on
  read; `STORED` still available and required for some index cases); SQLite has both
  (3.31+).

## Growing schemas

Prefer adding nullable columns / new tables over repurposing old ones. A column whose meaning
changed is worse than two columns. Delete columns in a later migration than the code that
stopped writing them (expand-migrate-contract, `migrations.md`).
