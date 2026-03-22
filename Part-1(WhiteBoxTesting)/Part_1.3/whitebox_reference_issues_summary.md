# White-Box Issues Found (Reference Report)

## Error 1
- Issue: Importing `moneypoly.game` fails with `ModuleNotFoundError: No module named 'config'` due to non‑package imports.
- Fix: Use package‑relative imports with a direct‑execution fallback in `game.py`, `player.py`, `board.py`, and `bank.py`.

## Error 2
- Issue: `Dice.roll()` used `random.randint(1, 5)` so face value 6 was impossible.
- Fix: Change bounds to `random.randint(1, 6)` for both dice in `moneypoly/dice.py`.

## Error 3
- Issue: `Player.move()` only paid salary when landing exactly on Go; passing Go paid nothing.
- Fix: Detect wrap‑around (`new_position < old_position`) and pay `GO_SALARY` for pass/land.

## Error 4
- Issue: `PropertyGroup.all_owned_by()` used `any(...)`, so owning one property counted as full ownership.
- Fix: Use `all(...)` to require complete group ownership.

## Error 5
- Issue: `buy_property()` rejected exact‑balance purchases (`balance <= price`).
- Fix: Allow purchase when `balance == price` by checking `balance < price`.

## Error 6
- Issue: `pay_rent()` deducted tenant money but did not credit the owner.
- Fix: Add `prop.owner.add_money(rent)` after tenant deduction.

## Error 7
- Issue: Voluntary jail fine path credited the bank but did not deduct the player.
- Fix: Call `player.deduct_money(JAIL_FINE)` before bank collection in `_handle_jail_turn()`.

## Error 8
- Issue: `find_winner()` used `min(...)`, declaring the poorest player winner.
- Fix: Use `max(...)` to select highest net worth.

## Error 9
- Issue: `unmortgage_property()` cleared mortgage before checking affordability, leaving it un‑mortgaged on failure.
- Fix: Validate mortgaged state and affordability first, then call `prop.unmortgage()` only on success.

## Error 10
- Issue: `trade()` deducted money from buyer but never credited seller; non‑positive trades allowed.
- Fix: Credit seller and reject non‑positive cash trades.

## Error 11
- Issue: `buy_property()` allowed overwriting an already‑owned property.
- Fix: Add owner check and return `False` when already owned.

## Error 12
- Issue: `Bank.give_loan()` credited player without reducing bank funds and allowed over‑lending.
- Fix: Reduce `_funds` on loan and raise `ValueError` when requested loan exceeds reserves; guard non‑positive loans.

## Error 13
- Issue: `cards_remaining()` / `__repr__()` used modulo by `len(cards)` and crashed on empty decks (`ZeroDivisionError`).
- Fix: Add empty‑deck guards; `cards_remaining()` returns 0 and `__repr__()` is safe.

## Error 14
- Issue: `Player.net_worth()` returned only cash and ignored property values.
- Fix: Include owned property values (full price if normal, mortgage value if mortgaged).

## Error 15
- Issue: `auction_property()` allowed re‑auctioning already‑owned properties.
- Fix: Early guard that exits when `prop.owner` is not `None`.

## Error 16
- Issue: Over‑limit loan request in interactive menu propagated `ValueError` and crashed the game loop.
- Fix: Wrap loan call in `interactive_menu()` with `try/except ValueError` and show user‑friendly message.

## Error 17
- Issue: `_card_collect()` propagated `ValueError` when bank lacked funds, terminating gameplay.
- Fix: Catch `ValueError`, log a clear message, treat payout as $0 so the turn continues.

## Error 18
- Issue: `main()` accepted fewer than two players, despite documented minimum.
- Fix: Validate count and raise `ValueError` when fewer than 2 names are provided.

## Error 19
- Issue: `_apply_card()` indexed `card["action"]`/`card["value"]` directly, raising `KeyError` on malformed cards.
- Fix: Read fields safely via `.get()`, default value to 0, ignore missing action with a clear message.
