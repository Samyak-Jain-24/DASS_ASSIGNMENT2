from .state import SystemState
from .inventory import update_cash
from .maintenance import mark_damaged


def record_result(
    state: SystemState,
    race_id: int,
    position: int,
    prize_money: float,
    car_damaged: bool = False,
) -> None:
    if race_id not in state.races:
        raise ValueError("Race not found")
    if position < 1:
        raise ValueError("Position must be >= 1")
    from .models import RaceResult

    state.results[race_id] = RaceResult(race_id=race_id, position=position, prize_money=prize_money)
    update_cash(state, prize_money)

    race = state.races[race_id]
    car = state.inventory.cars[race.car_id]
    car.in_use = False
    if car_damaged:
        mark_damaged(state, race.car_id)

    state.rankings[race.driver_id] = state.rankings.get(race.driver_id, 0) + (10 if position == 1 else 5)
