def assert_keys(obj, keys):
    missing = [key for key in keys if key not in obj]
    assert not missing, f"Missing keys: {missing}"


def assert_type(obj, key, expected_type):
    assert key in obj, f"Key {key} missing"
    assert isinstance(obj[key], expected_type), f"{key} must be {expected_type}"


def assert_status(resp, expected):
    assert resp.status_code == expected, f"Expected {expected}, got {resp.status_code}: {resp.text}"


def assert_json(resp):
    try:
        return resp.json()
    except Exception as exc:
        raise AssertionError(f"Invalid JSON response: {exc}\n{resp.text}")
