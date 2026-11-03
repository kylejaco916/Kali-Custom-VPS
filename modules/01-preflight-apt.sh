#!/usr/bin/env bash
# ==============================================================================
# Module 01: System Pre-Flight, Non-Interactive APT/DPKG, Cache Guard & Debconf
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== [Module 01] Pre-Flight APT, Needrestart & Debconf Configuration ==="

# 0. Ensure passwordless sudo for unattended automation
if [[ ! -f /etc/sudoers.d/90-kali-nopasswd ]]; then
    echo "$(whoami) ALL=(ALL:ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/90-kali-nopasswd >/dev/null
    sudo chmod 0440 /etc/sudoers.d/90-kali-nopasswd
fi

# 1. Deploy Non-Interactive APT & Cache Cleanup Drop-ins
sudo mkdir -p /etc/apt/apt.conf.d /etc/needrestart/conf.d
sudo cp -f "${REPO_ROOT}/configs/apt/99noninteractive" /etc/apt/apt.conf.d/99noninteractive
sudo cp -f "${REPO_ROOT}/configs/apt/99clean-cache" /etc/apt/apt.conf.d/99clean-cache
sudo cp -f "${REPO_ROOT}/configs/apt/99batch.conf" /etc/needrestart/conf.d/99batch.conf
sudo chmod 644 /etc/apt/apt.conf.d/99noninteractive /etc/apt/apt.conf.d/99clean-cache /etc/needrestart/conf.d/99batch.conf

# 2. Ensure debconf-utils is installed
if ! command -v debconf-set-selections >/dev/null 2>&1; then
    sudo apt-get update -qq
    sudo env DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a apt-get install -y -qq debconf-utils
fi

# 3. Pre-seed debconf database for all 28 kali-tools-* metapackages
sudo debconf-set-selections < "${REPO_ROOT}/configs/apt/debconf.selections"

# 4. Verify dpkg health
sudo dpkg --configure -a
sudo dpkg --audit

echo "[+] Module 01 complete: Non-interactive APT, cache cleanup, and debconf pre-seeding active."
