---
name: skeletal-blueprint
description: Generates a chronological 5-tier top-down project familial tree and action checklist with proportional effort percentages (summing to 100%) and timeframes for multi-agent workflows. Invoke when planning, auditing, or tracking /teamwork-preview or large project lifecycles.
---

# SKELETAL BLUEPRINT & WORKFORCE TELEMETRY PROTOCOL

When activated, compile an exhaustive, chronologically ordered, top-down **Skeletal Project Blueprint** without conversational filler.

## 1. HIERARCHICAL TREE ARCHITECTURE
Render strictly as a Unicode familial tree (`│`, `├──`, `└──`) across 5 tiers:
- **TIER 1 [WORKFORCE]:** Active `agy` agents and domains in compact shorthand.
- **TIER 2 [PROJECT GOAL]:** Macro objective (strictly 3 words to 1 dense paragraph).
- **TIER 3 [PHASES]:** Sequential stages (`PHASE 1..N`) with a 3-to-10-word objective.
- **TIER 4 [COMPONENTS]:** Functional subsystems inside each phase.
- **TIER 5 [ATOMIC ACTIONS & PIVOTS]:** Every granular task, state handoff, `PIVOT:`, or `ADJUSTMENT:`.

## 2. MANDATORY TELEMETRY TAG SYNTAX
Prefix every Tier 3, 4, and 5 node with:
`[Status] [Effort: X.X% | Δt: Time | @Agent] Concise Label — Skeletal description (max 15 words)`
- **Status:** `[x]` Done | `[~]` Active/Pivoting | `[ ]` Pending
- **Proportional Rollup Law:** Tier 5 percentages MUST sum to their parent Tier 4 `%`. Tier 4 MUST sum to Tier 3 `%`. All Tier 3 Phases MUST sum to **100.0%**.
- **Verification:** Before outputting, if `scripts/verify_rollup.py` exists, validate tier sums or perform an explicit mental checksum `[Checksum: Phase1(X%) + Phase2(Y%) ... = 100.0%]`.

