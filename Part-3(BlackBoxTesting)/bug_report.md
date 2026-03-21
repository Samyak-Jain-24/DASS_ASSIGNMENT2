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
