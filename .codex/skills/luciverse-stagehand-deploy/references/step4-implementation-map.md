# Step 4 Implementation Map

## Field Flow
1. Spec fields (`luciverse-system-config/api/luciverse-openapi.yaml`)
2. Wallet manifest (`luciverse-sovereign-orchestrator/credentials/manifest.json`)
3. Generated Stagehand manifest env (`luciverse-web/stagehand-config/manifest-environment.json`)
4. Stagehand config env mapping (`luciverse-web/stagehand-config/stagehand.config.ts`)
5. AgentBridge runtime context (`luciverse/sensai/src/core/AgentBridge.ts`)
6. Ops automation scripts (`luciverse-web` npm deploy scripts)

## DID/TID + Auth Handoff Requirements
- Preserve the 1Password Agentic Autofill handshake with Browserbase:
  - https://developer.1password.com/docs/agentic-autofill#step-1-connect-1password-and-browserbase
- Inject DID/TID via manifest-generated env vars only.
- Do not replace existing auth credential channel; append identity metadata to the same agent execution path.

## Regression Focus
- Cache regression: missing/invalid `cacheDir` in generated agent payload.
- Auth regression: Stagehand auth works before/after DID/TID injection with no extra credential prompts.
- Bridge regression: AgentBridge receives DID/TID values and preserves existing credential resolution order.

## Deployment Order
1. `python3 /home/daryl/luciverse-sovereign-orchestrator/wallets/provision_all.py`
2. `python3 /home/daryl/luciverse-web/scripts/generate_stagehand_env.py`
3. `npm run deploy:all` in `/home/daryl/luciverse-web`
4. Optional: `npm run deploy:idigit` if rolling that worker independently
