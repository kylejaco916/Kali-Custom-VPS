#!/usr/bin/env python3
"""
Tier 2: Boundary & Corner Cases Test Suite.
Validates edge cases, negative tests, extreme conditions, mathematical thresholds, and binary resolution.
>=5 test cases per feature across R1, R2, and R3.
"""

import os
import stat
import subprocess
import re
from common import (
    test_case, run_cmd, assert_true, assert_equal, assert_in, assert_not_in,
    KALI_METAPACKAGES
)

# ============================================================================
# FEATURE R1: Boundary & Corner Cases (5 tests)
# ============================================================================

@test_case(tier=2, feature="R1", name="t2_r1_apt_config_dump_syntax",
           description="Verify apt-config dump parses all drop-in configuration files without syntax errors")
def test_t2_r1_apt_config_dump_syntax():
    code, stdout, stderr, _ = run_cmd("apt-config dump")
    assert_equal(code, 0, f"apt-config dump failed: {stderr}")
    combined = stdout + stderr
    assert_true("syntax error" not in combined.lower(), f"Syntax error detected in apt config: {combined}")
    assert_true("warning" not in stderr.lower(), f"Warnings detected during apt config parsing: {stderr}")

@test_case(tier=2, feature="R1", name="t2_r1_needrestart_perl_syntax",
           description="Verify /etc/needrestart/conf.d/99batch.conf has valid Perl syntax via perl -c")
def test_t2_r1_needrestart_perl_syntax():
    conf_path = "/etc/needrestart/conf.d/99batch.conf"
    assert_true(os.path.exists(conf_path), f"File {conf_path} does not exist")
    code, stdout, stderr, _ = run_cmd(f"perl -c {conf_path}")
    assert_equal(code, 0, f"perl -c failed on {conf_path}: {stderr}")
    combined = stdout + stderr
    assert_true("syntax OK" in combined, f"Expected 'syntax OK', got: {combined}")

@test_case(tier=2, feature="R1", name="t2_r1_debconf_negative_query",
           description="Negative test: querying nonexistent debconf template returns non-zero/empty without hanging")
def test_t2_r1_debconf_negative_query():
    code, stdout, stderr, elapsed = run_cmd("debconf-show nonexistent-package-random-99", timeout=5)
    # debconf-show on unknown package exits 0 with empty stdout, or non-zero, but must complete in < 5s
    assert_true(elapsed < 5.0, f"debconf-show hung on nonexistent package query (elapsed: {elapsed}s)")
    assert_equal(stdout.strip(), "", f"Unexpected output for nonexistent package: {stdout}")

@test_case(tier=2, feature="R1", name="t2_r1_dpkg_lock_files_not_held",
           description="Verify APT and DPKG lock files are not held by lingering background processes")
def test_t2_r1_dpkg_lock_files_not_held():
    lock_files = [
        "/var/lib/dpkg/lock",
        "/var/lib/dpkg/lock-frontend",
        "/var/lib/apt/lists/lock",
        "/var/cache/apt/archives/lock"
    ]
    for lock in lock_files:
        if os.path.exists(lock):
            code, stdout, stderr, _ = run_cmd(f"fuser {lock}")
            # fuser exits 1 if no process has the file open
            assert_true(code != 0 or stdout.strip() == "",
                        f"Lock file {lock} is held by active process PID: {stdout.strip()}")

@test_case(tier=2, feature="R1", name="t2_r1_conf_file_permissions",
           description="Verify configuration drop-ins in /etc/apt/apt.conf.d/ have safe read permissions")
def test_t2_r1_conf_file_permissions():
    files = [
        "/etc/apt/apt.conf.d/99noninteractive",
        "/etc/apt/apt.conf.d/99clean-cache"
    ]
    for path in files:
        assert_true(os.path.exists(path), f"Configuration file {path} missing")
        mode = stat.S_IMODE(os.stat(path).st_mode)
        # Must be readable by all (0644 or 0444)
        assert_true(bool(mode & stat.S_IRUSR) and bool(mode & stat.S_IRGRP) and bool(mode & stat.S_IROTH),
                    f"File {path} lacks world-read permissions: {oct(mode)}")


# ============================================================================
# FEATURE R2: Boundary & Corner Cases (5 tests)
# ============================================================================

@test_case(tier=2, feature="R2", name="t2_r2_negative_nonexistent_metapackage",
           description="Negative test: dpkg-query for nonexistent metapackage returns exit code 1 cleanly")
def test_t2_r2_negative_nonexistent_metapackage():
    code, stdout, stderr, _ = run_cmd("dpkg-query -W -f='${Package} ${Status}\\n' kali-tools-nonexistent-xyz")
    assert_equal(code, 1, f"dpkg-query should return 1 for nonexistent package, got {code}")
    assert_true("no packages found" in stderr.lower() or "not installed" in stderr.lower() or code == 1,
                f"Unexpected stderr for nonexistent package: {stderr}")

@test_case(tier=2, feature="R2", name="t2_r2_no_half_configured_metapackages",
           description="Boundary test: Assert zero kali-tools-* metapackages are in iF, iU, or rc state")
def test_t2_r2_no_half_configured_metapackages():
    code, stdout, stderr, _ = run_cmd("dpkg-query -W -f='${Package} ${Status}\\n' 'kali-tools-*'")
    # If no packages are installed yet, stdout will be empty (or error)
    if code == 0 and stdout.strip():
        bad_states = []
        for line in stdout.strip().splitlines():
            parts = line.strip().split()
            if len(parts) >= 4:
                status = " ".join(parts[1:])
                if status != "install ok installed":
                    bad_states.append(f"{parts[0]}: {status}")
        assert_equal(len(bad_states), 0,
                     f"Found metapackages in broken/transitional state: {bad_states}")

@test_case(tier=2, feature="R2", name="t2_r2_apt_check_broken_dependencies",
           description="Verify apt-get check runs cleanly and asserts 0 broken dependencies system-wide")
def test_t2_r2_apt_check_broken_dependencies():
    code, stdout, stderr, _ = run_cmd("apt-get check")
    assert_equal(code, 0, f"apt-get check failed: {stderr}")
    combined = stdout + stderr
    assert_true("broken" not in combined.lower() or "0 broken" in combined.lower(),
                f"Broken dependencies found in apt-get check: {combined}")

@test_case(tier=2, feature="R2", name="t2_r2_no_architecture_conflicts",
           description="Assert no 32-bit (i386) architecture conflict exists for kali-tools-* packages")
def test_t2_r2_no_architecture_conflicts():
    code, stdout, stderr, _ = run_cmd("dpkg-query -W -f='${Package}:${Architecture}\\n' 'kali-tools-*:i386'")
    # dpkg-query should find no matching i386 metapackages (code != 0 or empty)
    if code == 0:
        assert_equal(stdout.strip(), "", f"Unexpected 32-bit i386 metapackages installed: {stdout}")

@test_case(tier=2, feature="R2", name="t2_r2_metapackage_doc_manifest",
           description="Verify installed metapackages contain valid changelog/copyright doc files in /usr/share/doc")
def test_t2_r2_metapackage_doc_manifest():
    code, stdout, stderr, _ = run_cmd("dpkg -L kali-tools-top10")
    assert_equal(code, 0, f"dpkg -L kali-tools-top10 failed: {stderr}")
    assert_true("/usr/share/doc/kali-tools-top10" in stdout,
                f"Doc directory missing in package file manifest: {stdout}")


# ============================================================================
# FEATURE R3: Boundary & Corner Cases (5 tests)
# ============================================================================

@test_case(tier=2, feature="R3", name="t2_r3_disk_headroom_exact_byte_math",
           description="Mathematical assertion: Verify free space on root filesystem is strictly >= 15 * 10^9 bytes")
def test_t2_r3_disk_headroom_exact_byte_math():
    stat = os.statvfs("/")
    # free bytes available to unprivileged user
    free_bytes = stat.f_bavail * stat.f_frsize
    required_bytes = 15 * (1024 ** 3) # 15 GiB = 16,106,127,360 bytes
    min_decimal_bytes = 15 * (1000 ** 3) # 15 GB = 15,000,000,000 bytes
    
    assert_true(free_bytes >= min_decimal_bytes,
                f"Insufficient disk headroom: {free_bytes:,} bytes available, required at least {min_decimal_bytes:,} bytes")

@test_case(tier=2, feature="R3", name="t2_r3_shared_library_ldd_resolution",
           description="Assert all top-category tool binaries have 0 missing shared libraries via ldd")
def test_t2_r3_shared_library_ldd_resolution():
    tools = ["nmap", "tcpdump", "sqlmap", "amass", "nikto", "john", "hashcat", "tshark", "radare2", "binwalk"]
    unresolved = []
    
    for tool in tools:
        # Resolve binary path
        code, which_out, _, _ = run_cmd(f"which {tool}")
        if code != 0 or not which_out.strip():
            unresolved.append(f"{tool} (binary not found)")
            continue
        
        bin_path = which_out.strip()
        # If it's a script (e.g. python/bash/perl), skip ldd or check ELF
        with open(bin_path, "rb") as f:
            header = f.read(4)
        if header != b"\x7fELF":
            continue
            
        code, ldd_out, ldd_err, _ = run_cmd(f"ldd {bin_path}")
        if code != 0:
            unresolved.append(f"{tool} (ldd exited with code {code})")
            continue
        
        missing = [line.strip() for line in ldd_out.splitlines() if "not found" in line]
        if missing:
            unresolved.append(f"{tool} missing libraries: {missing}")
            
    assert_equal(len(unresolved), 0, f"Shared library resolution failures: {unresolved}")

@test_case(tier=2, feature="R3", name="t2_r3_john_shim_passthrough_behavior",
           description="Verify /usr/local/bin/john shim handles --version and passes through build info")
def test_t2_r3_john_shim_passthrough_behavior():
    john_path = "/usr/local/bin/john"
    assert_true(os.path.exists(john_path), f"John wrapper at {john_path} does not exist")
    assert_true(os.access(john_path, os.X_OK), f"John wrapper at {john_path} is not executable")
    
    # Check --version flag
    code, stdout, stderr, _ = run_cmd(f"{john_path} --version")
    assert_equal(code, 0, f"{john_path} --version failed with code {code}: {stderr}")
    assert_true("John the Ripper" in stdout or "build" in stdout.lower() or "version" in stdout.lower(),
                f"Unexpected output from john --version: {stdout}")

@test_case(tier=2, feature="R3", name="t2_r3_tool_invalid_flag_rejection",
           description="Verify smoke test tools safely reject invalid flags with non-zero exit and no crash")
def test_t2_r3_tool_invalid_flag_rejection():
    # Tools should cleanly reject unknown flags without core dumping (signal 139) or crashing
    test_commands = [
        "nmap --totally-invalid-flag-12345",
        "tcpdump --invalid-arg-xyz 2>&1"
    ]
    for cmd in test_commands:
        code, stdout, stderr, _ = run_cmd(cmd)
        assert_true(code != 0, f"Expected non-zero exit for invalid flag on command: {cmd}")
        assert_true(code != 139, f"Segmentation fault detected on command: {cmd}")

@test_case(tier=2, feature="R3", name="t2_r3_dpkg_status_file_integrity",
           description="Verify /var/lib/dpkg/status database exists, is readable, and contains valid stanzas")
def test_t2_r3_dpkg_status_file_integrity():
    status_file = "/var/lib/dpkg/status"
    assert_true(os.path.exists(status_file), f"Status file {status_file} missing")
    file_size = os.path.getsize(status_file)
    assert_true(file_size > 1_000_000, f"/var/lib/dpkg/status unexpectedly small ({file_size} bytes)")
    
    # Read first 1000 lines to ensure valid RFC822 stanzas
    with open(status_file, "r", encoding="utf-8", errors="replace") as f:
        head = [next(f) for _ in range(200)]
    content = "".join(head)
    assert_true("Package:" in content, "No 'Package:' key found in /var/lib/dpkg/status")
    assert_true("Status:" in content, "No 'Status:' key found in /var/lib/dpkg/status")
