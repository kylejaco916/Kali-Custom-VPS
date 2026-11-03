# `ffuf-replay` — Noise-Free Web Fuzzer (Matched Hits Only to Caido)

## Overview
- **Binary Location**: `/usr/local/bin/ffuf-replay`
- **Underlying Tool**: `ffuf` (`2.1.0-dev`) + `SecLists` (`$SECLISTS` = `/usr/share/seclists`)
- **Burp Suite Equivalent**: Content Discovery / Intruder with filtered result forwarding
- **Underlying Command**: `/usr/bin/ffuf -replay-proxy http://127.0.0.1:8080 "$@"`

## What It Does
Runs `ffuf` directly against the target at maximum speed and **only replays matched requests** (after `-mc` / `-fc` / `-fs` / `-fw` filtering) into Caido (`http://127.0.0.1:8080`) via `-replay-proxy`.
- Prevents flooding Caido (and ZAP when chained) with tens of thousands of `404 Not Found` responses during large SecLists fuzzing runs.
- Every valid endpoint or hit immediately appears in Caido's HTTP History and Sitemap ready to send to Replay (Repeater).

---

## Usage & PortSwigger Lab Examples

### 1. High-Speed Endpoint Discovery (Only Send Hits to Caido)
```bash
ffuf-replay -w "$SECLISTS/Discovery/Web-Content/common.txt" \
  -u "https://YOUR-LAB-ID.web-security-academy.net/FUZZ" \
  -mc 200,301,302,403
```

### 2. Virtual Host / Subdomain Fuzzing (Filter by Response Size)
```bash
ffuf-replay -w "$SECLISTS/Discovery/DNS/subdomains-top1million-5000.txt" \
  -u "https://YOUR-LAB-ID.web-security-academy.net/" \
  -H "Host: FUZZ.web-security-academy.net" \
  -fs 4215
```

---

## Annotated Script Source
```bash
#!/usr/bin/env bash
# ==============================================================================
# Command: ffuf-replay
# Purpose: Execute ffuf directly at full speed and replay ONLY matched/filtered
#          hits into Caido (http://127.0.0.1:8080) via '-replay-proxy'.
# ==============================================================================
exec /usr/bin/ffuf -replay-proxy http://127.0.0.1:8080 "$@"
```
