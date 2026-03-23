from .state import SystemState


def assign_role(state: SystemState, member_id: int, role: str, skill_level: int) -> None:
    if member_id not in state.crew_members:
        raise ValueError("Crew member must be registered before assigning a role")
    if role.lower() not in ("driver", "mechanic", "strategist"):
        raise ValueError("Invalid role")
    if not (1 <= skill_level <= 10):
        raise ValueError("Skill level must be between 1 and 10")
    member = state.crew_members[member_id]
    member.role = role.lower()
    member.skill_level = skill_level
