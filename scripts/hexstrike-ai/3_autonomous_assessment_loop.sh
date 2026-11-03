#!/usr/bin/env bash
# KALI <-> HEADLESS COLAB TAILSCALE 3-PHASE ASSESSMENT ORCHESTRATOR
# Usage: ./3_autonomous_assessment_loop.sh <authorized_target_scope> [colab_tailscale_host|--mock-test]
set -euo pipefail

TARGET="${1:-}"
COLAB_HOST="${2:-colab-gpu}"
STATIC_URL="http://${COLAB_HOST}:8085"
[[ "${COLAB_HOST}" == "--mock-test" ]] && STATIC_URL="http://127.0.0.1:18085"

HEX_DIR="${HOME}/hexstrike-ai"
MCP_CFG="${HOME}/.config/hermes/config.json"
LOG_DIR="${HEX_DIR}/logs/assessment_$(date +%Y%m%d_%H%M%S)"

if [[ -z "${TARGET}" ]]; then
    echo "Usage: $0 <authorized_target_scope> [colab_host|--mock-test]"
    exit 1
fi
mkdir -p "${LOG_DIR}"

if ! curl -fsSL --max-time 3 "${STATIC_URL}/health" 2>/dev/null | grep -q "ok"; then
    "${HEX_DIR}/2_kali_gpu_controller.sh" 0 "${COLAB_HOST}"
fi

MODEL_ID=$(jq -r '.model.default // "default"' "${MCP_CFG}" 2>/dev/null || echo "default")
SUMMARY="${LOG_DIR}/rolling_assessment_state.md"
printf "# Authorized Scope: %s | Model: %s | %s\n" "${TARGET}" "${MODEL_ID}" "$(date -u +%FT%TZ)" > "${SUMMARY}"

PHASES=(
    "Phase 1 (Surface & Service Enumeration): Enumerate exposed ports, active services, and TLS/HTTP metadata for authorized scope '${TARGET}'. Output a concise Markdown inventory."
    "Phase 2 (Configuration & Endpoint Auditing): Analyze discovered services, HTTP security headers, and exposed paths on '${TARGET}' for security misconfigurations. Summarize findings concisely."
    "Phase 3 (Vulnerability Correlation & Remediation Report): Correlate service versions and configuration findings on '${TARGET}' against known CVEs and security best practices. Produce a structured report with Executive Summary, Technical Observations, Risk Ratings, and Remediation Steps."
)

for idx in "${!PHASES[@]}"; do
    P_NUM=$((idx + 1))
    CTX=$(tail -c 12000 "${SUMMARY}")
    PROMPT="Prior Context:\n${CTX}\n\nTask:\n${PHASES[$idx]}"
    echo "[*] Executing Phase ${P_NUM}/3 via ${STATIC_URL} ..."
    if [[ "${COLAB_HOST}" != "--mock-test" ]] && command -v hermes >/dev/null 2>&1; then
        hermes --config "${MCP_CFG}" --prompt "${PROMPT}" | tee "${LOG_DIR}/phase_${P_NUM}.md"
    else
        jq -n --arg m "${MODEL_ID}" --arg p "${PROMPT}" \
            '{model:$m, temperature:0.1, repeat_penalty:1.15, max_tokens:2048, messages:[{role:"user",content:$p}]}' \
            | curl -fsSL "${STATIC_URL}/v1/chat/completions" -H "Content-Type: application/json" -d @- \
            | jq -r '.choices[0].message.content // empty' | tee "${LOG_DIR}/phase_${P_NUM}.md"
    fi
    printf "\n## Phase %d Findings\n%s\n" "${P_NUM}" "$(cat "${LOG_DIR}/phase_${P_NUM}.md")" >> "${SUMMARY}"
done
echo "[+] Assessment complete! Report: ${SUMMARY}"
