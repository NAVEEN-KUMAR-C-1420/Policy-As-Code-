import os
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
