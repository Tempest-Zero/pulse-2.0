"""
PULSE Backend Debug Test Runner

Debug script to run specific failing tests with detailed output.
Usage: python debug_tests.py
"""

import pytest
import sys
import os


def main():
    """Run a specific test with verbose debug output."""
    print("=" * 70)
    print("PULSE Backend - Debug Test Runner")
    print("=" * 70)
    print()
    
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Edit this to target specific failing test
    target_test = "tests/test_main.py"
    
    print(f"Running: {target_test}")
    print("-" * 70)
    print()
    
    # Debug arguments for maximum output
    args = [
        target_test,                       # Specific test to debug
        "-v",                              # Verbose
        "-s",                              # Don't capture output (show prints)
        "--tb=long",                       # Long traceback
        "--no-cov",                        # Disable coverage for cleaner output
    ]
    
    exit_code = pytest.main(args)
    
    print()
    print("=" * 70)
    
    if exit_code != 0:
        print("Debugging Steps:")
        print("-" * 40)
        print("  1. Check if fixtures create data correctly")
        print("  2. Verify database relationships are set up properly")
        print("  3. Review model fields match schema expectations")
        print("  4. Check if test database is being used (not production)")
        print("  5. Add print statements in conftest.py fixtures")
    else:
        print("✅ Test passed!")
    
    print("=" * 70)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
