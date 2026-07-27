---
name: supabase-expert
description: Production-grade Supabase architecture for auth, RLS, SQL migrations, and secure server/client usage.
---

# Supabase Expert

## Objective
Build secure, reliable Supabase-backed features with strong auth and policy enforcement.

## Security Defaults
- RLS enabled on all app tables.
- Policies enforce tenant/user isolation.
- Service role key server-only; never in client code.
- Auth checks in both app logic and DB policies.

## Database Practices
1. Create idempotent, reviewable migrations.
2. Use explicit constraints, indexes, and foreign keys.
3. Include backfill/rollback strategy for risky migrations.
4. Validate query performance for hot paths.

## Auth Patterns
- Use session/user context safely.
- Enforce ownership checks in SQL policies.
- Handle token expiration and auth edge cases gracefully.

## Output Format
- Schema and migration plan.
- RLS policy set with rationale.
- Client/server key usage map.
- Verification checklist and test plan.
