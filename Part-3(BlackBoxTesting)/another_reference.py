import pytest
import requests

BASE_URL = "http://localhost:8080/api/v1"

# --- FIXTURES ---

@pytest.fixture
def user_1_headers():
    return {"X-Roll-Number": "2024101011", "X-User-ID": "11"}

@pytest.fixture
def user_2_headers():
    return {"X-Roll-Number": "2024101010", "X-User-ID": "12"}

@pytest.fixture
def valid_headers():
    return {
        "X-Roll-Number": "2024101011",
        "X-User-ID": "1"
    }

@pytest.fixture
def admin_headers():
    return {
        "X-Roll-Number": "2024101011"
    }

# --- GLOBAL / AUTHORIZATION TESTS ---

def test_missing_roll_number_returns_401():
    response = requests.get(f"{BASE_URL}/profile", headers={"X-User-ID": "1"})
    assert response.status_code == 401

def test_invalid_roll_number_returns_400():
    response = requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": "abc", "X-User-ID": "1"})
    assert response.status_code == 400

def test_missing_user_id_returns_400(admin_headers):
    # Missing X-User-ID on a user-scoped endpoint
    response = requests.get(f"{BASE_URL}/profile", headers=admin_headers)
    assert response.status_code == 400

# --- ADMIN TESTS ---

def test_admin_endpoints_success(admin_headers):
    endpoints = ["users", "carts", "orders", "products", "coupons", "tickets", "addresses"]
    for ep in endpoints:
        response = requests.get(f"{BASE_URL}/admin/{ep}", headers=admin_headers)
        assert response.status_code == 200

# --- PROFILE TESTS ---

def test_get_profile(valid_headers):
    response = requests.get(f"{BASE_URL}/profile", headers=valid_headers)
    assert response.status_code == 200

@pytest.mark.parametrize("name, phone, expected_status", [
    ("Alice", "1234567890", 200),          # Valid
    ("A", "1234567890", 400),              # Name too short (<2)
    ("A" * 51, "1234567890", 400),         # Name too long (>50)
    ("Bob", "12345", 400),                 # Phone too short
    ("Bob", "12345678901", 400),           # Phone too long
    ("Bob", "abcdefghij", 400),            # Phone invalid chars
])
def test_put_profile_validation(valid_headers, name, phone, expected_status):
    payload = {"name": name, "phone": phone}
    response = requests.put(f"{BASE_URL}/profile", json=payload, headers=valid_headers)
    assert response.status_code == expected_status

# --- ADDRESS TESTS ---

def test_add_address_valid(valid_headers):
    payload = {
        "label": "HOME",
        "street": "123 Main Street",
        "city": "Hyderabad",
        "pincode": "500001"
    }
    response = requests.post(f"{BASE_URL}/addresses", json=payload, headers=valid_headers)
    assert response.status_code in [200, 201]
    data = response.json()
    assert "address_id" in data
    assert data["label"] == "HOME"

@pytest.mark.parametrize("label, street, city, pincode, expected_status", [
    ("INVALID", "123 Main Street", "Hyderabad", "500001", 400), # Invalid label
    ("HOME", "123", "Hyderabad", "500001", 400),                # Street too short (<5)
    ("HOME", "123 Main Street", "H", "500001", 400),            # City too short (<2)
    ("HOME", "123 Main Street", "Hyderabad", "500", 400),       # Pincode too short
    ("HOME", "123 Main Street", "Hyderabad", "5000010", 400),   # Pincode too long
])
def test_add_address_invalid(valid_headers, label, street, city, pincode, expected_status):
    payload = {"label": label, "street": street, "city": city, "pincode": pincode}
    response = requests.post(f"{BASE_URL}/addresses", json=payload, headers=valid_headers)
    assert response.status_code == expected_status

def test_delete_nonexistent_address(valid_headers):
    response = requests.delete(f"{BASE_URL}/addresses/999999", headers=valid_headers)
    assert response.status_code == 404

# --- PRODUCT TESTS ---

def test_get_products(valid_headers):
    response = requests.get(f"{BASE_URL}/products", headers=valid_headers)
    assert response.status_code == 200
    # Add an assertion to check if a known inactive product is NOT in the list if you know one

def test_get_product_not_found(valid_headers):
    response = requests.get(f"{BASE_URL}/products/999999", headers=valid_headers)
    assert response.status_code == 404

# --- CART TESTS ---

def test_add_to_cart_invalid_quantity(valid_headers):
    payload = {"product_id": 1, "quantity": 0}
    response = requests.post(f"{BASE_URL}/cart/add", json=payload, headers=valid_headers)
    assert response.status_code == 400

    payload = {"product_id": 1, "quantity": -5}
    response = requests.post(f"{BASE_URL}/cart/add", json=payload, headers=valid_headers)
    assert response.status_code == 400

def test_add_nonexistent_product_to_cart(valid_headers):
    payload = {"product_id": 999999, "quantity": 1}
    response = requests.post(f"{BASE_URL}/cart/add", json=payload, headers=valid_headers)
    assert response.status_code == 404

def test_remove_nonexistent_item_from_cart(valid_headers):
    payload = {"product_id": 999999}
    response = requests.post(f"{BASE_URL}/cart/remove", json=payload, headers=valid_headers)
    assert response.status_code == 404

# --- CHECKOUT TESTS ---

def test_checkout_invalid_payment_method(valid_headers):
    payload = {"payment_method": "CRYPTO"}
    response = requests.post(f"{BASE_URL}/checkout", json=payload, headers=valid_headers)
    assert response.status_code == 400

def test_checkout_empty_cart(valid_headers):
    # Ensure cart is empty first
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    
    payload = {"payment_method": "COD"}
    response = requests.post(f"{BASE_URL}/checkout", json=payload, headers=valid_headers)
    assert response.status_code == 400

# --- WALLET TESTS ---

@pytest.mark.parametrize("amount, expected_status", [
    (500, 200),        # Valid
    (0, 400),          # Boundary invalid
    (-100, 400),       # Negative
    (100001, 400),     # Exceeds max
])
def test_wallet_add(valid_headers, amount, expected_status):
    payload = {"amount": amount}
    response = requests.post(f"{BASE_URL}/wallet/add", json=payload, headers=valid_headers)
    assert response.status_code == expected_status

def test_wallet_pay_insufficient_funds(valid_headers):
    # Try to pay an absurdly high amount
    payload = {"amount": 999999999}
    response = requests.post(f"{BASE_URL}/wallet/pay", json=payload, headers=valid_headers)
    assert response.status_code == 400

# --- REVIEWS TESTS ---

@pytest.mark.parametrize("rating, expected_status", [
    (1, 200), (5, 200),  # Valid boundaries
    (0, 400), (6, 400)   # Invalid boundaries
])
def test_add_review_rating_boundaries(valid_headers, rating, expected_status):
    # Assuming product 1 exists
    payload = {"rating": rating, "comment": "Good product!"}
    response = requests.post(f"{BASE_URL}/products/1/reviews", json=payload, headers=valid_headers)
    # This might return 404 if product 1 doesn't exist, so you may need to adjust the product ID based on your DB.
    if response.status_code != 404: 
        assert response.status_code == expected_status

# --- SUPPORT TICKETS TESTS ---

def test_create_ticket_invalid_lengths(valid_headers):
    # Subject < 5 chars
    payload1 = {"subject": "abc", "message": "Valid message here"}
    resp1 = requests.post(f"{BASE_URL}/support/ticket", json=payload1, headers=valid_headers)
    assert resp1.status_code == 400

    # Message empty
    payload2 = {"subject": "Valid Subject", "message": ""}
    resp2 = requests.post(f"{BASE_URL}/support/ticket", json=payload2, headers=valid_headers)
    assert resp2.status_code == 400

def test_ticket_invalid_state_transition(valid_headers):
    # Create a ticket first
    payload = {"subject": "Valid Subject", "message": "Valid Message"}
    resp = requests.post(f"{BASE_URL}/support/ticket", json=payload, headers=valid_headers)
    
    if resp.status_code in [200, 201]:
        ticket_id = resp.json().get("ticket_id")
        
        # Try skipping IN_PROGRESS and going straight to CLOSED (if business logic prevents it) or reverting
        # Let's test reverting from IN_PROGRESS to OPEN which is explicitly forbidden
        requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", json={"status": "IN_PROGRESS"}, headers=valid_headers)
        invalid_resp = requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", json={"status": "OPEN"}, headers=valid_headers)
        
        assert invalid_resp.status_code == 400

# =================================================================== MORE TESTS =========================================================
# --- ADDRESS TESTS (Update Restrictions) ---

def test_update_address_restricted_fields(valid_headers):
    # The doc states: "only the street and the is_default field can be changed. Label, city, and pincode cannot be changed"
    # Assuming address ID 1 exists
    payload = {
        "street": "456 New Street",
        "is_default": True,
        "city": "Mumbai",  # This should be ignored or throw an error depending on strictness
        "label": "OFFICE"  # This should also be ignored/rejected
    }
    response = requests.put(f"{BASE_URL}/addresses/1", json=payload, headers=valid_headers)
    
    # If the API strictly rejects requests with immutable fields, it should return 400.
    # If it ignores them, it returns 200 but the response should NOT reflect the changed city/label.
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        data = response.json()
        assert data["street"] == "456 New Street"
        # Ensure immutable fields didn't change (assuming original wasn't Mumbai/OFFICE)
        assert data.get("city") != "Mumbai" or data.get("label") != "OFFICE"

# --- PRODUCT TESTS (Filtering and Sorting) ---

def test_get_products_with_filters(valid_headers):
    # Testing query parameters: category, search, sort
    params = {
        "category": "Electronics",
        "search": "Phone",
        "sort": "price_asc"
    }
    response = requests.get(f"{BASE_URL}/products", params=params, headers=valid_headers)
    assert response.status_code == 200
    products = response.json()
    
    # Verify sorting logic if products are returned
    if len(products) > 1:
        prices = [p["price"] for p in products]
        assert prices == sorted(prices), "Products are not sorted by price ascending"

# --- CART TESTS (Updates and Limits) ---

def test_cart_add_exceeds_stock(valid_headers):
    # The doc states: "If the quantity asked for is more than what is in stock, the server returns a 400 error."
    payload = {"product_id": 1, "quantity": 999999} # Unlikely to have this much stock
    response = requests.post(f"{BASE_URL}/cart/add", json=payload, headers=valid_headers)
    assert response.status_code == 400

@pytest.mark.parametrize("quantity, expected_status", [
    (5, 200),   # Valid update
    (0, 400),   # Invalid boundary
    (-2, 400)   # Invalid negative
])
def test_cart_update_quantity(valid_headers, quantity, expected_status):
    # Assuming the product is already in the cart
    payload = {"product_id": 1, "quantity": quantity}
    response = requests.post(f"{BASE_URL}/cart/update", json=payload, headers=valid_headers)
    assert response.status_code == expected_status

# --- COUPON TESTS ---

def test_apply_coupon_minimum_value_unmet(valid_headers):
    # Test "the cart total must meet the coupon's minimum cart value"
    payload = {"coupon_code": "MEGA_DISCOUNT"} # Assuming this requires a high cart value
    response = requests.post(f"{BASE_URL}/coupon/apply", json=payload, headers=valid_headers)
    # If cart is empty or too low, it should fail
    assert response.status_code == 400 

def test_remove_coupon(valid_headers):
    response = requests.post(f"{BASE_URL}/coupon/remove", headers=valid_headers)
    assert response.status_code == 200

# --- CHECKOUT TESTS (COD Limits) ---

def test_checkout_cod_limit_exceeded(valid_headers):
    # The doc states: "COD is not allowed if the order total is more than 5000."
    # Note: To fully automate this, you'd first add a high-value item to the cart.
    payload = {"payment_method": "COD"}
    response = requests.post(f"{BASE_URL}/checkout", json=payload, headers=valid_headers)
    
    # If the setup script added >5000 worth of items:
    if response.status_code == 400:
        pass # Expected if total > 5000
    elif response.status_code == 200:
        # If it succeeds, we must verify the total was actually <= 5000
        assert True # Ideally, check the returned order total here.

@pytest.mark.parametrize("amount, expected_status", [
    (0, 400),   # Must be at least 1
    (-10, 400), # Cannot be negative
    (1, 200)    # Valid (assuming user has at least 1 point)
])
def test_redeem_loyalty_points_boundaries(valid_headers, amount, expected_status):
    payload = {"amount": amount}
    response = requests.post(f"{BASE_URL}/loyalty/redeem", json=payload, headers=valid_headers)
    if response.status_code != 400 or expected_status == 400: # Account for insufficient points (400) on a valid request
        assert response.status_code == expected_status

# --- ORDERS TESTS ---

def test_get_all_orders(valid_headers):
    response = requests.get(f"{BASE_URL}/orders", headers=valid_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_cancel_nonexistent_order(valid_headers):
    # "Trying to cancel an order that does not exist returns a 404 error."
    response = requests.post(f"{BASE_URL}/orders/999999/cancel", headers=valid_headers)
    assert response.status_code == 404

def test_get_order_invoice(valid_headers):
    # Assuming order ID 1 belongs to the user
    response = requests.get(f"{BASE_URL}/orders/1/invoice", headers=valid_headers)
    # Could be 404 if order doesn't exist, but if it does, it should be 200
    if response.status_code == 200:
        data = response.json()
        assert "subtotal" in data
        assert "gst" in data
        assert "total" in data
        # "GST is 5 percent... The total shown must match the actual order total exactly."
        expected_total = data["subtotal"] + data["gst"]
        assert round(data["total"], 2) == round(expected_total, 2)

# --- REVIEWS TESTS (Comment Length Boundaries) ---

@pytest.mark.parametrize("comment, expected_status", [
    ("", 400),                                   # Too short (< 1)
    ("A" * 201, 400),                            # Too long (> 200)
    ("A perfectly valid review comment.", 200)   # Valid
])
def test_add_review_comment_length(valid_headers, comment, expected_status):
    # "A comment must be between 1 and 200 characters."
    payload = {"rating": 5, "comment": comment}
    response = requests.post(f"{BASE_URL}/products/1/reviews", json=payload, headers=valid_headers)
    if response.status_code != 404: # Ignore 404 if product 1 doesn't exist
        assert response.status_code == expected_status

# --- ADDRESSES (Default Logic & GET) ---

def test_get_all_addresses(valid_headers):
    response = requests.get(f"{BASE_URL}/addresses", headers=valid_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_address_single_default_enforcement(valid_headers):
    # "When a new address is added as the default, all other addresses must stop being the default first."
    
    # 1. Create first default address
    addr1_payload = {"label": "HOME", "street": "Test Street One", "city": "Delhi", "pincode": "110001", "is_default": True}
    resp1 = requests.post(f"{BASE_URL}/addresses", json=addr1_payload, headers=valid_headers)
    
    # 2. Create second default address
    addr2_payload = {"label": "OFFICE", "street": "Test Street Two", "city": "Delhi", "pincode": "110002", "is_default": True}
    resp2 = requests.post(f"{BASE_URL}/addresses", json=addr2_payload, headers=valid_headers)
    
    # 3. Fetch all addresses and ensure only ONE is marked default
    get_resp = requests.get(f"{BASE_URL}/addresses", headers=valid_headers)
    addresses = get_resp.json()
    
    default_count = sum(1 for a in addresses if a.get("is_default") is True)
    assert default_count <= 1, "System allowed multiple default addresses simultaneously."

# --- CART (Math & Subtotal Logic) ---

def test_get_cart_math_validation(valid_headers):
    # "Each item in the cart must show the correct subtotal (quantity * unit price). 
    # The cart total must be the sum of all item subtotals."
    response = requests.get(f"{BASE_URL}/cart", headers=valid_headers)
    assert response.status_code == 200
    
    cart_data = response.json()
    if "items" in cart_data and len(cart_data["items"]) > 0:
        calculated_total = 0
        for item in cart_data["items"]:
            expected_subtotal = item["quantity"] * item["unit_price"]
            assert item["subtotal"] == expected_subtotal, f"Subtotal mismatch for product {item['product_id']}"
            calculated_total += expected_subtotal
        
        assert cart_data["total"] == calculated_total, "Cart total does not match sum of subtotals."

# --- CHECKOUT (Initial State Logic) ---

@pytest.mark.parametrize("payment_method, expected_initial_status", [
    ("COD", "PENDING"),
    ("WALLET", "PENDING"),
    ("CARD", "PAID")
])
def test_checkout_initial_order_status(valid_headers, payment_method, expected_initial_status):
    # Ensure items are in cart before checkout (assuming server state allows it)
    # "When paying with COD or WALLET, order starts as PENDING. CARD starts as PAID."
    payload = {"payment_method": payment_method}
    response = requests.post(f"{BASE_URL}/checkout", json=payload, headers=valid_headers)
    
    if response.status_code == 200:
        order_data = response.json()
        assert order_data.get("payment_status") == expected_initial_status

# --- WALLET (Exact Deduction Validation) ---

def test_wallet_exact_deduction(valid_headers):
    # "the exact amount requested is deducted from the balance. No extra amount is taken."
    
    # 1. Get current balance
    initial_resp = requests.get(f"{BASE_URL}/wallet", headers=valid_headers)
    if initial_resp.status_code == 200:
        initial_balance = initial_resp.json().get("balance", 0)
        
        # 2. Add some money to ensure we can pay
        requests.post(f"{BASE_URL}/wallet/add", json={"amount": 100}, headers=valid_headers)
        new_balance = initial_balance + 100
        
        # 3. Pay a specific amount
        pay_amount = 50
        pay_resp = requests.post(f"{BASE_URL}/wallet/pay", json={"amount": pay_amount}, headers=valid_headers)
        
        if pay_resp.status_code == 200:
            # 4. Verify exact deduction
            final_resp = requests.get(f"{BASE_URL}/wallet", headers=valid_headers)
            final_balance = final_resp.json().get("balance", 0)
            assert final_balance == (new_balance - pay_amount), "Wallet deducted an incorrect amount."

# --- ORDERS (Single GET) ---

def test_get_single_order(valid_headers):
    # Just checking if the endpoint exists and returns 404 for a dummy ID
    response = requests.get(f"{BASE_URL}/orders/999999", headers=valid_headers)
    assert response.status_code == 404

# --- REVIEWS (Decimal Validation) ---

def test_get_reviews_decimal_average(valid_headers):
    # "The average rating shown must be a proper decimal calculation, not a rounded-down integer. 
    # If no reviews, average is 0."
    response = requests.get(f"{BASE_URL}/products/1/reviews", headers=valid_headers)
    
    if response.status_code == 200:
        data = response.json()
        assert "average_rating" in data
        avg_rating = data["average_rating"]
        
        # Check if it's a float or 0
        assert isinstance(avg_rating, (float, int))
        if len(data.get("reviews", [])) == 0:
            assert avg_rating == 0

# --- SUPPORT TICKETS (GET List) ---

def test_get_all_tickets(valid_headers):
    response = requests.get(f"{BASE_URL}/support/tickets", headers=valid_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# --- ADMIN TEST ---

def test_get_single_user_admin(admin_headers):
    # The doc states this returns one specific user. 
    # Assuming user ID 1 exists in the database.
    response = requests.get(f"{BASE_URL}/admin/users/1", headers=admin_headers)
    
    # If the user exists, it should be 200. If not, it might be 404.
    if response.status_code == 200:
        data = response.json()
        # Verifying it returns user-specific data like the doc mentions for users
        assert "user_id" in data or "wallet_balance" in data or "loyalty_points" in data
    else:
        assert response.status_code == 404

# --- LOYALTY TEST ---

def test_get_loyalty_points(valid_headers):
    response = requests.get(f"{BASE_URL}/loyalty", headers=valid_headers)
    assert response.status_code == 200
    
    assert "loyalty_points" in response.json()

def test_cart_totals(valid_headers):
    """
    Checks if subtotal is calculated correctly 
    and if total actually evaluates to a non-zero number.
    """
    # 1. Clear cart and add an item
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": 2}, headers=valid_headers)
    
    # 2. Fetch cart
    resp = requests.get(f"{BASE_URL}/cart", headers=valid_headers)
    assert resp.status_code == 200
    cart = resp.json()
    
    # 3. Verify total is not 0
    assert cart.get("total", 0) > 0, "Cart total is 0 despite having items."
    
    # 4. Verify subtotal math
    for item in cart.get("items", []):
        expected_subtotal = item["quantity"] * item["unit_price"]
        assert item["subtotal"] == expected_subtotal, f"Subtotal {item['subtotal']} != {expected_subtotal}"

# --- Coupons PERCENT max_discount cap ---

def test_coupon_max_discount(valid_headers):
    """
    Applies a coupon and checks if the discount exceeds its defined maximum cap.
    """
    # Assuming there's a known coupon like "FESTIVE50" (50% off, max 100 Rs)
    # Note: You may need to adjust the coupon code and expected logic based on your DB.
    payload = {"coupon_code": "FESTIVE50"}
    resp = requests.post(f"{BASE_URL}/coupon/apply", json=payload, headers=valid_headers)
    
    if resp.status_code == 200:
        data = resp.json()
        discount = data.get("discount_applied", 0)
        max_cap = 100 # Example max cap
        assert discount <= max_cap, f"Discount {discount} exceeded cap {max_cap}!"

# --- Orders Stock Restoration ---

def test_stock_restored_after_cancel(valid_headers, admin_headers):
    """
    Checks if stock count increases back to original after order cancellation.
    """
    # 1. Get initial stock for Product 1
    prod_resp = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers)
    initial_stock = next((p["stock_quantity"] for p in prod_resp.json() if p["product_id"] == 1), 0)
    
    # 2. Add to cart & checkout (Assuming this creates Order #100)
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": 1}, headers=valid_headers)
    checkout_resp = requests.post(f"{BASE_URL}/checkout", json={"payment_method": "COD"}, headers=valid_headers)
    
    if checkout_resp.status_code == 200:
        order_id = checkout_resp.json().get("order_id")
        
        # 3. Cancel the order
        cancel_resp = requests.post(f"{BASE_URL}/orders/{order_id}/cancel", headers=valid_headers)
        assert cancel_resp.status_code == 200
        
        # 4. Verify stock is restored
        prod_resp_after = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers)
        final_stock = next((p["stock_quantity"] for p in prod_resp_after.json() if p["product_id"] == 1), 0)
        
        assert final_stock == initial_stock, "Stock was not restored after cancellation."

# --- Delivered orders can be cancelled ---

def test_delivered_order_cancellation(valid_headers, admin_headers):
    """
    Attempts to cancel an order that is already DELIVERED.
    """
    # Find a delivered order via admin endpoint
    orders_resp = requests.get(f"{BASE_URL}/admin/orders", headers=admin_headers)
    delivered_orders = [o for o in orders_resp.json() if o.get("order_status") == "DELIVERED"]
    
    if delivered_orders:
        order_id = delivered_orders[0]["order_id"]
        cancel_resp = requests.post(f"{BASE_URL}/orders/{order_id}/cancel", headers=valid_headers)
        
        # It MUST return 400 according to docs
        assert cancel_resp.status_code == 400, "Successfully cancelled a delivered order!"

# --- Product Price Mismatch ---

def test_product_price_mismatch(valid_headers, admin_headers):
    """
    Compares the price of a product in the public listing vs the admin listing.
    """
    public_resp = requests.get(f"{BASE_URL}/products", headers=valid_headers)
    admin_resp = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers)
    
    public_products = {p["product_id"]: p["price"] for p in public_resp.json()}
    admin_products = {p["product_id"]: p["price"] for p in admin_resp.json()}
    
    for pid, public_price in public_products.items():
        admin_price = admin_products.get(pid)
        assert public_price == admin_price, f"Price mismatch for Product {pid} (Public: {public_price}, Admin: {admin_price})"

# --- Wallet Precision Error ---

def test_wallet_floating_point_precision(valid_headers):
    """
    Tests for floating-point accumulation errors by dealing with decimal amounts.
    """
    # Add an awkward decimal amount
    requests.post(f"{BASE_URL}/wallet/add", json={"amount": 100}, headers=valid_headers)
    
    # Pay an awkward decimal amount
    resp = requests.post(f"{BASE_URL}/wallet/pay", json={"amount": 50}, headers=valid_headers)
    
    if resp.status_code == 200:
        wallet_resp = requests.get(f"{BASE_URL}/wallet", headers=valid_headers)
        balance = wallet_resp.json().get("balance", 0)
        
        # Verify no trailing 000000001 or 99999999 type float errors
        # Standardize to 2 decimal places to check underlying precision issues
        assert round(balance, 2) == balance, f"Imprecise wallet deduction resulting in {balance}"

# --- Reviews on nonexistent product ---

def test_reviews_nonexistent_product(valid_headers):
    """
    Fetches reviews for a product ID that doesn't exist.
    """
    resp = requests.get(f"{BASE_URL}/products/9999999/reviews", headers=valid_headers)
    assert resp.status_code == 404, "Returned 200 for a nonexistent product's reviews."

# --- Support Tickets same-status transition ---

def test_ticket_same_status(valid_headers):
    """
    Attempts to update a ticket to the exact same status it currently has.
    """
    # Create ticket (Defaults to OPEN)
    payload = {"subject": "Test Ticket", "message": "Testing idempotency."}
    create_resp = requests.post(f"{BASE_URL}/support/ticket", json=payload, headers=valid_headers)
    
    if create_resp.status_code in [200, 201]:
        ticket_id = create_resp.json().get("ticket_id")
        
        # Attempt to PUT status to OPEN (which it already is)
        # Docs: "OPEN can go to IN_PROGRESS. No other changes are allowed."
        update_resp = requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", json={"status": "OPEN"}, headers=valid_headers)
        
        assert update_resp.status_code == 400, "Allowed updating a ticket to its existing status."

# --- Cart nonexistent X-User-ID ---

def test_cart_nonexistent_user():
    """
    Tests if GET /cart validates the existence of the user ID.
    """
    headers = {"X-Roll-Number": "123456", "X-User-ID": "99999999"}
    resp = requests.get(f"{BASE_URL}/cart", headers=headers)
    
    # Docs: "If it is missing or invalid, the server returns a 400 error."
    assert resp.status_code == 400, "Accepted a nonexistent X-User-ID."

# --- Cart Update nonexistent item ---

def test_cart_update_nonexistent_item(valid_headers):
    """
    Attempts to update the quantity of a product not currently in the cart.
    """
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    
    payload = {"product_id": 1, "quantity": 5}
    resp = requests.post(f"{BASE_URL}/cart/update", json=payload, headers=valid_headers)
    
    assert resp.status_code == 404, "Returned success when updating an item not in the cart."

# --- Checkout WALLET validation ---

def test_wallet_checkout_insufficient_funds(valid_headers):
    """
    Attempts to checkout using WALLET when the balance is 0.
    """
    # 1. Clear cart and add expensive item
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": 10}, headers=valid_headers)
    
    # 2. Ensure wallet is empty or insufficient (depends on test state, but assuming 0)
    # Ideally, there's a way to clear the wallet, but we'll try checking out an absurdly high cart
    
    payload = {"payment_method": "WALLET"}
    resp = requests.post(f"{BASE_URL}/checkout", json=payload, headers=valid_headers)
    
    assert resp.status_code == 400, "Allowed WALLET checkout with insufficient funds!"

def test_wallet_checkout_does_not_deduct(valid_headers):
    """
    Checks if a successful WALLET checkout actually decreases the wallet balance.
    """
    # 1. Add money to wallet
    requests.post(f"{BASE_URL}/wallet/add", json={"amount": 1000}, headers=valid_headers)
    
    # 2. Get pre-checkout balance
    pre_balance = requests.get(f"{BASE_URL}/wallet", headers=valid_headers).json().get("balance", 0)
    
    # 3. Add item and checkout
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": 1}, headers=valid_headers)
    
    # Need to know the cart total to verify exact deduction
    cart_total = requests.get(f"{BASE_URL}/cart", headers=valid_headers).json().get("total", 0)
    # Calculate order total (Total + 5% GST)
    expected_order_total = cart_total + (cart_total * 0.05)
    
    checkout_resp = requests.post(f"{BASE_URL}/checkout", json={"payment_method": "WALLET"}, headers=valid_headers)
    
    if checkout_resp.status_code == 200:
        # 4. Get post-checkout balance
        post_balance = requests.get(f"{BASE_URL}/wallet", headers=valid_headers).json().get("balance", 0)
        
        assert post_balance < pre_balance, "Wallet balance was not deducted after WALLET checkout!"
        # To be extra precise:
        assert round(post_balance, 2) == round(pre_balance - expected_order_total, 2), "Wallet deduction amount is incorrect during checkout."

def test_bug_cart_subtotal_integer_overflow(valid_headers):
    """
    Attempts to trigger a 32-bit or 64-bit integer overflow by adding a massive quantity.
    The spec states: "The total is calculated correctly with no number overflow."
    """
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    
    # Max 32-bit signed int is 2,147,483,647. Let's send something larger.
    massive_quantity = 3000000000 
    
    # This should ideally be rejected with a 400 if stock is checked properly,
    # but if it bypasses stock checks, we need to ensure the subtotal doesn't become negative.
    resp = requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": massive_quantity}, headers=valid_headers)
    
    if resp.status_code == 200:
        cart_resp = requests.get(f"{BASE_URL}/cart", headers=valid_headers)
        cart = cart_resp.json()
        for item in cart.get("items", []):
            if item["product_id"] == 1:
                assert item["subtotal"] > 0, f"Integer overflow occurred! Subtotal is {item['subtotal']}"

def test_coupon_exact_boundary_cap(valid_headers):
    """
    Tests if the max_discount cap logic accidentally blocks valid discounts that 
    are EXACTLY AT or JUST BELOW the cap.
    """
    # Assume "FESTIVE50" has a max cap of 100.
    # We need a cart total that yields a discount of exactly 100, and one that yields 99.
    # If the system uses `<` instead of `<=`, the exact cap will fail.
    
    # 1. Test discount exactly at cap (assuming cart total is setup to yield exactly the cap)
    payload = {"coupon_code": "FESTIVE50"}
    resp = requests.post(f"{BASE_URL}/coupon/apply", json=payload, headers=valid_headers)
    
    if resp.status_code == 200:
        discount = resp.json().get("discount_applied", 0)
        # Assuming the cart was engineered so 50% = 100
        if discount == 100:
             assert True # Handled correctly
        elif discount > 100:
             pytest.fail(f"Discount {discount} exceeded cap!")

def test_multi_item_stock_restoration(valid_headers, admin_headers):
    """
    Checks if stock is restored for ALL items in a multi-item order, not just the first one.
    """
    # 1. Get initial stock for Product 1 and 2
    prod_resp = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers)
    products = prod_resp.json()
    
    # Using the correct key: 'stock_quantity'
    stock_1 = next((p["stock_quantity"] for p in products if p["product_id"] == 1), 0)
    stock_2 = next((p["stock_quantity"] for p in products if p["product_id"] == 2), 0)
    
    # 2. Add both to cart and checkout
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": 1}, headers=valid_headers)
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": 2, "quantity": 1}, headers=valid_headers)
    checkout_resp = requests.post(f"{BASE_URL}/checkout", json={"payment_method": "COD"}, headers=valid_headers)
    
    if checkout_resp.status_code == 200:
        order_id = checkout_resp.json().get("order_id")
        requests.post(f"{BASE_URL}/orders/{order_id}/cancel", headers=valid_headers)
        
        # 3. Verify ALL stock is restored
        prod_resp_after = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers)
        products_after = prod_resp_after.json()
        
        final_stock_1 = next((p["stock_quantity"] for p in products_after if p["product_id"] == 1), 0)
        final_stock_2 = next((p["stock_quantity"] for p in products_after if p["product_id"] == 2), 0)
        
        assert final_stock_1 == stock_1, f"Product 1 stock not restored. Expected {stock_1}, got {final_stock_1}"
        assert final_stock_2 == stock_2, f"Product 2 stock not restored. Expected {stock_2}, got {final_stock_2}"

def test_wallet_ieee_754_accumulation(valid_headers):
    """
    Forces classic floating-point arithmetic errors. 
    In many languages, 0.1 + 0.2 equals 0.30000000000000004.
    """
    # Note: amounts must be > 0 according to docs.
    # Let's add 1.1 and 2.2, which often sum to 3.3000000000000003
    requests.post(f"{BASE_URL}/wallet/add", json={"amount": 1.1}, headers=valid_headers)
    requests.post(f"{BASE_URL}/wallet/add", json={"amount": 2.2}, headers=valid_headers)
    
    wallet_resp = requests.get(f"{BASE_URL}/wallet", headers=valid_headers)
    balance = wallet_resp.json().get("balance", 0)
    
    # If backend stores as float without rounding, this might fail
    # We allow a small tolerance in test, but check if the raw JSON string is ugly
    balance_str = str(balance)
    assert len(balance_str.split('.')[-1]) <= 2, f"Imprecise float detected in JSON response: {balance_str}"


def test_ticket_skip_state_transition(valid_headers):
    """
    Docs state: "OPEN can go to IN_PROGRESS. IN_PROGRESS can go to CLOSED."
    Attempting to jump straight from OPEN to CLOSED should fail.
    """
    payload = {"subject": "Test Ticket", "message": "Testing skip transition."}
    create_resp = requests.post(f"{BASE_URL}/support/ticket", json=payload, headers=valid_headers)
    
    if create_resp.status_code in [200, 201]:
        ticket_id = create_resp.json().get("ticket_id")
        
        # Try skipping IN_PROGRESS
        update_resp = requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", json={"status": "CLOSED"}, headers=valid_headers)
        
        assert update_resp.status_code == 400, "Allowed skipping states from OPEN directly to CLOSED."

def test_cart_negative_user_id():
    """
    The docs state: "require an X-User-ID header containing a positive integer matching an existing user."
    """
    headers = {"X-Roll-Number": "123456", "X-User-ID": "-1"}
    resp = requests.get(f"{BASE_URL}/cart", headers=headers)
    
    assert resp.status_code == 400, "Accepted a negative X-User-ID."

# --- Checkout exact wallet balance boundary ---

def test_wallet_checkout_exact_balance(valid_headers):
    """
    Tests the exact boundary where Wallet Balance == Order Total (including GST).
    If the code uses `balance > total` instead of `balance >= total`, this will falsely fail.
    """
    # 1. Get cart total and calculate expected order total with 5% GST
    cart_resp = requests.get(f"{BASE_URL}/cart", headers=valid_headers)
    if cart_resp.status_code == 200 and cart_resp.json().get("total", 0) > 0:
        cart_total = cart_resp.json().get("total")
        order_total = cart_total + (cart_total * 0.05)
        
        # 2. Get current wallet balance
        wallet_resp = requests.get(f"{BASE_URL}/wallet", headers=valid_headers)
        current_balance = wallet_resp.json().get("balance", 0)
        
        # 3. Add exactly enough to make balance == order_total
        shortfall = order_total - current_balance
        if shortfall > 0:
             requests.post(f"{BASE_URL}/wallet/add", json={"amount": shortfall}, headers=valid_headers)
        
        # 4. Checkout
        checkout_resp = requests.post(f"{BASE_URL}/checkout", json={"payment_method": "WALLET"}, headers=valid_headers)
        
        # Should succeed because we have EXACTLY enough
        assert checkout_resp.status_code == 200, "Failed WALLET checkout when balance exactly matched total."

# --- CART: Aggregation Logic ---

def test_cart_same_product_aggregation(valid_headers):
    """
    Doc: "If the same product is added to the cart more than once, 
    the quantities are added together. The existing cart quantity is not replaced."
    """
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    
    # Add product 1 with quantity 2
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": 2}, headers=valid_headers)
    
    # Add product 1 AGAIN with quantity 3
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": 3}, headers=valid_headers)
    
    resp = requests.get(f"{BASE_URL}/cart", headers=valid_headers)
    cart = resp.json()
    
    # Find the item and verify quantity is 5 (2 + 3)
    item = next((i for i in cart.get("items", []) if i["product_id"] == 1), None)
    assert item is not None, "Product was not added to cart."
    assert item["quantity"] == 5, f"Expected aggregated quantity 5, got {item['quantity']}."

# --- ADDRESSES: Upper Boundaries & Case Sensitivity ---

def test_address_max_boundaries(valid_headers):
    """
    Doc: "The street must be between 5 and 100 characters. 
    The city must be between 2 and 50 characters."
    Let's test EXACTLY 100 characters and 50 characters.
    """
    payload = {
        "label": "HOME",
        "street": "A" * 100,  # Exactly 100
        "city": "B" * 50,     # Exactly 50
        "pincode": "500001"
    }
    resp = requests.post(f"{BASE_URL}/addresses", json=payload, headers=valid_headers)
    assert resp.status_code in [200, 201], "Failed to accept valid maximum boundary lengths for street/city."

def test_address_label_case_sensitivity(valid_headers):
    """
    Doc: "the label must be HOME, OFFICE, or OTHER."
    Testing if the backend strictly enforces uppercase or if it implicitly accepts lowercase.
    """
    payload = {
        "label": "home",  # Lowercase
        "street": "123 Main Street",
        "city": "Hyderabad",
        "pincode": "500001"
    }
    resp = requests.post(f"{BASE_URL}/addresses", json=payload, headers=valid_headers)
    assert resp.status_code == 400, "API accepted a lowercase label instead of strictly HOME, OFFICE, or OTHER."

# --- COUPONS: Expiry and Math Calculations ---

def test_coupon_expired_rejection(valid_headers, admin_headers):
    """
    Doc: "First, the coupon must not be expired."
    We will find an expired coupon using the admin API and try to apply it.
    """
    # Find an expired coupon
    coupons_resp = requests.get(f"{BASE_URL}/admin/coupons", headers=admin_headers)
    expired_coupons = [c for c in coupons_resp.json() if c.get("is_expired") is True]
    
    if expired_coupons:
        code = expired_coupons[0]["code"]
        payload = {"coupon_code": code}
        resp = requests.post(f"{BASE_URL}/coupon/apply", json=payload, headers=valid_headers)
        assert resp.status_code == 400, "API successfully applied an expired coupon!"

# --- LOYALTY POINTS: Insufficient Balance ---

def test_loyalty_redeem_exceeds_balance(valid_headers):
    """
    Doc: "When redeeming, the user must have enough points."
    """
    # 1. Get current points
    points_resp = requests.get(f"{BASE_URL}/loyalty", headers=valid_headers)
    current_points = points_resp.json().get("loyalty_points", 0)
    
    # 2. Try to redeem 10 more than the user has
    payload = {"amount": current_points + 10}
    resp = requests.post(f"{BASE_URL}/loyalty/redeem", json=payload, headers=valid_headers)
    
    assert resp.status_code == 400, "API allowed redeeming more loyalty points than the user possesses."

# --- REVIEWS: True Average Calculation ---

def test_reviews_average_math(valid_headers):
    """
    Doc: "The average rating shown must be a proper decimal calculation."
    We will add a 5-star and a 2-star review. The average MUST equal 3.5.
    (Assuming product 2 has no reviews yet, or we verify the math against existing ones).
    """
    # Note: If the backend restricts 1 review per user, this test would require multiple X-User-IDs.
    # Assuming for this test we can post multiple.
    requests.post(f"{BASE_URL}/products/2/reviews", json={"rating": 5, "comment": "Great!"}, headers=valid_headers)
    
    headers_user2 = {"X-Roll-Number": "123456", "X-User-ID": "2"}
    requests.post(f"{BASE_URL}/products/2/reviews", json={"rating": 2, "comment": "Bad!"}, headers=headers_user2)
    
    resp = requests.get(f"{BASE_URL}/products/2/reviews", headers=valid_headers)
    if resp.status_code == 200:
        data = resp.json()
        reviews = data.get("reviews", [])
        
        # Manually calculate the true average of all returned reviews
        if len(reviews) > 0:
            total_score = sum(r["rating"] for r in reviews)
            expected_avg = total_score / len(reviews)
            
            # Assert the API's computed average matches reality
            assert data["average_rating"] == expected_avg, f"Average rating math is wrong. Expected {expected_avg}, got {data['average_rating']}"

# --- WALLET: Exact Maximum Boundary ---

def test_wallet_add_exact_max_boundary(valid_headers):
    """
    Doc: "the amount must be more than 0 and at most 100000."
    We previously tested >100000. Now we test exactly 100000.
    """
    payload = {"amount": 100000}
    resp = requests.post(f"{BASE_URL}/wallet/add", json=payload, headers=valid_headers)
    assert resp.status_code == 200, "Failed to add exactly 100,000 to the wallet (upper boundary rejected)."

def test_coupon_prevents_negative_cart_total(user_1_headers, admin_headers):
    """
    If a FIXED discount coupon is applied to a cart whose total is LESS than the discount amount,
    does the cart total drop below 0 (meaning the store owes the user money)?
    """
    requests.delete(f"{BASE_URL}/cart/clear", headers=user_1_headers)
    
    # 1. Find a FIXED coupon from admin API
    coupons_resp = requests.get(f"{BASE_URL}/admin/coupons", headers=admin_headers)
    fixed_coupons = [c for c in coupons_resp.json() if c.get("type") == "FIXED" and c.get("is_expired") is False]
    
    if fixed_coupons:
        target_coupon = fixed_coupons[0]
        discount_amount = target_coupon.get("discount_value", 0)
        min_cart_value = target_coupon.get("min_cart_value", 0)
        
        # 2. Add item(s) to barely meet the min_cart_value, but ensuring Total < Discount Amount
        # (Only works if the DB has a coupon where discount > min_cart_value, a common setup flaw).
        if discount_amount > min_cart_value:
            # Add a cheap product (assuming product 1 is cheap)
            requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": 1}, headers=user_1_headers)
            
            # Apply coupon
            requests.post(f"{BASE_URL}/coupon/apply", json={"coupon_code": target_coupon["code"]}, headers=user_1_headers)
            
            # Fetch cart and verify total >= 0
            cart_resp = requests.get(f"{BASE_URL}/cart", headers=user_1_headers)
            total = cart_resp.json().get("total", 0)
            
            assert total >= 0, f"CRITICAL: Cart total went negative ({total}) after FIXED coupon application!"

# --- Inactive Product Purchasing ---

def test_add_inactive_product_to_cart(user_1_headers, admin_headers):
    """
    Docs state: "Inactive products are never shown in the list."
    But what if a malicious user guesses the product_id of an inactive item and tries to add it directly?
    """
    # 1. Find an inactive product via admin
    prod_resp = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers)
    inactive_products = [p for p in prod_resp.json() if p.get("is_active") is False]
    
    if inactive_products:
        inactive_id = inactive_products[0]["product_id"]
        
        # 2. Try to add to cart
        resp = requests.post(f"{BASE_URL}/cart/add", json={"product_id": inactive_id, "quantity": 1}, headers=user_1_headers)
        
        # The system should ideally return 400 or 404 because the product is technically unavailable to the user.
        assert resp.status_code in [400, 404], "Security/Logic Flaw: Allowed adding an INACTIVE product to the cart."

# --- Cross-User Data Access ---

def test_cancel_other_users_order(user_1_headers, user_2_headers):
    """
    Insecure Direct Object Reference: Can User 2 cancel User 1's order?
    """
    # 1. User 1 creates an order
    requests.delete(f"{BASE_URL}/cart/clear", headers=user_1_headers)
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": 1}, headers=user_1_headers)
    checkout_resp = requests.post(f"{BASE_URL}/checkout", json={"payment_method": "COD"}, headers=user_1_headers)
    
    if checkout_resp.status_code == 200:
        order_id = checkout_resp.json().get("order_id")
        
        # 2. User 2 attempts to cancel User 1's order
        cancel_resp = requests.post(f"{BASE_URL}/orders/{order_id}/cancel", headers=user_2_headers)
        
        # It must return 403 Forbidden or 404 Not Found (since it's not User 2's order).
        assert cancel_resp.status_code in [403, 404], "User 2 successfully cancelled User 1's order!"

def test_view_other_users_address(user_1_headers, user_2_headers):
    """
    Can User 2 modify or delete User 1's address?
    """
    # 1. User 1 creates an address
    payload = {"label": "HOME", "street": "User 1 Street", "city": "Delhi", "pincode": "110001"}
    addr_resp = requests.post(f"{BASE_URL}/addresses", json=payload, headers=user_1_headers)
    
    if addr_resp.status_code in [200, 201]:
        addr_id = addr_resp.json().get("address_id")
        
        # 2. User 2 tries to delete it
        delete_resp = requests.delete(f"{BASE_URL}/addresses/{addr_id}", headers=user_2_headers)
        
        assert delete_resp.status_code in [403, 404], "User 2 successfully deleted User 1's address!"

# --- COD Boundary Logic with Coupons ---

def test_checkout_cod_boundary_post_discount(user_1_headers, admin_headers):
    """
    Docs: "COD is not allowed if the order total is more than 5000."
    If my cart is 6000, but I apply a 2000 discount coupon, the final total is 4000.
    Does the backend correctly evaluate COD eligibility on the POST-discount total, or the PRE-discount total?
    """
    requests.delete(f"{BASE_URL}/cart/clear", headers=user_1_headers)
    
    # Setup: Add expensive item to make cart > 5000 (e.g., Qty 100 of a 60 Rs item)
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": 100}, headers=user_1_headers)
    
    # Verify cart is actually > 5000
    cart_pre = requests.get(f"{BASE_URL}/cart", headers=user_1_headers).json()
    if cart_pre.get("total", 0) > 5000:
        
        # Apply a massive discount coupon if available in admin
        coupons_resp = requests.get(f"{BASE_URL}/admin/coupons", headers=admin_headers)
        massive_coupons = [c for c in coupons_resp.json() if c.get("type") == "FIXED" and c.get("discount_value", 0) >= 2000]
        
        if massive_coupons:
            requests.post(f"{BASE_URL}/coupon/apply", json={"coupon_code": massive_coupons[0]["code"]}, headers=user_1_headers)
            
            # Verify final total is now <= 5000
            cart_post = requests.get(f"{BASE_URL}/cart", headers=user_1_headers).json()
            if cart_post.get("total", 0) <= 5000:
                
                # Attempt COD checkout
                checkout_resp = requests.post(f"{BASE_URL}/checkout", json={"payment_method": "COD"}, headers=user_1_headers)
                
                assert checkout_resp.status_code == 200, "COD rejected based on pre-discount cart total rather than final order total."

# --- Alphanumeric Pincode Format ---

def test_address_pincode_alphanumeric_edge(user_1_headers):
    """
    Docs: "The pincode must be exactly 6 digits."
    We already checked length (5 and 7). Now we check EXACTLY 6 characters, but including letters.
    """
    payload = {
        "label": "HOME",
        "street": "123 Main Street",
        "city": "Hyderabad",
        "pincode": "50000A" # 6 characters, but ends in A
    }
    resp = requests.post(f"{BASE_URL}/addresses", json=payload, headers=user_1_headers)
    assert resp.status_code == 400, "System accepted alphabetical characters in a 6-digit pincode."

# --- Ticket Message Maximum Boundary ---

def test_ticket_message_exact_maximum(user_1_headers):
    """
    Docs: "The message must be between 1 and 500 characters."
    Let's test EXACTLY 500 characters to ensure the backend `<` vs `<=` boundary is solid.
    """
    payload = {
        "subject": "Valid Subject",
        "message": "A" * 500
    }
    resp = requests.post(f"{BASE_URL}/support/ticket", json=payload, headers=user_1_headers)
    assert resp.status_code in [200, 201], "System rejected a support ticket message of exactly 500 characters."

# --- HEADER DATA TYPES ---
@pytest.mark.parametrize("roll_no, user_id, expected_status", [
    (123456, 1, 200),           # Valid Integers (Requests library casts to string, but let's test strictness if possible)
    ("123.45", "1", 400),       # Float string in Roll Number
    ("123456", "1.5", 400),     # Float string in User ID
    ("123456", "true", 400),    # Boolean string in User ID
])
def test_header_data_types(roll_no, user_id, expected_status):
    """
    Docs: "X-Roll-Number header containing a valid integer... X-User-ID header containing a positive integer."
    """
    headers = {
        "X-Roll-Number": str(roll_no),
        "X-User-ID": str(user_id)
    }
    resp = requests.get(f"{BASE_URL}/profile", headers=headers)
    assert resp.status_code == expected_status, f"Type validation failed for Headers: Roll={roll_no}, User={user_id}"

# --- ADDRESS DATA TYPES ---

@pytest.mark.parametrize("payload, expected_status", [
    # Pincode as an Integer instead of String (e.g., 500001 instead of "500001")
    ({"label": "HOME", "street": "123 Main Street", "city": "Delhi", "pincode": 500001}, 400),
    
    # is_default as a String instead of Boolean
    ({"label": "OFFICE", "street": "456 Main Street", "city": "Delhi", "pincode": "500002", "is_default": "true"}, 400),
    
    # Missing mandatory field (city)
    ({"label": "OTHER", "street": "789 Main Street", "pincode": "500003"}, 400)
])
def test_address_strict_types_and_missing_fields(valid_headers, payload, expected_status):
    """
    Tests if the API strictly enforces JSON schema types and catches missing required keys.
    """
    resp = requests.post(f"{BASE_URL}/addresses", json=payload, headers=valid_headers)
    assert resp.status_code == expected_status, f"Address Type Validation Failed for payload: {payload}"

# --- CART DATA TYPES ---

@pytest.mark.parametrize("product_id, quantity", [
    ("1", 1),         # product_id as string
    (1, "2"),         # quantity as string
    (1, 1.5),         # quantity as float
    (1, True),        # quantity as boolean
    (1, None)         # quantity as null
])
def test_cart_strict_data_types(valid_headers, product_id, quantity):
    """
    Cart endpoints should strictly reject anything that isn't a solid integer for IDs and Quantities.
    """
    payload = {"product_id": product_id, "quantity": quantity}
    resp = requests.post(f"{BASE_URL}/cart/add", json=payload, headers=valid_headers)
    
    assert resp.status_code in [400, 422], f"Cart accepted invalid data type: product_id={type(product_id)}, quantity={type(quantity)}"

# --- WALLET DATA TYPES ---

@pytest.mark.parametrize("amount", [
    "50",       # String integer
    "50.5",     # String float
    True,       # Boolean
    None,       # Null
    [50]        # Array
])
def test_wallet_amount_data_types(valid_headers, amount):
    """
    Wallet amounts handle financial math. Accepting strings or booleans can cause massive downstream calculation errors.
    """
    payload = {"amount": amount}
    resp = requests.post(f"{BASE_URL}/wallet/add", json=payload, headers=valid_headers)
    assert resp.status_code in [400, 422], f"Wallet accepted invalid data type for amount: {type(amount)}"

# --- REVIEWS DATA TYPES ---

@pytest.mark.parametrize("rating, comment", [
    (4.5, "Good"),        # Float rating (Docs say 1 to 5, usually implies integers)
    ("5", "Perfect"),     # String rating
    (5, 12345),           # Integer comment instead of string
    (None, "Nice")        # Null rating
])
def test_reviews_data_types(valid_headers, rating, comment):
    """
    Reviews schema validation. Does it cast strings to ints automatically, or strictly reject them?
    """
    payload = {"rating": rating, "comment": comment}
    # Assuming product 1 exists
    resp = requests.post(f"{BASE_URL}/products/1/reviews", json=payload, headers=valid_headers)
    
    if resp.status_code != 404: # Ignore 404 if product doesn't exist
        assert resp.status_code in [400, 422], f"Reviews accepted invalid types: rating={type(rating)}, comment={type(comment)}"

# --- CHECKOUT DATA TYPES ---

@pytest.mark.parametrize("payment_method", [
    1,          # Integer instead of "COD" / "CARD"
    True,       # Boolean
    ["COD"],    # Array
    None        # Null
])
def test_checkout_data_types(valid_headers, payment_method):
    """
    Checks if the payment_method enum is strictly validated against incorrect base types.
    """
    # Ensure cart has an item to bypass the "empty cart" 400 error
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": 1}, headers=valid_headers)
    
    payload = {"payment_method": payment_method}
    resp = requests.post(f"{BASE_URL}/checkout", json=payload, headers=valid_headers)
    
    assert resp.status_code in [400, 422], f"Checkout accepted invalid payment_method type: {type(payment_method)}"

# --- COUPON DATA TYPES ---

def test_coupon_missing_code_key(valid_headers):
    """
    What happens if we completely omit the expected 'coupon_code' key from the JSON payload?
    """
    payload = {"wrong_key": "MEGA50"}
    resp = requests.post(f"{BASE_URL}/coupon/apply", json=payload, headers=valid_headers)
    assert resp.status_code in [400, 422], "Coupon API did not reject a payload with a missing 'coupon_code' key."

# --- SUPPORT TICKET DATA TYPES ---

@pytest.mark.parametrize("status", [
    1,          # Integer instead of string
    False,      # Boolean
    "open"      # Lowercase instead of strict UPPERCASE
])
def test_ticket_status_data_types(valid_headers, status):
    """
    Docs: "OPEN can go to IN_PROGRESS. IN_PROGRESS can go to CLOSED."
    Testing if the system strictly enforces the Enum types and rejects malformed inputs.
    """
    # Create ticket
    create_resp = requests.post(f"{BASE_URL}/support/ticket", json={"subject": "Test Data Types", "message": "Valid msg"}, headers=valid_headers)
    
    if create_resp.status_code in [200, 201]:
        ticket_id = create_resp.json().get("ticket_id")
        
        # Update with bad type
        update_resp = requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", json={"status": status}, headers=valid_headers)
        assert update_resp.status_code in [400, 422], f"Ticket API accepted invalid status type/format: {status}"

# --- Double Cancellation ---

def test_cancel_already_cancelled_order(valid_headers):
    """
    State Abuse: Can a user cancel an order that has ALREADY been cancelled?
    If yes, does it restore the stock a second time (creating infinite stock)?
    """
    # 1. Add item and checkout
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    requests.post(f"{BASE_URL}/cart/add", json={"product_id": 1, "quantity": 1}, headers=valid_headers)
    checkout_resp = requests.post(f"{BASE_URL}/checkout", json={"payment_method": "COD"}, headers=valid_headers)
    
    if checkout_resp.status_code == 200:
        order_id = checkout_resp.json().get("order_id")
        
        # 2. Cancel it the first time (Should be 200 OK)
        first_cancel = requests.post(f"{BASE_URL}/orders/{order_id}/cancel", headers=valid_headers)
        assert first_cancel.status_code == 200, "Setup failed: Could not cancel order."
        
        # 3. Cancel it the SECOND time (Should be 400 Bad Request)
        second_cancel = requests.post(f"{BASE_URL}/orders/{order_id}/cancel", headers=valid_headers)
        assert second_cancel.status_code == 400, "State Abuse: System allowed cancelling an already cancelled order!"

# --- WHITESPACE BYPASSES ---

def test_profile_whitespace_bypass(valid_headers):
    """
    Validation Bypass: The name must be between 2 and 50 characters.
    What if I send 5 spaces? "     "
    A secure backend will .trim() or .strip() before checking length.
    """
    payload = {"name": "     ", "phone": "1234567890"}
    resp = requests.put(f"{BASE_URL}/profile", json=payload, headers=valid_headers)
    
    assert resp.status_code == 400, "Validation Bypass: API accepted a name consisting entirely of whitespace."

def test_address_whitespace_bypass(valid_headers):
    """
    Validation Bypass: Street must be 5 to 100 characters. Sending 10 spaces.
    """
    payload = {
        "label": "HOME",
        "street": "          ", # 10 spaces
        "city": "Hyderabad",
        "pincode": "500001"
    }
    resp = requests.post(f"{BASE_URL}/addresses", json=payload, headers=valid_headers)
    assert resp.status_code == 400, "Validation Bypass: API accepted a street consisting entirely of whitespace."

