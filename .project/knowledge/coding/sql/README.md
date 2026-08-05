# SQL Guide — use when working with SQL (queries, schemas, migrations)

> Covers **PostgreSQL 18** and **SQLite 3** (3.35+ assumed; notes flag newer minimums).
> General-purpose reference + style guide — project-independent. Engine-specific material lives
> in its own file; everything else applies to both.

## Files

| File | Read when |
|---|---|
| `style.md` | Always at least once — formatting, naming, casing, query-writing rules |
| `schema-design.md` | Designing tables: keys, types, constraints, soft-delete, tenancy |
| `query-patterns.md` | Writing non-trivial queries: joins, CTEs, upsert, pagination, locking |
| `indexing.md` | Adding/reviewing indexes; reading query plans |
| `migrations.md` | Any schema change — safety rules for both engines |
| `postgresql.md` | PostgreSQL-specific: v18 features, JSONB, RLS, sequences vs identity |
| `sqlite.md` | SQLite-specific: STRICT tables, WAL, type affinity, single-writer reality |
| `pitfalls.md` | Reviewing or debugging — NULL logic, implicit casts, lost updates… |

## The five rules that outrank everything

1. **NULL is three-valued logic** — every `NOT IN`, `<>`, and `WHERE` against a nullable column
   is a bug candidate until proven (`pitfalls.md`).
2. Constraints encode business rules in the schema (PK/FK/UNIQUE/CHECK/NOT NULL) — the app
   layer re-checks for UX, the database enforces truth.
3. No `SELECT *` outside ad-hoc exploration; name the columns you consume.
4. Every migration has a real down path, and every index has a real query that justifies it.
5. Parameterize always (`$1` / `?`) — string-built SQL is an injection, even "internal" SQL.
