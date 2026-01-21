#!/usr/bin/env python3
"""Master test script dat alle client tests uitvoert.

Dit script voert alle test suites uit en biedt een uitgebreide samenvatting:
- test_auth.py: Authenticatie en token caching tests
- test_end_to_end.py: End-to-end integratie tests met mockserver
- test_sanering_import.py: Sanering proces import tests
"""

import subprocess
import sys
import time
import json
import glob
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class TestRunner:
    """Voert alle test suites uit en volgt resultaten."""

    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.project_root = Path(__file__).parent.parent
        self.logs_dir = self.project_root / "log"
        self.logs_dir.mkdir(exist_ok=True)

    def cleanup_old_logs(self, keep_count: int = 3):
        """Behoud alleen de laatste N log bestanden en JSON outputs."""
        if not self.logs_dir.exists():
            return

        log_files = sorted(
            self.logs_dir.glob("*.log"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        json_files = sorted(
            self.logs_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for log_file in log_files[keep_count:]:
            try:
                log_file.unlink()
                print(f"🗑️  Verwijderd oud log: {log_file.name}")
            except Exception as e:
                print(f"⚠️  Kon {log_file.name} niet verwijderen: {e}")

        for json_file in json_files[keep_count:]:
            try:
                json_file.unlink()
                print(f"🗑️  Verwijderd oud JSON: {json_file.name}")
            except Exception as e:
                print(f"⚠️  Kon {json_file.name} niet verwijderen: {e}")

    def run_test_suite(self, test_file: str, description: str) -> bool:
        """Voer een enkele test suite uit en retourneer success status."""
        print(f"\n{'='*70}")
        print(f"Uitvoering: {description}")
        print(f"Bestand: {test_file}")
        print(f"{'='*70}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = Path(test_file).stem
        log_file = self.logs_dir / f"{test_name}_{timestamp}.log"
        json_file = self.logs_dir / f"{test_name}_{timestamp}.json"

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short",
                 f"--log-file={log_file}"],
                cwd=str(self.project_root),
                capture_output=False,
                timeout=300
            )
            success = result.returncode == 0

            self._create_json_report(test_name, description, success, result.returncode, json_file)

            self.results[description] = {
                "file": test_file,
                "success": success,
                "return_code": result.returncode,
                "log_file": str(log_file),
                "json_file": str(json_file)
            }
            return success
        except subprocess.TimeoutExpired:
            print(f"❌ TIMEOUT: {description} duurde te lang (>5 minuten)")
            self.results[description] = {
                "file": test_file,
                "success": False,
                "return_code": -1
            }
            return False
        except Exception as e:
            print(f"❌ FOUT: {description} mislukt met uitzondering: {e}")
            self.results[description] = {
                "file": test_file,
                "success": False,
                "return_code": -1
            }
            return False

    def _create_json_report(self, test_name: str, description: str, success: bool, return_code: int, json_file: Path):
        """Maak een JSON rapport voor de test suite."""
        report = {
            "test_name": test_name,
            "description": description,
            "success": success,
            "return_code": return_code,
            "timestamp": datetime.now().isoformat(),
            "log_file": str(self.logs_dir / f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        }
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Kon JSON rapport niet schrijven naar {json_file}: {e}")

    def run_all(self):
        """Voer alle test suites uit."""
        self.start_time = datetime.now()

        tests = [
            ("tests/test_auth.py", "Authenticatie Tests"),
            ("tests/test_end_to_end.py", "End-to-End Integratie Tests"),
            ("tests/test_sanering_import.py", "Sanering Import Tests"),
        ]

        for test_file, description in tests:
            self.run_test_suite(test_file, description)
            time.sleep(0.5)

        self.end_time = datetime.now()

    def print_summary(self):
        """Print uitgebreide test samenvatting."""
        print(f"\n{'='*70}")
        print("TEST SAMENVATTING")
        print(f"{'='*70}")

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r["success"])
        failed_tests = total_tests - passed_tests

        for description, result in self.results.items():
            status = "✅ GESLAAGD" if result["success"] else "❌ MISLUKT"
            print(f"{status}: {description}")

        print(f"\n{'='*70}")
        print(f"Resultaten: {passed_tests}/{total_tests} test suites geslaagd")
        print(f"Duur: {self.end_time - self.start_time}")
        print(f"{'='*70}\n")

        print("🧹 Oude log bestanden opschonen...")
        self.cleanup_old_logs(keep_count=3)

        if failed_tests > 0:
            print(f"⚠️  {failed_tests} test suite(s) mislukt")
            return False
        else:
            print("✅ Alle test suites geslaagd!")
            return True


def main():
    """Ingangspunt."""
    print(f"\n{'='*70}")
    print("DIGITALECOACH CLIENT - MASTER TEST RUNNER")
    print(f"Gestart: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")

    runner = TestRunner()
    runner.run_all()
    success = runner.print_summary()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
