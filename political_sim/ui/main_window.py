from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from ..engine import SimulationEngine
from .screens import DashboardScreen, InboxScreen, LogScreen, RoutineScreen, SimpleTextScreen, StoriesScreen


class MainWindow(QMainWindow):
    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Councillor Routine and Beat Prototype")
        self.resize(1360, 860)

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
            "Inbox / Casework",
            "Today’s Flow",
            "Stories",
            "Party / Branch",
            "Factions",
            "Actors",
            "Constituency",
            "Relationships",
            "Career",
            "Decision Result",
            "Log",
        ]
        self.nav.addItems(self.screen_names)
        self.nav.setMaximumWidth(190)
        body.addWidget(self.nav)

        self.stack = QStackedWidget()
        body.addWidget(self.stack, 1)

        self.dashboard = DashboardScreen(engine, self.open_screen)
        self.inbox = InboxScreen(engine, self._set_result)
        self.routine = RoutineScreen(engine)
        self.stories = StoriesScreen(engine)
        self.party = SimpleTextScreen(engine, "Party / Branch", self._party_text)
        self.factions = SimpleTextScreen(engine, "Factions", self._faction_text)
        self.actors = SimpleTextScreen(engine, "Actors", self._actors_text)
        self.constituency = SimpleTextScreen(engine, "Constituency", self._constituency_text)
        self.relationships = SimpleTextScreen(engine, "Relationships", self._relationship_text)
        self.career = SimpleTextScreen(engine, "Career", self._career_text)
        self.result = SimpleTextScreen(engine, "Decision Result", lambda: self.engine.state.current_result)
        self.log = LogScreen(engine)

        for screen in [self.dashboard, self.inbox, self.routine, self.stories, self.party, self.factions, self.actors, self.constituency, self.relationships, self.career, self.result, self.log]:
            self.stack.addWidget(screen)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.currentRowChanged.connect(lambda _: self.refresh_all())
        self.nav.setCurrentRow(0)
        self.refresh_all()

    def open_screen(self, name: str) -> None:
        if name in self.screen_names:
            self.nav.setCurrentRow(self.screen_names.index(name))

    def _set_result(self, _result: str) -> None:
        self.refresh_all()
        self.open_screen("Decision Result")

    def refresh_all(self) -> None:
        s = self.engine.state
        self.top.setText(
            f"Date: {s.game_date.value.isoformat()} | Slot: {s.current_slot.value} | Player: {s.player.name} | "
            f"Role: {s.career.current_role.value} | Party: {s.party.name} | Constituency: {s.constituency.name} | "
            f"Stamina: {s.player.stamina} | Influence: {s.player.influence}"
        )
        for i in range(self.stack.count()):
            self.stack.widget(i).refresh()

    def _party_text(self) -> str:
        s = self.engine.state
        return (
            f"Party group trust: {s.relationships['party_figure'].score}\n"
            f"Branch support: {s.player.branch_support}\n"
            f"Current expectation: balance ward routine with Stormont campaign support."
        )

    def _faction_text(self) -> str:
        s = self.engine.state
        return "\n".join(f"- {f.name}: pressure {f.pressure}" for f in s.factions.values())

    def _actors_text(self) -> str:
        s = self.engine.state
        return "\n".join(f"- {a.name} ({a.role})" for a in s.actors.values())

    def _constituency_text(self) -> str:
        s = self.engine.state
        return f"{s.constituency.name}\nCurrent flashpoint: {s.constituency.flashpoint}"

    def _relationship_text(self) -> str:
        s = self.engine.state
        return "\n".join(f"- {r.label}: {r.score}" for r in s.relationships.values())

    def _career_text(self) -> str:
        s = self.engine.state
        return (
            "Councillor -> Candidate -> MLA -> Junior Minister\n"
            f"Reputation: {s.player.reputation}, local base: {s.player.local_base}, branch support: {s.player.branch_support}\n"
            f"Career momentum: {s.player.career_momentum}, rival threat: {s.player.rival_threat}\n"
            f"Assembly selection open: {'Yes' if s.career.assembly_selection_open else 'No'}"
        )
