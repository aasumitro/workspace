# Conventions — Database (AUTHORING GUIDE)

> **Replace this file** with the schema reference + migration rules — what the DATABASE role and
> any schema-touching plan builds on.

# Conventions — Database

> current to {{commit sha / date}}. Migrations in `{{path}}`.

## Engine & access
*{{DB engine + version · access layer (ORM? raw SQL? query builder?) · connection/pool setup ·
the data-ownership model (single schema? schema-per-module? DB-per-service?) and its boundary
rule (e.g. "cross-module references are plain IDs validated in code, never FKs").}}*

## Migrations
*{{tool + commands (create/up/down/version) · file naming · the team's convention for editing vs
appending during dev · rules for data migrations (idempotent, chunked, reversible).}}*

## Schemas & tables
*{{per schema/domain: table → columns that matter → notable constraints/indexes. Dense table
form. Include the "which table/column names differ from intuition" mapping if any.}}*

## Modeling rules
*{{JSON vs columns policy · enum handling (CHECK constraints?) · soft-delete pattern · timestamp
conventions · ID strategy (UUIDv7? serial?) · personal-data minimization + retention/cleanup
ownership ("who sweeps expired rows" — name the mechanism).}}*

## Seed / reference data
*{{what's seeded, why, and how it's maintained (migration? admin tool?).}}*

## Security at the DB layer
*{{RLS? per-service credentials? encryption at rest expectations? — or explicitly "service-layer
scoping only".}}*
