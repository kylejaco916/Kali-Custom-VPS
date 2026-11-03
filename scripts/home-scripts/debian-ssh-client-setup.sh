#!/bin/bash
set -euo pipefail

# Ensure ~/.ssh exists on client
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

# Ensure config file exists with secure permissions
touch "$HOME/.ssh/config"
chmod 600 "$HOME/.ssh/config"

# Check if host block already exists
if grep -q "Host kali" "$HOME/.ssh/config" 2>/dev/null; then
    echo "Entry for 'Host kali' already exists in ~/.ssh/config."
else
    cat << 'CONFIG_BLOCK' >> "$HOME/.ssh/config"

Host kali
    HostName 167.234.221.173
    User kali
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ForwardX11 yes
    ForwardX11Trusted yes
CONFIG_BLOCK
    echo "Added 'Host kali' block to ~/.ssh/config."
fi

# Fix key permissions if the default ed25519 file exists
if [ -f "$HOME/.ssh/id_ed25519" ]; then
    chmod 600 "$HOME/.ssh/id_ed25519"
    echo "Set permissions 600 on ~/.ssh/id_ed25519."
fi

echo "Setup complete! You can now connect by running: ssh kali"
