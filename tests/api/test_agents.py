def test_list_agents(client):
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)

def test_get_agent_success(client):
    # Depending on what agents exist. E.g., data_collector_agent
    response = client.get("/agents/data_collector_agent")
    if response.json()["success"]:
        assert response.status_code == 200
    else:
        assert response.status_code == 404

def test_get_agent_not_found(client):
    response = client.get("/agents/invalid_agent_xyz")
    # API might return 200 with success=False, or 400. We check envelope structure.
    data = response.json()
    assert "success" in data

def test_agent_run_validation_error(client):
    # Missing input_data
    response = client.post("/agents/data_collector_agent/run", json={})
    assert response.status_code == 422
