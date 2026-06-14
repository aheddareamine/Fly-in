"""Data models for the Fly-in drone routing system."""

from dataclasses import dataclass
from enum import Enum


class HubType(Enum):
    """Types of zone prefixes in the map file."""

    START_HUB = "start_hub"
    END_HUB = "end_hub"
    HUB = "hub"


class ZoneType(Enum):
    """Zone behavior types affecting movement cost."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


@dataclass
class Hub:
    """Represents a zone in the drone network."""

    type: str
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str | None = None
    max_drones: int = 1


@dataclass
class Connection:
    """Represents a bidirectional link between two hubs."""

    hub_a: str
    hub_b: str
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        """Normalize hub order for duplicate detection."""
        if self.hub_a > self.hub_b:
            self.hub_a, self.hub_b = (
                self.hub_b, self.hub_a
            )


@dataclass
class Graph:
    """Represents the full parsed drone network."""

    nb_drones: int
    hubs: list[Hub]
    connections: list[Connection]
    start_hub: Hub
    end_hub: Hub
