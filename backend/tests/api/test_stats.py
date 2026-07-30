def test_agent_stats(client):
    response = client.get("/stats/agents")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_tool_stats(client):
    response = client.get("/stats/tools")
    assert response.status_code == 200
    assert response.json()["success"] is True
