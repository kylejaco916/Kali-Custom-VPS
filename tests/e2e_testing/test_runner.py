#!/usr/bin/env python3
"""
Master E2E Test Runner for 28 kali-tools-* Metapackage Suite Deployment & Verification.
Supports filtering by Tier (--tier <1|2|3|4|all>) and Feature (--feature <R1|R2|R3|all>).
"""

import sys
import os
import argparse
import time
import json
import traceback

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from common import TestRegistry, TestCase
import tier1_coverage
import tier2_boundary
import tier3_combinations
import tier4_scenarios

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def parse_args():
    parser = argparse.ArgumentParser(
        description="E2E Test Runner for 28 kali-tools-* Metapackage Deployment"
    )
    parser.add_argument(
        "--tier",
        type=str,
        default="all",
        choices=["1", "2", "3", "4", "all"],
        help="Test tier to run (1: Coverage, 2: Boundary, 3: Combinations, 4: Scenarios, all: All tiers)"
    )
    parser.add_argument(
        "--feature",
        type=str,
        default="all",
        choices=["R1", "R2", "R3", "all", "r1", "r2", "r3", "ALL"],
        help="Feature scope to run (R1, R2, R3, or all)"
    )
    parser.add_argument(
        "--json",
        type=str,
        dest="json_output",
        default=None,
        help="Path to write JSON test results"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    tier_filter = None
    if args.tier.lower() != "all":
        tier_filter = int(args.tier)
        
    feature_filter = args.feature.upper()
    
    # Retrieve matching tests
    all_registered = TestRegistry._tests
    selected_tests = []
    for test in all_registered:
        if tier_filter is not None and test.tier != tier_filter:
            continue
        if feature_filter != "ALL":
            if test.feature != feature_filter:
                continue
        selected_tests.append(test)
        
    print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}  E2E Test Suite: 28 kali-tools-* Deployment & System Verification{RESET}")
    print(f"{BOLD}{CYAN}======================================================================{RESET}")
    print(f"Filter Configuration:")
    print(f"  • Tier    : {args.tier.upper()}")
    print(f"  • Feature : {feature_filter}")
    print(f"  • Tests   : {len(selected_tests)} selected (out of {len(all_registered)} total)")
    print(f"{BOLD}{CYAN}----------------------------------------------------------------------{RESET}")

    if not selected_tests:
        print(f"{YELLOW}No tests matched the specified filter criteria.{RESET}")
        sys.exit(0)

    passed_count = 0
    failed_count = 0
    results_summary = []
    overall_start = time.time()

    for idx, test in enumerate(selected_tests, 1):
        tier_label = f"T{test.tier}"
        feat_label = f"{test.feature}"
        test_id = f"[{tier_label}:{feat_label}] {test.name}"
        
        sys.stdout.write(f"  [{idx:2d}/{len(selected_tests):2d}] {test_id:<48} ")
        sys.stdout.flush()

        test_start = time.time()
        status = "PASS"
        error_msg = ""
        error_trace = ""
        
        try:
            test.func()
            duration = time.time() - test_start
            passed_count += 1
            print(f"{GREEN}[PASS]{RESET} ({duration:.2f}s)")
        except AssertionError as ae:
            duration = time.time() - test_start
            failed_count += 1
            status = "FAIL"
            error_msg = str(ae)
            error_trace = traceback.format_exc()
            print(f"{RED}[FAIL]{RESET} ({duration:.2f}s)")
            if args.verbose:
                print(f"      {RED}AssertionError: {error_msg}{RESET}")
        except Exception as e:
            duration = time.time() - test_start
            failed_count += 1
            status = "ERROR"
            error_msg = f"{type(e).__name__}: {str(e)}"
            error_trace = traceback.format_exc()
            print(f"{RED}[ERROR]{RESET} ({duration:.2f}s)")
            if args.verbose:
                print(f"      {RED}Exception: {error_msg}{RESET}")

        results_summary.append({
            "name": test.name,
            "tier": test.tier,
            "feature": test.feature,
            "description": test.description,
            "status": status,
            "duration": round(duration, 4),
            "error": error_msg,
            "traceback": error_trace if status != "PASS" else None
        })

    total_duration = time.time() - overall_start

    print(f"{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}Execution Summary:{RESET}")
    print(f"  • Total Executed : {len(selected_tests)}")
    print(f"  • Passed         : {GREEN}{passed_count}{RESET}")
    print(f"  • Failed         : {RED if failed_count > 0 else GREEN}{failed_count}{RESET}")
    print(f"  • Total Duration : {total_duration:.2f}s")
    print(f"{BOLD}{CYAN}======================================================================{RESET}")

    # Output detailed failures if any
    if failed_count > 0:
        print(f"\n{BOLD}{RED}FAILED TESTS DETAIL:{RESET}")
        for item in results_summary:
            if item["status"] != "PASS":
                print(f"\n{BOLD}{RED}• [Tier {item['tier']} | {item['feature']}] {item['name']}:{RESET}")
                print(f"  Description: {item['description']}")
                print(f"  Error: {item['error']}")
                if item["traceback"]:
                    print(f"  Traceback:\n{item['traceback']}")

    # Write JSON output if requested
    if args.json_output:
        json_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tier_filter": args.tier,
            "feature_filter": feature_filter,
            "total": len(selected_tests),
            "passed": passed_count,
            "failed": failed_count,
            "duration_seconds": round(total_duration, 4),
            "tests": results_summary
        }
        with open(args.json_output, "w") as jf:
            json.dump(json_data, jf, indent=2)
        print(f"\nJSON results written to {args.json_output}")

    if failed_count == 0:
        print(f"\n{BOLD}{GREEN}✓ ALL TESTS PASSED SUCCESSFULLY.{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{BOLD}{RED}✗ TEST SUITE FAILED ({failed_count} failures).{RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
