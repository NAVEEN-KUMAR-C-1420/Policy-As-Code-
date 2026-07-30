"""
Test Configuration (conftest.py)
=================================
Central test configuration for the entire test suite.

This file handles:
  - PYTHONPATH setup (also configured in pyproject.toml)
  - Database initialization for tests (SQLite)
  - Dummy API keys for modules that import LLM-related code
  - FastAPI TestClient fixture
"""

import os
import sys

import pytest

# ── Environment setup for CI ─────────────────────────────────────
# Force SQLite for testing (no external DB dependency)
os.environ.setdefault("DATABASE_PROVIDER", "sqlite")

# Provide dummy API keys so modules that import LLM loaders
# don't crash at import time. These are never used for real API calls.
os.environ.setdefault("GROQ_API_KEY", "test_dummy_key")
os.environ.setdefault("TAVILY_API_KEY", "test_dummy_key")
os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")

# Auto-approve HITL for automated testing
os.environ.setdefault("AUTO_APPROVE_HITL", "1")

# ── Path setup ───────────────────────────────────────────────────
# pyproject.toml sets pythonpath=["."] which handles most cases.
# This explicit insert ensures it works even when running pytest
# from non-standard locations.
from core.paths import BASE_DIR as PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ── Database initialization (once per session) ──────────────────
@pytest.fixture(scope="session", autouse=True)
def _init_test_database():
    """Initialize the SQLite test database before any tests run."""
    from data.init_db import main as init_db

    init_db()
    yield
    # No teardown needed — SQLite DB is ephemeral on CI


# ── FastAPI TestClient ──────────────────────────────────────────
@pytest.fixture(scope="session")
def client():
    """Provide a FastAPI TestClient for API tests."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as c:
        yield c
