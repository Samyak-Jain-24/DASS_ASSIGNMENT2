# DASS_ASSIGNMENT2

OneDrive Link:
https://1drv.ms/f/c/55aaaea708d50778/IgBgXe6sYzF6TI9-hlpKjZuYAUGm9hE81-xiE38rxCYuSKY?e=SlnGVO

GitHub Repository:
- https://github.com/Samyak-Jain-24/DASS_ASSIGNMENT2

This repository contains three parts:
- Whitebox Testing
- Integration Testing
- Blackbox Testing

## 1) Whitebox

Location:
- whitebox/

Run the code:
1. cd DASS_ASSIGNMENT2/whitebox/code
2. python main.py

Run the tests:
1. cd DASS_ASSIGNMENT2
2. python -m pytest whitebox/tests -q

## 2) Integration

Location:
- integration/

Run the code (demo flow):
1. cd DASS_ASSIGNMENT2
2. python -m integration.code.main

Run the integration tests:
1. cd DASS_ASSIGNMENT2
2. python integration/tests/integration_test_runner.py

## 3) Blackbox

Location:
- blackbox/

Run the code:
- There is no local application entrypoint inside blackbox/.
- Blackbox tests target the external QuickCart API server.

Run the tests:
1. Start QuickCart server (default expected URL: http://localhost:8080).
2. Set required environment variable QUICKCART_ROLL_NUMBER.
3. Optional: set QUICKCART_BASE_URL and QUICKCART_USER_ID.
4. cd DASS_ASSIGNMENT2
5. python -m pytest blackbox/tests -q

Example (PowerShell):
- $env:QUICKCART_ROLL_NUMBER="2024101062"
- $env:QUICKCART_BASE_URL="http://localhost:8080"
- python -m pytest blackbox/tests -q

## Notes

- Use Python 3.10+.
- If pytest is missing, install it:
	- python -m pip install pytest requests

