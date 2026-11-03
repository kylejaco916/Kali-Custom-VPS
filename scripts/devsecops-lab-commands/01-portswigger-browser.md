# `portswigger-browser` — Dedicated Lab Browser Launcher

## Overview
- **Binary Location**: `/usr/local/bin/portswigger-browser` (Source: `/home/kali/.local/share/devsecops-lab/bin/portswigger-browser`)
- **Profile Path**: `/home/kali/.mozilla/firefox/portswigger-lab`
- **Certificate Database**: `/home/kali/.mozilla/firefox/portswigger-lab/cert9.db`
- **Burp Suite Equivalent**: Burp's built-in pre-configured Chromium browser

## What It Does
Launches Firefox ESR using a dedicated, isolated lab profile (`portswigger-lab`) with `--no-remote` so it can run alongside any personal browser session without mixing cookies, history, or proxy settings.

### Pre-Configured Profile Features (`user.js` & `cert9.db`)
1. **Zero Certificate Warnings (Out-of-the-Box HTTPS Interception)**:
   - Both `Caido Root CA` and `OWASP ZAP Root CA` are imported with `CT,C,C` trust flags inside `/home/kali/.mozilla/firefox/portswigger-lab/cert9.db`.
2. **Pre-Wired Local Proxy**:
   - Configured to route HTTP and HTTPS traffic through `127.0.0.1:8080` (Caido) by default, including `network.proxy.allow_hijacking_localhost = true` for local Docker/DevSecOps targets.
3. **Container Tabs Enabled**:
   - Firefox Multi-Account Containers (`privacy.userContext.enabled = true`) are enabled out of the box for testing horizontal/vertical privilege escalation (IDOR / BAC) across multiple user sessions in adjacent color-coded tabs.
4. **Clean Proxy History (Noise Suppression)**:
   - Disables Firefox captive portal checks (`detectportal.firefox.com`), telemetry, and SafeBrowsing background requests so your Caido and ZAP HTTP histories only show actual lab traffic.

---

## Usage & Examples

### 1. Launch Default PortSwigger All-Labs Page
```bash
portswigger-browser
```

### 2. Launch Directly to a Specific Lab URL
```bash
portswigger-browser "https://0a1b2c3d.web-security-academy.net/"
```

### 3. Verify Trusted Root Certificates in the Profile
```bash
certutil -L -d sql:/home/kali/.mozilla/firefox/portswigger-lab
```

---

## Annotated Script Source
```bash
#!/usr/bin/env bash
# ==============================================================================
# Command: portswigger-browser
# Purpose: Launch Firefox ESR with the isolated 'portswigger-lab' profile.
#          Pre-configured with Caido & ZAP Root CAs in cert9.db, Container Tabs,
#          noise-free telemetry settings, and proxy routing.
# ==============================================================================

PROFILE_DIR="/home/kali/.mozilla/firefox/portswigger-lab"

# --profile : Forces Firefox to use the dedicated lab profile directory
# --no-remote: Allows running a separate Firefox instance alongside other profiles
# Default URL: Opens PortSwigger Web Security Academy labs list if no URL argument is passed
exec /usr/bin/firefox --profile "$PROFILE_DIR" --no-remote "${@:-https://portswigger.net/web-security/all-labs}"
```
