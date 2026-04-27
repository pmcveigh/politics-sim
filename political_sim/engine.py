from __future__ import annotations

import random
from typing import Dict, List, Optional

from .data_moments import create_moment_from_template, build_moment_templates
from .data_parties import build_actors, build_constituencies, build_factions, build_institutions, build_parties
from .models import (
    Actor,
    CareerState,
    Decision,
    Moment,
    Player,
    Relationship,
    Role,
    SimulationState,
    TimeSlot,
    Urgency,
)

SLOT_ORDER = [TimeSlot.MORNING, TimeSlot.AFTERNOON, TimeSlot.EVENING, TimeSlot.LATE_NIGHT]
ROLE_POWER = {
    Role.ACTIVIST: 8,
    Role.COUNCILLOR: 20,
    Role.CANDIDATE: 18,
    Role.MLA: 35,
    Role.ADVISER: 30,
    Role.JUNIOR_MINISTER: 45,
    Role.MINISTER: 58,
}


class SimulationEngine:
    def __init__(self, seed: Optional[int] = None) -> None:
        self.random = random.Random(seed)
        self.templates = build_moment_templates()
        self.state: Optional[SimulationState] = None

    def create_simulation(self, player_name: str, party_id: str, role: Role, constituency_name: str) -> SimulationState:
        parties = build_parties()
        factions = build_factions()
        actors = build_actors()
        constituencies = build_constituencies()
        institutions = build_institutions()

        player_actor_id = "player_actor"
        actors[player_actor_id] = Actor(
            id=player_actor_id,
            name=player_name,
            role=role,
            party_id=party_id,
            constituency_id=constituencies[constituency_name].id,
            faction_id=self._pick_player_faction_id(party_id, factions),
            reputation=50,
            competence=52,
            ambition=60,
            loyalty_to_party=52,
            loyalty_to_leader=48,
            faction_loyalty=50,
            media_skill=48,
            local_machine_strength=50,
            ideological_intensity=54,
            scandal_risk=35,
            stamina=90,
            career_momentum=40,
            influence=0,
        )
        actor = actors[player_actor_id]
        career = CareerState(current_role=role)
        player = Player(
            actor_id=player_actor_id,
            current_role=role,
            stamina=90,
            local_base=45,
            party_trust=48,
            leader_trust=45,
            faction_support=48,
            media_profile=24,
            career_momentum=40,
            allies=[],
            enemies=[],
            career_state=career,
            available_actions=[],
        )
        relationships = self._initial_relationships(player_actor_id, party_id, factions)

        self.state = SimulationState(
            day=1,
            month=5,
            year=2027,
            slot=TimeSlot.MORNING,
            parties=parties,
            factions=factions,
            actors=actors,
            player=player,
            constituencies=constituencies,
            institutions=institutions,
            relationships=relationships,
            active_moments=[],
            event_log=[],
        )
        self._recalculate_actor_influence()
        self._update_player_available_actions()
        self.generate_daily_agenda()
        self.state.event_log.append("Simulation started on 1 May 2027.")
        return self.state

    def _pick_player_faction_id(self, party_id: str, factions: Dict[str, object]) -> str:
        options = [f.id for f in factions.values() if f.party_id == party_id]
        return options[0]

    def _initial_relationships(self, player_actor_id: str, party_id: str, factions: Dict[str, object]) -> Dict[str, Relationship]:
        rels: Dict[str, Relationship] = {
            "leader": Relationship(player_actor_id, f"leader_{party_id}", 50, "Party leader"),
            "local_branch": Relationship(player_actor_id, f"branch_{party_id}", 52, "Local branch"),
            "media": Relationship(player_actor_id, "journalist_pool", 45, "Media contacts"),
        }
        for faction in [f for f in factions.values() if f.party_id == party_id]:
            rels[f"faction:{faction.id}"] = Relationship(player_actor_id, faction.id, 47, faction.name)
        return rels

    def _recalculate_actor_influence(self) -> None:
        assert self.state is not None
        for actor in self.state.actors.values():
            relation_bonus = 0
            if actor.id == self.state.player.actor_id:
                relation_bonus = sum(r.score for r in self.state.relationships.values()) // max(1, len(self.state.relationships))
            actor.influence = max(
                0,
                min(
                    100,
                    ROLE_POWER[actor.role]
                    + actor.reputation // 5
                    + actor.career_momentum // 4
                    + actor.faction_loyalty // 6
                    + relation_bonus // 8,
                ),
            )

    def _update_player_available_actions(self) -> None:
        assert self.state is not None
        role = self.state.player.current_role
        base = {
            Role.ACTIVIST: ["canvass", "build branch influence", "attend local meetings", "spread gossip", "support candidates", "leak local information"],
            Role.COUNCILLOR: ["handle local issues", "influence local media", "court branches", "fight council votes", "support selection"],
            Role.CANDIDATE: ["campaign", "raise profile", "court branches", "attack opponents", "manage scandals"],
            Role.MLA: ["vote", "rebel", "ask questions", "join committees", "lobby ministers", "court media"],
            Role.ADVISER: ["shape messaging", "brief journalists", "prepare leaders", "leak", "protect actors", "damage actors"],
            Role.JUNIOR_MINISTER: ["handle narrow policy", "manage small crises", "work with civil service", "defend department"],
            Role.MINISTER: ["handle major crises", "set departmental priorities", "manage media", "fight executive disputes"],
        }
        self.state.player.available_actions = base[role]

    def generate_daily_agenda(self) -> List[Moment]:
        assert self.state is not None
        party = self.state.parties[self.state.actors[self.state.player.actor_id].party_id]
        constituency = self.player_constituency
        pressure = party.media_pressure + party.faction_pressure + constituency.local_issue_pressure // 2
        base_count = 1 if pressure < 120 else 2
        if pressure > 155 or self.state.player.stamina > 82:
            base_count = 3

        slots = SLOT_ORDER[:]
        party_templates = [t for t in self.templates if t["party_type"] == party.party_type]
        selected = self.random.sample(party_templates, k=base_count)
        self.state.active_moments = [
            create_moment_from_template(
                tmpl,
                day=self.state.day,
                slot=slots[i],
                slot_index=i,
                party_id=party.id,
                constituency_name=constituency.name,
                faction_name=self.state.factions[self.state.actors[self.state.player.actor_id].faction_id].name,
            )
            for i, tmpl in enumerate(selected)
        ]
        return self.state.active_moments

    @property
    def player_constituency(self):
        assert self.state is not None
        actor = self.state.actors[self.state.player.actor_id]
        return next(c for c in self.state.constituencies.values() if c.id == actor.constituency_id)

    def get_moment_by_id(self, moment_id: str) -> Moment:
        assert self.state is not None
        for moment in self.state.active_moments:
            if moment.id == moment_id:
                return moment
        raise ValueError("Moment not found.")

    def available_decisions(self, moment: Moment) -> List[Decision]:
        role = self.state.player.current_role  # type: ignore[union-attr]
        return [d for d in moment.decision_options if role in d.required_roles]

    def role_authority_message(self) -> str:
        return "You do not have the authority to do this. You can lobby, leak, support or oppose, but you cannot command party strategy from your current role."

    def apply_decision(self, moment_id: str, decision_id: str) -> str:
        assert self.state is not None
        moment = self.get_moment_by_id(moment_id)
        options = {d.id: d for d in self.available_decisions(moment)}
        if decision_id not in options:
            return self.role_authority_message()
        decision = options[decision_id]
        if self.state.player.stamina < decision.stamina_cost:
            return "You are too exhausted for that move. Consider a lighter response or defer the moment."

        self._apply_effects(decision)
        self.state.player.stamina = max(0, self.state.player.stamina - decision.stamina_cost)
        self._consume_moment(moment.id)
        reaction = self._generate_system_reaction(moment, handled=True)
        self._advance_time(decision.time_advance)
        self._check_career_opportunity()
        self._recalculate_actor_influence()

        change_lines = self._describe_effects(decision)
        result = (
            f"Decision: {decision.label}\n"
            f"Immediate result: {decision.consequence_text}\n"
            f"Likely risk: {decision.risk_level}/100\n"
            f"Changes:\n{change_lines}\n"
            f"System reaction:\n- {reaction}\n"
            f"Time advances to {self.state.slot.value}."
        )
        self.state.event_log.append(result)
        return result

    def _apply_effects(self, decision: Decision) -> None:
        assert self.state is not None
        for key, delta in decision.effects.items():
            self._apply_effect_key(key, delta)
        for key, delta in decision.relationship_effects.items():
            if key.startswith("faction:"):
                faction_id = key.split(":", 1)[1]
                rel_key = f"faction:{faction_id}"
                if rel_key in self.state.relationships:
                    self.state.relationships[rel_key].score = max(0, min(100, self.state.relationships[rel_key].score + delta))
        for key, delta in decision.career_effects.items():
            if hasattr(self.state.player.career_state, key):
                old = getattr(self.state.player.career_state, key)
                if isinstance(old, int):
                    setattr(self.state.player.career_state, key, max(0, min(100, old + delta)))

    def _apply_effect_key(self, key: str, delta: int) -> None:
        assert self.state is not None
        party = self.state.parties[self.state.actors[self.state.player.actor_id].party_id]
        constituency = self.player_constituency
        player = self.state.player
        actor = self.state.actors[player.actor_id]

        if key.startswith("party.custom."):
            ckey = key.replace("party.custom.", "")
            if ckey in party.custom_variables:
                party.custom_variables[ckey] = max(0, min(100, party.custom_variables[ckey] + delta))
            return
        if key.startswith("party."):
            attr = key.replace("party.", "")
            if hasattr(party, attr):
                setattr(party, attr, max(0, min(100, getattr(party, attr) + delta)))
            return
        if key.startswith("player."):
            attr = key.replace("player.", "")
            if hasattr(player, attr):
                setattr(player, attr, max(0, min(100, getattr(player, attr) + delta)))
            elif hasattr(actor, attr):
                setattr(actor, attr, max(0, min(100, getattr(actor, attr) + delta)))
            return
        if key.startswith("constituency."):
            attr = key.replace("constituency.", "")
            if hasattr(constituency, attr):
                setattr(constituency, attr, max(0, min(100, getattr(constituency, attr) + delta)))
            return

    def _describe_effects(self, decision: Decision) -> str:
        lines = [f"- Player stamina -{decision.stamina_cost}"]
        for key, delta in decision.effects.items():
            lines.append(f"- {key} {delta:+d}")
        for key, delta in decision.relationship_effects.items():
            lines.append(f"- relationship {key} {delta:+d}")
        for key, delta in decision.career_effects.items():
            lines.append(f"- career {key} {delta:+d}")
        return "\n".join(lines)

    def _consume_moment(self, moment_id: str) -> None:
        assert self.state is not None
        self.state.active_moments = [m for m in self.state.active_moments if m.id != moment_id]

    def ignore_moment(self, moment_id: str, defer: bool = False) -> str:
        assert self.state is not None
        moment = self.get_moment_by_id(moment_id)
        if defer:
            self._advance_time(1)
            self.state.event_log.append(f"Deferred moment: {moment.title}.")
            return f"Deferred: {moment.title}. It may worsen before you return to it."

        self._consume_moment(moment.id)
        self.state.player.party_trust = max(0, self.state.player.party_trust - (3 if moment.urgency in [Urgency.HIGH, Urgency.CRITICAL] else 1))
        reaction = self._generate_system_reaction(moment, handled=False)
        self.state.event_log.append(f"Ignored: {moment.title}. {moment.ignored_effect} {reaction}")
        return f"Ignored: {moment.title}. {moment.ignored_effect}\nSystem reaction: {reaction}"

    def _generate_system_reaction(self, moment: Moment, handled: bool) -> str:
        assert self.state is not None
        pool = [
            "A senior adviser notes your loyalty.",
            "A rival handles the issue instead and gains local reputation.",
            "The faction chair is pleased and may support you later.",
            "The local paper runs the story without your quote.",
            "The party whip sends a warning.",
            "Civil service officials quietly adjust their briefing line.",
            "An opposing party spokesperson uses the row to attack your side.",
        ]
        reaction = self.random.choice(pool)
        if not handled:
            self.state.player.career_momentum = max(0, self.state.player.career_momentum - 1)
            self.player_constituency.local_media_heat = min(100, self.player_constituency.local_media_heat + 1)
        else:
            self.state.player.career_momentum = min(100, self.state.player.career_momentum + 1)
        return reaction

    def _advance_time(self, slots: int) -> None:
        assert self.state is not None
        for _ in range(slots):
            idx = SLOT_ORDER.index(self.state.slot)
            if idx < len(SLOT_ORDER) - 1:
                self.state.slot = SLOT_ORDER[idx + 1]
                self.resolve_unhandled_moments()
            else:
                self.end_day()
                self.start_next_day()

    def resolve_unhandled_moments(self) -> None:
        assert self.state is not None
        current_idx = SLOT_ORDER.index(self.state.slot)
        remaining: List[Moment] = []
        for moment in self.state.active_moments:
            age = current_idx - moment.created_slot_index
            if age >= moment.expires_after_slots:
                if moment.can_escalate and self.random.random() < 0.4:
                    self.state.event_log.append(f"Escalation: {moment.title} becomes tomorrow's crisis.")
                    self.state.player.leader_trust = max(0, self.state.player.leader_trust - 2)
                else:
                    self.state.event_log.append(f"System handled: {moment.title}. {moment.ignored_effect}")
                    self.state.player.party_trust = max(0, self.state.player.party_trust - 1)
            else:
                remaining.append(moment)
        self.state.active_moments = remaining

    def end_day(self) -> None:
        assert self.state is not None
        self.resolve_unhandled_moments()
        self.state.event_log.append(f"Day {self.state.day} ended.")

    def start_next_day(self) -> None:
        assert self.state is not None
        self.state.day += 1
        self.state.slot = TimeSlot.MORNING
        self.state.player.stamina = min(100, self.state.player.stamina + 30)
        self.generate_daily_agenda()
        self.state.event_log.append(f"Day {self.state.day} started.")

    def advance_time(self) -> str:
        self._advance_time(1)
        assert self.state is not None
        return f"Time advanced to {self.state.date_label()}."

    def _check_career_opportunity(self) -> None:
        assert self.state is not None
        p = self.state.player
        offers = p.career_state.promotion_offers
        if p.career_momentum >= 60 and Role.CANDIDATE not in offers and p.current_role == Role.ACTIVIST:
            offers.append(Role.CANDIDATE)
            self.state.event_log.append("Career opportunity: candidate selection track is open.")
        if p.career_momentum >= 68 and Role.MLA not in offers and p.current_role in [Role.COUNCILLOR, Role.CANDIDATE]:
            offers.append(Role.MLA)
            self.state.event_log.append("Career opportunity: committee and MLA track is open.")
        if p.career_momentum >= 75 and Role.JUNIOR_MINISTER not in offers and p.current_role == Role.MLA:
            offers.append(Role.JUNIOR_MINISTER)
            self.state.event_log.append("Career opportunity: junior ministry is being discussed.")
        if p.career_momentum >= 82 and Role.MINISTER not in offers and p.current_role == Role.JUNIOR_MINISTER:
            offers.append(Role.MINISTER)
            self.state.event_log.append("Career opportunity: ministerial role may be available.")

    def accept_promotion(self, role: Role) -> str:
        assert self.state is not None
        if role not in self.state.player.career_state.promotion_offers:
            return "No such promotion offer is available."
        old_role = self.state.player.current_role
        self.state.player.current_role = role
        self.state.player.career_state.previous_roles.append(old_role)
        self.state.player.career_state.current_role = role
        self.state.player.career_state.promotion_offers.remove(role)
        self._update_player_available_actions()
        self._recalculate_actor_influence()
        return f"You accept the opportunity and move from {old_role.value} to {role.value}."
