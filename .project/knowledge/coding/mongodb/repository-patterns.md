# Repository Patterns

How the data-access layer is structured, so that MongoDB stays an implementation detail of storage
rather than a shape that leaks into every layer of the application.

## The boundary

A repository owns one aggregate — one root document and whatever is embedded in it — and exposes
**domain operations**, not database operations.

```
reserveStock(sku, qty) -> Result        ✅ a domain operation with an invariant
updateOne(filter, update)               ❌ a database operation wearing a repository's name
```

A repository that exposes filters and update documents to its callers has not encapsulated
anything: the query language spreads through the codebase, and no single place can enforce the
tenant scope or the version increment.

**Rules for the boundary:**

- Callers pass domain types and receive domain types. `ObjectId`, `Decimal128`, and BSON `Date`
  never escape the repository.
- The repository translates driver errors into domain errors: duplicate key (`11000`) becomes
  `AlreadyExists`; a zero `matchedCount` on a versioned update becomes `ConflictError`; a write
  timeout becomes a retryable failure.
- One repository per aggregate. A `$lookup` that spans two aggregates belongs in a query service,
  not in either repository.
- The tenant scope is applied **inside** the repository, from an explicit context argument — never
  left to the caller to remember. This is a security control (`../../conventions/security.md`).

## Mapping

Keep the persistence shape and the domain shape separate, with explicit mapping functions. It costs
a small amount of code and buys the ability to change either side independently:

```ts
// Persistence shape — what is actually in the collection
interface OrderDoc {
  _id: ObjectId
  orgId: ObjectId
  status: "draft" | "paid" | "shipped" | "cancelled"
  total: Decimal128
  items: { sku: string; qty: number; unitPrice: Decimal128 }[]
  version: number
  createdAt: Date
  updatedAt: Date
  schemaVersion: number
}

function toDomain(doc: OrderDoc): Order { /* ... */ }
function toDoc(order: Order): OrderDoc  { /* ... */ }
```

- **Never let the ODM's document object be the domain object.** A domain entity that carries a live
  database handle cannot be constructed in a test, serialized, or reasoned about.
- Mapping is where `schemaVersion` is handled: the read path accepts version n and n-1 during a
  migration and normalizes both to one domain shape (`schema-design.md`).
- Map money and dates explicitly. `Decimal128` → the language's decimal type, never a float.

## Structure

```
repository/
├── orders.ts          the repository: domain operations
├── orders.doc.ts      the document interface + mapping
└── orders.indexes.ts  index definitions, applied at startup or by a migration
```

Keeping index definitions **in code beside the repository** is what stops indexes from being
something someone added once in a shell and nobody can find. Apply them from a migration step, not
implicitly on every connection.

## Writes that carry invariants

Concentrate concurrency control in the repository so no caller can bypass it:

```ts
async function markPaid(ctx: Ctx, id: OrderId, expectedVersion: number): Promise<Order> {
  const res = await this.col.findOneAndUpdate(
    { _id: toObjectId(id), orgId: ctx.orgId, status: "draft", version: expectedVersion },
    { $set: { status: "paid", paidAt: new Date(), updatedAt: new Date() }, $inc: { version: 1 } },
    { returnDocument: "after" }
  )
  if (!res) throw new ConflictError("order changed or not in draft")
  return toDomain(res)
}
```

The guard condition (`status: "draft"`) and the version live in the filter, inside the repository —
so every path that marks an order paid gets the same protection.

## Sessions and transactions

Pass the session through as an optional argument on every method, so a caller can compose several
repositories inside one transaction without the repositories knowing about each other:

```ts
async function insert(ctx: Ctx, order: Order, session?: ClientSession): Promise<void>
```

A repository that opens its own transaction internally cannot be composed. Transaction boundaries
belong to the use case, not to storage (`transactions.md`).

## Testing

| Layer | Against | Covers |
|---|---|---|
| Domain logic | Nothing — pure functions | Business rules, state transitions, money math |
| Repository | **A real MongoDB** (container or in-memory replica set) | Filters, indexes, upserts, version conflicts, unique violations |
| Use case | Fake repository interfaces | Orchestration and error handling |

**Do not mock the driver to test a repository.** A mocked `updateOne` returns whatever you told it
to; it cannot tell you that your filter misses documents where the field is absent, that your index
does not serve the sort, or that your unique constraint is on the wrong fields. Those are exactly
the bugs repository tests exist to catch.

Practical rules for repository tests:

- Run against a **single-node replica set**, not a standalone server, so transaction and session
  code paths are exercised.
- Create the real indexes in test setup. A test suite without indexes passes queries that will
  collection-scan in production, and never catches a unique-constraint mistake.
- Isolate by database or by tenant per test, and clean up after. Shared mutable fixtures across
  tests produce failures that depend on execution order.
- Test the conflict paths explicitly: a stale version, a duplicate key, a guard condition that
  fails. These are the paths that only appear in production otherwise.

## Migrations

Schema and index changes are versioned files applied in order, exactly like relational migrations —
the absence of `ALTER TABLE` is not an absence of the need to track changes:

```
migrations/
├── 001_orders_indexes.ts
├── 002_orders_add_schema_version.ts
└── 003_orders_backfill_customer_name.ts
```

Each migration records itself in a `_migrations` collection, is idempotent, and processes large
collections in batches (`production.md`). Down paths must genuinely reverse, or must state in a
comment why the change is one-way — an index drop is reversible, a field deletion is not.
