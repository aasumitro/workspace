# Conventions — User Experience (AUTHORING GUIDE)

> **Replace this file** with the product-behavior rules the UI must express, independent of which
> component renders them. UI mechanics live in `user-interface.md`; underlying business rules in
> `../MODULES.md`. These generic sections survive most projects — keep what fits, make
> each concrete with YOUR patterns.

# Conventions — User Experience

> current to {{commit sha / date}}

## The four states — every data surface has all of them
*{{your loading pattern (skeletons? spinners?) · empty state (with a next action) · error state
(+retry, connection-vs-server distinction) · success/feedback pattern (toasts? inline?).}}*

## Permissions UX
*{{how role/plan-gated features appear: hidden vs locked-with-explainer? Pick ONE policy, state
its exceptions (e.g. a billing-blocked account hides operational pages entirely).}}*

## Language & locale
*{{supported languages + the "both at introduction time" rule · which locale wins where
(user preference vs tenant locale — incl. emails/documents) · timezone handling and the
"editable in exactly one place" rule.}}*

## Destructive & high-stakes flows
*{{confirm patterns (enumerate consequences, type-to-confirm for irreversible) · soft-delete
surfacing ("can be restored" honesty) · undo pattern · step-up auth (MFA) on which actions.}}*

## Preview-before-commit
*{{the flows that show consequences before committing (price previews, dry-run imports,
join-previews) — and the rule that new flows of this shape follow the pattern.}}*

## Honest, accessible interfaces
*{{relative-time + parsed labels over raw ISO/UA · screen-reader announcements on errors ·
touch-target minimums · keyboard shortcuts and their one-owner-per-context rule.}}*

## Notifications UX (if applicable)
*{{opt-out model (per-user? per-tenant?) · grouping/categorization · deep-link rules incl.
recipients who can't access the target page.}}*
