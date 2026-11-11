from enum import Enum
import sys
try:
    from pydantic import BaseModel, Field
except ImportError:
    print("pydantic import failed")
    print("Please run:")
    print("make install")
    sys.exit(1)
from .drone import Drone


class ZoneType(str, Enum):
    """Four zone types:
        normal:  Standard zone with 1 turn movement cost (default)
        blocked: inaccessible zone
        restricted: Movement to this zone costs 2 turns
        priority: Movement to this zone costs 1 turn but should be prioritized
    """

    weight: float

    NORMAL = ("normal", 1.0)
    BLOCKED = ("blocked", float("inf"))
    RESTRICTED = ("restricted", 2.0)
    PRIORITY = ("priority", 0.5)

    def __new__(cls, label: str, weight: float) -> "ZoneType":
        """Create a zone type with its label and weight"""
        obj = str.__new__(cls, label)
        obj._value_ = label
        obj.weight = weight
        return obj


class NodeStatus(Enum):
    """Three status for a node: hub (normal), start, end"""

    START = "start"
    END = "end"
    HUB = "hub"


class Node(BaseModel):
    """An intersection on the graph.
    Attributes:
        name: Unique identifier of the zone (no dashes or spaces).
        x: Horizontal coordinate.
        y: Vertical coordinate.
        status: start, end or "hub" (normal)
        zone: zone type
        drones: list of drones present on the node.
        max_drones: maximum number of drones allowed at the same time.
            Not used for start and end.
        reserved: number of drones planning to enter the node
            after spending one turn on a connection. Only used for restricted.
        color: optional display color for visual representation
    """

    name: str
    x: int
    y: int
    status: NodeStatus = NodeStatus.HUB
    zone: ZoneType = ZoneType.NORMAL
    drones: list[Drone] = Field(default_factory=list)
    max_drones: int = Field(default=1, ge=1)
    reserved: int = 0
    color: str | None = None

    @property
    def nb(self) -> int:
        """Return size of list 'drones'"""
        return len(self.drones)

    def has_capacity(self) -> bool:
        """Return True if a new drone can enter the node"""
        if self.status == NodeStatus.END or self.status == NodeStatus.START:
            return True
        if len(self.drones) < self.max_drones:
            return True
        return False

    def add_drone(self, drone: Drone) -> bool:
        """Append drone to the list 'drones'"""
        if drone in self.drones:
            return False
        if not self.has_capacity():
            return False
        self.drones.append(drone)
        return True

    def remove_drone(self, drone: Drone) -> bool:
        """Remove drone from the list 'drones'"""
        if drone in self.drones:
            self.drones.remove(drone)
            return True
        return False
