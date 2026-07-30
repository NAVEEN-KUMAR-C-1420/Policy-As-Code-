def test_list_reports(client):
    response = client.get("/reports")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_download_report_not_found(client):
    response = client.get("/reports/invalid_report.md/download")
    assert response.status_code == 404
