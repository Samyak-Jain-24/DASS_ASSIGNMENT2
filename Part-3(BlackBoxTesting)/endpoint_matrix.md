# QuickCart Endpoint Matrix

Headers:
- All requests require `X-Roll-Number` (integer).
- User endpoints also require `X-User-ID` (positive integer).
- Admin endpoints do NOT require `X-User-ID`.

| Domain | Method | Endpoint | Required Fields | Key Rules | Expected Errors |
|---|---|---|---|---|---|
| Admin | GET | `/api/v1/admin/users` | – | Full user list | 401/400 for header issues |
| Admin | GET | `/api/v1/admin/users/{user_id}` | – | Single user lookup | 404 missing |
| Admin | GET | `/api/v1/admin/carts` | – | All carts | 401/400 |
| Admin | GET | `/api/v1/admin/orders` | – | All orders | 401/400 |
| Admin | GET | `/api/v1/admin/products` | – | All products including inactive | 401/400 |
| Admin | GET | `/api/v1/admin/coupons` | – | All coupons including expired | 401/400 |
| Admin | GET | `/api/v1/admin/tickets` | – | All tickets | 401/400 |
| Admin | GET | `/api/v1/admin/addresses` | – | All addresses | 401/400 |
| Profile | GET | `/api/v1/profile` | – | Get own profile | 400 invalid/missing X-User-ID |
| Profile | PUT | `/api/v1/profile` | `name`, `phone` | Name 2–50, phone 10 digits | 400 rule violations |
| Address | GET | `/api/v1/addresses` | – | List addresses | 400 invalid/missing X-User-ID |
| Address | POST | `/api/v1/addresses` | `label`, `street`, `city`, `pincode` | Label enum, street 5–100, city 2–50, pincode 6 digits | 400 invalid |
| Address | PUT | `/api/v1/addresses/{id}` | `street`, `is_default` | Only street/is_default editable | 400 invalid |
| Address | DELETE | `/api/v1/addresses/{id}` | – | 404 if missing | 404 missing |
| Products | GET | `/api/v1/products` | – | Only active products | 400 invalid X-User-ID |
| Products | GET | `/api/v1/products/{id}` | – | 404 if missing | 404 missing |
| Cart | GET | `/api/v1/cart` | – | Totals must sum | 400 invalid X-User-ID |
| Cart | POST | `/api/v1/cart/add` | `product_id`, `quantity` | quantity >=1, product exists, stock | 400/404 |
| Cart | POST | `/api/v1/cart/update` | `product_id`, `quantity` | quantity >=1 | 400/404 |
| Cart | POST | `/api/v1/cart/remove` | `product_id` | 404 if not in cart | 404 missing |
| Cart | DELETE | `/api/v1/cart/clear` | – | Clear cart | 400 invalid X-User-ID |
| Coupon | POST | `/api/v1/coupon/apply` | `code` | not expired, min cart, discount rules | 400 invalid |
| Coupon | POST | `/api/v1/coupon/remove` | – | remove applied coupon | 400 invalid |
| Checkout | POST | `/api/v1/checkout` | `payment_method` | COD/WALLET/CARD only; GST 5%; COD <=5000 | 400 invalid |
| Wallet | GET | `/api/v1/wallet` | – | View balance | 400 invalid X-User-ID |
| Wallet | POST | `/api/v1/wallet/add` | `amount` | 1..100000 | 400 invalid |
| Wallet | POST | `/api/v1/wallet/pay` | `amount` | >0 and <= balance | 400 invalid |
| Loyalty | GET | `/api/v1/loyalty` | – | View points | 400 invalid X-User-ID |
| Loyalty | POST | `/api/v1/loyalty/redeem` | `points` | >=1 and <= available | 400 invalid |
| Orders | GET | `/api/v1/orders` | – | List orders | 400 invalid X-User-ID |
| Orders | GET | `/api/v1/orders/{id}` | – | 404 if missing | 404 missing |
| Orders | POST | `/api/v1/orders/{id}/cancel` | – | 400 if delivered; 404 missing | 400/404 |
| Orders | GET | `/api/v1/orders/{id}/invoice` | – | subtotal + gst = total | 404 missing |
| Reviews | GET | `/api/v1/products/{id}/reviews` | – | avg rating decimal; 0 if none | 404 missing product |
| Reviews | POST | `/api/v1/products/{id}/reviews` | `rating`, `comment` | rating 1–5; comment 1–200 | 400 invalid |
| Support | POST | `/api/v1/support/ticket` | `subject`, `message` | subject 5–100, message 1–500, status OPEN | 400 invalid |
| Support | GET | `/api/v1/support/tickets` | – | view tickets | 400 invalid |
| Support | PUT | `/api/v1/support/tickets/{id}` | `status` | OPEN→IN_PROGRESS→CLOSED only | 400 invalid |
