# `interactsh-caido` — Out-of-Band (OAST) Collaborator Client

## Overview
- **Binary Location**: `/usr/local/bin/interactsh-caido`
- **Underlying Tool**: `interactsh-client` (`v1.4.1`, `/usr/local/bin/interactsh-client`)
- **Burp Suite Equivalent**: Burp Collaborator Client
- **OWASP ZAP Integration**: Wired into ZAP's OAST add-on (`oast-beta-0.26.0.zap`) on `127.0.0.1:8081` (`oast.activeScanService=Interactsh`, `serverUrl=https://oast.pro`, `pollInSecs=10`)

## What It Does
Generates unique Out-of-Band (OAST) `.oast.pro` / `.oast.live` / `.oast.site` subdomains and polls for incoming DNS, HTTP, HTTPS, SMTP, and LDAP interactions in real time, routing client polling traffic through Caido (`http://127.0.0.1:8080`).
- Essential for blind vulnerabilities in PortSwigger labs:
  - Blind SSRF
  - Blind XXE (XML External Entity)
  - Blind OS Command Injection (DNS/HTTP exfiltration)
  - Blind SQL Injection (Out-of-Band DNS lookup via `EXTRACTVALUE`, `xp_dirtree`, `COPY`)
  - Blind XSS / Asynchronous RCE

---

## Usage & PortSwigger Lab Examples

### 1. Start Interactive OAST Session (Generates Copy-Pasteable `.oast.*` Domain)
```bash
interactsh-caido
```

### 2. Filter Only DNS or HTTP Interactions & Save Output to File
```bash
interactsh-caido -dns-only -o oast-dns-hits.txt
```

### 3. Check OWASP ZAP's Built-in Interactsh OAST Service Status
```bash
curl -s "http://127.0.0.1:8081/JSON/oast/view/getActiveScanService/"
curl -s "http://127.0.0.1:8081/JSON/oast/view/getInteractshOptions/"
```

---

## Annotated Script Source
```bash
#!/usr/bin/env bash
# ==============================================================================
# Command: interactsh-caido
# Purpose: Run ProjectDiscovery interactsh-client (Burp Collaborator equivalent)
#          with HTTP_PROXY/HTTPS_PROXY routed through Caido (127.0.0.1:8080).
# ==============================================================================
HTTP_PROXY="http://127.0.0.1:8080" HTTPS_PROXY="http://127.0.0.1:8080" exec /usr/local/bin/interactsh-client "$@"
```
