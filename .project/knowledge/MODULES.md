# Modules — Map & Business Rules (AUTHORING GUIDE)

> **Replace this file** with your domain map + the exact edge-case behavior enforced in code.
> This is the doc that makes reviews catch *business* bugs, not just code bugs — for a pharmacy
> app that's prescription/expiry/batch rules; for a POS it's pricing/discount/refund/shift
> rules. When a rule and the code disagree, **the code wins** — fix this doc.

# Modules — Map & Business Rules

> current to {{commit sha / date}}

## Dependency order

*{{diagram or list: which module depends on which; which are leaves; anything event-driven or
middleware-driven that hangs off everything.}}*

| Module | One-liner | Deep doc |
|---|---|---|
| {{inventory}} | {{batch/expiry-tracked stock}} | `../architecture/{{inventory}}.md` |
| {{sales}} | {{POS transactions, shifts, refunds}} | `../architecture/{{sales}}.md` |

*{{plus a routes-at-a-glance line per module if the project is API-shaped.}}*

---

## Business rules (the exact edge-case catalog)

*{{One subsection per module. One bullet per rule — exact, testable, with error
codes/limits/timeouts named. This section is the reviewer's checklist and the planner's
edge-case source. The style that works:}}*

### {{Module A}}
- *{{"Roles are fixed: X > Y > Z. No custom roles."}}*
- *{{"Delete is a soft-delete; a deleted {{thing}} returns 403 (not 404) because …"}}*
- *{{"{{Limit}} is enforced before insert on EVERY {{adding}} path: {{list the paths}}."}}*
- *{{"{{Action}} requires {{condition}}, else 422 `{{ERROR_CODE}}`."}}*

### {{Module B}}
- *{{"State machine: {{a → b → c}}; the {{d}} state does not exist yet."}}*
- *{{"{{Money-state}} moves only from {{verified source}} — never a direct client call."}}*
- *{{"{{Fee/discount}} applies to the NEXT {{invoice/receipt}}, not the current one."}}*

*{{Maintenance rule: every shipped feature appends its new edge cases here (Definition of Done);
every "bug" report gets checked against this list before being fixed — it may be intended
behavior.}}*
