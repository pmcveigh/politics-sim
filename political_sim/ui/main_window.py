from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from ..engine import SimulationEngine
from .screens import DashboardScreen, InboxScreen, LogScreen, SimpleTextScreen


class MainWindow(QMainWindow):
    def __init__(self, engine: SimulationEngine) -> None:
        super().__init__()
        self.engine = engine
        self.setWindowTitle("Northern Ireland Political Simulator - MVP")
        self.resize(1300, 760)

        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)

        self.top = QLabel()
        outer.addWidget(self.top)

        body = QHBoxLayout()
        outer.addLayout(body)

        self.nav = QListWidget()
        self.nav.addItems(["Dashboard", "Inbox", "Party", "Factions", "Actors", "Constituency", "Relationships", "Career", "Decision Result", "Log"])
        self.nav.setMaximumWidth(180)
        body.addWidget(self.nav)

        self.stack = QStackedWidget()
        body.addWidget(self.stack, 1)

        self.context = QLabel()
        self.context.setWordWrap(True)
        self.context.setMaximumWidth(280)
        body.addWidget(self.context)

        self.dashboard = DashboardScreen(engine)
        self.inbox = InboxScreen(engine, self._set_result)
        self.party = SimpleTextScreen(engine, "Party", self._party_text)
        self.factions = SimpleTextScreen(engine, "Factions", self._factions_text)
        self.actors = SimpleTextScreen(engine, "Actors", self._actors_text)
        self.constituency = SimpleTextScreen(engine, "Constituency", self._constituency_text)
        self.relationships = SimpleTextScreen(engine, "Relationships", self._relationships_text)
        self.career = SimpleTextScreen(engine, "Career", self._career_text)
        self.result = SimpleTextScreen(engine, "Decision Result", lambda: engine.state.current_result if engine.state and engine.state.current_result else "No decision yet")
        self.log = LogScreen(engine)

        for screen in [self.dashboard, self.inbox, self.party, self.factions, self.actors, self.constituency, self.relationships, self.career, self.result, self.log]:
            self.stack.addWidget(screen)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.currentRowChanged.connect(lambda _: self.refresh_all())
        self.nav.setCurrentRow(0)
        self.refresh_all()

    def refresh_all(self) -> None:
        s = self.engine.state
        assert s
        self.top.setText(
            f"Date: {s.current_date.isoformat()} | Slot: {s.time_slot.value} | Player: {s.player.name} | Role: {s.player.role.value} | "
            f"Party: {s.parties[s.player.party_id].name} | Constituency: {s.constituencies[s.player.constituency_id].name} | "
            f"Stamina: {s.player.stamina} | Influence: {s.player.influence}"
        )
        self.context.setText(self._context_text())
        for i in range(self.stack.count()):
            self.stack.widget(i).refresh()

    def _set_result(self, _: str) -> None:
        self.refresh_all()
        self.nav.setCurrentRow(8)

    def _context_text(self) -> str:
        s = self.engine.state
        assert s
        party = s.parties[s.player.party_id]
        warnings = []
        if party.scandal_risk > 55:
            warnings.append("Scandal risk high")
        if s.player.stamina < 35:
            warnings.append("Player stamina low")
        if s.relationships["leader"].score < 45:
            warnings.append("Leader trust fragile")
        return (
            "Context summary\n"
            f"Next moments: {', '.join([m.title for m in s.active_moments[:2]])}\n"
            f"Branch relationship: {s.relationships['local_branch'].score}\n"
            f"Media relationship: {s.relationships['local_media'].score}\n"
            f"Warnings: {', '.join(warnings) if warnings else 'None'}"
        )

    def _party_text(self) -> str:
        s = self.engine.state
        assert s
        p = s.parties[s.player.party_id]
        custom = "\n".join([f"- {k}: {v}" for k, v in p.custom_variables.items()])
        return (
            f"Party: {p.name}\nLeader: {s.actors[p.leader_actor_id].name if p.leader_actor_id in s.actors else p.leader_actor_id}\n"
            f"unity {p.party_unity}, authority {p.leader_authority}, morale {p.activist_morale}, trust {p.public_trust}, media pressure {p.media_pressure}, scandal risk {p.scandal_risk}\n"
            f"election readiness {p.election_readiness}, faction pressure {p.faction_pressure}, government credibility {p.government_credibility}, machine {p.local_machine_strength}\n"
            f"Custom variables:\n{custom}"
        )

    def _factions_text(self) -> str:
        s = self.engine.state
        assert s
        rows = [f"- {f.name}: strength {f.strength}, agitation {f.agitation}, loyalty {f.loyalty_to_leader}, rel(player) {f.relationship_with_player}" for f in s.factions.values() if f.party_id == s.player.party_id]
        return "\n".join(rows)

    def _actors_text(self) -> str:
        s = self.engine.state
        assert s
        rows = [f"- {a.name}: {a.role.value}, reputation {a.reputation}, influence {a.influence}, current attitude {'Ally' if a.loyalty_to_party > 55 else 'Guarded'}" for a in s.actors.values() if a.party_id == s.player.party_id][:10]
        return "\n".join(rows)

    def _constituency_text(self) -> str:
        s = self.engine.state
        assert s
        c = s.constituencies[s.player.constituency_id]
        machine = ", ".join([f"{k}:{v}" for k, v in c.party_machine_strength.items()])
        return f"{c.name}\nFlashpoint: {c.current_flashpoint}\nLocal issue pressure: {c.local_issue_pressure}\nLocal media heat: {c.local_media_heat}\nParty machine strengths: {machine}\nVoter blocs U/N/C: {c.unionist_strength}/{c.nationalist_strength}/{c.cross_community_strength}"

    def _relationships_text(self) -> str:
        s = self.engine.state
        assert s
        rows = [f"- {r.label}: {r.score}" for r in s.relationships.values()]
        return "\n".join(rows) + "\nAllies and rivals are created through moments and reactions."

    def _career_text(self) -> str:
        s = self.engine.state
        assert s
        if s.player.role.value == "Councillor":
            next_step = "Assembly selection"
        elif s.player.role.value == "Candidate":
            next_step = "Assembly election"
        elif s.player.role.value == "MLA":
            next_step = "Junior minister offer"
        else:
            next_step = "Consolidate current post"
        return (
            f"Current role: {s.career.current_role.value}\nCareer momentum: {s.player.career_momentum}\n"
            f"Eligibility progress: reputation {s.player.reputation}/55, local base {s.player.local_base}/50, branch {s.relationships['local_branch'].score}/50, momentum {s.player.career_momentum}/5\n"
            f"Possible next step: {next_step}\nPromotion offers: {[r.value for r in s.career.promotion_offers]}\n"
            f"Recent career events: {', '.join(s.career.recent_events[-5:]) if s.career.recent_events else 'None yet'}"
        )
