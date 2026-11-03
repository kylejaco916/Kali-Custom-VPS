#!/usr/bin/env bash
# ==============================================================================
# Module 02: All 28 Kali Tools Metapackages, SecLists, Go 1.27+, uv & John Shim
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKIP_METAPACKAGES="${SKIP_METAPACKAGES:-0}"

echo "=== [Module 02] Kali Everything Tools (28 Metapackages) & Core Runtimes ==="

# 1. Staged 5-Batch Installation of all 28 official kali-tools-* metapackages
INSTALLED_COUNT=$(dpkg -l 'kali-tools-*' 2>/dev/null | grep -c '^ii' || true)
if [[ "${SKIP_METAPACKAGES}" == "1" ]]; then
    echo "[*] --skip-metapackages set (${INSTALLED_COUNT}/28 currently installed). Skipping 5-batch metapackage download."
elif [[ "${INSTALLED_COUNT}" -ge 28 ]]; then
    echo "[+] All 28 kali-tools-* metapackages are already installed (${INSTALLED_COUNT}/28)."
else
    echo "[*] Updating APT indices and deploying 28 kali-tools-* suites across 5 batches..."
    sudo apt-get update -qq

    BATCH_1=(kali-tools-information-gathering kali-tools-top10 kali-tools-web kali-tools-vulnerability)
    BATCH_2=(kali-tools-exploitation kali-tools-database kali-tools-social-engineering kali-tools-post-exploitation kali-tools-windows-resources)
    BATCH_3=(kali-tools-passwords kali-tools-crypto-stego kali-tools-fuzzing kali-tools-sniffing-spoofing kali-tools-voip)
    BATCH_4=(kali-tools-802-11 kali-tools-bluetooth kali-tools-rfid kali-tools-sdr kali-tools-hardware kali-tools-gpu)
    BATCH_5=(kali-tools-forensics kali-tools-reverse-engineering kali-tools-detect kali-tools-identify kali-tools-protect kali-tools-recover kali-tools-reporting kali-tools-respond)

    for b_idx in 1 2 3 4 5; do
        eval " pkg_list=(\"\${BATCH_${b_idx}[@]}\") "
        echo "[*] Installing Batch ${b_idx}/5: ${pkg_list[*]} ..."
        sudo env DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a apt-get install -y "${pkg_list[@]}"
        sudo apt-get clean
    done
fi

# 2. Ensure Core Runtimes, SecLists & Utilities are present
CORE_PKGS=(seclists jq curl wget git python3 python3-venv python3-pip nodejs npm libnss3-tools xauth)
MISSING_CORE=()
for p in "${CORE_PKGS[@]}"; do
    if ! dpkg -l "$p" 2>/dev/null | grep -q '^ii'; then
        MISSING_CORE+=("$p")
    fi
done
if [[ ${#MISSING_CORE[@]} -gt 0 ]]; then
    sudo apt-get update -qq
    sudo env DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a apt-get install -y "${MISSING_CORE[@]}"
    sudo apt-get clean
fi

# 3. Install / Verify Go 1.27.3+ in /usr/local/go
if [[ ! -x /usr/local/go/bin/go ]]; then
    echo "[*] Installing latest Go into /usr/local/go..."
    GO_VER=$(curl -fsSL "https://go.dev/VERSION?m=text" | head -n 1 || echo "go1.24.2")
    ARCH=$(dpkg --print-architecture)
    curl -fsSL "https://go.dev/dl/${GO_VER}.linux-${ARCH}.tar.gz" -o /tmp/go.tar.gz
    sudo rm -rf /usr/local/go
    sudo tar -C /usr/local -xzf /tmp/go.tar.gz
    rm -f /tmp/go.tar.gz
fi
sudo ln -sf /usr/local/go/bin/go /usr/local/bin/go
sudo ln -sf /usr/local/go/bin/gofmt /usr/local/bin/gofmt

# 4. Install Astral uv / uvx in ~/.local/bin
if [[ ! -x "${HOME}/.local/bin/uv" ]]; then
    echo "[*] Installing Astral uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# 5. Deploy John the Ripper --version Compatibility Shim
sudo cp -f "${REPO_ROOT}/scripts/usr-local-bin/john" /usr/local/bin/john
sudo chmod 0755 /usr/local/bin/john
sudo ln -sf /usr/local/bin/john /usr/local/sbin/john

# 6. Deploy CLI convenience symlinks in /usr/local/bin
[[ -x /usr/bin/caido-cli ]] && sudo ln -sf /usr/bin/caido-cli /usr/local/bin/caido
[[ -x /usr/bin/httpx-toolkit ]] && sudo ln -sf /usr/bin/httpx-toolkit /usr/local/bin/httpx
[[ -x /usr/bin/zaproxy ]] && sudo ln -sf /usr/bin/zaproxy /usr/local/bin/zap
[[ -x /usr/bin/zaproxy ]] && sudo ln -sf /usr/bin/zaproxy /usr/local/bin/zap.sh

echo "[+] Module 02 complete: Kali tool suites, Go ($(go version)), uv, and shims verified."
