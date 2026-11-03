#!/usr/bin/env bash
# ==============================================================================
# Module 04: Tailscale Mesh, Hardened SSHD + X11Forwarding & Multi-Device SSH
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "=== [Module 04] Tailscale Mesh & Hardened SSH Configuration ==="

# 1. Install Tailscale if not present
if ! command -v tailscale >/dev/null 2>&1; then
    echo "[*] Installing Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
fi
sudo systemctl enable --now tailscaled.service

# 2. Harden OpenSSH Server & Enable X11Forwarding
sudo mkdir -p /etc/ssh/sshd_config.d
sudo cp -f "${REPO_ROOT}/configs/ssh/99-kali-custom.conf" /etc/ssh/sshd_config.d/99-kali-custom.conf
sudo chmod 0644 /etc/ssh/sshd_config.d/99-kali-custom.conf
sudo sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?KbdInteractiveAuthentication .*/KbdInteractiveAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?X11Forwarding .*/X11Forwarding yes/' /etc/ssh/sshd_config
grep -q '^ClientAliveInterval' /etc/ssh/sshd_config || echo "ClientAliveInterval 120" | sudo tee -a /etc/ssh/sshd_config >/dev/null
sudo systemctl enable --now ssh.service
sudo systemctl reload ssh.service || true

# 3. Configure ~/.ssh/authorized_keys, ~/.ssh/config (with Host termux & Host colab-gpu), and Ed25519 keypair
mkdir -p "${HOME}/.ssh"
chmod 0700 "${HOME}/.ssh"

touch "${HOME}/.ssh/authorized_keys"
chmod 0600 "${HOME}/.ssh/authorized_keys"
while IFS= read -r keyline; do
    [[ -z "${keyline}" || "${keyline}" =~ ^# ]] && continue
    if ! grep -Fqx "${keyline}" "${HOME}/.ssh/authorized_keys" 2>/dev/null; then
        echo "${keyline}" >> "${HOME}/.ssh/authorized_keys"
    fi
done < "${REPO_ROOT}/configs/ssh/authorized_keys"

cp -f "${REPO_ROOT}/configs/ssh/config.template" "${HOME}/.ssh/config"
chmod 0600 "${HOME}/.ssh/config"

if [[ ! -f "${HOME}/.ssh/id_ed25519" ]]; then
    echo "[*] Generating fresh Ed25519 SSH keypair for this Kali VPS..."
    ssh-keygen -t ed25519 -C "kali-custom-vps" -f "${HOME}/.ssh/id_ed25519" -N ""
fi
chmod 0600 "${HOME}/.ssh/id_ed25519"
chmod 0644 "${HOME}/.ssh/id_ed25519.pub"

# 4. Deploy helper scripts and guides to /home/kali
cp -f "${REPO_ROOT}/scripts/home-scripts/debian-ssh-client-setup.sh" "${HOME}/debian-ssh-client-setup.sh"
chmod 0755 "${HOME}/debian-ssh-client-setup.sh"
cp -f "${REPO_ROOT}/scripts/home-scripts/HOW_TO_SEND_FILES_TO_TERMUX" "${HOME}/HOW_TO_SEND_FILES_TO_TERMUX"
cp -f "${REPO_ROOT}/scripts/home-scripts/HOW_TO_SEND_FILES_TO_TERMUX" "${HOME}/.ssh/HOW_TO_SEND_FILES_TO_TERMUX"
cp -f "${REPO_ROOT}/scripts/home-scripts/steps.txt" "${HOME}/steps.txt"

echo "[+] Module 04 complete: Tailscale daemon, SSHD X11/Key-auth hardening, and Host blocks (termux, colab-gpu) configured."
