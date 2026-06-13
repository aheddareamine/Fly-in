from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ZoneType(Enum):
    """Zone type affecting movement cost."""

    NORMAL="normal"
    RESTRICTED="restricted"
    PRIORITY="priority"
    BLOCKED="blocked"

class HubType(Enum):
    """Hub role in the graph."""

    START = "start_hub"
    END = "end_hub"
    REGULAR = "hub"

@dataclass
class Hub:
    """Represents a zone in the drone network."""

    name: str
    x: int
    y: int
    hub_type: HubType
    zone_type: ZoneType = ZoneType.NORMAL
    color: str | None = None
    max_drones: int = 1

@dataclass
class Connection:
    """Represents a bidirectional connection between two zones."""

    zone1: str
    zone2: str
    max_link_capacity: int = 1
