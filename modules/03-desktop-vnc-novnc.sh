#!/usr/bin/env bash
# ==============================================================================
# Module 03: XFCE4 Desktop, Kali Menu, TigerVNC, noVNC, Burp Java 21 & kali-mode
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VNC_PASSWORD="${VNC_PASSWORD:-kali}"

echo "=== [Module 03] Desktop GUI, TigerVNC (:5901), noVNC (:6080), Burp Java 21 Fix & kali-mode ==="

# 1. Ensure XFCE, Kali Menu, VNC/noVNC, and OpenJDK 21 LTS are installed
GUI_PKGS=(kali-desktop-xfce kali-menu kali-defaults-desktop tigervnc-standalone-server novnc websockify xrdp openjdk-21-jre openjdk-21-jdk desktop-file-utils)
MISSING_GUI=()
for p in "${GUI_PKGS[@]}"; do
    if ! dpkg -l "$p" 2>/dev/null | grep -q '^ii'; then
        MISSING_GUI+=("$p")
    fi
done
if [[ ${#MISSING_GUI[@]} -gt 0 ]]; then
    sudo apt-get update -qq
    sudo env DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a apt-get install -y "${MISSING_GUI[@]}"
    sudo apt-get clean
fi

# 2. Configure TigerVNC xstartup & VNC Password
mkdir -p "${HOME}/.config/tigervnc"
cp -f "${REPO_ROOT}/configs/tigervnc/xstartup" "${HOME}/.config/tigervnc/xstartup"
chmod 0755 "${HOME}/.config/tigervnc/xstartup"
ln -sfn .config/tigervnc "${HOME}/.vnc"

if [[ ! -f "${HOME}/.config/tigervnc/passwd" ]]; then
    echo "${VNC_PASSWORD}" | vncpasswd -f > "${HOME}/.config/tigervnc/passwd"
    chmod 0600 "${HOME}/.config/tigervnc/passwd"
fi

# 3. Deploy TigerVNC & noVNC systemd units
sudo cp -f "${REPO_ROOT}/configs/systemd/tigervnc.service" /etc/systemd/system/tigervnc.service
sudo cp -f "${REPO_ROOT}/configs/systemd/novnc.service" /etc/systemd/system/novnc.service
sudo systemctl daemon-reload
sudo systemctl enable tigervnc.service novnc.service
if ! systemctl is-active --quiet tigervnc.service; then
    sudo systemctl start tigervnc.service || true
fi
if ! systemctl is-active --quiet novnc.service; then
    sudo systemctl start novnc.service || true
fi

# 4. Patch noVNC UI (/usr/share/novnc/app/ui.js) to suppress false-alarm HTTP banner on mobile browsers
if [[ -f /usr/share/novnc/app/ui.js ]]; then
    sudo sed -i 's|^\([[:space:]]*\)UI\.showStatus(_("Running without HTTPS is not recommended|\1// UI.showStatus(_("Running without HTTPS is not recommended|g' /usr/share/novnc/app/ui.js
fi

# 5. Configure Java 21 LTS & patch /usr/bin/burpsuite against Java 25 Swing UI crash
if [[ -d /usr/lib/jvm/java-21-openjdk-amd64 ]]; then
    sudo update-java-alternatives -s java-1.21.0-openjdk-amd64 2>/dev/null || true
fi
if [[ -f /usr/share/burpsuite/burpsuite.jar ]]; then
    sudo tee /usr/bin/burpsuite >/dev/null << 'BURP_EOF'
#!/usr/bin/env sh

set -e

# Include the wrappers utility script
. /usr/lib/java-wrappers/java-wrappers.sh

JAVA_CMD=${JAVA_CMD:-/usr/lib/jvm/java-21-openjdk-amd64/bin/java}
run_java -jar /usr/share/burpsuite/burpsuite.jar --suppress-jre-check --disable-check-for-updates-dialog "$@"
BURP_EOF
    sudo chmod 0755 /usr/bin/burpsuite
fi

# 6. Install /usr/local/bin/kali-mode switcher
sudo cp -f "${REPO_ROOT}/scripts/usr-local-bin/kali-mode" /usr/local/bin/kali-mode
sudo chmod 0755 /usr/local/bin/kali-mode

echo "[+] Module 03 complete: TigerVNC, noVNC, Burp Suite Java 21 fix, and kali-mode active."
