import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from integration.code.state import SystemState
from integration.code.registration import register_member
from integration.code.crew_management import assign_role
from integration.code.inventory import add_car, update_cash
from integration.code.race_management import create_race
from integration.code.results import record_result
from integration.code.mission_planning import assign_mission
from integration.code.maintenance import mark_damaged
from integration.code.maintenance import repair_car
from integration.code.inventory import add_spare_parts
from integration.code.reputation import update_reputation


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

    # IT-08
    try:
        state8 = SystemState()
        d_id = register_member(state8, "Ari")
        assign_role(state8, d_id, "driver", 7)
        c_id = add_car(state8, "Bolt")
        create_race(state8, d_id, c_id)
        create_race(state8, d_id, c_id)
        results.append(("IT-08", "FAIL", "Second race created with a car already in use"))
    except Exception as exc:
        results.append(("IT-08", "PASS", str(exc)))

    # IT-09
    try:
        state9 = SystemState()
        strategist_id = register_member(state9, "Nia")
        assign_role(state9, strategist_id, "strategist", 6)
        c_id = add_car(state9, "Ghost")
        create_race(state9, strategist_id, c_id)
        results.append(("IT-09", "FAIL", "Race created with non-driver role"))
    except Exception as exc:
        results.append(("IT-09", "PASS", str(exc)))

    # IT-10
    try:
        state10 = SystemState()
        d_id = register_member(state10, "Mika")
        assign_role(state10, d_id, "driver", 9)
        c_id = add_car(state10, "Nova")
        race_id_10 = create_race(state10, d_id, c_id)
        record_result(state10, race_id_10, position=2, prize_money=150.0)
        race_id_10b = create_race(state10, d_id, c_id)
        results.append(("IT-10", "PASS", f"Race {race_id_10b} created after result release"))
    except Exception as exc:
        results.append(("IT-10", "FAIL", str(exc)))

    # IT-11
    try:
        state11 = SystemState()
        d_id = register_member(state11, "Rey")
        assign_role(state11, d_id, "driver", 8)
        c_id = add_car(state11, "Comet")
        race_id_11 = create_race(state11, d_id, c_id)
        record_result(state11, race_id_11, position=3, prize_money=75.0, car_damaged=True)
        assign_mission(state11, "delivery", ["driver"], [d_id], car_id=c_id)
        results.append(("IT-11", "FAIL", "Damaged-car mission assigned without mechanic"))
    except Exception as exc:
        results.append(("IT-11", "PASS", str(exc)))

    # IT-12
    try:
        state12 = SystemState()
        d_id = register_member(state12, "Tara")
        m_id = register_member(state12, "Vik")
        assign_role(state12, d_id, "driver", 8)
        assign_role(state12, m_id, "mechanic", 7)
        c_id = add_car(state12, "Saber")
        race_id_12 = create_race(state12, d_id, c_id)
        record_result(state12, race_id_12, position=1, prize_money=250.0, car_damaged=True)
        mission_id = assign_mission(state12, "rescue", ["mechanic"], [m_id], car_id=c_id)
        results.append(("IT-12", "PASS", f"Mission {mission_id} assigned with mechanic for damaged car"))
    except Exception as exc:
        results.append(("IT-12", "FAIL", str(exc)))

    # IT-13
    try:
        state13 = SystemState()
        c_id = add_car(state13, "Drift")
        mark_damaged(state13, c_id)
        add_spare_parts(state13, 1)
        repair_car(state13, c_id, [])
        results.append(("IT-13", "FAIL", "Repair succeeded without mechanic"))
    except Exception as exc:
        results.append(("IT-13", "PASS", str(exc)))

    # IT-14
    try:
        state14 = SystemState()
        crew_id = register_member(state14, "Omar")
        assign_role(state14, crew_id, "driver", 5)
        update_reputation(state14, member_id=999, delta=2)
        results.append(("IT-14", "FAIL", "Updated reputation for unknown member"))
    except Exception as exc:
        results.append(("IT-14", "PASS", str(exc)))

    return results


if __name__ == "__main__":
    for test_id, status, message in run_tests():
        print(f"{test_id}: {status} - {message}")
