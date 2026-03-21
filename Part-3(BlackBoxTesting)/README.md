# QuickCart Black-Box API Testing

This folder contains a comprehensive black-box test suite and reports for the QuickCart REST API.

## What’s Included
- `tests/`: pytest + requests automated test suite
- `test_cases.md`: detailed test case catalog (input, expected output, justification)
- `traceability.md`: requirement-to-test mapping checklist
- `BUG_REPORT_TEMPLATE.md`: required bug report format
- `requirements.txt`: Python dependencies

## Assumptions
- The API server is running at `http://localhost:8080` unless overridden.
- Admin endpoints only require `X-Roll-Number`.
- User endpoints require both `X-Roll-Number` and `X-User-ID`.

## Configure
Set environment variables (recommended):

```bash
export QUICKCART_BASE_URL="http://localhost:8080"
export QUICKCART_ROLL_NUMBER="<your-roll-number>"
export QUICKCART_USER_ID="<existing-user-id>"
```

## Start Server (Docker)
```bash
docker load -i quickcart_image.tar
docker run -p 8080:8080 quickcart
```

## Install
```bash
python -m pip install -r requirements.txt
```

## Run Tests
```bash
pytest -q
```

Optional overrides:
```bash
pytest -q --base-url http://localhost:8080 --roll 1234 --user-id 1
```

## Notes
- Some tests dynamically select existing users/products via admin endpoints.
- If the database has no eligible data for a specific test, the test is skipped.
