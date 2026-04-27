from __future__ import annotations

import random
from typing import Dict, List, Optional

from .data_moments import create_moments
from .data_parties import create_actors, create_constituencies, create_institutions, create_parties
from .models import CareerState, PlayerState, PoliticalMoment, Relationship, Role, SimulationState, TimeMode


ROLE_ACTION_BUDGET: Dict[Role, int] = {
    Role.ACTIVIST: 1,
    Role.COUNCILLOR: 2,
    Role.CANDIDATE: 2,
    Role.MLA: 3,
    Role.ADVISER: 3,
    Role.JUNIOR_MINISTER: 3,
    Role.MINISTER: 4,
}


class SimulationEngine:
    def __init__(self, seed: Optional[int] = None) -> None:
        self.random = random.Random(seed)
        self.moments = create_moments()
        self.state: Optional[SimulationState] = None

    def create_simulation(
        self,
        player_name: str,
        party_id: str,
        role: Role,
        constituency: str,
        faction: str,
    ) -> SimulationState:
        player = PlayerState(
            name=player_name,
            party_id=party_id,
            constituency=constituency,
            faction=faction,
            career=CareerState(current_role=role),
            relationships={
                "leader": Relationship("leader", 50),
                "media": Relationship("media", 45),
                "hardliners": Relationship("hardliners", 48),
                "moderates": Relationship("moderates", 48),
                "faction_rival": Relationship("faction_rival", 45),
            },
        )
        self.state = SimulationState(
            current_day=1,
            parties=create_parties(),
            actors=create_actors(),
            constituencies=create_constituencies(),
            institutions=create_institutions(),
            player=player,
        )
        self.state.event_log.append("Simulation started. Politics moves with or without you.")
        return self.state

    def _time_jump(self, mode: TimeMode) -> int:
        if mode == TimeMode.QUIET:
            return self.random.randint(21, 120)
        if mode == TimeMode.CRISIS:
            return self.random.randint(1, 4)
        if mode == TimeMode.CAMPAIGN:
            return self.random.randint(3, 10)
        return self.random.randint(7, 21)

    def draw_moment(self) -> PoliticalMoment:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        party_id = self.state.player.party_id
        eligible = [
            m
            for m in self.moments
            if m.target_party_id == party_id and self.state.player.career.current_role in m.eligible_roles
        ]
        if not eligible:
            raise RuntimeError("No eligible moments available.")
        moment = self.random.choice(eligible)
        self.state.current_moment = moment
        self.state.current_day += self._time_jump(moment.time_mode)
        self.state.event_log.append(f"Day {self.state.current_day}: {moment.title} ({moment.time_mode.value})")
        return moment

    def get_available_options(self, moment: PoliticalMoment) -> List:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        role = self.state.player.career.current_role
        return [opt for opt in moment.decision_options if role in opt.required_roles]

    def apply_decision(self, option_id: str) -> str:
        if self.state is None or self.state.current_moment is None:
            raise RuntimeError("No active moment.")
        moment = self.state.current_moment
        options = {o.id: o for o in self.get_available_options(moment)}
        if option_id not in options:
            raise ValueError("That option is not available for your current role.")

        option = options[option_id]
        player = self.state.player
        party = self.state.parties[player.party_id]

        if ROLE_ACTION_BUDGET[player.career.current_role] <= 1 and "major" in option.text.lower():
            raise ValueError("Your rank cannot execute major strategic commands.")

        for attr, delta in option.effects_player.items():
            old = getattr(player, attr)
            setattr(player, attr, max(0, min(100, old + delta)))

        for var, delta in option.effects_party.items():
            if var in party.variables:
                party.variables[var] = max(0, min(100, party.variables[var] + delta))

        for rel_name, delta in option.effects_relationships.items():
            if rel_name in player.relationships:
                player.relationships[rel_name].score = max(0, min(100, player.relationships[rel_name].score + delta))

        self._update_career_opportunities()
        result = (
            f"{option.consequence_text}\n"
            f"System response: {moment.consequence_text}\n"
            f"Relationship effects: {moment.relationship_effects}\n"
            f"Career effects: {moment.career_effects}"
        )
        if option.delayed_effect_note:
            result += f"\nDelayed effect hint: {option.delayed_effect_note}"

        self.state.event_log.append(f"Decision in {moment.id}: {option.text}")
        self.state.event_log.append(result)
        self.state.current_moment = None
        return result

    def _update_career_opportunities(self) -> None:
        if self.state is None:
            return
        player = self.state.player
        possible = []
        if player.reputation >= 55 and player.local_base >= 45:
            possible.append(Role.CANDIDATE)
        if player.influence >= 45 and player.party_trust >= 45:
            possible.append(Role.ADVISER)
        if player.reputation >= 60 and player.influence >= 55 and player.party_trust >= 50:
            possible.append(Role.JUNIOR_MINISTER)
        if player.reputation >= 70 and player.influence >= 65 and player.leader_trust >= 55:
            possible.append(Role.MINISTER)
        player.career.opportunities = [r for r in possible if r != player.career.current_role and r not in player.career.declined_roles]

    def accept_opportunity(self, role: Role) -> str:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        player = self.state.player
        if role not in player.career.opportunities:
            raise ValueError("Role not currently available.")
        player.career.current_role = role
        player.career.opportunities = []
        self.state.event_log.append(f"Career move: accepted role {role.value}")
        return f"You accepted promotion to {role.value}."

    def decline_opportunity(self, role: Role) -> str:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        player = self.state.player
        if role in player.career.opportunities and role not in player.career.declined_roles:
            player.career.declined_roles.append(role)
            player.career.opportunities.remove(role)
            self.state.event_log.append(f"Career move: declined role {role.value}")
        return f"You declined {role.value}."
