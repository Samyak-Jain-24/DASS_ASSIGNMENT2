import pytest
from .helpers import assert_status, assert_json, assert_keys


def _pick_active_product(admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    for product in products:
        active = product.get("active")
        if active is None:
            active = product.get("is_active")
        if active in (True, 1, "true"):
            return product
    return products[0]


@pytest.mark.user
def test_products_list_only_active(user_client, admin_client):
    admin_products = admin_client.get_json("/api/v1/admin/products")
    resp = user_client.request("GET", "/api/v1/products")
    assert_status(resp, 200)
    public_products = assert_json(resp)
    public_ids = {p.get("product_id") for p in public_products}
    inactive_ids = set()
    for p in admin_products:
        active = p.get("active")
        if active is None:
            active = p.get("is_active")
        if active in (False, 0, "false"):
            inactive_ids.add(p.get("product_id"))
    if inactive_ids:
        assert not (public_ids & inactive_ids)


@pytest.mark.user
def test_products_get(user_client, admin_client):
    product = _pick_active_product(admin_client)
    product_id = product.get("product_id")
    resp = user_client.request("GET", f"/api/v1/products/{product_id}")
    assert_status(resp, 200)
    data = assert_json(resp)
    assert data.get("product_id") == product_id


@pytest.mark.user
@pytest.mark.negative
def test_products_get_missing(user_client):
    resp = user_client.request("GET", "/api/v1/products/99999999")
    assert_status(resp, 404)


def _cart_items(cart):
    if isinstance(cart, dict) and "items" in cart:
        return cart["items"], cart.get("total")
    if isinstance(cart, list):
        return cart, None
    return [], None


@pytest.mark.user
def test_cart_add_update_remove(user_client, admin_client):
    product = _pick_active_product(admin_client)
    product_id = product.get("product_id")

    user_client.request("DELETE", "/api/v1/cart/clear")

    add1 = user_client.request("POST", "/api/v1/cart/add", json={"product_id": product_id, "quantity": 1})
    assert_status(add1, 200)

    add2 = user_client.request("POST", "/api/v1/cart/add", json={"product_id": product_id, "quantity": 2})
    assert_status(add2, 200)

    cart = user_client.request("GET", "/api/v1/cart")
    assert_status(cart, 200)
    cart_json = assert_json(cart)
    items, total = _cart_items(cart_json)
    item = next((i for i in items if i.get("product_id") == product_id), None)
    assert item, "Expected product in cart"
    assert item.get("quantity") in (3, "3")
    if "subtotal" in item and ("unit_price" in item or "price" in item):
        unit_price = item.get("unit_price", item.get("price"))
        assert abs(float(item["subtotal"]) - (float(unit_price) * float(item["quantity"]))) < 0.01
    if total is not None and items:
        computed = 0
        for i in items:
            unit_price = i.get("unit_price", i.get("price", 0))
            computed += float(i.get("quantity", 0)) * float(unit_price)
        assert abs(float(total) - computed) < 0.01

    update = user_client.request("POST", "/api/v1/cart/update", json={"product_id": product_id, "quantity": 1})
    assert_status(update, 200)

    remove = user_client.request("POST", "/api/v1/cart/remove", json={"product_id": product_id})
    assert_status(remove, 200)


@pytest.mark.user
@pytest.mark.boundary
def test_cart_invalid_quantity(user_client, admin_client):
    product = _pick_active_product(admin_client)
    product_id = product.get("product_id")
    resp = user_client.request("POST", "/api/v1/cart/add", json={"product_id": product_id, "quantity": 0})
    assert_status(resp, 400)

    resp = user_client.request("POST", "/api/v1/cart/add", json={"product_id": product_id, "quantity": "one"})
    assert resp.status_code in (400, 422)

    resp = user_client.request("POST", "/api/v1/cart/update", json={"product_id": product_id, "quantity": 0})
    assert_status(resp, 400)


@pytest.mark.user
@pytest.mark.negative
def test_cart_missing_fields(user_client):
    resp = user_client.request("POST", "/api/v1/cart/add", json={"quantity": 1})
    assert resp.status_code in (400, 422)
    resp = user_client.request("POST", "/api/v1/cart/add", json={"product_id": 1})
    assert resp.status_code in (400, 422)


@pytest.mark.user
@pytest.mark.negative
def test_cart_remove_missing(user_client):
    resp = user_client.request("POST", "/api/v1/cart/remove", json={"product_id": 99999999})
    assert_status(resp, 404)
