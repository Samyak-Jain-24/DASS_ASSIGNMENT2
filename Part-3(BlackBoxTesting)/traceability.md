# Requirement Traceability Matrix

This matrix maps every assignment requirement to concrete artifacts.

## Assignment Requirements
- Valid requests
- Invalid inputs
- Missing fields
- Wrong data types
- Boundary values
- Correct HTTP status codes
- Proper JSON response structures
- Correctness of returned data based on API spec
- Bug report includes: endpoint, request payload (method, URL, headers, body), expected result, actual result

## Mapping
- Valid requests: `tests/test_*` positive cases + `test_cases.md`
- Invalid inputs: `tests/test_*` negative cases + `test_cases.md`
- Missing fields: header tests + payload omission tests
- Wrong data types: payload type tests in each domain
- Boundary values: min/max length & numeric tests
- HTTP status codes: `assert_status` in all tests
- JSON structure: `assert_keys` checks and response schema checks
- Correct data: subtotal/total/GST/calc verification tests
- Bug reports: `BUG_REPORT_TEMPLATE.md`
