from typing import Optional
from .state import SystemState
from .models import CrewMember


def register_member(state: SystemState, name: str, role: Optional[str] = None) -> int:
    if not name or not name.strip():
        raise ValueError("Name is required")
    member_id = state.next_member_id
    state.next_member_id += 1
    state.crew_members[member_id] = CrewMember(member_id=member_id, name=name.strip(), role=role)
    return member_id
