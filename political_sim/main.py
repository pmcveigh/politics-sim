from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .engine import SimulationEngine
from .ui import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    engine = SimulationEngine()
    engine.create_simulation()
    window = MainWindow(engine)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
