from simulation import Simulation
from models import Node, Connection, Drone
import sys
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"


class Visual:
    """Receive an object from class Simulation
        and display the graph and drone moves using pygame module.
    """

    def __init__(self, simul: Simulation) -> None:
        """Initialize visualization attributes and import pygame."""
        try:
            import pygame
        except ImportError:
            print("pygame import failed")
            print("Please run:")
            print("make install")
            sys.exit(1)
        self.pygame = pygame
        self.map_name = os.path.splitext(os.path.basename(simul.filename))[0]
        self.nodes = simul.nodes
        self.connections = simul.connections
        self.all_states = simul.all_states
        self.scale = 200
        self.margin = 120
        self.min_x = min(node.x for node in self.nodes)
        self.max_x = max(node.x for node in self.nodes)
        self.min_y = min(node.y for node in self.nodes)
        self.max_y = max(node.y for node in self.nodes)
        self.footer_height = 45
        self.calculate_dimensions()

    def calculate_dimensions(self) -> None:
        """Reduce the map scale if its dimensions exceed
            the available screen size.
        """
        available_width = 3800
        available_height = 1800 - self.footer_height
        self.width = (
            (self.max_x - self.min_x) * self.scale + 2 * self.margin
        )
        self.height = (
            (self.max_y - self.min_y) * self.scale + 2 * self.margin
        )
        if self.width > available_width or self.height > available_height:
            scale_x = available_width / self.width
            scale_y = available_height / self.height
            factor = min(scale_x, scale_y)
            self.scale = int(self.scale * factor)
            self.width = int(self.width * factor)
            self.height = int(self.height * factor)

    def to_screen(self, x: float, y: float) -> tuple[float, float]:
        """Convert map coordinates to screen coordinates."""
        screen_x = self.margin + (x - self.min_x) * self.scale
        screen_y = self.margin + (self.max_y - y) * self.scale
        return (screen_x, screen_y)

    def get_color(self, color: str | None) -> str:
        """Return the given color if valid, or else 'gray' by default."""
        if color is None:
            return "gray"
        try:
            self.pygame.Color(color)
            return color
        except ValueError:
            return "gray"

    def draw_grid(self) -> None:
        """Draw a coordinate grid, highlighting the x- and y-axes."""
        for x in range(self.min_x, self.max_x + 1):
            start = self.to_screen(x, self.min_y)
            end = self.to_screen(x, self.max_y)
            color = "darkslategray" if x == 0 else "lightgray"
            self.pygame.draw.line(
                self.screen, color,
                start,
                end,
                1
            )
        for y in range(self.min_y, self.max_y + 1):
            start = self.to_screen(self.min_x, y)
            end = self.to_screen(self.max_x, y)
            color = "darkslategray" if y == 0 else "lightgray"
            self.pygame.draw.line(
                self.screen,
                color,
                start,
                end,
                1
            )

    def draw_connections(self) -> None:
        """Draw connections between nodes as thick black lines."""
        for connection in self.connections:
            start = self.to_screen(
                connection.node_1.x,
                connection.node_1.y
            )
            end = self.to_screen(
                connection.node_2.x,
                connection.node_2.y
            )
            self.pygame.draw.line(
                self.screen,
                "black",
                start,
                end,
                20
            )

    def draw_nodes(self) -> None:
        """Draw graph nodes as colored circles,
            with their names centered inside.
        """
        for node in self.nodes:
            position = self.to_screen(node.x, node.y)
            color = self.get_color(node.color)

            self.pygame.draw.circle(
                self.screen,
                color,
                position,
                50
            )
            text = self.font.render(node.name, True, "dimgray")
            text_rect = text.get_rect(
                center=(position[0], position[1])
            )
            self.screen.blit(text, text_rect)

    def draw_drones(
        self, states: list[tuple[Drone, Node | Connection]]
    ) -> None:
        """Draw drones as grey diamonds on the map
            with their IDs centered inside.
        """
        for drone, position in states:
            x: float
            y: float
            if isinstance(position, Node):
                x = position.x
                y = position.y
            else:
                x = (position.node_1.x + position.node_2.x) / 2
                y = (position.node_1.y + position.node_2.y) / 2
            screen_x, screen_y = self.to_screen(x, y)
            self.pygame.draw.polygon(
                self.screen,
                "grey",
                [
                    (screen_x, screen_y - 25),  # Arriba
                    (screen_x + 25, screen_y),  # Derecha
                    (screen_x, screen_y + 25),  # Abajo
                    (screen_x - 25, screen_y),  # Izquierda
                ]
            )
            text = self.font.render(f"D{drone.id}", True, "black")
            text_rect = text.get_rect(
                center=(screen_x, screen_y)
            )
            self.screen.blit(text, text_rect)

    def draw_instructions(self) -> None:
        """Display instructions for navigating between simulation turns."""
        instruction_font = self.pygame.font.Font(None, 35)
        instructions = instruction_font.render(
            "SPACE: NEXT TURN | BACKSPACE: PREVIOUS TURN",
            True,
            "white",
            "black"
        )
        self.screen.blit(
            instructions,
            (self.width - instructions.get_width() - 10, self.height - 10)
        )

    def draw_turn(self, current_turn: int) -> None:
        """Display the current simulation turn in the bottom-left corner."""
        turn_font = self.pygame.font.Font(None, 40)
        turn = turn_font.render(
            f"TURN: {current_turn}",
            True,
            "blue"
        )
        self.screen.blit(
            turn,
            (10, self.height - 10)
        )

    def visualization_loop(self) -> None:
        """Handle user input and update the visualization"""
        running = True
        current_turn = 0
        while running:
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    running = False
                elif event.type == self.pygame.KEYDOWN:
                    if event.key == self.pygame.K_ESCAPE:
                        running = False
                    elif event.key == self.pygame.K_SPACE:
                        if current_turn < len(self.all_states) - 1:
                            current_turn += 1
                    elif event.key == self.pygame.K_BACKSPACE:
                        if current_turn > 0:
                            current_turn -= 1
            self.screen.fill("white")
            self.draw_grid()
            self.draw_connections()
            self.draw_nodes()
            self.draw_drones(self.all_states[current_turn])
            self.draw_instructions()
            self.draw_turn(current_turn)
            self.pygame.display.flip()

    def run(self) -> None:
        """Initialize pygame, run the visualization loop and quit pygame"""
        try:
            window_height = self.height + self.footer_height
            self.pygame.init()
            self.screen = self.pygame.display.set_mode(
                (self.width, window_height)
            )
            self.pygame.display.set_caption(f"Fly In - {self.map_name}")
            self.font = self.pygame.font.Font(None, 25)
            self.visualization_loop()
        except KeyboardInterrupt:
            print("\nVisualization interrupted by user")
        except self.pygame.error as e:
            print(f"Pygame error: {e}")
            sys.exit(1)
        finally:
            self.pygame.quit()
