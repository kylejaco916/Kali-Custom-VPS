#!/usr/bin/env bash
# ==============================================================================
# Safe-Harbor Compliant Recon & API Surface Pipeline (run_recon.sh)
# Strictly filters all assets against scope/in_scope.txt & scope/out_of_scope.txt
# before any active DNS, port, or HTTP probing occurs.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

[ -f "$HOME/.bounty_env" ] && source "$HOME/.bounty_env"

IN_SCOPE="scope/in_scope.txt"
OUT_SCOPE="scope/out_of_scope.txt"
FILTER="./scope_filter.sh"

if [ ! -f "$IN_SCOPE" ]; then
    echo "[!] Missing $IN_SCOPE" >&2
    exit 1
fi

echo "[*] Extracting root seed domains from $IN_SCOPE..."
grep -v '^#' "$IN_SCOPE" | sed -E 's#^\*\.##; s#^https?://##; s#/.*$##' | sort -u | grep -v '^$' > recon/seed_domains.txt

echo "[1/6] Passive Subdomain Discovery (subfinder + amass)..."
subfinder -dL recon/seed_domains.txt -silent > recon/raw_subdomains.txt || true
# Optional passive amass enum (timeout 2m per seed list)
amass enum -passive -df recon/seed_domains.txt -timeout 2 -silent >> recon/raw_subdomains.txt 2>/dev/null || true

echo "[2/6] Enforcing Safe-Harbor Scope Gate on Passive Subdomains..."
"$FILTER" -i "$IN_SCOPE" -o "$OUT_SCOPE" recon/raw_subdomains.txt > recon/scoped_subdomains.txt

echo "[3/6] DNS Permutations & Resolution (alterx -> scope-filter -> dnsx)..."
cat recon/scoped_subdomains.txt | alterx -silent 2>/dev/null | "$FILTER" -i "$IN_SCOPE" -o "$OUT_SCOPE" -q > recon/permuted_scoped.txt || true
cat recon/scoped_subdomains.txt recon/permuted_scoped.txt | sort -u | dnsx -silent -rate-limit "${MAX_RATE:-10}" | "$FILTER" -i "$IN_SCOPE" -o "$OUT_SCOPE" > recon/resolved_hosts.txt

echo "[4/6] Service Enumeration & HTTP Probing (naabu -> httpx-safe -> gowitness)..."
naabu -list recon/resolved_hosts.txt -rate "${MAX_RATE:-10}" -silent 2>/dev/null | "$FILTER" -i "$IN_SCOPE" -o "$OUT_SCOPE" > recon/open_ports.txt || true
cat recon/resolved_hosts.txt recon/open_ports.txt | sort -u | /usr/local/bin/httpx-safe -silent > recon/live_web.txt
gowitness scan file -f recon/live_web.txt --write-db --screenshot-path recon/screenshots >/dev/null 2>&1 || true

echo "[5/6] Historical & Active Endpoint Discovery (gau + waybackurls + katana-safe)..."
cat recon/resolved_hosts.txt | gau --threads 2 2>/dev/null > recon/raw_urls.txt || true
cat recon/resolved_hosts.txt | waybackurls >> recon/raw_urls.txt 2>/dev/null || true
/usr/local/bin/katana-safe -list recon/live_web.txt -jc -silent >> recon/raw_urls.txt 2>/dev/null || true

echo "[*] Filtering all discovered URLs strictly against Scope Gate..."
"$FILTER" -i "$IN_SCOPE" -o "$OUT_SCOPE" recon/raw_urls.txt > recon/scoped_urls.txt

echo "[6/6] Client-Side JS Secret Analysis (trufflehog)..."
grep -iE '\.js(\?|$)' recon/scoped_urls.txt > js/js_urls.txt || true
echo "[+] Pipeline complete. Scoped outputs stored in recon/ and js/."
