from enum import Enum
import sys
try:
    from pydantic import BaseModel, Field
except ImportError:
    print("pydantic import failed")
    print("Please run:")
    print("make install")
    sys.exit(1)


class DroneState(Enum):
    """Define three possible states for a drone:
        waiting, moving to the next node, or on a connection.
    """

    WAITING = "waiting"
    MOVING = "moving"
    ON_CONNECTION = "on_connection"


class Drone(BaseModel):
    """A drone moving on the given map.
    Attributes:
        id: id number of each drone
        state: waiting, moving or on_connection
        position: coordinates of current location
        target_node: coordinates of target node, defined by simulation
    """

    id: int = Field(ge=1)
    state: DroneState = DroneState.WAITING
    position: tuple[int, int]
    target_node: tuple[int, int] | None = None

    def wait(self) -> None:
        """Change drone state to 'waiting'"""
        self.state = DroneState.WAITING

    def go_to_connection(self) -> None:
        """Change drone state to 'on_connection'"""
        self.state = DroneState.ON_CONNECTION

    def move(self) -> None:
        """Change drone state to 'moving', update position and target_node"""
        self.state = DroneState.MOVING
        if self.target_node is not None:
            self.position = self.target_node
        self.target_node = None
