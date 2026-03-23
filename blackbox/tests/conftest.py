import os
import pytest
import requests


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default=None)
    parser.addoption("--roll", action="store", default=None)
    parser.addoption("--user-id", action="store", default=None)


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    return (
        pytestconfig.getoption("base_url")
        or os.getenv("QUICKCART_BASE_URL")
        or "http://localhost:8080"
    )


@pytest.fixture(scope="session")
def roll_number(pytestconfig):
    value = pytestconfig.getoption("roll") or os.getenv("QUICKCART_ROLL_NUMBER")
    if value is None:
        pytest.skip("Set QUICKCART_ROLL_NUMBER or pass --roll to run tests")
    try:
        return str(int(value))
    except ValueError:
        pytest.skip("QUICKCART_ROLL_NUMBER must be a valid integer")


@pytest.fixture(scope="session")
def default_headers(roll_number):
    return {"X-Roll-Number": str(roll_number)}


@pytest.fixture(scope="session")
def admin_client(base_url, default_headers):
    return APIClient(base_url, default_headers)


@pytest.fixture(scope="session")
def user_id(pytestconfig, admin_client):
    explicit = pytestconfig.getoption("user_id") or os.getenv("QUICKCART_USER_ID")
    if explicit:
        try:
            return int(explicit)
        except ValueError:
            pass
    users = admin_client.get_json("/api/v1/admin/users")
    if not users:
        pytest.skip("No users available from admin endpoint")
    return int(users[0]["user_id"])


@pytest.fixture(scope="session")
def user_headers(default_headers, user_id):
    headers = dict(default_headers)
    headers["X-User-ID"] = str(user_id)
    return headers


class APIClient:
    def __init__(self, base_url, headers):
        self.base_url = base_url.rstrip("/")
        self.headers = headers

    def _url(self, path):
        return f"{self.base_url}{path}"

    def request(self, method, path, **kwargs):
        headers = dict(self.headers)
        headers.update(kwargs.pop("headers", {}) or {})
        return requests.request(method, self._url(path), headers=headers, **kwargs)

    def get_json(self, path, **kwargs):
        resp = self.request("GET", path, **kwargs)
        resp.raise_for_status()
        return resp.json()


@pytest.fixture(scope="session")
def user_client(base_url, user_headers):
    return APIClient(base_url, user_headers)
