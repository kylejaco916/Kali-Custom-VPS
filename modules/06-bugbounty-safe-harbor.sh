#!/usr/bin/env bash
# ==============================================================================
# Module 06: Bug Bounty ASM, API Auditing (jwt_tool, Bruno) & Safe-Harbor Stack
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="/usr/local/go/bin:${HOME}/go/bin:/usr/local/bin:${PATH}"

echo "=== [Module 06] Bug Bounty ASM, API Auditing & Safe-Harbor Compliance ==="

# 1. Install APT Recon & Auditing Packages
BB_PKGS=(subfinder amass dnsx naabu gowitness dalfox trufflehog feroxbuster)
MISSING_BB=()
for p in "${BB_PKGS[@]}"; do
    if ! dpkg -l "$p" 2>/dev/null | grep -q '^ii'; then
        MISSING_BB+=("$p")
    fi
done
if [[ ${#MISSING_BB[@]} -gt 0 ]]; then
    sudo apt-get update -qq
    sudo env DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a apt-get install -y "${MISSING_BB[@]}"
    sudo apt-get clean
fi

# 2. Install Go-based Recon Binaries (alterx, gau, waybackurls)
if ! command -v alterx >/dev/null 2>&1; then
    echo "[*] Installing alterx..."
    go install github.com/projectdiscovery/alterx/cmd/alterx@latest
fi
[[ -f "${HOME}/go/bin/alterx" ]] && sudo cp -f "${HOME}/go/bin/alterx" /usr/local/bin/alterx && sudo chmod 0755 /usr/local/bin/alterx

if ! command -v gau >/dev/null 2>&1; then
    echo "[*] Installing gau..."
    go install github.com/lc/gau/v2/cmd/gau@latest
fi
[[ -f "${HOME}/go/bin/gau" ]] && sudo cp -f "${HOME}/go/bin/gau" /usr/local/bin/gau && sudo chmod 0755 /usr/local/bin/gau

if ! command -v waybackurls >/dev/null 2>&1; then
    echo "[*] Installing waybackurls..."
    go install github.com/tomnomnom/waybackurls@latest
fi
[[ -f "${HOME}/go/bin/waybackurls" ]] && sudo cp -f "${HOME}/go/bin/waybackurls" /usr/local/bin/waybackurls && sudo chmod 0755 /usr/local/bin/waybackurls

# 3. Install & Patch jwt_tool (/opt/jwt_tool + ~/.jwt_tool/jwtconf.ini)
if [[ ! -d /opt/jwt_tool ]]; then
    echo "[*] Cloning jwt_tool into /opt/jwt_tool..."
    sudo git clone --depth 1 https://github.com/ticarpi/jwt_tool.git /opt/jwt_tool
    sudo python3 -m venv /opt/jwt_tool/.venv
    sudo /opt/jwt_tool/.venv/bin/pip install --quiet -r /opt/jwt_tool/requirements.txt
    # Apply Python 3.14 SafeConfigParser/RawConfigParser compatibility patch if needed
    sudo sed -i 's/SafeConfigParser/ConfigParser/g' /opt/jwt_tool/jwt_tool.py || true
fi
sudo cp -f "${REPO_ROOT}/scripts/usr-local-bin/jwt_tool" /usr/local/bin/jwt_tool
sudo chmod 0755 /usr/local/bin/jwt_tool
mkdir -p "${HOME}/.jwt_tool"
if [[ ! -f "${HOME}/.jwt_tool/jwtconf.ini" ]]; then
    cp -f "${REPO_ROOT}/configs/jwt_tool/jwtconf.ini" "${HOME}/.jwt_tool/jwtconf.ini"
fi

# 4. Install Bruno API Client & Caido-routed Preferences
if ! command -v bruno >/dev/null 2>&1; then
    echo "[*] Installing Bruno API Client..."
    BRUNO_DEB_URL=$(curl -fsSL https://api.github.com/repos/usebruno/bruno/releases/latest | jq -r '.assets[] | select(.name | endswith("_amd64_linux.deb")) | .browser_download_url' | head -n 1 || true)
    if [[ -n "${BRUNO_DEB_URL}" ]]; then
        curl -fsSL "${BRUNO_DEB_URL}" -o /tmp/bruno.deb
        sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y /tmp/bruno.deb
        rm -f /tmp/bruno.deb
    fi
fi
sudo cp -f "${REPO_ROOT}/scripts/usr-local-bin/bruno-caido" /usr/local/bin/bruno-caido
sudo chmod 0755 /usr/local/bin/bruno-caido
mkdir -p "${HOME}/.config/bruno"
cp -f "${REPO_ROOT}/configs/bruno/preferences.json" "${HOME}/.config/bruno/preferences.json"

# 5. Deploy ~/.bounty_env & Safe-Harbor Wrappers in /usr/local/bin
cp -f "${REPO_ROOT}/configs/dotfiles/.bounty_env" "${HOME}/.bounty_env"
SAFE_WRAPPERS=(dalfox-safe ffuf-safe httpx-safe katana-safe nuclei-safe scope-filter)
for sw in "${SAFE_WRAPPERS[@]}"; do
    sudo cp -f "${REPO_ROOT}/scripts/usr-local-bin/${sw}" "/usr/local/bin/${sw}"
    sudo chmod 0755 "/usr/local/bin/${sw}"
done

# 6. Deploy Target Workspace Template (~/bounties/target-template)
mkdir -p "${HOME}/bounties/target-template"/{scope,recon,js,findings,poc}
cp -f "${REPO_ROOT}/scripts/bounties/target-template/run_recon.sh" "${HOME}/bounties/target-template/run_recon.sh"
cp -f "${REPO_ROOT}/scripts/bounties/target-template/scope_filter.sh" "${HOME}/bounties/target-template/scope_filter.sh"
chmod 0755 "${HOME}/bounties/target-template/run_recon.sh" "${HOME}/bounties/target-template/scope_filter.sh"
cp -f "${REPO_ROOT}/scripts/bounties/target-template/scope/in_scope.txt" "${HOME}/bounties/target-template/scope/in_scope.txt"
cp -f "${REPO_ROOT}/scripts/bounties/target-template/scope/out_of_scope.txt" "${HOME}/bounties/target-template/scope/out_of_scope.txt"
cp -f "${REPO_ROOT}/scripts/bounties/target-template/poc/bruno.json" "${HOME}/bounties/target-template/poc/bruno.json"

echo "[+] Module 06 complete: Recon pipeline, jwt_tool, Bruno, Safe-Harbor wrappers, and target-template ready."
