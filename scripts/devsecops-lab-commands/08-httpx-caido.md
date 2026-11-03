# `httpx-caido` — HTTP Prober & Tech-Stack Fingerprinter

## Overview
- **Binary Location**: `/usr/local/bin/httpx-caido`
- **Underlying Tool**: `httpx` (`v1.9.0`, `/usr/local/bin/httpx`)
- **Burp Suite Equivalent**: Target Site Map Analyzer / Wappalyzer Tech Fingerprinting
- **Underlying Command**: `/usr/local/bin/httpx -proxy http://127.0.0.1:8080 "$@"`

## What It Does
Probes URLs, lists of endpoints, or crawled paths for HTTP status codes, content lengths, page titles, server headers, and technology stacks (`-td`), while sending every probe through Caido (`http://127.0.0.1:8080`) so valid endpoints populate Caido's HTTP History.

---

## Usage & PortSwigger Lab Examples

### 1. Probe Target URL with Tech Detection, Title, and Status Code
```bash
httpx-caido -u "https://YOUR-LAB-ID.web-security-academy.net" -sc -title -td -cl
```

### 2. Pipe Katana Crawl Results into `httpx-caido`
```bash
katana -u "https://YOUR-LAB-ID.web-security-academy.net" -jc -silent | \
  httpx-caido -sc -title -cl
```

---

## Annotated Script Source
```bash
#!/usr/bin/env bash
# ==============================================================================
# Command: httpx-caido
# Purpose: Probe HTTP endpoints and technologies with ProjectDiscovery httpx
#          while routing all probes into Caido (http://127.0.0.1:8080).
# ==============================================================================
exec /usr/local/bin/httpx -proxy http://127.0.0.1:8080 "$@"
```
