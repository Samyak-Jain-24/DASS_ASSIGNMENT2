import pytest
from .helpers import assert_status, assert_json


def _pick_order(user_client):
    resp = user_client.request("GET", "/api/v1/orders")
    assert_status(resp, 200)
    orders = assert_json(resp)
    if not orders:
        pytest.skip("No orders available")
    return orders[0]
    

@pytest.mark.user
def test_orders_list(user_client):
    resp = user_client.request("GET", "/api/v1/orders")
    assert_status(resp, 200)
    data = assert_json(resp)
    assert isinstance(data, list)


@pytest.mark.user
def test_order_detail_and_invoice(user_client):
    order = _pick_order(user_client)
    order_id = order.get("order_id")
    detail = user_client.request("GET", f"/api/v1/orders/{order_id}")
    assert_status(detail, 200)

    invoice = user_client.request("GET", f"/api/v1/orders/{order_id}/invoice")
    assert_status(invoice, 200)
    inv = assert_json(invoice)
    subtotal = float(inv.get("subtotal", 0))
    gst = float(inv.get("gst", 0))
    total = float(inv.get("total", 0))
    assert abs((subtotal + gst) - total) < 0.01


@pytest.mark.user
@pytest.mark.negative
def test_order_detail_missing(user_client):
    resp = user_client.request("GET", "/api/v1/orders/99999999")
    assert_status(resp, 404)


@pytest.mark.user
def test_cancel_already_cancelled_order(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product = products[0]
    user_client.request("DELETE", "/api/v1/cart/clear")
    add = user_client.request("POST", "/api/v1/cart/add", json={"product_id": product.get("product_id"), "quantity": 1})
    if add.status_code != 200:
        pytest.skip("Could not add product to cart")

    checkout = user_client.request("POST", "/api/v1/checkout", json={"payment_method": "COD"})
    if checkout.status_code != 200:
        pytest.skip("Checkout failed")
    order_id = assert_json(checkout).get("order_id")
    if not order_id:
        pytest.skip("Order ID missing from checkout response")

    first = user_client.request("POST", f"/api/v1/orders/{order_id}/cancel")
    assert_status(first, 200)
    second = user_client.request("POST", f"/api/v1/orders/{order_id}/cancel")
    assert_status(second, 400)


@pytest.mark.user
def test_cancel_restores_stock_exactly(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if len(products) < 2:
        pytest.skip("Need at least two products")
    product_a = products[0]
    product_b = products[1]

    stock_before = {
        product_a.get("product_id"): product_a.get("stock", product_a.get("stock_quantity")),
        product_b.get("product_id"): product_b.get("stock", product_b.get("stock_quantity")),
    }
    if stock_before[product_a.get("product_id")] is None or stock_before[product_b.get("product_id")] is None:
        pytest.skip("Stock fields missing")

    user_client.request("DELETE", "/api/v1/cart/clear")
    add1 = user_client.request("POST", "/api/v1/cart/add", json={"product_id": product_a.get("product_id"), "quantity": 1})
    add2 = user_client.request("POST", "/api/v1/cart/add", json={"product_id": product_b.get("product_id"), "quantity": 1})
    if add1.status_code != 200 or add2.status_code != 200:
        pytest.skip("Could not add products to cart")

    checkout = user_client.request("POST", "/api/v1/checkout", json={"payment_method": "COD"})
    if checkout.status_code != 200:
        pytest.skip("Checkout failed")
    order_id = assert_json(checkout).get("order_id")
    if not order_id:
        pytest.skip("Order ID missing from checkout response")

    cancel = user_client.request("POST", f"/api/v1/orders/{order_id}/cancel")
    assert_status(cancel, 200)

    products_after = admin_client.get_json("/api/v1/admin/products")
    after_map = {p.get("product_id"): p.get("stock", p.get("stock_quantity")) for p in products_after}
    assert after_map.get(product_a.get("product_id")) == stock_before.get(product_a.get("product_id"))
    assert after_map.get(product_b.get("product_id")) == stock_before.get(product_b.get("product_id"))


@pytest.mark.user
def test_cancel_delivered_order_if_any(user_client):
    resp = user_client.request("GET", "/api/v1/orders")
    assert_status(resp, 200)
    orders = assert_json(resp)
    delivered = next((o for o in orders if o.get("status") == "DELIVERED"), None)
    if not delivered:
        pytest.skip("No delivered orders")
    order_id = delivered.get("order_id")
    cancel = user_client.request("POST", f"/api/v1/orders/{order_id}/cancel")
    assert_status(cancel, 400)


@pytest.mark.user
def test_cancel_order_restores_stock_if_possible(user_client, admin_client):
    orders_resp = user_client.request("GET", "/api/v1/orders")
    assert_status(orders_resp, 200)
    orders = assert_json(orders_resp)
    cancellable = next((o for o in orders if o.get("status") not in ("DELIVERED", "CANCELLED")), None)
    if not cancellable:
        pytest.skip("No cancellable orders")
    order_id = cancellable.get("order_id")
    detail = user_client.request("GET", f"/api/v1/orders/{order_id}")
    assert_status(detail, 200)
    order = assert_json(detail)
    items = order.get("items", [])
    if not items:
        pytest.skip("Order has no items")
    products_before = {p.get("product_id"): p for p in admin_client.get_json("/api/v1/admin/products")}

    cancel = user_client.request("POST", f"/api/v1/orders/{order_id}/cancel")
    if cancel.status_code != 200:
        pytest.skip("Cancel not allowed in current state")

    products_after = {p.get("product_id"): p for p in admin_client.get_json("/api/v1/admin/products")}
    for item in items:
        product_id = item.get("product_id")
        if product_id not in products_before or product_id not in products_after:
            continue
        stock_before = products_before[product_id].get("stock")
        stock_after = products_after[product_id].get("stock")
        if stock_before is None or stock_after is None:
            continue
        assert stock_after >= stock_before


@pytest.mark.user
@pytest.mark.negative
def test_cancel_missing_order(user_client):
    resp = user_client.request("POST", "/api/v1/orders/99999999/cancel")
    assert_status(resp, 404)


@pytest.mark.user
def test_reviews_get_and_average(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product_id = products[0].get("product_id")
    resp = user_client.request("GET", f"/api/v1/products/{product_id}/reviews")
    assert_status(resp, 200)
    data = assert_json(resp)
    reviews = data.get("reviews", []) if isinstance(data, dict) else data
    avg = data.get("average_rating", 0) if isinstance(data, dict) else 0
    if reviews:
        calc = sum(r.get("rating", 0) for r in reviews) / len(reviews)
        assert abs(calc - float(avg)) < 0.01
    else:
        assert float(avg) == 0


@pytest.mark.user
@pytest.mark.negative
def test_reviews_nonexistent_product(user_client):
    resp = user_client.request("GET", "/api/v1/products/9999999/reviews")
    assert_status(resp, 404)


@pytest.mark.user
@pytest.mark.negative
def test_reviews_invalid_types(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product_id = products[0].get("product_id")
    resp = user_client.request(
        "POST",
        f"/api/v1/products/{product_id}/reviews",
        json={"rating": None, "comment": "Nice"},
    )
    if resp.status_code != 404:
        assert resp.status_code in (400, 422)


@pytest.mark.user
@pytest.mark.boundary
def test_reviews_invalid_rating(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product_id = products[0].get("product_id")
    resp = user_client.request("POST", f"/api/v1/products/{product_id}/reviews", json={"rating": 0, "comment": "bad"})
    assert_status(resp, 400)


@pytest.mark.user
@pytest.mark.boundary
def test_reviews_invalid_rating_upper(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product_id = products[0].get("product_id")
    resp = user_client.request("POST", f"/api/v1/products/{product_id}/reviews", json={"rating": 6, "comment": "too high"})
    assert_status(resp, 400)


@pytest.mark.user
@pytest.mark.boundary
def test_reviews_invalid_rating_type(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product_id = products[0].get("product_id")
    resp = user_client.request("POST", f"/api/v1/products/{product_id}/reviews", json={"rating": "5", "comment": "type"})
    assert_status(resp, 400)


@pytest.mark.user
@pytest.mark.boundary
def test_reviews_invalid_comment_length(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product_id = products[0].get("product_id")
    resp = user_client.request(
        "POST",
        f"/api/v1/products/{product_id}/reviews",
        json={"rating": 3, "comment": ""},
    )
    assert_status(resp, 400)


@pytest.mark.user
@pytest.mark.boundary
def test_reviews_invalid_comment_max(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product_id = products[0].get("product_id")
    resp = user_client.request(
        "POST",
        f"/api/v1/products/{product_id}/reviews",
        json={"rating": 5, "comment": "A" * 201},
    )
    assert_status(resp, 400)


@pytest.mark.user
@pytest.mark.negative
def test_reviews_missing_comment(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    product_id = products[0].get("product_id")
    resp = user_client.request(
        "POST",
        f"/api/v1/products/{product_id}/reviews",
        json={"rating": 5},
    )
    assert_status(resp, 400)


@pytest.mark.user
def test_reviews_average_zero_when_none(user_client, admin_client):
    products = admin_client.get_json("/api/v1/admin/products")
    if not products:
        pytest.skip("No products available")
    target = None
    for product in products[:10]:
        product_id = product.get("product_id")
        resp = user_client.request("GET", f"/api/v1/products/{product_id}/reviews")
        if resp.status_code != 200:
            continue
        data = assert_json(resp)
        reviews = data.get("reviews", []) if isinstance(data, dict) else data
        avg = data.get("average_rating", 0) if isinstance(data, dict) else 0
        if not reviews and float(avg) == 0:
            target = product_id
            break
    if target is None:
        pytest.skip("No product with zero reviews found")
    resp = user_client.request("GET", f"/api/v1/products/{target}/reviews")
    assert_status(resp, 200)
    data = assert_json(resp)
    reviews = data.get("reviews", []) if isinstance(data, dict) else data
    avg = data.get("average_rating", 0) if isinstance(data, dict) else 0
    assert reviews == []
    assert float(avg) == 0


@pytest.mark.user
def test_support_ticket_flow(user_client):
    create = user_client.request(
        "POST",
        "/api/v1/support/ticket",
        json={"subject": "Order delayed", "message": "Please check my order status"},
    )
    assert_status(create, 200)
    ticket = assert_json(create)
    ticket_id = ticket.get("ticket_id")
    assert ticket.get("status") == "OPEN"

    invalid = user_client.request(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        json={"status": "CLOSED"},
    )
    assert_status(invalid, 400)

    update = user_client.request(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        json={"status": "IN_PROGRESS"},
    )
    assert_status(update, 200)

    update = user_client.request(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        json={"status": "CLOSED"},
    )
    assert_status(update, 200)


@pytest.mark.user
def test_support_ticket_backward_transition(user_client):
    create = user_client.request(
        "POST",
        "/api/v1/support/ticket",
        json={"subject": "Delay", "message": "Check status"},
    )
    assert_status(create, 200)
    ticket = assert_json(create)
    ticket_id = ticket.get("ticket_id")

    update = user_client.request(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        json={"status": "IN_PROGRESS"},
    )
    assert_status(update, 200)

    invalid = user_client.request(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        json={"status": "OPEN"},
    )
    assert_status(invalid, 400)


@pytest.mark.user
def test_support_ticket_invalid_status_value(user_client):
    create = user_client.request(
        "POST",
        "/api/v1/support/ticket",
        json={"subject": "Delay", "message": "Check status"},
    )
    assert_status(create, 200)
    ticket = assert_json(create)
    ticket_id = ticket.get("ticket_id")

    invalid = user_client.request(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        json={"status": "REOPENED"},
    )
    assert_status(invalid, 400)


@pytest.mark.user
def test_support_ticket_closed_cannot_reopen(user_client):
    create = user_client.request(
        "POST",
        "/api/v1/support/ticket",
        json={"subject": "Delay", "message": "Check status"},
    )
    assert_status(create, 200)
    ticket = assert_json(create)
    ticket_id = ticket.get("ticket_id")

    update = user_client.request(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        json={"status": "IN_PROGRESS"},
    )
    assert_status(update, 200)

    update = user_client.request(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        json={"status": "CLOSED"},
    )
    assert_status(update, 200)

    invalid = user_client.request(
        "PUT",
        f"/api/v1/support/tickets/{ticket_id}",
        json={"status": "IN_PROGRESS"},
    )
    assert_status(invalid, 400)


@pytest.mark.user
@pytest.mark.boundary
def test_support_ticket_invalid_fields(user_client):
    resp = user_client.request(
        "POST",
        "/api/v1/support/ticket",
        json={"subject": "ABCD", "message": "M"},
    )
    assert_status(resp, 400)

    resp = user_client.request(
        "POST",
        "/api/v1/support/ticket",
        json={},
    )
    assert_status(resp, 400)


@pytest.mark.user
def test_support_tickets_list(user_client):
    resp = user_client.request("GET", "/api/v1/support/tickets")
    assert_status(resp, 200)
    data = assert_json(resp)
    assert isinstance(data, list)


@pytest.mark.user
def test_support_ticket_update_missing(user_client):
    resp = user_client.request(
        "PUT",
        "/api/v1/support/tickets/99999999",
        json={"status": "IN_PROGRESS"},
    )
    assert_status(resp, 404)
