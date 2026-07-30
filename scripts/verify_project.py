import os
import sys
import subprocess
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Ensure we are running from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

load_dotenv()

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title.upper()}")
    print(f"{'='*60}\n")

def run_step(name, cmd_list, env=None, check=True):
    print(f"[*] Running: {name}")
    try:
        env_vars = os.environ.copy()
        if env:
            env_vars.update(env)
        
        result = subprocess.run(
            cmd_list,
            shell=False,
            env=env_vars,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        print(f"    [OK] {name} passed.")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"    [FAIL] {name} failed with exit code {e.returncode}.")
        print("--- Output ---")
        print(e.stdout)
        print("--------------")
        return False, e.stdout

def verify_cleanliness():
    print_header("Verifying Repository Cleanliness")
    failed = False

    # Check for .env
    if (PROJECT_ROOT / ".env").exists():
        try:
            res = subprocess.run(["git", "ls-files", "--error-unmatch", ".env"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0:
                print("    [FAIL] .env file is tracked by git! It must NEVER be committed.")
                failed = True
            else:
                print("    [OK] .env exists locally but is safely ignored by git.")
        except Exception:
            pass
    else:
        print("    [OK] .env is safely excluded.")

    # Check for .env.example
    if not (PROJECT_ROOT / ".env.example").exists():
        print("    [FAIL] .env.example is missing.")
        failed = True
    else:
        print("    [OK] .env.example is present.")

    if failed:
        return False
    return True

def verify_database():
    print_header("Verifying Database")
    
    provider = os.getenv("DATABASE_PROVIDER", "sqlite").lower()
    if provider not in ["sqlite", "supabase"]:
        print(f"    [FAIL] Invalid DATABASE_PROVIDER '{provider}'. Must be 'sqlite' or 'supabase'.")
        return False
        
    print(f"    [*] Provider: {provider}")
    
    # Initialize Test Database
    success, _ = run_step(
        "Initialize Database Schema", 
        [sys.executable, "data/init_db.py"],
        env={"DATABASE_PROVIDER": provider}
    )
    if not success:
        return False

    if provider == "sqlite":
        db_path = PROJECT_ROOT / "data" / "finance.db"
        if not db_path.exists():
            print(f"    [FAIL] SQLite database {db_path} not found after initialization.")
            return False
        
        print("    [OK] Database file created.")

        # Check required tables
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ["accounts", "transactions", "reports", "policy_versions"]
            for table in required_tables:
                if table not in tables:
                    print(f"    [FAIL] Required table '{table}' is missing.")
                    return False
            
            print("    [OK] All required tables exist in SQLite.")
        except Exception as e:
            print(f"    [FAIL] Database inspection failed: {e}")
            return False
        finally:
            conn.close()
    elif provider == "supabase":
        print("    [OK] Assumed schema initialization succeeded for remote Supabase Postgres.")

    return True

def run_tests():
    print_header("Running Tests")
    
    provider = os.getenv("DATABASE_PROVIDER", "sqlite").lower()
    env_vars = {
        "DATABASE_PROVIDER": provider,
        "AUTO_APPROVE_HITL": "1", # Bypass HITL for automated testing
    }
    
    if not os.getenv("GROQ_API_KEY"):
        env_vars["GROQ_API_KEY"] = "dummy_key_for_tests"
    if not os.getenv("TAVILY_API_KEY"):
        env_vars["TAVILY_API_KEY"] = "dummy_key_for_tests"

    steps = [
        ("Compile Check", [sys.executable, "-m", "compileall", "."]),
        ("API Tests", [sys.executable, "-m", "pytest", "api_testing", "-v"]),
        ("Governance Tests", [sys.executable, "test_governance.py"]),
    ]
    
    # Only run pipeline if we have real API keys, otherwise it will fail with 401
    current_groq = os.getenv("GROQ_API_KEY", env_vars.get("GROQ_API_KEY"))
    if current_groq and current_groq != "dummy_key_for_tests":
        steps.append(("Pipeline Execution", [sys.executable, "orchestrator/run_pipeline.py"]))
    else:
        print("    [!] Skipping Pipeline Execution because no real GROQ_API_KEY was found.")

    for name, cmd_list in steps:
        success, _ = run_step(name, cmd_list, env=env_vars)
        if not success:
            print(f"\n[!] Verification halted due to failure in {name}.")
            print(f"[!] Recommended Fix: Review the logs above for {name}. Ensure you have activated your virtual environment and installed requirements.txt.")
            return False

    return True

def main():
    print_header("LOCAL CI VERIFICATION SUITE")
    print("This script mirrors GitHub Actions to guarantee production readiness.")
    print("Any failure here will also fail the CI/CD pipeline.\n")

    if not verify_cleanliness():
        sys.exit(1)
        
    if not verify_database():
        sys.exit(1)
        
    if not run_tests():
        sys.exit(1)

    print_header("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    sys.exit(0)

if __name__ == "__main__":
    main()
