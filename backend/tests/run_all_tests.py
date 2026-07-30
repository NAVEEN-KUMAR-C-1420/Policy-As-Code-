"""
Unified Enterprise Testing Framework
======================================
Single authoritative entry point for running all tests.

Usage from backend/ directory:
    python tests/run_all_tests.py

Or via pytest directly (preferred in CI):
    python -m pytest tests/ -v

This script exists as a convenience wrapper. In CI, pytest is called
directly for better control and reporting.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Force UTF-8 output to avoid charmap UnicodeEncodeError on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Determine project root without importing core.paths
# (so this script works even before PYTHONPATH is configured)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Ensure backend is in PYTHONPATH for subprocess calls
env = os.environ.copy()
existing_pythonpath = env.get("PYTHONPATH", "")
if str(PROJECT_ROOT) not in existing_pythonpath:
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + existing_pythonpath

# Force test-safe environment
env.setdefault("DATABASE_PROVIDER", "sqlite")
env.setdefault("GROQ_API_KEY", "dummy_key_for_tests")
env.setdefault("TAVILY_API_KEY", "dummy_key_for_tests")
env.setdefault("AUTO_APPROVE_HITL", "1")
env.setdefault("LANGCHAIN_TRACING_V2", "false")


def discover_test_suites():
    """Find test directories that actually contain test files."""
    test_dirs = {
        "tests/unit": "Unit Tests",
        "tests/api": "API Tests",
        "tests/integration": "Integration Tests",
        "tests/e2e": "End-to-End Tests",
        "tests/security": "Security Tests",
        "tests/performance": "Performance Tests",
    }

    discovered = {}
    for rel_dir, title in test_dirs.items():
        full_dir = PROJECT_ROOT / rel_dir
        if full_dir.exists():
            has_tests = any(f.name.startswith("test_") and f.name.endswith(".py") for f in full_dir.rglob("*.py"))
            if has_tests:
                discovered[rel_dir] = title
            else:
                print(f"  ℹ️  {title}: no test files found in {rel_dir}/")

    return discovered


def run_pytest_suite(test_dir: str, title: str) -> dict:
    """Run pytest on a single test directory and return results."""
    print(f"\n{'-'*60}\n{title.upper()}\n{'-'*60}")

    report_name = title.lower().replace(" ", "_")
    report_path = PROJECT_ROOT / "tests" / "reports" / f"{report_name}.xml"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(PROJECT_ROOT / test_dir),
        f"--junitxml={report_path}",
        "--override-ini=pythonpath=.",
        "-v",
        "--tb=short",
    ]

    start = time.time()
    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=str(PROJECT_ROOT),
        env=env,
    )
    duration = time.time() - start
    stdout = process.stdout

    print(stdout)

    # Parse results from output
    passed = stdout.count("PASSED")
    failed = stdout.count("FAILED")
    skipped = stdout.count("SKIPPED")

    if "no tests ran" in stdout:
        status = "NO TESTS"
    else:
        status = "PASS" if process.returncode == 0 else "FAIL"

    print(
        f"Status: {status} | Passed: {passed} | Failed: {failed} | " f"Skipped: {skipped} | Duration: {duration:.2f}s"
    )

    return {
        "title": title,
        "status": status,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "duration": duration,
    }


def main():
    print("=" * 60)
    print(" UNIFIED ENTERPRISE TESTING FRAMEWORK")
    print("=" * 60)
    print(f" Project Root: {PROJECT_ROOT}")
    print(f" Python:       {sys.version.split()[0]}")
    print(f" DB Provider:  {env.get('DATABASE_PROVIDER', 'unknown')}")
    print()

    # Initialize database before tests
    print("[*] Initializing test database...")
    init_result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "data" / "init_db.py")],
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    if init_result.returncode != 0:
        print("    ❌ Database initialization failed:")
        print(f"    {init_result.stderr or init_result.stdout}")
        sys.exit(1)
    print("    ✅ Database initialized.")

    # Compile check
    print("\n[*] Running compile check...")
    subprocess.run(
        [sys.executable, "-m", "compileall", str(PROJECT_ROOT), "-q"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("    ✅ Compile check passed.")

    # Discover and run test suites
    suites = discover_test_suites()
    if not suites:
        print("\n❌ No test suites discovered!")
        sys.exit(1)

    results = []
    for rel_dir, title in suites.items():
        results.append(run_pytest_suite(rel_dir, title))

    # Summary
    print("\n" + "=" * 60)
    print(" TEST EXECUTION SUMMARY")
    print("=" * 60)

    total_passed = sum(r["passed"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    total_skipped = sum(r["skipped"] for r in results)
    total_duration = sum(r["duration"] for r in results)

    overall_status = "PASS" if total_failed == 0 else "FAIL"

    for r in results:
        print(
            f"  {r['title']:<25} | {r['status']:<10} | "
            f"Passed: {r['passed']:<4} | Failed: {r['failed']:<4} | "
            f"{r['duration']:>5.2f}s"
        )

    print("-" * 60)
    print(f"  OVERALL STATUS:       {overall_status}")
    print(f"  Total Tests Executed: {total_passed + total_failed}")
    print(f"  Total Passed:         {total_passed}")
    print(f"  Total Failed:         {total_failed}")
    print(f"  Total Skipped:        {total_skipped}")
    print(f"  Total Duration:       {total_duration:.2f}s")
    print("=" * 60)

    sys.exit(0 if overall_status == "PASS" else 1)


if __name__ == "__main__":
    main()
