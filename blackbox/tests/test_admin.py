import pytest
from .helpers import assert_status, assert_json, assert_keys


@pytest.mark.admin
def test_admin_users_list(admin_client):
    resp = admin_client.request("GET", "/api/v1/admin/users")
    assert_status(resp, 200)
    data = assert_json(resp)
    assert isinstance(data, list)


@pytest.mark.admin
def test_admin_users_get(admin_client):
    users = admin_client.get_json("/api/v1/admin/users")
    if not users:
        pytest.skip("No users to fetch")
    user_id = users[0]["user_id"]
    resp = admin_client.request("GET", f"/api/v1/admin/users/{user_id}")
    assert_status(resp, 200)
    data = assert_json(resp)
    assert_keys(data, ["user_id", "wallet_balance", "loyalty_points"])


@pytest.mark.admin
def test_admin_users_missing(admin_client):
    resp = admin_client.request("GET", "/api/v1/admin/users/99999999")
    assert resp.status_code in (404, 400)


@pytest.mark.admin
def test_admin_products_list(admin_client):
    resp = admin_client.request("GET", "/api/v1/admin/products")
    assert_status(resp, 200)
    data = assert_json(resp)
    assert isinstance(data, list)


@pytest.mark.admin
def test_missing_roll_header(base_url):
    import requests

    resp = requests.get(f"{base_url}/api/v1/admin/users")
    assert_status(resp, 401)


@pytest.mark.admin
def test_invalid_roll_header(base_url):
    import requests

    resp = requests.get(
        f"{base_url}/api/v1/admin/users", headers={"X-Roll-Number": "abc"}
    )
    assert_status(resp, 400)
