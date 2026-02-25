# OP Credential Flow Reference

## Goal
Read credentials from 1Password when present, and create/populate when missing, without breaking runtime auth flows.

## Standard flow
1. Attempt `op read` (or existing connect API call).
2. If missing:
- Return clear non-fatal message in user-facing tools.
- Trigger credential creation routine (Lucia-managed path).
3. Retry read after creation.
4. Cache only short-lived tokens where required.

## Guardrails
- Never hardcode secrets.
- Prefer item references (`op://vault/item/field`) over raw values in code.
- Log missing-secret events without secret values.
- Separate personal vs business credential namespaces.
