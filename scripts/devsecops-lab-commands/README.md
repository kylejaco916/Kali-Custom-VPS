# DevSecOps & PortSwigger Lab Custom Commands Reference

This folder (`/home/kali/devsecops-lab-commands`) contains individual, thoroughly notated reference files and annotated executable scripts for every custom wrapper command, proxy toggle utility, and shell alias created for your local PortSwigger Web Security Academy & DevSecOps pipeline.

---

## Directory Index

### Individual Command Documentation Files
1. [`01-portswigger-browser.md`](./01-portswigger-browser.md) — Pre-configured Firefox ESR launcher with isolated `portswigger-lab` profile, Container Tabs, and trusted Caido + ZAP Root CAs (`cert9.db`).
2. [`02-proxy-toggle.md`](./02-proxy-toggle.md) — Master proxy mode switcher & upstream proxy chaining controller (`caido`, `zap`, `chain`, `direct`, `status`).
3. [`03-ffuf-caido.md`](./03-ffuf-caido.md) — Unthrottled web fuzzer wrapper routing all requests into Caido (`127.0.0.1:8080`).
4. [`04-ffuf-replay.md`](./04-ffuf-replay.md) — Noise-free fuzzing wrapper that only forwards **matched** hits into Caido (`-replay-proxy`).
5. [`05-nuclei-caido.md`](./05-nuclei-caido.md) — Template-driven active vulnerability scanner wrapper routed through Caido.
6. [`06-interactsh-caido.md`](./06-interactsh-caido.md) — Out-of-Band (OAST) Collaborator replacement wrapper + OWASP ZAP OAST integration notes.
7. [`07-katana-caido.md`](./07-katana-caido.md) — Modern JS-parsing & headless crawler wrapper populating Caido/ZAP site trees.
8. [`08-httpx-caido.md`](./08-httpx-caido.md) — HTTP tech-stack & endpoint prober routed into Caido.
9. [`09-sqlmap-caido.md`](./09-sqlmap-caido.md) — Automated SQL injection detection & exploitation wrapper routed into Caido.
10. [`10-arjun-caido.md`](./10-arjun-caido.md) — Hidden HTTP parameter discovery (Param Miner replacement) forwarding discovered parameters into Caido.
11. [`11-aliases-and-env.md`](./11-aliases-and-env.md) — Shell aliases (`proxy-caido`, `proxy-zap`, `proxy-chain`, etc.) and exported environment variables (`$SECLISTS`, `$CAIDO_PROXY`, `$ZAP_PROXY`, `$LAB_CA_BUNDLE`).
12. [`12-kali-menu-entries.md`](./12-kali-menu-entries.md) — Complete reference of all Kali Applications drop-down menu `.desktop` entries and sub-categories.

### Annotated Executable Scripts (`./scripts/`)
Every executable script installed in `/usr/local/bin/` also has a heavily commented reference copy in [`./scripts/`](./scripts/):
- [`scripts/portswigger-browser`](./scripts/portswigger-browser)
- [`scripts/proxy-toggle`](./scripts/proxy-toggle)
- [`scripts/ffuf-caido`](./scripts/ffuf-caido)
- [`scripts/ffuf-replay`](./scripts/ffuf-replay)
- [`scripts/nuclei-caido`](./scripts/nuclei-caido)
- [`scripts/interactsh-caido`](./scripts/interactsh-caido)
- [`scripts/katana-caido`](./scripts/katana-caido)
- [`scripts/httpx-caido`](./scripts/httpx-caido)
- [`scripts/sqlmap-caido`](./scripts/sqlmap-caido)
- [`scripts/arjun-caido`](./scripts/arjun-caido)
- [`scripts/aliases.sh`](./scripts/aliases.sh)

---

## Quick Cheat Sheet

| Custom Command | Shortcut Alias | Burp Pro Equivalent | Description |
| :--- | :--- | :--- | :--- |
| `portswigger-browser` | `portswigger-browser` | Embedded Browser | Launches isolated Firefox ESR with Caido & ZAP Root CAs trusted |
| `proxy-toggle caido` | `proxy-caido` | Proxy -> Standalone | Browser -> Caido (`127.0.0.1:8080`) -> Target |
| `proxy-toggle zap` | `proxy-zap` | Scanner Standalone | Browser -> OWASP ZAP (`127.0.0.1:8081`) -> Target |
| `proxy-toggle chain` | `proxy-chain` | Upstream Proxy Rule | Browser -> Caido (`8080`) -> OWASP ZAP (`8081`) -> Target |
| `proxy-toggle direct` | `proxy-direct` | Intercept Off / Direct | Disables browser proxy (`network.proxy.type = 0`) |
| `proxy-toggle status` | `proxy-status` | Proxy Listeners Tab | Displays live listener sockets, chaining state, and OAST status |
| `ffuf-caido` | `ffuf-caido` | Intruder (All Traffic) | Runs `ffuf` with `-x http://127.0.0.1:8080` |
| `ffuf-replay` | `ffuf-replay` | Intruder (Hits Only) | Runs `ffuf` with `-replay-proxy http://127.0.0.1:8080` |
| `nuclei-caido` | `nuclei-caido` | Burp Pro Active Scanner | Runs `nuclei` with `-proxy http://127.0.0.1:8080` |
| `interactsh-caido` | `interactsh-caido` | Burp Collaborator Client | Runs `interactsh-client` routed through Caido (`127.0.0.1:8080`) |
| `katana-caido` | `katana-caido` | Burp Crawler | Runs `katana` with `-proxy http://127.0.0.1:8080` |
| `httpx-caido` | `httpx-caido` | Target Analyzer / Prober | Runs `httpx` with `-proxy http://127.0.0.1:8080` |
| `sqlmap-caido` | `sqlmap-caido` | SQLi Scanner / CO2 | Runs `sqlmap` with `--proxy="http://127.0.0.1:8080"` |
| `arjun-caido` | `arjun-caido` | Param Miner | Runs `arjun` through Caido and outputs hits via `-oB 127.0.0.1:8080` |
