#!/usr/bin/env bash
set -euo pipefail

WEB_ROOT="/home/daryl/luciverse-web"
SYNC_SCRIPT="/home/daryl/.codex/skills/luciverse-stagehand-deploy/scripts/sync_manifest_and_stagehand_env.sh"
RUN_SYNC="true"

if [[ "${1:-}" == "--skip-sync" ]]; then
  RUN_SYNC="false"
fi

if [[ "${RUN_SYNC}" == "true" ]]; then
  "${SYNC_SCRIPT}"
fi

cd "${WEB_ROOT}"
echo "[deploy] Running npm run deploy:all"
npm run deploy:all

echo "[verify] Running npm run typecheck"
npm run typecheck

echo "Deployment workflow complete."
