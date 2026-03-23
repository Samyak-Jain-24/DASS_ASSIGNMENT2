"""White-box tests for Game tile resolution, card actions, and jail branches."""

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

from moneypoly.config import GO_SALARY, INCOME_TAX_AMOUNT, JAIL_FINE, JAIL_POSITION, LUXURY_TAX_AMOUNT
from moneypoly.game import Game
from moneypoly.property import Property


class GameMoveResolveWhiteBoxTests(unittest.TestCase):
    def test_move_resolve_income_tax(self):
        g = Game(["A"])
        p = g.players[0]
        start_balance = p.balance
        start_bank = g.bank.get_balance()
        with patch.object(g.board, "get_tile_type", return_value="income_tax"):
            g._move_and_resolve(p, 1)
        self.assertEqual(p.balance, start_balance - INCOME_TAX_AMOUNT)
        self.assertEqual(g.bank.get_balance(), start_bank + INCOME_TAX_AMOUNT)

    def test_move_resolve_luxury_tax(self):
        g = Game(["A"])
        p = g.players[0]
        start_balance = p.balance
        start_bank = g.bank.get_balance()
        with patch.object(g.board, "get_tile_type", return_value="luxury_tax"):
            g._move_and_resolve(p, 1)
        self.assertEqual(p.balance, start_balance - LUXURY_TAX_AMOUNT)
        self.assertEqual(g.bank.get_balance(), start_bank + LUXURY_TAX_AMOUNT)

    def test_move_resolve_go_to_jail(self):
        g = Game(["A"])
        p = g.players[0]
        with patch.object(g.board, "get_tile_type", return_value="go_to_jail"):
            g._move_and_resolve(p, 1)
        self.assertTrue(p.in_jail)
        self.assertEqual(p.position, JAIL_POSITION)

    def test_move_resolve_free_parking_no_money_change(self):
        g = Game(["A"])
        p = g.players[0]
        start_balance = p.balance
        with patch.object(g.board, "get_tile_type", return_value="free_parking"):
            g._move_and_resolve(p, 1)
        self.assertEqual(p.balance, start_balance)

    def test_move_resolve_chance_draws_card(self):
        g = Game(["A"])
        p = g.players[0]
        with patch.object(g.board, "get_tile_type", return_value="chance"), patch.object(g.chance_deck, "draw", return_value={"description": "X", "action": "collect", "value": 1}) as draw, patch.object(g, "_apply_card") as apply:
            g._move_and_resolve(p, 1)
        draw.assert_called_once()
        apply.assert_called_once()

    def test_move_resolve_community_draws_card(self):
        g = Game(["A"])
        p = g.players[0]
        with patch.object(g.board, "get_tile_type", return_value="community_chest"), patch.object(g.community_deck, "draw", return_value={"description": "X", "action": "collect", "value": 1}) as draw, patch.object(g, "_apply_card") as apply:
            g._move_and_resolve(p, 1)
        draw.assert_called_once()
        apply.assert_called_once()

    def test_move_resolve_property_calls_property_handler_when_prop_exists(self):
        g = Game(["A"])
        p = g.players[0]
        prop = Property("X", 1, 100, 10)
        with patch.object(g.board, "get_tile_type", return_value="property"), patch.object(g.board, "get_property_at", return_value=prop), patch.object(g, "_handle_property_tile") as handler:
            g._move_and_resolve(p, 1)
        handler.assert_called_once_with(p, prop)

    def test_move_resolve_property_skips_when_no_prop(self):
        g = Game(["A"])
        p = g.players[0]
        with patch.object(g.board, "get_tile_type", return_value="property"), patch.object(g.board, "get_property_at", return_value=None), patch.object(g, "_handle_property_tile") as handler:
            g._move_and_resolve(p, 1)
        handler.assert_not_called()

    def test_move_resolve_railroad_calls_property_handler(self):
        g = Game(["A"])
        p = g.players[0]
        prop = Property("R", 5, 200, 25)
        with patch.object(g.board, "get_tile_type", return_value="railroad"), patch.object(g.board, "get_property_at", return_value=prop), patch.object(g, "_handle_property_tile") as handler:
            g._move_and_resolve(p, 1)
        handler.assert_called_once_with(p, prop)


class GameCardActionWhiteBoxTests(unittest.TestCase):
    def test_apply_card_none_noop(self):
        g = Game(["A"])
        p = g.players[0]
        start = p.balance
        g._apply_card(p, None)
        self.assertEqual(p.balance, start)

    def test_apply_card_collect(self):
        g = Game(["A"])
        p = g.players[0]
        start = p.balance
        g._apply_card(p, {"description": "C", "action": "collect", "value": 50})
        self.assertEqual(p.balance, start + 50)

    def test_apply_card_pay(self):
        g = Game(["A"])
        p = g.players[0]
        start = p.balance
        g._apply_card(p, {"description": "P", "action": "pay", "value": 20})
        self.assertEqual(p.balance, start - 20)

    def test_apply_card_jail(self):
        g = Game(["A"])
        p = g.players[0]
        g._apply_card(p, {"description": "J", "action": "jail", "value": 0})
        self.assertTrue(p.in_jail)

    def test_apply_card_jail_free(self):
        g = Game(["A"])
        p = g.players[0]
        before = p.get_out_of_jail_cards
        g._apply_card(p, {"description": "F", "action": "jail_free", "value": 0})
        self.assertEqual(p.get_out_of_jail_cards, before + 1)

    def test_apply_card_move_to_passing_go_gives_salary(self):
        g = Game(["A"])
        p = g.players[0]
        p.position = 10
        p.balance = 0
        with patch.object(g.board, "get_tile_type", return_value="blank"):
            g._apply_card(p, {"description": "M", "action": "move_to", "value": 0})
        self.assertEqual(p.position, 0)
        self.assertEqual(p.balance, GO_SALARY)

    def test_apply_card_move_to_property_invokes_property_handler(self):
        g = Game(["A"])
        p = g.players[0]
        prop = Property("X", 1, 100, 10)
        with patch.object(g.board, "get_tile_type", return_value="property"), patch.object(g.board, "get_property_at", return_value=prop), patch.object(g, "_handle_property_tile") as handler:
            g._apply_card(p, {"description": "M", "action": "move_to", "value": 1})
        handler.assert_called_once_with(p, prop)

    def test_apply_card_birthday_only_collects_from_players_who_can_pay(self):
        g = Game(["A", "B", "C"])
        a, b, c = g.players
        a.balance = 0
        b.balance = 5
        c.balance = 30
        g._apply_card(a, {"description": "B", "action": "birthday", "value": 10})
        self.assertEqual(a.balance, 10)
        self.assertEqual(b.balance, 5)
        self.assertEqual(c.balance, 20)

    def test_apply_card_collect_from_all_only_collects_from_players_who_can_pay(self):
        g = Game(["A", "B", "C"])
        a, b, c = g.players
        a.balance = 0
        b.balance = 100
        c.balance = 1
        g._apply_card(a, {"description": "A", "action": "collect_from_all", "value": 20})
        self.assertEqual(a.balance, 20)
        self.assertEqual(b.balance, 80)
        self.assertEqual(c.balance, 1)


class GameJailTurnWhiteBoxTests(unittest.TestCase):
    def test_jail_turn_use_card_yes(self):
        g = Game(["A"])
        p = g.players[0]
        p.in_jail = True
        p.get_out_of_jail_cards = 1
        with patch("moneypoly.ui.confirm", side_effect=[True]), patch.object(g.dice, "roll", return_value=4), patch.object(g, "_move_and_resolve") as move:
            g._handle_jail_turn(p)
        self.assertFalse(p.in_jail)
        self.assertEqual(p.get_out_of_jail_cards, 0)
        move.assert_called_once()

    def test_jail_turn_card_no_then_pay_yes(self):
        g = Game(["A"])
        p = g.players[0]
        p.in_jail = True
        p.get_out_of_jail_cards = 1
        start_bank = g.bank.get_balance()
        with patch("moneypoly.ui.confirm", side_effect=[False, True]), patch.object(g.dice, "roll", return_value=3), patch.object(g, "_move_and_resolve") as move:
            g._handle_jail_turn(p)
        self.assertFalse(p.in_jail)
        self.assertEqual(g.bank.get_balance(), start_bank + JAIL_FINE)
        move.assert_called_once()

    def test_jail_turn_no_action_under_three_turns(self):
        g = Game(["A"])
        p = g.players[0]
        p.in_jail = True
        p.jail_turns = 1
        with patch("moneypoly.ui.confirm", return_value=False):
            g._handle_jail_turn(p)
        self.assertTrue(p.in_jail)
        self.assertEqual(p.jail_turns, 2)

    def test_jail_turn_mandatory_release_on_third_turn(self):
        g = Game(["A"])
        p = g.players[0]
        p.in_jail = True
        p.jail_turns = 2
        p.balance = 100
        with patch("moneypoly.ui.confirm", return_value=False), patch.object(g.dice, "roll", return_value=4), patch.object(g, "_move_and_resolve") as move:
            g._handle_jail_turn(p)
        self.assertFalse(p.in_jail)
        self.assertEqual(p.jail_turns, 0)
        self.assertEqual(p.balance, 100 - JAIL_FINE)
        move.assert_called_once()


if __name__ == "__main__":
    unittest.main()
