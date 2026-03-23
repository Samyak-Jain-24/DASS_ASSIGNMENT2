# QuickCart Black-Box Testing Comprehensive Report

**Course/Assignment:** Black-Box API Testing

**System Under Test:** QuickCart REST API

**Base URL:** `http://localhost:8080`

**Default Headers Used:**
- `X-Roll-Number: 2024101062`
- `X-User-ID: 1`

**Note:** Some tests intentionally omit or modify headers; those are explicitly listed in each case.

---

## Test Cases (Detailed, Per Test)

### `test_admin.py`

#### `test_admin_users_list`
- **Input:** `GET /api/v1/admin/users` with valid admin headers.
- **Expected Output:** `200` with a JSON array of user objects.
- **Justification:** Confirms admin listing is available and returns the correct list structure, which is foundational for admin workflows.

#### `test_admin_users_get`
- **Input:** `GET /api/v1/admin/users/{user_id}` using the first user from the admin list (skip if empty).
- **Expected Output:** `200` with keys `user_id`, `wallet_balance`, and `loyalty_points`.
- **Justification:** Ensures admin can retrieve user details and that wallet/loyalty fields exist for downstream validations.

#### `test_admin_users_missing`
- **Input:** `GET /api/v1/admin/users/99999999`.
- **Expected Output:** `404` or `400`.
- **Justification:** Validates missing-resource handling to prevent false-positive user lookups.

#### `test_admin_products_list`
- **Input:** `GET /api/v1/admin/products`.
- **Expected Output:** `200` with a JSON array of products.
- **Justification:** Provides authoritative product data used to verify public catalog, cart, and checkout behavior.

#### `test_missing_roll_header`
- **Input:** `GET /api/v1/admin/users` without `X-Roll-Number`.
- **Expected Output:** `401`.
- **Justification:** Confirms mandatory global header enforcement for protected endpoints.

#### `test_invalid_roll_header`
- **Input:** `GET /api/v1/admin/users` with `X-Roll-Number: abc`.
- **Expected Output:** `400`.
- **Justification:** Ensures strict header type validation to prevent malformed identifiers.

---

### `test_products_cart.py`

#### `test_products_list_only_active`
- **Input:** `GET /api/v1/products`; compare with `GET /api/v1/admin/products`.
- **Expected Output:** No inactive product IDs appear in the public list.
- **Justification:** Validates catalog visibility rules and prevents users from seeing disabled inventory.

#### `test_add_inactive_product_to_cart`
- **Input:** `POST /api/v1/cart/add` with an inactive product ID (skip if none).
- **Expected Output:** `400` or `404`.
- **Justification:** Ensures inactive products cannot be purchased, protecting business rules and inventory integrity.

#### `test_products_get`
- **Input:** `GET /api/v1/products/{product_id}` for an active product.
- **Expected Output:** `200` and response `product_id` matches.
- **Justification:** Verifies product detail retrieval and ID consistency used in cart operations.

#### `test_products_get_missing`
- **Input:** `GET /api/v1/products/99999999`.
- **Expected Output:** `404`.
- **Justification:** Confirms correct error handling for missing products.

#### `test_products_filter_search_sort`
- **Input:** `GET /api/v1/products` with `category`, `search`, `sort=price_asc`, `sort=price_desc` (skip where not applicable).
- **Expected Output:** Category filter matches, search term appears in names, prices are sorted per parameter.
- **Justification:** Validates query logic and ordering essential for product discovery UX.

#### `test_product_price_consistency`
- **Input:** Compare admin `price` with public `GET /api/v1/products/{id}` (skip if no admin price).
- **Expected Output:** Prices match exactly.
- **Justification:** Ensures public pricing is consistent with admin configuration and prevents billing inconsistencies.

#### `test_cart_add_update_remove`
- **Input:** Clear cart; add product with qty 1 then qty 2; fetch cart; update quantity to 1; remove item.
- **Expected Output:** All mutations return `200`; quantity aggregates to 3; subtotal and total arithmetic consistent.
- **Justification:** Exercises full cart lifecycle and validates monetary arithmetic, a high-risk area for defects.

#### `test_cart_invalid_quantity`
- **Input:** Add quantity 0, -1, and "one"; update quantity to 0.
- **Expected Output:** `400` (or `422` for invalid types).
- **Justification:** Ensures quantity bounds and types are enforced to prevent invalid cart state.

#### `test_cart_missing_fields`
- **Input:** Add without `product_id`, without `quantity`, and with empty payload.
- **Expected Output:** `400` or `422`.
- **Justification:** Validates required fields to prevent incomplete cart entries.

#### `test_cart_invalid_types`
- **Input:** Add with `product_id: "abc"` and with `quantity: "2"`.
- **Expected Output:** `400` or `422`.
- **Justification:** Ensures strict type validation for cart payloads.

#### `test_cart_invalid_types_extended`
- **Input:** Add with `quantity: null`, `true`, or `1.5`.
- **Expected Output:** `400` or `422`.
- **Justification:** Rejects ambiguous or non-integer quantities that could corrupt totals.

#### `test_cart_add_missing_product`
- **Input:** Add with `product_id: 99999999`.
- **Expected Output:** `404`.
- **Justification:** Confirms cart cannot contain non-existent products.

#### `test_cart_update_nonexistent_item`
- **Input:** Clear cart; update a product not in cart.
- **Expected Output:** `404`.
- **Justification:** Ensures updates require existing cart items.

#### `test_cart_invalid_user_id`
- **Input:** `GET /api/v1/cart` with `X-User-ID: 99999999`.
- **Expected Output:** `400`.
- **Justification:** Validates user identity checks on cart access.

#### `test_cart_negative_user_id`
- **Input:** `GET /api/v1/cart` with `X-User-ID: -1`.
- **Expected Output:** `400`.
- **Justification:** Rejects invalid user identifiers to prevent data leakage.

#### `test_cart_update_arithmetic`
- **Input:** Add item qty 1; update to qty 3; fetch cart.
- **Expected Output:** Subtotals and totals reflect updated quantity.
- **Justification:** Detects arithmetic drift after updates that can lead to billing errors.

#### `test_cart_total_multiple_items`
- **Input:** Add two distinct products; fetch cart.
- **Expected Output:** Cart total equals sum of all line totals.
- **Justification:** Verifies aggregation logic across multiple items.

#### `test_cart_remove_missing`
- **Input:** Remove `product_id: 99999999`.
- **Expected Output:** `404`.
- **Justification:** Ensures removal requires a valid cart entry.

---

### `test_profile_addresses.py`

#### `test_user_header_required`
- **Input:** `GET /api/v1/profile` without `X-User-ID`.
- **Expected Output:** `400`.
- **Justification:** Confirms user-scoped endpoints enforce identity headers.

#### `test_user_header_invalid`
- **Input:** `GET /api/v1/profile` with `X-User-ID: abc`.
- **Expected Output:** `400`.
- **Justification:** Protects against non-numeric user IDs.

#### `test_user_header_negative_id`
- **Input:** `GET /api/v1/profile` with `X-User-ID: -1`.
- **Expected Output:** `400` or `404`.
- **Justification:** Validates lower-bound handling for user IDs.

#### `test_user_header_zero_id`
- **Input:** `GET /api/v1/profile` with `X-User-ID: 0`.
- **Expected Output:** `400` or `404`.
- **Justification:** Ensures non-positive IDs are rejected.

#### `test_user_header_unknown_id`
- **Input:** `GET /api/v1/profile` with `X-User-ID: 99999999`.
- **Expected Output:** `400` or `404`.
- **Justification:** Confirms unknown users cannot access profile data.

#### `test_profile_get`
- **Input:** `GET /api/v1/profile` with valid user.
- **Expected Output:** `200` with `name` and `phone` fields.
- **Justification:** Baseline profile read for user-facing UI and account management.

#### `test_profile_update_valid`
- **Input:** `PUT /api/v1/profile` with valid name and phone.
- **Expected Output:** `200` and updated fields echoed back.
- **Justification:** Confirms successful update path for core user data.

#### `test_profile_update_invalid_name`
- **Input:** `PUT /api/v1/profile` with name length 1 and 51.
- **Expected Output:** `400`.
- **Justification:** Enforces name length constraints and prevents invalid profile data.

#### `test_profile_update_invalid_phone`
- **Input:** `PUT /api/v1/profile` with short, alphabetic, and overlong phone values.
- **Expected Output:** `400`.
- **Justification:** Ensures phone normalization and validation are enforced.

#### `test_profile_update_wrong_types`
- **Input:** `PUT /api/v1/profile` with numeric `name` or numeric `phone`.
- **Expected Output:** `400`.
- **Justification:** Prevents schema drift and invalid serialization.

#### `test_profile_update_missing_fields`
- **Input:** `PUT /api/v1/profile` missing `name`, missing `phone`, and empty payload.
- **Expected Output:** `400` or `422`.
- **Justification:** Ensures required fields are enforced during updates.

#### `test_profile_whitespace_bypass`
- **Input:** `PUT /api/v1/profile` with whitespace-only name.
- **Expected Output:** `400`.
- **Justification:** Guards against validation bypass via whitespace.

#### `test_address_crud_flow`
- **Input:** Create address; list; update street/is_default; delete address.
- **Expected Output:** Create returns `address_id`; list includes it; update reflects new street; delete succeeds.
- **Justification:** Verifies the full address lifecycle used during checkout.

#### `test_address_update_restricted_fields`
- **Input:** Update address with `street`/`is_default` and attempt restricted `city`/`label` changes.
- **Expected Output:** `200` or `400`; if `200`, restricted fields are unchanged.
- **Justification:** Ensures immutable fields remain protected after creation.

#### `test_address_invalid_payloads`
- **Input:** Invalid label, street length 4/101, city length 1/51, pincode length 5/7 or non-digits, wrong types, and empty payload.
- **Expected Output:** `400` (or `422` for missing fields).
- **Justification:** Comprehensive coverage for address validation boundaries and schema enforcement.

#### `test_address_missing_fields_variants`
- **Input:** Missing `label`, `street`, `city`, or `pincode`.
- **Expected Output:** `400` or `422`.
- **Justification:** Confirms required fields across all missing-field combinations.

#### `test_address_max_boundaries`
- **Input:** `POST /api/v1/addresses` with street length 100 and city length 50.
- **Expected Output:** `200` or `201`.
- **Justification:** Ensures maximum accepted boundary values are permitted.

#### `test_address_label_case_sensitivity`
- **Input:** `POST /api/v1/addresses` with lowercase label.
- **Expected Output:** `400`.
- **Justification:** Validates strict enum handling.

#### `test_address_whitespace_bypass`
- **Input:** `POST /api/v1/addresses` with whitespace-only street.
- **Expected Output:** `400`.
- **Justification:** Prevents creation of invalid addresses via whitespace.

#### `test_address_delete_missing`
- **Input:** `DELETE /api/v1/addresses/99999999`.
- **Expected Output:** `404`.
- **Justification:** Ensures deletion requires an existing resource.

---

### `test_coupons_checkout.py`

#### `test_coupon_apply_invalid`
- **Input:** `POST /api/v1/coupon/apply` with invalid code.
- **Expected Output:** `400` or `404`.
- **Justification:** Ensures invalid coupons are rejected to prevent unauthorized discounts.

#### `test_coupon_apply_missing_code`
- **Input:** `POST /api/v1/coupon/apply` with empty payload.
- **Expected Output:** `400` or `422`.
- **Justification:** Validates required coupon code field.

#### `test_coupon_remove`
- **Input:** `POST /api/v1/coupon/remove`.
- **Expected Output:** `200` or `400` if no coupon applied.
- **Justification:** Confirms removal behavior in both applied and non-applied states.

#### `test_coupon_apply_if_available`
- **Input:** Apply first available admin coupon to a cart (skip if none or not applicable).
- **Expected Output:** `200` with `discount` or `total`; removal works.
- **Justification:** Validates happy-path coupon application and its effect on totals.

#### `test_coupon_apply_expired_if_available`
- **Input:** Apply an expired coupon.
- **Expected Output:** `400`.
- **Justification:** Prevents expired promotions from being used.

#### `test_coupon_min_cart_value_enforced`
- **Input:** Apply coupon when cart total is below `min_cart_value`.
- **Expected Output:** `400`.
- **Justification:** Ensures minimum spend requirements are enforced.

#### `test_coupon_max_cap_firstorder`
- **Input:** Apply `FIRSTORDER` on cart total > 1000 (skip if not feasible).
- **Expected Output:** `200`; discount does not exceed cap.
- **Justification:** Validates max discount cap on first-order coupon.

#### `test_coupon_max_cap_percent20`
- **Input:** Apply `PERCENT20` on cart total > 1000 (skip if not feasible).
- **Expected Output:** `200`; discount does not exceed cap.
- **Justification:** Enforces cap for percentage-based discounts.

#### `test_checkout_invalid_method`
- **Input:** Checkout with `payment_method: "CRYPTO"`.
- **Expected Output:** `400`.
- **Justification:** Ensures only supported payment methods are accepted.

#### `test_checkout_missing_payment_method`
- **Input:** Checkout with `{}`, `{payment_method: null}`, and `{payment_method: 123}`.
- **Expected Output:** `400`.
- **Justification:** Validates required field and type enforcement for checkout.

#### `test_checkout_empty_cart`
- **Input:** Clear cart; checkout with COD.
- **Expected Output:** `400`.
- **Justification:** Prevents checkout without items.

#### `test_checkout_valid_flow`
- **Input:** Cart with items; GST @ 5%; use COD if total ≤ 5000 else WALLET (fund wallet if needed).
- **Expected Output:** `200`; `payment_status` is `PENDING` or `PAID`.
- **Justification:** Validates successful checkout with correct payment selection logic.

#### `test_checkout_cod_limit`
- **Input:** Cart total > 5000; checkout with COD.
- **Expected Output:** `400`.
- **Justification:** Enforces COD upper limit rule.

#### `test_checkout_payment_status_mapping`
- **Input:** Checkout with CARD, COD, and WALLET (ensure wallet funds).
- **Expected Output:** CARD → `PAID`, COD → `PENDING`, WALLET → `PENDING`.
- **Justification:** Ensures consistent payment status mapping for downstream order flows.

#### `test_wallet_checkout_insufficient_funds`
- **Input:** Wallet checkout with cart total > wallet balance.
- **Expected Output:** `400`.
- **Justification:** Prevents underfunded wallet payments.

#### `test_wallet_checkout_deducts_balance`
- **Input:** Wallet checkout with sufficient funds.
- **Expected Output:** `200` (or skip if wallet checkout not allowed) and balance reduced by total.
- **Justification:** Confirms wallet balance is correctly debited on purchase.

---

### `test_orders_reviews_support.py`

#### `test_orders_list`
- **Input:** `GET /api/v1/orders`.
- **Expected Output:** `200` with a list.
- **Justification:** Verifies the order history endpoint and baseline response structure.

#### `test_order_detail_and_invoice`
- **Input:** `GET /api/v1/orders/{order_id}` and `/invoice` for first order (skip if none).
- **Expected Output:** `200` for both; invoice satisfies `subtotal + gst = total`.
- **Justification:** Ensures order details and invoice arithmetic are consistent and reliable.

#### `test_order_detail_missing`
- **Input:** `GET /api/v1/orders/99999999`.
- **Expected Output:** `404`.
- **Justification:** Confirms proper error handling for missing orders.

#### `test_cancel_already_cancelled_order`
- **Input:** Create order via checkout; cancel twice.
- **Expected Output:** First cancel `200`, second cancel `400`.
- **Justification:** Enforces idempotency rules and prevents repeated cancellation.

#### `test_cancel_restores_stock_exactly`
- **Input:** Create order with two products; cancel; compare stock before/after.
- **Expected Output:** Stock returns exactly to pre-order levels.
- **Justification:** Ensures inventory consistency after order cancellation.

#### `test_cancel_delivered_order_if_any`
- **Input:** Attempt to cancel a delivered order (skip if none).
- **Expected Output:** `400`.
- **Justification:** Ensures delivery status is terminal for cancellation.

#### `test_cancel_order_restores_stock_if_possible`
- **Input:** Cancel a cancellable order; compare stock deltas.
- **Expected Output:** Stock after cancel is not less than before.
- **Justification:** Confirms stock restoration logic for valid cancellations.

#### `test_cancel_missing_order`
- **Input:** `POST /api/v1/orders/99999999/cancel`.
- **Expected Output:** `404`.
- **Justification:** Validates proper handling for non-existent orders.

#### `test_reviews_get_and_average`
- **Input:** `GET /api/v1/products/{id}/reviews`.
- **Expected Output:** `200`; average equals computed if reviews exist, otherwise average is 0.
- **Justification:** Ensures review aggregation is correct and numerically stable.

#### `test_reviews_nonexistent_product`
- **Input:** `GET /api/v1/products/9999999/reviews`.
- **Expected Output:** `404`.
- **Justification:** Prevents review access for invalid product IDs.

#### `test_reviews_invalid_types`
- **Input:** `POST /api/v1/products/{id}/reviews` with `rating: null`.
- **Expected Output:** `400` or `422` (unless endpoint missing returns `404`).
- **Justification:** Validates payload type checking on review creation.

#### `test_reviews_invalid_rating`
- **Input:** `POST /api/v1/products/{id}/reviews` with `rating: 0`.
- **Expected Output:** `400`.
- **Justification:** Enforces minimum rating boundary.

#### `test_reviews_invalid_rating_upper`
- **Input:** `POST /api/v1/products/{id}/reviews` with `rating: 6`.
- **Expected Output:** `400`.
- **Justification:** Enforces maximum rating boundary.

#### `test_reviews_invalid_rating_type`
- **Input:** `POST /api/v1/products/{id}/reviews` with `rating: "5"`.
- **Expected Output:** `400`.
- **Justification:** Ensures rating is numeric.

#### `test_reviews_invalid_comment_length`
- **Input:** `POST /api/v1/products/{id}/reviews` with empty comment.
- **Expected Output:** `400`.
- **Justification:** Enforces minimum comment length.

#### `test_reviews_invalid_comment_max`
- **Input:** `POST /api/v1/products/{id}/reviews` with comment length 201.
- **Expected Output:** `400`.
- **Justification:** Enforces maximum comment length.

#### `test_reviews_missing_comment`
- **Input:** `POST /api/v1/products/{id}/reviews` with rating only.
- **Expected Output:** `400`.
- **Justification:** Ensures required fields are present.

#### `test_reviews_average_zero_when_none`
- **Input:** `GET /api/v1/products/{id}/reviews` for a product with zero reviews.
- **Expected Output:** `200` with `reviews: []` and `average_rating: 0`.
- **Justification:** Validates empty review behavior and default aggregation.

#### `test_support_ticket_flow`
- **Input:** Create ticket; attempt direct CLOSE; then update OPEN → IN_PROGRESS → CLOSED.
- **Expected Output:** Create `200` with status OPEN; direct CLOSE `400`; subsequent transitions `200`.
- **Justification:** Ensures support ticket state transitions are enforced.

#### `test_support_ticket_backward_transition`
- **Input:** Create ticket; set to IN_PROGRESS; attempt transition back to OPEN.
- **Expected Output:** `400`.
- **Justification:** Prevents backward state transitions.

#### `test_support_ticket_invalid_status_value`
- **Input:** Update ticket with status `REOPENED`.
- **Expected Output:** `400`.
- **Justification:** Validates allowed status enum values.

#### `test_support_ticket_closed_cannot_reopen`
- **Input:** Close ticket; attempt transition to IN_PROGRESS.
- **Expected Output:** `400`.
- **Justification:** Ensures CLOSED state is terminal.

#### `test_support_ticket_invalid_fields`
- **Input:** Create ticket with short subject/message and empty payload.
- **Expected Output:** `400`.
- **Justification:** Enforces field length requirements and required inputs.

#### `test_support_tickets_list`
- **Input:** `GET /api/v1/support/tickets`.
- **Expected Output:** `200` with a list.
- **Justification:** Confirms ticket list endpoint works and returns correct structure.

#### `test_support_ticket_update_missing`
- **Input:** `PUT /api/v1/support/tickets/99999999` with valid status.
- **Expected Output:** `404`.
- **Justification:** Ensures missing ticket updates are rejected.

---

### `test_wallet_loyalty.py`

#### `test_wallet_get`
- **Input:** `GET /api/v1/wallet`.
- **Expected Output:** `200` with `balance` field.
- **Justification:** Baseline wallet balance retrieval for checkout validation.

#### `test_wallet_add_boundaries`
- **Input:** `POST /api/v1/wallet/add` with amount 0, 100001, and `{}`.
- **Expected Output:** `400` or `422`.
- **Justification:** Ensures wallet top-up limits and required fields are enforced.

#### `test_wallet_pay_insufficient`
- **Input:** `POST /api/v1/wallet/pay` with amount 0, -1, and `balance + 1`.
- **Expected Output:** `400`.
- **Justification:** Validates insufficient funds and invalid amounts.

#### `test_wallet_pay_exact_deduction`
- **Input:** Add 10 to wallet, pay 10, then read balance.
- **Expected Output:** Final balance equals initial balance (within tolerance).
- **Justification:** Ensures wallet debit logic is exact and consistent.

#### `test_loyalty_get`
- **Input:** `GET /api/v1/loyalty`.
- **Expected Output:** `200` with `points` field.
- **Justification:** Baseline loyalty points retrieval for rewards logic.

#### `test_loyalty_redeem_invalid`
- **Input:** Redeem points 0, -1, "1", and `{}`.
- **Expected Output:** `400` or `422`.
- **Justification:** Validates type and boundary enforcement for redemption.

#### `test_loyalty_redeem_insufficient`
- **Input:** Redeem `points + 1` when points > 0 (skip if no points).
- **Expected Output:** `400`.
- **Justification:** Prevents over-redemption beyond available points.

---

## Bug Report (Appended)

### Summary
The following bugs were observed while running the black-box tests against the QuickCart API.

Headers used:
- `X-Roll-Number: 2024101062`
- `X-User-ID: 1`

---

### Bug 1: Invoice totals inconsistent
**Endpoint tested:** `GET /api/v1/orders/{order_id}/invoice`

**Request payload**
- Method: GET
- URL: `http://localhost:8080/api/v1/orders/{order_id}/invoice`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: None

**Expected result (per API spec)**
- Invoice shows subtotal, GST, and total such that `subtotal + gst = total` exactly.

**Actual result observed**
- Example: `subtotal=120`, `gst=0`, `total=0` (mismatch).

---

### Bug 2: Review average rating rounded down
**Endpoint tested:** `GET /api/v1/products/{product_id}/reviews`

**Request payload**
- Method: GET
- URL: `http://localhost:8080/api/v1/products/{product_id}/reviews`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: None

**Expected result (per API spec)**
- Average rating is a proper decimal (not rounded down).

**Actual result observed**
- Example: calculated average $3.2$ returned as $3.0$.

---

### Bug 3: Invalid support ticket status transition allowed
**Endpoint tested:** `PUT /api/v1/support/tickets/{ticket_id}`

**Request payload**
- Method: PUT
- URL: `http://localhost:8080/api/v1/support/tickets/{ticket_id}`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "status": "CLOSED" }` immediately after creation (OPEN)

**Expected result (per API spec)**
- Status must progress OPEN → IN_PROGRESS → CLOSED only; direct OPEN → CLOSED should return 400.

**Actual result observed**
- Response 200 with status `CLOSED`.

---

### Bug 4: Cart item subtotal incorrect
**Endpoint tested:** `GET /api/v1/cart`

**Request payload**
- Method: GET
- URL: `http://localhost:8080/api/v1/cart`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: None

**Expected result (per API spec)**
- Each item subtotal equals `quantity × unit_price`.

**Actual result observed**
- Example: `quantity=3`, `unit_price=120`, expected subtotal $360$ but returned `104`.

---

### Bug 5: Cart add allows quantity 0
**Endpoint tested:** `POST /api/v1/cart/add`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/cart/add`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "product_id": <valid>, "quantity": 0 }`

**Expected result (per API spec)**
- Quantity must be at least 1; invalid quantity should return 400.

**Actual result observed**
- Response 200 with message `Item added to cart`.

---

### Bug 6: Cart add missing required fields returns 404
**Endpoint tested:** `POST /api/v1/cart/add`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/cart/add`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "quantity": 1 }` (missing `product_id`)

**Expected result (per API spec)**
- Missing required fields should return 400.

**Actual result observed**
- Response 404.

---

### Bug 7: Profile accepts non-digit phone number
**Endpoint tested:** `PUT /api/v1/profile`

**Request payload**
- Method: PUT
- URL: `http://localhost:8080/api/v1/profile`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "name": "Valid Name", "phone": "abcdefghij" }`

**Expected result (per API spec)**
- Phone must be exactly 10 digits; invalid phone should return 400.

**Actual result observed**
- Response 200 with success message.

---

### Bug 8: Address creation rejects valid pincode
**Endpoint tested:** `POST /api/v1/addresses`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/addresses`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "label": "OTHER", "street": "Main Street 12", "city": "Hyderabad", "pincode": "500001", "is_default": true }`

**Expected result (per API spec)**
- Pincode exactly 6 digits should be accepted.

**Actual result observed**
- Response 400: `{"error":"Invalid pincode"}`.

---

### Bug 9: Address creation accepts non-digit pincode
**Endpoint tested:** `POST /api/v1/addresses`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/addresses`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "label": "HOME", "street": "Main Street 12", "city": "Hyderabad", "pincode": "ABCDE" }`

**Expected result (per API spec)**
- Pincode must be exactly 6 digits; invalid pincode should return 400.

**Actual result observed**
- Response 200 with address created.

---

### Bug 10: Wallet payment succeeds with insufficient balance
**Endpoint tested:** `POST /api/v1/wallet/pay`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/wallet/pay`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "amount": <balance + 1> }`

**Expected result (per API spec)**
- If wallet balance is not enough, return 400.

**Actual result observed**
- Response 200 with `Payment successful` and reduced balance.

---

### Bug 11: Profile update response omits updated fields
**Endpoint tested:** `PUT /api/v1/profile`

**Request payload**
- Method: PUT
- URL: `http://localhost:8080/api/v1/profile`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "name": "QA Tester", "phone": "9999999999" }`

**Expected result (per API spec)**
- Response includes updated profile data (e.g., `name`, `phone`).

**Actual result observed**
- Response 200 with only a success message, missing `name` and `phone` fields.

---

### Bug 12: Address creation accepts 5-digit pincode
**Endpoint tested:** `POST /api/v1/addresses`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/addresses`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "label": "HOME", "street": "Main Street 12", "city": "Hyderabad", "pincode": "12345" }`

**Expected result (per API spec)**
- Pincode must be exactly 6 digits; invalid pincode should return 400.

**Actual result observed**
- Response 200 with address created.

---

### Bug 13: Address creation allows missing pincode
**Endpoint tested:** `POST /api/v1/addresses`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/addresses`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "label": "HOME", "street": "Main Street 12", "city": "Hyderabad" }`

**Expected result (per API spec)**
- Missing required fields should return 400.

**Actual result observed**
- Response 200 with address created.

---

### Bug 14: Cart total does not equal sum of item subtotals (multi-item cart)
**Endpoint tested:** `GET /api/v1/cart`

**Request payload**
- Method: GET
- URL: `http://localhost:8080/api/v1/cart`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: None (cart set up by adding two products)

**Expected result (per API spec)**
- `cart.total` equals the sum of all `item.subtotal` values.

**Actual result observed**
- Example: computed total $250$, API returned $120$.

---

### Bug 15: Support ticket allows backward transition IN_PROGRESS → OPEN
**Endpoint tested:** `PUT /api/v1/support/tickets/{ticket_id}`

**Request payload**
- Method: PUT
- URL: `http://localhost:8080/api/v1/support/tickets/{ticket_id}`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "status": "OPEN" }` after setting ticket to `IN_PROGRESS`

**Expected result (per API spec)**
- Backward transition should return 400.

**Actual result observed**
- Response 200 with status `OPEN`.

---

### Bug 16: Support ticket accepts invalid status value
**Endpoint tested:** `PUT /api/v1/support/tickets/{ticket_id}`

**Request payload**
- Method: PUT
- URL: `http://localhost:8080/api/v1/support/tickets/{ticket_id}`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "status": "REOPENED" }`

**Expected result (per API spec)**
- Invalid status values should return 400.

**Actual result observed**
- Response 200 with status `REOPENED`.

---

### Bug 17: Support ticket allows CLOSED → IN_PROGRESS transition
**Endpoint tested:** `PUT /api/v1/support/tickets/{ticket_id}`

**Request payload**
- Method: PUT
- URL: `http://localhost:8080/api/v1/support/tickets/{ticket_id}`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "status": "IN_PROGRESS" }` after ticket is `CLOSED`

**Expected result (per API spec)**
- Closed state should be terminal; transition should return 400.

**Actual result observed**
- Response 200 with status `IN_PROGRESS`.

---

### Bug 18: Wallet GET response uses `wallet_balance` instead of `balance`
**Endpoint tested:** `GET /api/v1/wallet`

**Request payload**
- Method: GET
- URL: `http://localhost:8080/api/v1/wallet`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: None

**Expected result (per API spec)**
- Response includes a `balance` field.

**Actual result observed**
- Response contains `wallet_balance` instead of `balance`.

---

### Bug 19: Loyalty GET response uses `loyalty_points` instead of `points`
**Endpoint tested:** `GET /api/v1/loyalty`

**Request payload**
- Method: GET
- URL: `http://localhost:8080/api/v1/loyalty`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: None

**Expected result (per API spec)**
- Response includes a `points` field.

**Actual result observed**
- Response contains `loyalty_points` instead of `points`.

---

### Bug 20: Order can be cancelled multiple times
**Endpoint tested:** `POST /api/v1/orders/{order_id}/cancel`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/orders/{order_id}/cancel`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: None (order created via checkout)

**Expected result (per API spec)**
- First cancel returns 200; second cancel should return 400 because order is already cancelled.

**Actual result observed**
- Second cancel returns 200 and repeats cancellation.

---

### Bug 21: Stock not fully restored after cancel (multi-item order)
**Endpoint tested:** `POST /api/v1/orders/{order_id}/cancel`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/orders/{order_id}/cancel`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: None (order includes two products)

**Expected result (per API spec)**
- Stock for each item should return exactly to its pre-order value.

**Actual result observed**
- At least one product stock remains lower than the original count after cancellation.

---

### Bug 22: Reviews for non-existent product return 200
**Endpoint tested:** `GET /api/v1/products/{product_id}/reviews`

**Request payload**
- Method: GET
- URL: `http://localhost:8080/api/v1/products/9999999/reviews`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: None

**Expected result (per API spec)**
- Non-existent product should return 404.

**Actual result observed**
- Response 200 with `{ "average_rating": 0, "reviews": [] }`.

---

### Bug 23: Inactive product can be added to cart
**Endpoint tested:** `POST /api/v1/cart/add`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/cart/add`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "product_id": <inactive_id>, "quantity": 1 }`

**Expected result (per API spec)**
- Inactive products should not be purchasable; return 400/404.

**Actual result observed**
- Response 200 with item added to cart.

---

### Bug 24: Cart accepts null quantity
**Endpoint tested:** `POST /api/v1/cart/add`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/cart/add`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "product_id": 1, "quantity": null }`

**Expected result (per API spec)**
- Quantity must be a positive integer; null should return 400/422.

**Actual result observed**
- Response 200 with item added to cart.

---

### Bug 25: Cart update succeeds for non-existent item
**Endpoint tested:** `POST /api/v1/cart/update`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/cart/update`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "product_id": 1, "quantity": 5 }` (cart cleared first)

**Expected result (per API spec)**
- Updating a missing cart item should return 404.

**Actual result observed**
- Response 200 with success message.

---

### Bug 26: Cart accepts unknown user id
**Endpoint tested:** `GET /api/v1/cart`

**Request payload**
- Method: GET
- URL: `http://localhost:8080/api/v1/cart`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 99999999`
- Body: None

**Expected result (per API spec)**
- Invalid user id should return 400.

**Actual result observed**
- Response 200 with empty cart.

---

### Bug 27: Profile accepts whitespace-only name
**Endpoint tested:** `PUT /api/v1/profile`

**Request payload**
- Method: PUT
- URL: `http://localhost:8080/api/v1/profile`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "name": "     ", "phone": "1234567890" }`

**Expected result (per API spec)**
- Name should fail validation and return 400.

**Actual result observed**
- Response 200 with success message.

---

### Bug 28: Address max boundary values rejected
**Endpoint tested:** `POST /api/v1/addresses`

**Request payload**
- Method: POST
- URL: `http://localhost:8080/api/v1/addresses`
- Headers: `X-Roll-Number: 2024101062`, `X-User-ID: 1`
- Body: `{ "label": "HOME", "street": "A" * 100, "city": "B" * 50, "pincode": "500001" }`

**Expected result (per API spec)**
- Street length 100 and city length 50 should be accepted.

**Actual result observed**
- Response 400.
```
