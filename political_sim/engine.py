from __future__ import annotations

import random
from typing import Dict, List, Optional

from .data_moments import build_moment_templates, create_moment_from_template
from .data_parties import create_actors, create_constituencies, create_institutions, create_parties
from .models import (
    CareerState,
    DailyAgenda,
    GameDate,
    PlayerState,
    PoliticalMoment,
    Relationship,
    Role,
    SimulationState,
    TimeSlot,
    Urgency,
)

SLOT_ORDER = [TimeSlot.MORNING, TimeSlot.AFTERNOON, TimeSlot.EVENING, TimeSlot.LATE_NIGHT]


class MomentGenerator:
    def __init__(self, rng: random.Random) -> None:
        self.rng = rng
        self.templates = build_moment_templates()

    def generate(self, state: SimulationState) -> List[PoliticalMoment]:
        role = state.player.career.current_role
        party = state.parties[state.player.party_id]
        pressure = party.variables.get("media_pressure", 50) + party.variables.get("faction_pressure", 50)
        count = 1 if pressure < 90 else 2
        if pressure > 120 or state.player.stamina > 85:
            count = 3

        eligible = [t for t in self.templates if role in t["eligible_roles"]]
        if not eligible:
            eligible = self.templates

        self.rng.shuffle(eligible)
        slots = SLOT_ORDER[:]
        moments: List[PoliticalMoment] = []
        for i in range(min(count, len(eligible))):
            slot = slots[i]
            moments.append(
                create_moment_from_template(
                    eligible[i],
                    party_id=state.player.party_id,
                    constituency=state.player.constituency,
                    slot=slot,
                    day_index=state.day_index,
                )
            )
        return moments


class SimulationEngine:
    def __init__(self, seed: Optional[int] = None) -> None:
        self.random = random.Random(seed)
        self.generator = MomentGenerator(self.random)
        self.state: Optional[SimulationState] = None

    def create_simulation(self, player_name: str, party_id: str, role: Role, constituency: str, faction: str) -> SimulationState:
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
                "local_org": Relationship("local_org", 50),
            },
        )
        self.state = SimulationState(
            day_index=1,
            game_date=GameDate(day=1, month=5, year=2027, time_slot=TimeSlot.MORNING),
            parties=create_parties(),
            actors=create_actors(),
            constituencies=create_constituencies(),
            institutions=create_institutions(),
            player=player,
            daily_agenda=DailyAgenda(day_index=1),
        )
        self.state.event_log.append("Simulation started. Date: 01/05/2027 (Morning).")
        self.start_day()
        return self.state

    def start_day(self) -> None:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        self.state.player.stamina = min(100, self.state.player.stamina + 30)
        self.generate_daily_agenda()
        self.state.event_log.append(f"Day {self.state.day_index} started: {len(self.state.daily_agenda.moments)} moments on agenda.")

    def generate_daily_agenda(self) -> DailyAgenda:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        moments = self.generator.generate(self.state)
        self.state.daily_agenda = DailyAgenda(day_index=self.state.day_index, moments=moments)
        return self.state.daily_agenda

    def show_current_agenda(self) -> List[PoliticalMoment]:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        return [m for m in self.state.daily_agenda.moments if m.time_slot == self.state.game_date.time_slot]

    def choose_moment(self, moment_id: str) -> PoliticalMoment:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        for m in self.state.daily_agenda.moments:
            if m.id == moment_id:
                return m
        raise ValueError("Moment not found on agenda.")

    def get_available_options(self, moment: PoliticalMoment) -> List:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        role = self.state.player.career.current_role
        return [opt for opt in moment.decision_options if role in opt.required_roles]

    def apply_decision(self, moment_id: str, option_id: str) -> str:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        moment = self.choose_moment(moment_id)
        option_map = {o.id: o for o in self.get_available_options(moment)}
        if option_id not in option_map:
            raise ValueError("Option unavailable for role.")

        option = option_map[option_id]
        player = self.state.player
        party = self.state.parties[player.party_id]

        changes: List[str] = []
        for attr, delta in option.effects_player.items():
            if hasattr(player, attr):
                old = getattr(player, attr)
                setattr(player, attr, max(0, min(100, old + delta)))
                changes.append(f"Player {attr} {delta:+d}")

        for var, delta in option.effects_party.items():
            if var in party.variables:
                party.variables[var] = max(0, min(100, party.variables[var] + delta))
                changes.append(f"Party {var} {delta:+d}")

        for rel_name, delta in option.effects_relationships.items():
            if rel_name in player.relationships:
                player.relationships[rel_name].score = max(0, min(100, player.relationships[rel_name].score + delta))
                changes.append(f"Relationship {rel_name} {delta:+d}")

        player.stamina = max(0, player.stamina - option.stamina_cost)
        self.state.daily_agenda.moments = [m for m in self.state.daily_agenda.moments if m.id != moment_id]
        time_msg = self.advance_time_slot(option.advances_slots)

        result = (
            f"Decision: {option.text}\n"
            f"Immediate result: {option.consequence_text}\n"
            f"Changes:\n- "
            + "\n- ".join(changes + [f"Player stamina -{option.stamina_cost}"])
            + f"\nTime advances to {self.state.game_date.time_slot.value}.\n{time_msg}"
        )
        self.state.event_log.append(result)
        return result

    def ignore_moment(self, moment_id: str) -> str:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        moment = self.choose_moment(moment_id)
        self.state.daily_agenda.moments = [m for m in self.state.daily_agenda.moments if m.id != moment_id]
        self.state.player.party_trust = max(0, self.state.player.party_trust - (3 if moment.urgency in [Urgency.HIGH, Urgency.CRITICAL] else 1))
        msg = f"Ignored: {moment.title}. {moment.ignored_effect}"
        self.state.event_log.append(msg)
        return msg

    def advance_time_slot(self, slots: int = 1) -> str:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        for _ in range(slots):
            idx = SLOT_ORDER.index(self.state.game_date.time_slot)
            if idx == len(SLOT_ORDER) - 1:
                self.end_day()
                self.start_next_day()
                return "Day ended and next day started."
            self.state.game_date.time_slot = SLOT_ORDER[idx + 1]
            self.apply_system_actions_for_unhandled_moments()
        return ""

    def end_day(self) -> None:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        self.apply_system_actions_for_unhandled_moments(end_of_day=True)
        self.state.event_log.append(f"Day {self.state.day_index} ended.")

    def start_next_day(self) -> None:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        self.state.day_index += 1
        self.state.game_date.day += 1
        self.state.game_date.time_slot = TimeSlot.MORNING
        self.start_day()

    def apply_system_actions_for_unhandled_moments(self, end_of_day: bool = False) -> None:
        if self.state is None:
            raise RuntimeError("Simulation has not started.")
        remaining: List[PoliticalMoment] = []
        current_slot_idx = SLOT_ORDER.index(self.state.game_date.time_slot)
        for moment in self.state.daily_agenda.moments:
            moment_slot_idx = SLOT_ORDER.index(moment.time_slot)
            age_slots = (current_slot_idx - moment_slot_idx) if self.state.day_index == moment.created_day_index else 4
            if end_of_day or age_slots >= moment.expires_after_slots:
                if moment.can_escalate and self.random.random() < 0.4:
                    self.state.player.leader_trust = max(0, self.state.player.leader_trust - 4)
                    self.state.event_log.append(f"Escalation: {moment.title} worsened overnight.")
                else:
                    self.state.player.reputation = max(0, self.state.player.reputation - 2)
                    self.state.event_log.append(f"System handled: {moment.title}. {moment.handled_by_system_effect}")
            else:
                remaining.append(moment)
        self.state.daily_agenda.moments = remaining
