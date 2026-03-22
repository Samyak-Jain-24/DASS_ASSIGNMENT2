"""Player model for the MoneyPoly game."""

from moneypoly.config import STARTING_BALANCE, BOARD_SIZE, GO_SALARY, JAIL_POSITION


class Player:
    """Represents a single player in a MoneyPoly game."""

    def __init__(self, name, balance=STARTING_BALANCE):
        self._state = {
            "name": name,
            "balance": balance,
            "position": 0,
            "properties": [],
            "is_eliminated": False,
            "in_jail": False,
            "jail_turns": 0,
            "cards": 0,
        }

    @property
    def name(self):
        """Return the player's name."""
        return self._state["name"]

    @name.setter
    def name(self, value):
        """Update the player's name."""
        self._state["name"] = value

    @property
    def balance(self):
        """Return the player's current cash balance."""
        return self._state["balance"]

    @balance.setter
    def balance(self, value):
        """Update the player's cash balance."""
        self._state["balance"] = value

    @property
    def position(self):
        """Return the player's current board position."""
        return self._state["position"]

    @position.setter
    def position(self, value):
        """Update the player's board position."""
        self._state["position"] = value

    @property
    def properties(self):
        """Return the list of properties owned by this player."""
        return self._state["properties"]

    @properties.setter
    def properties(self, value):
        """Replace the list of properties owned by this player."""
        self._state["properties"] = value

    @property
    def is_eliminated(self):
        """Return True if the player has been eliminated."""
        return self._state["is_eliminated"]

    @is_eliminated.setter
    def is_eliminated(self, value):
        """Update elimination status."""
        self._state["is_eliminated"] = bool(value)

    @property
    def in_jail(self):
        """Return whether the player is currently in jail."""
        return self._state["in_jail"]

    @in_jail.setter
    def in_jail(self, value):
        """Set the player's jail status."""
        self._state["in_jail"] = bool(value)

    @property
    def jail_turns(self):
        """Return the number of turns the player has spent in jail."""
        return self._state["jail_turns"]

    @jail_turns.setter
    def jail_turns(self, value):
        """Update the number of turns spent in jail."""
        self._state["jail_turns"] = int(value)

    @property
    def get_out_of_jail_cards(self):
        """Return the number of Get Out of Jail Free cards held."""
        return self._state["cards"]

    @get_out_of_jail_cards.setter
    def get_out_of_jail_cards(self, value):
        """Update the number of Get Out of Jail Free cards held."""
        self._state["cards"] = int(value)


    def add_money(self, amount):
        """Add funds to this player's balance. Amount must be non-negative."""
        if amount < 0:
            raise ValueError(f"Cannot add a negative amount: {amount}")
        self.balance += amount

    def deduct_money(self, amount):
        """Deduct funds from this player's balance. Amount must be non-negative."""
        if amount < 0:
            raise ValueError(f"Cannot deduct a negative amount: {amount}")
        self.balance -= amount

    def is_bankrupt(self):
        """Return True if this player has no money remaining."""
        return self.balance <= 0

    def net_worth(self):
        """Calculate and return this player's total net worth."""
        total = self.balance
        for prop in self.properties:
            if prop.is_mortgaged:
                total += prop.mortgage_value
            else:
                total += prop.price
        return total

    def move(self, steps):
        """
        Move this player forward by `steps` squares, wrapping around the board.
        Awards the Go salary if the player passes or lands on Go.
        Returns the new board position.
        """
        old_position = self.position
        self.position = (self.position + steps) % BOARD_SIZE

        # Award salary when crossing or landing on Go during forward movement.
        if steps > 0 and (old_position + steps) >= BOARD_SIZE:
            self.add_money(GO_SALARY)
            print(f"  {self.name} landed on Go and collected ${GO_SALARY}.")

        return self.position

    def go_to_jail(self):
        """Send this player directly to the Jail square."""
        self.position = JAIL_POSITION
        self.in_jail = True
        self.jail_turns = 0


    def add_property(self, prop):
        """Add a property tile to this player's holdings."""
        if prop not in self.properties:
            self.properties.append(prop)

    def remove_property(self, prop):
        """Remove a property tile from this player's holdings."""
        if prop in self.properties:
            self.properties.remove(prop)

    def count_properties(self):
        """Return the number of properties this player currently owns."""
        return len(self.properties)


    def status_line(self):
        """Return a concise one-line status string for this player."""
        jail_tag = " [JAILED]" if self.in_jail else ""
        return (
            f"{self.name}: ${self.balance}  "
            f"pos={self.position}  "
            f"props={len(self.properties)}"
            f"{jail_tag}"
        )

    def __repr__(self):
        return f"Player({self.name!r}, balance={self.balance}, pos={self.position})"
