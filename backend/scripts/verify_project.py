"""
CI Verification Framework
===========================
This script validates the project structure, configuration integrity,
and environment setup. It is designed to run in both CI and local
development environments.

In CI, this runs AFTER pytest (as a final validation step).
Locally, it can be run standalone to check readiness:

    python scripts/verify_project.py

This script does NOT run tests (pytest handles that).
It does NOT initialize the database (conftest.py handles that).
"""

import os
import sqlite3
import sys
from pathlib import Path

# ── Determine project root ──────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

# Force UTF-8 output to avoid charmap UnicodeEncodeError on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add to path for imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title.upper()}")
    print(f"{'='*60}\n")


def verify_structure():
    """Verify all required directories and files exist."""
    print_header("Verifying Project Structure")
    errors = []

    # Required directories
    required_dirs = [
        "agents",
        "api",
        "common",
        "config",
        "core",
        "data",
        "middleware",
        "orchestrator",
        "scripts",
        "tests",
        "agents/data_collector_agent",
        "agents/risk_analyzer_agent",
        "agents/report_writer_agent",
    ]
    for d in required_dirs:
        if not (PROJECT_ROOT / d).is_dir():
            errors.append(f"Missing directory: {d}/")
        else:
            print(f"    [OK] {d}/")

    # Required files
    required_files = [
        "requirements.txt",
        "pyproject.toml",
        ".env.example",
        "config/providers.yaml",
        "core/paths.py",
        "core/__init__.py",
        "api/main.py",
        "data/init_db.py",
        "tests/conftest.py",
        "tests/run_all_tests.py",
        "scripts/verify_project.py",
    ]
    for f in required_files:
        if not (PROJECT_ROOT / f).is_file():
            errors.append(f"Missing file: {f}")
        else:
            print(f"    [OK] {f}")

    # Agent structure
    for agent in ["data_collector_agent", "risk_analyzer_agent", "report_writer_agent"]:
        for required in ["agent.yaml", "policy.yaml"]:
            path = PROJECT_ROOT / "agents" / agent / required
            if not path.is_file():
                errors.append(f"Missing: agents/{agent}/{required}")

    if errors:
        for e in errors:
            print(f"    [FAIL] {e}")
        return False

    print(f"\n    [OK] All {len(required_dirs) + len(required_files)} items verified.")
    return True


def verify_cleanliness():
    """Check for security issues in the repository."""
    print_header("Verifying Repository Cleanliness")
    failed = False

    # Check for .env (should not be committed)
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        try:
            import subprocess

            res = subprocess.run(
                ["git", "ls-files", "--error-unmatch", ".env"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(PROJECT_ROOT),
            )
            if res.returncode == 0:
                print("    [FAIL] .env file is tracked by git! It must NEVER be committed.")
                failed = True
            else:
                print("    [OK] .env exists locally but is safely ignored by git.")
        except Exception:
            print("    [WARN] Could not verify git tracking status for .env")
    else:
        print("    [OK] .env is safely excluded.")

    # Check for .env.example
    if not (PROJECT_ROOT / ".env.example").exists():
        print("    [FAIL] .env.example is missing.")
        failed = True
    else:
        print("    [OK] .env.example is present.")

    return not failed


def verify_policies():
    """Validate that all agent policy YAML files are parseable."""
    print_header("Verifying Agent Policies")

    try:
        import yaml
    except ImportError:
        print("    [WARN] pyyaml not installed, skipping policy validation.")
        return True

    agents = ["data_collector_agent", "risk_analyzer_agent", "report_writer_agent"]
    all_valid = True

    for agent in agents:
        policy_path = PROJECT_ROOT / "agents" / agent / "policy.yaml"
        agent_path = PROJECT_ROOT / "agents" / agent / "agent.yaml"

        for fpath, label in [(policy_path, "policy.yaml"), (agent_path, "agent.yaml")]:
            if fpath.exists():
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                    if not isinstance(data, dict):
                        print(f"    [FAIL] {agent}/{label}: not a valid YAML dictionary")
                        all_valid = False
                    else:
                        print(f"    [OK] {agent}/{label} is valid YAML")
                except yaml.YAMLError as e:
                    print(f"    [FAIL] {agent}/{label}: YAML parse error: {e}")
                    all_valid = False
            else:
                print(f"    [FAIL] {agent}/{label}: file not found")
                all_valid = False

    return all_valid


def verify_imports():
    """Verify critical imports resolve correctly."""
    print_header("Verifying Critical Imports")
    errors = []

    imports_to_check = [
        ("core.paths", "BASE_DIR"),
        ("common.db", "PROVIDER"),
        ("middleware.policy_loader", "load_policy"),
        ("middleware.policy_validator", "validate_policy"),
        ("middleware.audit_log", "write_audit_entry"),
        ("api.main", "app"),
    ]

    for module, attr in imports_to_check:
        try:
            mod = __import__(module, fromlist=[attr])
            getattr(mod, attr)
            print(f"    [OK] from {module} import {attr}")
        except Exception as e:
            print(f"    [FAIL] from {module} import {attr}: {e}")
            errors.append(f"{module}.{attr}: {e}")

    return len(errors) == 0


def verify_database():
    """Verify the test database can be initialized."""
    print_header("Verifying Database")

    provider = os.getenv("DATABASE_PROVIDER", "sqlite").lower()
    print(f"    [*] Provider: {provider}")

    if provider != "sqlite":
        print("    [OK] Non-SQLite provider — skipping local DB check.")
        return True

    try:
        from data.init_db import main as init_db

        init_db()
        print("    [OK] Database initialized successfully.")
    except Exception as e:
        print(f"    [FAIL] Database initialization failed: {e}")
        return False

    db_path = PROJECT_ROOT / "data" / "finance.db"
    if not db_path.exists():
        print(f"    [FAIL] Database file not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = ["accounts", "transactions", "reports", "policy_versions"]
        missing = [t for t in required_tables if t not in tables]
        if missing:
            print(f"    [FAIL] Missing tables: {missing}")
            conn.close()
            return False

        print(f"    [OK] All required tables exist: {required_tables}")
        conn.close()
    except Exception as e:
        print(f"    [FAIL] Database verification failed: {e}")
        return False

    return True


def main():
    print_header("CI VERIFICATION FRAMEWORK")
    print("This script validates project structure and configuration.")
    print("It mirrors CI checks to guarantee production readiness.\n")

    checks = [
        ("Project Structure", verify_structure),
        ("Repository Cleanliness", verify_cleanliness),
        ("Agent Policies", verify_policies),
        ("Critical Imports", verify_imports),
        ("Database", verify_database),
    ]

    failed_checks = []
    for name, check_fn in checks:
        try:
            if not check_fn():
                failed_checks.append(name)
        except Exception as e:
            print(f"\n    [FAIL] {name} check raised an exception: {e}")
            failed_checks.append(name)

    if failed_checks:
        print_header("VERIFICATION FAILED")
        print(f"Failed checks: {', '.join(failed_checks)}")
        print("\nRecommended actions:")
        print("  1. Review the errors above")
        print("  2. Ensure you have activated your virtual environment")
        print("  3. Run: pip install -r requirements.txt")
        print("  4. Check that DATABASE_PROVIDER is set correctly")
        sys.exit(1)
    else:
        print_header("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
        sys.exit(0)


if __name__ == "__main__":
    main()
