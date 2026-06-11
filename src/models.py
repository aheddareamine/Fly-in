from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ZoneType(Enum):
    NORMAL="normal"
    RESTRICTED="restricted"
    PRIORITY="priority"
    BLOCKED="blocked"

# # class Arguments(Enum):
    

# class Colors(Enum):
#     GREEN = "green"
#     BLUE = "blue"
#     YELLOW = "yellow"
#     ORANGE = "orange"
#     RED = "red"
#     PURPLE = "Purple"
#     CYAN = "cyan"
#     BROWN = "brown"
#     MAGENTA = "darkred"
#     MAROON = "maroon"

@dataclass
class Hub:
    name: str = ""
    x: int = 0
    y: int = 0
    color: str = None
    zone: str = ZoneType.NORMAL
    max_drones: int = 1

# @dataclass
# class connection:
#     pass