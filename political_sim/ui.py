from __future__ import annotations

from typing import List

from .engine import SimulationEngine
from .models import Role


class TerminalUI:
    def __init__(self, engine: SimulationEngine) -> None:
        self.engine = engine

    def run(self) -> None:
        self._setup_game()
        while True:
            print("\n=== Northern Ireland Political Simulator (Stage 1) ===")
            print("1. Main dashboard")
            print("2. Player profile")
            print("3. Party overview")
            print("4. Faction overview")
            print("5. Constituency overview")
            print("6. Current political moment")
            print("7. Career opportunities")
            print("8. Relationship overview")
            print("9. Event log")
            print("0. Exit")
            choice = input("Select: ").strip()
            if choice == "1":
                self.show_dashboard()
            elif choice == "2":
                self.show_player_profile()
            elif choice == "3":
                self.show_party_overview()
            elif choice == "4":
                self.show_factions()
            elif choice == "5":
                self.show_constituency()
            elif choice == "6":
                self.play_moment()
            elif choice == "7":
                self.show_career_opportunities()
            elif choice == "8":
                self.show_relationships()
            elif choice == "9":
                self.show_event_log()
            elif choice == "0":
                print("Goodbye.")
                break

    def _setup_game(self) -> None:
        print("Welcome. You are one actor inside a moving political system.")
        name = input("Your name: ").strip() or "Player"
        party_id = self._pick_from(["unionist_front", "people_first", "civic_alliance"], "Choose party")
        role = Role(self._pick_from([r.value for r in Role], "Choose starting role"))
        constituency = self._pick_from(
            ["East Belfast", "North Down", "Fermanagh and South Tyrone", "West Belfast", "Lagan Valley"],
            "Choose constituency",
        )
        party = self.engine.create_simulation(name, party_id, role, constituency, faction="Local network")
        print(f"Simulation started on Day {party.current_day}.")

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
        print(f"Day {s.current_day} | Role: {s.player.career.current_role.value} | Party: {s.parties[s.player.party_id].name}")
        print("Politics continues around you; moments jump to meaningful decisions.")

    def show_player_profile(self) -> None:
        p = self.engine.state.player
        print(f"Name: {p.name} | Role: {p.career.current_role.value} | Constituency: {p.constituency}")
        print(f"Reputation {p.reputation} | Influence {p.influence} | Party trust {p.party_trust} | Leader trust {p.leader_trust}")
        print(f"Local base {p.local_base} | Media profile {p.media_profile} | Career momentum {p.career_momentum}")

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
        print(f"Party machine strengths: {c.party_machine_strength}")

    def play_moment(self) -> None:
        moment = self.engine.draw_moment()
        options = self.engine.get_available_options(moment)
        print(f"\n[{moment.time_mode.value}] {moment.title}")
        print(moment.description)
        if not options:
            print("No actions available at your current rank.")
            return
        for i, option in enumerate(options, start=1):
            print(f"{i}. {option.text}")
        while True:
            pick = input("Choose option: ").strip()
            if pick.isdigit() and 1 <= int(pick) <= len(options):
                selected = options[int(pick) - 1]
                break
            print("Invalid option.")
        result = self.engine.apply_decision(selected.id)
        print("\nDecision result:")
        print(result)

    def show_career_opportunities(self) -> None:
        player = self.engine.state.player
        if not player.career.opportunities:
            print("No active career openings right now.")
            return
        print("Career opportunities:")
        for i, role in enumerate(player.career.opportunities, start=1):
            print(f"{i}. {role.value}")
        pick = input("Accept one? enter number or press Enter to leave: ").strip()
        if pick.isdigit() and 1 <= int(pick) <= len(player.career.opportunities):
            role = player.career.opportunities[int(pick) - 1]
            print(self.engine.accept_opportunity(role))

    def show_relationships(self) -> None:
        rel = self.engine.state.player.relationships
        print("Relationships:")
        for item in rel.values():
            print(f"- {item.target}: {item.score}")

    def show_event_log(self) -> None:
        for entry in self.engine.state.event_log[-15:]:
            print(f"- {entry}")
