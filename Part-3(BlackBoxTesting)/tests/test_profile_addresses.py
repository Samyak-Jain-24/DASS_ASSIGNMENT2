import uuid
import pytest
from .helpers import assert_status, assert_json, assert_keys


def _random_text(prefix="T"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@pytest.mark.user
def test_user_header_required(base_url, default_headers):
    import requests

    resp = requests.get(f"{base_url}/api/v1/profile", headers=default_headers)
    assert_status(resp, 400)


@pytest.mark.user
def test_user_header_invalid(base_url, default_headers):
    import requests

    headers = dict(default_headers)
    headers["X-User-ID"] = "abc"
    resp = requests.get(f"{base_url}/api/v1/profile", headers=headers)
    assert_status(resp, 400)


@pytest.mark.user
def test_profile_get(user_client):
    resp = user_client.request("GET", "/api/v1/profile")
    assert_status(resp, 200)
    data = assert_json(resp)
    assert_keys(data, ["name", "phone"])


@pytest.mark.user
def test_profile_update_valid(user_client):
    payload = {"name": "QA Tester", "phone": "9999999999"}
    resp = user_client.request("PUT", "/api/v1/profile", json=payload)
    assert_status(resp, 200)
    data = assert_json(resp)
    assert data.get("name") == payload["name"]
    assert data.get("phone") == payload["phone"]


@pytest.mark.user
@pytest.mark.boundary
def test_profile_update_invalid_name(user_client):
    resp = user_client.request("PUT", "/api/v1/profile", json={"name": "A", "phone": "9999999999"})
    assert_status(resp, 400)


@pytest.mark.user
@pytest.mark.boundary
def test_profile_update_invalid_phone(user_client):
    resp = user_client.request("PUT", "/api/v1/profile", json={"name": "Valid Name", "phone": "12345"})
    assert_status(resp, 400)

    resp = user_client.request("PUT", "/api/v1/profile", json={"name": "Valid Name", "phone": "abcdefghij"})
    assert_status(resp, 400)


@pytest.mark.user
@pytest.mark.negative
def test_profile_update_missing_fields(user_client):
    resp = user_client.request("PUT", "/api/v1/profile", json={"name": "Only Name"})
    assert resp.status_code in (400, 422)
    resp = user_client.request("PUT", "/api/v1/profile", json={"phone": "9999999999"})
    assert resp.status_code in (400, 422)


@pytest.mark.user
def test_address_crud_flow(user_client):
    payload = {
        "label": "OTHER",
        "street": "Main Street 12",
        "city": "Hyderabad",
        "pincode": "500001",
        "is_default": True,
    }
    create = user_client.request("POST", "/api/v1/addresses", json=payload)
    assert_status(create, 200)
    created = assert_json(create)
    assert "address_id" in created
    address_id = created["address_id"]

    resp = user_client.request("GET", "/api/v1/addresses")
    assert_status(resp, 200)
    addresses = assert_json(resp)
    assert any(a["address_id"] == address_id for a in addresses)

    new_street = f"{_random_text('Street')}"
    update = user_client.request(
        "PUT",
        f"/api/v1/addresses/{address_id}",
        json={"street": new_street, "is_default": False},
    )
    assert_status(update, 200)
    updated = assert_json(update)
    assert updated.get("street") == new_street

    delete = user_client.request("DELETE", f"/api/v1/addresses/{address_id}")
    assert_status(delete, 200)


@pytest.mark.user
@pytest.mark.boundary
def test_address_invalid_payloads(user_client):
    bad_label = {
        "label": "HOUSE",
        "street": "Main Street 12",
        "city": "Hyderabad",
        "pincode": "500001",
    }
    resp = user_client.request("POST", "/api/v1/addresses", json=bad_label)
    assert_status(resp, 400)

    missing_field = {
        "label": "HOME",
        "street": "Main Street 12",
        "pincode": "500001",
    }
    resp = user_client.request("POST", "/api/v1/addresses", json=missing_field)
    assert resp.status_code in (400, 422)

    short_street = {
        "label": "HOME",
        "street": "1234",
        "city": "Hyderabad",
        "pincode": "500001",
    }
    resp = user_client.request("POST", "/api/v1/addresses", json=short_street)
    assert_status(resp, 400)

    short_city = {
        "label": "HOME",
        "street": "Main Street 12",
        "city": "H",
        "pincode": "500001",
    }
    resp = user_client.request("POST", "/api/v1/addresses", json=short_city)
    assert_status(resp, 400)

    bad_pincode = {
        "label": "HOME",
        "street": "Main Street 12",
        "city": "Hyderabad",
        "pincode": "ABCDE",
    }
    resp = user_client.request("POST", "/api/v1/addresses", json=bad_pincode)
    assert_status(resp, 400)

    resp = user_client.request("POST", "/api/v1/addresses", json={})
    assert resp.status_code in (400, 422)


@pytest.mark.user
def test_address_delete_missing(user_client):
    resp = user_client.request("DELETE", "/api/v1/addresses/99999999")
    assert_status(resp, 404)
