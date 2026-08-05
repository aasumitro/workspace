# MQL — the query language

Reference for reads, updates, and projections. Aggregation pipelines: `aggregation.md`.

## Query operators

| Group | Operators | Notes |
|---|---|---|
| Comparison | `$eq $ne $gt $gte $lt $lte $in $nin` | `$ne` and `$nin` cannot use an index efficiently — they must examine everything not excluded |
| Logical | `$and $or $not $nor` | `$or` can use an index **per branch**; each branch needs its own |
| Element | `$exists $type` | `$exists: false` cannot use a normal index — consider a partial index |
| Array | `$all $elemMatch $size` | `$size` takes no range — precompute a count field if you need `> n` |
| Evaluation | `$regex $expr $mod $jsonSchema $text` | `$expr` compares fields to each other; it is slower and index use is limited |

```js
// Implicit AND across fields
db.orders.find({ status: "paid", total: { $gte: 100 } })

// $in beats a chain of $or on one field
db.orders.find({ status: { $in: ["paid", "shipped"] } })

// Field-to-field comparison needs $expr
db.orders.find({ $expr: { $gt: ["$paidTotal", "$invoiceTotal"] } })
```

## Arrays — the part that surprises people

A query on an array field matches if **any element** matches. Two conditions on the same array
match if *any combination* of elements satisfies them — not necessarily the same element:

```js
// WRONG: matches a doc with items [{sku:"A", qty:1},{sku:"B", qty:9}]
db.orders.find({ "items.sku": "A", "items.qty": { $gte: 5 } })

// RIGHT: both conditions must hold on the SAME element
db.orders.find({ items: { $elemMatch: { sku: "A", qty: { $gte: 5 } } } })
```

`$all` requires every listed value to be present somewhere in the array. Dot-notation into an array
by index (`items.0.sku`) works but couples the query to element order — usually a smell.

## Projection

```js
db.users.find({ orgId }, { name: 1, email: 1 })          // inclusion (+ _id unless excluded)
db.users.find({ orgId }, { passwordHash: 0, tokens: 0 }) // exclusion
db.users.find({ orgId }, { _id: 0, name: 1 })            // _id is the only field mixable
```

Inclusion and exclusion cannot be mixed in one projection (except `_id`). Project narrowly on hot
reads: it cuts network and BSON-decode cost, and it is what makes a **covered query** possible
(`indexing.md`).

Array projections:

```js
{ items: { $slice: 5 } }              // first 5
{ items: { $slice: [10, 5] } }        // skip 10, take 5
{ items: { $elemMatch: { sku: "A" } } } // the first matching element only
```

## Update operators

| Group | Operators |
|---|---|
| Fields | `$set $unset $setOnInsert $rename $inc $mul $min $max $currentDate` |
| Arrays | `$push $addToSet $pop $pull $pullAll` + modifiers `$each $slice $sort $position` |

```js
// Atomic counter — never read-modify-write in application code
db.inventory.updateOne({ _id }, { $inc: { onHand: -qty } })

// Capped, sorted array: keep the 20 most recent events, newest first
db.devices.updateOne({ _id }, {
  $push: { events: { $each: [ev], $sort: { at: -1 }, $slice: 20 } }
})

// Set on insert only — safe upsert defaults
db.counters.updateOne(
  { _id: key },
  { $inc: { seq: 1 }, $setOnInsert: { createdAt: new Date() } },
  { upsert: true }
)
```

`$addToSet` is set-semantics (no duplicates); `$push` always appends. Neither bounds growth — pair
with `$slice` or move to a child collection.

## Updating array elements

```js
// Positional $ — the FIRST element matched by the query filter
db.orders.updateOne(
  { _id, "items.sku": "A" },
  { $set: { "items.$.qty": 5 } }
)

// All elements
db.orders.updateOne({ _id }, { $inc: { "items.$[].version": 1 } })

// Filtered — every element matching the arrayFilters condition
db.orders.updateOne(
  { _id },
  { $set: { "items.$[it].status": "shipped" } },
  { arrayFilters: [{ "it.sku": { $in: ["A", "B"] } }] }
)
```

`$` requires the array field to appear in the query filter. `$[<id>]` with `arrayFilters` is the
general tool — prefer it when updating more than one element or when the filter is not the query.

## Aggregation-pipeline updates

An update may be a pipeline, which unlocks computing a field from other fields in one round trip:

```js
db.invoices.updateOne({ _id }, [
  { $set: { balance: { $subtract: ["$total", "$paid"] },
            status:  { $cond: [{ $gte: ["$paid", "$total"] }, "paid", "open"] },
            updatedAt: "$$NOW" } }
])
```

Only `$set`/`$addFields`, `$unset`, `$replaceRoot`/`$replaceWith`, `$project`, and a few others are
allowed in an update pipeline.

## Find-and-modify

`findOneAndUpdate` / `findOneAndDelete` / `findOneAndReplace` return the document atomically —
the basis for job-queue claims and optimistic concurrency (`query-patterns.md`):

```js
db.jobs.findOneAndUpdate(
  { status: "queued", runAt: { $lte: new Date() } },
  { $set: { status: "running", startedAt: new Date() } },
  { sort: { runAt: 1 }, returnDocument: "after" }
)
```

## Query safety

- Never pass a user-supplied object straight into a filter. `{ email: req.body.email }` becomes
  `{ email: { $ne: null } }` if the body is JSON and unchecked. Cast to the expected primitive
  first, or validate the shape.
- `$where` and `$function` execute JavaScript on the server: slow, unindexable, and a code-execution
  surface. Treat them as forbidden unless there is no alternative and the input is not user data.
- `$regex` with a leading wildcard (`/.*foo/`) cannot use an index. Anchored prefixes (`/^foo/`)
  can. For real search, use a text index or Atlas Search (`performance.md`).
