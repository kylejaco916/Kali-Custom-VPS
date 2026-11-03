---
name: cyber-sec-pack
description: Sub-agent context isolation protocol for offensive/defensive security auditing (nmap, nuclei, ffuf, caido, sqlmap, HexStrike-AI MCP) inside /teamwork-preview.
---
# Cybersecurity Sub-Agent Isolation Protocol
1. Delegate all active recon, fuzzing, and binary analysis to `@net-recon` or `@qa-sec` via `invoke_agent`.
2. Ensure `PreToolUse` (`rewrite_cmd.py`) and `PostToolUse` (`sanitize_stdout.py`) hooks are active so raw scanner output never pollutes `@orchestrator`.
3. Return only structured findings (`[VULN-ID | CVSS | VECTOR | REMEDIATION]`) to the lead orchestrator.
