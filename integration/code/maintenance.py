from .state import SystemState


def mark_damaged(state: SystemState, car_id: int) -> None:
    if car_id not in state.inventory.cars:
        raise ValueError("Car not found")
    state.inventory.cars[car_id].condition = "damaged"


def repair_car(state: SystemState, car_id: int, mechanic_ids: list) -> None:
    if car_id not in state.inventory.cars:
        raise ValueError("Car not found")
    roles = {state.crew_members[mid].role for mid in mechanic_ids if mid in state.crew_members}
    if "mechanic" not in roles:
        raise ValueError("Mechanic required for repair")
    if state.inventory.spare_parts < 1:
        raise ValueError("Spare parts required")
    state.inventory.spare_parts -= 1
    state.inventory.cars[car_id].condition = "good"
