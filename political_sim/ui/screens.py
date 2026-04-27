from __future__ import annotations

from PySide6.QtWidgets import QListWidget, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ..engine import SimulationEngine
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
        party = s.parties[s.player.party_id]
        c = s.constituencies[s.player.constituency_id]
        rel = sorted(s.relationships.values(), key=lambda r: r.score)[:3]
        next_moment = s.active_moments[0].title if s.active_moments else "None"
        self.card.update_body(
            f"Date/Slot: {s.datetime_label()}\nRole: {s.player.role.value}\nReputation: {s.player.reputation} | Influence: {s.player.influence} | "
            f"Stamina: {s.player.stamina} | Career momentum: {s.player.career_momentum}\n"
            f"Party focus: unity {party.party_unity}, trust {party.public_trust}, pressure {party.media_pressure}\n"
            f"Constituency pressures: issues {c.local_issue_pressure}, turnout {c.turnout_energy}, media heat {c.local_media_heat}\n"
            f"Relationships needing attention: {', '.join([f'{r.label} ({r.score})' for r in rel])}\n"
            f"Next moment: {next_moment}"
        )


class InboxScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine, on_result) -> None:
        super().__init__(engine)
        self.listing = QListWidget()
        self.respond = QPushButton("Respond")
        self.ignore = QPushButton("Ignore")
        self.respond.clicked.connect(lambda: self._act(True, on_result))
        self.ignore.clicked.connect(lambda: self._act(False, on_result))
        self.layout.addWidget(self.listing)
        self.layout.addWidget(self.respond)
        self.layout.addWidget(self.ignore)

    def refresh(self) -> None:
        self.listing.clear()
        s = self.engine.state
        assert s
        for m in s.active_moments:
            self.listing.addItem(f"{m.title} | {m.category.value} | {m.urgency.value} | expiry {m.expiry_slots} | {m.risk_preview}")

    def _act(self, respond: bool, on_result) -> None:
        row = self.listing.currentRow()
        s = self.engine.state
        assert s
        if row < 0 or row >= len(s.active_moments):
            return
        m = s.active_moments[row]
        if respond:
            decisions = self.engine.available_decisions(m)
            if decisions:
                txt = self.engine.apply_decision(m.id, decisions[0].id)
                on_result(txt)
        else:
            txt = self.engine.ignore_moment(m.id)
            on_result(txt)


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
        self.text.setPlainText("\n\n".join(s.event_log[-80:]))
