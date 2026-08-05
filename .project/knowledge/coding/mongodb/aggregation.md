# Aggregation

The pipeline is MongoDB's real query language for anything beyond a single-collection lookup. It is
also where most production slowdowns are born, because a pipeline that starts wrong cannot recover.

## The rule that governs every pipeline

**Filter first, shrink second, join last.** `$match` and `$sort` before anything else so they can
use an index; `$project` away fields you do not need before `$lookup` or `$group`; `$lookup` on the
smallest possible input.

Only the stages at the *head* of a pipeline can use an index. Once a `$group`, `$unwind`, or
`$project` has run, everything after it is working in memory.

```js
db.orders.aggregate([
  { $match: { orgId, createdAt: { $gte: from, $lt: to } } },  // indexed, cuts the input
  { $project: { customerId: 1, total: 1 } },                  // shrink before grouping
  { $group: { _id: "$customerId", spend: { $sum: "$total" }, orders: { $sum: 1 } } },
  { $match: { spend: { $gte: 1000 } } },                      // filter after grouping — unavoidable
  { $sort: { spend: -1 } },
  { $limit: 20 }
])
```

## Stages worth knowing

| Stage | Does | Watch for |
|---|---|---|
| `$match` | Filter | Put it first; it is the only stage that can use an index freely |
| `$project` / `$set` / `$unset` | Reshape | `$set` (alias `$addFields`) adds without dropping the rest |
| `$group` | Aggregate | `_id: null` groups everything; 100 MB memory limit per stage |
| `$sort` | Order | Uses an index only at the head; otherwise 100 MB in-memory limit |
| `$limit` / `$skip` | Window | `$sort` + `$limit` together is optimized into a top-k scan |
| `$lookup` | Left outer join | The expensive one — see below |
| `$unwind` | Array → documents | Multiplies document count; `preserveNullAndEmptyArrays` matters |
| `$facet` | Several pipelines over one input | The clean way to get results and a count in one round trip |
| `$unionWith` | Concatenate another collection | Useful for archive + live queries |
| `$setWindowFields` | Running totals, rank, moving averages | Replaces most self-joins |
| `$merge` / `$out` | Write results to a collection | `$merge` can incrementally update; `$out` replaces wholesale |
| `$count` | Count documents | Cheaper than `$group` when you only need a number |

## `$lookup` — the join, and its cost

```js
{ $lookup: {
    from: "users",
    localField: "customerId",
    foreignField: "_id",
    as: "customer"
} }
```

- The foreign collection **must have an index on `foreignField`**, or this is a collection scan per
  input document. This is the single most common cause of a pipeline that "works in dev".
- `as` always produces an array — follow with `$unwind` (or `{ $first: "$customer" }`) when the
  relationship is to-one.
- The sub-pipeline form lets you filter and project the foreign side before it is materialized:

```js
{ $lookup: {
    from: "orders",
    let: { uid: "$_id" },
    pipeline: [
      { $match: { $expr: { $eq: ["$customerId", "$$uid"] }, status: "paid" } },
      { $project: { total: 1, createdAt: 1 } },
      { $sort: { createdAt: -1 } },
      { $limit: 5 }
    ],
    as: "recentOrders"
} }
```

**Before writing a `$lookup`, ask whether an extended reference belongs in the schema instead**
(`schema-design.md`). A join on every read of a hot endpoint is usually a modeling decision that was
deferred rather than made.

## Results plus total count, in one pass

```js
db.orders.aggregate([
  { $match: { orgId, status: "paid" } },
  { $facet: {
      rows:  [ { $sort: { createdAt: -1 } }, { $limit: 20 }, { $project: { total: 1, createdAt: 1 } } ],
      total: [ { $count: "n" } ]
  } }
])
```

Each `$facet` branch shares the input but has its own 100 MB budget. Note that `$facet` blocks index
use for the branches — for large collections, prefer a separate `countDocuments` with the same
filter, or an approximate count.

## Window functions

`$setWindowFields` handles running totals, ranking, and gap analysis without a self-join:

```js
{ $setWindowFields: {
    partitionBy: "$customerId",
    sortBy: { createdAt: 1 },
    output: {
      runningSpend: { $sum: "$total", window: { documents: ["unbounded", "current"] } },
      rank:         { $rank: {} }
    }
} }
```

## Memory and disk

- Each blocking stage (`$group`, `$sort`, `$bucket`, `$facet`) has a **100 MB** memory limit.
- Exceeding it errors unless the aggregation runs with `allowDiskUse: true` — which is a correctness
  escape hatch, not a performance setting. A pipeline that needs disk on ordinary data is a pipeline
  that filtered too late.
- `$sort` immediately after `$match` on an indexed field avoids the limit entirely by reading in
  index order.

## Explaining a pipeline

```js
db.orders.explain("executionStats").aggregate([...])
```

Read the first stage: if it is not `IXSCAN`, nothing downstream can save it. Then check whether the
optimizer coalesced your stages — MongoDB moves `$match` earlier and merges `$sort` + `$limit`
automatically, so the executed plan may differ from what you wrote. Trust the plan, not the source.

## Materializing expensive results

For dashboards and reports that tolerate staleness, compute on a schedule and read the result:

```js
{ $merge: { into: "daily_revenue", on: ["orgId", "day"], whenMatched: "replace", whenNotMatched: "insert" } }
```

Cheaper, more predictable, and it moves the cost off the request path. Record the freshness
guarantee wherever the collection is documented — a materialized view with an undocumented lag is a
bug generator.
