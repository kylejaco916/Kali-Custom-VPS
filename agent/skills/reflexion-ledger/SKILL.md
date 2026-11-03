---
name: reflexion-ledger
description: Cross-node SQLite FTS5 BM25 + JSONL episodic failure ledger. Queries known error signatures and records [Error Sig ==> Root Cause ==> Verified Fix] tuples for GRPO RLVR training.
---
# REFLEXION EPISODIC FAILURE LEDGER (PILLAR 3A)
Whenever you resolve a new bug or architectural pivot that was not previously in the ledger, record the verified tuple before completing the turn:
```bash
python3 ~/.gemini/antigravity/skills/reflexion-ledger/scripts/reflexion_ledger.py log \
  --domain "<domain>" \
  --env "<target-node-env>" \
  --failed-cmd "<command that failed>" \
  --error-signature "<concise stderr signature>" \
  --root-cause "<1-sentence mechanical cause>" \
  --verified-fix "<exact deterministic command/code fix>"
```
