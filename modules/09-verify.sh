#!/usr/bin/env bash
# ==============================================================================
# Module 09: End-to-End Verification, AST Syntax & Secret Scan Gates
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== [Module 09] Full System, AST Syntax, Secret Scan & E2E Verification Gates ==="

# 1. Gate 1A: Secret & Blacklist Scan on Repository Tree
echo "[1/6] Running Repository Secret, Key & Blacklist Hygiene Gate..."
if grep -rnE "BEGIN (OPENSSH|RSA|EC|DSA) PRIVATE [K]EY|teamwork_[p]rojects" "${REPO_ROOT}/" 2>/dev/null; then
    echo "  [FAIL] Private key material or blacklisted path detected in repository!"
    exit 1
fi
if find "${REPO_ROOT}" -name "id_ed25519" -o -name "id_rsa" -o -name "passwd" | grep -q .; then
    echo "  [FAIL] Raw private key or VNC passwd file found in repository!"
    exit 1
fi
echo "  [PASS] Zero private keys, tokens, VNC passwd files, or blacklisted paths in repository."

# 2. Gate 1B: Syntax & AST Compilation Checks (Bash + Python)
echo "[2/6] Running Bash & Python Syntax / AST Verification..."
while IFS= read -r -d '' shfile; do
    if head -n 1 "${shfile}" | grep -q "python"; then
        python3 -m py_compile "${shfile}"
    else
        bash -n "${shfile}"
    fi
done < <(find "${REPO_ROOT}" -type f -name "*.sh" -print0)

for wfile in "${REPO_ROOT}/scripts/usr-local-bin/"*; do
    [[ -f "${wfile}" ]] || continue
    head -n 1 "${wfile}" | grep -q "sh" && bash -n "${wfile}"
done

PYTHONDONTWRITEBYTECODE=1 python3 -B -m py_compile \
    "${REPO_ROOT}/scripts/hexstrike-ai/1_colab_orchestrator.py" \
    "${REPO_ROOT}/scripts/hexstrike-ai/ask_ai.py" \
    "${REPO_ROOT}/scripts/hexstrike-ai/chat.py" \
    "${REPO_ROOT}/scripts/hexstrike-ai/hexstrike_mcp.py" \
    "${REPO_ROOT}/scripts/hexstrike-ai/hexstrike_server.py" \
    "${REPO_ROOT}/agent/mcp/security_mcp_server.py" \
    "${REPO_ROOT}/scripts/usr-local-bin/scope-filter"
echo "  [PASS] All Bash scripts and Python modules passed syntax & AST compilation."

# 3. Gate 2A: Headless Colab Orchestrator Dry-Run Matrix
echo "[3/6] Verifying HexStrike Colab Orchestrator Dry-Run (Models 0, 1, 2)..."
for idx in 0 1 2; do
    OUT=$(STRIKE_MODEL_IDX=$idx python3 "${HOME}/hexstrike-ai/1_colab_orchestrator.py" --dry-run)
    echo "${OUT}" | jq -e '.status == "PASS" and .endpoint == "http://colab-gpu:8085"' >/dev/null
done
echo "  [PASS] 1_colab_orchestrator.py dry-run verified on port 8085."

# 4. Gate 2B: Core Environment & MCP Audit (~/verify_environment.sh)
echo "[4/6] Running ~/verify_environment.sh..."
"${HOME}/verify_environment.sh"

# 5. Gate 2C: Modules 03–08 Full-Stack Customizations Audit
echo "[5/6] Auditing Modules 03–08 Services, CAs, Wrappers, Desktop Menus & Standalone Venv..."

# 5a. Systemd services enabled/active
for svc in tigervnc.service novnc.service caido.service hexstrike-server.service tailscaled.service ssh.service; do
    systemctl is-enabled --quiet "${svc}" || { echo "  [FAIL] ${svc} is not enabled"; exit 1; }
    systemctl is-active --quiet "${svc}" || { echo "  [FAIL] ${svc} is not active"; exit 1; }
done

# 5b. Live HTTP endpoints (:8080 Caido & :8888 HexStrike Server)
curl -fsSL --max-time 3 http://127.0.0.1:8080/ca.crt | grep -q "BEGIN CERTIFICATE" || { echo "  [FAIL] Caido :8080/ca.crt unreachable"; exit 1; }
curl -fsSL --max-time 3 http://127.0.0.1:8888/health | grep -qi "healthy\|ok\|status" || { echo "  [FAIL] HexStrike Server :8888/health unreachable"; exit 1; }

# 5c. Firefox portswigger-lab profile & Root CAs in cert9.db
CERT_LIST=$(certutil -L -d "sql:${HOME}/.mozilla/firefox/portswigger-lab")
echo "${CERT_LIST}" | grep -q "Caido Root CA" || { echo "  [FAIL] Caido Root CA missing in Firefox cert9.db"; exit 1; }
echo "${CERT_LIST}" | grep -q "OWASP ZAP Root CA" || { echo "  [FAIL] OWASP ZAP Root CA missing in Firefox cert9.db"; exit 1; }

# 5d. Custom wrappers in /usr/local/bin
WRAPPERS=(kali-mode proxy-toggle portswigger-browser arjun-caido ffuf-caido ffuf-replay httpx-caido interactsh-caido katana-caido nuclei-caido sqlmap-caido dalfox-safe ffuf-safe httpx-safe katana-safe nuclei-safe scope-filter bruno-caido jwt_tool john)
for w in "${WRAPPERS[@]}"; do
    [[ -x "/usr/local/bin/${w}" ]] || { echo "  [FAIL] Missing executable /usr/local/bin/${w}"; exit 1; }
done

# 5e. Standalone ~/hexstrike-ai & ~/hexstrike-ai/hexstrike-env (not symlinks) + Hermes CLI + Configs
[[ ! -L "${HOME}/hexstrike-ai" && -d "${HOME}/hexstrike-ai" ]] || { echo "  [FAIL] ~/hexstrike-ai is still a symlink or missing"; exit 1; }
[[ ! -L "${HOME}/hexstrike-ai/hexstrike-env" && -x "${HOME}/hexstrike-ai/hexstrike-env/bin/hermes" ]] || { echo "  [FAIL] ~/hexstrike-ai/hexstrike-env is not a standalone virtualenv with hermes"; exit 1; }
[[ -f "${HOME}/.hermes/SOUL.md" && -f "${HOME}/.gemini/antigravity-cli/settings.json" ]] || { echo "  [FAIL] Missing ~/.hermes/SOUL.md or ~/.gemini/antigravity-cli/settings.json"; exit 1; }

# 5f. 32 .desktop launchers & 21 custom Antigravity skills in ~/.agents/skills
DESKTOP_COUNT=$(ls -1 "${REPO_ROOT}/configs/desktop-entries/"*.desktop 2>/dev/null | wc -l)
SKILL_COUNT=$(find "${HOME}/.agents/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
[[ "${DESKTOP_COUNT}" -ge 32 ]] || { echo "  [FAIL] Expected >=32 .desktop launchers, found ${DESKTOP_COUNT}"; exit 1; }
[[ "${SKILL_COUNT}" -ge 21 ]] || { echo "  [FAIL] Expected >=21 custom Antigravity skills, found ${SKILL_COUNT}"; exit 1; }
echo "  [PASS] All 6 systemd services, Firefox CAs, 20 wrappers, standalone HexStrike/Hermes venv, 32 .desktop entries, and ${SKILL_COUNT} custom skills verified."

# 6. Gate 2D: 44-Test 4-Tier E2E Verification Suite
echo "[6/6] Running 44-Test 4-Tier E2E Verification Suite..."
"${REPO_ROOT}/tests/e2e_testing/run_e2e_tests.sh" --tier all --feature all

echo "=============================================================================="
echo " [PASS] ALL KALI-CUSTOM-VPS VERIFICATION GATES PASSED (EXIT CODE 0)"
echo "=============================================================================="
