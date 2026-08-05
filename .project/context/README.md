# context/ — per-surface reading profiles

`AGENTS.md` §6 is the generic answer to "what do I read for this surface" — it works for any
Workspace project. A context profile is *this project's own* answer: the exact `knowledge/` docs a
surface needs, including anything project-specific the generic table can't know about (e.g. "the
billing surface always needs `conventions/security.md` too, because it's the one surface that
touches money").

## Format

One YAML file per surface or subsystem, named to match its `knowledge/architecture/` doc:

```yaml
# backend.yaml — context profile for backend/API work
required:
  - architecture/backend.md
  - conventions/api.md
optional:
  - conventions/security.md
```

Paths are relative to `.project/knowledge/`. `required:` is read before writing any code on that
surface — nothing more. `optional:` is read only if the task actually touches that concern (auth,
migrations, i18n, …). `python .project/scripts/check.py` fails if a listed path doesn't exist, so a
profile can't silently point at a doc that got renamed or deleted.

## Using one

Touching a surface that has a profile replaces the lookup in `AGENTS.md` §6 for that surface: read
exactly the `required:` list, then `optional:` entries as the task needs them. No profile for the
surface → fall back to §6's generic table.

## Shipped examples

`.project/context/frontend.yaml` and `.project/context/backend.yaml` are starting points, matching
the two example surfaces `MANIFEST.yaml` ships with. Once real surfaces are named in
`MANIFEST.yaml → repos → surfaces`, rename these to match, trim or extend the lists to what the
project actually needs, and add one per additional surface or subsystem. Delete what doesn't apply
— an unused profile is a doc-load with no behavioral gain, exactly what `AGENTS.md` §6 warns
against.
