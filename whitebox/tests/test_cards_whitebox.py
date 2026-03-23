"""White-box tests for cards.py and CardDeck behavior."""

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

from moneypoly.cards import CardDeck, CHANCE_CARDS, COMMUNITY_CHEST_CARDS


class CardDataShapeTests(unittest.TestCase):
    def test_chance_cards_have_required_keys(self):
        for card in CHANCE_CARDS:
            self.assertIn("description", card)
            self.assertIn("action", card)
            self.assertIn("value", card)

    def test_community_cards_have_required_keys(self):
        for card in COMMUNITY_CHEST_CARDS:
            self.assertIn("description", card)
            self.assertIn("action", card)
            self.assertIn("value", card)

    def test_card_actions_are_known_set(self):
        allowed = {"collect", "pay", "jail", "jail_free", "move_to", "birthday", "collect_from_all"}
        for card in CHANCE_CARDS + COMMUNITY_CHEST_CARDS:
            self.assertIn(card["action"], allowed)


class CardDeckWhiteBoxTests(unittest.TestCase):
    def test_len_matches_input_cards(self):
        deck = CardDeck([{"description": "A", "action": "collect", "value": 1}])
        self.assertEqual(len(deck), 1)

    def test_draw_none_when_empty(self):
        deck = CardDeck([])
        self.assertIsNone(deck.draw())

    def test_peek_none_when_empty(self):
        deck = CardDeck([])
        self.assertIsNone(deck.peek())

    def test_cards_remaining_empty_expected_zero(self):
        deck = CardDeck([])
        self.assertEqual(deck.cards_remaining(), 0)

    def test_peek_does_not_advance(self):
        cards = [
            {"description": "A", "action": "collect", "value": 1},
            {"description": "B", "action": "pay", "value": 2},
        ]
        deck = CardDeck(cards)
        p1 = deck.peek()
        p2 = deck.peek()
        self.assertEqual(p1["description"], "A")
        self.assertEqual(p2["description"], "A")

    def test_draw_advances(self):
        cards = [
            {"description": "A", "action": "collect", "value": 1},
            {"description": "B", "action": "pay", "value": 2},
        ]
        deck = CardDeck(cards)
        c1 = deck.draw()
        c2 = deck.draw()
        self.assertEqual(c1["description"], "A")
        self.assertEqual(c2["description"], "B")

    def test_draw_cycles_when_exhausted(self):
        cards = [
            {"description": "A", "action": "collect", "value": 1},
            {"description": "B", "action": "pay", "value": 2},
        ]
        deck = CardDeck(cards)
        deck.draw()
        deck.draw()
        c3 = deck.draw()
        self.assertEqual(c3["description"], "A")

    def test_cards_remaining_counts_down_and_wraps(self):
        cards = [
            {"description": "A", "action": "collect", "value": 1},
            {"description": "B", "action": "pay", "value": 2},
            {"description": "C", "action": "pay", "value": 3},
        ]
        deck = CardDeck(cards)
        self.assertEqual(deck.cards_remaining(), 3)
        deck.draw()
        self.assertEqual(deck.cards_remaining(), 2)
        deck.draw()
        self.assertEqual(deck.cards_remaining(), 1)
        deck.draw()
        self.assertEqual(deck.cards_remaining(), 3)

    def test_reshuffle_resets_index(self):
        cards = [
            {"description": "A", "action": "collect", "value": 1},
            {"description": "B", "action": "pay", "value": 2},
        ]
        deck = CardDeck(cards)
        deck.draw()
        self.assertEqual(deck.cards_remaining(), 1)
        with patch("moneypoly.cards.random.shuffle"):
            deck.reshuffle()
        self.assertEqual(deck.cards_remaining(), 2)


if __name__ == "__main__":
    unittest.main()
