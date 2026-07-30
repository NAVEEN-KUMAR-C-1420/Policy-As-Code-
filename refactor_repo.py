import os
import shutil
from pathlib import Path

def main():
    root_dir = Path(os.getcwd())
    backend_dir = root_dir / "backend"
    frontend_dir = root_dir / "frontend"
    core_dir = backend_dir / "core"

    # Create directories
    backend_dir.mkdir(exist_ok=True)
    frontend_dir.mkdir(exist_ok=True)
    core_dir.mkdir(exist_ok=True)

    # Files and dirs to move
    to_move = [
        "agents", "api", "common", "config", "data", "middleware", 
        "orchestrator", "scripts", "tests", "logs", "reports",
        "requirements.txt", "render.yaml", ".env.example", "README.md"
    ]

    for item in to_move:
        src = root_dir / item
        dst = backend_dir / item
        if src.exists() and not dst.exists():
            shutil.move(str(src), str(dst))
            print(f"Moved {item} to backend/")
        elif dst.exists():
            print(f"{item} already in backend/")
        else:
            print(f"{item} not found in root")

    # Create root README.md if it was moved
    root_readme = root_dir / "README.md"
    if not root_readme.exists():
        with open(root_readme, "w") as f:
            f.write("# AIVAR Project\n\nSee the `backend/` folder for documentation.\n")
        print("Created root README.md")
    
    # Create backend/core/paths.py
    paths_code = '''import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"
TEST_DIR = BASE_DIR / "tests"
SCRIPT_DIR = BASE_DIR / "scripts"
AGENTS_DIR = BASE_DIR / "agents"
MIDDLEWARE_DIR = BASE_DIR / "middleware"

# Ensure essential directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
'''
    paths_py = core_dir / "paths.py"
    with open(paths_py, "w") as f:
        f.write(paths_code)
    print("Created backend/core/paths.py")
    
    # Ensure __init__.py exists in core
    with open(core_dir / "__init__.py", "w") as f:
        pass
        
if __name__ == "__main__":
    main()
