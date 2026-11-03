# `nuclei-caido` — Active Vulnerability Scanner (Routed Through Caido)

## Overview
- **Binary Location**: `/usr/local/bin/nuclei-caido`
- **Underlying Tool**: `nuclei` (`v3.11.1`) + `nuclei-templates` (`/home/kali/.local/nuclei-templates`)
- **Burp Suite Equivalent**: Burp Suite Professional Active Vulnerability Scanner & BChecks
- **Underlying Command**: `/usr/bin/nuclei -proxy http://127.0.0.1:8080 "$@"`

## What It Does
Executes ProjectDiscovery's `nuclei` engine using updated YAML templates while routing all template probes and exploit checks through Caido (`http://127.0.0.1:8080`) via `-proxy http://127.0.0.1:8080`.
- Every vulnerability check sent by `nuclei` is logged in Caido's HTTP History so you can inspect the exact raw HTTP request/response or send a finding directly to Caido Replay (Repeater) to manually customize the payload.

---

## Usage & PortSwigger Lab Examples

### 1. Run Generic Web Vulnerability Templates (XSS, SQLi, SSRF, LFI, SSTI)
```bash
nuclei-caido -u "https://YOUR-LAB-ID.web-security-academy.net" \
  -tags xss,sqli,ssrf,lfi,ssti,xxe
```

### 2. Scan with DAST / Fuzzing Templates on Crawled URLs with Parameters
```bash
katana-caido -u "https://YOUR-LAB-ID.web-security-academy.net" -silent | \
  nuclei-caido -dast -H "Cookie: session=YOUR_SESSION_COOKIE"
```

### 3. Scan for Misconfigurations, Exposures & CVEs
```bash
nuclei-caido -u "https://YOUR-LAB-ID.web-security-academy.net" \
  -t exposures/ -t misconfiguration/ -t cves/
```

---

## Annotated Script Source
```bash
#!/usr/bin/env bash
# ==============================================================================
# Command: nuclei-caido
# Purpose: Run Nuclei vulnerability scanner with all HTTP traffic routed through
#          Caido (http://127.0.0.1:8080) using '-proxy'.
# ==============================================================================
exec /usr/bin/nuclei -proxy http://127.0.0.1:8080 "$@"
```
