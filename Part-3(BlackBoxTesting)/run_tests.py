import os
import sys
import pytest


def main():
    args = ["-q"]
    base_url = os.getenv("QUICKCART_BASE_URL")
    roll = os.getenv("QUICKCART_ROLL_NUMBER")
    user_id = os.getenv("QUICKCART_USER_ID")
    if base_url:
        args += ["--base-url", base_url]
    if roll:
        args += ["--roll", roll]
    if user_id:
        args += ["--user-id", user_id]
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(main())
