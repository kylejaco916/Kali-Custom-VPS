---
name: skill-crystallizer
description: Voyager-style procedural memory compiler. Invoke after solving any complex multi-step workflow to crystallize working commands into ~/.gemini/antigravity/skills/learned/<slug>/SKILL.md.
---
# Voyager Skill Crystallizer (Pillar 3B)
Whenever a multi-step engineering, provisioning, or security workflow succeeds (`exit_code == 0`), strip all failed attempts and run:
```bash
python3 ~/.gemini/antigravity/skills/skill-crystallizer/scripts/crystallize_skill.py \
  --name "<workflow-slug>" \
  --description "<concise trigger description>" \
  --preconditions "<OS/hardware preconditions>" \
  --step "<verified command 1>" \
  --step "<verified command 2>" \
  --verify-cmd "<deterministic verification command>" \
  --sync
```
