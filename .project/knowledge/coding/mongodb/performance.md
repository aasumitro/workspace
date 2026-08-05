# Performance

Diagnosis order: **measure → find the query → read its plan → fix the index or the schema.** Almost
every real MongoDB performance problem is one of four things: a missing index, a wrong compound
index order, a working set that no longer fits in RAM, or a schema that forces a join or a scan.

## The working set

MongoDB (WiredTiger) keeps recently used documents and index pages in a cache — by default about
half of available RAM. Performance is excellent while the **working set** — the documents and index
entries your queries actually touch — fits in that cache, and degrades sharply when it does not,
because every miss becomes a disk read.

Symptoms of a working set that has outgrown RAM: latency that got worse without a code change,
cache eviction rising, disk read IOPS climbing, and queries that are fast in isolation but slow
under concurrency.

Fixes, in order of preference: index only what you query (every unused index competes for the same
cache), project fewer fields, archive cold data out of the hot collection, then add RAM, then shard.

## Finding the slow query

**Profiler** — the first tool, always:

```js
db.setProfilingLevel(1, { slowms: 100 })   // log operations slower than 100ms
db.system.profile.find().sort({ ts: -1 }).limit(20)
db.setProfilingLevel(0)                    // turn it off when done
```

Profiling level 2 captures everything and is expensive — use it briefly, in development.

**Current operations** — for something slow right now:

```js
db.currentOp({ "secs_running": { $gte: 3 }, "op": { $ne: "none" } })
db.killOp(opid)   // only with a human's agreement
```

**`$indexStats`** — which indexes are actually used:

```js
db.orders.aggregate([{ $indexStats: {} }])
```

**Server status** — cache pressure, connections, queues:

```js
db.serverStatus().wiredTiger.cache
db.serverStatus().connections
db.serverStatus().globalLock.currentQueue
```

## Reading the plan

`explain("executionStats")` on the slow query, then the ratio that matters:

```
totalKeysExamined : totalDocsExamined : nReturned
```

- `1000 : 1000 : 10` — the index locates but does not filter. The compound order is wrong (ESR,
  `indexing.md`), or a low-selectivity field leads.
- `0 : 50000 : 10` — `COLLSCAN`. No usable index at all.
- `10 : 10 : 10` — correct.
- `10 : 0 : 10` — covered query; the index answered without touching documents.

A `SORT` stage in the plan means the sort happened in memory. Fix the index so the sort is served by
index order, or accept the cost knowingly for small result sets.

## The usual causes, in the order they appear

1. **Missing index on a `$lookup` foreign field.** A pipeline that scans the joined collection once
   per input document. Check every `$lookup` before anything else (`aggregation.md`).
2. **Wrong compound order.** Index exists, is used, and still examines thousands of keys.
3. **Unbounded result sets.** A query with no `limit` that returned 40 documents in development and
   returns 400,000 in production. Every list endpoint needs a hard cap.
4. **`skip`-based pagination** degrading linearly with page depth (`query-patterns.md`).
5. **N+1 in the application** — a loop issuing one `findOne` per item. Replace with a single
   `$in` query and a map lookup in memory.
6. **Oversized documents** on a hot path — reading a 2 MB document to display three fields. Project
   narrowly, or use the subset pattern.
7. **Write amplification** — a large document rewritten on every small update; an array that grows
   without bound.
8. **Too many indexes.** Every write updates every matching index, and every index competes for
   cache. An index with zero `$indexStats` accesses is pure cost.

## Read and write cost levers

| Lever | Effect | Cost |
|---|---|---|
| Narrow projection | Less network, less BSON decoding, enables covered queries | None — do it always on hot paths |
| `readPreference: secondaryPreferred` | Spreads read load | **Stale reads.** Never for read-your-writes |
| `w: 1` instead of `w: "majority"` | Faster acknowledgement | Writes can be lost on failover. A correctness decision, not a tuning knob |
| `$merge` materialized views | Moves aggregation cost off the request path | Staleness that must be documented |
| Batch reads with `$in` | Removes N+1 round trips | Cap the batch size |
| `allowDiskUse` | Lets a large aggregation complete | Slow. Signals the pipeline filtered too late |

## Connection pooling

The pool is per client instance, and **one client instance per process** is the rule — creating a
client per request exhausts connections and pays TCP and TLS handshakes on every call.

`maxPoolSize` defaults to 100. Size it to what the server can serve: total connections across all
application instances must stay well under the server's connection limit. Too large a pool moves
queueing from the application into the database, where it is harder to see and affects everyone.

Watch `connections.current` against `connections.available`, and watch pool checkout wait time in
the driver's metrics — rising checkout time means the pool, not the database, is the bottleneck.

## Text search

The built-in text index handles keyword lookup: one text index per collection, no relevance tuning
worth the name, no fuzzy matching, no faceting. It is adequate for "find the product by name" and
inadequate for a real search feature — reach for Atlas Search (`$search`) or a dedicated engine
before contorting a text index into something it is not.

`$regex` is not a search strategy: anchored patterns (`/^foo/`) can use an index, everything else
scans.

## Sharding — the last resort

Sharding solves one problem: a working set or write throughput that cannot fit on one primary. It
costs operational complexity, cross-shard query latency, and a **shard key you can never change on
an existing collection without resharding**.

Before sharding, exhaust: indexing, schema shape, archiving cold data, and vertical scaling.

If you do shard, the shard key decides everything:

- It must appear in the majority of queries, or every query becomes a scatter-gather.
- It must distribute writes. A monotonically increasing key (timestamp, `ObjectId`) sends every
  insert to one shard — hashed or compound keys avoid the hotspot.
- It must have high cardinality; low cardinality produces jumbo chunks that cannot split.

Record the choice and its reasoning as an ADR. It is one of the least reversible decisions in the
system.
