#!/usr/bin/env bash
# ==============================================================================
# Module 08: Agent Rules, 23 Skills, MCP Servers, Headless Colab + HexStrike AI
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

# 2. Ensure ~/hexstrike-ai is a standalone directory (decoupled from any legacy symlinks)
LEGACY_VENV=""
if [[ -L "${HOME}/hexstrike-ai/hexstrike-env" ]]; then
    LEGACY_VENV="$(readlink -f "${HOME}/hexstrike-ai/hexstrike-env" 2>/dev/null || true)"
fi
if [[ -L "${HOME}/hexstrike-ai" ]]; then
    echo "[*] Converting symlink ${HOME}/hexstrike-ai into standalone directory..."
    rm -f "${HOME}/hexstrike-ai"
fi
mkdir -p "${HOME}/hexstrike-ai/logs"
if [[ -L "${HOME}/hexstrike-ai/hexstrike-env" ]]; then
    rm -f "${HOME}/hexstrike-ai/hexstrike-env"
fi

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

# 3. Provision standalone ~/hexstrike-ai/hexstrike-env virtualenv
VENV_DIR="${HOME}/hexstrike-ai/hexstrike-env"

if [[ ! -d "${VENV_DIR}" && -n "${LEGACY_VENV}" && -d "${LEGACY_VENV}" ]]; then
    echo "[*] Migrating existing virtualenv into standalone ${VENV_DIR}..."
    cp -a "${LEGACY_VENV}" "${VENV_DIR}"
    find "${VENV_DIR}/bin" -maxdepth 1 -type f -exec sed -i "s|${LEGACY_VENV}|${VENV_DIR}|g" {} + 2>/dev/null || true
    [[ -f "${VENV_DIR}/pyvenv.cfg" ]] && sed -i "s|${LEGACY_VENV}|${VENV_DIR}|g" "${VENV_DIR}/pyvenv.cfg" || true
fi

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

# 4. Deploy & Start Persistent systemd service for Local HexStrike Server (127.0.0.1:8888)
sudo cp -f "${REPO_ROOT}/configs/systemd/hexstrike-server.service" /etc/systemd/system/hexstrike-server.service
sudo systemctl daemon-reload
sudo systemctl enable hexstrike-server.service
if ! systemctl is-active --quiet hexstrike-server.service; then
    # Stop any unmanaged hexstrike_server.py process holding port 8888 before starting systemd unit
    pkill -f "hexstrike_server\.py" 2>/dev/null || true
    sleep 1
    sudo systemctl start hexstrike-server.service
fi

# Wait up to 10s for HexStrike Server health endpoint on 127.0.0.1:8888
for _ in {1..10}; do
    if curl -fsSL --max-time 2 http://127.0.0.1:8888/health >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

# 5. Deploy Hermes Config (~/.config/hermes/config.json + ~/.hermes/SOUL.md), Antigravity CLI settings.json & MCP Config
mkdir -p "${HOME}/.config/hermes" "${HOME}/.hermes" "${HOME}/.local/share/mcp-servers/security-tools" "${HOME}/.gemini/config" "${HOME}/.gemini/antigravity-cli"
cp -f "${REPO_ROOT}/configs/hermes/config.json" "${HOME}/.config/hermes/config.json"
cp -f "${REPO_ROOT}/configs/hermes/SOUL.md" "${HOME}/.hermes/SOUL.md"
chmod 0600 "${HOME}/.hermes/SOUL.md"

cp -f "${REPO_ROOT}/agent/mcp/security_mcp_server.py" "${HOME}/.local/share/mcp-servers/security-tools/security_mcp_server.py"
chmod 0755 "${HOME}/.local/share/mcp-servers/security-tools/security_mcp_server.py"
cp -f "${REPO_ROOT}/agent/mcp/mcp_config.json" "${HOME}/.gemini/config/mcp_config.json"

if [[ ! -f "${HOME}/.gemini/antigravity-cli/settings.json" ]]; then
    cp -f "${REPO_ROOT}/agent/agy/settings.json" "${HOME}/.gemini/antigravity-cli/settings.json"
    chmod 0600 "${HOME}/.gemini/antigravity-cli/settings.json"
fi

# 6. Deploy All 23 Custom Antigravity Skills (~/.agents/skills/) & verify_environment.sh
mkdir -p "${HOME}/.agents/skills"
cp -rf "${REPO_ROOT}/agent/skills/"* "${HOME}/.agents/skills/"
cp -f "${REPO_ROOT}/scripts/home-scripts/verify_environment.sh" "${HOME}/verify_environment.sh"
chmod 0755 "${HOME}/verify_environment.sh"

# 7. Deploy E2E Test Suite to ~/.agents/teamwork/e2e_testing/
mkdir -p "${HOME}/.agents/teamwork/e2e_testing"
cp -rf "${REPO_ROOT}/tests/e2e_testing/"* "${HOME}/.agents/teamwork/e2e_testing/"
chmod 0755 "${HOME}/.agents/teamwork/e2e_testing/run_e2e_tests.sh" "${HOME}/.agents/teamwork/e2e_testing/test_runner.py"

echo "[+] Module 08 complete: Standalone HexStrike AI + Colab Tailscale stack, hexstrike-server.service, Hermes CLI, MCP servers, 23 skills, and dotfiles active."
