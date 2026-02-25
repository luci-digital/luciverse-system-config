---
name: luciverse-stagehand-deploy
description: Use when deploying LuciVerse Stagehand/AgentBridge after wallet manifest changes, including DID/TID sync, auth-safe credential flow checks, and Cloudflare Wrangler rollout.
---

# Luciverse Stagehand Deploy

## Overview

This skill provides a concrete deployment workflow for LuciVerse Stagehand + AgentBridge with manifest synchronization and auth-safety checks.  
Use it when `manifest.json`, wallet provisioning, `stagehand.config.ts`, or deployment pipelines are updated.

## Workflow

## 1) Preflight Checks
- Validate 1Password session: `op whoami`
- Validate required tools:
  - `python3 --version`
  - `node -v`
  - `npm -v`

## 2) Sync Wallet Manifest Into Stagehand
- Run wallet provisioning first:
  - `python3 /home/daryl/luciverse-sovereign-orchestrator/wallets/provision_all.py`
- Regenerate Stagehand environment:
  - `python3 /home/daryl/luciverse-web/scripts/generate_stagehand_env.py`
- Confirm output exists:
  - `/home/daryl/luciverse-web/stagehand-config/manifest-environment.json`

## 3) Verify Step 4 Mapping Integrity
- Confirm spec/manifest/bridge links are still wired:
  - `luciverse-system-config/api/luciverse-openapi.yaml`
  - `luciverse/sensai/src/core/AgentBridge.ts`
  - `luciverse-web/stagehand-config/stagehand.config.ts`
- Ensure each generated agent exposes:
  - `STAGEHAND_AGENT_DID`
  - `STAGEHAND_AGENT_TID`
  - `STAGEHAND_AGENT_CACHE_DIR`
- Keep 1Password/Browserbase handoff unchanged:
  - `https://developer.1password.com/docs/agentic-autofill#step-1-connect-1password-and-browserbase`

## 4) Build + Deploy
- Run full rollout from `luciverse-web`:
  - `npm run deploy:all`
- Optional focused deploy:
  - `npm run deploy:idigit`

## 5) Regression Guardrails
- Add or run logs/tests that catch:
  - Manifest cache mismatch
  - Missing DID/TID env injection
  - Stagehand cache/auth handshake failures
- Suggested checks:
  - `npm run typecheck`
  - `npm run test:idigit`
  - deployment log grep for missing auth vars

## Helper Scripts
- `scripts/sync_manifest_and_stagehand_env.sh`
- `scripts/deploy_luciverse_stagehand.sh`

## References
- `references/step4-implementation-map.md` for the spec -> manifest -> Stagehand -> AgentBridge -> ops mapping.
