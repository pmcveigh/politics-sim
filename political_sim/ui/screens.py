from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..engine import SimulationEngine
from ..models import ItemStatus, StoryStatus, TimeSlot
from .widgets import AgendaItemCard, AlertCard, ConsequenceCard, MetricBar, RelationshipMiniCard, StoryArcCard, SummaryCard


class BaseScreen(QWidget):
    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__()
        self.engine = engine
        self.layout = QVBoxLayout(self)

    def refresh(self) -> None:
        return


class DashboardScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine, open_screen) -> None:
        super().__init__(engine)
        self.open_screen = open_screen
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.layout.addWidget(scroll)

        holder = QWidget()
        self.grid = QGridLayout(holder)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(holder)

        self.today = SummaryCard("1) Today's Desk", button_label="Open Routine", on_open=lambda: open_screen("Routine"))
        self.casework = SummaryCard("2) Casework Inbox", button_label="Open Inbox", on_open=lambda: open_screen("Inbox"))
        self.routine = AgendaItemCard("3) Today's Routine", button_label="Open Routine", on_open=lambda: open_screen("Routine"))
        self.ward = SummaryCard("4) Ward Mood", button_label="Open Constituency", on_open=lambda: open_screen("Constituency"))
        self.party = SummaryCard("5) Party Pressure", button_label="Open Party", on_open=lambda: open_screen("Party"))
        self.relationships = RelationshipMiniCard("6) Relationships", button_label="Open Relationships", on_open=lambda: open_screen("Relationships"))
        self.career = SummaryCard("7) Career Track", button_label="Open Career", on_open=lambda: open_screen("Career"))
        self.news = SummaryCard("8) News / Local Chatter", button_label="Open Log", on_open=lambda: open_screen("Log"))
        self.alerts = AlertCard("9) Alerts", button_label="Open Inbox", on_open=lambda: open_screen("Inbox"))
        self.consequence = ConsequenceCard("10) Recent Consequence", button_label="Open Decision Result", on_open=lambda: open_screen("Decision Result"))
        self.story = StoryArcCard("Active Local Story", button_label="Open Stories", on_open=lambda: open_screen("Stories"))

        cards = [self.today, self.casework, self.routine, self.ward, self.party, self.relationships, self.career, self.news, self.alerts, self.consequence, self.story]
        for idx, card in enumerate(cards):
            self.grid.addWidget(card, idx // 2, idx % 2)

    def refresh(self) -> None:
        s = self.engine.state
        assert s
        c = s.constituencies[s.player.constituency_id]
        open_items = [i for i in s.routine_items if i.status == ItemStatus.OPEN]
        top = open_items[0] if open_items else None
        self.today.update_body(
            f"{s.current_date.strftime('%A %d %b %Y')} | {s.time_slot.value}\n"
            f"Next required action: {'Handle a slot item' if self.engine.items_for_current_slot() else 'Advance time'}\n"
            f"Top agenda item: {top.title if top else 'None'}"
        )

        oldest = next((i.title for i in open_items), "None")
        urgent = len([i for i in open_items if i.urgency.value in {"High", "Critical"}])
        self.casework.update_body(
            f"Open resident issues: {s.player.casework_backlog}\nUrgent complaints: {urgent}\n"
            f"Oldest unresolved: {oldest}"
        )

        lines = []
        for slot in [TimeSlot.MORNING, TimeSlot.AFTERNOON, TimeSlot.EVENING, TimeSlot.LATE_NIGHT]:
            slot_ids = s.daily_agenda.items_by_slot.get(slot, [])
            item = next((i for i in s.routine_items if i.id in slot_ids), None)
            state = item.status.value if item else "Pending"
            lines.append(f"{slot.value}: {(item.title if item else 'No fixed item')} ({state})")
        self.routine.update_body("\n".join(lines))

        self.ward.update_body(
            f"Resident trust: {s.player.resident_trust}\nLocal issue pressure: {c.local_issue_pressure}\n"
            f"Local media heat: {c.local_media_heat}\nFlashpoint: {c.current_flashpoint}\nRival activity: {s.player.rival_threat}"
        )
        faction_pressure = max((f.pressure for f in s.factions.values()), default=50)
        self.party.update_body(
            f"Party group trust: {s.player.party_group_trust}\nBranch support: {s.player.branch_support}\n"
            f"Faction pressure: {faction_pressure}\nCurrent conflict: {'Yes' if s.player.party_group_trust < 45 else 'Manageable'}"
        )

        top_ally = max(s.relationships.values(), key=lambda r: r.score)
        top_risk = min(s.relationships.values(), key=lambda r: r.score)
        self.relationships.update_body(
            f"Top ally: {top_ally.label} ({top_ally.score})\nTop rival: Main Rival Councillor ({s.relationships['main_rival'].score})\n"
            f"Relationship at risk: {top_risk.label} ({top_risk.score})\nLatest movement: Check Decision Result"
        )

        progress = min(100, int((s.player.reputation + s.player.local_base + s.player.branch_support + s.player.career_momentum * 12) / 4))
        self.career.update_body(
            f"Current role: {s.career.current_role.value}\nNext target: {s.career.path_target.value}\nReputation: {s.player.reputation}\n"
            f"Local base: {s.player.local_base}\nBranch support: {s.player.branch_support}\n"
            f"Career momentum: {s.player.career_momentum}\nAssembly selection progress: {progress}%"
        )

        self.news.update_body("\n".join(s.event_log[-4:]))

        alerts = []
        if any(i.slots_remaining <= 1 and i.status == ItemStatus.OPEN for i in open_items):
            alerts.append("Item expires soon")
        if s.player.stamina <= 25:
            alerts.append("Stamina low")
        if s.player.rival_threat >= 55:
            alerts.append("Rival gaining credit")
        if s.player.branch_support <= 45:
            alerts.append("Branch unhappy")
        if s.player.officer_relationship <= 40:
            alerts.append("Officer relationship deteriorating")
        if c.local_media_heat >= 55:
            alerts.append("Local media waiting for comment")
        self.alerts.update_body("\n".join(alerts) if alerts else "No urgent warnings right now.")

        self.consequence.update_body(s.recent_consequence or "No recent consequence yet.")
        active = [a for a in s.active_story_arcs if a.status == StoryStatus.ACTIVE]
        if active:
            a = active[0]
            self.story.update_body(
                f"{a.title} | stage {a.current_stage}\nPressure: {a.pressure_level}\nPublic visibility: {a.public_visibility}\n"
                f"Player ownership: {a.player_ownership}\nRival ownership: {a.rival_ownership}\nNext: {a.next_possible_moments[min(a.current_stage-1, len(a.next_possible_moments)-1)]}"
            )
        else:
            self.story.update_body("No active stories.")


class InboxScreen(BaseScreen):
    def __init__(self, engine: SimulationEngine, on_result) -> None:
        super().__init__(engine)
        self.on_result = on_result
        self.listing = QListWidget()
        self.decisions = QComboBox()
        self.decision_context = QLabel()
        self.decision_context.setWordWrap(True)
        row = QHBoxLayout()
        self.apply_btn = QPushButton("Handle")
        self.ignore_btn = QPushButton("Delay/Ignore")
        self.advance_btn = QPushButton("Advance Time Slot")
        row.addWidget(self.apply_btn)
        row.addWidget(self.ignore_btn)
        row.addWidget(self.advance_btn)

        self.layout.addWidget(self.listing)
        self.layout.addWidget(self.decisions)
        self.layout.addWidget(self.decision_context)
        self.layout.addLayout(row)

        self.listing.currentRowChanged.connect(self._load_decisions)
        self.decisions.currentIndexChanged.connect(self._update_decision_context)
        self.apply_btn.clicked.connect(self._apply)
        self.ignore_btn.clicked.connect(self._ignore)
        self.advance_btn.clicked.connect(self._advance)

    def refresh(self) -> None:
        s = self.engine.state
        assert s
        self.listing.clear()
        grouped = {"urgent": [], "waiting on officer": [], "awaiting player response": [], "escalated": [], "resolved": []}
        for i in s.routine_items:
            if i.status == ItemStatus.HANDLED:
                grouped["resolved"].append(i)
            elif i.status in {ItemStatus.EXPIRED, ItemStatus.TAKEN_BY_OTHERS}:
                grouped["escalated"].append(i)
            elif i.category.value == "Officer Follow-Up":
                grouped["waiting on officer"].append(i)
            elif i.urgency.value in {"High", "Critical"}:
                grouped["urgent"].append(i)
            else:
                grouped["awaiting player response"].append(i)
        for label, items in grouped.items():
            if not items:
                continue
            self.listing.addItem(f"--- {label.upper()} ---")
            for i in items:
                self.listing.addItem(f"{i.id} | {i.title} | {i.status.value} | expires {i.slots_remaining}")
        self._load_decisions(self.listing.currentRow())

    def _selected_item(self):
        s = self.engine.state
        assert s
        text = self.listing.currentItem().text() if self.listing.currentItem() else ""
        if text.startswith("---") or "|" not in text:
            return None
        item_id = text.split("|", 1)[0].strip()
        return next((i for i in s.routine_items if i.id == item_id), None)

    def _load_decisions(self, _: int) -> None:
        self.decisions.clear()
        item = self._selected_item()
        if not item:
            self.decision_context.setText("Select an actionable item.")
            return
        for d in self.engine.available_decisions(item):
            self.decisions.addItem(d.label, d.id)
        self._update_decision_context()

    def _update_decision_context(self) -> None:
        item = self._selected_item()
        if not item:
            return
        d_id = self.decisions.currentData()
        decision = next((d for d in self.engine.available_decisions(item) if d.id == d_id), None)
        if not decision:
            return
        affected = ", ".join(decision.affected_groups or item.involved_relationships or ["Residents", "Officers", "Rival"])
        self.decision_context.setText(
            f"Decision: {decision.label}\n"
            f"Short explanation: {item.description}\n"
            f"Likely upside: {decision.likely_upside or 'Improves issue handling visibility.'}\n"
            f"Likely risk: {decision.likely_risk or 'Can increase pressure if follow-up is weak.'}\n"
            f"Cost: Stamina -{decision.stamina_cost}, Influence -{decision.influence_cost}\n"
            f"Affected groups: {affected}"
        )

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
        self.card = SummaryCard("Today's Agenda")
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
                    link = f" [Story: {item.story_arc_id}]" if item.story_arc_id else ""
                    lines.append(f"  - {item.title} [{item.category.value}] ({item.status.value}){link}")
        self.card.update_body("\n".join(lines))


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
        for arc in s.active_story_arcs:
            lines.append(
                f"{arc.title} ({arc.theme})\n"
                f"Status: {arc.status.value} | Stage: {arc.current_stage}\n"
                f"Pressure {arc.pressure_level} | Public visibility {arc.public_visibility}\n"
                f"Player ownership {arc.player_ownership} | Rival ownership {arc.rival_ownership}\n"
                f"Next development: {arc.next_possible_moments[min(arc.current_stage-1, len(arc.next_possible_moments)-1)]}\n"
                f"Memory flags: {', '.join([k for k, v in arc.memory.items() if v]) or 'None'}\n"
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
        s = self.engine.state
        assert s
        self.text.setPlainText("\n\n".join(s.event_log[-120:]))
