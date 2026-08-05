# Pitfalls — the review and debug checklist

What actually bites, roughly in order of how often. Use this as a checklist when reviewing any
MongoDB change.

## Query correctness

**`null` matches missing.** `{ field: null }` matches documents where the field is `null` **and**
documents where it is absent. These are different states and often mean different things.

```js
{ field: null }                    // null OR missing
{ field: { $type: "null" } }       // explicitly null only
{ field: { $exists: false } }      // missing only
{ field: { $ne: null } }           // present and not null
```

**Type bracketing.** Comparisons only match values of the same BSON type. `{ age: { $gt: 18 } }`
never matches `age: "25"`. A collection with mixed types silently returns partial results — this is
why `$jsonSchema` validation matters.

**Array conditions match across elements.** Two predicates on the same array field can be satisfied
by two different elements. Use `$elemMatch` when both must hold on one element (`mql.md`). This is
the most common *silent* correctness bug in MQL.

**`$ne` and `$nin` cannot use an index efficiently.** They must consider everything not excluded.
Rewrite as a positive predicate where possible.

**`$or` needs an index per branch.** One unindexed branch turns the whole query into a scan.

**Case sensitivity.** Queries are case- and diacritic-sensitive by default. A collation index makes
case-insensitive matching indexable — but the query must specify the *same* collation or it will
not use the index (`indexing.md`).

**`$regex` with a leading wildcard cannot use an index.** `/^prefix/` can; `/.*substring/` cannot.

**Empty filter deletes everything.** `deleteMany({})` and `updateMany({}, ...)` are valid. Guard
against an undefined variable collapsing a filter to `{}` — check the filter is non-empty before any
bulk mutation.

## NoSQL injection

Passing a user-supplied object into a filter lets the user supply operators:

```js
// Body: { "email": { "$ne": null } }  → matches the first user in the collection
db.users.findOne({ email: req.body.email, passwordHash: hash })
```

Cast to the expected primitive (`String(req.body.email)`) or validate the shape before it reaches a
query. `$where` and `$function` execute server-side JavaScript — treat both as forbidden.

## Schema and data

**Unbounded arrays.** The document eventually exceeds 16 MB, and long before that every update
rewrites the whole document. Bound with `$slice` or move to a child collection.

**Doubles for money.** `0.1 + 0.2` is wrong in BSON too. `Decimal128`, always, end to end — a
`Decimal128` field read into a language `float` loses the guarantee at the boundary.

**Dates as strings.** They sort lexically, break range queries, and carry no timezone. BSON `Date`,
UTC.

**Deep nesting.** Beyond two or three levels, updates need `arrayFilters` gymnastics and queries
become unreadable. Flatten or split.

**Missing `schemaVersion`.** Without it, a live migration has no way to tell which shape a document
is in, and the read path cannot be safely simplified later.

## Indexes

**No index on a `$lookup` foreign field** — a scan of the joined collection per input document. The
single most expensive omission in aggregation.

**Wrong compound order.** ESR: equality, sort, range. A range field before the sort field forces an
in-memory sort.

**Assuming a prefix works in reverse.** `{a, b, c}` does not serve a query on `b`.

**More than one array field in a compound index** — rejected at creation, and only discovered when
the data arrives.

**Unique index added to a collection that already has duplicates** — the build fails, sometimes
after a long run. Check for duplicates first with a `$group` on the key.

**Building an index on a hot collection without a rolling procedure.**

**Indexes created in a shell and never recorded.** They vanish on the next environment rebuild.
Index definitions live in the repository (`repository-patterns.md`).

## Concurrency

**Read-modify-write without a version or a guard.** Two concurrent updates, one silently lost. No
error, no log line (`query-patterns.md`).

**Upsert without a unique index.** Concurrent upserts that both miss both insert.

**Forgetting `session` on an operation inside a transaction.** It executes outside the transaction
and neither the driver nor the server complains.

**Assuming `updateMany` is atomic.** It is not: other readers see partially applied results, and a
failover can leave it half-done — it is not retryable.

**Assuming `bulkWrite` is a transaction.** It is not. Design operations to be individually
idempotent.

## Aggregation

**`$match` placed after `$group` or `$project`** — the index is gone by then.

**`$unwind` before `$match`** — multiplies the document count, then filters. Filter first.

**100 MB stage limit** hit by `$group` or `$sort` on unfiltered input. `allowDiskUse` makes it
complete, not correct — the pipeline filtered too late.

**`$lookup` result is always an array**, even for a to-one relationship.

**`$facet` blocks index use** for its branches. For large collections, run the count separately.

## Operations

**Standalone server in development, replica set in production.** Transactions, change streams, and
retryable writes are never exercised locally, then fail on first contact with production semantics.

**`readPreference: secondaryPreferred` combined with read-your-writes.** Replication lag makes the
write invisible to the read that follows it. Use causal consistency or read from the primary.

**`w: 1` on data that matters.** Acknowledged by the primary alone; lost if that primary fails
before replication.

**A client instance created per request.** Connection exhaustion plus a handshake on every call.

**`updateMany` used as a backfill on a large collection.** Batch it (`production.md`).

**Deleted data not returning disk space.** WiredTiger reuses it internally; the filesystem does not
shrink without `compact` or a resync.

**Logging a connection string or a document containing personal data.** Redact before logging,
always.

## Review checklist

- [ ] Every new query has an index, and `explain` was read — `keysExamined : nReturned` near 1:1
- [ ] Compound index order follows ESR; no second array field
- [ ] `$lookup` foreign fields are indexed
- [ ] Tenant scope is in the query, applied inside the repository
- [ ] Filters cannot be collapsed to `{}` by an undefined variable
- [ ] No user-supplied object reaches a filter uncast
- [ ] Read-modify-write is guarded by a version or a filter condition
- [ ] Upserts are backed by a unique index and handle error 11000
- [ ] Arrays are bounded; documents cannot grow without limit
- [ ] Money is `Decimal128`; dates are BSON `Date` in UTC
- [ ] Write concern is deliberate for anything that must not be lost
- [ ] Migrations are batched, idempotent, and resumable; the down path is real or documented as
      one-way
- [ ] New collections have `$jsonSchema` validation and a documented shape in
      `../../conventions/database.md`
