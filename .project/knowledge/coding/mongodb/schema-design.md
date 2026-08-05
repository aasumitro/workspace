# Schema Design

The schema is the performance decision. In a relational engine you normalize and let the planner
join; here you shape documents around the queries you will actually run, and a wrong shape cannot
be fixed by an index.

## The one decision: embed or reference

**Embed when** the child is read with the parent almost every time, the child does not need to be
queried independently, the relationship is one-to-few, and the array has a natural ceiling.

**Reference when** the child is queried on its own, the relationship is one-to-many with no
ceiling, the child is written far more often than the parent, or the child is large.

| Cardinality | Default shape |
|---|---|
| One-to-one | Embed |
| One-to-few (≤ dozens, bounded) | Embed the array |
| One-to-many (hundreds, bounded) | Embed IDs in the parent, or reference from the child |
| One-to-squillions (unbounded) | Child collection with a parent reference and an index on it |
| Many-to-many | Reference both ways, or an edge collection when the edge has attributes |

```js
// Embedded: an order and its lines — always read together, bounded
{ _id, orgId, status, total: Decimal128("120.50"),
  items: [ { sku: "A", qty: 2, unitPrice: Decimal128("30.00") } ] }

// Referenced: a product and its reviews — unbounded, queried on their own
{ _id: productId, orgId, name, price }
{ _id, productId, orgId, rating, body, createdAt }   // index: { productId: 1, createdAt: -1 }
```

## Hard limits that shape designs

| Limit | Value | Consequence |
|---|---|---|
| Document size | 16 MB | Any unbounded array or embedded log eventually fails a write |
| Nesting depth | 100 levels | Deeply nested trees are a modeling smell long before this |
| Index key | ~1024 bytes | Cannot index a long string field in full |
| Indexes per collection | 64 | Write cost makes this a soft limit far earlier |
| Collection name + db | 255 bytes | — |

A document is rewritten in full when it grows past its allocated space. A 2 MB document updated on
every request is a write-amplification problem no index will solve.

## Patterns worth knowing

| Pattern | Problem it solves | Shape |
|---|---|---|
| **Extended reference** | `$lookup` on every read | Copy the two or three fields you actually display (`{ userId, userName }`) into the child; refresh on change |
| **Subset** | Huge embedded array read whole | Embed the top N (recent comments), keep the rest in a child collection |
| **Computed** | Recomputing an aggregate on every read | Store `orderCount`, `totalSpend` on the parent; update with `$inc` in the same write |
| **Bucket** | Millions of tiny time-series documents | One document per device per hour holding an array of readings |
| **Outlier** | 99% of docs are small, 1% are enormous | Flag the outlier (`hasOverflow: true`) and spill to a child collection |
| **Attribute** | Many sparse, unpredictable fields | `attrs: [{ k: "color", v: "red" }]` with an index on `attrs.k, attrs.v` |
| **Schema version** | Migrating a live collection | `schemaVersion: 3` on every document; read handles n and n-1, migrate lazily |
| **Polymorphic** | Related things with different fields | One collection, a `type` discriminator, shared fields at the top level |

**Extended reference is the standard answer to "should I `$lookup` here?"** Denormalize the display
fields, accept that they need updating, and decide explicitly whether staleness is tolerable —
usually it is for a name, never for a price.

## Anti-patterns

- **Unbounded arrays.** The single most common production failure. Bound every array with `$slice`
  or move it out.
- **Massive number of small collections** (one per tenant, one per day). Each costs metadata and
  index overhead. Use a field and an index instead.
- **Relational carry-over.** A collection per table with `$lookup` everywhere gives you a slow
  relational database with no foreign keys. Either shape it for the reads, or use a relational
  engine.
- **Case-normalized duplicates** (`emailLower` alongside `email`) when a collation index would do
  (`indexing.md`).
- **Storing computed data you never query** — every field costs bytes on every read.
- **`_id` as a meaningless surrogate when a natural unique key exists.** `_id: orgId + ":" + slug`
  gives uniqueness and a free index.

## Field conventions

- **`_id`** — `ObjectId` by default; its first four bytes are a timestamp, so `_id` sorts roughly
  by creation time and works as a pagination tiebreaker. Use a natural key when one exists and is
  immutable. Never a random UUID stored as a string if you can avoid it: 36 bytes on every index
  entry, and no locality.
- **Money** — `Decimal128`. Never a double, never a float in any language binding.
- **Dates** — BSON `Date`, UTC, no strings. Store the timezone separately if the *user's* timezone
  is part of the domain.
- **Tenancy** — the tenant key (`orgId`) is the first field of nearly every index and appears in
  **every** query. This is a security control, not just a performance one (`../../conventions/security.md`).
- **Enums** — short strings, validated by `$jsonSchema`. Integers save bytes and cost readability
  in every log line you will ever read.
- **Soft delete** — `deletedAt: Date | null` plus a partial index `{ deletedAt: { $exists: false } }`
  so live-document queries stay cheap.
- **Timestamps** — `createdAt` / `updatedAt` on everything. `$currentDate` or `$$NOW` sets them
  server-side, which avoids clock skew between application hosts.

## Schema validation

Validation belongs in the database, not only in the application — the application is not the only
writer (migrations, scripts, another service):

```js
db.createCollection("orders", {
  validator: { $jsonSchema: {
    bsonType: "object",
    required: ["orgId", "status", "total", "createdAt"],
    properties: {
      orgId:  { bsonType: "objectId" },
      status: { enum: ["draft", "paid", "shipped", "cancelled"] },
      total:  { bsonType: "decimal", minimum: 0 },
      items:  { bsonType: "array", maxItems: 500,
                items: { bsonType: "object", required: ["sku", "qty"] } }
    }
  }},
  validationLevel: "moderate",   // strict | moderate (existing invalid docs are left alone)
  validationAction: "error"      // error | warn
})
```

Adding validation to a live collection: start with `validationAction: "warn"`, watch the logs, then
switch to `error`. `validationLevel: "moderate"` applies rules only to documents that already
conform — the safe setting during a migration.

## Evolving a schema

There is no `ALTER TABLE`, which makes migration *easier* and forgetting *cheaper* — both are
traps. The disciplined path:

1. Add `schemaVersion` to new documents from day one.
2. New fields are optional at first; the read path handles both shapes.
3. Backfill in chunks (`production.md`), never in one `updateMany` over a large collection.
4. Only after the backfill completes and the read path no longer needs the old shape, tighten the
   validator and remove the compatibility branch.

Document the current shape in `../../conventions/database.md` — a collection whose real shape lives
only in application code is a collection nobody can safely query.
