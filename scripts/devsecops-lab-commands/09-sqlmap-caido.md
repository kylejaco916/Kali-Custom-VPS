# `sqlmap-caido` — Automated SQL Injection Scanner & Exploiter

## Overview
- **Binary Location**: `/usr/local/bin/sqlmap-caido`
- **Underlying Tool**: `sqlmap` (`1.10.8#stable`, `/usr/bin/sqlmap`)
- **Burp Suite Equivalent**: Burp Pro SQLi Active Scanner + SQLiPy / CO2 Extension
- **Underlying Command**: `/usr/bin/sqlmap --proxy="http://127.0.0.1:8080" "$@"`

## What It Does
Runs `sqlmap` with `--proxy="http://127.0.0.1:8080"` pre-configured so every boolean-blind, time-based, error-based, and UNION-based SQL injection payload is captured inside Caido (`127.0.0.1:8080`).
- Allows you to watch the exact SQLi payloads `sqlmap` uses to solve PortSwigger SQLi labs and replay or tweak them manually in Caido Replay.

---

## Usage & PortSwigger Lab Examples

### 1. Test a URL Parameter (e.g., PortSwigger `category` Filter SQLi)
```bash
sqlmap-caido -u "https://YOUR-LAB-ID.web-security-academy.net/filter?category=Gifts" \
  --batch --dbs
```

### 2. Test a Cookie Parameter (e.g., PortSwigger `TrackingId` Blind SQLi Lab)
```bash
sqlmap-caido -u "https://YOUR-LAB-ID.web-security-academy.net/" \
  --cookie="TrackingId=xyz123; session=YOUR_SESSION_COOKIE" \
  -p TrackingId \
  --level=2 --batch --dump -T users
```

### 3. Test from a Raw HTTP Request Saved from Caido (`req.txt`)
```bash
sqlmap-caido -r req.txt --batch --current-user --dbs
```

---

## Annotated Script Source
```bash
#!/usr/bin/env bash
# ==============================================================================
# Command: sqlmap-caido
# Purpose: Execute sqlmap with '--proxy=http://127.0.0.1:8080' so all SQLi
#          detection and exploitation payloads are visible in Caido.
# ==============================================================================
exec /usr/bin/sqlmap --proxy="http://127.0.0.1:8080" "$@"
```
