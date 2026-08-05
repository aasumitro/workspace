# Transactions and Consistency

Multi-document transactions exist and work. They are also the most over-reached-for tool in
MongoDB: they cost more here than in a relational engine, and most cases that appear to need one
are a schema that put the unit of consistency in the wrong place.

## Try these first, in order

1. **One document.** A single-document update is atomic across all its fields and arrays, with no
   transaction. If two facts must always agree, the strongest design puts them in one document.
2. **`findOneAndUpdate` with a guard condition.** Claim-check semantics — "decrement only if enough
   stock exists" — in a single atomic operation:

   ```js
   db.inventory.findOneAndUpdate(
     { _id: sku, onHand: { $gte: qty } },     // the guard IS the concurrency control
     { $inc: { onHand: -qty }, $set: { updatedAt: new Date() } },
     { returnDocument: "after" }
   )
   // null result = the guard failed; no write happened
   ```
3. **Optimistic concurrency with a version field** (`query-patterns.md`) — for read-modify-write
   over a single document.
4. **Idempotent operations plus a retry.** Many "transactional" flows only need to be safely
   repeatable, not atomic.
5. **Only then, a transaction.**

## Requirements and limits

- Replica set or sharded cluster. **Transactions do not exist on a standalone server** — which is
  why they work in production and fail on a developer's single-node install. Run a single-node
  replica set locally so environments match.
- Default lifetime: **60 seconds** (`transactionLifetimeLimitSeconds`). A transaction that outlives
  it aborts. Never hold one across a network call to another service.
- All operations must go through the same session, and the session must be passed to *every* call
  inside the transaction. A missed `session` argument silently executes outside the transaction —
  the most common transaction bug there is.
- The transaction takes locks; long transactions block others and grow the WiredTiger cache.

## Shape

```js
const session = client.startSession()
try {
  await session.withTransaction(async () => {
    const from = await accounts.findOneAndUpdate(
      { _id: fromId, balance: { $gte: amount } },
      { $inc: { balance: -amount } },
      { session, returnDocument: "after" }
    )
    if (!from) throw new Error("insufficient funds")

    await accounts.updateOne({ _id: toId }, { $inc: { balance: amount } }, { session })
    await ledger.insertOne({ fromId, toId, amount, at: new Date() }, { session })
  }, {
    readConcern:  { level: "snapshot" },
    writeConcern: { w: "majority" },
    readPreference: "primary"
  })
} finally {
  await session.endSession()
}
```

`withTransaction` handles the retry loop for `TransientTransactionError` and
`UnknownTransactionCommitResult` for you. **Use it rather than manual
`startTransaction`/`commitTransaction`** — hand-rolled loops almost always miss one of the two
retryable classes.

**The callback must be idempotent.** It can and will run more than once.

## Read and write concerns

| Concern | Setting | Means |
|---|---|---|
| `writeConcern` | `w: 1` | Acknowledged by the primary only — lost on failover |
| | `w: "majority"` | Acknowledged by a majority; survives failover. **The default choice for anything you cannot lose** |
| | `journal: true` | Also flushed to disk |
| `readConcern` | `local` | Whatever the node has — may be rolled back |
| | `majority` | Only data acknowledged by a majority; never rolled back |
| | `snapshot` | A consistent point-in-time view; transactions only |
| `readPreference` | `primary` | Correct by default |
| | `secondaryPreferred` | Faster, **stale by replication lag** — never for read-your-writes |

The dangerous combination is `w: 1` plus `readPreference: secondaryPreferred`: writes that can
vanish, read from a node that may not have them yet. Choose both deliberately and write the choice
down in `../../conventions/database.md`.

## Causal consistency

Inside a session, reads see that session's own prior writes even across nodes — the fix for
"created it, immediately read it back, got nothing" when reading from secondaries:

```js
const session = client.startSession({ causalConsistency: true })
await orders.insertOne(doc, { session })
await orders.findOne({ _id: doc._id }, { session })   // guaranteed visible
```

Sessions are causally consistent by default in modern drivers. The guarantee holds **only for
operations passed that session** — this is another place a forgotten `session` argument silently
removes the property you were relying on.

## Retryable writes and reads

Modern drivers enable both by default. A single write that fails on a transient network error or a
primary election is retried once, safely, using an operation ID that prevents duplication.

This covers `insertOne`, `updateOne`, `deleteOne`, `findOneAndX`. It does **not** cover multi-document
`updateMany` / `deleteMany` — those are not retryable, and a partial `updateMany` interrupted by a
failover has applied to some documents and not others. Batch such operations yourself (`production.md`).

## Rules

- **Keep transactions short and local.** No HTTP calls, no queue publishes, no waiting inside one.
- **Publish events after commit**, never inside — a rolled-back transaction that already emitted an
  event has told the rest of the system a lie. If the publish must be reliable, write an outbox
  document in the same transaction and let a worker publish it.
- **Never grow a transaction to cover a design problem.** Three collections that must always agree
  are usually one document that got split for no reason.
- **Test transaction paths against a replica set**, including a forced failover. Code that only ever
  ran on a healthy primary has never exercised its retry path.
