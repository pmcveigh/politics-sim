from __future__ import annotations

import random
from typing import List

from .engine import SimulationEngine
from .models import Moment, Role


class TerminalUI:
    def __init__(self, engine: SimulationEngine) -> None:
        self.engine = engine

    def run(self) -> None:
        self.setup_game()
        while True:
            self.show_header()
            print("1. View today's agenda")
            print("2. Respond to a political moment")
            print("3. Ignore or defer a moment")
            print("4. View player profile")
            print("5. View party overview")
            print("6. View faction overview")
            print("7. View constituency overview")
            print("8. View relationships")
            print("9. Advance time")
            print("10. View event log")
            print("11. Quit")
            choice = input("Select: ").strip()
            if choice == "1":
                self.show_agenda()
            elif choice == "2":
                self.respond_to_moment()
            elif choice == "3":
                self.ignore_or_defer()
            elif choice == "4":
                self.show_player_profile()
            elif choice == "5":
                self.show_party_overview()
            elif choice == "6":
                self.show_faction_overview()
            elif choice == "7":
                self.show_constituency_overview()
            elif choice == "8":
                self.show_relationships()
            elif choice == "9":
                print(self.engine.advance_time())
            elif choice == "10":
                self.show_event_log()
            elif choice == "11":
                print("Goodbye.")
                break

    def setup_game(self) -> None:
        print("Northern Ireland Political Simulator - Stage 1 terminal prototype")
        party_id = self.pick_option("Choose party", ["unionist_front", "people_first", "civic_alliance"])
        role = Role(self.pick_option("Choose role", [r.value for r in Role]))
        constituency = self.pick_option(
            "Choose constituency",
            ["East Belfast", "North Down", "Fermanagh and South Tyrone", "West Belfast", "Lagan Valley"],
        )
        typed_name = input("Player name (leave blank for generated name): ").strip()
        name = typed_name or self.generate_name()
        self.engine.create_simulation(name, party_id, role, constituency)

    @staticmethod
    def generate_name() -> str:
        first = random.choice(["Erin", "Cal", "Aoife", "Niall", "Megan", "Ciara", "Connor", "Leah", "Rory"])
        last = random.choice(["Wallace", "Donnelly", "McIvor", "Lennon", "Taggart", "Reid", "Sloan", "Mullan"])
        return f"{first} {last}"

    @staticmethod
    def pick_option(prompt: str, options: List[str]) -> str:
        print(prompt)
        for idx, option in enumerate(options, start=1):
            print(f"{idx}. {option}")
        while True:
            choice = input("Number: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice) - 1]
            print("Invalid option.")

    def show_header(self) -> None:
        s = self.engine.state
        assert s is not None
        actor = s.actors[s.player.actor_id]
        party = s.parties[actor.party_id]
        print("\n" + "=" * 72)
        print(f"Date: {s.date_label()}")
        print(f"Player: {actor.role.value} {actor.name}, {self.engine.player_constituency.name}, {party.party_type.value} party")
        print(f"Stamina: {s.player.stamina} | Influence: {actor.influence} | Career momentum: {s.player.career_momentum}")

    def show_agenda(self) -> None:
        s = self.engine.state
        assert s is not None
        print("Today's agenda:")
        if not s.active_moments:
            print("No active moments. Advance time to generate fresh pressure.")
            return
        for idx, moment in enumerate(s.active_moments, start=1):
            expiry_slot = min(3, moment.created_slot_index + moment.expires_after_slots)
            expiry_label = ["Morning", "Afternoon", "Evening", "Late Night"][expiry_slot]
            print(
                f"{idx}. {moment.title} | {', '.join(moment.institution_tags)} | {moment.urgency.value} urgency | expires {expiry_label}"
            )
            print(f"   Actors/Factions: {', '.join(moment.involved_actor_ids[:2])}; {', '.join(moment.faction_tags[:2])}")

    def choose_moment(self) -> Moment | None:
        s = self.engine.state
        assert s is not None
        if not s.active_moments:
            print("No moments to choose.")
            return None
        for idx, moment in enumerate(s.active_moments, start=1):
            print(f"{idx}. {moment.title} ({moment.urgency.value})")
        pick = input("Pick moment number: ").strip()
        if not pick.isdigit() or not 1 <= int(pick) <= len(s.active_moments):
            print("Invalid moment.")
            return None
        return s.active_moments[int(pick) - 1]

    def respond_to_moment(self) -> None:
        moment = self.choose_moment()
        if not moment:
            return
        print(f"\n{moment.title}\n{moment.description}")
        print(f"Consequence tension: {moment.consequence_summary}")
        decisions = self.engine.available_decisions(moment)
        if not decisions:
            print(self.engine.role_authority_message())
            return
        for idx, decision in enumerate(decisions, start=1):
            print(f"{idx}. {decision.label} | risk {decision.risk_level}/100 | stamina {decision.stamina_cost}")
            print(f"   {decision.description}")
        pick = input("Choose decision: ").strip()
        if not pick.isdigit() or not 1 <= int(pick) <= len(decisions):
            print("Invalid decision.")
            return
        print(self.engine.apply_decision(moment.id, decisions[int(pick) - 1].id))

    def ignore_or_defer(self) -> None:
        moment = self.choose_moment()
        if not moment:
            return
        action = self.pick_option("Ignore or defer", ["Ignore", "Defer"])
        print(self.engine.ignore_moment(moment.id, defer=(action == "Defer")))

    def show_player_profile(self) -> None:
        s = self.engine.state
        assert s is not None
        a = s.actors[s.player.actor_id]
        p = s.player
        print(f"{a.name} | {p.current_role.value}")
        print(f"Reputation: {a.reputation} | Competence: {a.competence} | Influence: {a.influence}")
        print(f"Party trust: {p.party_trust} | Leader trust: {p.leader_trust} | Faction support: {p.faction_support}")
        print(f"Local base: {p.local_base} | Media profile: {p.media_profile} | Stamina: {p.stamina}")
        print("Role-limited actions:")
        for action in p.available_actions:
            print(f"- {action}")
        if p.career_state.promotion_offers:
            print("Career opportunities:")
            for idx, role in enumerate(p.career_state.promotion_offers, start=1):
                print(f"{idx}. {role.value}")
            if input("Accept one now? (y/n): ").strip().lower() == "y":
                pick = input("Number: ").strip()
                if pick.isdigit() and 1 <= int(pick) <= len(p.career_state.promotion_offers):
                    print(self.engine.accept_promotion(p.career_state.promotion_offers[int(pick) - 1]))

    def show_party_overview(self) -> None:
        s = self.engine.state
        assert s is not None
        party = s.parties[s.actors[s.player.actor_id].party_id]
        print(f"{party.name} ({party.party_type.value})")
        print(f"Unity {party.party_unity} | Leader authority {party.leader_authority} | Public trust {party.public_trust}")
        print(f"Media pressure {party.media_pressure} | Election readiness {party.election_readiness} | Government credibility {party.government_credibility}")
        print("Custom variables:")
        for key, val in party.custom_variables.items():
            print(f"- {key}: {val}")

    def show_faction_overview(self) -> None:
        s = self.engine.state
        assert s is not None
        party_id = s.actors[s.player.actor_id].party_id
        for faction in [f for f in s.factions.values() if f.party_id == party_id]:
            print(f"{faction.name} | strength {faction.strength} | agitation {faction.agitation} | leader loyalty {faction.loyalty_to_leader}")

    def show_constituency_overview(self) -> None:
        c = self.engine.player_constituency
        print(f"{c.name} | flashpoint: {c.current_flashpoint}")
        print(f"Unionist {c.unionist_strength} | Nationalist {c.nationalist_strength} | Cross-community {c.cross_community_strength}")
        print(f"Working class pressure {c.working_class_pressure} | Middle class pressure {c.middle_class_pressure}")
        print(f"Rural pressure {c.rural_pressure} | Urban pressure {c.urban_pressure}")
        print(f"Local issue pressure {c.local_issue_pressure} | Turnout energy {c.turnout_energy} | Local media heat {c.local_media_heat}")

    def show_relationships(self) -> None:
        s = self.engine.state
        assert s is not None
        for rel in s.relationships.values():
            print(f"{rel.label}: {rel.score}")

    def show_event_log(self) -> None:
        s = self.engine.state
        assert s is not None
        for item in s.event_log[-20:]:
            print(f"- {item}")
