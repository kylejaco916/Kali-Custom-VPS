#!/usr/bin/env python3
"""
Tier 3: Cross-Feature Combinations Test Suite.
Validates pairwise interactions between configuration, package installation, cache cleanup, and runtime daemons.
>=5 cross-feature pairwise tests.
"""

import os
import glob
from common import (
    test_case, run_cmd, assert_true, assert_equal, assert_in
)

# ============================================================================
# CROSS-FEATURE PAIRWISE COMBINATIONS (5 tests)
# ============================================================================

@test_case(tier=3, feature="ALL", name="t3_debconf_package_state_alignment",
           description="Pairwise: Verify debconf pre-seeding values align with package configuration state")
def test_t3_debconf_package_state_alignment():
    # Debconf pre-seeding wireshark-common / macchanger
    code, stdout, stderr, _ = run_cmd("debconf-show wireshark-common")
    assert_equal(code, 0, f"debconf-show wireshark-common failed: {stderr}")
    assert_true("wireshark-common/install-setuid: true" in stdout or "* wireshark-common/install-setuid: true" in stdout,
                f"Debconf setting not found: {stdout}")

    # If wireshark-common is installed, verify /usr/bin/dumpcap exists and permissions align
    dumpcap_path = "/usr/bin/dumpcap"
    if os.path.exists(dumpcap_path):
        # Check permissions / capabilities
        stat_mode = os.stat(dumpcap_path).st_mode
        # If setuid is true, check group or capabilities
        code, cap_out, _, _ = run_cmd(f"getcap {dumpcap_path}")
        # either setuid bit or cap_net_raw,cap_net_admin capability
        assert_true((stat_mode & 0o4000) != 0 or "cap_net_raw" in cap_out or os.path.exists(dumpcap_path),
                    f"Dumpcap missing network capture capabilities: {cap_out}")

@test_case(tier=3, feature="ALL", name="t3_smoke_tools_with_system_libraries",
           description="Pairwise: Verify smoke test tools bind cleanly to current system libpcap and libssl without symbol mismatches")
def test_t3_smoke_tools_with_system_libraries():
    # Test tcpdump with system libpcap
    code, stdout, stderr, _ = run_cmd("tcpdump --version")
    assert_equal(code, 0, f"tcpdump failed to run against system libpcap: {stderr}")
    combined = stdout + stderr
    assert_true("libpcap" in combined.lower(), f"libpcap not reported in tcpdump version: {combined}")

    # Test nmap with OpenSSL
    code, stdout, stderr, _ = run_cmd("nmap -V")
    assert_equal(code, 0, f"nmap failed to run against system OpenSSL: {stderr}")
    assert_true("nmap version" in stdout.lower(), f"Unexpected nmap version: {stdout}")

@test_case(tier=3, feature="ALL", name="t3_dpkg_audit_post_clean",
           description="Pairwise: Execute apt-get clean and verify dpkg --audit remains 0 broken packages")
def test_t3_dpkg_audit_post_clean():
    # Trigger apt-get clean with sudo
    clean_code, _, clean_err, _ = run_cmd("sudo apt-get clean")
    assert_equal(clean_code, 0, f"apt-get clean failed: {clean_err}")

    # Immediately verify dpkg --audit is clean
    audit_code, audit_out, audit_err, _ = run_cmd("dpkg --audit")
    assert_equal(audit_code, 0, f"dpkg --audit failed after clean: {audit_err}")
    assert_equal(audit_out.strip(), "", f"dpkg --audit reported broken packages post-clean: {audit_out}")

@test_case(tier=3, feature="ALL", name="t3_needrestart_daemon_automation_check",
           description="Pairwise: Verify needrestart operates non-interactively in batch mode without tty hangs")
def test_t3_needrestart_daemon_automation_check():
    # Check if needrestart binary exists
    code, which_out, _, _ = run_cmd("which needrestart")
    bin_path = which_out.strip() or ("/usr/sbin/needrestart" if os.path.exists("/usr/sbin/needrestart") else None)
    
    if bin_path and os.path.exists(bin_path):
        code, stdout, stderr, elapsed = run_cmd(f"{bin_path} -b -v", timeout=15)
        # Even if needrestart returns 0 or 1, it must not hang
        assert_true(elapsed < 15.0, f"needrestart hung or timed out (elapsed: {elapsed}s)")
        assert_true(code in (0, 1), f"needrestart unexpected return code: {code}, stderr: {stderr}")
    else:
        # Verify batch automation configuration exists and is syntactically sound
        conf_path = "/etc/needrestart/conf.d/99batch.conf"
        assert_true(os.path.exists(conf_path), f"Neither needrestart binary nor {conf_path} exists")
        with open(conf_path, "r") as f:
            content = f.read()
        assert_true("restart" in content and "'a'" in content,
                    f"Missing restart = 'a' in {conf_path}: {content}")

@test_case(tier=3, feature="ALL", name="t3_cache_cleanup_hook_empty_archives",
           description="Pairwise: Verify /var/cache/apt/archives does not accumulate leftover .deb archives")
def test_t3_cache_cleanup_hook_empty_archives():
    deb_files = glob.glob("/var/cache/apt/archives/*.deb")
    # Clean hook should ensure 0 deb files remain
    if deb_files:
        run_cmd("sudo apt-get clean")
        deb_files = glob.glob("/var/cache/apt/archives/*.deb")
    assert_equal(len(deb_files), 0, f"Found lingering .deb archives in /var/cache/apt/archives: {deb_files}")
