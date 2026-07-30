def test_pipeline_run_validation(client):
    # Missing account_id
    response = client.post("/pipeline/run", json={})
    assert response.status_code == 422


def test_pipeline_status(client):
    response = client.get("/pipeline/status/123")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_pipeline_history(client):
    response = client.get("/pipeline/history")
    assert response.status_code == 200
    assert response.json()["success"] is True
