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


def _wallet_balance(user_client):
    resp = user_client.request("GET", "/api/v1/wallet")
    assert_status(resp, 200)
    data = assert_json(resp)
    if "balance" in data:
        return float(data.get("balance", 0))
    return float(data.get("wallet_balance", 0))


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


def _coupon_payload(coupons, code):
    key = "code"
    if coupons:
        sample = coupons[0]
        for field in ("code", "coupon_code", "couponCode"):
            if field in sample:
                key = field
                break
    return {key: code}


def _coupon_max_cap(coupon):
    for key in ("max_discount", "max_discount_amount", "max_cap", "max"):
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
def test_coupon_apply_expired_if_available(user_client, admin_client):
    coupons = admin_client.get_json("/api/v1/admin/coupons")
    if not coupons:
        pytest.skip("No coupons available")
    expired = None
    for coupon in coupons:
        code = _coupon_code(coupon) or ""
        if "EXPIRED" in code.upper() or coupon.get("is_expired") is True:
            expired = coupon
            break
    if not expired:
        pytest.skip("No expired coupon found")

    _ensure_cart_with_product(user_client, admin_client)
    payload = _coupon_payload(coupons, _coupon_code(expired))
    resp = user_client.request("POST", "/api/v1/coupon/apply", json=payload)
    assert_status(resp, 400)


@pytest.mark.user
@pytest.mark.negative
def test_coupon_min_cart_value_enforced(user_client, admin_client):
    coupons = admin_client.get_json("/api/v1/admin/coupons")
    if not coupons:
        pytest.skip("No coupons available")
    candidate = next((c for c in coupons if c.get("min_cart_value")), None)
    if not candidate:
        pytest.skip("No coupon with min_cart_value found")

    _ensure_cart_with_product(user_client, admin_client)
    _, total = _cart_snapshot(user_client)
    min_value = float(candidate.get("min_cart_value"))
    if total >= min_value:
        pytest.skip("Cart total already meets minimum value")

    payload = _coupon_payload(coupons, _coupon_code(candidate))
    resp = user_client.request("POST", "/api/v1/coupon/apply", json=payload)
    assert_status(resp, 400)


@pytest.mark.user
def test_coupon_max_cap_firstorder(user_client, admin_client):
    coupons = admin_client.get_json("/api/v1/admin/coupons")
    if not coupons:
        pytest.skip("No coupons available")
    target = next((c for c in coupons if str(_coupon_code(c)).upper() == "FIRSTORDER"), None)
    if not target:
        pytest.skip("FIRSTORDER coupon not available")

    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product = max(products, key=lambda p: p.get("stock", 0))
    price = float(product.get("price", 0))
    stock = int(product.get("stock", 0))
    if price <= 0 or stock <= 0:
        pytest.skip("No usable product for cap test")

    desired_total = 1200
    qty = min(stock, max(1, int(desired_total // price) + 1))
    if qty * price < 1000:
        pytest.skip("Insufficient stock to exceed cap threshold")

    user_client.request("DELETE", "/api/v1/cart/clear")
    add = user_client.request("POST", "/api/v1/cart/add", json={"product_id": product.get("product_id"), "quantity": qty})
    assert_status(add, 200)

    payload = _coupon_payload(coupons, _coupon_code(target))
    resp = user_client.request("POST", "/api/v1/coupon/apply", json=payload)
    assert_status(resp, 200)
    data = assert_json(resp)
    discount = float(data.get("discount", data.get("discount_amount", 0)))
    cap = _coupon_max_cap(target)
    if cap is not None:
        assert discount <= float(cap) + 0.01


@pytest.mark.user
def test_coupon_max_cap_percent20(user_client, admin_client):
    coupons = admin_client.get_json("/api/v1/admin/coupons")
    if not coupons:
        pytest.skip("No coupons available")
    target = next((c for c in coupons if str(_coupon_code(c)).upper() == "PERCENT20"), None)
    if not target:
        pytest.skip("PERCENT20 coupon not available")

    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product = max(products, key=lambda p: p.get("stock", 0))
    price = float(product.get("price", 0))
    stock = int(product.get("stock", 0))
    if price <= 0 or stock <= 0:
        pytest.skip("No usable product for cap test")

    desired_total = 1200
    qty = min(stock, max(1, int(desired_total // price) + 1))
    if qty * price < 1000:
        pytest.skip("Insufficient stock to exceed cap threshold")

    user_client.request("DELETE", "/api/v1/cart/clear")
    add = user_client.request("POST", "/api/v1/cart/add", json={"product_id": product.get("product_id"), "quantity": qty})
    assert_status(add, 200)

    payload = _coupon_payload(coupons, _coupon_code(target))
    resp = user_client.request("POST", "/api/v1/coupon/apply", json=payload)
    assert_status(resp, 200)
    data = assert_json(resp)
    discount = float(data.get("discount", data.get("discount_amount", 0)))
    cap = _coupon_max_cap(target)
    if cap is not None:
        assert discount <= float(cap) + 0.01


@pytest.mark.user
@pytest.mark.negative
def test_checkout_invalid_method(user_client, admin_client):
    _ensure_cart_with_product(user_client, admin_client)
    resp = user_client.request("POST", "/api/v1/checkout", json={"payment_method": "CRYPTO"})
    assert_status(resp, 400)


@pytest.mark.user
@pytest.mark.negative
def test_checkout_missing_payment_method(user_client, admin_client):
    _ensure_cart_with_product(user_client, admin_client)
    resp = user_client.request("POST", "/api/v1/checkout", json={})
    assert_status(resp, 400)

    resp = user_client.request("POST", "/api/v1/checkout", json={"payment_method": None})
    assert_status(resp, 400)

    resp = user_client.request("POST", "/api/v1/checkout", json={"payment_method": 123})
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


@pytest.mark.user
def test_checkout_cod_limit(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product = max(products, key=lambda p: p.get("stock", 0))
    price = float(product.get("price", 0))
    stock = int(product.get("stock", 0))
    if price <= 0 or stock <= 0:
        pytest.skip("No usable product for COD limit test")

    desired_total = 5100
    qty = min(stock, max(1, int(desired_total // price) + 1))
    if qty * price <= 5000:
        pytest.skip("Insufficient stock to exceed COD limit")

    user_client.request("DELETE", "/api/v1/cart/clear")
    add = user_client.request("POST", "/api/v1/cart/add", json={"product_id": product.get("product_id"), "quantity": qty})
    assert_status(add, 200)

    resp = user_client.request("POST", "/api/v1/checkout", json={"payment_method": "COD"})
    assert_status(resp, 400)


@pytest.mark.user
def test_checkout_payment_status_mapping(user_client, admin_client):
    _ensure_cart_with_product(user_client, admin_client)
    resp = user_client.request("POST", "/api/v1/checkout", json={"payment_method": "CARD"})
    assert_status(resp, 200)
    data = assert_json(resp)
    assert data.get("payment_status") == "PAID"

    _ensure_cart_with_product(user_client, admin_client)
    resp = user_client.request("POST", "/api/v1/checkout", json={"payment_method": "COD"})
    assert_status(resp, 200)
    data = assert_json(resp)
    assert data.get("payment_status") == "PENDING"

    _ensure_cart_with_product(user_client, admin_client)
    wallet = user_client.request("GET", "/api/v1/wallet")
    assert_status(wallet, 200)
    wallet_data = assert_json(wallet)
    balance = float(wallet_data.get("balance", 0))
    items, total = _cart_snapshot(user_client)
    if balance < total:
        add = user_client.request("POST", "/api/v1/wallet/add", json={"amount": math.ceil(total - balance)})
        assert_status(add, 200)
    resp = user_client.request("POST", "/api/v1/checkout", json={"payment_method": "WALLET"})
    assert_status(resp, 200)
    data = assert_json(resp)
    assert data.get("payment_status") == "PENDING"


@pytest.mark.user
def test_wallet_checkout_insufficient_funds(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product = max(products, key=lambda p: p.get("stock", 0))
    price = float(product.get("price", 0))
    stock = int(product.get("stock", 0))
    if price <= 0 or stock <= 0:
        pytest.skip("No usable product for wallet checkout")

    balance = _wallet_balance(user_client)
    desired_total = balance + 100
    qty = min(stock, max(1, int(desired_total // price) + 1))
    if qty * price <= balance:
        pytest.skip("Insufficient stock to exceed wallet balance")

    user_client.request("DELETE", "/api/v1/cart/clear")
    add = user_client.request("POST", "/api/v1/cart/add", json={"product_id": product.get("product_id"), "quantity": qty})
    assert_status(add, 200)

    resp = user_client.request("POST", "/api/v1/checkout", json={"payment_method": "WALLET"})
    assert_status(resp, 400)


@pytest.mark.user
def test_wallet_checkout_deducts_balance(user_client, admin_client):
    _ensure_cart_with_product(user_client, admin_client)
    items, subtotal = _cart_snapshot(user_client)
    expected_total = subtotal + (subtotal * 0.05)
    balance = _wallet_balance(user_client)
    if balance < expected_total:
        add = user_client.request("POST", "/api/v1/wallet/add", json={"amount": expected_total - balance + 1})
        assert_status(add, 200)
    pre_balance = _wallet_balance(user_client)

    resp = user_client.request("POST", "/api/v1/checkout", json={"payment_method": "WALLET"})
    if resp.status_code != 200:
        pytest.skip("Wallet checkout not allowed")
    post_balance = _wallet_balance(user_client)
    assert abs(pre_balance - post_balance - expected_total) < 0.05
