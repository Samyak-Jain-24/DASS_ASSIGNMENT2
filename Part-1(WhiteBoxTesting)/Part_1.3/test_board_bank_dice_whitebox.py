"""White-box tests for board.py, bank.py, and dice.py."""

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
from moneypoly.board import Board, SPECIAL_TILES
from moneypoly.config import (
    BANK_STARTING_FUNDS,
    FREE_PARKING_POSITION,
    GO_TO_JAIL_POSITION,
    INCOME_TAX_POSITION,
    JAIL_POSITION,
    LUXURY_TAX_POSITION,
)
from moneypoly.dice import Dice
from moneypoly.player import Player


class BoardWhiteBoxTests(unittest.TestCase):
    def test_special_tiles_mapping_has_core_positions(self):
        self.assertEqual(SPECIAL_TILES[0], "go")
        self.assertEqual(SPECIAL_TILES[JAIL_POSITION], "jail")
        self.assertEqual(SPECIAL_TILES[GO_TO_JAIL_POSITION], "go_to_jail")

    def test_board_creates_expected_property_count(self):
        board = Board()
        self.assertEqual(len(board.properties), 22)

    def test_board_creates_expected_group_count(self):
        board = Board()
        self.assertEqual(len(board.groups), 8)

    def test_get_property_at_hit_and_miss(self):
        board = Board()
        hit = board.get_property_at(board.properties[0].position)
        miss = board.get_property_at(INCOME_TAX_POSITION)
        self.assertIsNotNone(hit)
        self.assertIsNone(miss)

    def test_get_tile_type_special(self):
        board = Board()
        self.assertEqual(board.get_tile_type(INCOME_TAX_POSITION), "income_tax")
        self.assertEqual(board.get_tile_type(LUXURY_TAX_POSITION), "luxury_tax")
        self.assertEqual(board.get_tile_type(FREE_PARKING_POSITION), "free_parking")

    def test_get_tile_type_property_and_blank(self):
        board = Board()
        prop_pos = board.properties[0].position
        self.assertEqual(board.get_tile_type(prop_pos), "property")
        self.assertEqual(board.get_tile_type(12), "blank")

    def test_is_purchasable_false_for_non_property(self):
        board = Board()
        self.assertFalse(board.is_purchasable(INCOME_TAX_POSITION))

    def test_is_purchasable_false_for_mortgaged(self):
        board = Board()
        prop = board.properties[0]
        prop.is_mortgaged = True
        self.assertFalse(board.is_purchasable(prop.position))

    def test_is_purchasable_false_for_owned(self):
        board = Board()
        prop = board.properties[0]
        prop.owner = Player("O")
        self.assertFalse(board.is_purchasable(prop.position))

    def test_is_purchasable_true_for_unowned_unmortgaged(self):
        board = Board()
        prop = board.properties[0]
        self.assertTrue(board.is_purchasable(prop.position))

    def test_is_special_tile_true_false(self):
        board = Board()
        self.assertTrue(board.is_special_tile(0))
        self.assertFalse(board.is_special_tile(1))

    def test_owned_and_unowned_lists(self):
        board = Board()
        owner = Player("O")
        prop = board.properties[0]
        prop.owner = owner
        self.assertIn(prop, board.properties_owned_by(owner))
        self.assertNotIn(prop, board.unowned_properties())


class BankWhiteBoxTests(unittest.TestCase):
    def test_initial_funds(self):
        bank = Bank()
        self.assertEqual(bank.get_balance(), BANK_STARTING_FUNDS)

    def test_collect_increases_funds(self):
        bank = Bank()
        bank.collect(100)
        self.assertEqual(bank.get_balance(), BANK_STARTING_FUNDS + 100)

    def test_collect_negative_decreases_funds_current_behavior(self):
        bank = Bank()
        bank.collect(-50)
        self.assertEqual(bank.get_balance(), BANK_STARTING_FUNDS - 50)

    def test_payout_zero_or_negative_returns_zero(self):
        bank = Bank()
        self.assertEqual(bank.pay_out(0), 0)
        self.assertEqual(bank.pay_out(-1), 0)

    def test_payout_raises_if_insufficient(self):
        bank = Bank()
        with self.assertRaises(ValueError):
            bank.pay_out(BANK_STARTING_FUNDS + 1)

    def test_payout_success_decreases_funds(self):
        bank = Bank()
        amount = bank.pay_out(200)
        self.assertEqual(amount, 200)
        self.assertEqual(bank.get_balance(), BANK_STARTING_FUNDS - 200)

    def test_give_loan_non_positive_ignored(self):
        bank = Bank()
        p = Player("A", balance=0)
        bank.give_loan(p, 0)
        bank.give_loan(p, -10)
        self.assertEqual(p.balance, 0)
        self.assertEqual(bank.loan_count(), 0)

    def test_give_loan_positive_tracks(self):
        bank = Bank()
        p = Player("A", balance=0)
        bank.give_loan(p, 75)
        self.assertEqual(p.balance, 75)
        self.assertEqual(bank.loan_count(), 1)
        self.assertEqual(bank.total_loans_issued(), 75)


class DiceWhiteBoxTests(unittest.TestCase):
    def test_reset_clears_values(self):
        d = Dice()
        d.die1 = 4
        d.die2 = 2
        d.doubles_streak = 2
        d.reset()
        self.assertEqual((d.die1, d.die2, d.doubles_streak), (0, 0, 0))

    def test_roll_calls_randint_with_full_six_sided_range(self):
        calls = []

        def fake_randint(a, b):
            calls.append((a, b))
            return 3

        with patch("moneypoly.dice.random.randint", side_effect=fake_randint):
            d = Dice()
            d.roll()

        self.assertEqual(calls, [(1, 6), (1, 6)])

    def test_roll_updates_streak_on_doubles(self):
        with patch("moneypoly.dice.random.randint", side_effect=[2, 2]):
            d = Dice()
            d.roll()
        self.assertEqual(d.doubles_streak, 1)

    def test_roll_resets_streak_on_non_doubles(self):
        with patch("moneypoly.dice.random.randint", side_effect=[2, 2, 2, 3]):
            d = Dice()
            d.roll()
            d.roll()
        self.assertEqual(d.doubles_streak, 0)

    def test_is_doubles_total_describe(self):
        d = Dice()
        d.die1 = 4
        d.die2 = 4
        self.assertTrue(d.is_doubles())
        self.assertEqual(d.total(), 8)
        self.assertIn("DOUBLES", d.describe())


if __name__ == "__main__":
    unittest.main()
