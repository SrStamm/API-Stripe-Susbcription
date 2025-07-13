from test.conftest import client, auth_headers


def test_get_plans(client):
    response = client.get("/plans/")
    assert response.status_code == 200
