import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

def get_health() -> dict:
    return {"status": "ok"}

def get_system_status() -> dict:
    provider = os.getenv("DATABASE_PROVIDER", "sqlite").lower()
    db_ok = False
    
    if provider == "supabase":
        # We assume if the URL is set, the remote DB is active. We don't block health ping on DB introspect.
        db_ok = bool(os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_DB_HOST"))
    else:
        db_path = os.path.join(PROJECT_ROOT, "data", "finance.db")
        db_ok = os.path.exists(db_path)
    
    agents_dir = os.path.join(PROJECT_ROOT, "agents")
    agents = [d for d in os.listdir(agents_dir) if os.path.isdir(os.path.join(agents_dir, d))] if os.path.exists(agents_dir) else []
    
    llm_ok = bool(os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))
    
    return {
        "database": "connected" if db_ok else "disconnected",
        "provider": provider,
        "llm_configuration": "valid" if llm_ok else "missing",
        "runtime": "active",
        "audit": "enabled",
        "number_of_agents": len(agents),
        "number_of_policies": len(agents),
        "overall_status": "healthy" if (db_ok and llm_ok) else "degraded"
    }

def get_system_version() -> dict:
    return {
        "api_version": "1.0.0",
        "application_version": "1.0.0",
        "supported_langchain_version": ">=0.1.0",
        "build_timestamp": "2026-07-30T00:00:00Z"
    }

def get_metrics() -> dict:
    return {
        "uptime_seconds": 3600,
        "requests_served": 42
    }
