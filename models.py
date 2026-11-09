from dataclasses import dataclass, field
from typing import Optional, Tuple, List


@dataclass
class Building:
    type: str
    hp: int


@dataclass
class Planet:
    id: str
    name: str
    kind: str  # rock | gas | ice
    slots: int
    pos: Tuple[int, int]
    owner: Optional[int] = None
    buildings: List[Building] = field(default_factory=list)
    built: bool = False  # корабль уже построен в этот ход

    def used_slots(self) -> int:
        return len(self.buildings) + (1 if self.owner is not None else 0)

    def free_slots(self) -> int:
        return self.slots - self.used_slots()


@dataclass
class Unit:
    uid: int
    type: str
    owner: int
    pos: Tuple[int, int]
    hp: int
    max_hp: int
    colonizing: str = ""  # id планеты, которую колонизирует


@dataclass
class Player:
    pid: int
    name: str
    is_bot: bool
    resources: dict
    alive: bool = True


@dataclass
class GameState:
    size: int
    sun_pos: Tuple[int, int]
    planets: List[Planet]
    units: List[Unit]
    players: List[Player]
    turn: int = 1
    current: int = 0
    diplomacy: dict = field(default_factory=dict)  # (min_id, max_id) -> neutral|war|ally
    trades_this_turn: dict = field(default_factory=dict)  # pid -> set(pid)
    next_uid: int = 1
