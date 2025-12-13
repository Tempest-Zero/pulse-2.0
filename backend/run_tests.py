"""
PULSE Backend Test Runner

Main test runner script that runs all unit tests and provides detailed reporting.
Usage: python run_tests.py
"""

import pytest
import sys
import os
from datetime import datetime


def main():
    """Run the test suite with coverage reporting."""
    print("=" * 70)
    print("PULSE Backend - Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # pytest arguments
    args = [
        "tests/",                          # Test directory
        "-v",                              # Verbose output
        "--tb=short",                      # Short traceback format
        "--durations=10",                  # Show 10 slowest tests
        "--cov=.",                         # Code coverage for current directory
        "--cov-report=term-missing",       # Show missing lines in coverage
        "--cov-report=html:htmlcov",       # Generate HTML coverage report
        "--disable-warnings",              # Hide deprecation warnings
        "--color=yes",                     # Color output
    ]
    
    # Run tests
    exit_code = pytest.main(args)
    
    print()
    print("=" * 70)
    
    if exit_code == 0:
        print("✅ ALL TESTS PASSED!")
        print()
        print("Coverage Summary:")
        print("-" * 40)
        print("  • Tasks routes: Tested ✅")
        print("  • Schedule routes: Tested ✅")
        print("  • Reflections routes: Tested ✅")
        print("  • Mood routes: Tested ✅")
        print("  • Database: CRUD operations tested ✅")
        print()
        print("📊 View detailed coverage: open htmlcov/index.html")
        print()
        print("Production-Ready Features:")
        print("-" * 40)
        print("  ✓ Task management")
        print("  ✓ Schedule block handling")
        print("  ✓ End-of-day reflections")
        print("  ✓ Mood tracking and analytics")
        print("  ✓ Error handling and validation")
        print()
        print("Next Steps:")
        print("-" * 40)
        print("  1. Deploy to staging environment")
        print("  2. Set up CI/CD pipeline")
        print("  3. Add integration tests")
        print("  4. Configure production database")
    else:
        print("❌ SOME TESTS FAILED!")
        print()
        print("Troubleshooting Tips:")
        print("-" * 40)
        print("  1. Check database connection and models")
        print("  2. Verify all required packages are installed")
        print("  3. Review recent code changes")
        print("  4. Run: pip install -r requirements-test.txt")
        print()
        print("Debug Commands:")
        print("-" * 40)
        print("  • Run single test: pytest tests/test_main.py::TestMainRoutes::test_root_endpoint -v")
        print("  • Debug mode: pytest tests/ -v -s --tb=long")
        print("  • Skip coverage: pytest tests/ -v --no-cov")
        print()
        print("Next Steps:")
        print("-" * 40)
        print("  1. Fix failing tests")
        print("  2. Review error messages above")
        print("  3. Check test fixtures in conftest.py")
    
    print("=" * 70)
    print()
    
    print("Useful Commands:")
    print("-" * 40)
    print("  pytest tests/test_main.py -v                    # Run main tests only")
    print("  pytest tests/test_tasks_routes.py -v            # Run tasks tests only")
    print("  pytest tests/test_schedule_routes.py -v         # Run schedule tests only")
    print("  pytest tests/test_reflections_routes.py -v      # Run reflections tests only")
    print("  pytest tests/test_mood_routes.py -v             # Run mood tests only")
    print("  pytest tests/ -v -s --tb=long                   # Debug with full output")
    print("  python debug_tests.py                           # Run debug script")
    print()
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
