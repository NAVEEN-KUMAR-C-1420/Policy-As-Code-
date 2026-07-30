def test_list_versions(client):
    response = client.get("/policies/data_collector_agent/versions")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert isinstance(response.json()["data"], list)


def test_get_historical_policy_not_found(client):
    response = client.get("/policies/data_collector_agent/versions/invalid_sha")
    assert response.json()["success"] is False


def test_rollback_validation(client):
    response = client.post("/policies/data_collector_agent/rollback", json={})
    assert response.status_code == 422
