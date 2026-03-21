from typing import Optional
from .state import SystemState


def assign_mission(
    state: SystemState,
    mission_type: str,
    required_roles: list,
    assigned_member_ids: list,
    car_id: Optional[int] = None,
) -> int:
    for member_id in assigned_member_ids:
        if member_id not in state.crew_members:
            raise ValueError("Crew member must be registered")

    roles_available = {state.crew_members[m].role for m in assigned_member_ids}
    for role in required_roles:
        if role not in roles_available:
            raise ValueError("Required role unavailable")

    if car_id is not None and car_id in state.inventory.cars:
        car = state.inventory.cars[car_id]
        if car.condition == "damaged" and "mechanic" not in roles_available:
            raise ValueError("Damaged car requires mechanic availability")

    mission_id = state.next_mission_id
    state.next_mission_id += 1
    from .models import Mission

    state.missions[mission_id] = Mission(
        mission_id=mission_id,
        mission_type=mission_type,
        required_roles=required_roles,
        assigned_member_ids=assigned_member_ids,
    )
    return mission_id
