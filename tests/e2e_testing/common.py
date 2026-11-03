#!/usr/bin/env python3
"""
Common utilities, test harness, and registries for the E2E Test Suite.
"""

import sys
import os
import subprocess
import time
import json
import re
from typing import List, Dict, Any, Callable, Optional, Tuple

KALI_METAPACKAGES = [
    "kali-tools-802-11",
    "kali-tools-bluetooth",
    "kali-tools-crypto-stego",
    "kali-tools-database",
    "kali-tools-detect",
    "kali-tools-exploitation",
    "kali-tools-forensics",
    "kali-tools-fuzzing",
    "kali-tools-gpu",
    "kali-tools-hardware",
    "kali-tools-identify",
    "kali-tools-information-gathering",
    "kali-tools-passwords",
    "kali-tools-post-exploitation",
    "kali-tools-protect",
    "kali-tools-recover",
    "kali-tools-reporting",
    "kali-tools-respond",
    "kali-tools-reverse-engineering",
    "kali-tools-rfid",
    "kali-tools-sdr",
    "kali-tools-sniffing-spoofing",
    "kali-tools-social-engineering",
    "kali-tools-top10",
    "kali-tools-voip",
    "kali-tools-vulnerability",
    "kali-tools-web",
    "kali-tools-windows-resources",
]

class TestCase:
    def __init__(self, func: Callable, tier: int, feature: str, name: str, description: str):
        self.func = func
        self.tier = tier
        self.feature = feature.upper()
        self.name = name
        self.description = description

class TestRegistry:
    _tests: List[TestCase] = []

    @classmethod
    def register(cls, tier: int, feature: str, name: str, description: str):
        def decorator(func: Callable):
            cls._tests.append(TestCase(func, tier, feature, name, description))
            return func
        return decorator

    @classmethod
    def get_tests(cls, tier: Optional[int] = None, feature: Optional[str] = None) -> List[TestCase]:
        res = []
        for test in cls._tests:
            if tier is not None and test.tier != tier:
                continue
            if feature is not None and feature.upper() != "ALL" and test.feature != feature.upper():
                continue
            res.append(test)
        return res

test_case = TestRegistry.register

def run_cmd(cmd: str, timeout: int = 30) -> Tuple[int, str, str, float]:
    """Execute a shell command and return (returncode, stdout, stderr, elapsed_seconds)."""
    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        elapsed = time.time() - start
        return proc.returncode, proc.stdout, proc.stderr, elapsed
    except subprocess.TimeoutExpired as te:
        elapsed = time.time() - start
        stdout = te.stdout or "" if isinstance(te.stdout, str) else (te.stdout.decode() if te.stdout else "")
        stderr = te.stderr or "" if isinstance(te.stderr, str) else (te.stderr.decode() if te.stderr else "")
        return 124, stdout, f"Timeout ({timeout}s): {stderr}", elapsed

def assert_true(condition: bool, message: str = ""):
    if not condition:
        raise AssertionError(message or "Assertion failed: expected True but got False")

def assert_equal(actual: Any, expected: Any, message: str = ""):
    if actual != expected:
        raise AssertionError(message or f"Assertion failed: expected {expected!r}, got {actual!r}")

def assert_in(member: Any, container: Any, message: str = ""):
    if member not in container:
        raise AssertionError(message or f"Assertion failed: {member!r} not found in container")

def assert_not_in(member: Any, container: Any, message: str = ""):
    if member in container:
        raise AssertionError(message or f"Assertion failed: {member!r} unexpectedly found in container")
