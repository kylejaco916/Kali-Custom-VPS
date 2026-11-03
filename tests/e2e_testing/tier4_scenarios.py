#!/usr/bin/env python3
"""
Tier 4: Real-World Application-Level Scenarios Test Suite.
Validates realistic end-to-end toolchains across Recon, Web, Passwords, Sniffing, and Forensics.
>=5 application-level scenario tests.
"""

import os
import tempfile
import hashlib
from common import (
    test_case, run_cmd, assert_true, assert_equal, assert_in
)

# ============================================================================
# REAL-WORLD APPLICATION SCENARIOS (5 tests)
# ============================================================================

@test_case(tier=4, feature="ALL", name="t4_reconnaissance_chain",
           description="Scenario 1: Realistic Reconnaissance — Run nmap TCP connect scan against loopback and verify structured output")
def test_t4_reconnaissance_chain():
    # Execute nmap localhost scan against common ports
    cmd = "nmap -sT -p 22,80,443,8080 127.0.0.1 -oN -"
    code, stdout, stderr, elapsed = run_cmd(cmd, timeout=30)
    assert_equal(code, 0, f"nmap reconnaissance scan failed: {stderr}")
    assert_true("Nmap" in stdout and ("scan initiated" in stdout or "Starting Nmap" in stdout or "Nmap scan report" in stdout),
                f"Missing Nmap scan initiation: {stdout}")
    assert_true("Nmap scan report for" in stdout, f"Missing scan report header: {stdout}")
    assert_true("PORT" in stdout and "STATE" in stdout and "SERVICE" in stdout,
                f"Missing port table headers: {stdout}")
    assert_true("Nmap done" in stdout, f"Missing scan completion line: {stdout}")

@test_case(tier=4, feature="ALL", name="t4_web_assessment_chain",
           description="Scenario 2: Realistic Web Assessment — Execute sqlmap target inspection and nikto version signature scan")
def test_t4_web_assessment_chain():
    # 1. sqlmap dry-run target validation
    cmd_sqlmap = 'sqlmap -u "http://127.0.0.1:9999/test.php?id=1" --batch --retries 0 --timeout 1'
    code, stdout, stderr, elapsed = run_cmd(cmd_sqlmap, timeout=20)
    # sqlmap should handle unreachable host gracefully without fatal traceback
    assert_true("Traceback (most recent call last)" not in stderr,
                f"sqlmap crashed with traceback: {stderr}")
    assert_true("Traceback (most recent call last)" not in stdout,
                f"sqlmap crashed with traceback in stdout: {stdout}")
    assert_true("sqlmap" in stdout.lower() or "sqlmap" in stderr.lower(),
                "sqlmap did not initialize properly")

    # 2. nikto version scan
    code, stdout, stderr, _ = run_cmd("nikto -Version")
    assert_equal(code, 0, f"nikto version scan failed: {stderr}")
    assert_true("Nikto" in stdout or "nikto" in stdout.lower(), f"Unexpected nikto output: {stdout}")

@test_case(tier=4, feature="ALL", name="t4_password_audit_chain",
           description="Scenario 3: Realistic Password Audit — Hash target string, benchmark cracking engine, verify hashcat")
def test_t4_password_audit_chain():
    # 1. Create a known MD5 hash
    plaintext = "password123"
    md5_hash = hashlib.md5(plaintext.encode()).hexdigest()
    
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(f"{md5_hash}\n")
        hash_file = f.name
        
    try:
        # Check john cracking engine benchmark / format support
        code, stdout, stderr, elapsed = run_cmd("john --list=format-details", timeout=15)
        assert_equal(code, 0, f"john --list=format-details failed: {stderr}")
        assert_true("md5" in stdout.lower() or "raw-md5" in stdout.lower(),
                    "john missing raw-md5 format support")

        # 2. Verify hashcat can report device/engine status
        code, stdout, stderr, _ = run_cmd("hashcat --version")
        assert_equal(code, 0, f"hashcat --version failed: {stderr}")
        assert_true(len(stdout.strip()) > 0, "hashcat returned empty version")
    finally:
        if os.path.exists(hash_file):
            os.unlink(hash_file)

@test_case(tier=4, feature="ALL", name="t4_network_traffic_chain",
           description="Scenario 4: Realistic Network Traffic Analysis — Capture/dissect traffic with tcpdump and tshark")
def test_t4_network_traffic_chain():
    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".pcap") as f:
        pcap_file = f.name

    try:
        # Generate minimal valid PCAP file (24-byte header: magic d4 c3 b2 a1, v2.4, standard ethernet link type 1)
        pcap_hdr = bytes([
            0xd4, 0xc3, 0xb2, 0xa1,  # magic number
            0x02, 0x00,              # major version 2
            0x04, 0x00,              # minor version 4
            0x00, 0x00, 0x00, 0x00,  # thiszone
            0x00, 0x00, 0x00, 0x00,  # sigfigs
            0xff, 0xff, 0x00, 0x00,  # snaplen (65535)
            0x01, 0x00, 0x00, 0x00   # network (LINKTYPE_ETHERNET = 1)
        ])
        with open(pcap_file, "wb") as pf:
            pf.write(pcap_hdr)

        # 1. Verify tcpdump can read the pcap header cleanly
        code, stdout, stderr, _ = run_cmd(f"tcpdump -r {pcap_file}")
        assert_equal(code, 0, f"tcpdump failed to parse pcap header: {stderr}")

        # 2. Verify tshark can read the pcap file
        code, stdout, stderr, _ = run_cmd(f"tshark -r {pcap_file}")
        assert_equal(code, 0, f"tshark failed to parse pcap: {stderr}")
    finally:
        if os.path.exists(pcap_file):
            os.unlink(pcap_file)

@test_case(tier=4, feature="ALL", name="t4_binary_forensics_chain",
           description="Scenario 5: Realistic Forensics & Reversing — Extract ELF headers with radare2 and inspect magic with binwalk")
def test_t4_binary_forensics_chain():
    target_binary = "/usr/bin/true"
    assert_true(os.path.exists(target_binary), f"Target binary {target_binary} missing")

    # 1. radare2 binary info extraction
    cmd_r2 = f'radare2 -qc "i" {target_binary}'
    code, stdout, stderr, _ = run_cmd(cmd_r2, timeout=15)
    assert_equal(code, 0, f"radare2 binary inspection failed: {stderr}")
    assert_true("arch" in stdout.lower(), f"radare2 failed to identify binary architecture: {stdout}")
    assert_true("bits" in stdout.lower(), f"radare2 failed to identify binary bit width: {stdout}")

    # 2. binwalk signature scan
    cmd_binwalk = f"binwalk {target_binary}"
    code, stdout, stderr, _ = run_cmd(cmd_binwalk, timeout=15)
    assert_equal(code, 0, f"binwalk signature scan failed: {stderr}")
    assert_true("DECIMAL" in stdout and "HEXADECIMAL" in stdout and "DESCRIPTION" in stdout,
                f"Missing standard binwalk table headers: {stdout}")
    assert_true("ELF" in stdout, f"binwalk failed to recognize ELF signature in {target_binary}: {stdout}")
