#!/usr/bin/env python3
"""
Test runner script for IBM Cloud agents.
Provides convenient way to run different test suites.
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=False, capture_output=False)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def run_unit_tests():
    """Run unit tests."""
    return run_command(
        "python -m pytest tests/unit/ -v --tb=short",
        "Running unit tests"
    )


def run_integration_tests():
    """Run integration tests."""
    return run_command(
        "python -m pytest tests/integration/ -v --tb=short -m 'not slow'",
        "Running integration tests (fast)"
    )


def run_slow_tests():
    """Run slow integration tests."""
    return run_command(
        "python -m pytest tests/integration/ -v --tb=short -m 'slow'",
        "Running slow integration tests"
    )


def run_all_tests():
    """Run all tests."""
    return run_command(
        "python -m pytest tests/ -v --tb=short",
        "Running all tests"
    )


def run_coverage():
    """Run tests with coverage."""
    return run_command(
        "python -m pytest tests/ --cov=src --cov-report=term --cov-report=html:tests/htmlcov",
        "Running tests with coverage"
    )


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Test runner for IBM Cloud agents")
    parser.add_argument(
        "test_type", 
        choices=["unit", "integration", "slow", "all", "coverage"],
        nargs="?",
        default="unit",
        help="Type of tests to run (default: unit)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    print("🚀 IBM Cloud Agents Test Runner")
    print(f"Running: {args.test_type} tests")
    
    success = False
    
    if args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "slow":
        success = run_slow_tests()
    elif args.test_type == "all":
        success = run_all_tests()
    elif args.test_type == "coverage":
        success = run_coverage()
    
    if success:
        print(f"\n🎉 {args.test_type.upper()} TESTS COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print(f"\n💥 {args.test_type.upper()} TESTS FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()