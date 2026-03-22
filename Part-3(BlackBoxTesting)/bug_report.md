# Bug Report

## Summary
The following bugs were observed while running the black-box tests against the QuickCart API.

Headers used:
- `X-Roll-Number: 2024101062`
- `X-User-ID: 1`

---

## Bug 1: Invoice totals inconsistent
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

## Bug 2: Review average rating rounded down
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

## Bug 3: Invalid support ticket status transition allowed
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

## Bug 4: Cart item subtotal incorrect
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

## Bug 5: Cart add allows quantity 0
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

## Bug 6: Cart add missing required fields returns 404
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

## Bug 7: Profile accepts non-digit phone number
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

## Bug 8: Address creation rejects valid pincode
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

## Bug 9: Address creation accepts non-digit pincode
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

## Bug 10: Wallet payment succeeds with insufficient balance
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

## Bug 11: Profile update response omits updated fields
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

## Bug 12: Address creation accepts 5-digit pincode
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

## Bug 13: Address creation allows missing pincode
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

## Bug 14: Cart total does not equal sum of item subtotals (multi-item cart)
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

## Bug 15: Support ticket allows backward transition IN_PROGRESS → OPEN
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

## Bug 16: Support ticket accepts invalid status value
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

## Bug 17: Support ticket allows CLOSED → IN_PROGRESS transition
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

## Bug 18: Wallet GET response uses `wallet_balance` instead of `balance`
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

## Bug 19: Loyalty GET response uses `loyalty_points` instead of `points`
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

## Bug 20: Order can be cancelled multiple times
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

## Bug 21: Stock not fully restored after cancel (multi-item order)
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

## Bug 22: Reviews for non-existent product return 200
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

## Bug 23: Inactive product can be added to cart
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

## Bug 24: Cart accepts null quantity
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

## Bug 25: Cart update succeeds for non-existent item
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

## Bug 26: Cart accepts unknown user id
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

## Bug 27: Profile accepts whitespace-only name
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

## Bug 28: Address max boundary values rejected
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
