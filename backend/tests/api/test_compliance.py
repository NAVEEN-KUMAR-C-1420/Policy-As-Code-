def test_compliance_status(client):
    response = client.get("/compliance/summary")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_compliance_report(client):
    response = client.get("/compliance/report")
    assert response.status_code == 200
    assert response.json()["success"] is True
