#!/usr/bin/env bash
set -euo pipefail

repo_path="${1:-}"
if [[ -z "${repo_path}" ]]; then
  echo "usage: $0 <repo-path>"
  exit 2
fi

echo "[identity-checks] repo: ${repo_path}"

if [[ -f "${repo_path}/auth/ssi_oidc_bridge.py" ]]; then
  python3 -m py_compile "${repo_path}/auth/ssi_oidc_bridge.py"
fi

if [[ -f "${repo_path}/tests/test_ssi_oidc_bridge_did_compat.py" ]]; then
  pytest -q "${repo_path}/tests/test_ssi_oidc_bridge_did_compat.py"
fi

if [[ -f "${repo_path}/tests/test_gui_intent_adapter_placeholder.py" ]]; then
  pytest -q "${repo_path}/tests/test_gui_intent_adapter_placeholder.py"
fi

echo "[identity-checks] done"
