---
name: idempotent-state-guard
description: Cross-branch idempotency & state-deduplication engine. Prevents re-running commands, package installs, or file writes that already succeeded on this machine unless content SHA-256 drifted or an update flag is set.
---
# CROSS-BRANCH IDEMPOTENT EXECUTION GUARD

When executing compiled Master Prompts or multi-branch automation scripts in `/teamwork-preview`, strictly obey these rules to avoid wasting tokens or clobbering existing state:

## 1. AUTOMATIC PRE-TOOL & POST-TOOL INTERCEPTION
`rewrite_cmd.py` (`PreToolUse`) automatically queries `idempotency_guard.py check --cmd "<cmd>"` before any shell command runs, and `sanitize_stdout.py` (`PostToolUse`) commits successful executions (`exit_code == 0`) to `~/.gemini/antigravity/memory/execution_state.db`.
- If a command emits `[IDEMPOTENT-CACHE-HIT]`, DO NOT retry or force-run it; mark the corresponding task node `[x]` immediately and proceed to the next step.

## 2. CONTENT-DRIFT AWARENESS (UPDATES VS. REDUNDANT WRITES)
- **Identical File (`SHA-256 Match`):** Automatically skipped at zero disk/token cost.
- **Updated File (`SHA-256 Drift`):** Automatically permitted to overwrite and update the manifest hash.
- **Forced Re-Execution:** To intentionally re-run a cached command (e.g., refreshing a package or re-running a build), prefix the command with `AGY_FORCE_RERUN=1` or append `# @force-run`.

## 3. MANUAL LEDGER QUERY
Check machine execution state at any time via:
```bash
python3 ~/.gemini/config/scripts/idempotency_guard.py status
```
