# coding/ — language style guides

One folder per language. Agents load the matching guide whenever they touch that language — the
trigger table is in `AGENTS.md` §6. All guides are **general-purpose and project-independent**;
per-project rules layer on top in `../conventions/`.

| Folder | Language | Current to | Files |
|---|---|---|---|
| `go/` | Go | **Go 1.26** | README + 10 guides (version-gated `modern-syntax` 1.0→1.26, patterns, errors, context, concurrency, slices/maps, generics, testing, performance, pitfalls) |
| `rust/` | Rust | **Rust 1.97 · Edition 2024** | README + 8 guides (version-gated `modern-syntax`, patterns, ownership/borrowing, errors, traits/generics, concurrency/async, testing, performance, pitfalls) |
| `py/` | Python | **Python 3.14** (incl. free-threading, t-strings, PEP 695) | README + 7 guides (version-gated `modern-syntax` 3.10→3.14, patterns, typing, errors, concurrency, testing, performance, pitfalls) |
| `ts/` | TypeScript | **TS 6 / 7** (native compiler era) | README + 7 guides (version-gated `modern-syntax` 4.9→7, patterns, types, errors, async, testing, tooling & 6→7 migration, pitfalls) |
| `sql/` | SQL | **PostgreSQL 18 · SQLite 3** (3.35+ baseline) | README + 8 guides (style, schema design, query patterns, indexing, migrations, postgresql, sqlite, pitfalls) |
| `mongodb/` | MongoDB | **MongoDB 8.x** (7.0 floor) | README + 10 guides (MQL, schema design, indexing, aggregation, transactions, query patterns, repository patterns, performance, production, pitfalls) |
| `tw/` | Tailwind CSS |  **v4.3** | README + 6 guides (modern-syntax, variants & states, patterns, best practices, tooling & migration, pitfalls) |

## Shared conventions across all guides

- **Version-gating**: each language's `modern-syntax.md` is ordered by version — use features up
  to the project's declared floor (go.mod / rust-toolchain / requires-python / package.json),
  nothing past it. *Stop reading at your project's version boundary.*
- Every folder README carries "the five rules that outrank everything" — the non-negotiables a
  reviewer cites without opening the deep docs.
- `pitfalls.md` per language is the review/debug checklist — grown every time something bites.
- Dense, reference-first, example-backed: these docs load into model context; every sentence
  costs budget.

## Per-project setup

Keep the folders matching your stack; delete the rest; add missing languages by cloning the
structure (README + modern-syntax + patterns + error-handling + testing + pitfalls is the
minimum viable set). House rule for growth: when a review repeatedly flags the same
language-level mistake, that rule graduates into the guide.
