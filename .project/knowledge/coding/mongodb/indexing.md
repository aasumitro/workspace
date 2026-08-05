# Indexing

An index is a permanent write tax and a chunk of RAM justified by a named query. No speculative
indexes; write the query beside the index in the migration or the plan.

## ESR — the rule that decides compound index order

**Equality, Sort, Range**, in that order:

```js
// Query
db.orders.find({ orgId, status: "paid", total: { $gte: 100 } }).sort({ createdAt: -1 })

// Index
{ orgId: 1, status: 1, createdAt: -1, total: 1 }
//  └── equality ──┘   └── sort ──┘   └─ range ─┘
```

Getting this wrong is the difference between an index scan that returns exactly the rows you asked
for and one that returns thousands and sorts them in memory. A range field placed before the sort
field forces an in-memory sort — and a sort of more than 100 MB fails outright unless the query
allows disk use.

**Prefix rule:** `{a: 1, b: 1, c: 1}` serves queries on `a`, `a+b`, and `a+b+c` — never `b` alone.
One good compound index replaces three single-field ones.

**Sort direction:** an index can be walked in either direction, so `{a: 1, b: -1}` serves both
`sort({a: 1, b: -1})` and `sort({a: -1, b: 1})` — but not `sort({a: 1, b: 1})`.

## Index types

| Type | Use for | Note |
|---|---|---|
| Single field | One predicate | `{ email: 1 }` |
| Compound | Everything real | Up to 32 fields; ESR order |
| Multikey | Any indexed array field | Created automatically; **at most one array field per index** |
| Text | Keyword search | One text index per collection; use Atlas Search for anything serious |
| Wildcard | Genuinely unpredictable field names | `{ "attrs.$**": 1 }` — a last resort, not a shortcut |
| Hashed | Shard key with even distribution | Cannot serve range queries |
| 2dsphere | Geospatial | GeoJSON only |
| TTL | Automatic expiry | Single field, BSON `Date` |

**Index properties** — combinable with the types above:

```js
// Unique, scoped to the tenant
db.users.createIndex({ orgId: 1, email: 1 }, { unique: true })

// Partial — index only the rows queries touch; smaller, hotter, cheaper to maintain
db.orders.createIndex(
  { orgId: 1, createdAt: -1 },
  { partialFilterExpression: { status: "pending" } }
)

// Uniqueness among the living (soft delete)
db.files.createIndex(
  { orgId: 1, path: 1 },
  { unique: true, partialFilterExpression: { deletedAt: { $exists: false } } }
)

// Case-insensitive: the index and the query must use the SAME collation
db.users.createIndex({ email: 1 }, { collation: { locale: "en", strength: 2 } })
db.users.find({ email: "Foo@Bar.com" }).collation({ locale: "en", strength: 2 })

// TTL — deletes documents ~60s after expiresAt passes
db.sessions.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 })
```

**Partial beats sparse.** `sparse: true` only skips documents missing the field;
`partialFilterExpression` expresses any condition and is strictly more capable.

## Multikey constraints

- **One array field per compound index.** `{ "items.sku": 1, "tags": 1 }` fails if both are arrays.
- Multikey indexes cannot fully cover a query — the array element is not enough to reconstruct the
  document.
- An index on an array of subdocuments (`items.sku`) does not enforce that a single element matched
  both conditions; that is `$elemMatch`'s job (`mql.md`).

## Reading `explain`

```js
db.orders.find({ orgId, status: "paid" }).sort({ createdAt: -1 })
  .explain("executionStats")
```

The four numbers that matter:

| Field | Want | Bad sign |
|---|---|---|
| `stage` | `IXSCAN` → `FETCH` | `COLLSCAN` on anything large |
| `totalKeysExamined` vs `nReturned` | close to 1:1 | 1000 keys for 10 documents = wrong index order |
| `totalDocsExamined` vs `nReturned` | close to 1:1, or 0 for a covered query | high = the index cannot filter, only locate |
| `SORT` stage present | absent | present = in-memory sort; the index is not serving the sort |

`executionTimeMillis` is the last thing to look at, not the first — it varies with cache state; the
examined-to-returned ratio does not.

**Covered query:** every field in the filter, sort, and projection lives in the index, so
`totalDocsExamined` is 0. Requires excluding `_id` unless `_id` is in the index. Worth engineering
for the one or two hottest list endpoints; not worth contorting a schema over.

## Building indexes in production

- Modern versions build indexes with only brief exclusive locks at start and end, but the build
  still consumes I/O and memory on a hot collection.
- On a replica set, prefer a **rolling build**: one secondary at a time, then step down the primary.
- Always name indexes explicitly (`{ name: "orders_org_status_created" }`). The generated name is
  unreadable at 64 characters, and every drop and rollback becomes a guessing game without it.
- Create indexes before the code that needs them ships — an index built after the traffic arrives is
  built under load.

## Hygiene

- `db.collection.aggregate([{ $indexStats: {} }])` shows access counts per index. An index with zero
  accesses over a representative window is pure write tax — drop it.
- Redundant prefixes: `{a: 1}` alongside `{a: 1, b: 1}` — keep the compound, drop the prefix.
- Every index must fit its working set in RAM, together with the documents it points at. Once the
  index no longer fits, every query pays a disk read per key.
- `db.collection.getIndexes()` belongs in review whenever a query is added.
