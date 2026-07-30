import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ensure project root is in python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from api.main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
