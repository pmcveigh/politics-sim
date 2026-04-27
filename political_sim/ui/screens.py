from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QGridLayout, QHBoxLayout, QListWidget, QPushButton, QScrollArea, QTextEdit, QVBoxLayout, QWidget

from ..engine import SimulationEngine
from ..models import BeatStatus, TimeSlot
from .widgets import AlertCard, ConsequenceCard, StoryArcCard, SummaryCard


class BaseScreen(QWidget):
    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__()
        self.engine = engine
        self.layout = QVBoxLayout(self)

    def refresh(self) -> None:
        pass


class DashboardScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine, open_screen) -> None:
        super().__init__(engine)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.layout.addWidget(scroll)
        holder = QWidget()
        self.grid = QGridLayout(holder)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(holder)

        self.today_flow = SummaryCard("1) Today's Flow", button_label="Open Today’s Flow", on_open=lambda: open_screen("Today’s Flow"))
        self.casework = SummaryCard("2) Casework and Inbox", button_label="Open Inbox", on_open=lambda: open_screen("Inbox / Casework"))
        self.stories = StoryArcCard("3) Active Local Stories", button_label="Open Stories", on_open=lambda: open_screen("Stories"))
        self.ward = SummaryCard("4) Ward Mood", button_label="Open Constituency", on_open=lambda: open_screen("Constituency"))
        self.party = SummaryCard("5) Party and Branch Pressure", button_label="Open Party", on_open=lambda: open_screen("Party / Branch"))
        self.relationships = SummaryCard("6) Relationships", button_label="Open Relationships", on_open=lambda: open_screen("Relationships"))
        self.career = SummaryCard("7) Career Track", button_label="Open Career", on_open=lambda: open_screen("Career"))
        self.news = SummaryCard("8) News and Local Chatter", button_label="Open Log", on_open=lambda: open_screen("Log"))
        self.alerts = AlertCard("9) Alerts", button_label="Open Today’s Flow", on_open=lambda: open_screen("Today’s Flow"))
        self.consequence = ConsequenceCard("10) Recent Consequence", button_label="Open Decision Result", on_open=lambda: open_screen("Decision Result"))

        cards = [self.today_flow, self.casework, self.stories, self.ward, self.party, self.relationships, self.career, self.news, self.alerts, self.consequence]
        for i, card in enumerate(cards):
            self.grid.addWidget(card, i // 2, i % 2)

    def refresh(self) -> None:
        s = self.engine.state
        assert s
        lines = []
        for slot in [TimeSlot.MORNING, TimeSlot.AFTERNOON, TimeSlot.EVENING, TimeSlot.LATE_NIGHT]:
            ids = s.daily_agenda.beats_by_slot.get(slot, [])
            titles = [s.daily_beats[i].title for i in ids[:2]]
            lines.append(f"{slot.value}: {', '.join(titles) if titles else 'No listed beat'}")
        self.today_flow.update_body("\n".join(lines))

        open_beats = [b for b in s.daily_beats.values() if b.status == BeatStatus.OPEN]
        self.casework.update_body(f"Open issues: {len(open_beats)}\nUrgent queries: {len([b for b in open_beats if b.urgency == 'High'])}")
        arc_lines = []
        for arc in s.active_story_arcs.values():
            arc_lines.append(f"{arc.title}: stage {arc.current_stage}, pressure {arc.pressure_level}, visibility {arc.public_visibility}")
        self.stories.update_body("\n".join(arc_lines[:3]))

        self.ward.update_body(
            f"Resident trust: {s.player.resident_trust}\nLocal issue pressure: {max(a.pressure_level for a in s.active_story_arcs.values())}\n"
            f"Current flashpoint: {s.constituency.flashpoint}\nRival activity: {s.player.rival_threat}"
        )
        self.party.update_body(
            f"Party group trust: {s.relationships['party_figure'].score}\nBranch support: {s.player.branch_support}\n"
            f"Faction pressure: {max(f.pressure for f in s.factions.values())}\nCurrent expectation: support routine and campaign requests"
        )
        self.relationships.update_body(
            f"Top ally: {max(s.relationships.values(), key=lambda r: r.score).label}\n"
            f"Main rival: {s.relationships['rival'].score}\nRelationship at risk: {min(s.relationships.values(), key=lambda r: r.score).label}"
        )
        self.career.update_body(
            f"Current role: {s.career.current_role.value}\nNext target: Candidate\nReputation: {s.player.reputation}\n"
            f"Local base: {s.player.local_base}\nCareer momentum: {s.player.career_momentum}\n"
            f"Progress towards Assembly selection: {'Open' if s.career.assembly_selection_open else 'Building'}"
        )
        self.news.update_body("\n".join(s.event_log[-4:]))
        self.alerts.update_body("Media waiting for comment" if any(b.beat_type.value == 'Media Request' and b.status == BeatStatus.OPEN for b in s.daily_beats.values()) else "No urgent alerts")
        self.consequence.update_body(s.recent_consequence)


class InboxScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine, on_result) -> None:
        super().__init__(engine)
        self.on_result = on_result
        self.listing = QListWidget()
        self.decisions = QComboBox()
        self.context = QTextEdit()
        self.context.setReadOnly(True)
        row = QHBoxLayout()
        self.apply_btn = QPushButton("Respond")
        self.ignore_btn = QPushButton("Ignore")
        self.advance_btn = QPushButton("Advance Time Slot")
        row.addWidget(self.apply_btn)
        row.addWidget(self.ignore_btn)
        row.addWidget(self.advance_btn)
        self.layout.addWidget(self.listing)
        self.layout.addWidget(self.decisions)
        self.layout.addWidget(self.context)
        self.layout.addLayout(row)
        self.listing.currentRowChanged.connect(self._load_decisions)
        self.decisions.currentIndexChanged.connect(self._show_decision)
        self.apply_btn.clicked.connect(self._apply)
        self.ignore_btn.clicked.connect(self._ignore)
        self.advance_btn.clicked.connect(self._advance)

    def refresh(self) -> None:
        s = self.engine.state
        assert s
        self.listing.clear()
        for beat in self.engine.beats_for_slot():
            self.listing.addItem(f"{beat.id} | {beat.title} | {beat.urgency} | expires {beat.expiry}")
        self._load_decisions(0)

    def _selected_beat_id(self):
        text = self.listing.currentItem().text() if self.listing.currentItem() else ""
        return text.split("|")[0].strip() if "|" in text else None

    def _load_decisions(self, _):
        self.decisions.clear()
        beat_id = self._selected_beat_id()
        if not beat_id:
            return
        beat = self.engine.state.daily_beats[beat_id]
        for d in beat.decision_options:
            self.decisions.addItem(d.label, d.id)
        self._show_decision()

    def _show_decision(self):
        beat_id = self._selected_beat_id()
        if not beat_id or self.decisions.currentData() is None:
            return
        beat = self.engine.state.daily_beats[beat_id]
        d = next(x for x in beat.decision_options if x.id == self.decisions.currentData())
        self.context.setPlainText(
            f"{beat.title}\n\n{beat.description}\n\nLikely upside: {d.likely_upside}\nLikely risk: {d.likely_risk}\n"
            f"Stamina cost: {d.stamina_cost}\nInfluence cost: {d.influence_cost}\nExplanation: {d.explanation}"
        )

    def _apply(self):
        beat_id = self._selected_beat_id()
        if not beat_id:
            return
        self.on_result(self.engine.choose_beat(beat_id, self.decisions.currentData()))

    def _ignore(self):
        beat_id = self._selected_beat_id()
        if not beat_id:
            return
        self.on_result(self.engine.ignore_beat(beat_id))

    def _advance(self):
        self.engine.advance_time()
        self.on_result("Time advanced")


class RoutineScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__(engine)
        self.card = SummaryCard("Today’s Flow")
        self.layout.addWidget(self.card)

    def refresh(self) -> None:
        s = self.engine.state
        assert s
        out = []
        for slot in [TimeSlot.MORNING, TimeSlot.AFTERNOON, TimeSlot.EVENING, TimeSlot.LATE_NIGHT]:
            out.append(slot.value)
            for beat_id in s.daily_agenda.beats_by_slot.get(slot, []):
                beat = s.daily_beats[beat_id]
                out.append(f"- {beat.title} ({beat.status.value})")
        self.card.update_body("\n".join(out))


class StoriesScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__(engine)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.layout.addWidget(self.text)

    def refresh(self) -> None:
        s = self.engine.state
        assert s
        lines = []
        for arc in s.active_story_arcs.values():
            lines.append(
                f"{arc.title}\nStatus: {arc.status.value} | Stage: {arc.current_stage}\n"
                f"Pressure: {arc.pressure_level}, Visibility: {arc.public_visibility}\n"
                f"Player ownership: {arc.player_ownership}, Rival ownership: {arc.rival_ownership}\n"
                f"Flags: {', '.join([k for k,v in arc.flags.items() if v]) or 'None'}\n"
            )
        self.text.setPlainText("\n".join(lines))


class SimpleTextScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine, title: str, producer) -> None:
        super().__init__(engine)
        self.card = SummaryCard(title)
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
        self.text.setPlainText("\n\n".join(self.engine.state.event_log[-100:]))
