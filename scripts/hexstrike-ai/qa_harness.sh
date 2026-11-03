#!/usr/bin/env bash
export QA_FILE="${HOME}/hexstrike-ai/QA_AUDIT_REPORT.md"

init_qa() {
    cat << HEADER > "${QA_FILE}"
# KALI <-> HEADLESS COLAB QA TELEMETRY AUDIT (TOKEN-COMPRESSED)
- **Timestamp**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- **Host/OS**: $(uname -srm) | $(grep -E '^PRETTY_NAME=' /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"' || echo "Linux")
- **User/UID**: $(whoami) (${EUID})
---
## 1. EXECUTION & I/O TELEMETRY LOG
HEADER
}

qa_exec() {
    local step_id="$1"
    local cmd_str="$2"
    local tmp_out="/tmp/qa_out_$$.txt"
    local start_ms
    start_ms=$(date +%s%3N 2>/dev/null || date +%s)

    printf "    -> Running [%s] ... " "${step_id}"

    # Disable errexit and pipefail across the entire QA capture & filter block
    set +e
    set +o pipefail
    eval "${cmd_str}" > "${tmp_out}" 2>&1
    local rc=$?

    local end_ms
    end_ms=$(date +%s%3N 2>/dev/null || date +%s)
    local dur=$((end_ms - start_ms))

    # Pure awk + sed sanitizer (never returns exit code 1 on empty output)
    local clean_out
    clean_out=$(sed -E 's/\x1B\[[0-9;]*[a-zA-Z]//g; s/\r//g' "${tmp_out}" 2>/dev/null \
        | awk '!/^(Reading database|\(Reading database|Preparing to unpack|Unpacking |Selecting previously|Get:[0-9]+|Fetched [0-9]+|Hit:[0-9]+|Ign:[0-9]+|[[:space:]]*$)/ {
            lines[++c] = $0
        } END {
            if (c <= 20) {
                for (i = 1; i <= c; i++) print lines[i]
            } else {
                for (i = 1; i <= 10; i++) print lines[i]
                print "... [TRUNCATED " (c - 20) " VERBOSE LINES] ..."
                for (i = c - 9; i <= c; i++) print lines[i]
            }
        }' || true)

    cat << LOG >> "${QA_FILE}"
### [${step_id}] RC=${rc} (${dur}ms)
- **IN**: \`${cmd_str}\`
- **OUT**:
\`\`\`text
${clean_out:-<EMPTY_STDOUT>}
\`\`\`
LOG
    rm -f "${tmp_out}"
    printf "DONE (RC=%d, %dms)\n" "${rc}" "${dur}"
    set -e
    set -o pipefail
    return 0
}
