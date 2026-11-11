from models import Node, NodeStatus, ZoneType, Connection, Drone, DroneState
from typing import Any
from parser import Parser
import heapq
import sys


class Simulation:
    """Define shortest path and move all drones along the same path"""

    def __init__(self, filename: str) -> None:
        """Receive name of config file and create the simulation"""
        self.filename = filename
        self.config = Parser.parser(self.filename)
        try:
            self.nodes = self.create_nodes(self.config["hubs"])
            for node in self.nodes:
                if node.status == NodeStatus.START:
                    self.start = node
                elif node.status == NodeStatus.END:
                    self.end = node
            self.nodes_by_name = {
                node.name: node
                for node in self.nodes
            }
            self.nodes_by_position = {
                (node.x, node.y): node
                for node in self.nodes
            }
            roads = self.config["connections"]
            self.connections = self.create_connections(roads)
            self.drones = self.create_drones(self.config["nb_drones"])
            self.graph = self.create_graph()
            previous_nodes = self.dijkstra()
            self.path = self.get_shortest_path(previous_nodes, self.end)
            self.check_path()
            self.path_coordinates = self.get_path_by_coord()
            self.all_states = []
            self.all_states.append(self.save_state())
            self.start_simulation()
        except ValueError as e:
            print(f"{e}")

    def check_path(self) -> None:
        """Verify that the found path starts at the designated start node."""
        first = self.nodes_by_name[self.path[0]]
        if first != self.start:
            print("Map error: No path from start to end")
            sys.exit(1)

    def start_simulation(self) -> None:
        """Move drones along the path and print moves"""
        goal_coord = self.end.x, self.end.y
        while len(self.end.drones) < self.config["nb_drones"]:
            moves: list[str] = []
            for drone in self.drones:
                if drone.position == goal_coord:
                    continue
                self.define_target(drone)
                current = self.nodes_by_position[drone.position]
                if drone.target_node is not None:
                    target = self.nodes_by_position[drone.target_node]
                else:
                    raise ValueError("Target node not found")
                if drone.state == DroneState.ON_CONNECTION:
                    connection = self.get_connection(current, target)
                    connection.remove_drone(drone)
                    target.add_drone(drone)
                    target.reserved -= 1
                    drone.move()
                    moves.append(f"D{drone.id}-{target.name}")
                    continue
                if target.zone == ZoneType.RESTRICTED:
                    connection = self.get_connection(current, target)
                    if target.nb + target.reserved < target.max_drones:
                        if connection.add_drone(drone):
                            drone.go_to_connection()
                            target.reserved += 1
                            current.remove_drone(drone)
                            txt = f"D{drone.id}-{current.name}-{target.name}"
                            moves.append(txt)
                        else:
                            drone.wait()
                    else:
                        drone.wait()
                else:
                    if target.add_drone(drone):
                        drone.move()
                        current.remove_drone(drone)
                        moves.append(f"D{drone.id}-{target.name}")
                    else:
                        drone.wait()
            move = " ".join(moves)
            print(move)
            self.all_states.append(self.save_state())

    def get_current_position(self, drone: Drone) -> Node | Connection:
        """Return Node or Connection where a drone currently is"""
        if drone.state != DroneState.ON_CONNECTION:
            x, y = drone.position
            return self.nodes_by_position[(x, y)]
        else:
            current = self.nodes_by_position[drone.position]
            if drone.target_node is not None:
                target = self.nodes_by_position[drone.target_node]
            else:
                raise ValueError("Target node not found")
            return self.get_connection(current, target)

    def save_state(self) -> list[tuple[Drone, Node | Connection]]:
        """List the current positions of all drones"""
        return [
            (drone, self.get_current_position(drone))
            for drone in self.drones
        ]

    def define_target(self, drone: Drone) -> None:
        """Define the target node of the drone"""
        i = 0
        while i < len(self.path_coordinates):
            if self.path_coordinates[i] == drone.position:
                break
            i += 1
        drone.target_node = self.path_coordinates[i + 1]
        return

    def get_connection(self, node1: Node, node2: Node) -> Connection:
        """Return the connection between two nodes"""
        for connection in self.connections:
            if connection.node_1 == node1 and connection.node_2 == node2:
                return connection
            if connection.node_1 == node2 and connection.node_2 == node1:
                return connection
        raise ValueError("Connection not found")

    @staticmethod
    def create_nodes(hubs: list[dict[str, Any]]) -> list[Node]:
        """Take config and create list of nodes"""
        nodes = []
        for data in hubs:
            node = Node(**data)
            nodes.append(node)
        return nodes

    def create_connections(
            self, edges: list[dict[str, Any]]
    ) -> list[Connection]:
        """Take config and create list of connections"""
        connections = []
        for data in edges:
            connection_data = data.copy()
            connection_data["node_1"] = self.nodes_by_name[data["node_1"]]
            connection_data["node_2"] = self.nodes_by_name[data["node_2"]]
            connection = Connection(**connection_data)
            connections.append(connection)
        return connections

    def create_drones(self, nb_drones: int) -> list[Drone]:
        """Take config and create list of drones"""
        drones = []
        starting_pos = self.start.x, self.start.y
        i = 1
        while i <= nb_drones:
            drone = Drone(
                id=i,
                position=starting_pos,
            )
            drones.append(drone)
            i += 1
        return drones

    def create_graph(self) -> dict[str, dict[str, float]]:
        """Create the structure of the graph as a dict"""
        graph: dict[str, dict[str, float]] = {}
        for node in self.nodes:
            neighbors: dict[str, float] = {}
            for connection in self.connections:
                if connection.node_1 == node:
                    neighbor = connection.node_2
                    neighbors[neighbor.name] = neighbor.zone.weight
                elif connection.node_2 == node:
                    neighbor = connection.node_1
                    neighbors[neighbor.name] = neighbor.zone.weight
            graph[node.name] = neighbors
        return graph

    def dijkstra(self) -> dict[str, str | None]:
        """Calculate shortest path from any node to start.
        Return a dict 'node: previous node' for each node on the map
        """
        distances_from_source = {
            node.name: float('inf') for node in self.nodes
        }
        distances_from_source[self.start.name] = 0
        previous_nodes: dict[str, str | None] = {
            node.name: None for node in self.nodes
        }
        visited = set()
        to_visit: list[tuple[float, str]] = [(0, self.start.name)]
        while to_visit:
            current_distance, current_node = heapq.heappop(to_visit)
            if current_node in visited:
                continue
            for neighbor, weight in self.graph[current_node].items():
                if neighbor in visited:
                    continue
                distance = current_distance + weight
                if distance < distances_from_source[neighbor]:
                    distances_from_source[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(to_visit, (distance, neighbor))
            visited.add(current_node)
        return previous_nodes

    @staticmethod
    def get_shortest_path(
            previous_nodes: dict[str, str | None], destination: Node
    ) -> list[str]:
        """Return shortest path from start to goal"""
        path = []
        current_node: str | None = destination.name
        while current_node is not None:
            path.append(current_node)
            current_node = previous_nodes[current_node]
        path.reverse()
        return path

    def get_path_by_coord(self) -> list[tuple[int, int]]:
        """Get path as list of coordinates"""
        path_coordinates = [
            (self.nodes_by_name[name].x, self.nodes_by_name[name].y)
            for name in self.path
        ]
        return path_coordinates
