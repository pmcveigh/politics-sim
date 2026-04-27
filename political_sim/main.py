from .engine import SimulationEngine
from .ui import TerminalUI


def main() -> None:
    engine = SimulationEngine()
    ui = TerminalUI(engine)
    ui.run()


if __name__ == "__main__":
    main()
