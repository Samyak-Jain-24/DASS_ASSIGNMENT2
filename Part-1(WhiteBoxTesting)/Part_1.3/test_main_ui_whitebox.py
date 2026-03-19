"""White-box tests for main.py and ui.py utility behavior."""

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

import main as main_mod
from moneypoly import ui
from moneypoly.player import Player
from moneypoly.property import Property
from moneypoly.board import Board


class MainWhiteBoxTests(unittest.TestCase):
    def test_get_player_names_splits_and_strips(self):
        with patch("builtins.input", return_value=" Alice , Bob,Charlie "):
            names = main_mod.get_player_names()
        self.assertEqual(names, ["Alice", "Bob", "Charlie"])

    def test_get_player_names_ignores_empty_tokens(self):
        with patch("builtins.input", return_value="A,, ,B,"):
            names = main_mod.get_player_names()
        self.assertEqual(names, ["A", "B"])

    def test_main_keyboard_interrupt_path(self):
        with patch.object(main_mod, "get_player_names", return_value=["A", "B"]), patch("main.Game") as game_cls:
            game_instance = game_cls.return_value
            game_instance.run.side_effect = KeyboardInterrupt
            buf = io.StringIO()
            with redirect_stdout(buf):
                main_mod.main()
            self.assertIn("Game interrupted", buf.getvalue())

    def test_main_value_error_path(self):
        with patch.object(main_mod, "get_player_names", return_value=["A"]), patch("main.Game", side_effect=ValueError("bad setup")):
            buf = io.StringIO()
            with redirect_stdout(buf):
                main_mod.main()
            self.assertIn("Setup error: bad setup", buf.getvalue())


class UiWhiteBoxTests(unittest.TestCase):
    def test_format_currency(self):
        self.assertEqual(ui.format_currency(1500), "$1,500")

    def test_safe_int_input_valid(self):
        with patch("builtins.input", return_value="42"):
            self.assertEqual(ui.safe_int_input("x", default=0), 42)

    def test_safe_int_input_invalid_uses_default(self):
        with patch("builtins.input", return_value="abc"):
            self.assertEqual(ui.safe_int_input("x", default=-1), -1)

    def test_confirm_true_for_y_only(self):
        with patch("builtins.input", return_value="y"):
            self.assertTrue(ui.confirm("x"))
        with patch("builtins.input", return_value="Y"):
            self.assertTrue(ui.confirm("x"))
        with patch("builtins.input", return_value="yes"):
            self.assertFalse(ui.confirm("x"))

    def test_print_banner_outputs_title(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ui.print_banner("HELLO")
        out = buf.getvalue()
        self.assertIn("HELLO", out)

    def test_print_player_card_with_and_without_properties(self):
        p = Player("A")
        buf = io.StringIO()
        with redirect_stdout(buf):
            ui.print_player_card(p)
        self.assertIn("Properties: none", buf.getvalue())

        prop = Property("X", 1, 100, 10)
        p.properties.append(prop)
        buf = io.StringIO()
        with redirect_stdout(buf):
            ui.print_player_card(p)
        self.assertIn("Properties:", buf.getvalue())
        self.assertIn("X", buf.getvalue())

    def test_print_standings_sorts_by_net_worth(self):
        p1 = Player("A", balance=10)
        p2 = Player("B", balance=100)
        buf = io.StringIO()
        with redirect_stdout(buf):
            ui.print_standings([p1, p2])
        out = buf.getvalue()
        self.assertLess(out.find("B"), out.find("A"))

    def test_print_board_ownership_shows_mortgage_flag(self):
        board = Board()
        prop = board.properties[0]
        prop.is_mortgaged = True
        buf = io.StringIO()
        with redirect_stdout(buf):
            ui.print_board_ownership(board)
        self.assertIn("(* = mortgaged)", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
