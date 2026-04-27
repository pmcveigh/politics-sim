from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List, Optional

from .data import build_actors, build_constituencies, build_factions, build_institutions, build_parties, build_relationships
from .models import (
    CareerState,
    ItemStatus,
    Moment,
    MomentCategory,
    Player,
    Role,
    RoutineItem,
    SimulationState,
    TimeSlot,
    Urgency,
)
from .routine import build_daily_routine

SLOT_ORDER = [TimeSlot.MORNING, TimeSlot.AFTERNOON, TimeSlot.EVENING, TimeSlot.LATE_NIGHT]


class SimulationEngine:
    def __init__(self) -> None:
        self.state: Optional[SimulationState] = None

    def create_simulation(self, player_name: str = "Alex Mercer", party_id: str = "cap", role: Role = Role.COUNCILLOR, constituency_id: str = "north_down") -> SimulationState:
        player = Player(
            actor_id="player",
            name=player_name,
            role=role,
            party_id=party_id,
            constituency_id=constituency_id,
            reputation=50,
            influence=25,
            stamina=80,
            casework_backlog=6,
            resident_trust=52,
            local_media_profile=35,
            branch_support=52,
            party_group_trust=50,
            officer_relationship=47,
            rival_threat=40,
            social_media_volatility=32,
            ward_visibility=45,
            committee_credibility=44,
            local_issue_pressure=50,
            career_momentum=3,
            local_base=50,
        )
        agenda, items = build_daily_routine(date(2026, 4, 27), 0, constituency_id)
        self.state = SimulationState(
            current_date=date(2026, 4, 27),
            time_slot=TimeSlot.MORNING,
            day_index=0,
            parties=build_parties(),
            factions=build_factions(),
            actors=build_actors(),
            player=player,
            constituencies=build_constituencies(),
            institutions=build_institutions(),
            relationships=build_relationships(),
            career=CareerState(current_role=role),
            routine_items=items,
            moments=[],
            daily_agenda=agenda,
            event_log=["You begin as a councillor. The day starts with inbox triage and agenda review."],
        )
        self._inject_career_opportunity_if_ready()
        return self.state

    def items_for_current_slot(self) -> List[RoutineItem]:
        assert self.state
        return [i for i in self.state.routine_items if i.time_slot == self.state.time_slot and i.status == ItemStatus.OPEN]

    def available_decisions(self, item: RoutineItem):
        assert self.state
        return [d for d in item.possible_decisions if self.state.player.role in d.allowed_roles]

    def apply_decision(self, item_id: str, decision_id: str) -> str:
        assert self.state
        item = self._get_item(item_id)
        if item.status != ItemStatus.OPEN:
            return "Item is no longer actionable."
        decision = next((d for d in self.available_decisions(item) if d.id == decision_id), None)
        if not decision:
            return "Decision unavailable for current role."
        if decision.is_minor:
            if self.state.minor_actions_used >= 1 or self.state.player.stamina < 12:
                return "Minor action unavailable (already used or stamina too low)."
            self.state.minor_actions_used += 1
        else:
            if self.state.main_actions_used >= 1:
                return "Main action already used this time slot."
            self.state.main_actions_used += 1

        self._apply_effects(decision.effects)
        self._apply_relationships(decision.relationship_effects)
        self.state.player.stamina = max(0, self.state.player.stamina - decision.stamina_cost)
        item.status = ItemStatus.HANDLED

        reaction = self._reaction_for(item)
        result = (
            f"Decision taken: {decision.label}\n"
            f"Immediate result: {decision.result_text}\n"
            f"System reaction: {reaction}\n"
            f"Next time slot: {self.state.time_slot.value}"
        )
        self.state.current_result = result
        self.state.event_log.append(result)
        self._inject_career_opportunity_if_ready()
        return result

    def ignore_item(self, item_id: str) -> str:
        assert self.state
        item = self._get_item(item_id)
        if item.status != ItemStatus.OPEN:
            return "Item is already resolved."
        self._apply_effects(item.ignored_effect)
        item.status = ItemStatus.EXPIRED
        self.state.moments.append(Moment(f"esc_{item.id}", "Issue escalated", item.escalation, MomentCategory.ESCALATION, item.id))
        txt = f"Ignored: {item.title}\nSystem reaction: {item.escalation}"
        self.state.current_result = txt
        self.state.event_log.append(txt)
        return txt

    def advance_time(self) -> None:
        assert self.state
        self._progress_unresolved_items()
        idx = SLOT_ORDER.index(self.state.time_slot) + 1
        if idx >= len(SLOT_ORDER):
            self.state.current_date = self.state.current_date + timedelta(days=1)
            self.state.day_index += 1
            self.state.time_slot = TimeSlot.MORNING
            self.state.main_actions_used = 0
            self.state.minor_actions_used = 0
            self._start_new_day()
            return
        self.state.time_slot = SLOT_ORDER[idx]
        self.state.main_actions_used = 0
        self.state.minor_actions_used = 0

    def _start_new_day(self) -> None:
        assert self.state
        agenda, items = build_daily_routine(self.state.current_date, self.state.day_index, self.state.player.constituency_id)
        self.state.daily_agenda = agenda
        self.state.routine_items.extend(items)
        self.state.event_log.append(f"New day: {agenda.day_name}. Inbox, routine and complications updated.")
        if self.state.current_date.weekday() == 6:
            self.state.player.stamina = min(100, self.state.player.stamina + 10)

    def _progress_unresolved_items(self) -> None:
        assert self.state
        for item in [i for i in self.state.routine_items if i.status == ItemStatus.OPEN]:
            item.slots_remaining -= 1
            if item.slots_remaining > 0:
                continue
            self._apply_effects(item.ignored_effect)
            if self.state.player.rival_threat >= 45:
                item.status = ItemStatus.TAKEN_BY_OTHERS
                self.state.event_log.append(f"Rival intervened on: {item.title}.")
            else:
                item.status = ItemStatus.EXPIRED
                self.state.event_log.append(f"Unresolved item worsened: {item.title}.")
            self.state.moments.append(Moment(f"late_{item.id}", "Late fallout", item.escalation, MomentCategory.REACTION, item.id))

    def _apply_effects(self, effects: Dict[str, int]) -> None:
        assert self.state
        for key, value in effects.items():
            scope, attr = key.split(".", 1)
            if scope == "player" and hasattr(self.state.player, attr):
                cur = getattr(self.state.player, attr)
                setattr(self.state.player, attr, max(0, min(100, cur + value)))
            if scope == "constituency":
                c = self.state.constituencies[self.state.player.constituency_id]
                if hasattr(c, attr):
                    cur = getattr(c, attr)
                    setattr(c, attr, max(0, min(100, cur + value)))

    def _apply_relationships(self, rel_effects: Dict[str, int]) -> None:
        assert self.state
        for rid, delta in rel_effects.items():
            if rid in self.state.relationships:
                r = self.state.relationships[rid]
                r.score = max(0, min(100, r.score + delta))

    def _reaction_for(self, item: RoutineItem) -> str:
        assert self.state
        if item.category.value == "Officer Follow-Up" and self.state.player.officer_relationship >= 50:
            return "The council officer replies quickly because your relationship is good."
        if item.category.value == "Local Media" and self.state.relationships["local_journalist"].score >= 50:
            return "The local journalist frames your answer fairly."
        if self.state.player.stamina < 25:
            return "Low stamina blunts your follow-through and leaves room for rivals."
        return "The issue is not fully solved, but people can see you are working it."

    def _eligible_for_selection(self) -> bool:
        assert self.state
        p = self.state.player
        return all([
            p.reputation >= 55,
            p.local_base >= 50,
            p.branch_support >= 50,
            p.career_momentum >= 5,
            p.rival_threat <= 65,
        ])

    def _inject_career_opportunity_if_ready(self) -> None:
        assert self.state
        if self.state.career.assembly_selection_open or not self._eligible_for_selection():
            return
        self.state.career.assembly_selection_open = True
        selection = RoutineItem(
            id=f"career_selection_{self.state.day_index}",
            title="Assembly selection opening",
            description="A shortlist opens. Your local routine record now matters.",
            category=self._career_category(),
            time_slot=TimeSlot.EVENING,
            urgency=Urgency.HIGH,
            workload_cost=1,
            stamina_cost=5,
            influence_cost=2,
            expires_after_slots=2,
            involved_actor_ids=["main_rival"],
            involved_relationships=["local_branch", "key_faction"],
            linked_constituency_id=self.state.player.constituency_id,
            possible_decisions=[],
            ignored_effect={"player.career_momentum": -1, "player.rival_threat": 2},
            escalation="Branch figures say you hesitated and your rival looks hungrier.",
            slots_remaining=2,
        )
        self.state.routine_items.append(selection)
        self.state.daily_agenda.items_by_slot[TimeSlot.EVENING].append(selection.id)
        self.state.event_log.append("Career opportunity unlocked: Assembly selection opening.")

    def _career_category(self):
        from .models import RoutineCategory

        return RoutineCategory.CAREER_POSITIONING

    def _get_item(self, item_id: str) -> RoutineItem:
        assert self.state
        for item in self.state.routine_items:
            if item.id == item_id:
                return item
        raise ValueError("Unknown routine item")
