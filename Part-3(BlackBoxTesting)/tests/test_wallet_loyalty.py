import pytest
from .helpers import assert_status, assert_json


@pytest.mark.user
def test_wallet_get(user_client):
    resp = user_client.request("GET", "/api/v1/wallet")
    assert_status(resp, 200)
    data = assert_json(resp)
    assert "balance" in data


@pytest.mark.user
@pytest.mark.boundary
def test_wallet_add_boundaries(user_client):
    resp = user_client.request("POST", "/api/v1/wallet/add", json={"amount": 0})
    assert_status(resp, 400)
    resp = user_client.request("POST", "/api/v1/wallet/add", json={"amount": 100001})
    assert_status(resp, 400)
    resp = user_client.request("POST", "/api/v1/wallet/add", json={})
    assert resp.status_code in (400, 422)


@pytest.mark.user
def test_wallet_pay_insufficient(user_client):
    resp = user_client.request("GET", "/api/v1/wallet")
    assert_status(resp, 200)
    data = assert_json(resp)
    balance = float(data.get("balance", 0))
    resp = user_client.request("POST", "/api/v1/wallet/pay", json={"amount": 0})
    assert_status(resp, 400)
    resp = user_client.request("POST", "/api/v1/wallet/pay", json={"amount": -1})
    assert_status(resp, 400)
    resp = user_client.request("POST", "/api/v1/wallet/pay", json={"amount": balance + 1})
    assert_status(resp, 400)


@pytest.mark.user
def test_wallet_pay_exact_deduction(user_client):
    resp = user_client.request("GET", "/api/v1/wallet")
    assert_status(resp, 200)
    data = assert_json(resp)
    initial = float(data.get("balance", 0))

    add = user_client.request("POST", "/api/v1/wallet/add", json={"amount": 10})
    assert_status(add, 200)
    pay = user_client.request("POST", "/api/v1/wallet/pay", json={"amount": 10})
    assert_status(pay, 200)

    resp = user_client.request("GET", "/api/v1/wallet")
    assert_status(resp, 200)
    data = assert_json(resp)
    final = float(data.get("balance", 0))
    assert abs(final - initial) < 0.01


@pytest.mark.user
def test_loyalty_get(user_client):
    resp = user_client.request("GET", "/api/v1/loyalty")
    assert_status(resp, 200)
    data = assert_json(resp)
    assert "points" in data


@pytest.mark.user
@pytest.mark.boundary
def test_loyalty_redeem_invalid(user_client):
    resp = user_client.request("POST", "/api/v1/loyalty/redeem", json={"points": 0})
    assert_status(resp, 400)
    resp = user_client.request("POST", "/api/v1/loyalty/redeem", json={"points": -1})
    assert_status(resp, 400)
    resp = user_client.request("POST", "/api/v1/loyalty/redeem", json={"points": "1"})
    assert_status(resp, 400)
    resp = user_client.request("POST", "/api/v1/loyalty/redeem", json={})
    assert resp.status_code in (400, 422)


@pytest.mark.user
def test_loyalty_redeem_insufficient(user_client):
    resp = user_client.request("GET", "/api/v1/loyalty")
    assert_status(resp, 200)
    data = assert_json(resp)
    points = int(data.get("points", 0))
    if points == 0:
        pytest.skip("No loyalty points to redeem")
    resp = user_client.request("POST", "/api/v1/loyalty/redeem", json={"points": points + 1})
    assert_status(resp, 400)
