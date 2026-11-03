# `proxy-toggle` — Proxy Mode Switcher & Caido-to-ZAP Chaining Controller

## Overview
- **Binary Location**: `/usr/local/bin/proxy-toggle` (Source: `/home/kali/.local/share/devsecops-lab/bin/proxy-toggle`)
- **Shortcut Aliases**:
  - `proxy-caido` -> `proxy-toggle caido`
  - `proxy-zap` -> `proxy-toggle zap`
  - `proxy-chain` -> `proxy-toggle chain`
  - `proxy-direct` -> `proxy-toggle direct`
  - `proxy-status` -> `proxy-toggle status`

## What It Does
Coordinates both the Firefox `portswigger-lab` profile proxy configuration (`user.js` / `prefs.js`) and **Caido's Upstream HTTP Proxy settings** (via Caido's live GraphQL API on `http://127.0.0.1:8080/graphql` + SQLite database at `~/.local/share/caido/config.db`).

### Supported Modes

| Mode Command | Short Alias | Traffic Flow | When to Use |
| :--- | :--- | :--- | :--- |
| `proxy-toggle caido` | `proxy-caido` | `Browser / CLI -> Caido (8080) -> Target` | Fast manual inspection, Repeater (Replay), Tamper rules, and low-latency browsing |
| `proxy-toggle zap` | `proxy-zap` | `Browser / CLI -> OWASP ZAP (8081) -> Target` | Direct ZAP HUD, Ajax Spider, or standalone ZAP active/passive scanning |
| `proxy-toggle chain` | `proxy-chain` | `Browser / CLI -> Caido (8080) -> ZAP (8081) -> Target` | **Best of both worlds**: Manual Repeater/Intercept in Caido while ZAP passively scans every request and builds a full scan tree upstream |
| `proxy-toggle direct` | `proxy-direct` | `Browser -> Target (No Proxy)` | Bypass proxies temporarily without closing the lab browser |
| `proxy-toggle status` | `proxy-status` | *(Read-only status check)* | Inspects `ss -tln` for ports `8080`/`8081`, active routing mode, and ZAP's OAST Interactsh service |

---

## Usage & Examples

### 1. Check Current Pipeline Status
```bash
proxy-toggle status
# or:
proxy-status
```

### 2. Enable Upstream Chaining (Caido 8080 -> ZAP 8081)
```bash
proxy-toggle chain
# or:
proxy-chain
```
*Note: In `chain` mode, all CLI wrappers (`ffuf-caido`, `katana-caido`, `nuclei-caido`, etc.) and the browser send traffic to Caido (`127.0.0.1:8080`), which automatically forwards every request upstream to OWASP ZAP (`127.0.0.1:8081`).*

### 3. Switch Back to Standalone Caido
```bash
proxy-toggle caido
# or:
proxy-caido
```

### 4. Switch Browser Directly to OWASP ZAP (Port 8081)
```bash
proxy-toggle zap
# or:
proxy-zap
```

---

## How Upstream Chaining Works Internally
1. Authenticates to Caido's local GraphQL endpoint (`http://127.0.0.1:8080/graphql`) via `mutation { loginAsGuest { token { accessToken } } }`.
2. Invokes `toggleUpstreamProxyHttp(id: "1", enabled: true|false)` for the upstream rule `127.0.0.1:8081`.
3. Synchronizes the `upstream_proxies_http` table in `/home/kali/.local/share/caido/config.db` so the setting persists across restarts.
4. Updates `network.proxy.http_port` and `network.proxy.ssl_port` in `/home/kali/.mozilla/firefox/portswigger-lab/user.js` and `prefs.js`.
