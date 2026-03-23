from .state import SystemState


def update_reputation(state: SystemState, member_id: int, delta: int) -> None:
    if member_id not in state.crew_members:
        raise ValueError("Crew member not found")
    state.rankings[member_id] = state.rankings.get(member_id, 0) + delta
