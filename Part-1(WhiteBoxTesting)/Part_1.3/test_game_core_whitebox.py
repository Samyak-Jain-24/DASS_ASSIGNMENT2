"""White-box tests for core Game turn flow and winner/bankruptcy logic."""

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

from moneypoly.game import Game
from moneypoly.property import Property


class GameTurnFlowWhiteBoxTests(unittest.TestCase):
    def test_current_player_and_advance(self):
        g = Game(["A", "B"])
        self.assertEqual(g.current_player().name, "A")
        g.advance_turn()
        self.assertEqual(g.current_player().name, "B")
        self.assertEqual(g.turn_number, 1)

    def test_play_turn_jailed_player_uses_jail_handler_and_advances(self):
        g = Game(["A", "B"])
        p = g.players[0]
        p.in_jail = True
        with patch.object(g, "_handle_jail_turn") as jail_handler:
            g.play_turn()
        jail_handler.assert_called_once_with(p)
        self.assertEqual(g.current_index, 1)

    def test_play_turn_three_doubles_sends_to_jail(self):
        g = Game(["A", "B"])
        p = g.players[0]
        g.dice.doubles_streak = 3
        with patch.object(g.dice, "roll", return_value=6), patch.object(g.dice, "describe", return_value="3+3"), patch.object(g, "_move_and_resolve"):
            g.play_turn()
        self.assertTrue(p.in_jail)
        self.assertEqual(g.current_index, 1)

    def test_play_turn_doubles_extra_turn_no_advance(self):
        g = Game(["A", "B"])
        with patch.object(g.dice, "roll", return_value=4), patch.object(g.dice, "describe", return_value="2+2"), patch.object(g.dice, "is_doubles", return_value=True), patch.object(g, "_move_and_resolve"):
            g.play_turn()
        self.assertEqual(g.current_index, 0)

    def test_play_turn_non_doubles_advances(self):
        g = Game(["A", "B"])
        with patch.object(g.dice, "roll", return_value=5), patch.object(g.dice, "describe", return_value="2+3"), patch.object(g.dice, "is_doubles", return_value=False), patch.object(g, "_move_and_resolve"):
            g.play_turn()
        self.assertEqual(g.current_index, 1)


class GameBankruptcyWinnerWhiteBoxTests(unittest.TestCase):
    def test_check_bankruptcy_non_bankrupt_does_nothing(self):
        g = Game(["A", "B"])
        p = g.players[0]
        p.balance = 1
        g._check_bankruptcy(p)
        self.assertIn(p, g.players)

    def test_check_bankruptcy_removes_player_and_resets_props(self):
        g = Game(["A", "B"])
        p = g.players[0]
        prop = Property("X", 1, 100, 10)
        prop.owner = p
        prop.is_mortgaged = True
        p.properties.append(prop)
        p.balance = -1
        g._check_bankruptcy(p)
        self.assertNotIn(p, g.players)
        self.assertIsNone(prop.owner)
        self.assertFalse(prop.is_mortgaged)
        self.assertTrue(p.is_eliminated)

    def test_check_bankruptcy_resets_current_index_when_out_of_range(self):
        g = Game(["A", "B"])
        g.current_index = 1
        p = g.players[1]
        p.balance = -1
        g._check_bankruptcy(p)
        self.assertEqual(g.current_index, 0)

    def test_find_winner_none_when_no_players(self):
        g = Game(["A", "B"])
        g.players = []
        self.assertIsNone(g.find_winner())

    def test_find_winner_should_pick_richest(self):
        g = Game(["A", "B"])
        g.players[0].balance = 10
        g.players[1].balance = 200
        winner = g.find_winner()
        self.assertEqual(winner.name, "B")

    def test_run_breaks_immediately_with_single_player(self):
        g = Game(["Solo"])
        with patch.object(g, "play_turn") as play_turn:
            g.run()
        play_turn.assert_not_called()


if __name__ == "__main__":
    unittest.main()
