# Query Patterns

Pagination, concurrency control, upserts, and bulk writes — the four patterns every non-trivial
MongoDB application needs and most get wrong at least once.

## Pagination

### Never use `skip`

`skip(n)` walks and discards n documents server-side on every page. Page 1 is fast, page 500 is a
scan, and the cost grows without bound. It is also *incorrect* under concurrent writes: a document
inserted before your position shifts everything, so you see a row twice or miss it entirely.

### Range pagination (the correct default)

Sort by an indexed key, carry the last value forward, and break ties with `_id`:

```js
// Page 1
db.orders.find({ orgId })
  .sort({ createdAt: -1, _id: -1 })
  .limit(20)

// Page n+1 — cursor = { createdAt, _id } of the last row of page n
db.orders.find({
  orgId,
  $or: [
    { createdAt: { $lt: cursor.createdAt } },
    { createdAt: cursor.createdAt, _id: { $lt: cursor._id } }   // tiebreaker
  ]
}).sort({ createdAt: -1, _id: -1 }).limit(20)

// Index: { orgId: 1, createdAt: -1, _id: -1 }
```

The `$or` tiebreaker is mandatory whenever the sort key is not unique — without it, documents
sharing a timestamp are skipped or repeated at page boundaries.

**Encode the cursor opaquely** (base64 of the sort values) so clients cannot craft one, and so you
can change the sort key without breaking the API contract.

Trade-off: range pagination gives next/previous, not "jump to page 40". That is almost always the
right trade. When a UI genuinely needs page numbers, cap the range (`page ≤ 100`) or precompute.

### Counting

`countDocuments(filter)` runs a real aggregation and scans the index — it is not free on a large
collection. `estimatedDocumentCount()` reads collection metadata and is instant but ignores filters
and is approximate. For a paginated list, prefer: return `hasMore` (fetch `limit + 1`, return
`limit`) instead of a total. Most UIs need "is there more", not "how many".

## Optimistic concurrency

The read-modify-write race: two requests read version 4, both compute a new state, the second
silently overwrites the first. This is a **lost update**, and it is invisible in logs.

### Version field (the general pattern)

```js
// Read
const doc = await orders.findOne({ _id })            // doc.version === 4

// ...application logic computes newStatus...

// Write — the version is part of the filter
const res = await orders.updateOne(
  { _id, version: doc.version },
  { $set: { status: newStatus, updatedAt: new Date() }, $inc: { version: 1 } }
)

if (res.matchedCount === 0) {
  // someone else wrote first: re-read and retry, or surface a 409 to the caller
}
```

Rules that make it work:

- **Every** writer increments the version. One path that forgets defeats the whole mechanism.
- The version lives in the filter, never only in the update.
- Decide the retry policy explicitly: retry a bounded number of times for machine-driven writes;
  return `409 Conflict` for user-driven edits so the human resolves the conflict.
- Reject an update whose version is absent — that is an old client, not a valid write.

### Guard conditions (better, when it fits)

When the invariant can be expressed as a predicate, skip versions entirely — the filter *is* the
concurrency control, and it never needs a retry:

```js
// Only transition from a specific state
db.orders.findOneAndUpdate(
  { _id, status: "pending" },
  { $set: { status: "paid", paidAt: new Date() } }
)

// Only decrement if stock allows
db.inventory.findOneAndUpdate(
  { _id: sku, onHand: { $gte: qty } },
  { $inc: { onHand: -qty } }
)
```

Prefer this shape wherever the business rule is expressible as a filter. It is atomic, single-round-
trip, and cannot lose an update.

## Upserts

```js
db.counters.updateOne(
  { _id: key },
  { $inc: { seq: 1 }, $setOnInsert: { createdAt: new Date() } },
  { upsert: true }
)
```

- `$setOnInsert` applies **only** on insert — use it for creation timestamps and immutable defaults.
- Fields in the *filter* are copied into the new document automatically; do not repeat them in
  `$set`.
- **An upsert on a non-unique filter can create duplicates under concurrency.** Two simultaneous
  upserts that both miss will both insert. Back every upsert filter with a unique index and catch
  the duplicate-key error (code `11000`) as the retry signal.

```js
try {
  await users.updateOne({ orgId, email }, { $setOnInsert: doc }, { upsert: true })
} catch (e) {
  if (e.code !== 11000) throw e     // 11000 = another writer won the race; re-read
}
```

## Bulk writes

```js
await orders.bulkWrite([
  { updateOne: { filter: { _id: a }, update: { $set: { status: "shipped" } } } },
  { updateOne: { filter: { _id: b }, update: { $inc: { version: 1 } } } },
  { deleteOne: { filter: { _id: c } } }
], { ordered: false })
```

- `ordered: false` runs operations in parallel and continues past failures — faster, and it collects
  every error rather than stopping at the first. `ordered: true` stops at the first failure.
- **A bulk write is not a transaction.** Partial application is normal; design the operations to be
  individually idempotent.
- Batch size: a few hundred to a few thousand operations. The wire limit is 100,000 operations and
  the command has a size cap; huge batches also hold resources long enough to affect other traffic.
- Always inspect the result (`writeErrors`, `nModified`) — a bulk write that half-failed returns
  successfully at the transport level.

## Job queue claim

```js
db.jobs.findOneAndUpdate(
  { status: "queued", runAt: { $lte: new Date() } },
  { $set: { status: "running", claimedBy: workerId, claimedAt: new Date() } },
  { sort: { runAt: 1 }, returnDocument: "after" }
)
// Index: { status: 1, runAt: 1 }
```

Atomic claim, no transaction, no double-processing. Add a reaper that returns jobs whose `claimedAt`
is older than the maximum run time back to `queued` — a worker that dies mid-job otherwise strands
its work forever.
