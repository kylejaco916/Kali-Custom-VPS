#!/data/data/com.termux/files/usr/bin/python3
"""
Pillar 3A: Episodic Reflexion Failure Ledger (SQLite FTS5 BM25 + Append-Only JSONL)
Stores and retrieves [FAILURE SIGNATURE] ==> [ROOT CAUSE] ==> [VERIFIED FIX] tuples
and exports failure trajectories as JSONL curricula for Pillar 4 Unsloth GRPO RLVR.
Supports subcommands: intercept, record, log, export-curriculum.
"""
import os, sys, json, sqlite3, argparse, time, re

MEM_DIR = os.path.expanduser("~/.gemini/antigravity/memory")
DB_PATH = os.path.join(MEM_DIR, "ledger.db")
JSONL_PATH = os.path.join(MEM_DIR, "ledger.jsonl")
CURRICULUM_PATH = os.path.join(MEM_DIR, "grpo_curriculum.jsonl")

def init_db():
    os.makedirs(MEM_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE VIRTUAL TABLE IF NOT EXISTS reflexion_fts USING fts5(
            error_sig, cmd, root_cause, verified_fix, domain, env, timestamp UNINDEXED,
            tokenize='porter unicode61'
        );"""
    )
    conn.commit()
    return conn

def sanitize_fts_query(text: str) -> str:
    tokens = re.findall(r"[a-zA-Z0-9_]{3,}", text)
    seen = []
    for t in tokens:
        if t.lower() not in seen:
            seen.append(t.lower())
    return " OR ".join(seen[:12]) if seen else "error"

def intercept_error(cmd: str, err: str):
    conn = init_db()
    q = sanitize_fts_query(f"{cmd} {err}")
    cur = conn.cursor()
    cur.execute(
        """SELECT error_sig, root_cause, verified_fix, bm25(reflexion_fts) AS rank
           FROM reflexion_fts WHERE reflexion_fts MATCH ? ORDER BY rank LIMIT 1;""",
        (q,),
    )
    row = cur.fetchone()
    if row:
        sig, cause, fix, _ = row
        print(
            f"[REFLEXION LEDGER HIT — KNOWN FAILURE SIGNATURE]\n"
            f"  [FAILURE SIGNATURE] ==> {sig}\n"
            f"  [ROOT CAUSE]        ==> {cause}\n"
            f"  [VERIFIED FIX]      ==> {fix}\n"
            f"  [DIRECTIVE] Apply [VERIFIED FIX] immediately; do not repeat failed command."
        )
    else:
        print(
            f"[REFLEXION LEDGER MISS — NEW FAILURE DETECTED]\n"
            f"  [DIRECTIVE] Diagnose in <=2 lines and commit tuple via:\n"
            f"  python3 ~/.gemini/antigravity/skills/reflexion-ledger/scripts/reflexion_ledger.py log "
            f"--domain 'sys' --env 'termux' --failed-cmd '{cmd[:60]}' "
            f"--error-signature '<ErrorSig>' --root-cause '<RootCause>' --verified-fix '<VerifiedFix>'"
        )
    conn.close()

def record_tuple(sig: str, cmd: str, cause: str, fix: str, domain: str = "general", env: str = "termux-arm64"):
    conn = init_db()
    cur = conn.cursor()
    cur.execute("SELECT error_sig FROM reflexion_fts WHERE error_sig = ? LIMIT 1;", (sig,))
    if cur.fetchone():
        conn.close()
        print(f"[REFLEXION IDEMPOTENT-SKIP] Signature already recorded: {sig}")
        return

    ts = str(int(time.time()))
    conn.execute(
        "INSERT INTO reflexion_fts (error_sig, cmd, root_cause, verified_fix, domain, env, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?);",
        (sig, cmd, cause, fix, domain, env, ts),
    )
    conn.commit()
    conn.close()
    entry = {
        "timestamp": int(ts),
        "domain": domain,
        "env": env,
        "failure_signature": sig,
        "command": cmd,
        "root_cause": cause,
        "verified_fix": fix,
        "tuple": f"[{sig}] ==> [{cause}] ==> [{fix}]",
    }
    with open(JSONL_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[REFLEXION RECORDED] {entry['tuple']}")

def export_curriculum():
    os.makedirs(MEM_DIR, exist_ok=True)
    if not os.path.exists(JSONL_PATH):
        record_tuple(
            "OAuth Loopback Timeout on Termux Android 16",
            "agy auth login",
            "Headless mobile viewport cannot bind local browser callback port",
            "Export AGY_OAUTH_NO_BROWSER=1 and AGY_OAUTH_FLOW=oob before invoking auth",
        )
    count = 0
    with open(JSONL_PATH, "r") as fin, open(CURRICULUM_PATH, "w") as fout:
        for line in fin:
            if not line.strip():
                continue
            item = json.loads(line)
            prompt = (
                f"Use Chain-of-Draft (<=5 words/step before ####). Resolve failure:\n"
                f"Command: {item['command']}\nError Signature: {item['failure_signature']}"
            )
            record = {
                "prompt": prompt,
                "reference_cause": item["root_cause"],
                "reference_fix": item["verified_fix"],
            }
            fout.write(json.dumps(record) + "\n")
            count += 1
    print(f"[CURRICULUM EXPORTED] {count} RLVR training items -> {CURRICULUM_PATH}")

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action")

    p_int = sub.add_parser("intercept")
    p_int.add_argument("--cmd", default="")
    p_int.add_argument("--err", default="")

    p_rec = sub.add_parser("record")
    p_rec.add_argument("--sig", required=True)
    p_rec.add_argument("--cmd", default="")
    p_rec.add_argument("--cause", required=True)
    p_rec.add_argument("--fix", required=True)

    p_log = sub.add_parser("log")
    p_log.add_argument("--domain", default="general")
    p_log.add_argument("--env", default="termux-arm64")
    p_log.add_argument("--failed-cmd", default="")
    p_log.add_argument("--error-signature", required=True)
    p_log.add_argument("--root-cause", required=True)
    p_log.add_argument("--verified-fix", required=True)

    sub.add_parser("export-curriculum")

    args = parser.parse_args()
    if args.action == "intercept":
        intercept_error(args.cmd, args.err)
    elif args.action == "record":
        record_tuple(args.sig, args.cmd, args.cause, args.fix)
    elif args.action == "log":
        record_tuple(
            args.error_signature,
            args.failed_cmd,
            args.root_cause,
            args.verified_fix,
            args.domain,
            args.env,
        )
    elif args.action == "export-curriculum":
        export_curriculum()
    else:
        init_db()
        export_curriculum()

if __name__ == "__main__":
    main()
