#!/usr/bin/env bash
# ==============================================================================
# Module 05: DevSecOps & PortSwigger Web Security Academy Lab Pipeline
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== [Module 05] DevSecOps & PortSwigger Lab Stack (Caido :8080 + ZAP :8081 + Firefox Profile) ==="

# 1. Ensure Lab Packages & Browsers are installed
LAB_PKGS=(firefox-esr chromium caido-cli zaproxy ffuf nuclei katana httpx-toolkit sqlmap arjun libnss3-tools sqlite3)
MISSING_LAB=()
for p in "${LAB_PKGS[@]}"; do
    if ! dpkg -l "$p" 2>/dev/null | grep -q '^ii'; then
        MISSING_LAB+=("$p")
    fi
done
if [[ ${#MISSING_LAB[@]} -gt 0 ]]; then
    sudo apt-get update -qq
    sudo env DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a apt-get install -y "${MISSING_LAB[@]}"
    sudo apt-get clean
fi

# 2. Ensure interactsh-client is installed in /usr/local/bin
if ! command -v interactsh-client >/dev/null 2>&1; then
    echo "[*] Building interactsh-client via Go..."
    export PATH="/usr/local/go/bin:${HOME}/go/bin:${PATH}"
    go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest
    sudo cp -f "${HOME}/go/bin/interactsh-client" /usr/local/bin/interactsh-client
    sudo chmod 0755 /usr/local/bin/interactsh-client
fi

# 3. Configure Dedicated Firefox Lab Profile (/home/kali/.mozilla/firefox/portswigger-lab)
PROFILE_DIR="${HOME}/.mozilla/firefox/portswigger-lab"
mkdir -p "${PROFILE_DIR}" "${HOME}/.local/share/devsecops-lab/certs" "${HOME}/.local/share/devsecops-lab/bin" "${HOME}/.config/devsecops-lab"
cp -f "${REPO_ROOT}/configs/firefox-portswigger-lab/user.js" "${PROFILE_DIR}/user.js"

PROFILES_INI="${HOME}/.mozilla/firefox/profiles.ini"
if [[ ! -f "${PROFILES_INI}" ]] || ! grep -q "Path=portswigger-lab" "${PROFILES_INI}" 2>/dev/null; then
    cat << 'INI_EOF' >> "${PROFILES_INI}"

[Profile_PortSwiggerLab]
Name=portswigger-lab
IsRelative=1
Path=portswigger-lab
INI_EOF
fi

# Initialize NSS cert9.db inside Firefox profile if missing
if [[ ! -f "${PROFILE_DIR}/cert9.db" ]]; then
    certutil -N -d "sql:${PROFILE_DIR}" --empty-password
fi

# 4. Deploy OWASP ZAP config.xml (:8081 + Interactsh OAST)
mkdir -p "${HOME}/.ZAP"
if [[ ! -f "${HOME}/.ZAP/config.xml" ]]; then
    cp -f "${REPO_ROOT}/configs/zap/config.xml" "${HOME}/.ZAP/config.xml"
fi

# 5. Export / Trust Caido & ZAP Root CAs in Firefox cert9.db if present
if [[ -f "${HOME}/.local/share/caido/ca.crt" && ! -f "${HOME}/.local/share/devsecops-lab/certs/caido-ca.pem" ]]; then
    cp -f "${HOME}/.local/share/caido/ca.crt" "${HOME}/.local/share/devsecops-lab/certs/caido-ca.pem"
fi
if [[ -f "${HOME}/.local/share/devsecops-lab/certs/caido-ca.pem" ]]; then
    certutil -A -n "Caido Root CA" -t "CT,C,C" -i "${HOME}/.local/share/devsecops-lab/certs/caido-ca.pem" -d "sql:${PROFILE_DIR}" 2>/dev/null || true
fi
if [[ -f "${HOME}/.local/share/devsecops-lab/certs/zap-ca.pem" ]]; then
    certutil -A -n "OWASP ZAP Root CA" -t "CT,C,C" -i "${HOME}/.local/share/devsecops-lab/certs/zap-ca.pem" -d "sql:${PROFILE_DIR}" 2>/dev/null || true
fi

# 6. Install all DevSecOps Wrapper Scripts & Proxy Chaining Controller
DEVSECOPS_WRAPPERS=(portswigger-browser proxy-toggle arjun-caido ffuf-caido ffuf-replay httpx-caido interactsh-caido katana-caido nuclei-caido sqlmap-caido)
for w in "${DEVSECOPS_WRAPPERS[@]}"; do
    cp -f "${REPO_ROOT}/scripts/usr-local-bin/${w}" "${HOME}/.local/share/devsecops-lab/bin/${w}"
    chmod 0755 "${HOME}/.local/share/devsecops-lab/bin/${w}"
    sudo cp -f "${REPO_ROOT}/scripts/usr-local-bin/${w}" "/usr/local/bin/${w}"
    sudo chmod 0755 "/usr/local/bin/${w}"
done

# 7. Deploy ~/.config/devsecops-lab/aliases.sh and ~/devsecops-lab-commands documentation folder
cp -f "${REPO_ROOT}/configs/dotfiles/devsecops-aliases.sh" "${HOME}/.config/devsecops-lab/aliases.sh"
mkdir -p "${HOME}/devsecops-lab-commands"
cp -rf "${REPO_ROOT}/scripts/devsecops-lab-commands/"* "${HOME}/devsecops-lab-commands/"
chmod 0755 "${HOME}/devsecops-lab-commands/scripts/"*

echo "[+] Module 05 complete: PortSwigger Lab browser profile, proxy-toggle, *-caido wrappers, and documentation deployed."
