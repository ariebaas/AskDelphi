#!/usr/bin/env python3
"""Master test script that runs all client tests.

This script executes all test suites and provides a comprehensive summary:
- test_auth.py: Authentication and token caching tests
- test_end_to_end.py: End-to-end integration tests with mockserver
- test_sanering_import.py: Sanering process import tests
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class TestRunner:
    """Runs all test suites and tracks results."""

    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None

    def run_test_suite(self, test_file: str, description: str) -> bool:
        """Run a single test suite and return success status."""
        print(f"\n{'='*70}")
        print(f"Running: {description}")
        print(f"File: {test_file}")
        print(f"{'='*70}")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                cwd=str(Path(__file__).parent),
                capture_output=False,
                timeout=300
            )
            success = result.returncode == 0
            self.results[description] = {
                "file": test_file,
                "success": success,
                "return_code": result.returncode
            }
            return success
        except subprocess.TimeoutExpired:
            print(f"❌ TIMEOUT: {description} took too long (>5 minutes)")
            self.results[description] = {
                "file": test_file,
                "success": False,
                "return_code": -1
            }
            return False
        except Exception as e:
            print(f"❌ ERROR: {description} failed with exception: {e}")
            self.results[description] = {
                "file": test_file,
                "success": False,
                "return_code": -1
            }
            return False

    def run_all(self):
        """Run all test suites."""
        self.start_time = datetime.now()

        tests = [
            ("tests/test_auth.py", "Authentication Tests"),
            ("tests/test_end_to_end.py", "End-to-End Integration Tests"),
            ("tests/test_sanering_import.py", "Sanering Import Tests"),
        ]

        for test_file, description in tests:
            self.run_test_suite(test_file, description)
            time.sleep(0.5)  # Brief pause between test suites

        self.end_time = datetime.now()

    def print_summary(self):
        """Print comprehensive test summary."""
        print(f"\n{'='*70}")
        print("TEST SUMMARY")
        print(f"{'='*70}")

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["success"])
        failed_tests = total_tests - passed_tests

        for description, result in self.results.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            print(f"{status}: {description}")

        print(f"\n{'='*70}")
        print(f"Results: {passed_tests}/{total_tests} test suites passed")
        print(f"Duration: {self.end_time - self.start_time}")
        print(f"{'='*70}\n")

        if failed_tests > 0:
            print(f"⚠️  {failed_tests} test suite(s) failed")
            return False
        else:
            print("✅ All test suites passed!")
            return True


def main():
    """Main entry point."""
    print(f"\n{'='*70}")
    print("DIGITALECOACH CLIENT - MASTER TEST RUNNER")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    runner = TestRunner()
    runner.run_all()
    success = runner.print_summary()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
