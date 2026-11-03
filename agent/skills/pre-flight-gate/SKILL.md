---
name: pre-flight-gate
description: 3-Gate Deterministic Pre-Flight Protocol for Colab, Linux, and Termux provisioning (Hardware Fingerprinting, Context7 MCP + uv dry-run, and Headless Cell Execution).
---
# 3-Gate Deterministic Pre-Flight Protocol
1. **Gate A (Hardware Fingerprint):** Run `~/.gemini/antigravity/skills/pre-flight-gate/probe_hw.sh` before writing any provisioning or ML code.
2. **Gate B (Version-Locked Docs + Dry-Run):** Query `@upstash/context7-mcp` for live 2026 API signatures and run `uv pip install --dry-run <pkgs>` before installing dependencies.
3. **Gate C (Headless Cell Verification):** Never emit untested raw `.ipynb` JSON. Write percent-format `# %%` Python scripts and execute cells headlessly via `run_verified_nb.py` (`jupytext` + `nbclient`), asserting `exit_code == 0`.
