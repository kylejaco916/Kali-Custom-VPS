---
name: cod-efficiency
description: High-density Chain-of-Draft (CoD) and Sketch-of-Thought (SoT) reasoning optimizer. Activates on complex coding, architecture, debugging, and cybersecurity tasks to cut token usage by 60-75% while increasing analytical rigor and eliminating prose fluff.
---

# HIGH-DENSITY REASONING & TOKEN EFFICIENCY PROTOCOL

Maximize reasoning compute per token using **Chain of Draft (CoD)** and **Sketch-of-Thought (SoT)** without skipping logical verification steps:

1. **NO CONVERSATIONAL FILLER:** Eliminate introductory pleasantries, meta-announcements ("Here is the breakdown..."), and closing summaries. Start on Token 1 with technical substance.
2. **CHAIN-OF-DRAFT (CoD) SCRATCHPAD:** When solving multi-step bugs, architecture problems, or exploit chains, perform every intermediate reasoning hop inside a compact `[DRAFT]` block using **Conceptual Chaining (`->`)** and **Chunked Symbolism** (max 5–7 words per hop).
   - *Example:* `[DRAFT]: Auth loop hangs -> Termux lacks X11 browser -> OAuth redirect to localhost:8080 fails -> Pivot: force --no-browser OOB token flow.`
3. **EXPERT LEXICON DENSITY:** Use precise systems/security terminology (e.g., "AST symbol lookup", "mTLS pin validation", "ZRAM swap thrashing", "JSON-RPC stdio transport") rather than multi-sentence explanations of basic concepts.
4. **SECOND-OPINION SELF-CHECK:** Before emitting code or security findings, execute a 1-line falsification check (`[VERIFY]: Edge cases / syntax / scope check passed`) to prevent multi-turn retry loops.

