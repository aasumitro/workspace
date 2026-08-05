# Architecture — Overview (AUTHORING GUIDE)

> **Replace this file** with your project's overview. It is the FIRST doc every agent reads —
> it must let an agent orient in one read: what the product is, how the pieces fit, where the
> code lives, and what state it's in. Aim for 1-3 screens. Skeleton below; the italic notes say
> what to write, then delete them.

# {{Project}} — Project Overview & Architecture

**What:** *{{one paragraph: what the product is, who it serves, what makes its shape special —
e.g. "a pharmacy management app for Indonesian apotek: POS, inventory with batch/expiry
tracking, BPOM compliance reporting"}}*

> current to {{commit sha / date}}

## Core principles

*{{3-7 bullets: the architectural stances that shape everything — auth approach, tenancy model,
monolith vs services, build-vs-buy lines. These feed the Invariants list in `../README.md`.}}*

## Surfaces

*{{one table row per deployable/buildable surface — must match `MANIFEST.yaml → surfaces`:}}*

| Surface | What it is | Stack | Talks to |
|---|---|---|---|
| {{backend}} | {{...}} | {{lang, framework, DB, queue}} | {{...}} |
| {{web}} | {{...}} | {{...}} | {{...}} |

## Repository layout

*{{annotated tree of `project/<repo>` — top 2 levels, one comment per entry. Agents navigate by
this; keep it exact.}}*

## Domains / modules

*{{table: module → responsibility → depends on. Then state the boundary rules: how modules may
and may not communicate (imports? events? shared DB?). Deep per-module docs go in
`../MODULES.md` and per-subsystem files here.}}*

## How the pieces communicate

*{{sync paths (HTTP, RPC, interfaces) and async paths (queue/events) — with the actual
names/topics. Include the request path: what middleware/guards run, in order, before a handler.}}*

## System flow diagram

*{{one ASCII diagram of the whole system — clients, services, stores, third parties.}}*

## Feature status

*{{what's built vs in progress vs known-gap — honest, short. Details in `../roadmap/README.md`.}}*

---

## Also create in this folder (one file per surface/subsystem)

- `backend.md` / `frontend.md` — per-surface deep docs (skeletons provided in this folder).
- One `<subsystem>.md` per cross-cutting concern big enough to own a doc (billing, messaging,
  storage, notifications, …). Structure each like the surface docs: what it owns → key behaviors
  (load-bearing, gotchas included) → its interfaces/events.
