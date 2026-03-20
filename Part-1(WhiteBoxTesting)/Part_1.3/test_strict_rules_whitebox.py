"""Additional strict white-box tests for rule/spec conformance.

These tests intentionally enforce stricter gameplay and docstring-aligned
behavior, and may reveal new logical defects.
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

CURRENT_DIR = os.path.dirname(__file__)
PART1_ROOT = os.path.dirname(CURRENT_DIR)
OUTER_MONEYPOLY = os.path.join(PART1_ROOT, "moneypoly")
if OUTER_MONEYPOLY not in sys.path:
    sys.path.insert(0, OUTER_MONEYPOLY)

from moneypoly.bank import Bank
from moneypoly.config import GO_SALARY, JAIL_FINE
from moneypoly.game import Game
from moneypoly.player import Player
from moneypoly.property import Property


class StrictRuleTests(unittest.TestCase):
    """Rule-focused tests that can expose additional behavioral defects."""

    def test_player_move_passing_go_collects_salary(self):
        """Docstring says salary is awarded when passing or landing on Go."""

        p = Player("A", balance=0)
        p.position = 39
        new_pos = p.move(2)
        self.assertEqual(new_pos, 1)
        self.assertEqual(p.balance, GO_SALARY)

    def test_bank_collect_negative_amount_is_ignored(self):
        """Bank.collect docstring says negative amounts are ignored."""

        bank = Bank()
        start = bank.get_balance()
        bank.collect(-100)
        self.assertEqual(bank.get_balance(), start)

    def test_bank_give_loan_reduces_bank_funds(self):
        """Bank.give_loan docstring says bank funds are reduced accordingly."""

        bank = Bank()
        start = bank.get_balance()
        p = Player("A", balance=0)
        bank.give_loan(p, 75)
        self.assertEqual(p.balance, 75)
        self.assertEqual(bank.get_balance(), start - 75)

    def test_buy_property_with_exact_balance_should_succeed(self):
        """A player with exact funds should be able to buy the property."""

        g = Game(["A"])
        p = g.players[0]
        prop = Property("X", 1, 100, 10)
        p.balance = 100
        self.assertTrue(g.buy_property(p, prop))
        self.assertIs(prop.owner, p)

    def test_pay_rent_transfers_money_to_owner(self):
        """Rent should move money from tenant to owner, not just deduct tenant."""

        g = Game(["Tenant", "Owner"])
        tenant, owner = g.players
        prop = Property("X", 1, 100, 10)
        prop.owner = owner

        tenant.balance = 100
        owner.balance = 0
        g.pay_rent(tenant, prop)

        self.assertEqual(tenant.balance, 90)
        self.assertEqual(owner.balance, 10)

    def test_jail_pay_fine_should_deduct_player_balance(self):
        """Voluntary jail fine payment should reduce player money by JAIL_FINE."""

        g = Game(["A"])
        p = g.players[0]
        p.in_jail = True
        p.balance = 100

        with patch("moneypoly.ui.confirm", return_value=True), patch.object(g.dice, "roll", return_value=2), patch.object(g, "_move_and_resolve"):
            g._handle_jail_turn(p)

        self.assertEqual(p.balance, 100 - JAIL_FINE)

    def test_trade_should_credit_seller_cash(self):
        """Trade should transfer cash from buyer to seller along with property."""

        g = Game(["Seller", "Buyer"])
        seller, buyer = g.players
        prop = Property("X", 1, 100, 10)
        prop.owner = seller
        seller.add_property(prop)

        seller.balance = 0
        buyer.balance = 100

        self.assertTrue(g.trade(seller, buyer, prop, 50))
        self.assertEqual(buyer.balance, 50)
        self.assertEqual(seller.balance, 50)


if __name__ == "__main__":
    unittest.main()
