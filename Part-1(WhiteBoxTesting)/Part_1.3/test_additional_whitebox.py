"""Additional white-box tests to expand branch and state coverage."""

import os
import sys
import unittest
from unittest.mock import patch

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "moneypoly"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from moneypoly.board import Board
from moneypoly.config import GO_SALARY
from moneypoly.game import Game
from moneypoly.property import Property, PropertyGroup, PropertySpec


class PropertySpecWhiteBoxTests(unittest.TestCase):
    """PropertySpec constructor and group-link tests."""

    def test_propertyspec_constructor_registers_group(self):
        group = PropertyGroup("Test", "test")
        spec = PropertySpec("X", 1, 100, 10)
        prop = Property(spec, group=group)
        self.assertEqual(prop.name, "X")
        self.assertEqual(prop.position, 1)
        self.assertEqual(prop.price, 100)
        self.assertEqual(prop.base_rent, 10)
        self.assertIn(prop, group.properties)


class BoardTileEdgeTests(unittest.TestCase):
    """Board tile-type edge cases."""

    def test_blank_tile_returns_blank(self):
        board = Board()
        self.assertEqual(board.get_tile_type(12), "blank")


class GameCardBranchTests(unittest.TestCase):
    """Card action branches for Game._apply_card handlers."""

    def setUp(self):
        self.game = Game(["A", "B"])
        self.player = self.game.players[0]
        self.other = self.game.players[1]

    def test_card_collect_increases_balance(self):
        starting_balance = self.player.balance
        self.game._card_collect(self.player, 50)
        self.assertEqual(self.player.balance, starting_balance + 50)

    def test_card_pay_decreases_balance(self):
        starting_balance = self.player.balance
        self.game._card_pay(self.player, 25)
        self.assertEqual(self.player.balance, starting_balance - 25)

    def test_card_move_to_passing_go_awards_salary(self):
        self.player.position = 39
        with patch.object(self.game, "_handle_property_tile"):
            self.game._card_move_to(self.player, 1)
        self.assertEqual(self.player.balance, 1500 + GO_SALARY)

    def test_collect_from_all_skips_insufficient_players(self):
        self.player.balance = 100
        self.other.balance = 5
        self.game._collect_from_all(self.player, 10)
        self.assertEqual(self.player.balance, 100)
        self.assertEqual(self.other.balance, 5)
