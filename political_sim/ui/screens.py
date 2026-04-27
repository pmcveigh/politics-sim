from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QListWidget, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ..engine import SimulationEngine
from ..models import ItemStatus, TimeSlot
from .widgets import Card


class BaseScreen(QWidget):
    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__()
        self.engine = engine
        self.layout = QVBoxLayout(self)

    def refresh(self) -> None:
        return


class DashboardScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__(engine)
        self.card = Card("Dashboard")
        self.layout.addWidget(self.card)

    def refresh(self) -> None:
        s = self.engine.state
        assert s
        open_items = [i for i in s.routine_items if i.status == ItemStatus.OPEN]
        urgent = next((i.title for i in open_items if i.urgency.value in {"High", "Critical"}), "None")
        next_item = open_items[0].title if open_items else "None"
        self.card.update_body(
            f"Today's routine: obligation + opportunity + complication\n"
            f"Casework backlog: {s.player.casework_backlog}\n"
            f"Urgent item: {urgent}\n"
            f"Next meeting/event: {next_item}\n"
            f"Stamina {s.player.stamina} | Reputation {s.player.reputation} | Resident trust {s.player.resident_trust}\n"
            f"Party group trust {s.player.party_group_trust} | Branch support {s.player.branch_support}\n"
            f"Rival threat {s.player.rival_threat} | Career momentum {s.player.career_momentum}"
        )


class InboxScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine, on_result) -> None:
        super().__init__(engine)
        self.on_result = on_result
        self.listing = QListWidget()
        self.decisions = QComboBox()
        row = QHBoxLayout()
        self.apply_btn = QPushButton("Handle")
        self.ignore_btn = QPushButton("Delay/Ignore")
        self.advance_btn = QPushButton("Advance Time Slot")
        row.addWidget(self.apply_btn)
        row.addWidget(self.ignore_btn)
        row.addWidget(self.advance_btn)

        self.layout.addWidget(self.listing)
        self.layout.addWidget(self.decisions)
        self.layout.addLayout(row)

        self.listing.currentRowChanged.connect(self._load_decisions)
        self.apply_btn.clicked.connect(self._apply)
        self.ignore_btn.clicked.connect(self._ignore)
        self.advance_btn.clicked.connect(self._advance)

    def refresh(self) -> None:
        s = self.engine.state
        assert s
        self.listing.clear()
        for i in self.engine.items_for_current_slot():
            self.listing.addItem(f"{i.title} | {i.category.value} | {i.urgency.value} | expires in {i.slots_remaining}")
        self._load_decisions(self.listing.currentRow())

    def _selected_item(self):
        items = self.engine.items_for_current_slot()
        row = self.listing.currentRow()
        if row < 0 or row >= len(items):
            return None
        return items[row]

    def _load_decisions(self, _: int) -> None:
        self.decisions.clear()
        item = self._selected_item()
        if not item:
            return
        for d in self.engine.available_decisions(item):
            self.decisions.addItem(f"{d.label} ({d.handling_style.value})", d.id)

    def _apply(self) -> None:
        item = self._selected_item()
        if not item or self.decisions.currentIndex() < 0:
            return
        result = self.engine.apply_decision(item.id, str(self.decisions.currentData()))
        self.on_result(result)

    def _ignore(self) -> None:
        item = self._selected_item()
        if not item:
            return
        result = self.engine.ignore_item(item.id)
        self.on_result(result)

    def _advance(self) -> None:
        self.engine.advance_time()
        self.on_result("Time advanced.")


class RoutineScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__(engine)
        self.card = Card("Routine")
        self.layout.addWidget(self.card)

    def refresh(self) -> None:
        s = self.engine.state
        assert s
        lines = []
        for slot in [TimeSlot.MORNING, TimeSlot.AFTERNOON, TimeSlot.EVENING, TimeSlot.LATE_NIGHT]:
            lines.append(f"{slot.value}:")
            slot_ids = s.daily_agenda.items_by_slot.get(slot, [])
            if not slot_ids:
                lines.append("  - No fixed item")
                continue
            for item_id in slot_ids:
                item = next((i for i in s.routine_items if i.id == item_id), None)
                if item:
                    lines.append(f"  - {item.title} [{item.category.value}] ({item.status.value})")
        self.card.update_body("\n".join(lines))


class SimpleTextScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine, title: str, producer) -> None:
        super().__init__(engine)
        self.card = Card(title)
        self.producer = producer
        self.layout.addWidget(self.card)

    def refresh(self) -> None:
        self.card.update_body(self.producer())


class LogScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__(engine)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.layout.addWidget(self.text)

    def refresh(self) -> None:
        s = self.engine.state
        assert s
        self.text.setPlainText("\n\n".join(s.event_log[-120:]))
