---
name: uv-context7-gate
description: Eliminates Python dependency conflicts and stale API hallucinations. Enforces live documentation lookups via Context7 MCP and 50ms dry-run dependency resolution via Astral uv before installing packages or writing ML/security code.
---
# DETERMINISTIC DEPENDENCY & LIVE DOCUMENTATION GATE
To prevent "slot-machine" package breakage in Google Colab, Kali, and Debian, strictly obey these three rules:
1. **Live API Grounding (Context7 MCP):** When writing code involving fast-evolving frameworks (`unsloth`, `trl`, `vllm`, `transformers`, `peft`, `bitsandbytes`, `diffusers`, `comfyui`, `langgraph`), call `resolve-library-id` followed by `get-library-docs` from the `context7` MCP server to verify exact class signatures and kwargs.
2. **Astral `uv` Dry-Run SAT Solver Gate:** NEVER run raw `pip install <pkg1> <pkg2>` blindly. Pre-verify resolution first:
   `uv pip install --system --dry-run <packages...>`
3. **Preserve Colab Base Wheels:** In Google Colab, pin against the existing pre-installed `torch`, `torchaudio`, and `torchvision` CUDA wheels so `pip`/`uv` never downloads a conflicting 2.5GB PyTorch wheel.
