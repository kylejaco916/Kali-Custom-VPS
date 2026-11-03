# `ffuf-caido` — Unthrottled Web Fuzzer (All Traffic Routed to Caido)

## Overview
- **Binary Location**: `/usr/local/bin/ffuf-caido`
- **Underlying Tool**: `ffuf` (`2.1.0-dev`) + `SecLists` (`$SECLISTS` = `/usr/share/seclists`)
- **Burp Suite Equivalent**: Burp Intruder (Unthrottled Community/Pro replacement) with full proxy logging
- **Underlying Command**: `/usr/bin/ffuf -x http://127.0.0.1:8080 "$@"`

## What It Does
Runs `ffuf` at full multi-threaded speed while routing **every request and response** through Caido on `http://127.0.0.1:8080` via the `-x` proxy flag.
- Useful when fuzzing authentication endpoints, small wordlists, parameter values, or IDOR numeric ranges where you want to inspect both successful and failed responses inside Caido's HTTP History.
- *(Tip: If you are running a massive directory brute-force and only want 200/301 hits sent to Caido, use [`ffuf-replay`](./04-ffuf-replay.md) instead).*

---

## Usage & PortSwigger Lab Examples

### 1. Directory & File Discovery with SecLists
```bash
ffuf-caido -w "$SECLISTS/Discovery/Web-Content/raft-small-words.txt" \
  -u "https://YOUR-LAB-ID.web-security-academy.net/FUZZ" \
  -mc 200,204,301,302,307,401,403
```

### 2. Brute-Forcing Login Passwords / 2FA Codes (Intruder Sniper Replacement)
```bash
ffuf-caido -w "$SECLISTS/Passwords/Common-Credentials/10k-most-common.txt" \
  -u "https://YOUR-LAB-ID.web-security-academy.net/login" \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=carlos&password=FUZZ" \
  -fc 200
```

### 3. Fuzzing Numeric IDOR / BOLA Identifiers
```bash
seq 1 200 | ffuf-caido -w - \
  -u "https://YOUR-LAB-ID.web-security-academy.net/my-account?id=FUZZ" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -mc 200
```

---

## Annotated Script Source
```bash
#!/usr/bin/env bash
# ==============================================================================
# Command: ffuf-caido
# Purpose: Route all ffuf fuzzing requests through Caido (http://127.0.0.1:8080)
#          using the '-x' HTTP proxy flag.
# ==============================================================================
exec /usr/bin/ffuf -x http://127.0.0.1:8080 "$@"
```
