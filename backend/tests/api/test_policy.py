def test_list_policies(client):
    response = client.get("/policies")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_get_policy_schema(client):
    response = client.get("/policies/schema")
    assert response.status_code == 200


def test_validate_policy_valid(client):
    valid_yaml = "agent_id: test\nname: test"
    response = client.post("/policies/validate", json={"policy_yaml_content": valid_yaml})
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_deploy_policy_invalid(client):
    invalid_yaml = "invalid: yaml: :"
    response = client.post(
        "/policies/deploy", json={"agent_id": "data_collector_agent", "policy_yaml_content": invalid_yaml}
    )
    # Will throw validation error from service
    data = response.json()
    assert data["success"] is False


def test_diff_policies_validation(client):
    response = client.post("/policies/diff", json={})
    assert response.status_code == 422
