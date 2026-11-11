from simulation import Simulation
from visual import Visual
import sys


def main() -> None:
    """Main function. Create simulation and run visual representation"""
    if len(sys.argv) != 2:
        print(f"Invalid input. Usage: python3 {sys.argv[0]} <map_file>")
        return
    simul = Simulation(sys.argv[1])
    visual = Visual(simul)
    visual.run()


if __name__ == "__main__":
    main()
