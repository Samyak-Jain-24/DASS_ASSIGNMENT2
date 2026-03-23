from .state import SystemState
from .registration import register_member
from .crew_management import assign_role
from .inventory import add_car, update_cash
from .race_management import create_race
from .results import record_result
from .mission_planning import assign_mission
from .maintenance import mark_damaged
from .reputation import update_reputation


def demo():
    state = SystemState()

    driver_id = register_member(state, "Riya")
    mechanic_id = register_member(state, "Arjun")
    assign_role(state, driver_id, "driver", 7)
    assign_role(state, mechanic_id, "mechanic", 6)

    car_id = add_car(state, "Falcon GT")
    race_id = create_race(state, driver_id, car_id)

    record_result(state, race_id, position=1, prize_money=500.0, car_damaged=True)
    update_reputation(state, driver_id, delta=5)

    mark_damaged(state, car_id)
    assign_mission(
        state,
        mission_type="rescue",
        required_roles=["mechanic"],
        assigned_member_ids=[mechanic_id],
        car_id=car_id,
    )

    return state


if __name__ == "__main__":
    demo()
