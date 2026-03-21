from .state import SystemState
from .models import Car


def add_car(state: SystemState, name: str) -> int:
    if not name or not name.strip():
        raise ValueError("Car name required")
    car_id = state.next_car_id
    state.next_car_id += 1
    state.inventory.cars[car_id] = Car(car_id=car_id, name=name.strip())
    return car_id


def add_spare_parts(state: SystemState, count: int) -> None:
    if count < 0:
        raise ValueError("Count must be non-negative")
    state.inventory.spare_parts += count


def add_tools(state: SystemState, count: int) -> None:
    if count < 0:
        raise ValueError("Count must be non-negative")
    state.inventory.tools += count


def update_cash(state: SystemState, amount: float) -> None:
    state.inventory.cash_balance += amount
