# QuickCart Test Case Catalog

Each test includes input, expected output, and justification. IDs map to automated tests where applicable.

## Global Headers
- **HB-01** Valid headers: `X-Roll-Number` integer, `X-User-ID` valid -> 2xx for user endpoints. *Justification:* baseline access.
- **HB-02** Missing `X-Roll-Number` -> 401. *Justification:* required header rule.
- **HB-03** Non-integer `X-Roll-Number` -> 400. *Justification:* input validation.
- **HB-04** Missing `X-User-ID` on user endpoint -> 400. *Justification:* user-scoped rule.
- **HB-05** Non-integer `X-User-ID` -> 400. *Justification:* input validation.

## Admin
- **AD-01** GET `/admin/users` -> 200, array of users. *Justification:* inspection data.
- **AD-02** GET `/admin/users/{id}` valid -> 200. *Justification:* single lookup.
- **AD-03** GET `/admin/users/{id}` invalid -> 404. *Justification:* missing resource.
- **AD-04** GET `/admin/products` -> 200. *Justification:* used to verify active/inactive rules.

## Profile
- **PR-01** GET `/profile` -> 200 with profile fields. *Justification:* baseline.
- **PR-02** PUT `/profile` valid name (2–50), phone 10 digits -> 200 updated. *Justification:* positive update.
- **PR-03** PUT name length 1 -> 400. *Justification:* boundary (min-1).
- **PR-04** PUT name length 51 -> 400. *Justification:* boundary (max+1).
- **PR-05** PUT phone length 9/11 -> 400. *Justification:* boundary.
- **PR-06** PUT phone with letters -> 400. *Justification:* datatype.

## Addresses
- **AD-DR-01** POST valid HOME/OFFICE/OTHER -> 200 + full address object with `address_id`. *Justification:* create.
- **AD-DR-02** POST invalid label -> 400. *Justification:* enum validation.
- **AD-DR-03** POST street len 4 / 101 -> 400. *Justification:* boundary.
- **AD-DR-04** POST city len 1 / 51 -> 400. *Justification:* boundary.
- **AD-DR-05** POST pincode len 5/7 or non-digits -> 400. *Justification:* datatype + boundary.
- **AD-DR-06** GET addresses -> list includes new address. *Justification:* view.
- **AD-DR-07** PUT address change street + default -> 200 updated street. *Justification:* update allowed fields.
- **AD-DR-08** PUT attempt change city/label/pincode -> 400 or unchanged. *Justification:* restricted fields.
- **AD-DR-09** Only one default address at a time. *Justification:* uniqueness.
- **AD-DR-10** DELETE non-existent address -> 404. *Justification:* missing resource.

## Products
- **PRD-01** GET `/products` -> 200, only active products. *Justification:* active filter.
- **PRD-02** GET `/products/{id}` valid -> 200. *Justification:* lookup.
- **PRD-03** GET `/products/{id}` invalid -> 404. *Justification:* missing resource.
- **PRD-04** Filter by category, search, sort -> valid ordering/filtering. *Justification:* query logic.
- **PRD-05** Price shown equals DB price. *Justification:* correctness.

## Cart
- **CRT-01** POST add quantity 1 -> 200, item present. *Justification:* add.
- **CRT-02** POST add quantity 0/-1 -> 400. *Justification:* boundary.
- **CRT-03** POST add non-existent product -> 404. *Justification:* missing resource.
- **CRT-04** POST add quantity > stock -> 400. *Justification:* stock rule.
- **CRT-05** Add same product twice -> quantities summed. *Justification:* aggregation.
- **CRT-06** POST update quantity 1+ -> 200 updated. *Justification:* update.
- **CRT-07** POST update quantity 0 -> 400. *Justification:* boundary.
- **CRT-08** POST remove missing product -> 404. *Justification:* missing resource.
- **CRT-09** Cart subtotal per item = qty * price; total = sum. *Justification:* correctness.
- **CRT-10** DELETE clear -> empty cart. *Justification:* clear.

## Coupons
- **CPN-01** Apply expired coupon -> 400. *Justification:* expiry rule.
- **CPN-02** Apply below minimum cart -> 400. *Justification:* min cart value.
- **CPN-03** Apply PERCENT -> percent discount correct. *Justification:* formula.
- **CPN-04** Apply FIXED -> flat discount correct. *Justification:* formula.
- **CPN-05** Apply cap -> discount not exceed cap. *Justification:* cap rule.
- **CPN-06** Remove coupon -> totals restored. *Justification:* remove.

## Checkout
- **CHK-01** Payment method invalid -> 400. *Justification:* enum.
- **CHK-02** Empty cart -> 400. *Justification:* required items.
- **CHK-03** GST added once at 5%. *Justification:* tax correctness.
- **CHK-04** COD total > 5000 -> 400. *Justification:* business rule.
- **CHK-05** COD/WALLET status PENDING; CARD status PAID. *Justification:* status logic.

## Wallet
- **WAL-01** GET wallet -> balance present. *Justification:* view.
- **WAL-02** Add amount 0/-1 -> 400. *Justification:* boundary.
- **WAL-03** Add amount 100001 -> 400. *Justification:* boundary.
- **WAL-04** Pay amount > balance -> 400. *Justification:* insufficient funds.
- **WAL-05** Pay amount deducted exactly. *Justification:* correctness.

## Loyalty
- **LOY-01** GET loyalty -> points present. *Justification:* view.
- **LOY-02** Redeem 0 -> 400. *Justification:* boundary.
- **LOY-03** Redeem > points -> 400. *Justification:* insufficient points.

## Orders
- **ORD-01** GET orders -> list. *Justification:* view.
- **ORD-02** GET order detail valid -> 200. *Justification:* lookup.
- **ORD-03** GET order detail invalid -> 404. *Justification:* missing resource.
- **ORD-04** Cancel delivered -> 400. *Justification:* rule.
- **ORD-05** Cancel invalid ID -> 404. *Justification:* missing resource.
- **ORD-06** Cancel restores stock. *Justification:* inventory correction.
- **ORD-07** Invoice includes subtotal, GST, total and matches order. *Justification:* correctness.

## Reviews
- **REV-01** GET reviews -> avg rating 0 if none. *Justification:* base case.
- **REV-02** POST rating <1 or >5 -> 400. *Justification:* boundary.
- **REV-03** POST comment len 0 or >200 -> 400. *Justification:* boundary.
- **REV-04** Average rating is proper decimal based on ratings. *Justification:* precision.

## Support Tickets
- **SUP-01** POST valid subject/message -> 200 with status OPEN. *Justification:* create.
- **SUP-02** Subject len <5 or >100 -> 400. *Justification:* boundary.
- **SUP-03** Message len 0 or >500 -> 400. *Justification:* boundary.
- **SUP-04** Status transition OPEN->IN_PROGRESS->CLOSED only. *Justification:* FSM rule.
- **SUP-05** Invalid status transition -> 400. *Justification:* rule enforcement.
