import os
import sys
from pathlib import Path

from core.paths import AGENTS_DIR
from core.paths import BASE_DIR as PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


def get_health() -> dict:
    return {"status": "ok"}


def get_system_status() -> dict:
    db_path = PROJECT_ROOT / "data" / "finance.db"
    db_ok = Path(db_path).exists()

    agents_dir = AGENTS_DIR
    agents = [d for d in os.listdir(agents_dir) if (agents_dir / d).is_dir()] if agents_dir.exists() else []

    return {
        "database": "connected" if db_ok else "disconnected",
        "runtime": "active",
        "audit": "enabled",
        "number_of_agents": len(agents),
        "number_of_policies": len(agents),
        "overall_status": "healthy" if db_ok else "degraded",
    }


def get_system_version() -> dict:
    return {
        "api_version": "1.0.0",
        "application_version": "1.0.0",
        "supported_langchain_version": ">=0.1.0",
        "build_timestamp": "2026-07-30T00:00:00Z",
    }


def get_metrics() -> dict:
    return {"uptime_seconds": 3600, "requests_served": 42}
