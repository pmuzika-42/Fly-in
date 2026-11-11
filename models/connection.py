import sys
try:
    from pydantic import BaseModel, Field
except ImportError:
    print("pydantic import failed")
    print("Please run:")
    print("make install")
    sys.exit(1)
from .node import Node
from .drone import Drone


class Connection(BaseModel):
    """A bidirectional road between two nodes.

    Attributes:
        node_1, node_2: the two nodes being connected.
        drones: list of drones present on the connection.
        max_link_capacity: maximum number of drones allowed on the connection
    """

    node_1: Node
    node_2: Node
    drones: list[Drone] = Field(default_factory=list)
    max_link_capacity: int = Field(default=1, ge=1)

    def has_capacity(self) -> bool:
        """Return True if a new drone can enter the connection"""
        return len(self.drones) < self.max_link_capacity

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
