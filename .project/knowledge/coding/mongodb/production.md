# Production Practices

Running MongoDB where losing data is not an option.

## Deployment baseline

- **Always a replica set**, never a standalone — even for one node in development. Transactions,
  change streams, retryable writes, and `w: "majority"` all require it, so a standalone development
  server means those paths are never exercised until production.
- Three data-bearing members minimum for a real majority. Two members plus an arbiter can accept
  writes it cannot durably keep — avoid arbiters in any deployment that stores something valuable.
- Enable authentication and TLS from the first day. A MongoDB reachable without credentials is
  found by scanners in hours.
- Pin the driver's server API version (`{ serverApi: { version: '1' } }`) so a server upgrade cannot
  change behavior underneath the application.

## Connections

One client instance per process, reused for the process's lifetime. Set explicitly:

| Option | Guidance |
|---|---|
| `maxPoolSize` | Total across all instances must stay well under the server limit |
| `minPoolSize` | Small; avoids handshake latency on the first requests after idle |
| `maxIdleTimeMS` | Recycle idle connections behind a load balancer |
| `serverSelectionTimeoutMS` | Fail fast (a few seconds) — do not let requests pile up during an election |
| `connectTimeoutMS` / `socketTimeoutMS` | Bounded; an unbounded socket timeout hides a dead node |
| `retryWrites` / `retryReads` | Leave enabled (the default) |
| `compressors` | `zstd` or `snappy` pays for itself on large result sets |

Store the connection string in an environment variable, never in the repository. Credentials in a
URI end up in logs and stack traces — redact the URI before logging it, always.

## Failover behavior

A primary election takes seconds, during which writes fail. The application must survive it:

- Retryable writes cover single-document operations automatically. `updateMany` and `deleteMany` are
  **not** retryable — batch them into retryable single operations, or make the whole job idempotent
  and re-runnable.
- `serverSelectionTimeoutMS` bounds how long a request waits for a new primary. Set it below the
  request's own timeout so failures are clean rather than cascading.
- Test a failover. `rs.stepDown()` in a staging environment reveals every code path that assumed a
  primary is always available.

## Migrations and backfills

Schema changes are code, versioned and applied in order (`repository-patterns.md`). Backfills are
where production incidents come from.

**Never run `updateMany` across a large collection.** It holds resources, is not retryable, and a
failover leaves it half-applied with no record of where it stopped.

```js
// Batched, resumable, throttled
let lastId = null
for (;;) {
  const batch = await col.find(
    { schemaVersion: { $lt: 2 }, ...(lastId ? { _id: { $gt: lastId } } : {}) },
    { projection: { _id: 1 } }
  ).sort({ _id: 1 }).limit(1000).toArray()

  if (batch.length === 0) break

  await col.bulkWrite(batch.map(d => ({
    updateOne: {
      filter: { _id: d._id, schemaVersion: { $lt: 2 } },   // idempotent
      update: { $set: { schemaVersion: 2, /* ... */ } }
    }
  })), { ordered: false })

  lastId = batch[batch.length - 1]._id
  await sleep(50)                                          // leave headroom for real traffic
}
```

Every backfill is: batched by `_id`, idempotent per document, resumable from the last processed
`_id`, and throttled. Log progress so an interrupted run can be resumed rather than restarted.

**Expand and contract**, always in three deploys:

1. Add the new field, write both shapes, read the old one. Backfill.
2. Read the new field, keep writing both.
3. Stop writing the old field, drop it, tighten the validator.

Collapsing these into one deploy is how a rollback becomes impossible.

## Indexes in production

Build with a rolling procedure on a replica set, and always name indexes explicitly. Create the
index *before* the code that depends on it ships. Verify with `$indexStats` a week later that it is
actually used — an index nobody uses is a write tax paid forever (`indexing.md`).

## Backups and recovery

- Point-in-time recovery via oplog or a managed snapshot service. Snapshots alone lose everything
  since the snapshot.
- **A backup that has never been restored is a hypothesis.** Restore to a scratch environment on a
  schedule and record the actual restore time — that number is your real RTO.
- Know and write down the RPO (how much data you can lose) and RTO (how long recovery takes). If
  nobody has decided them, the answer is whatever the infrastructure happens to do.
- Guard against the failure backups do not cover: a bad migration replicates instantly to every
  member. Oplog-based PITR is the only defense.

## Monitoring

| Signal | Watch for |
|---|---|
| Replication lag | Seconds of lag makes secondary reads incorrect, not just slow |
| WiredTiger cache eviction / dirty bytes | Working set exceeding RAM |
| Opcounters and queue depth | Load shape changes before latency does |
| Slow query log (`slowms`) | New slow queries after every deploy |
| Connections current vs available | Pool sizing errors and connection leaks |
| Oplog window | Must exceed the longest expected secondary downtime, or resync is required |
| Disk usage and IOPS | Fragmentation and growth trends |

Alert on replication lag, oplog window, and connection saturation. Those three predict outages;
CPU rarely does.

## Data lifecycle

- **TTL indexes** for anything with a natural expiry — sessions, tokens, ephemeral events. The
  background remover runs about every 60 seconds, so expiry is approximate; never rely on it for a
  security boundary.
- **Archive cold data** out of hot collections rather than letting them grow forever. `$out` or
  `$merge` into an archive collection, then delete in batches. Reads across both use `$unionWith`.
- **Deletes do not return disk to the filesystem** — WiredTiger reuses the space internally.
  Reclaiming it requires `compact` (blocking, on a secondary) or an initial resync. Plan capacity
  on data written, not data retained.

## Security

- Least-privilege roles per application. The application user needs `readWrite` on its own database
  — never `root`, never cluster administration.
- Separate credentials for migrations and for the application runtime, so the runtime cannot alter
  schema or drop collections.
- Field-level encryption or Queryable Encryption for regulated data — decide at design time, since
  encrypted fields have restricted query capability.
- Network: private networking or IP allowlist. Never expose the port publicly, whatever the
  authentication.
- Never log a full connection string, a query containing personal data, or a document that carries
  secrets (`../../conventions/security.md`).
