from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CrewMember:
    member_id: int
    name: str
    role: Optional[str] = None
    skill_level: Optional[int] = None


@dataclass
class Car:
    car_id: int
    name: str
    condition: str = "good"  # good, damaged
    in_use: bool = False


@dataclass
class Inventory:
    cars: Dict[int, Car] = field(default_factory=dict)
    spare_parts: int = 0
    tools: int = 0
    cash_balance: float = 0.0


@dataclass
class Race:
    race_id: int
    driver_id: int
    car_id: int
    status: str = "scheduled"  # scheduled, completed, cancelled


@dataclass
class RaceResult:
    race_id: int
    position: int
    prize_money: float


@dataclass
class Mission:
    mission_id: int
    mission_type: str
    required_roles: List[str]
    assigned_member_ids: List[int]
    status: str = "planned"  # planned, active, completed
