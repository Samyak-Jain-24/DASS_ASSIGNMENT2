"""Additional balanced white-box tests.

This module focuses on expected-to-pass behavior confirmation tests,
complementing strict defect-finding tests.
"""

from __future__ import annotations

import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

CURRENT_DIR = os.path.dirname(__file__)
PART1_ROOT = os.path.dirname(CURRENT_DIR)
OUTER_MONEYPOLY = os.path.join(PART1_ROOT, "moneypoly")
if OUTER_MONEYPOLY not in sys.path:
    sys.path.insert(0, OUTER_MONEYPOLY)

from moneypoly.bank import Bank
from moneypoly.board import Board
from moneypoly.cards import CardDeck
from moneypoly.game import Game
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup
from moneypoly import ui


class BalancedModelTests(unittest.TestCase):
    def test_propertygroup_owner_counts_empty(self):
        group = PropertyGroup("Green", "green")
        self.assertEqual(group.get_owner_counts(), {})

    def test_propertygroup_size_updates(self):
        group = PropertyGroup("Green", "green")
        Property("P1", 1, 100, 10, group=group)
        Property("P2", 2, 110, 11, group=group)
        self.assertEqual(group.size(), 2)

    def test_player_remove_absent_property_no_change(self):
        player = Player("A")
        prop = Property("P", 1, 100, 10)
        player.remove_property(prop)
        self.assertEqual(player.count_properties(), 0)

    def test_bank_total_loans_multiple(self):
        bank = Bank()
        player = Player("A", balance=0)
        bank.give_loan(player, 40)
        bank.give_loan(player, 60)
        self.assertEqual(bank.loan_count(), 2)
        self.assertEqual(bank.total_loans_issued(), 100)

    def test_bank_summary_prints(self):
        bank = Bank()
        out = io.StringIO()
        with redirect_stdout(out):
            bank.summary()
        text = out.getvalue()
        self.assertIn("Bank reserves", text)
        self.assertIn("Loans issued", text)


class BalancedBoardAndCardsTests(unittest.TestCase):
    def test_board_repr_contains_counts(self):
        board = Board()
        text = repr(board)
        self.assertIn("properties", text)

    def test_carddeck_repr_non_empty(self):
        deck = CardDeck([{"description": "A", "action": "collect", "value": 10}])
        text = repr(deck)
        self.assertIn("CardDeck", text)

    def test_carddeck_draw_then_peek(self):
        deck = CardDeck(
            [
                {"description": "A", "action": "collect", "value": 1},
                {"description": "B", "action": "pay", "value": 2},
            ]
        )
        _ = deck.draw()
        self.assertEqual(deck.peek()["description"], "B")


class BalancedUiTests(unittest.TestCase):
    def test_safe_int_input_type_error_path(self):
        with patch("builtins.input", return_value=None):
            self.assertEqual(ui.safe_int_input("x", default=7), 7)

    def test_confirm_trims_spaces(self):
        with patch("builtins.input", return_value="  y  "):
            self.assertTrue(ui.confirm("x"))


class BalancedGameFlowTests(unittest.TestCase):
    def test_advance_turn_single_player(self):
        game = Game(["Solo"])
        game.advance_turn()
        self.assertEqual(game.current_index, 0)
        self.assertEqual(game.turn_number, 1)

    def test_apply_card_move_to_without_passing_go_no_salary(self):
        game = Game(["A"])
        player = game.players[0]
        player.position = 1
        player.balance = 0
        with patch.object(game.board, "get_tile_type", return_value="blank"):
            game._apply_card(player, {"description": "M", "action": "move_to", "value": 5})
        self.assertEqual(player.position, 5)
        self.assertEqual(player.balance, 0)

    def test_apply_card_unknown_action_noop(self):
        game = Game(["A"])
        player = game.players[0]
        start_balance = player.balance
        game._apply_card(player, {"description": "X", "action": "unknown", "value": 99})
        self.assertEqual(player.balance, start_balance)

    def test_run_no_players_prints_no_players_message(self):
        game = Game(["A"])
        game.players = []
        out = io.StringIO()
        with redirect_stdout(out):
            game.run()
        self.assertIn("no players remaining", out.getvalue().lower())

    def test_menu_mortgage_invalid_selection_does_not_call_action(self):
        game = Game(["A"])
        player = game.players[0]
        prop = Property("P", 1, 100, 10)
        prop.owner = player
        player.properties.append(prop)

        with patch("moneypoly.ui.safe_int_input", return_value=99), patch.object(game, "mortgage_property") as mortgage:
            game._menu_mortgage(player)
        mortgage.assert_not_called()

    def test_menu_unmortgage_invalid_selection_does_not_call_action(self):
        game = Game(["A"])
        player = game.players[0]
        prop = Property("P", 1, 100, 10)
        prop.owner = player
        prop.is_mortgaged = True
        player.properties.append(prop)

        with patch("moneypoly.ui.safe_int_input", return_value=99), patch.object(game, "unmortgage_property") as unm:
            game._menu_unmortgage(player)
        unm.assert_not_called()


if __name__ == "__main__":
    unittest.main()
