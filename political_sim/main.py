from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .engine import SimulationEngine
from .models import Role
from .ui import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    engine = SimulationEngine()
    engine.create_simulation(player_name="Alex Mercer", party_id="cap", role=Role.COUNCILLOR, constituency_id="north_down")
    window = MainWindow(engine)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
