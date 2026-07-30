import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ensure project root is in python path
from core.paths import BASE_DIR as PROJECT_ROOT
sys.path.append(PROJECT_ROOT)

from api.main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
