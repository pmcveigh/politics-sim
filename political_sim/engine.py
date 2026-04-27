from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List, Optional

from .data import build_actors, build_constituencies, build_factions, build_institutions, build_moments, build_parties, build_relationships
from .models import CareerState, Decision, Moment, Player, Role, SimulationState, TimeSlot

SLOT_ORDER = [TimeSlot.MORNING, TimeSlot.AFTERNOON, TimeSlot.EVENING, TimeSlot.LATE_NIGHT]


class SimulationEngine:
    def __init__(self) -> None:
        self.moment_catalog = {m.id: m for m in build_moments()}
        self.state: Optional[SimulationState] = None
        self.pending_chain: List[str] = []

    def create_simulation(self, player_name: str = "Alex Mercer", party_id: str = "cap", role: Role = Role.COUNCILLOR, constituency_id: str = "north_down") -> SimulationState:
        parties = build_parties()
        actors = build_actors()
        factions = build_factions()
        constituencies = build_constituencies()
        institutions = build_institutions()

        player = Player(
            actor_id="player",
            name=player_name,
            role=role,
            party_id=party_id,
            constituency_id=constituency_id,
            stamina=88,
            influence=26,
            reputation=52,
            local_base=50,
            party_trust=52,
            leader_trust=50,
            media_profile=35,
            career_momentum=5,
        )
        actors[player.actor_id] = actors.get("cap_councillor")
        actors[player.actor_id].id = "player"
        actors[player.actor_id].name = player_name
        actors[player.actor_id].party_id = party_id
        actors[player.actor_id].role = role
        actors[player.actor_id].constituency_id = constituency_id

        self.state = SimulationState(
            current_date=date(2027, 5, 1),
            time_slot=TimeSlot.MORNING,
            parties=parties,
            factions=factions,
            actors=actors,
            player=player,
            constituencies=constituencies,
            institutions=institutions,
            relationships=build_relationships("player", party_id),
            career=CareerState(current_role=role),
            active_moments=[],
            event_log=["Simulation started. You are one actor in a moving system."],
        )
        self.pending_chain = [
            "local_planning_row",
            "council_rebellion",
            "local_media_interview",
            "candidate_selection_opening",
            "faction_dinner",
            "rival_handles_issue",
            "assembly_campaign_launch",
            "debate_night",
            "election_result",
            "first_assembly_vote",
            "party_crisis_briefing",
        ]
        self.generate_agenda()
        return self.state

    def generate_agenda(self) -> List[Moment]:
        assert self.state
        agenda: List[Moment] = []
        if self.pending_chain:
            agenda.append(self._clone(self.pending_chain[0]))
        if len(self.pending_chain) > 1:
            agenda.append(self._clone(self.pending_chain[1]))
        if self._eligible_for_junior_minister() and "junior_minister_offer" not in [m.id for m in agenda]:
            agenda.append(self._clone("junior_minister_offer"))
        self.state.active_moments = agenda
        return agenda

    def _clone(self, moment_id: str) -> Moment:
        base = self.moment_catalog[moment_id]
        return Moment(**{k: v for k, v in base.__dict__.items()})

    def available_decisions(self, moment: Moment) -> List[Decision]:
        return [d for d in moment.decision_options if self.state and self.state.player.role in d.allowed_roles]

    def apply_decision(self, moment_id: str, decision_id: str) -> str:
        assert self.state
        moment = self._get_moment(moment_id)
        options = {d.id: d for d in self.available_decisions(moment)}
        if decision_id not in options:
            return "You do not have authority for that action at your current rank."
        decision = options[decision_id]

        self._apply_effect_map(decision.effects)
        self._apply_relationship_map(decision.relationship_effects)
        self._apply_career(decision.career_effects)
        self._advance_time(decision.time_advance)
        self._post_moment_progression(moment.id, decision.id)

        result = self._build_result(moment, decision)
        self.state.current_result = result
        self.state.event_log.append(result)
        self.generate_agenda()
        return result

    def ignore_moment(self, moment_id: str) -> str:
        assert self.state
        moment = self._get_moment(moment_id)
        self._apply_effect_map(moment.ignored_effects)
        self._apply_relationship_map(moment.ignored_relationship_effects)
        self._advance_time(1)
        self._post_moment_progression(moment.id, "ignored")
        result = f"Ignored: {moment.title}\nImmediate consequence: {moment.ignored_text}\nSystem reaction: {moment.system_reaction}\nTime advanced to {self.state.time_slot.value}."
        self.state.current_result = result
        self.state.event_log.append(result)
        self.generate_agenda()
        return result

    def _post_moment_progression(self, moment_id: str, decision_id: str) -> None:
        assert self.state
        if moment_id in self.pending_chain:
            self.pending_chain.remove(moment_id)

        if moment_id == "candidate_selection_opening" and self._eligible_for_candidate_selection():
            self.state.player.role = Role.CANDIDATE
            self.state.career.current_role = Role.CANDIDATE
            self.state.career.candidate_selected = True
            self.state.career.recent_events.append("Selected as Assembly candidate.")

        if moment_id == "election_result" and decision_id != "ignored":
            if self.state.player.reputation >= 55 or self.state.player.career_momentum >= 7:
                self.state.player.role = Role.MLA
                self.state.career.current_role = Role.MLA
                self.state.career.became_mla = True
                self.state.career.recent_events.append("Won Assembly seat and became MLA.")
            else:
                self.state.career.recent_events.append("Narrow loss; moved into party support role.")

        if moment_id == "party_crisis_briefing" and decision_id in {"crisis_defend", "crisis_brief"}:
            self.state.career.survived_party_crisis = True

        if moment_id == "junior_minister_offer" and decision_id == "offer_accept":
            self.state.player.role = Role.JUNIOR_MINISTER
            self.state.career.current_role = Role.JUNIOR_MINISTER
            self.state.career.recent_events.append("Appointed junior minister.")

    def _eligible_for_candidate_selection(self) -> bool:
        assert self.state
        return all(
            [
                self.state.player.reputation >= 55,
                self.state.player.local_base >= 50,
                self.state.relationships["local_branch"].score >= 50,
                self.state.player.career_momentum >= 5,
            ]
        )

    def _eligible_for_junior_minister(self) -> bool:
        assert self.state
        party = self.state.parties[self.state.player.party_id]
        return all(
            [
                self.state.player.role == Role.MLA,
                self.state.player.leader_trust >= 55,
                self.state.player.party_trust >= 55,
                self.state.player.reputation >= 60,
                self.state.career.survived_party_crisis,
                party.government_credibility >= 40,
            ]
        )

    def _apply_effect_map(self, effects: Dict[str, int]) -> None:
        assert self.state
        for key, delta in effects.items():
            if key.startswith("player."):
                attr = key.split(".", 1)[1]
                if hasattr(self.state.player, attr):
                    setattr(self.state.player, attr, max(0, min(100, getattr(self.state.player, attr) + delta)))
            elif key.startswith("party."):
                attr = key.split(".", 1)[1]
                party = self.state.parties[self.state.player.party_id]
                if attr in party.custom_variables:
                    party.custom_variables[attr] = max(0, min(100, party.custom_variables[attr] + delta))
                elif hasattr(party, attr):
                    setattr(party, attr, max(0, min(100, getattr(party, attr) + delta)))
            elif key.startswith("constituency."):
                attr = key.split(".", 1)[1]
                c = self.state.constituencies[self.state.player.constituency_id]
                if hasattr(c, attr):
                    setattr(c, attr, max(0, min(100, getattr(c, attr) + delta)))
            elif key.startswith("rival."):
                rival = self.state.actors[f"{self.state.player.party_id}_rival"]
                attr = key.split(".", 1)[1]
                if hasattr(rival, attr):
                    setattr(rival, attr, max(0, min(100, getattr(rival, attr) + delta)))

    def _apply_relationship_map(self, rel: Dict[str, int]) -> None:
        assert self.state
        for k, v in rel.items():
            if k in self.state.relationships:
                self.state.relationships[k].score = max(0, min(100, self.state.relationships[k].score + v))

    def _apply_career(self, career: Dict[str, int]) -> None:
        assert self.state
        self.state.player.career_momentum = max(0, min(100, self.state.player.career_momentum + career.get("career_momentum", 0)))

    def _get_moment(self, moment_id: str) -> Moment:
        assert self.state
        for m in self.state.active_moments:
            if m.id == moment_id:
                return m
        raise ValueError("Moment not in agenda")

    def _advance_time(self, steps: int) -> None:
        assert self.state
        idx = SLOT_ORDER.index(self.state.time_slot)
        for _ in range(steps):
            idx += 1
            if idx >= len(SLOT_ORDER):
                idx = 0
                self.state.current_date = self.state.current_date + timedelta(days=1)
        self.state.time_slot = SLOT_ORDER[idx]

    def _build_result(self, moment: Moment, decision: Decision) -> str:
        assert self.state
        return (
            f"Decision taken: {decision.label}\n"
            f"Immediate consequence: {decision.result_text}\n"
            f"Party changes: {decision.effects}\n"
            f"Relationship changes: {decision.relationship_effects}\n"
            f"Career changes: {decision.career_effects}\n"
            f"System reaction: {moment.system_reaction}\n"
            f"Time advanced to: {self.state.time_slot.value}"
        )
