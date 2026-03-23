"""White-box tests derived from the reference report issues and passing cases."""

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

from moneypoly.cards import CardDeck
from moneypoly.game import Game
from moneypoly.player import Player
from moneypoly.property import Property
import main as moneypoly_main


class ReferenceReportPlayerNetWorthTests(unittest.TestCase):
    def test_net_worth_includes_property_values(self):
        player = Player("A", balance=100)
        prop = Property("X", 1, 200, 10)
        prop.owner = player
        player.add_property(prop)
        self.assertEqual(player.net_worth(), 300)

    def test_net_worth_uses_mortgage_value_for_mortgaged(self):
        player = Player("A", balance=100)
        prop = Property("X", 1, 200, 10)
        prop.owner = player
        prop.is_mortgaged = True
        player.add_property(prop)
        self.assertEqual(player.net_worth(), 200)


class ReferenceReportAuctionAndBuyTests(unittest.TestCase):
    def test_buy_property_rejects_already_owned_property(self):
        game = Game(["A", "B"])
        buyer = game.players[0]
        owner = game.players[1]
        prop = Property("X", 1, 100, 10)
        prop.owner = owner
        owner.add_property(prop)

        result = game.buy_property(buyer, prop)
        self.assertFalse(result)
        self.assertIs(prop.owner, owner)

    def test_auction_property_rejects_already_owned_property(self):
        game = Game(["A", "B"])
        owner = game.players[0]
        prop = Property("X", 1, 100, 10)
        prop.owner = owner
        owner.add_property(prop)

        with patch("moneypoly.ui.safe_int_input") as prompt:
            game.auction_property(prop)
        prompt.assert_not_called()
        self.assertIs(prop.owner, owner)


class ReferenceReportInteractiveMenuTests(unittest.TestCase):
    def test_interactive_menu_loan_over_limit_does_not_crash(self):
        game = Game(["A"])
        game.bank._funds = 10
        with patch("moneypoly.ui.safe_int_input", side_effect=[6, 100, 0]):
            game.interactive_menu(game.players[0])
        self.assertEqual(game.bank.get_balance(), 10)


class ReferenceReportCardAndDeckTests(unittest.TestCase):
    def test_card_collect_insufficient_bank_funds_is_safe(self):
        game = Game(["A"])
        player = game.players[0]
        game.bank._funds = 0
        starting_balance = player.balance
        game._card_collect(player, 50)
        self.assertEqual(player.balance, starting_balance)

    def test_apply_card_missing_action_is_ignored(self):
        game = Game(["A"])
        player = game.players[0]
        starting_balance = player.balance
        game._apply_card(player, {"description": "Bad"})
        self.assertEqual(player.balance, starting_balance)

    def test_apply_card_missing_value_defaults_to_zero(self):
        game = Game(["A"])
        player = game.players[0]
        starting_balance = player.balance
        game._apply_card(player, {"description": "Safe", "action": "collect"})
        self.assertEqual(player.balance, starting_balance)

    def test_carddeck_repr_safe_when_empty(self):
        deck = CardDeck([])
        self.assertIn("next=none", repr(deck))


class ReferenceReportMainEntryTests(unittest.TestCase):
    def test_main_rejects_less_than_two_players(self):
        with patch("builtins.input", return_value="Solo"), patch("builtins.print") as printer:
            moneypoly_main.main()
        printed = " ".join(str(call.args[0]) for call in printer.call_args_list if call.args)
        self.assertIn("Setup error", printed)


if __name__ == "__main__":
    unittest.main()
