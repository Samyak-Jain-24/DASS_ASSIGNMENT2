from .state import SystemState


def create_race(state: SystemState, driver_id: int, car_id: int) -> int:
    if driver_id not in state.crew_members:
        raise ValueError("Driver must be registered")
    driver = state.crew_members[driver_id]
    if driver.role != "driver":
        raise ValueError("Only crew members with driver role may enter races")
    if car_id not in state.inventory.cars:
        raise ValueError("Car does not exist")
    car = state.inventory.cars[car_id]
    if car.in_use:
        raise ValueError("Car already in use")
    race_id = state.next_race_id
    state.next_race_id += 1
    from .models import Race

    state.races[race_id] = Race(race_id=race_id, driver_id=driver_id, car_id=car_id)
    car.in_use = True
    return race_id
    