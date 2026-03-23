"""White-box tests for property transactions, auctions, and menu branches in game.py."""

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


class GamePropertyTransactionWhiteBoxTests(unittest.TestCase):
    def test_handle_property_tile_buy_path(self):
        g = Game(["A"])
        p = g.players[0]
        p.balance = 200
        prop = Property("X", 1, 100, 10)
        with patch("builtins.input", return_value="b"):
            g._handle_property_tile(p, prop)
        self.assertIs(prop.owner, p)

    def test_handle_property_tile_auction_path(self):
        g = Game(["A"])
        p = g.players[0]
        prop = Property("X", 1, 100, 10)
        with patch("builtins.input", return_value="a"), patch.object(g, "auction_property") as auction:
            g._handle_property_tile(p, prop)
        auction.assert_called_once_with(prop)

    def test_handle_property_tile_skip_path(self):
        g = Game(["A"])
        p = g.players[0]
        prop = Property("X", 1, 100, 10)
        with patch("builtins.input", return_value="s"), patch.object(g, "buy_property") as buy, patch.object(g, "auction_property") as auction:
            g._handle_property_tile(p, prop)
        buy.assert_not_called()
        auction.assert_not_called()

    def test_handle_property_tile_owned_by_self_no_rent(self):
        g = Game(["A"])
        p = g.players[0]
        prop = Property("X", 1, 100, 10)
        prop.owner = p
        with patch.object(g, "pay_rent") as rent:
            g._handle_property_tile(p, prop)
        rent.assert_not_called()

    def test_handle_property_tile_owned_by_other_pays_rent(self):
        g = Game(["A", "B"])
        a, b = g.players
        prop = Property("X", 1, 100, 10)
        prop.owner = b
        with patch.object(g, "pay_rent") as rent:
            g._handle_property_tile(a, prop)
        rent.assert_called_once_with(a, prop)

    def test_buy_property_success_and_boundary_failure(self):
        g = Game(["A"])
        p = g.players[0]
        prop = Property("X", 1, 100, 10)

        p.balance = 100
        self.assertTrue(g.buy_property(p, prop))

        # Reset for underfunded branch check.
        prop.owner = None
        p.remove_property(prop)
        p.balance = 99
        self.assertFalse(g.buy_property(p, prop))

    def test_pay_rent_mortgaged_unowned_owned(self):
        g = Game(["A", "B"])
        a, b = g.players
        prop = Property("X", 1, 100, 10)
        a.balance = 100
        g.pay_rent(a, prop)
        self.assertEqual(a.balance, 100)
        prop.owner = b
        prop.is_mortgaged = True
        g.pay_rent(a, prop)
        self.assertEqual(a.balance, 100)
        prop.is_mortgaged = False
        g.pay_rent(a, prop)
        self.assertEqual(a.balance, 90)

    def test_mortgage_property_branches(self):
        g = Game(["A", "B"])
        a, b = g.players
        prop = Property("X", 1, 100, 10)
        self.assertFalse(g.mortgage_property(a, prop))
        prop.owner = a
        self.assertTrue(g.mortgage_property(a, prop))
        self.assertFalse(g.mortgage_property(a, prop))
        self.assertFalse(g.mortgage_property(b, prop))

    def test_unmortgage_property_branches(self):
        g = Game(["A", "B"])
        a, b = g.players
        prop = Property("X", 1, 100, 10)
        self.assertFalse(g.unmortgage_property(a, prop))
        prop.owner = a
        self.assertFalse(g.unmortgage_property(a, prop))
        prop.is_mortgaged = True
        a.balance = 1
        self.assertFalse(g.unmortgage_property(a, prop))
        prop.is_mortgaged = True
        a.balance = 1000
        self.assertTrue(g.unmortgage_property(a, prop))
        self.assertFalse(g.unmortgage_property(b, prop))

    def test_trade_success_and_failures(self):
        g = Game(["A", "B"])
        a, b = g.players
        prop = Property("X", 1, 100, 10)
        self.assertFalse(g.trade(a, b, prop, 50))
        prop.owner = a
        a.add_property(prop)
        b.balance = 10
        self.assertFalse(g.trade(a, b, prop, 50))
        b.balance = 100
        self.assertTrue(g.trade(a, b, prop, 50))
        self.assertIs(prop.owner, b)


class GameAuctionAndMenusWhiteBoxTests(unittest.TestCase):
    def test_auction_no_bids(self):
        g = Game(["A", "B"])
        prop = Property("X", 1, 100, 10)
        with patch("moneypoly.ui.safe_int_input", return_value=0):
            g.auction_property(prop)
        self.assertIsNone(prop.owner)

    def test_auction_highest_valid_bidder_wins(self):
        g = Game(["A", "B", "C"])
        prop = Property("X", 1, 100, 10)
        g.players[0].balance = 100
        g.players[1].balance = 5
        g.players[2].balance = 100
        with patch("moneypoly.ui.safe_int_input", side_effect=[10, 11, 20]):
            g.auction_property(prop)
        self.assertIs(prop.owner, g.players[2])

    def test_interactive_menu_exits_on_zero(self):
        g = Game(["A"])
        with patch("moneypoly.ui.safe_int_input", return_value=0):
            g.interactive_menu(g.players[0])

    def test_interactive_menu_routes_to_view_standings(self):
        g = Game(["A"])
        with patch("moneypoly.ui.safe_int_input", side_effect=[1, 0]), patch("moneypoly.ui.print_standings") as standings:
            g.interactive_menu(g.players[0])
        standings.assert_called_once()

    def test_interactive_menu_routes_to_board_ownership(self):
        g = Game(["A"])
        with patch("moneypoly.ui.safe_int_input", side_effect=[2, 0]), patch("moneypoly.ui.print_board_ownership") as ownership:
            g.interactive_menu(g.players[0])
        ownership.assert_called_once()

    def test_interactive_menu_routes_to_submenus_and_loan(self):
        g = Game(["A"])
        with patch("moneypoly.ui.safe_int_input", side_effect=[3, 4, 5, 6, 50, 0]), patch.object(g, "_menu_mortgage") as mm, patch.object(g, "_menu_unmortgage") as mu, patch.object(g, "_menu_trade") as mt, patch.object(g.bank, "give_loan") as loan:
            g.interactive_menu(g.players[0])
        mm.assert_called_once()
        mu.assert_called_once()
        mt.assert_called_once()
        loan.assert_called_once()

    def test_menu_mortgage_no_candidates(self):
        g = Game(["A"])
        p = g.players[0]
        g._menu_mortgage(p)

    def test_menu_mortgage_selected(self):
        g = Game(["A"])
        p = g.players[0]
        prop = Property("X", 1, 100, 10)
        prop.owner = p
        p.properties.append(prop)
        with patch("moneypoly.ui.safe_int_input", return_value=1), patch.object(g, "mortgage_property") as mortgage:
            g._menu_mortgage(p)
        mortgage.assert_called_once_with(p, prop)

    def test_menu_unmortgage_no_candidates(self):
        g = Game(["A"])
        p = g.players[0]
        g._menu_unmortgage(p)

    def test_menu_unmortgage_selected(self):
        g = Game(["A"])
        p = g.players[0]
        prop = Property("X", 1, 100, 10)
        prop.owner = p
        prop.is_mortgaged = True
        p.properties.append(prop)
        with patch("moneypoly.ui.safe_int_input", return_value=1), patch.object(g, "unmortgage_property") as unm:
            g._menu_unmortgage(p)
        unm.assert_called_once_with(p, prop)

    def test_menu_trade_no_other_players(self):
        g = Game(["A"])
        g._menu_trade(g.players[0])

    def test_menu_trade_invalid_partner_index(self):
        g = Game(["A", "B"])
        with patch("moneypoly.ui.safe_int_input", return_value=99):
            g._menu_trade(g.players[0])

    def test_menu_trade_no_properties(self):
        g = Game(["A", "B"])
        with patch("moneypoly.ui.safe_int_input", return_value=1):
            g._menu_trade(g.players[0])

    def test_menu_trade_invalid_property_index(self):
        g = Game(["A", "B"])
        p = g.players[0]
        prop = Property("X", 1, 100, 10)
        p.properties.append(prop)
        with patch("moneypoly.ui.safe_int_input", side_effect=[1, 99]):
            g._menu_trade(p)

    def test_menu_trade_success_path(self):
        g = Game(["A", "B"])
        a, b = g.players
        prop = Property("X", 1, 100, 10)
        a.properties.append(prop)
        with patch("moneypoly.ui.safe_int_input", side_effect=[1, 1, 50]), patch.object(g, "trade") as trade:
            g._menu_trade(a)
        trade.assert_called_once_with(a, b, prop, 50)


if __name__ == "__main__":
    unittest.main()
