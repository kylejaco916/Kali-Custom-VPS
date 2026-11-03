# Kali-Custom-VPS

Automated, one-command replication repository for provisioning and unpacking the complete custom **Kali Linux Security, Bug Bounty, DevSecOps & AI Red-Team Workstation**.

If you ever migrate or rebuild your Kali VPS, simply `git clone` this repository and run `./install.sh` to automatically unpack and configure every tool, wrapper, proxy chain, browser profile, certificate store, desktop menu entry, systemd daemon, Tailscale/SSH mesh block, Antigravity skill, and Headless Colab GPU + HexStrike MCP integration.

---

## Quickstart: One-Command Replication

On any fresh Kali Linux VPS:

```bash
git clone https://github.com/kylejaco916/Kali-Custom-VPS.git
cd Kali-Custom-VPS
chmod +x install.sh
./install.sh
```

### Installer Options
```bash
# Full replication (including 5-batch installation of all 28 kali-tools-* metapackages)
./install.sh

# Fast replication (skips 15 GB metapackage download if already installed)
./install.sh --skip-metapackages

# Run a single module (01 through 09)
./install.sh --only 08

# Run the full verification & 44-test E2E suite
./install.sh --verify
```

---

## Architecture & Provisioning Modules

| Module | Script | What It Configures |
| :--- | :--- | :--- |
| **01** | `modules/01-preflight-apt.sh` | Non-interactive APT (`99noninteractive`), tmpfs/RAM `.deb` cache auto-purge (`99clean-cache`), `needrestart` batch mode (`99batch.conf`), and `debconf` pre-seeding for unattended installs. |
| **02** | `modules/02-kali-everything-tools.sh` | Staged 5-batch install of all **28 `kali-tools-*` metapackages**, `seclists` (6,184+ wordlists), **Go 1.27+**, **Astral `uv`/`uvx`**, **John the Ripper `--version` shim** (`/usr/local/bin/john`), and CLI symlinks (`caido`, `httpx`, `zap`). |
| **03** | `modules/03-desktop-vnc-novnc.sh` | XFCE4 desktop, `kali-menu`, **TigerVNC** (`:1` / `:5901`), **noVNC** (`:6080` with mobile HTTP banner suppression patch in `ui.js`), **Burp Suite Java 21 LTS fix**, and `kali-mode` (`headless \| gui \| status`). |
| **04** | `modules/04-tailscale-ssh.sh` | Tailscale daemon, hardened `sshd_config` (`PasswordAuthentication no`, `X11Forwarding yes`), authorized public keys, `~/.ssh/config` (`Host termux` & `Host colab-gpu`), and `~/debian-ssh-client-setup.sh`. |
| **05** | `modules/05-devsecops-portswigger-lab.sh` | Dedicated Firefox ESR `portswigger-lab` profile (Container Tabs, MITM prefs, Caido & ZAP Root CAs auto-generated and injected into `cert9.db`), persistent **`caido.service` (`:8080`)** + **OWASP ZAP (`:8081` + Interactsh OAST)**, `proxy-toggle`, `*-caido` wrappers, and `~/devsecops-lab-commands/`. |
| **06** | `modules/06-bugbounty-safe-harbor.sh` | `subfinder`, `amass`, `dnsx`, `alterx`, `naabu`, `gau`, `waybackurls`, `gowitness`, `dalfox`, `trufflehog`, **`jwt_tool`** (Python 3.14 patched + Caido routed), **Bruno API Client** (`bruno-caido`), `~/.bounty_env`, `*-safe` rate-limited wrappers, `scope-filter`, and `~/bounties/target-template/`. |
| **07** | `modules/07-desktop-menus.sh` | Registers **32 custom `.desktop` launchers** in `/usr/share/applications/` and `~/.local/share/applications/` across Kali's numbered application categories. |
| **08** | `modules/08-agent-mcp-dotfiles.sh` | Deploys `.bashrc`, `.zshrc`, `GEMINI.md`, `~/.gemini/antigravity-cli/settings.json`, `~/.hermes/SOUL.md`, **23 Antigravity skills**, `kali-security-tools` MCP server, persistent **`hexstrike-server.service` (`:8888`)**, and the standalone **Headless Colab Tailscale + HexStrike AI + Hermes CLI** stack (`~/hexstrike-ai/` + `hexstrike-env` venv). |
| **09** | `modules/09-verify.sh` | 6-part verification suite: Secret/blacklist hygiene check, Bash/Python AST syntax verification, Colab orchestrator dry-run matrix, `~/verify_environment.sh`, full-stack Modules 03–08 service/CA/wrapper audit, and the **44-test 4-Tier E2E test suite**. |

---

## 1. Headless Colab Tailscale + HexStrike MCP + Hermes CLI Workflow

Located in `~/hexstrike-ai/` and pre-configured for **port `8085`** over Tailscale SSH (`colab-gpu:2222`).

### Step 1: Bootstrap Google Colab GPU Node (5-Line Cell)
Open `scripts/hexstrike-ai/5lineTailscaleKaliAI.ipynb` in Google Colab (or paste `~/hexstrike-ai/COLAB_BOOTSTRAP_CELL.py` into a single cell):

```python
# PASTE THIS 5-LINE CELL INTO GOOGLE COLAB (REPLACES ALL NOTEBOOK CODE)
!curl -fsSL https://tailscale.com/install.sh | sh && apt-get update -qq && apt-get install -y -qq openssh-server zstd psmisc > /dev/null
!mkdir -p /var/run/sshd /root/.ssh && chmod 700 /root/.ssh && echo "<YOUR_KALI_ED25519_PUBKEY>" > /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys
!ssh-keygen -A >/dev/null 2>&1 && sed -i 's/#\?Port .*/Port 2222/' /etc/ssh/sshd_config && grep -q '^PermitRootLogin' /etc/ssh/sshd_config || echo -e "PermitRootLogin prohibit-password\nPubkeyAuthentication yes" >> /etc/ssh/sshd_config && (killall -q sshd || true) && /usr/sbin/sshd
!killall -q tailscaled || true; nohup tailscaled --tun=userspace-networking --socks5-server=localhost:1055 > /tmp/tailscaled.log 2>&1 &
!sleep 3 && tailscale up --hostname="colab-gpu" --accept-routes
```

### Step 2: Push Orchestrator & Load Uncensored GPU Model from Kali
From your Kali terminal, push `1_colab_orchestrator.py` over Tailscale SSH (`root@colab-gpu:2222`), auto-detect VRAM/RAM tier (`T4`, `G4`, `L4`, `A100`), launch `/root/.llama-app/llama serve` on port `8085` with `--flash-attn on --no-mmproj`, and atomically update `~/.config/hermes/config.json` and `~/hexstrike-ai/.mcp.json`:

```bash
# Load Model Index 0 (default primary model for detected GPU tier)
~/hexstrike-ai/2_kali_gpu_controller.sh 0

# Load Model Index 1 or 2
~/hexstrike-ai/2_kali_gpu_controller.sh 1
~/hexstrike-ai/2_kali_gpu_controller.sh 2
```

### Step 3: Interactive Chat, Autonomous Tool Execution & 3-Phase Loops
```bash
# Interactive Hermes chat with full HexStrike MCP tool-calling
h

# Single-shot zero-confirmation Hermes + HexStrike MCP command
ask-hs "Scan 127.0.0.1 with hexstrike and summarize open services"

# Lightweight direct Python chat client to Colab GPU (http://colab-gpu:8085/v1)
ask

# Full 3-Phase Autonomous Assessment Loop (Surface -> Config Audit -> CVE Report)
~/hexstrike-ai/3_autonomous_assessment_loop.sh 127.0.0.1
```

---

## 2. DevSecOps & PortSwigger Web Security Academy Lab Commands

Full individual command documentation is also unpacked into `~/devsecops-lab-commands/`.

| Command / Alias | Description |
| :--- | :--- |
| `portswigger-browser` | Launches isolated Firefox ESR (`portswigger-lab` profile) with Container Tabs & trusted Caido/ZAP Root CAs |
| `proxy-toggle caido` | Browser -> Caido (`127.0.0.1:8080`) -> Target |
| `proxy-toggle zap` | Browser -> OWASP ZAP (`127.0.0.1:8081`) -> Target |
| `proxy-toggle chain` | Browser -> Caido (`127.0.0.1:8080`) -> OWASP ZAP (`127.0.0.1:8081`) -> Target |
| `proxy-toggle direct` | Disables browser proxy |
| `proxy-toggle status` | Shows live proxy listeners, Firefox mode, Caido upstream state, and ZAP OAST |
| `ffuf-caido` / `ffuf-replay` | Routes all `ffuf` traffic (`-x`) or matched hits only (`-replay-proxy`) through Caido |
| `nuclei-caido` | Runs `nuclei -proxy http://127.0.0.1:8080` |
| `interactsh-caido` | Runs `interactsh-client` through Caido |
| `katana-caido` / `httpx-caido` | Runs `katana` / `httpx` through Caido |
| `sqlmap-caido` / `arjun-caido` | Runs `sqlmap` / `arjun` through Caido |

---

## 3. Bug Bounty Safe-Harbor & ASM Pipeline

Configured via `~/.bounty_env` (`BOUNTY_HEADER`, `MAX_RATE=10`, `BOUNTY_PROXY="http://127.0.0.1:8080"`):

| Wrapper / Tool | Behavior |
| :--- | :--- |
| `ffuf-safe` | Injects `-H "$BOUNTY_HEADER" -rate "$MAX_RATE" -replay-proxy "$BOUNTY_PROXY"` |
| `nuclei-safe` | Injects `-H "$BOUNTY_HEADER" -rl "$MAX_RATE" -proxy "$BOUNTY_PROXY"` |
| `katana-safe` | Injects `-H "$BOUNTY_HEADER" -rl "$MAX_RATE" -proxy "$BOUNTY_PROXY"` |
| `httpx-safe` | Injects `-H "$BOUNTY_HEADER" -rl "$MAX_RATE" -proxy "$BOUNTY_PROXY"` |
| `dalfox-safe` | Injects `-H "$BOUNTY_HEADER" --proxy "$BOUNTY_PROXY" --delay 100` |
| `scope-filter` | Stream-filters domains/URLs against `scope/in_scope.txt` and `scope/out_of_scope.txt` |
| `bruno-caido` | Launches Bruno API Client pre-wired to Caido (`127.0.0.1:8080`) & Caido Root CA |
| `jwt_tool` | Launches Python 3.14-patched `jwt_tool` routed through Caido (`127.0.0.1:8080`) |

### Starting a New Bug Bounty Target
```bash
cp -r ~/bounties/target-template ~/bounties/acme-corp
cd ~/bounties/acme-corp
# Edit scope/in_scope.txt and scope/out_of_scope.txt, then run:
./run_recon.sh acme.com
```

---

## 4. Desktop GUI, VNC / noVNC & Mode Switching

- **Web VNC (noVNC)**: `http://<KALI_IP>:6080/vnc.html` (Default password: `kali`)
- **Native VNC**: `<KALI_IP>:5901`
- **Mode Switcher (`kali-mode`)**:
  ```bash
  kali-mode status           # Check current systemd target and RAM footprint
  sudo kali-mode headless    # Switch to lightweight multi-user.target (<350 MB RAM)
  sudo kali-mode gui         # Switch to full XFCE4 graphical.target
  ```
