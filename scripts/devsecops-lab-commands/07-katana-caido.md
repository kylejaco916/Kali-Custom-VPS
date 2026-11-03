# `katana-caido` — Modern JS & Headless Web Crawler

## Overview
- **Binary Location**: `/usr/local/bin/katana-caido`
- **Underlying Tool**: `katana` (`v1.7.0`, `/usr/bin/katana`)
- **Burp Suite Equivalent**: Burp Suite Crawler (Standard + Headless Chromium JS Spider)
- **Underlying Command**: `/usr/bin/katana -proxy http://127.0.0.1:8080 "$@"`

## What It Does
Crawls modern single-page applications (SPAs) and standard web apps, parsing JavaScript files for hidden API routes and automatically feeding every discovered URL and form into Caido (`127.0.0.1:8080`) — and into OWASP ZAP (`127.0.0.1:8081`) when `proxy-chain` is enabled.

---

## Usage & PortSwigger Lab Examples

### 1. Standard Crawl with JavaScript Endpoint Parsing (`-jc`)
```bash
katana-caido -u "https://YOUR-LAB-ID.web-security-academy.net" -jc -kf all
```

### 2. Headless Browser Crawl for Heavy Client-Side JS / DOM Labs (`-hl`)
```bash
katana-caido -u "https://YOUR-LAB-ID.web-security-academy.net" -hl -jc -d 3
```

### 3. Authenticated Crawl Using Session Cookie
```bash
katana-caido -u "https://YOUR-LAB-ID.web-security-academy.net" \
  -jc \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

---

## Annotated Script Source
```bash
#!/usr/bin/env bash
# ==============================================================================
# Command: katana-caido
# Purpose: Crawl targets with katana and route all requests through Caido
#          (http://127.0.0.1:8080) to populate Caido/ZAP sitemaps automatically.
# ==============================================================================
exec /usr/bin/katana -proxy http://127.0.0.1:8080 "$@"
```
