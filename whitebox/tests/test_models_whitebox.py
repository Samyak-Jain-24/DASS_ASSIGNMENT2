"""White-box tests for model modules: player.py and property.py."""

from __future__ import annotations

import os
import sys
import unittest

CURRENT_DIR = os.path.dirname(__file__)
PART1_ROOT = os.path.dirname(CURRENT_DIR)
OUTER_MONEYPOLY = os.path.join(PART1_ROOT, "moneypoly")
if OUTER_MONEYPOLY not in sys.path:
    sys.path.insert(0, OUTER_MONEYPOLY)

from moneypoly.config import BOARD_SIZE, GO_SALARY, JAIL_POSITION
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup


class PlayerWhiteBoxTests(unittest.TestCase):
    def test_player_defaults(self):
        p = Player("Alice")
        self.assertEqual(p.name, "Alice")
        self.assertEqual(p.position, 0)
        self.assertEqual(p.count_properties(), 0)
        self.assertFalse(p.in_jail)
        self.assertFalse(p.is_eliminated)

    def test_add_money_positive(self):
        p = Player("A", balance=10)
        p.add_money(5)
        self.assertEqual(p.balance, 15)

    def test_add_money_negative_raises(self):
        p = Player("A")
        with self.assertRaises(ValueError):
            p.add_money(-1)

    def test_deduct_money_positive(self):
        p = Player("A", balance=10)
        p.deduct_money(3)
        self.assertEqual(p.balance, 7)

    def test_deduct_money_negative_raises(self):
        p = Player("A")
        with self.assertRaises(ValueError):
            p.deduct_money(-1)

    def test_is_bankrupt_true_at_zero(self):
        p = Player("A", balance=0)
        self.assertTrue(p.is_bankrupt())

    def test_is_bankrupt_false_above_zero(self):
        p = Player("A", balance=1)
        self.assertFalse(p.is_bankrupt())

    def test_net_worth_matches_balance(self):
        p = Player("A", balance=123)
        self.assertEqual(p.net_worth(), 123)

    def test_move_wraps_board(self):
        p = Player("A", balance=0)
        p.position = BOARD_SIZE - 1
        new_pos = p.move(3)
        self.assertEqual(new_pos, 2)

    def test_move_landing_on_go_collects_salary(self):
        p = Player("A", balance=0)
        p.position = BOARD_SIZE - 2
        new_pos = p.move(2)
        self.assertEqual(new_pos, 0)
        self.assertEqual(p.balance, GO_SALARY)

    def test_go_to_jail_updates_all_jail_state(self):
        p = Player("A")
        p.jail_turns = 2
        p.go_to_jail()
        self.assertEqual(p.position, JAIL_POSITION)
        self.assertTrue(p.in_jail)
        self.assertEqual(p.jail_turns, 0)

    def test_add_remove_property_idempotent(self):
        p = Player("A")
        prop = Property("X", 1, 100, 10)
        p.add_property(prop)
        p.add_property(prop)
        self.assertEqual(p.count_properties(), 1)
        p.remove_property(prop)
        p.remove_property(prop)
        self.assertEqual(p.count_properties(), 0)

    def test_status_line_contains_jail_tag_when_jailed(self):
        p = Player("A")
        p.in_jail = True
        self.assertIn("[JAILED]", p.status_line())

    def test_status_line_omits_jail_tag_when_free(self):
        p = Player("A")
        self.assertNotIn("[JAILED]", p.status_line())


class PropertyWhiteBoxTests(unittest.TestCase):
    def test_property_defaults(self):
        prop = Property("X", 1, 100, 10)
        self.assertIsNone(prop.owner)
        self.assertFalse(prop.is_mortgaged)
        self.assertEqual(prop.mortgage_value, 50)

    def test_group_registration_happens_in_constructor(self):
        g = PropertyGroup("Brown", "brown")
        prop = Property("X", 1, 100, 10, group=g)
        self.assertIn(prop, g.properties)

    def test_get_rent_base_no_group(self):
        prop = Property("X", 1, 100, 10)
        self.assertEqual(prop.get_rent(), 10)

    def test_get_rent_zero_when_mortgaged(self):
        prop = Property("X", 1, 100, 10)
        prop.is_mortgaged = True
        self.assertEqual(prop.get_rent(), 0)

    def test_get_rent_doubles_with_full_group_owned(self):
        g = PropertyGroup("Brown", "brown")
        p1 = Property("A", 1, 60, 2, group=g)
        p2 = Property("B", 3, 60, 4, group=g)
        owner = Player("Owner")
        p1.owner = owner
        p2.owner = owner
        self.assertEqual(p1.get_rent(), 4)
        self.assertEqual(p2.get_rent(), 8)

    def test_get_rent_not_doubled_with_partial_group(self):
        g = PropertyGroup("Brown", "brown")
        p1 = Property("A", 1, 60, 2, group=g)
        Property("B", 3, 60, 4, group=g)
        owner = Player("Owner")
        p1.owner = owner
        self.assertEqual(p1.get_rent(), 2)

    def test_mortgage_success_then_repeat_returns_zero(self):
        prop = Property("X", 1, 100, 10)
        self.assertEqual(prop.mortgage(), 50)
        self.assertTrue(prop.is_mortgaged)
        self.assertEqual(prop.mortgage(), 0)

    def test_unmortgage_when_not_mortgaged_returns_zero(self):
        prop = Property("X", 1, 100, 10)
        self.assertEqual(prop.unmortgage(), 0)

    def test_unmortgage_success_clears_flag(self):
        prop = Property("X", 1, 100, 10)
        prop.mortgage()
        self.assertEqual(prop.unmortgage(), 55)
        self.assertFalse(prop.is_mortgaged)

    def test_is_available_true_only_unowned_unmortgaged(self):
        prop = Property("X", 1, 100, 10)
        self.assertTrue(prop.is_available())
        prop.owner = Player("O")
        self.assertFalse(prop.is_available())
        prop.owner = None
        prop.is_mortgaged = True
        self.assertFalse(prop.is_available())

    def test_group_all_owned_by_false_for_none(self):
        g = PropertyGroup("Red", "red")
        Property("A", 1, 100, 10, group=g)
        self.assertFalse(g.all_owned_by(None))

    def test_group_all_owned_by_true_when_all_match(self):
        g = PropertyGroup("Red", "red")
        p1 = Property("A", 1, 100, 10, group=g)
        p2 = Property("B", 2, 100, 10, group=g)
        owner = Player("O")
        p1.owner = owner
        p2.owner = owner
        self.assertTrue(g.all_owned_by(owner))

    def test_group_add_property_backlinks_and_prevents_duplicates(self):
        g = PropertyGroup("Red", "red")
        p = Property("A", 1, 100, 10)
        g.add_property(p)
        g.add_property(p)
        self.assertEqual(g.size(), 1)
        self.assertIs(p.group, g)

    def test_group_owner_counts_only_counts_non_none(self):
        g = PropertyGroup("Red", "red")
        p1 = Property("A", 1, 100, 10, group=g)
        p2 = Property("B", 2, 100, 10, group=g)
        o = Player("O")
        p1.owner = o
        counts = g.get_owner_counts()
        self.assertEqual(counts[o], 1)
        self.assertEqual(len(counts), 1)


if __name__ == "__main__":
    unittest.main()
