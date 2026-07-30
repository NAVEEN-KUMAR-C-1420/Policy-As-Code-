def test_search_audit(client):
    response = client.post("/audit/search", json={})
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)

def test_export_audit(client):
    response = client.get("/audit/export")
    assert response.status_code == 200
    assert response.json()["success"] is True
