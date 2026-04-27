from __future__ import annotations

from typing import List

from .engine import SimulationEngine
from .models import PoliticalMoment, Role


class TerminalUI:
    def __init__(self, engine: SimulationEngine) -> None:
        self.engine = engine

    def run(self) -> None:
        self._setup_game()
        while True:
            print("\n=== Northern Ireland Political Simulator (Daily Political Moments) ===")
            print("1. View today's agenda")
            print("2. Respond to a moment")
            print("3. Ignore/defer a moment")
            print("4. View player profile")
            print("5. View party overview")
            print("6. View faction overview")
            print("7. View constituency overview")
            print("8. View relationships")
            print("9. Advance time")
            print("10. View event log")
            print("11. Quit")
            self.show_dashboard()
            choice = input("Select: ").strip()
            if choice == "1":
                self.show_agenda()
            elif choice == "2":
                self.respond_to_moment()
            elif choice == "3":
                self.ignore_moment()
            elif choice == "4":
                self.show_player_profile()
            elif choice == "5":
                self.show_party_overview()
            elif choice == "6":
                self.show_factions()
            elif choice == "7":
                self.show_constituency()
            elif choice == "8":
                self.show_relationships()
            elif choice == "9":
                print(self.engine.advance_time_slot())
            elif choice == "10":
                self.show_event_log()
            elif choice == "11":
                print("Goodbye.")
                break

    def _setup_game(self) -> None:
        print("Welcome. Every day is politically active.")
        name = input("Your name: ").strip() or "Player"
        party_id = self._pick_from(["unionist_front", "people_first", "civic_alliance"], "Choose party")
        role = Role(self._pick_from([r.value for r in Role], "Choose starting role"))
        constituency = self._pick_from(
            ["East Belfast", "North Down", "Fermanagh and South Tyrone", "West Belfast", "Lagan Valley"],
            "Choose constituency",
        )
        state = self.engine.create_simulation(name, party_id, role, constituency, faction="Local network")
        print(f"Simulation started on {state.game_date.label()}.")

    @staticmethod
    def _pick_from(options: List[str], prompt: str) -> str:
        print(f"{prompt}:")
        for i, option in enumerate(options, start=1):
            print(f"  {i}. {option}")
        while True:
            pick = input("Number: ").strip()
            if pick.isdigit() and 1 <= int(pick) <= len(options):
                return options[int(pick) - 1]
            print("Invalid choice.")

    def show_dashboard(self) -> None:
        s = self.engine.state
        assert s is not None
        print(
            f"\nDate: {s.game_date.label()} | Role: {s.player.career.current_role.value} | "
            f"Stamina: {s.player.stamina} | Party: {s.parties[s.player.party_id].name} | Constituency: {s.player.constituency}"
        )
        urgent = [m for m in s.daily_agenda.moments if m.urgency.value in ["high", "critical"]]
        if urgent:
            print("Urgent warnings:")
            for m in urgent:
                print(f"- {m.title} ({m.urgency.value})")

    def show_agenda(self) -> None:
        s = self.engine.state
        print("Today's agenda:")
        if not s.daily_agenda.moments:
            print("- No remaining moments today.")
            return
        for m in s.daily_agenda.moments:
            print(f"- [{m.time_slot.value}] {m.title} | {m.category.value} | urgency: {m.urgency.value}")

    def _pick_moment(self) -> PoliticalMoment | None:
        s = self.engine.state
        if not s.daily_agenda.moments:
            print("No moments available.")
            return None
        for i, m in enumerate(s.daily_agenda.moments, start=1):
            print(f"{i}. [{m.time_slot.value}] {m.title} ({m.urgency.value})")
        pick = input("Pick moment: ").strip()
        if not pick.isdigit() or not (1 <= int(pick) <= len(s.daily_agenda.moments)):
            print("Invalid choice.")
            return None
        return s.daily_agenda.moments[int(pick) - 1]

    def respond_to_moment(self) -> None:
        moment = self._pick_moment()
        if not moment:
            return
        options = self.engine.get_available_options(moment)
        if not options:
            print("No actions available for this role.")
            return
        print(f"\n{moment.title}\n{moment.description}")
        for i, option in enumerate(options, start=1):
            action_type = "minor" if option.is_minor_action else "main"
            print(f"{i}. ({action_type}) {option.text}")
        pick = input("Choose option: ").strip()
        if not pick.isdigit() or not (1 <= int(pick) <= len(options)):
            print("Invalid choice.")
            return
        print("\nDecision result:")
        print(self.engine.apply_decision(moment.id, options[int(pick) - 1].id))

    def ignore_moment(self) -> None:
        moment = self._pick_moment()
        if not moment:
            return
        print(self.engine.ignore_moment(moment.id))

    def show_player_profile(self) -> None:
        p = self.engine.state.player
        print(f"Name: {p.name} | Role: {p.career.current_role.value} | Constituency: {p.constituency}")
        print(f"Reputation {p.reputation} | Influence {p.influence} | Party trust {p.party_trust} | Leader trust {p.leader_trust}")
        print(f"Local base {p.local_base} | Media profile {p.media_profile} | Career momentum {p.career_momentum} | Stamina {p.stamina}")

    def show_party_overview(self) -> None:
        s = self.engine.state
        party = s.parties[s.player.party_id]
        print(f"Party: {party.name} | Leader: {party.leader}")
        for k, v in party.variables.items():
            print(f"- {k}: {v}")

    def show_factions(self) -> None:
        s = self.engine.state
        party = s.parties[s.player.party_id]
        print("Factions:")
        for f in party.factions:
            print(f"- {f.name}: influence {f.influence}, discipline {f.discipline}, leader loyalty {f.loyalty_to_leader}")

    def show_constituency(self) -> None:
        s = self.engine.state
        c = s.constituencies[s.player.constituency]
        print(f"Constituency: {c.name}")
        print(f"Unionist {c.unionist_strength} | Nationalist {c.nationalist_strength} | Cross-community {c.cross_community_strength}")
        print(f"Turnout energy {c.turnout_energy} | Local issue pressure {c.local_issue_pressure}")

    def show_relationships(self) -> None:
        rel = self.engine.state.player.relationships
        print("Relationships:")
        for item in rel.values():
            print(f"- {item.target}: {item.score}")

    def show_event_log(self) -> None:
        for entry in self.engine.state.event_log[-20:]:
            print(f"- {entry}")
