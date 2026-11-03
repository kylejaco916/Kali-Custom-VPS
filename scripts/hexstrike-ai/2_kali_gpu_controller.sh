#!/usr/bin/env bash
# KALI -> HEADLESS COLAB GPU CONTROLLER (OVER TAILSCALE SSH + MOCK TEST MODE)
# Usage: ./2_kali_gpu_controller.sh [model_index_0_1_or_2] [colab_tailscale_host|--mock-test]
set -euo pipefail

MODEL_IDX="${1:-0}"
COLAB_HOST="${2:-colab-gpu}"
HEX_DIR="${HOME}/hexstrike-ai"
MCP_CFG="${HOME}/.config/hermes/config.json"
CLAUDE_MCP="${HEX_DIR}/.mcp.json"
NODE_JSON="/tmp/node_info.json"

mkdir -p "${HEX_DIR}" "$(dirname "${MCP_CFG}")"

if [[ "${COLAB_HOST}" == "--mock-test" ]]; then
    echo "[*] Running in local QA Mock-Test mode..."
    STRIKE_MODEL_IDX="${MODEL_IDX}" python3 "${HEX_DIR}/1_colab_orchestrator.py" --dry-run | tail -n 1 > "${NODE_JSON}"
    STATIC_URL="http://127.0.0.1:18085"
else
    echo "[*] Verifying Tailscale SSH connectivity to ${COLAB_HOST}:2222..."
    if ! ssh -p 2222 -o ConnectTimeout=5 "root@${COLAB_HOST}" "echo '[+] SSH Handshake OK'"; then
        echo "[-] Cannot reach ${COLAB_HOST} over Tailscale. Ensure the 5-line Colab bootstrap cell is running."
        exit 1
    fi
    echo "[*] Pushing 1_colab_orchestrator.py to ${COLAB_HOST} and loading Model Index [${MODEL_IDX}]..."
    scp -P 2222 -q "${HEX_DIR}/1_colab_orchestrator.py" "root@${COLAB_HOST}:/content/1_colab_orchestrator.py"
    ssh -p 2222 "root@${COLAB_HOST}" "STRIKE_MODEL_IDX=${MODEL_IDX} python3 /content/1_colab_orchestrator.py" | tail -n 1 > "${NODE_JSON}"
    STATIC_URL="http://${COLAB_HOST}:8085"
fi

MODEL_ID=$(jq -r '.hf_repo // .model_id // "default"' "${NODE_JSON}")
PROFILE=$(jq -r '.profile // "Unknown"' "${NODE_JSON}")
CTX=$(jq -r '.context_tokens // 65536' "${NODE_JSON}")

echo "[+] Hardware Profile : ${PROFILE} | Model: ${MODEL_ID} (${CTX} ctx)"
echo "[*] Polling VRAM readiness at ${STATIC_URL}/health..."
for ((i=1; i<=180; i++)); do
  if curl -fsSL --max-time 4 "${STATIC_URL}/health" 2>/dev/null | grep -q "ok"; then
    echo "[+] Endpoint online at ${STATIC_URL}/health"
    break
  fi
  if [[ "${COLAB_HOST}" == "--mock-test" ]]; then :; elif (( i % 3 == 0 )); then
    STATUS_LINE=$(ssh -p 2222 "root@${COLAB_HOST}" "pgrep -a llama >/dev/null || echo DEAD; tail -n 1 /content/llama_server.log 2>/dev/null | tr '' '
' | tail -n 1" 2>/dev/null || true)
    if echo "${STATUS_LINE}" | grep -q "^DEAD"; then
      echo "[-] llama process exited on Colab. Log output:"
      ssh -p 2222 "root@${COLAB_HOST}" "tail -n 25 /content/orchestrator_setup.log /content/llama_server.log 2>/dev/null" || true
      exit 1
    fi
    echo "    [poll ${i}/180] ${STATUS_LINE}"
  fi
  sleep 2
  if [[ $i -eq 180 ]]; then
    echo "[-] Timeout waiting for llama-server at ${STATIC_URL}"
    exit 1
  fi
done

HEX_MCP="/home/kali/hexstrike-ai/hexstrike_mcp.py"
[[ ! -f "${HEX_MCP}" ]] && HEX_MCP="${HEX_DIR}/hexstrike_mcp.py"

HEX_SRV="/usr/share/hexstrike-ai/hexstrike_server.py"
[[ ! -f "${HEX_SRV}" && -f "${HEX_DIR}/hexstrike_server.py" ]] && HEX_SRV="${HEX_DIR}/hexstrike_server.py"
if [[ -f "${HEX_SRV}" ]] && ! curl -fsSL --max-time 2 http://127.0.0.1:8888/health >/dev/null 2>&1; then
    nohup python3 "${HEX_SRV}" --host 127.0.0.1 --port 8888 > "${HEX_DIR}/hexstrike_server.log" 2>&1 &
fi

jq -n \
    --arg url "${STATIC_URL}/v1" \
    --arg model "${MODEL_ID}" \
    --arg mcp_path "${HEX_MCP}" \
    '{
      model: {
        provider: "openai-compatible",
        base_url: $url,
        api_key: "sk-tailscale-mesh",
        default: $model,
        parameters: {
          temperature: 0.1,
          repeat_penalty: 1.15,
          max_tokens: 2048
        }
      },
      mcpServers: {
        "hexstrike-ai": {
          type: "stdio",
          command: "/home/kali/hexstrike-ai/hexstrike-env/bin/python3",
          args: ["-Xutf8", $mcp_path, "--server", "http://127.0.0.1:8888", "--timeout", "600"],
          disabled: false
        }
      }
    }' > "${MCP_CFG}.tmp"

mv "${MCP_CFG}.tmp" "${MCP_CFG}"
cp "${MCP_CFG}" "${CLAUDE_MCP}"
echo "[+] Atomic MCP config updated: ${MCP_CFG} -> ${STATIC_URL}/v1"
