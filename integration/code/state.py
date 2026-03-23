from dataclasses import dataclass, field
from typing import Dict
from .models import CrewMember, Inventory, Mission, Race, RaceResult


@dataclass
class SystemState:
    crew_members: Dict[int, CrewMember] = field(default_factory=dict)
    inventory: Inventory = field(default_factory=Inventory)
    races: Dict[int, Race] = field(default_factory=dict)
    results: Dict[int, RaceResult] = field(default_factory=dict)
    missions: Dict[int, Mission] = field(default_factory=dict)
    rankings: Dict[int, int] = field(default_factory=dict)

    next_member_id: int = 1
    next_car_id: int = 1
    next_race_id: int = 1
    next_mission_id: int = 1
