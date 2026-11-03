#!/usr/bin/env bash
# ==============================================================================
# Module 08: Headless Colab Tailscale + HexStrike MCP + Hermes + Skills + Dotfiles
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== [Module 08] HexStrike AI + Headless Colab Tailscale Stack, Hermes CLI, Skills & Dotfiles ==="

# 1. Deploy Dotfiles (.bashrc, .zshrc, .profile, .zprofile, .bounty_env, GEMINI.md)
cp -f "${REPO_ROOT}/configs/dotfiles/.bashrc" "${HOME}/.bashrc"
cp -f "${REPO_ROOT}/configs/dotfiles/.zshrc" "${HOME}/.zshrc"
cp -f "${REPO_ROOT}/configs/dotfiles/.profile" "${HOME}/.profile"
cp -f "${REPO_ROOT}/configs/dotfiles/.zprofile" "${HOME}/.zprofile"
cp -f "${REPO_ROOT}/configs/dotfiles/.bounty_env" "${HOME}/.bounty_env"
cp -f "${REPO_ROOT}/configs/dotfiles/GEMINI.md" "${HOME}/GEMINI.md"
chmod 0600 "${HOME}/GEMINI.md"

# 2. Deploy Headless Colab Tailscale + HexStrike AI Stack to ~/hexstrike-ai/
mkdir -p "${HOME}/hexstrike-ai/logs"
cp -rf "${REPO_ROOT}/scripts/hexstrike-ai/"* "${HOME}/hexstrike-ai/"
cp -f "${REPO_ROOT}/scripts/hexstrike-ai/.mcp.json" "${HOME}/hexstrike-ai/.mcp.json"
chmod 0755 "${HOME}/hexstrike-ai/1_colab_orchestrator.py" \
           "${HOME}/hexstrike-ai/2_kali_gpu_controller.sh" \
           "${HOME}/hexstrike-ai/3_autonomous_assessment_loop.sh" \
           "${HOME}/hexstrike-ai/ask_ai.py" \
           "${HOME}/hexstrike-ai/chat.py" \
           "${HOME}/hexstrike-ai/qa_harness.sh"

# Re-inject live public key into COLAB_BOOTSTRAP_CELL.py if ~/.ssh/id_ed25519.pub exists
if [[ -f "${HOME}/.ssh/id_ed25519.pub" ]]; then
    PUBKEY=$(cat "${HOME}/.ssh/id_ed25519.pub")
    cat << EOF > "${HOME}/hexstrike-ai/COLAB_BOOTSTRAP_CELL.py"
# PASTE THIS 5-LINE CELL INTO GOOGLE COLAB (REPLACES ALL NOTEBOOK CODE)
!curl -fsSL https://tailscale.com/install.sh | sh && apt-get update -qq && apt-get install -y -qq openssh-server zstd psmisc > /dev/null
!mkdir -p /var/run/sshd /root/.ssh && chmod 700 /root/.ssh && echo "${PUBKEY}" > /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys
!ssh-keygen -A >/dev/null 2>&1 && sed -i 's/#\?Port .*/Port 2222/' /etc/ssh/sshd_config && grep -q '^PermitRootLogin' /etc/ssh/sshd_config || echo -e "PermitRootLogin prohibit-password\nPubkeyAuthentication yes" >> /etc/ssh/sshd_config && (killall -q sshd || true) && /usr/sbin/sshd
!killall -q tailscaled || true; nohup tailscaled --tun=userspace-networking --socks5-server=localhost:1055 > /tmp/tailscaled.log 2>&1 &
!sleep 3 && tailscale up --hostname="colab-gpu" --accept-routes
EOF
fi

# 3. Provision ~/hexstrike-ai/hexstrike-env virtualenv (hermes-agent, mcp, fastmcp, psutil, requests, flask)
VENV_DIR="${HOME}/hexstrike-ai/hexstrike-env"
if [[ ! -x "${VENV_DIR}/bin/python3" ]]; then
    echo "[*] Creating Python virtualenv at ${VENV_DIR}..."
    rm -rf "${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
fi
if ! "${VENV_DIR}/bin/python3" -c "import mcp, fastmcp, psutil, requests, flask" 2>/dev/null || [[ ! -x "${VENV_DIR}/bin/hermes" ]]; then
    echo "[*] Installing hermes-agent, mcp, fastmcp, psutil, requests, flask into ${VENV_DIR}..."
    "${VENV_DIR}/bin/pip" install --quiet --upgrade pip
    "${VENV_DIR}/bin/pip" install --quiet hermes-agent mcp "fastmcp>=0.2.0,<1.0.0" psutil requests flask beautifulsoup4 aiohttp
fi

# 4. Ensure Local HexStrike Server (127.0.0.1:8888) is running
if ! curl -fsSL --max-time 2 http://127.0.0.1:8888/health >/dev/null 2>&1; then
    echo "[*] Starting local HexStrike AI Server on 127.0.0.1:8888..."
    nohup "${VENV_DIR}/bin/python3" "${HOME}/hexstrike-ai/hexstrike_server.py" --port 8888 > "${HOME}/hexstrike-ai/hexstrike.log" 2>&1 &
    sleep 2
fi

# 5. Deploy Hermes Config (~/.config/hermes/config.json) & Antigravity MCP Config (~/.gemini/config/mcp_config.json)
mkdir -p "${HOME}/.config/hermes" "${HOME}/.local/share/mcp-servers/security-tools" "${HOME}/.gemini/config"
cp -f "${REPO_ROOT}/configs/hermes/config.json" "${HOME}/.config/hermes/config.json"
cp -f "${REPO_ROOT}/agent/mcp/security_mcp_server.py" "${HOME}/.local/share/mcp-servers/security-tools/security_mcp_server.py"
chmod 0755 "${HOME}/.local/share/mcp-servers/security-tools/security_mcp_server.py"
cp -f "${REPO_ROOT}/agent/mcp/mcp_config.json" "${HOME}/.gemini/config/mcp_config.json"

# 6. Deploy All 23 Custom Antigravity Skills (~/.agents/skills/) & verify_environment.sh
mkdir -p "${HOME}/.agents/skills"
cp -rf "${REPO_ROOT}/agent/skills/"* "${HOME}/.agents/skills/"
cp -f "${REPO_ROOT}/scripts/home-scripts/verify_environment.sh" "${HOME}/verify_environment.sh"
chmod 0755 "${HOME}/verify_environment.sh"

# 7. Deploy E2E Test Suite to ~/.agents/teamwork/e2e_testing/
mkdir -p "${HOME}/.agents/teamwork/e2e_testing"
cp -rf "${REPO_ROOT}/tests/e2e_testing/"* "${HOME}/.agents/teamwork/e2e_testing/"
chmod 0755 "${HOME}/.agents/teamwork/e2e_testing/run_e2e_tests.sh" "${HOME}/.agents/teamwork/e2e_testing/test_runner.py"

echo "[+] Module 08 complete: HexStrike AI + Colab Tailscale stack, Hermes CLI, MCP servers, 23 skills, and dotfiles active."
