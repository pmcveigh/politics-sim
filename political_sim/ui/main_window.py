from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from ..engine import SimulationEngine
from .screens import DashboardScreen, InboxScreen, LogScreen, RoutineScreen, SimpleTextScreen, StoriesScreen


class MainWindow(QMainWindow):
    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Northern Ireland Councillor Political Simulator")
        self.resize(1360, 820)

        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)

        self.top = QLabel()
        outer.addWidget(self.top)

        body = QHBoxLayout()
        outer.addLayout(body)

        self.nav = QListWidget()
        self.screen_names = [
            "Dashboard",
            "Inbox",
            "Routine",
            "Stories",
            "Party",
            "Factions",
            "Actors",
            "Constituency",
            "Relationships",
            "Career",
            "Decision Result",
            "Log",
        ]
        self.nav.addItems(self.screen_names)
        self.nav.setMaximumWidth(180)
        body.addWidget(self.nav)

        self.stack = QStackedWidget()
        body.addWidget(self.stack, 1)

        self.context = QLabel()
        self.context.setWordWrap(True)
        self.context.setMaximumWidth(320)
        body.addWidget(self.context)

        self.dashboard = DashboardScreen(engine, self.open_screen)
        self.inbox = InboxScreen(engine, self._set_result)
        self.routine = RoutineScreen(engine)
        self.stories = StoriesScreen(engine)
        self.party = SimpleTextScreen(engine, "Party", self._party_text)
        self.factions = SimpleTextScreen(engine, "Factions", self._factions_text)
        self.actors = SimpleTextScreen(engine, "Actors", self._actors_text)
        self.constituency = SimpleTextScreen(engine, "Constituency", self._constituency_text)
        self.relationships = SimpleTextScreen(engine, "Relationships", self._relationships_text)
        self.career = SimpleTextScreen(engine, "Career", self._career_text)
        self.result = SimpleTextScreen(engine, "Decision Result", lambda: self.engine.state.current_result if self.engine.state else "")
        self.log = LogScreen(engine)

        for screen in [
            self.dashboard,
            self.inbox,
            self.routine,
            self.stories,
            self.party,
            self.factions,
            self.actors,
            self.constituency,
            self.relationships,
            self.career,
            self.result,
            self.log,
        ]:
            self.stack.addWidget(screen)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.currentRowChanged.connect(lambda _: self.refresh_all())
        self.nav.setCurrentRow(0)
        self.refresh_all()

    def open_screen(self, name: str) -> None:
        if name in self.screen_names:
            self.nav.setCurrentRow(self.screen_names.index(name))

    def refresh_all(self) -> None:
        s = self.engine.state
        assert s
        self.top.setText(
            f"Date: {s.current_date.isoformat()} | Day: {s.current_date.strftime('%A')} | Time Slot: {s.time_slot.value} | "
            f"Player: {s.player.name} | Role: {s.player.role.value} | Party: {s.parties[s.player.party_id].name} | "
            f"Constituency: {s.constituencies[s.player.constituency_id].name} | Stamina: {s.player.stamina} | Influence: {s.player.influence}"
        )
        self.context.setText(self._context_text())
        for i in range(self.stack.count()):
            self.stack.widget(i).refresh()

    def _set_result(self, _: str) -> None:
        self.refresh_all()
        self.open_screen("Decision Result")

    def _context_text(self) -> str:
        s = self.engine.state
        assert s
        backlog_warning = "High" if s.player.casework_backlog >= 8 else "Manageable"
        rel = min(s.relationships.values(), key=lambda r: r.score)
        active_arc = next((a for a in s.active_story_arcs if a.status.value == "Active"), None)
        return (
            f"Warnings desk\n"
            f"Backlog: {backlog_warning} ({s.player.casework_backlog})\n"
            f"Flashpoint: {s.constituencies[s.player.constituency_id].current_flashpoint}\n"
            f"Relationship risk: {rel.label} ({rel.score})\n"
            f"Rival activity: threat {s.player.rival_threat}\n"
            f"Active story: {active_arc.title if active_arc else 'None'}"
        )

    def _party_text(self) -> str:
        s = self.engine.state
        assert s
        return (
            f"Party group trust: {s.player.party_group_trust}\n"
            f"Branch support: {s.player.branch_support}\n"
            f"Pressure today: routine discipline vs local responsiveness.\n"
            f"Current line conflict: {'Yes' if s.player.party_group_trust < 45 else 'No'}"
        )

    def _factions_text(self) -> str:
        s = self.engine.state
        assert s
        return "\n".join([f"- {f.name}: pressure {f.pressure}, relationship {s.relationships['key_faction'].score}" for f in s.factions.values()])

    def _actors_text(self) -> str:
        s = self.engine.state
        assert s
        return "\n".join([f"- {a.name} ({a.role.value})" for a in s.actors.values()])

    def _constituency_text(self) -> str:
        s = self.engine.state
        assert s
        c = s.constituencies[s.player.constituency_id]
        return (
            f"Flashpoint: {c.current_flashpoint}\n"
            f"Local issue pressure: {c.local_issue_pressure}\nLocal media heat: {c.local_media_heat}\nResident satisfaction: {c.resident_satisfaction}"
        )

    def _relationships_text(self) -> str:
        s = self.engine.state
        assert s

        def label(score: int) -> str:
            if score >= 60:
                return "trusted"
            if score >= 50:
                return "supportive"
            if score >= 40:
                return "wary"
            return "hostile"

        return "\n".join([f"- {r.label}: {r.score} ({label(r.score)})" for r in s.relationships.values()])

    def _career_text(self) -> str:
        s = self.engine.state
        assert s
        progress = min(100, int((s.player.reputation + s.player.local_base + s.player.branch_support + s.player.career_momentum * 12) / 4))
        return (
            f"Current role: {s.career.current_role.value}\n"
            f"Path target: Assembly selection\n"
            f"Requirements progress -> reputation {s.player.reputation}/55, local base {s.player.local_base}/50, "
            f"branch {s.player.branch_support}/50, momentum {s.player.career_momentum}/5\n"
            f"Career progress: {progress}%\n"
            f"Faction support: {s.relationships['key_faction'].score}\nRival threat: {s.player.rival_threat}\n"
            f"Assembly selection open: {'Yes' if s.career.assembly_selection_open else 'No'}"
        )
