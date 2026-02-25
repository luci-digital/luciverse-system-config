#!/usr/bin/env bash
set -euo pipefail

WALLET_ROOT="/home/daryl/luciverse-sovereign-orchestrator"
WEB_ROOT="/home/daryl/luciverse-web"

echo "[1/2] Provisioning wallets and manifest..."
python3 "${WALLET_ROOT}/wallets/provision_all.py"

echo "[2/2] Regenerating Stagehand environment manifest..."
python3 "${WEB_ROOT}/scripts/generate_stagehand_env.py"

echo "Done."
echo "Generated: ${WEB_ROOT}/stagehand-config/manifest-environment.json"
