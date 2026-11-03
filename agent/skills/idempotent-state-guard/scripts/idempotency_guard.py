#!/data/data/com.termux/files/usr/bin/python3
"""
Antigravity Cross-Branch Idempotency & State-Deduplication Engine
Prevents redundant execution when multiple compiled Master Prompts from parallel
chat branches are fed into agy on the same machine.

Mechanics:
1. Normalizes shell commands & extracts target file paths / heredoc payloads.
2. Computes SHA-256 hashes of commands and target files on disk.
3. Queries SQLite ledger (~/.gemini/antigravity/memory/execution_state.db):
   - SKIP if command already succeeded (exit_code == 0) AND target file/binary/pkg
     already exists on disk with matching SHA-256 hash.
   - RUN (UPDATE) if target file content in the new prompt differs (SHA-256 drift),
     or if target file/package is missing from disk, or if AGY_FORCE_RERUN=1 /
     --force / --upgrade / # @force-run is present.
"""
import argparse, hashlib, json, os, platform, re, shutil, sqlite3, sys, time
from pathlib import Path

MEM_DIR = os.path.expanduser("~/.gemini/antigravity/memory")
DB_PATH = os.path.join(MEM_DIR, "execution_state.db")

ALWAYS_RUN_PATTERNS = [
    r"\bverify_rollup\.py\b",
    r"\bidempotency_guard\.py\b",
    r"\breflexion_ledger\.py\s+(?:intercept|record|log|export-curriculum)\b",
    r"\bcrystallize_skill\.py\b",
    r"\bextract_symbols\.py\b",
    r"\bprobe_hw\.sh\b",
    r"--dry-run\b",
    r"#\s*@force-run\b",
    r"\bagy-sync\b",
]

FORCE_FLAGS_RE = re.compile(r"(?:\bAGY_FORCE_RERUN=1\b|\s--force\b|\s--upgrade\b|\s-U\b)")
HEREDOC_WRITE_RE = re.compile(
    r"cat\s+<<\s*['\"]?(\w+)['\"]?\s*>\s*([^\s;&|]+)\n([\s\S]*?)\n\1\b"
)

def init_db() -> sqlite3.Connection:
    os.makedirs(MEM_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS executed_steps (
            cmd_hash TEXT PRIMARY KEY,
            cmd_norm TEXT,
            target_path TEXT,
            target_sha256 TEXT,
            hostname TEXT,
            exit_code INTEGER,
            run_count INTEGER DEFAULT 1,
            first_run_ts INTEGER,
            last_run_ts INTEGER
        );"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS file_manifest (
            filepath TEXT PRIMARY KEY,
            sha256 TEXT,
            mode INTEGER,
            updated_ts INTEGER
        );"""
    )
    conn.commit()
    return conn

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

def sha256_file(path: str) -> str:
    exp = os.path.expanduser(path)
    if not os.path.isfile(exp):
        return ""
    h = hashlib.sha256()
    try:
        with open(exp, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def normalize_cmd(cmd: str) -> str:
    c = cmd.strip()
    c = re.sub(r"^export\s+NO_COLOR=1\s+TERM=dumb;\s*", "", c)
    return c.strip()

def check_packages_installed(cmd: str) -> bool:
    # For pkg install -y <pkgs> or apt-get install -y <pkgs>, check key binaries/packages
    m_pkg = re.search(r"\bpkg\s+install\s+(?:-y\s+)?(.+)", cmd)
    if m_pkg:
        pkgs = [p for p in m_pkg.group(1).split() if not p.startswith("-")]
        bin_map = {
            "python": "python3",
            "python-pip": "pip",
            "build-essential": "clang",
            "openssh": "ssh",
            "sqlite": "sqlite3",
        }
        for p in pkgs:
            b = bin_map.get(p, p)
            if shutil.which(b) is None:
                return False
        return True
    return False

def evaluate_command(cmd: str) -> dict:
    norm = normalize_cmd(cmd)
    cmd_hash = sha256_text(norm)

    if os.environ.get("AGY_FORCE_RERUN") == "1" or FORCE_FLAGS_RE.search(norm):
        return {"action": "run", "reason": "explicit_force_or_upgrade_flag", "cmd_hash": cmd_hash}

    for pat in ALWAYS_RUN_PATTERNS:
        if re.search(pat, norm):
            return {"action": "run", "reason": "verification_or_dynamic_probe", "cmd_hash": cmd_hash}

    # Check ssh-keygen idempotency
    if "ssh-keygen" in norm and "-f" in norm:
        m_key = re.search(r"-f\s+([^\s]+)", norm)
        if m_key and os.path.exists(os.path.expanduser(m_key.group(1))):
            return {
                "action": "skip",
                "reason": f"SSH key {m_key.group(1)} already exists on disk",
                "cmd_hash": cmd_hash,
            }

    # Check heredoc file writes for exact SHA-256 content match vs drift
    heredocs = HEREDOC_WRITE_RE.findall(norm)
    if heredocs and ">>" not in norm:
        all_match = True
        drifted = []
        for _, raw_path, body in heredocs:
            exp_path = os.path.expanduser(raw_path)
            intended_hash = sha256_text(body + "\n")
            intended_hash_alt = sha256_text(body)
            disk_hash = sha256_file(exp_path)
            if not disk_hash or (disk_hash != intended_hash and disk_hash != intended_hash_alt):
                all_match = False
                drifted.append(raw_path)
        if all_match:
            return {
                "action": "skip",
                "reason": f"Target file(s) already exist with identical SHA-256 ({cmd_hash[:10]})",
                "cmd_hash": cmd_hash,
            }
        else:
            return {
                "action": "run",
                "reason": f"File missing or SHA-256 content drift detected on: {', '.join(drifted)}",
                "cmd_hash": cmd_hash,
            }

    conn = init_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT target_path, target_sha256, exit_code, last_run_ts FROM executed_steps WHERE cmd_hash = ?;",
        (cmd_hash,),
    )
    row = cur.fetchone()
    conn.close()

    if row and row[2] == 0:
        t_path, t_sha, _, last_ts = row
        if t_path:
            curr_sha = sha256_file(t_path)
            if not curr_sha or (t_sha and curr_sha != t_sha):
                return {
                    "action": "run",
                    "reason": f"Tracked artifact {t_path} missing or modified on disk",
                    "cmd_hash": cmd_hash,
                }
        return {
            "action": "skip",
            "reason": f"Command previously succeeded (hash={cmd_hash[:10]}, ts={last_ts})",
            "cmd_hash": cmd_hash,
        }

    if check_packages_installed(norm):
        return {
            "action": "skip",
            "reason": "All requested Termux binaries already installed in PATH",
            "cmd_hash": cmd_hash,
        }

    return {"action": "run", "reason": "first_execution_on_host", "cmd_hash": cmd_hash}

def commit_command(cmd: str, exit_code: int, target_path: str = ""):
    if exit_code != 0:
        return
    norm = normalize_cmd(cmd)
    cmd_hash = sha256_text(norm)
    now = int(time.time())
    host = platform.node() or "termux-s25"

    heredocs = HEREDOC_WRITE_RE.findall(norm)
    if heredocs and not target_path:
        target_path = heredocs[0][1]

    t_sha = sha256_file(target_path) if target_path else ""
    conn = init_db()
    conn.execute(
        """INSERT INTO executed_steps
           (cmd_hash, cmd_norm, target_path, target_sha256, hostname, exit_code, run_count, first_run_ts, last_run_ts)
           VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
           ON CONFLICT(cmd_hash) DO UPDATE SET
               target_sha256=excluded.target_sha256,
               exit_code=excluded.exit_code,
               run_count=executed_steps.run_count + 1,
               last_run_ts=excluded.last_run_ts;""",
        (cmd_hash, norm[:2000], target_path, t_sha, host, exit_code, now, now),
    )
    if target_path and t_sha:
        exp = os.path.expanduser(target_path)
        mode = os.stat(exp).st_mode & 0o777 if os.path.exists(exp) else 0o644
        conn.execute(
            """INSERT OR REPLACE INTO file_manifest (filepath, sha256, mode, updated_ts)
               VALUES (?, ?, ?, ?);""",
            (exp, t_sha, mode, now),
        )
    conn.commit()
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Antigravity Cross-Branch Idempotency Guard")
    sub = parser.add_subparsers(dest="subcmd")

    p_chk = sub.add_parser("check")
    p_chk.add_argument("--cmd", required=True)

    p_com = sub.add_parser("commit")
    p_com.add_argument("--cmd", required=True)
    p_com.add_argument("--exit-code", type=int, default=0)
    p_com.add_argument("--target", default="")

    p_stat = sub.add_parser("status")

    args = parser.parse_args()
    if args.subcmd == "check":
        res = evaluate_command(args.cmd)
        print(json.dumps(res))
    elif args.subcmd == "commit":
        commit_command(args.cmd, args.exit_code, args.target)
        print(json.dumps({"committed": True}))
    elif args.subcmd == "status":
        conn = init_db()
        c1 = conn.execute("SELECT COUNT(*) FROM executed_steps WHERE exit_code=0;").fetchone()[0]
        c2 = conn.execute("SELECT COUNT(*) FROM file_manifest;").fetchone()[0]
        conn.close()
        print(f"[IDEMPOTENCY LEDGER] Verified Commands={c1} | Fingerprinted Files={c2} | DB={DB_PATH}")
    else:
        init_db()
        print(f"[IDEMPOTENCY LEDGER INITIALIZED] -> {DB_PATH}")

if __name__ == "__main__":
    main()
