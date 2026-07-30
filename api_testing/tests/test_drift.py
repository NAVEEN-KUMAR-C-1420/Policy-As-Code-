def test_detect_drift(client):
    response = client.get("/drift/detect")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_drift_history(client):
    response = client.get("/drift/history")
    assert response.status_code == 200
    assert response.json()["success"] is True
