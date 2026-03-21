from streetrace_manager.state import SystemState
from streetrace_manager.registration import register_member
from streetrace_manager.crew_management import assign_role
from streetrace_manager.inventory import add_car, update_cash
from streetrace_manager.race_management import create_race
from streetrace_manager.results import record_result
from streetrace_manager.mission_planning import assign_mission
from streetrace_manager.maintenance import mark_damaged
from streetrace_manager.maintenance import repair_car
from streetrace_manager.inventory import add_spare_parts
from streetrace_manager.reputation import update_reputation


def run_tests():
    results = []
    state = SystemState()

    # IT-01
    try:
        driver_id = register_member(state, "Lina")
        assign_role(state, driver_id, "driver", 8)
        car_id = add_car(state, "Viper")
        race_id = create_race(state, driver_id, car_id)
        results.append(("IT-01", "PASS", f"Race {race_id} created"))
    except Exception as exc:
        results.append(("IT-01", "FAIL", str(exc)))

    # IT-02
    try:
        add_car(state, "Falcon")
        create_race(state, driver_id=999, car_id=2)
        results.append(("IT-02", "FAIL", "Race created with unregistered driver"))
    except Exception as exc:
        results.append(("IT-02", "PASS", str(exc)))

    # IT-03
    try:
        update_cash(state, 0)
        record_result(state, race_id, position=1, prize_money=400.0)
        results.append(("IT-03", "PASS", f"Cash={state.inventory.cash_balance}"))
    except Exception as exc:
        results.append(("IT-03", "FAIL", str(exc)))

    # IT-04
    try:
        strategist_id = register_member(state, "Ishan")
        assign_role(state, strategist_id, "strategist", 6)
        assign_mission(state, "delivery", ["driver", "mechanic"], [strategist_id])
        results.append(("IT-04", "FAIL", "Mission assigned without required roles"))
    except Exception as exc:
        results.append(("IT-04", "PASS", str(exc)))

    # IT-05
    try:
        mechanic_id = register_member(state, "Ravi")
        assign_role(state, mechanic_id, "mechanic", 7)
        mark_damaged(state, car_id)
        mission_id = assign_mission(
            state,
            "rescue",
            ["mechanic"],
            [mechanic_id],
            car_id=car_id,
        )
        results.append(("IT-05", "PASS", f"Mission {mission_id} created"))
    except Exception as exc:
        results.append(("IT-05", "FAIL", str(exc)))

    # IT-06
    try:
        add_spare_parts(state, 2)
        before = state.inventory.spare_parts
        repair_car(state, car_id, [mechanic_id])
        after = state.inventory.spare_parts
        if after != before - 1:
            raise AssertionError("Spare parts not consumed")
        results.append(("IT-06", "PASS", "Repair completed"))
    except Exception as exc:
        results.append(("IT-06", "FAIL", str(exc)))

    # IT-07
    try:
        before_rank = state.rankings.get(driver_id, 0)
        update_reputation(state, driver_id, delta=3)
        after_rank = state.rankings.get(driver_id, 0)
        if after_rank != before_rank + 3:
            raise AssertionError("Reputation not updated")
        results.append(("IT-07", "PASS", "Reputation updated"))
    except Exception as exc:
        results.append(("IT-07", "FAIL", str(exc)))

    return results


if __name__ == "__main__":
    for test_id, status, message in run_tests():
        print(f"{test_id}: {status} - {message}")
