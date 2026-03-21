import math
import pytest
from .helpers import assert_status, assert_json


def _cart_snapshot(user_client):
    resp = user_client.request("GET", "/api/v1/cart")
    assert_status(resp, 200)
    data = assert_json(resp)
    if isinstance(data, dict) and "items" in data:
        items = data["items"]
        total = data.get("total")
    elif isinstance(data, list):
        items = data
        total = None
    else:
        items, total = [], None
    if total is None:
        total = 0
        for item in items:
            qty = item.get("quantity", 0)
            price = item.get("unit_price", item.get("price", 0))
            total += qty * price
    return items, float(total)


def _ensure_cart_with_product(user_client, admin_client):
    if admin_client is None:
        pytest.skip("Admin client required to select products")
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product = None
    for p in products:
        active = p.get("active")
        if active is None:
            active = p.get("is_active")
        if active in (True, 1, "true"):
            product = p
            break
    if product is None:
        product = products[0]
    product_id = product.get("product_id")
    user_client.request("DELETE", "/api/v1/cart/clear")
    resp = user_client.request("POST", "/api/v1/cart/add", json={"product_id": product_id, "quantity": 1})
    assert_status(resp, 200)
    return product_id


def _coupon_code(coupon):
    for key in ("code", "coupon_code", "couponCode"):
        if key in coupon:
            return coupon[key]
    return None


@pytest.mark.user
@pytest.mark.negative
def test_coupon_apply_invalid(user_client):
    resp = user_client.request("POST", "/api/v1/coupon/apply", json={"code": "INVALIDCODE"})
    assert resp.status_code in (400, 404)


@pytest.mark.user
@pytest.mark.negative
def test_coupon_apply_missing_code(user_client):
    resp = user_client.request("POST", "/api/v1/coupon/apply", json={})
    assert resp.status_code in (400, 422)


@pytest.mark.user
def test_coupon_remove(user_client):
    resp = user_client.request("POST", "/api/v1/coupon/remove")
    assert resp.status_code in (200, 400)


@pytest.mark.user
def test_coupon_apply_if_available(user_client, admin_client):
    coupons = admin_client.get_json("/api/v1/admin/coupons")
    if not coupons:
        pytest.skip("No coupons available")
    code = _coupon_code(coupons[0])
    if not code:
        pytest.skip("No recognizable coupon code field")
    _ensure_cart_with_product(user_client, admin_client)
    resp = user_client.request("POST", "/api/v1/coupon/apply", json={"code": code})
    if resp.status_code != 200:
        pytest.skip("Coupon not applicable to current cart")
    data = assert_json(resp)
    assert "discount" in data or "total" in data

    remove = user_client.request("POST", "/api/v1/coupon/remove")
    assert remove.status_code in (200, 400)


@pytest.mark.user
@pytest.mark.negative
def test_checkout_invalid_method(user_client, admin_client):
    _ensure_cart_with_product(user_client, admin_client)
    resp = user_client.request("POST", "/api/v1/checkout", json={"payment_method": "CRYPTO"})
    assert_status(resp, 400)


@pytest.mark.user
@pytest.mark.negative
def test_checkout_empty_cart(user_client):
    user_client.request("DELETE", "/api/v1/cart/clear")
    resp = user_client.request("POST", "/api/v1/checkout", json={"payment_method": "COD"})
    assert_status(resp, 400)


@pytest.mark.user
def test_checkout_valid_flow(user_client, admin_client):
    _ensure_cart_with_product(user_client, admin_client)
    items, subtotal = _cart_snapshot(user_client)
    gst = subtotal * 0.05
    expected_total = subtotal + gst

    method = "COD" if expected_total <= 5000 else "WALLET"
    if method == "WALLET":
        wallet = user_client.request("GET", "/api/v1/wallet")
        assert_status(wallet, 200)
        wallet_data = assert_json(wallet)
        balance = float(wallet_data.get("balance", 0))
        if balance < expected_total:
            add = user_client.request("POST", "/api/v1/wallet/add", json={"amount": math.ceil(expected_total - balance)})
            assert_status(add, 200)

    resp = user_client.request("POST", "/api/v1/checkout", json={"payment_method": method})
    assert_status(resp, 200)
    data = assert_json(resp)
    assert data.get("payment_status") in ("PENDING", "PAID")
