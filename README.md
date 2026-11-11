*This project has been created as part of the 42 curriculum by pmuzika.*

## Description

Fly In is a Python project that simulates multiple drones navigating a map represented as a graph. It uses Dijkstra's algorithm to find a minimum-cost path and simulates drone movements while respecting zone restrictions and capacity limits. A Pygame interface allows users to visualize the simulation turn by turn.

### Features

- Graph-based map representation.
- Weighted pathfinding using Dijkstra's algorithm.
- Simultaneous drone movement.
- Graphical visualization using Pygame.

## Algorithm and Implementation Strategy

### Pathfinding

Dijkstra's algorithm finds a minimum-cost path using the following zone weights:

| Zone type | Weight | Effect |
|---|---:|---|
| NORMAL | 1 | Standard traversal cost |
| RESTRICTED | 2 | Higher cost and two-turn movement |
| PRIORITY | 0.5 | Lower traversal cost |
| BLOCKED | Infinite | Cannot be traversed |

All drones follow the same calculated path, a deliberate simplification that was sufficient to pass the performance benchmarks.

### Restricted zones and reservations

Moving to a restricted zone takes two turns. During transit, a drone occupies the connection and must reach its destination on the next turn; it cannot wait for the destination zone to become available.

To prevent capacity conflicts, each zone has a `reserved` attribute tracking incoming drones. Before entering a connection, the simulation checks that:

`nb_drones + reserved < capacity`

This conservative strategy can sometimes cause unnecessary waiting, but helps prevent conflicts and avoids situations where drones must move into full zones.

## Visualization

The Pygame interface displays hubs as colored circles, connections as black lines, and drones as grey diamonds labelled with their IDs. A coordinate grid, turn counter, and navigation instructions are also provided.

The simulation runs before the visualization starts, allowing users to review the recorded states turn by turn.

- `SPACE`: advance to the next turn.
- `BACKSPACE`: return to the previous turn.

## Instructions

### Installation

The project requires Python 3, Pygame, and Pydantic. Install the dependencies with:

```bash
make install
```

Alternatively, run:

```bash
pip install -r requirements.txt
```

### Execution

Run the default map:

```bash
make run
```

To select another map:

```bash
make run ARG=maps/medium/03_priority_puzzle.txt
```

## Example Input

```text
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

## Expected Output

The terminal displays the drones' positions, one line per turn. For the example above, verify the actual output by running the simulation:

```text
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

## Performance Benchmarks

The following table compares the reference performance targets with the results achieved by this implementation.

| Difficulty | Map | Target turns | Actual turns |
|---|---|---:|---:|
| Easy | Linear path (2 drones) | ≤ 6 | **4** |
| Easy | Simple fork (4 drones) | ≤ 8 | **6** |
| Easy | Basic capacity (4 drones) | ≤ 6 | **4** |
| Medium | Dead end trap (5 drones) | ≤ 12 | **8** |
| Medium | Circular loop (6 drones) | ≤ 15 | **15** |
| Medium | Priority puzzle (5 drones) | ≤ 12 | **8** |
| Hard | Maze nightmare (8 drones) | ≤ 30 | **13** |
| Hard | Capacity hell (12 drones) | ≤ 35 | **16** |
| Hard | Ultimate challenge (15 drones) | ≤ 45 | **26** |
| Challenger (optional) | The Impossible Dream (25 drones) | 45 (reference record) | **67** |

All standard performance targets are met. The implementation also performs particularly well on the hard maps, completing them significantly below their reference limits.

The optional Challenger map is completed in 67 turns, compared with the reference record of 45 turns.

## Resources

- [Python documentation](https://docs.python.org/3/)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Pygame documentation](https://www.pygame.org/docs/)
- [Dijkstra's algorithm — CP-Algorithms](https://cp-algorithms.com/graph/dijkstra.html)
- Use of AI: ChatGPT-6 was used mainly for debugging and learning how to use Pygame, particularly its drawing functions, coordinate transformations, text rendering, and event handling.
