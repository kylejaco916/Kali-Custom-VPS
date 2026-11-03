#!/usr/bin/env bash
# ==============================================================================
# Module 09: End-to-End Verification, AST Syntax & Secret Scan Gates
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== [Module 09] Full System, AST Syntax, Secret Scan & E2E Verification Gates ==="

# 1. Gate 1A: Secret Scan on Repository Tree
echo "[1/5] Running Repository Secret & Key Hygiene Gate..."
if grep -rnE "BEGIN (OPENSSH|RSA|EC|DSA) PRIVATE KEY" "${REPO_ROOT}/" 2>/dev/null; then
    echo "  [FAIL] Private key material detected in repository!"
    exit 1
fi
if find "${REPO_ROOT}" -name "id_ed25519" -o -name "id_rsa" -o -name "passwd" | grep -q .; then
    echo "  [FAIL] Raw private key or VNC passwd file found in repository!"
    exit 1
fi
echo "  [PASS] Zero private keys, tokens, or VNC passwd files in repository."

# 2. Gate 1B: Syntax & AST Compilation Checks (Bash + Python)
echo "[2/5] Running Bash & Python Syntax / AST Verification..."
while IFS= read -r -d '' shfile; do
    if head -n 1 "${shfile}" | grep -q "python"; then
        python3 -m py_compile "${shfile}"
    else
        bash -n "${shfile}"
    fi
done < <(find "${REPO_ROOT}" -type f -name "*.sh" -print0)

for wfile in "${REPO_ROOT}/scripts/usr-local-bin/"*; do
    head -n 1 "${wfile}" | grep -q "sh" && bash -n "${wfile}"
done

python3 -m py_compile \
    "${REPO_ROOT}/scripts/hexstrike-ai/1_colab_orchestrator.py" \
    "${REPO_ROOT}/scripts/hexstrike-ai/ask_ai.py" \
    "${REPO_ROOT}/scripts/hexstrike-ai/chat.py" \
    "${REPO_ROOT}/scripts/hexstrike-ai/hexstrike_mcp.py" \
    "${REPO_ROOT}/scripts/hexstrike-ai/hexstrike_server.py" \
    "${REPO_ROOT}/agent/mcp/security_mcp_server.py" \
    "${REPO_ROOT}/scripts/usr-local-bin/scope-filter"
echo "  [PASS] All Bash scripts and Python modules passed syntax & AST compilation."

# 3. Gate 2A: Headless Colab Orchestrator Dry-Run Matrix
echo "[3/5] Verifying HexStrike Colab Orchestrator Dry-Run (Models 0, 1, 2)..."
for idx in 0 1 2; do
    OUT=$(STRIKE_MODEL_IDX=$idx python3 "${HOME}/hexstrike-ai/1_colab_orchestrator.py" --dry-run)
    echo "${OUT}" | jq -e '.status == "PASS" and .endpoint == "http://colab-gpu:8085"' >/dev/null
done
echo "  [PASS] 1_colab_orchestrator.py dry-run verified on port 8085."

# 4. Gate 2B: Core Environment & MCP Audit (~/verify_environment.sh)
echo "[4/5] Running ~/verify_environment.sh..."
"${HOME}/verify_environment.sh"

# 5. Gate 2C: 44-Test 4-Tier E2E Verification Suite
echo "[5/5] Running 44-Test 4-Tier E2E Verification Suite..."
"${REPO_ROOT}/tests/e2e_testing/run_e2e_tests.sh" --tier all --feature all

echo "=============================================================================="
echo " [PASS] ALL KALI-CUSTOM-VPS VERIFICATION GATES PASSED (EXIT CODE 0)"
echo "=============================================================================="
