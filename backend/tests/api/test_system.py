def test_system_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "status" in data["data"]


def test_system_metrics(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_system_versions(client):
    response = client.get("/system/version")
    assert response.status_code == 200
    assert response.json()["success"] is True
