#!/usr/bin/env bash
# ==============================================================================
# Module 07: Kali Applications Dropdown Menu Integration (32 Custom Launchers)
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== [Module 07] Kali Applications Menu Integration (32 Custom .desktop Launchers) ==="

mkdir -p "${HOME}/.local/share/applications"
sudo mkdir -p /usr/share/applications

for dfile in "${REPO_ROOT}/configs/desktop-entries/"*.desktop; do
    [[ -f "${dfile}" ]] || continue
    base="$(basename "${dfile}")"
    sudo cp -f "${dfile}" "/usr/share/applications/${base}"
    sudo chmod 0644 "/usr/share/applications/${base}"
    cp -f "${dfile}" "${HOME}/.local/share/applications/${base}"
    chmod 0644 "${HOME}/.local/share/applications/${base}"
done

sudo update-desktop-database /usr/share/applications 2>/dev/null || true
update-desktop-database "${HOME}/.local/share/applications" 2>/dev/null || true

echo "[+] Module 07 complete: All 32 custom security and wrapper launchers registered in Kali Applications menu."
