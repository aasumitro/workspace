# Conventions — Security (AUTHORING GUIDE)

> **Replace this file** with the consolidated security reference: every boundary and the
> mechanism that protects it. The SECURITY role treats this doc as the authority — keep it
> complete, or its reviews go blind.

# Conventions — Security

> current to {{commit sha / date}}

## Authentication (identity)
*{{who issues identity (own auth? Supabase/Auth0/Firebase?) · token type + validation (JWKS?
sessions?) · algorithm/issuer/audience pinning · how claims reach handlers · session
revocation/logout-everywhere mechanism · MFA model and which routes it gates, incl. the
fail-open/fail-closed choice on lookup errors.}}*

## Authorization
*{{the role/permission model (exact hierarchy) · where it's enforced (middleware? per-handler?) ·
caching + invalidation of role lookups · tenant scoping (how a request is bound to its
tenant/org and what happens for missing/deleted tenants) · client-side authz is UI-only.}}*

## Secrets & configuration
*{{where secrets live (env files, vault) · loading pattern · the "never hardcode/log/print"
rule · graceful-degrade behavior per optional integration (unset = skip? warn? fail?).}}*

## Webhooks & third-party callbacks
*{{per integration: verification mechanism (HMAC/token), replay protection, dedup, and the rule
about what state changes may only happen from a verified callback.}}*

## Input handling & transport
*{{validation policy · body-size limits · rate limiting (mechanism + keying) · CORS policy ·
upload restrictions (size, content-type sniffing) · SSRF policy for outbound fetches ·
injection guards (SQL, header/CRLF, CSV formula…).}}*

## Audit & logging
*{{what's audited automatically, where it's stored, the redaction list for sensitive fields
(NAME THE FIELDS — reviewers check new fields against it), and the never-log list
(secrets/tokens/PII).}}*

## Data protection
*{{what personal data is stored (minimize!) · deletion/export flows (GDPR-class) and their
failure semantics · signed-URL TTLs · retention rules.}}*

## Principles for new code
Validate every external input. Never log secrets/tokens/PII. Fail closed on auth/money paths.
When adding a sensitive field, extend the redaction list in the same change. *(keep these; add
project-specific ones)*
