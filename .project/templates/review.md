---
id: RV-000
title: {{review of what}}
status: draft            # draft | active | blocked | done
updated: {{YYYY-MM-DD}}
links: []                # the TASK/PLAN under review
---

# RV-000 — {{title}}

## Target
{{PLAN-XXX (design review) | TASK-XXX + diff (code review) | document path}}

## Verdict
**{{approve | approve-with-nits | request-changes}}**

{{one-paragraph summary: overall quality, the one thing that matters most}}

## Findings
<!-- one block per finding; delete severities you didn't use -->
### [blocker] {{one-line claim}}
- Where: `{{file:line}}`
- What: {{what is wrong}}
- Why: {{violated convention/ADR/business rule — cite it}}
- Suggestion: {{concrete fix — suggested, not applied}}

### [major] …
### [minor] …
### [nit] …

## Checklist walked
- [ ] Plan conformance (steps landed; deviations justified)
- [ ] Correctness & edge cases (vs modules/README.md)
- [ ] Boundaries (no cross-module imports; no cross-schema FKs; typed contracts; canonical event constants)
- [ ] Security (conventions/security.md)
- [ ] Tests (three layers; regression for fixes; not brittle)
- [ ] Conventions & doc sync (API-doc annotations; i18n; comment rules; KB updated)

## Ship check (pass 2 — only after findings resolve)
- [ ] Checks run THIS session, output seen, clean
- [ ] Work docs closed; knowledge synced; no stale claims left
- [ ] Hygiene: no debug/dead code, no workspace references in comments
- [ ] COMMIT.md written and accurate to the final diff

---
## Comments
{{> [YYYY-MM-DD] …}}
