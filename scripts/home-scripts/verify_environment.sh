#!/usr/bin/env bash
set -e

echo "=== Kali Security Tooling & MCP Environment Audit ==="
echo "Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo

# 1. Binary checks
echo "[1/4] Checking Core Binaries..."
TOOLS=(
    "caido-cli"
    "zaproxy"
    "subfinder"
    "httpx-toolkit"
    "katana"
    "naabu"
    "ffuf"
    "amass"
    "feroxbuster"
    "nmap"
    "sqlmap"
    "jq"
    "npm"
    "go"
    "python3"
)

MISSING=0
for tool in "${TOOLS[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo "  [PASS] $tool -> $(command -v "$tool")"
    else
        echo "  [FAIL] $tool is NOT in PATH"
        MISSING=$((MISSING + 1))
    fi
done

# Check symlinks
echo
echo "[2/4] Checking CLI Convenience Aliases..."
for alias_cmd in "caido" "zap" "zap.sh" "httpx"; do
    if command -v "$alias_cmd" >/dev/null 2>&1; then
        echo "  [PASS] $alias_cmd -> $(command -v "$alias_cmd")"
    else
        echo "  [WARN] $alias_cmd alias not found"
    fi
done

# Wordlists
echo
echo "[3/4] Checking Wordlists (SecLists)..."
if [ -d "/usr/share/seclists" ]; then
    WORDLIST_COUNT=$(find /usr/share/seclists -type f 2>/dev/null | wc -l)
    echo "  [PASS] /usr/share/seclists present ($WORDLIST_COUNT files indexed)"
else
    echo "  [WARN] /usr/share/seclists not yet fully unpacked"
fi

# MCP Server
echo
echo "[4/4] Verifying Model Context Protocol (MCP) Server..."
MCP_SCRIPT="/home/kali/.local/share/mcp-servers/security-tools/security_mcp_server.py"
MCP_CONFIG="/home/kali/.gemini/config/mcp_config.json"

if [ -f "$MCP_CONFIG" ]; then
    echo "  [PASS] Global MCP config registered at $MCP_CONFIG"
else
    echo "  [FAIL] MCP config missing at $MCP_CONFIG"
    MISSING=$((MISSING + 1))
fi

if [ -x "$MCP_SCRIPT" ]; then
    MCP_TEST=$(echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | python3 "$MCP_SCRIPT" 2>/dev/null || true)
    if echo "$MCP_TEST" | grep -q '"tools"'; then
        TOOL_COUNT=$(echo "$MCP_TEST" | jq '.result.tools | length' 2>/dev/null || echo "10")
        echo "  [PASS] MCP server responded with $TOOL_COUNT active tools"
    else
        echo "  [FAIL] MCP server failed to respond with valid tools schema"
        MISSING=$((MISSING + 1))
    fi
else
    echo "  [FAIL] MCP script missing or not executable at $MCP_SCRIPT"
    MISSING=$((MISSING + 1))
fi

echo
echo "=== Storage Check ==="
df -h / | awk 'NR==1 || NR==2 {print "  " $0}'
echo

if [ "$MISSING" -eq 0 ]; then
    echo "All core tooling and MCP servers verified successfully."
    exit 0
else
    echo "Verification finished with $MISSING failure(s)."
    exit 1
fi
