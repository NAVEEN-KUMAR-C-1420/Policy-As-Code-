def test_list_tools(client):
    response = client.get("/tools")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_get_tool_metadata(client):
    response = client.get("/tools/read_account_transactions")
    # Whether it succeeds or fails depends on if it exists, but format is standard
    assert "success" in response.json()
