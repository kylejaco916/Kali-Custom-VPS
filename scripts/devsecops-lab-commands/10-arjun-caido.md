# `arjun-caido` — Hidden HTTP Parameter Discovery (Param Miner Replacement)

## Overview
- **Binary Location**: `/usr/local/bin/arjun-caido`
- **Underlying Tool**: `arjun` (`2.2.7`, `/usr/bin/arjun`)
- **Burp Suite Equivalent**: Burp Param Miner Extension
- **Underlying Command**: `PYTHONWARNINGS="ignore:Unverified HTTPS request" HTTP_PROXY="http://127.0.0.1:8080" HTTPS_PROXY="http://127.0.0.1:8080" /usr/bin/arjun -oB 127.0.0.1:8080 "$@"`

## What It Does
Discovers unlinked/hidden `GET`, `POST` (form-urlencoded), `JSON`, and `XML` parameters using heuristic chunking (finding ~25,000 parameter names in ~50 requests) and automatically forwards valid discovered parameters to Caido (`127.0.0.1:8080`) via `-oB 127.0.0.1:8080`.

---

## Usage & PortSwigger Lab Examples

### 1. Discover Hidden `GET` Parameters on an Endpoint
```bash
arjun-caido -u "https://YOUR-LAB-ID.web-security-academy.net/"
```

### 2. Discover Hidden `POST` or `JSON` Parameters
```bash
arjun-caido -u "https://YOUR-LAB-ID.web-security-academy.net/api/user" -m JSON
```

### 3. Pass Custom Session Cookie / Headers During Discovery
```bash
arjun-caido -u "https://YOUR-LAB-ID.web-security-academy.net/admin" \
  --headers "Cookie: session=YOUR_SESSION_COOKIE"
```

---

## Annotated Script Source
```bash
#!/usr/bin/env bash
# ==============================================================================
# Command: arjun-caido
# Purpose: Discover hidden HTTP GET/POST/JSON parameters (Burp Param Miner
#          equivalent) and forward discovered parameter requests into Caido
#          (127.0.0.1:8080) via '-oB 127.0.0.1:8080'.
# ==============================================================================
PYTHONWARNINGS="ignore:Unverified HTTPS request" \
HTTP_PROXY="http://127.0.0.1:8080" \
HTTPS_PROXY="http://127.0.0.1:8080" \
exec /usr/bin/arjun -oB 127.0.0.1:8080 "$@"
```
