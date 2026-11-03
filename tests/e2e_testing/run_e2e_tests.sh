#!/usr/bin/env bash
#
# Master E2E Test Suite Runner for 28 kali-tools-* Metapackage Suite Deployment
#

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_RUNNER="${SCRIPT_DIR}/test_runner.py"

if [ ! -f "${PYTHON_RUNNER}" ]; then
    echo "Error: Test runner engine not found at ${PYTHON_RUNNER}" >&2
    exit 2
fi

exec python3 "${PYTHON_RUNNER}" "$@"
