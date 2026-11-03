#!/usr/bin/env python3
"""
scope_filter.sh / scope-filter
Strict Bug Bounty Safe-Harbor Scope Enforcer.
Filters stdin or input files against scope/in_scope.txt and scope/out_of_scope.txt
before any active DNS/HTTP/port probing occurs.
"""

import argparse
import fnmatch
import os
import sys
from urllib.parse import urlparse


def load_rules(filepath):
    rules = []
    if not filepath or not os.path.isfile(filepath):
        return rules
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            rules.append(line.lower())
    return rules


def extract_host_and_norm(raw_line):
    line = raw_line.strip()
    if not line:
        return None, None
    lower = line.lower()
    if "://" in lower:
        parsed = urlparse(lower)
        host = parsed.hostname or ""
        path_part = f"{host}{parsed.path or ''}"
        if parsed.query:
            path_part += f"?{parsed.query}"
    else:
        # Handle host:port or host/path
        slash_idx = lower.find("/")
        if slash_idx != -1:
            host_port = lower[:slash_idx]
            rest = lower[slash_idx:]
        else:
            host_port = lower
            rest = ""
        host = host_port.split(":")[0]
        path_part = f"{host}{rest}"
    host = host.strip(".")
    return host, path_part


def matches_rule(host, path_part, full_lower, rule):
    # Clean scheme from rule if present unless rule checks scheme
    rule_clean = rule
    if "://" in rule_clean:
        p = urlparse(rule_clean)
        r_host = (p.hostname or "").strip(".")
        r_path = p.path or ""
        rule_clean = f"{r_host}{r_path}"

    # If rule contains a path or wildcard path (e.g. *example.com/logout*)
    if "/" in rule_clean:
        return fnmatch.fnmatchcase(path_part, rule_clean) or fnmatch.fnmatchcase(full_lower, rule)

    # Domain rule: *.example.com or exact sub.example.com
    if rule_clean.startswith("*."):
        base = rule_clean[2:]
        return host == base or host.endswith("." + base) or fnmatch.fnmatchcase(host, rule_clean)
    elif "*" in rule_clean:
        return fnmatch.fnmatchcase(host, rule_clean)
    else:
        return host == rule_clean


def main():
    parser = argparse.ArgumentParser(
        description="Filter recon targets strictly against in_scope.txt and out_of_scope.txt"
    )
    parser.add_argument(
        "-i", "--in-scope",
        default="scope/in_scope.txt",
        help="Path to in-scope rules file (default: scope/in_scope.txt)"
    )
    parser.add_argument(
        "-o", "--out-of-scope",
        default="scope/out_of_scope.txt",
        help="Path to out-of-scope rules file (default: scope/out_of_scope.txt)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress stderr summary stats"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Optional input files (reads from stdin if omitted)"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.in_scope):
        sys.stderr.write(f"[!] Error: In-scope file not found: {args.in_scope}\n")
        sys.exit(1)

    in_rules = load_rules(args.in_scope)
    if not in_rules:
        sys.stderr.write(f"[!] Error: No active rules in {args.in_scope}. Refusing to pass unscoped targets.\n")
        sys.exit(1)

    out_rules = load_rules(args.out_of_scope)

    streams = []
    if args.files:
        for fp in args.files:
            streams.append(open(fp, "r", encoding="utf-8", errors="ignore"))
    else:
        streams.append(sys.stdin)

    seen = set()
    kept = 0
    dropped_oos = 0
    dropped_unscoped = 0

    for stream in streams:
        for raw_line in stream:
            target = raw_line.strip()
            if not target or target.startswith("#"):
                continue
            host, path_part = extract_host_and_norm(target)
            if not host:
                continue
            full_lower = target.lower()

            # 1. Must match at least one in_scope rule
            if not any(matches_rule(host, path_part, full_lower, r) for r in in_rules):
                dropped_unscoped += 1
                continue

            # 2. Must NOT match any out_of_scope rule
            if any(matches_rule(host, path_part, full_lower, r) for r in out_rules):
                dropped_oos += 1
                continue

            if target not in seen:
                seen.add(target)
                kept += 1
                sys.stdout.write(target + "\n")

        if stream is not sys.stdin:
            stream.close()

    if not args.quiet:
        sys.stderr.write(
            f"[scope-filter] Kept: {kept} | Dropped (Out-of-Scope): {dropped_oos} | Dropped (Not In-Scope): {dropped_unscoped}\n"
        )


if __name__ == "__main__":
    main()
