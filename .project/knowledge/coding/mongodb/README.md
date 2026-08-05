# MongoDB Guide — use when working with MongoDB (queries, schemas, aggregations, migrations)

> Covers **MongoDB 8.x**, with **7.0 as the assumed floor**; anything needing a newer version is
> flagged inline. General-purpose reference — project-independent. Project-specific rules layer on
> top in `../../conventions/database.md`.

## Files

| File | Read when |
|---|---|
| `mql.md` | Writing any query or update — operators, projection, array updates |
| `schema-design.md` | Designing collections: embed vs reference, patterns, validation |
| `indexing.md` | Adding or reviewing indexes; reading `explain` output |
| `aggregation.md` | Any pipeline beyond a trivial `$match` |
| `transactions.md` | Multi-document atomicity, sessions, causal consistency |
| `query-patterns.md` | Pagination, optimistic concurrency, upserts, bulk writes |
| `repository-patterns.md` | Structuring the data-access layer and testing it |
| `performance.md` | Slow queries, working set, profiler, read/write concerns |
| `production.md` | Deploying, connection pooling, migrations, backups, monitoring |
| `pitfalls.md` | Reviewing or debugging — the checklist of what actually bites |

## The five rules that outrank everything

1. **Design the schema around the queries, not the entities.** MongoDB has no query planner
   heroics to save a shape that does not match its access patterns. Write the two or three real
   queries down *first*, then design documents that answer them in one read.
2. **Every query in a hot path has an index, and you have seen its `explain`.** The number that
   matters is `totalKeysExamined` versus `nReturned`; anything far above 1:1 is a scan wearing a
   disguise. Compound index order follows **ESR**: equality, sort, range (`indexing.md`).
3. **Unbounded arrays are a schema bug.** A document that grows forever hits the 16 MB limit,
   rewrites entirely on every update, and destroys index locality. If an array has no natural
   ceiling, it is a separate collection (`schema-design.md`).
4. **Atomicity is per document.** A single document update is atomic; two are not, unless you open
   a transaction — and transactions cost more here than in a relational engine. Prefer a schema
   where the unit of consistency *is* one document (`transactions.md`).
5. **Never paginate with `skip`.** `skip(n)` walks and discards n documents on every page. Use
   range pagination on the sort key plus `_id` as the tiebreaker (`query-patterns.md`).

## Non-negotiables for correctness

- **Money is `Decimal128`, never a double.** Floating point loses cents silently.
- **Dates are BSON `Date` in UTC**, never strings — string dates sort lexically and break ranges.
- **Missing is not null.** `{field: null}` matches both missing and explicitly-null documents;
  `{field: {$exists: false}}` and `{field: {$type: "null"}}` are different questions
  (`pitfalls.md`).
- **Never build a query from string concatenation** or pass unvalidated user input as a query
  object — an attacker-supplied `{$ne: null}` is the NoSQL injection you will actually meet.
- **Write concern is a correctness decision.** Anything you cannot afford to lose is
  `w: "majority"`. The default is not always what you want (`production.md`).
