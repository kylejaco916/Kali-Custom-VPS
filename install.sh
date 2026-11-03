#!/usr/bin/env bash
# ==============================================================================
# Kali-Custom-VPS: Master Automated Unpacking & Replication Installer
# Repository: https://github.com/kylejaco916/Kali-Custom-VPS
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export SKIP_METAPACKAGES=0
ONLY_MODULE=""
VERIFY_ONLY=0

usage() {
    cat << 'EOF'
Usage: ./install.sh [OPTIONS]

Automated one-command unpacking and replication installer for Kali-Custom-VPS.

Options:
  --skip-metapackages   Skip the 5-batch 28 kali-tools-* APT download if already installed
  --only <01..09>       Run only a specific provisioning module (e.g., --only 08)
  --verify              Run only the verification and E2E test suite (Module 09)
  -h, --help            Display this help message
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-metapackages|--fast)
            export SKIP_METAPACKAGES=1
            shift
            ;;
        --only|--module)
            ONLY_MODULE="${2:-}"
            shift 2
            ;;
        --verify)
            VERIFY_ONLY=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
    esac
done

chmod +x "${REPO_ROOT}/modules/"*.sh

if [[ "${VERIFY_ONLY}" -eq 1 ]]; then
    exec "${REPO_ROOT}/modules/09-verify.sh"
fi

if [[ -n "${ONLY_MODULE}" ]]; then
    TARGET_SCRIPT=$(ls "${REPO_ROOT}/modules/${ONLY_MODULE}"*.sh 2>/dev/null | head -n 1 || true)
    if [[ -z "${TARGET_SCRIPT}" ]]; then
        echo "[-] Module '${ONLY_MODULE}' not found in ${REPO_ROOT}/modules/" >&2
        exit 1
    fi
    exec "${TARGET_SCRIPT}"
fi

echo "=============================================================================="
echo " Starting Full Kali-Custom-VPS Automated Replication"
echo "=============================================================================="
if ! sudo -n true 2>/dev/null; then
    sudo -v
fi

for mod in "${REPO_ROOT}/modules/"0[1-9]-*.sh; do
    "${mod}"
done

echo ""
echo "=============================================================================="
echo " [+] KALI-CUSTOM-VPS REPLICATION COMPLETE!"
echo "=============================================================================="
echo " Next Steps on a Brand-New VPS:"
echo "   1. Reload shell:     source ~/.zshrc"
echo "   2. Join Tailscale:   sudo tailscale up --ssh --accept-routes"
echo "   3. Check Lab Proxy:  proxy-toggle status"
echo "   4. Colab GPU Sync:   ~/hexstrike-ai/2_kali_gpu_controller.sh 0"
echo "=============================================================================="
