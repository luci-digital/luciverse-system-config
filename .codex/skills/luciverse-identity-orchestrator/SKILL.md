---
name: luciverse-identity-orchestrator
description: Implement and operate LuciVerse identity orchestration across SSI-OIDC bridge code, DID/TID compatibility, 1Password credential automation, and policy-gated adapter routes. Use when tasks involve auth bridge changes in auth/ssi_oidc_bridge.py, DID alias/canonical migration, OP secret read/create flows, adapter contract endpoints, or cross-repo identity plumbing between lucios and luciverse-sovereign-orchestrator.
---

# Luciverse Identity Orchestrator

## Quick Start

1. Identify scope:
- `auth bridge`: `auth/ssi_oidc_bridge.py`
- `adapter contract`: `threading_api_server.py` and `endpoints/adapter_*.py`
- `credential automation`: scripts/services calling `op read` or `op item create`

2. Pick the workflow:
- DID compatibility and resolver behavior: read `references/did-compat.md`
- OP integration and fallback creation: read `references/op-credential-flow.md`
- Policy-gated handoff and router wiring: read `references/adapter-policy-routing.md`

3. Implement with guardrails:
- Keep canonical DID output as `did:ownid:luciverse:*`.
- Preserve backward compatibility for legacy `did:luci:ownid:luciverse:*`.
- Add tests for every fallback path added.
- Avoid touching unrelated modified files in dirty worktrees.

4. Validate:
- Run `scripts/run_identity_checks.sh <repo-path>` for fast local checks.
- Run any focused pytest for touched components.

## Standard Workflow

### 1) Scope and map the existing flow
- Locate request entry points and where identity values are transformed.
- Document current canonical format, accepted aliases, and external dependencies (Hydra, Kratos, resolver, OP).

### 2) Patch minimally and compatibly
- Normalize inbound values once at trust boundary.
- Emit canonical DID in outbound claims and credentials.
- Keep alias lookups for resolver/identity backends.
- Add only additive adapter routes unless explicitly refactoring.

### 3) Add tests before finalizing
- Include direct canonical tests and alias fallback tests.
- Assert both success and fallback behavior.
- Prefer lightweight stubs over external service requirements.

### 4) Validate and commit cleanly
- Run targeted compile/tests first, then broader checks if cheap.
- Stage only relevant files.
- Keep auth bridge changes in a separate commit from adapter or UI changes.

## Output Requirements

Always provide:
- File list changed, grouped by concern (`auth`, `adapter`, `ops`).
- Validation commands run and pass/fail summary.
- Explicit note for anything skipped (missing deps, service unavailable).
