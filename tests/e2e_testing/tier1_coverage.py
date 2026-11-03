#!/usr/bin/env python3
"""
Tier 1: Feature Coverage Test Suite.
Validates core functionality for R1, R2, and R3 requirements.
>=5 test cases per feature.
"""

import os
import re
from common import (
    test_case, run_cmd, assert_true, assert_equal, assert_in,
    KALI_METAPACKAGES
)

# ============================================================================
# FEATURE R1: Pre-Flight Storage & Debconf Configuration (7 tests)
# ============================================================================

@test_case(tier=1, feature="R1", name="t1_r1_dpkg_noninteractive_options",
           description="Verify Dpkg::Options contains --force-confdef and --force-confold in apt config")
def test_t1_r1_dpkg_noninteractive_options():
    code, stdout, stderr, _ = run_cmd("apt-config dump")
    assert_equal(code, 0, f"apt-config dump failed: {stderr}")
    assert_in('DPkg::Options:: "--force-confdef";', stdout,
              "APT config missing DPkg::Options '--force-confdef'")
    assert_in('DPkg::Options:: "--force-confold";', stdout,
              "APT config missing DPkg::Options '--force-confold'")

@test_case(tier=1, feature="R1", name="t1_r1_assume_yes_and_fix_broken",
           description="Verify APT::Get::Assume-Yes and APT::Get::Fix-Broken are configured to true")
def test_t1_r1_assume_yes_and_fix_broken():
    conf_path = "/etc/apt/apt.conf.d/99noninteractive"
    assert_true(os.path.exists(conf_path), f"File {conf_path} does not exist")
    with open(conf_path, "r") as f:
        content = f.read()
    assert_true(re.search(r'APT::Get::Assume-Yes\s+"true";', content) is not None,
                "Missing APT::Get::Assume-Yes 'true' in 99noninteractive")
    assert_true(re.search(r'APT::Get::Fix-Broken\s+"true";', content) is not None,
                "Missing APT::Get::Fix-Broken 'true' in 99noninteractive")

@test_case(tier=1, feature="R1", name="t1_r1_debconf_wireshark",
           description="Verify debconf database contains pre-seeded wireshark-common/install-setuid")
def test_t1_r1_debconf_wireshark():
    code, stdout, stderr, _ = run_cmd("debconf-show wireshark-common")
    assert_equal(code, 0, f"debconf-show wireshark-common failed: {stderr}")
    assert_true("wireshark-common/install-setuid: true" in stdout or "* wireshark-common/install-setuid: true" in stdout,
                f"wireshark-common/install-setuid not pre-seeded to true: {stdout}")

@test_case(tier=1, feature="R1", name="t1_r1_debconf_kismet_macchanger_sslh",
           description="Verify debconf pre-seeding for kismet, macchanger, and sslh")
def test_t1_r1_debconf_kismet_macchanger_sslh():
    # Check kismet
    code, stdout, stderr, _ = run_cmd("debconf-show kismet")
    assert_equal(code, 0, f"debconf-show kismet failed: {stderr}")
    assert_true("kismet/install-setuid" in stdout, f"kismet/install-setuid missing: {stdout}")

    # Check macchanger
    code, stdout, stderr, _ = run_cmd("debconf-show macchanger")
    assert_equal(code, 0, f"debconf-show macchanger failed: {stderr}")
    assert_true("macchanger/automatically" in stdout, f"macchanger answer missing: {stdout}")

    # Check sslh
    code, stdout, stderr, _ = run_cmd("debconf-show sslh")
    assert_equal(code, 0, f"debconf-show sslh failed: {stderr}")
    assert_true("sslh/run_mode" in stdout, f"sslh/run_mode answer missing: {stdout}")

@test_case(tier=1, feature="R1", name="t1_r1_clean_cache_keep_packages",
           description="Verify APT::Keep-Downloaded-Packages is false in apt configuration")
def test_t1_r1_clean_cache_keep_packages():
    code, stdout, stderr, _ = run_cmd("apt-config dump")
    assert_equal(code, 0, f"apt-config dump failed: {stderr}")
    assert_in('APT::Keep-Downloaded-Packages "false";', stdout,
              "APT config missing APT::Keep-Downloaded-Packages 'false'")

@test_case(tier=1, feature="R1", name="t1_r1_clean_cache_post_invoke",
           description="Verify DPkg::Post-Invoke clean hook exists in 99clean-cache")
def test_t1_r1_clean_cache_post_invoke():
    conf_path = "/etc/apt/apt.conf.d/99clean-cache"
    assert_true(os.path.exists(conf_path), f"File {conf_path} does not exist")
    with open(conf_path, "r") as f:
        content = f.read()
    assert_true("apt-get clean" in content, f"apt-get clean missing in {conf_path}")

@test_case(tier=1, feature="R1", name="t1_r1_needrestart_auto_mode",
           description="Verify needrestart automation config sets restart mode to automatic ('a')")
def test_t1_r1_needrestart_auto_mode():
    conf_path = "/etc/needrestart/conf.d/99batch.conf"
    assert_true(os.path.exists(conf_path), f"File {conf_path} does not exist")
    with open(conf_path, "r") as f:
        content = f.read()
    assert_true(re.search(r"\$nrconf\{restart\}\s*=\s*['\"]a['\"];", content) is not None,
                f"Missing $nrconf{{restart}} = 'a' in {conf_path}")


# ============================================================================
# FEATURE R2: Complete 28 kali-tools-* Suite Deployment (5 tests)
# ============================================================================

@test_case(tier=1, feature="R2", name="t1_r2_metapackages_in_catalog",
           description="Verify all 28 official kali-tools-* metapackages exist in apt cache catalog")
def test_t1_r2_metapackages_in_catalog():
    missing = []
    for pkg in KALI_METAPACKAGES:
        code, stdout, stderr, _ = run_cmd(f"apt-cache show {pkg}")
        if code != 0 or f"Package: {pkg}" not in stdout:
            missing.append(pkg)
    assert_equal(len(missing), 0, f"The following metapackages are missing from apt cache: {missing}")

@test_case(tier=1, feature="R2", name="t1_r2_metapackage_candidate_versions",
           description="Verify non-empty candidate version exists for each of the 28 metapackages")
def test_t1_r2_metapackage_candidate_versions():
    no_candidate = []
    for pkg in KALI_METAPACKAGES:
        code, stdout, stderr, _ = run_cmd(f"apt-cache policy {pkg}")
        if code != 0:
            no_candidate.append(f"{pkg} (query failed)")
            continue
        match = re.search(r"Candidate:\s*(\S+)", stdout)
        if not match or match.group(1) == "(none)":
            no_candidate.append(pkg)
    assert_equal(len(no_candidate), 0, f"Metapackages with no candidate version: {no_candidate}")

@test_case(tier=1, feature="R2", name="t1_r2_metapackage_architectures",
           description="Verify package architecture is 'all' or 'amd64' for all 28 metapackages")
def test_t1_r2_metapackage_architectures():
    invalid_arch = []
    for pkg in KALI_METAPACKAGES:
        code, stdout, stderr, _ = run_cmd(f"apt-cache show {pkg}")
        if code != 0:
            invalid_arch.append(f"{pkg} (show failed)")
            continue
        arch_match = re.search(r"Architecture:\s*(\S+)", stdout)
        if not arch_match or arch_match.group(1) not in ("all", "amd64"):
            invalid_arch.append(f"{pkg} ({arch_match.group(1) if arch_match else 'missing'})")
    assert_equal(len(invalid_arch), 0, f"Metapackages with unexpected architecture: {invalid_arch}")

@test_case(tier=1, feature="R2", name="t1_r2_metapackage_dependency_trees",
           description="Verify apt-cache depends outputs valid dependency trees for core metapackages")
def test_t1_r2_metapackage_dependency_trees():
    sample_pkgs = ["kali-tools-top10", "kali-tools-information-gathering", "kali-tools-web", "kali-tools-passwords"]
    for pkg in sample_pkgs:
        code, stdout, stderr, _ = run_cmd(f"apt-cache depends {pkg}")
        assert_equal(code, 0, f"apt-cache depends failed on {pkg}: {stderr}")
        assert_true("Depends:" in stdout or "Recommends:" in stdout,
                    f"No Depends/Recommends found for {pkg}: {stdout}")

@test_case(tier=1, feature="R2", name="t1_r2_all_28_metapackages_installed_ii",
           description="Verify exactly 28 kali-tools-* metapackages are installed in 'ii' status")
def test_t1_r2_all_28_metapackages_installed_ii():
    code, stdout, stderr, _ = run_cmd("dpkg-query -W -f='${Package} ${Status}\\n' 'kali-tools-*'")
    installed_pkgs = {}
    if code == 0 and stdout:
        for line in stdout.strip().splitlines():
            parts = line.strip().split()
            if len(parts) >= 4 and parts[1] == "install" and parts[2] == "ok" and parts[3] == "installed":
                installed_pkgs[parts[0]] = "ii"
    
    missing_from_installed = [pkg for pkg in KALI_METAPACKAGES if pkg not in installed_pkgs]
    assert_equal(len(missing_from_installed), 0,
                 f"Not all 28 metapackages installed. Missing ({len(missing_from_installed)}): {missing_from_installed}")
    assert_true(len(installed_pkgs) >= 28,
                f"Expected at least 28 kali-tools-* metapackages in ii state, found {len(installed_pkgs)}")


# ============================================================================
# FEATURE R3: Post-Installation Verification & Cleanup (7 tests)
# ============================================================================

@test_case(tier=1, feature="R3", name="t1_r3_dpkg_audit_zero_broken",
           description="Verify dpkg --audit exits with code 0 and reports no unconfigured packages")
def test_t1_r3_dpkg_audit_zero_broken():
    code, stdout, stderr, _ = run_cmd("dpkg --audit")
    assert_equal(code, 0, f"dpkg --audit failed with code {code}: {stderr}")
    assert_equal(stdout.strip(), "", f"dpkg --audit reported broken/unconfigured packages: {stdout}")

@test_case(tier=1, feature="R3", name="t1_r3_disk_headroom_ge_15gb",
           description="Verify df -BG / confirms at least 15 GB of free space remains on /dev/sda1")
def test_t1_r3_disk_headroom_ge_15gb():
    code, stdout, stderr, _ = run_cmd("df -BG /")
    assert_equal(code, 0, f"df command failed: {stderr}")
    lines = stdout.strip().splitlines()
    assert_true(len(lines) >= 2, f"Unexpected df output format: {stdout}")
    # Filesystem 1G-blocks Used Available Use% Mounted on
    parts = lines[1].split()
    # Available is index 3 (e.g. '35G')
    avail_str = parts[3].rstrip("G")
    avail_gb = int(avail_str)
    assert_true(avail_gb >= 15, f"Available disk headroom ({avail_gb} GB) is less than required 15 GB")

@test_case(tier=1, feature="R3", name="t1_r3_smoke_recon_nmap_amass",
           description="Smoke test: Execute nmap --version and amass -version with exit code 0")
def test_t1_r3_smoke_recon_nmap_amass():
    # nmap
    code, stdout, stderr, _ = run_cmd("nmap --version")
    assert_equal(code, 0, f"nmap --version failed: {stderr}")
    combined_nmap = (stdout + stderr).lower()
    assert_true("nmap" in combined_nmap, f"Unexpected nmap version output: {stdout + stderr}")

    # amass (amass prints version to stderr)
    code, stdout, stderr, _ = run_cmd("amass -version")
    assert_equal(code, 0, f"amass -version failed: {stderr}")
    combined_amass = (stdout + stderr).strip()
    assert_true(len(combined_amass) > 0, "amass -version returned empty output")

@test_case(tier=1, feature="R3", name="t1_r3_smoke_web_sqlmap_nikto",
           description="Smoke test: Execute sqlmap --version and nikto -Version with exit code 0")
def test_t1_r3_smoke_web_sqlmap_nikto():
    # sqlmap
    code, stdout, stderr, _ = run_cmd("sqlmap --version")
    assert_equal(code, 0, f"sqlmap --version failed: {stderr}")
    combined_sqlmap = (stdout + stderr).strip()
    assert_true(len(combined_sqlmap) > 0, "sqlmap --version returned empty output")

    # nikto
    code, stdout, stderr, _ = run_cmd("nikto -Version")
    assert_equal(code, 0, f"nikto -Version failed: {stderr}")
    combined_nikto = (stdout + stderr).lower()
    assert_true("nikto" in combined_nikto, f"Unexpected nikto version output: {stdout + stderr}")

@test_case(tier=1, feature="R3", name="t1_r3_smoke_passwords_john_hashcat",
           description="Smoke test: Execute john --version and hashcat --version with exit code 0")
def test_t1_r3_smoke_passwords_john_hashcat():
    # john
    code, stdout, stderr, _ = run_cmd("john --version")
    assert_equal(code, 0, f"john --version failed: {stderr}")
    combined_john = (stdout + stderr).lower()
    assert_true("john" in combined_john or "ripper" in combined_john or "build" in combined_john,
                f"Unexpected john output: {stdout + stderr}")

    # hashcat
    code, stdout, stderr, _ = run_cmd("hashcat --version")
    assert_equal(code, 0, f"hashcat --version failed: {stderr}")
    combined_hashcat = (stdout + stderr).strip()
    assert_true(len(combined_hashcat) > 0, "hashcat --version returned empty output")

@test_case(tier=1, feature="R3", name="t1_r3_smoke_sniffing_tshark_tcpdump",
           description="Smoke test: Execute tshark --version and tcpdump --version with exit code 0")
def test_t1_r3_smoke_sniffing_tshark_tcpdump():
    # tshark
    code, stdout, stderr, _ = run_cmd("tshark --version")
    assert_equal(code, 0, f"tshark --version failed: {stderr}")
    combined_tshark = stdout + stderr
    assert_true("TShark" in combined_tshark or "Wireshark" in combined_tshark,
                f"Unexpected tshark output: {combined_tshark}")

    # tcpdump
    code, stdout, stderr, _ = run_cmd("tcpdump --version")
    assert_equal(code, 0, f"tcpdump --version failed: {stderr}")
    combined_tcpdump = (stdout + stderr).lower()
    assert_true("tcpdump" in combined_tcpdump or "libpcap" in combined_tcpdump,
                f"Unexpected tcpdump version output: {stdout + stderr}")

@test_case(tier=1, feature="R3", name="t1_r3_smoke_reversing_radare2_binwalk",
           description="Smoke test: Execute radare2 -v and binwalk --help with exit code 0")
def test_t1_r3_smoke_reversing_radare2_binwalk():
    # radare2
    code, stdout, stderr, _ = run_cmd("radare2 -v")
    assert_equal(code, 0, f"radare2 -v failed: {stderr}")
    combined_r2 = (stdout + stderr).lower()
    assert_true("radare2" in combined_r2, f"Unexpected radare2 output: {stdout + stderr}")

    # binwalk
    code, stdout, stderr, _ = run_cmd("binwalk --help")
    assert_equal(code, 0, f"binwalk --help failed: {stderr}")
    combined_binwalk = (stdout + stderr).lower()
    assert_true("binwalk" in combined_binwalk, f"Unexpected binwalk output: {stdout + stderr}")
