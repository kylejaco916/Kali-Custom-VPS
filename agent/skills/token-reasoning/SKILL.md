---
name: token-reasoning
description: Token-efficient algorithmic reasoning skill enforcing Chain-of-Draft (CoD), Sketch-of-Thought (SoT), TALE budget ceilings, and Second-Opinion Verification passes (60-92% token savings).
---
# Algorithmic Reasoning Compression Protocol
1. **Chain-of-Draft (CoD):** Think step-by-step, restricting each internal reasoning hop to $\le 5$ words before `####`.
2. **Sketch-of-Thought (SoT):** Use symbolic chains (`Input -> AST_Parse -> Vuln_Sink -> Patch`) and domain lexicons instead of prose.
3. **TALE Budget Ceiling:** Declare `[TALE-BUDGET: N tokens]` at task start; constrain words per step, NEVER number of reasoning steps.
4. **Second-Opinion Verification Pass:** Before emitting destructive shell commands or security patches, run a 1-line adversarial self-check: `[VERIFY: edge_cases_checked | exit_code_guarded]`.
