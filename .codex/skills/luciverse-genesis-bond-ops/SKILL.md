---
name: luciverse-genesis-bond-ops
description: Operate Lucia AI Genesis Bond and related Luciverse web authentication flows end-to-end. Use when diagnosing 1Password/OP session issues, OIDC callback failures, PAC login problems, Cloudflare worker route/deploy regressions, or when running post-deploy smoke checks and safe commit/push workflows across luciverse-web and lucidigital-net repositories.
---

# Luciverse Genesis Bond Ops

## Overview

Execute a reliable, non-destructive workflow for Genesis Bond login validation, OIDC callback troubleshooting, and deploy/runtime verification in Luciverse environments.

## Workflow

1. Confirm identity/session prerequisites.
2. Diagnose auth flow from `/login` to `/callback`.
3. Verify runtime/API health and route bindings.
4. Apply minimal non-breaking fixes.
5. Validate with smoke checks.
6. Commit and push only relevant changes.

## 1) Confirm Prerequisites

Run:

```bash
op whoami
env | rg '^OP_'
```

If `op whoami` fails, request sign-in in the same shell:

```bash
eval "$(op signin)"
op whoami
```

Do not claim access to secret values (master passkey or item secrets). Confirm account context only.

## 2) Diagnose OIDC Flow

For `io.lucidigital.io` and related properties, verify this sequence:

1. `GET /login` redirects to issuer with PAR/request URI.
2. issuer returns `code` and `state` to `/callback`.
3. callback exchanges code at token endpoint with PKCE verifier.
4. session cookie is set.
5. authenticated endpoints return authorized results.

Minimum probes:

```bash
curl -i https://io.lucidigital.io/login
curl -i "https://lucidigital.net/admin/callback?code=test&state=test&iss=https%3A%2F%2Fidigit.me"
curl -i https://io.lucidigital.io/api/session
```

When callback fails, harden:

- defensive JSON parsing for token responses
- explicit state/PKCE validation errors
- fallback handling when `access_token` exists without `id_token`
- top-level try/catch with traceable error response

## 3) Verify Route and Runtime Health

Check worker routes, static fallback, and API status:

```bash
curl -i https://io.lucidigital.io/
curl -i https://io.lucidigital.io/cbb-wallet
curl -i https://io.lucidigital.io/api/certification/status
curl -i https://idigit.me/health
```

If SPA route fails, ensure non-asset 404s fall back to `index.html`.
If host fails, verify route coverage includes `io.lucidigital.io/*`.

## 4) Apply Fixes Safely

- Keep changes additive and non-breaking.
- Do not change existing v1 API response schemas unless explicitly requested.
- Scope fixes to the smallest affected files.
- Preserve CBB ownership/consent boundaries in auth and data access paths.

## 5) Validate Before Commit

Run repo-local checks that match modified areas, for example:

```bash
npm run build
npm run typecheck
pytest -q resonant-garden/Integration/CBB/tests/test_api_contract_scaffold.py
python3 -m py_compile <modified_python_files>
```

Include targeted curl smoke results in the final report.

## 6) Commit/Push Discipline

Before commit:

```bash
git status --short
git diff -- <changed-files>
```

Rules:

- never revert unrelated existing local changes
- commit only files relevant to this task
- use clear commit messages tied to behavior changes
- push current branch and report branch + commit SHA

## Fast Response Template

Use this structure in updates:

1. current check being run
2. key finding
3. next action

Keep responses concise and operational.
