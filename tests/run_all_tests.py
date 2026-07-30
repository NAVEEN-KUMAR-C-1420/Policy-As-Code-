import os
import sys
import subprocess
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_pytest_on_dir(test_dir: str, title: str) -> dict:
    print(f"\n{'-'*60}\n{title.upper()}\n{'-'*60}")
    start = time.time()
    
    # We will generate JUnit XML reports for each directory
    report_path = os.path.join(PROJECT_ROOT, "tests", "reports", f"{title.lower().replace(' ', '_')}.xml")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    cmd = [
        sys.executable, "-m", "pytest",
        os.path.join(PROJECT_ROOT, test_dir),
        f"--junitxml={report_path}",
        "-v"
    ]
    
    # We don't want to crash on failure, we want to collect the result
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=PROJECT_ROOT)
    
    stdout, _ = process.communicate()
    print(stdout)
    
    duration = time.time() - start
    
    passed = stdout.count("PASSED")
    failed = stdout.count("FAILED")
    skipped = stdout.count("SKIPPED")
    
    if "no tests ran" in stdout:
        status = "NO TESTS"
    else:
        status = "PASS" if process.returncode == 0 else "FAIL"
        
    print(f"\nStatus: {status} | Passed: {passed} | Failed: {failed} | Skipped: {skipped} | Duration: {duration:.2f}s")
    
    return {
        "title": title,
        "status": status,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "duration": duration
    }

def main():
    print("="*60)
    print(" UNIFIED ENTERPRISE TESTING FRAMEWORK")
    print("="*60)
    
    # Pre-flight checks
    print("\n[*] Running: Compile Check")
    compile_cmd = [sys.executable, "-m", "compileall", PROJECT_ROOT]
    subprocess.run(compile_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("    [OK] Compile Check passed.")
    
    # Execute Test Suites
    results = []
    
    # Run tests that actually exist. We will just scan the tests/ directory.
    # Currently populated: api, unit
    # Others: integration, e2e, security, performance
    test_dirs = {
        "tests/unit": "Unit Tests",
        "tests/api": "API Tests",
        "tests/integration": "Integration Tests",
        "tests/e2e": "End-to-End Tests",
        "tests/security": "Security Tests",
        "tests/performance": "Performance Tests"
    }
    
    for rel_dir, title in test_dirs.items():
        full_dir = os.path.join(PROJECT_ROOT, rel_dir)
        if os.path.exists(full_dir):
            has_tests = False
            for root, _, files in os.walk(full_dir):
                if any(f.startswith("test_") and f.endswith(".py") for f in files):
                    has_tests = True
                    break
            if has_tests:
                results.append(run_pytest_on_dir(rel_dir, title))
            else:
                print(f"\n{'-'*60}\n{title.upper()}\n{'-'*60}\nNo tests discovered in {rel_dir}.")
    
    # Final Summary
    print("\n" + "="*60)
    print(" TEST EXECUTION SUMMARY")
    print("="*60)
    
    total_passed = sum(r["passed"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    total_skipped = sum(r["skipped"] for r in results)
    total_duration = sum(r["duration"] for r in results)
    
    overall_status = "PASS" if total_failed == 0 else "FAIL"
    
    for r in results:
        print(f"{r['title']:<20} | {r['status']:<10} | Passed: {r['passed']:<4} | Failed: {r['failed']:<4} | {r['duration']:>5.2f}s")
        
    print("-" * 60)
    print(f"OVERALL STATUS:       {overall_status}")
    print(f"Total Tests Executed: {total_passed + total_failed}")
    print(f"Total Passed:         {total_passed}")
    print(f"Total Failed:         {total_failed}")
    print(f"Total Skipped:        {total_skipped}")
    print(f"Total Duration:       {total_duration:.2f}s")
    print("="*60)
    
    sys.exit(0 if overall_status == "PASS" else 1)

if __name__ == "__main__":
    main()
