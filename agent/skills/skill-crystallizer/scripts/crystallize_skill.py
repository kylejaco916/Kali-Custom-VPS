#!/data/data/com.termux/files/usr/bin/python3
"""
crystallize_skill.py — Voyager-Style Procedural Skill Synthesizer for Antigravity
Compiles a verified multi-step workflow into a Level-1/2/3 Progressive Disclosure
SKILL.md package inside ~/.gemini/antigravity/skills/learned/<slug>/ and triggers
cross-node synchronization.
"""
import argparse, os, re, shutil, subprocess, sys, time
from pathlib import Path

SKILLS_ROOT = Path.home() / ".gemini" / "antigravity" / "skills" / "learned"

def validate_slug(slug: str) -> str:
    clean = re.sub(r"[^a-z0-9\-]", "-", slug.lower()).strip("-")
    if not clean or len(clean) > 64:
        raise ValueError("Skill slug must be 1-64 lowercase alphanumeric/hyphen chars.")
    return clean

def main() -> int:
    parser = argparse.ArgumentParser(description="Voyager Procedural Skill Crystallizer")
    parser.add_argument("--name", required=True, help="Skill slug (e.g., oracle-hexstrike-deploy)")
    parser.add_argument("--description", "--desc", dest="description", required=True, help="Level 1 trigger description (<200 chars)")
    parser.add_argument("--preconditions", default="Termux ARM64 (Android 16) or 4-Node Split-Cloud Mesh", help="Hardware/OS preconditions")
    parser.add_argument("--steps-file", default="", help="Path to markdown/text file containing verified steps")
    parser.add_argument("--step", action="append", default=[], help="Inline verified command step (repeatable)")
    parser.add_argument("--helper-script", default="", help="Optional path to a verified bash/python script to bundle")
    parser.add_argument("--verify-cmd", "--verify", dest="verify_cmd", default="echo 'VERIFIED=0'", help="Deterministic 1-liner that verifies success (exit 0)")
    parser.add_argument("--sync", action="store_true", help="Run agy-sync immediately after crystallization")
    args = parser.parse_args()

    slug = validate_slug(args.name)
    skill_dir = SKILLS_ROOT / slug
    scripts_dir = skill_dir / "scripts"
    skill_dir.mkdir(parents=True, exist_ok=True)

    if args.steps_file and Path(args.steps_file).exists():
        steps_content = Path(args.steps_file).read_text(encoding="utf-8").strip()
    elif args.step:
        steps_content = "\n".join(f"{i+1}. `{s}`" for i, s in enumerate(args.step))
    else:
        steps_content = "1. Execute bundled helper script."

    bundled_script_ref = "None"
    if args.helper_script:
        src_script = Path(args.helper_script).expanduser().resolve()
        if src_script.exists():
            scripts_dir.mkdir(parents=True, exist_ok=True)
            dst_script = scripts_dir / src_script.name
            shutil.copy2(src_script, dst_script)
            dst_script.chmod(0o755)
            bundled_script_ref = f"`~/.gemini/antigravity/skills/learned/{slug}/scripts/{src_script.name}`"

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    skill_md = f"""---
name: {slug}
description: {args.description.strip()}
---

# CRYSTALLIZED PROCEDURAL SKILL: {slug.upper()}
*Synthesized: {timestamp} | Pattern: Voyager Procedural Memory*

## 1. PRECONDITIONS & ENVIRONMENT SCOPE
{args.preconditions.strip()}

## 2. BUNDLED ZERO-TOKEN EXECUTABLE
- Helper Script: {bundled_script_ref}

## 3. DETERMINISTIC EXECUTION SEQUENCE
{steps_content}

## 4. VERIFICATION GATE (MANDATORY)
Before marking this workflow complete, run this verification check and confirm `exit_code == 0`:
```bash
{args.verify_cmd.strip()}
```
"""
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(skill_md, encoding="utf-8")
    print(f"[VOYAGER CRYSTALLIZER] Wrote procedural skill -> {skill_file}")

    if args.sync or os.path.exists("/data/data/com.termux/files/usr/bin/agy-sync"):
        subprocess.run(["/data/data/com.termux/files/usr/bin/agy-sync"], check=False)
    return 0

if __name__ == "__main__":
    sys.exit(main())
