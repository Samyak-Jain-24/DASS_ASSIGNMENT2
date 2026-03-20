"""Exhaustive white-box tests for remaining fine-grained branches and states."""

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
from moneypoly.config import (
    AUCTION_MIN_INCREMENT,
    BANK_STARTING_FUNDS,
    BOARD_SIZE,
    FREE_PARKING_POSITION,
    GO_SALARY,
    GO_TO_JAIL_POSITION,
    INCOME_TAX_AMOUNT,
    INCOME_TAX_POSITION,
    JAIL_FINE,
    JAIL_POSITION,
    LUXURY_TAX_AMOUNT,
    LUXURY_TAX_POSITION,
    MAX_TURNS,
    STARTING_BALANCE,
)
from moneypoly.game import Game
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup


class ConfigAndReprTests(unittest.TestCase):
    """Cover constants and repr/format paths that are easy to miss."""

    def test_config_constants_sanity(self):
        self.assertGreater(STARTING_BALANCE, 0)
        self.assertEqual(BOARD_SIZE, 40)
        self.assertGreater(GO_SALARY, 0)
        self.assertGreater(MAX_TURNS, 0)
        self.assertGreater(BANK_STARTING_FUNDS, 0)
        self.assertGreater(AUCTION_MIN_INCREMENT, 0)
        self.assertIn(JAIL_POSITION, range(BOARD_SIZE))
        self.assertIn(GO_TO_JAIL_POSITION, range(BOARD_SIZE))
        self.assertIn(FREE_PARKING_POSITION, range(BOARD_SIZE))
        self.assertIn(INCOME_TAX_POSITION, range(BOARD_SIZE))
        self.assertIn(LUXURY_TAX_POSITION, range(BOARD_SIZE))
        self.assertGreater(INCOME_TAX_AMOUNT, 0)
        self.assertGreater(LUXURY_TAX_AMOUNT, 0)
        self.assertGreater(JAIL_FINE, 0)

    def test_repr_methods_are_stable_for_non_empty_objects(self):
        player = Player("Alice")
        prop = Property("X", 1, 100, 10)
        group = PropertyGroup("Blue", "blue")
        bank = Bank()
        board = Board()
        deck = CardDeck([{"description": "A", "action": "collect", "value": 1}])

        self.assertIn("Player", repr(player))
        self.assertIn("Property", repr(prop))
        self.assertIn("PropertyGroup", repr(group))
        self.assertIn("Bank", repr(bank))
        self.assertIn("Board", repr(board))
        self.assertIn("CardDeck", repr(deck))


class CardDeckEdgeBranchTests(unittest.TestCase):
    """Cover additional edge branches in card deck progression."""

    def test_cards_remaining_after_multiple_cycles(self):
        cards = [
            {"description": "A", "action": "collect", "value": 1},
            {"description": "B", "action": "pay", "value": 2},
        ]
        deck = CardDeck(cards)
        for _ in range(7):
            deck.draw()
        # 7 draws on 2-card deck => index=7 => next card is B and 1 card remaining in cycle
        self.assertEqual(deck.cards_remaining(), 1)
        self.assertEqual(deck.peek()["description"], "B")

    def test_draw_empty_then_reshuffle_stays_safe(self):
        deck = CardDeck([])
        self.assertIsNone(deck.draw())
        deck.reshuffle()
        self.assertIsNone(deck.peek())


class GameFineBranchTests(unittest.TestCase):
    """Cover branches that are less visible in the main flow tests."""

    def test_move_and_resolve_blank_tile_only_checks_bankruptcy(self):
        game = Game(["A"])
        player = game.players[0]

        with patch.object(game.board, "get_tile_type", return_value="blank"), patch.object(game, "_check_bankruptcy") as chk:
            game._move_and_resolve(player, 1)
        chk.assert_called_once_with(player)

    def test_move_and_resolve_chance_with_none_card(self):
        game = Game(["A"])
        player = game.players[0]

        with patch.object(game.board, "get_tile_type", return_value="chance"), patch.object(game.chance_deck, "draw", return_value=None), patch.object(game, "_apply_card") as app:
            game._move_and_resolve(player, 1)
        app.assert_called_once_with(player, None)

    def test_apply_card_move_to_property_tile_but_no_property_object(self):
        game = Game(["A"])
        player = game.players[0]

        with patch.object(game.board, "get_tile_type", return_value="property"), patch.object(game.board, "get_property_at", return_value=None), patch.object(game, "_handle_property_tile") as handler:
            game._apply_card(player, {"description": "Move", "action": "move_to", "value": 1})
        handler.assert_not_called()

    def test_apply_card_birthday_does_not_charge_current_player(self):
        game = Game(["A", "B"])
        a, b = game.players
        a.balance = 0
        b.balance = 20

        game._apply_card(a, {"description": "Birthday", "action": "birthday", "value": 10})
        self.assertEqual(a.balance, 10)
        self.assertEqual(b.balance, 10)

    def test_apply_card_collect_from_all_does_not_charge_current_player(self):
        game = Game(["A", "B"])
        a, b = game.players
        a.balance = 0
        b.balance = 20

        game._apply_card(a, {"description": "Collect", "action": "collect_from_all", "value": 10})
        self.assertEqual(a.balance, 10)
        self.assertEqual(b.balance, 10)

    def test_interactive_menu_ignores_unknown_choice(self):
        game = Game(["A"])
        player = game.players[0]

        with patch("moneypoly.ui.safe_int_input", side_effect=[9, 0]):
            game.interactive_menu(player)

    def test_check_bankruptcy_when_last_player_removed(self):
        game = Game(["Solo"])
        player = game.players[0]
        player.balance = -1

        game._check_bankruptcy(player)
        self.assertEqual(game.players, [])
        self.assertEqual(game.current_index, 0)

    def test_run_exits_when_running_flag_false(self):
        game = Game(["A", "B"])
        game.running = False

        with patch.object(game, "play_turn") as play:
            out = io.StringIO()
            with redirect_stdout(out):
                game.run()
        play.assert_not_called()


class MenuAndAuctionEdgeTests(unittest.TestCase):
    """Cover additional selection and bid edge paths."""

    def test_menu_trade_negative_cash_still_routes_to_trade(self):
        game = Game(["A", "B"])
        a, b = game.players
        prop = Property("X", 1, 100, 10)
        a.properties.append(prop)

        with patch("moneypoly.ui.safe_int_input", side_effect=[1, 1, -50]), patch.object(game, "trade") as trade:
            game._menu_trade(a)
        trade.assert_called_once_with(a, b, prop, -50)

    def test_auction_rejects_equal_to_current_high_without_min_increment(self):
        game = Game(["A", "B"])
        prop = Property("X", 1, 100, 10)
        game.players[0].balance = 100
        game.players[1].balance = 100

        # First bid 10 accepted. Second bid 10 should be rejected (min raise required).
        with patch("moneypoly.ui.safe_int_input", side_effect=[10, 10]):
            game.auction_property(prop)

        # First bidder should remain the winner at 10.
        self.assertIs(prop.owner, game.players[0])

    def test_menu_mortgage_handles_default_zero_selection(self):
        game = Game(["A"])
        player = game.players[0]
        prop = Property("X", 1, 100, 10)
        prop.owner = player
        player.properties.append(prop)

        with patch("moneypoly.ui.safe_int_input", return_value=0), patch.object(game, "mortgage_property") as mort:
            game._menu_mortgage(player)
        mort.assert_not_called()

    def test_menu_unmortgage_handles_default_zero_selection(self):
        game = Game(["A"])
        player = game.players[0]
        prop = Property("X", 1, 100, 10)
        prop.owner = player
        prop.is_mortgaged = True
        player.properties.append(prop)

        with patch("moneypoly.ui.safe_int_input", return_value=0), patch.object(game, "unmortgage_property") as unm:
            game._menu_unmortgage(player)
        unm.assert_not_called()


if __name__ == "__main__":
    unittest.main()
