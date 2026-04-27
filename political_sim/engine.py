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
    RoutineCategory,
    RoutineItem,
    SimulationState,
    StoryArc,
    StoryStatus,
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
        arcs = self._build_story_arcs(constituency_id)
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
            event_log=["You begin as a councillor. The desk opens with casework, routine duties, and active local stories."],
            active_story_arcs=arcs,
            recent_consequence="New term opened: school parking and bins are already crowding your desk.",
        )
        self._inject_story_moments_for_day()
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
        self.state.player.influence = max(0, self.state.player.influence - decision.influence_cost)
        item.status = ItemStatus.HANDLED

        story_text = self._apply_story_decision_effects(item, decision.id)
        reaction = self._reaction_for(item)
        headline = f"Handled: {item.title}"
        result = (
            f"{headline}\n"
            f"Narrative: {decision.result_text}\n"
            f"Key changes: stamina -{decision.stamina_cost}, influence -{decision.influence_cost}.\n"
            f"System reaction: {reaction}\n"
            f"Story progression: {story_text}\n"
            f"Next suggested action: Check the next agenda panel before advancing time."
        )
        self.state.current_result = result
        self.state.recent_consequence = headline
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
        story_txt = self._on_story_ignored(item)
        txt = f"Ignored: {item.title}\nSystem reaction: {item.escalation}\nStory progression: {story_txt}"
        self.state.current_result = txt
        self.state.recent_consequence = f"Ignored: {item.title}"
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
        self._inject_story_moments_for_day()
        self._progress_arc_resolution()
        self.state.event_log.append(f"New day: {agenda.day_name}. Inbox, routine, active stories and complications updated.")
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
                if item.story_arc_id:
                    arc = self._arc(item.story_arc_id)
                    arc.rival_ownership = min(100, arc.rival_ownership + 8)
                    arc.player_ownership = max(0, arc.player_ownership - 5)
                    arc.memory["rival_intervened"] = True
            else:
                item.status = ItemStatus.EXPIRED
                self.state.event_log.append(f"Unresolved item worsened: {item.title}.")
            self.state.moments.append(Moment(f"late_{item.id}", "Late fallout", item.escalation, MomentCategory.REACTION, item.id))

    def _apply_story_decision_effects(self, item: RoutineItem, decision_id: str) -> str:
        assert self.state
        if not item.story_arc_id:
            return "Routine item handled with no active story arc shift."
        arc = self._arc(item.story_arc_id)
        if "public" in decision_id or "campaign" in decision_id:
            arc.public_visibility = min(100, arc.public_visibility + 9)
            arc.player_ownership = min(100, arc.player_ownership + 6)
            arc.rival_ownership = min(100, arc.rival_ownership + 3)
            arc.pressure_level = min(100, arc.pressure_level + 7)
            arc.memory["player_public"] = True
            arc.memory["party_worried"] = True
        elif "visit" in decision_id or "attend" in decision_id:
            arc.player_ownership = min(100, arc.player_ownership + 7)
            arc.pressure_level = min(100, arc.pressure_level + 4)
            arc.memory["residents_listened"] = True
        elif "forward" in decision_id or "polite" in decision_id or "dry" in decision_id:
            arc.public_visibility = max(0, arc.public_visibility - 3)
            arc.pressure_level = max(0, arc.pressure_level - 2)
            arc.player_ownership = min(100, arc.player_ownership + 3)
            arc.memory["player_quiet"] = True
        else:
            arc.pressure_level = min(100, arc.pressure_level + 2)
        arc.memory["officers_helpful"] = self.state.player.officer_relationship >= 50
        arc.memory["media_covered"] = self.state.constituencies[self.state.player.constituency_id].local_media_heat >= 50

        if arc.current_stage < 3:
            arc.current_stage += 1
            return f"{arc.title} advanced to stage {arc.current_stage}."
        return f"{arc.title} is awaiting resolution fallout."

    def _on_story_ignored(self, item: RoutineItem) -> str:
        if not item.story_arc_id:
            return "No linked story arc."
        arc = self._arc(item.story_arc_id)
        arc.pressure_level = min(100, arc.pressure_level + 10)
        arc.rival_ownership = min(100, arc.rival_ownership + 10)
        arc.player_ownership = max(0, arc.player_ownership - 5)
        arc.memory["rival_intervened"] = True
        arc.memory["residents_listened"] = False
        if arc.current_stage < 3:
            arc.current_stage += 1
            return f"{arc.title} escalated to stage {arc.current_stage} and rival ownership increased."
        return f"{arc.title} worsened and moved toward fallout."

    def _progress_arc_resolution(self) -> None:
        assert self.state
        for arc in self.state.active_story_arcs:
            if arc.current_stage < 3 or arc.status != StoryStatus.ACTIVE:
                continue
            if arc.player_ownership >= arc.rival_ownership and arc.pressure_level <= 65:
                arc.status = StoryStatus.RESOLVED
                arc.outcome_tags.append("local_credit")
                self.state.player.local_base = min(100, self.state.player.local_base + 2)
                self.state.player.career_momentum = min(100, self.state.player.career_momentum + 1)
            else:
                arc.status = StoryStatus.FALLOUT
                arc.outcome_tags.append("rival_credit")
                self.state.player.rival_threat = min(100, self.state.player.rival_threat + 2)

    def _inject_story_moments_for_day(self) -> None:
        assert self.state
        stage_slot = {1: TimeSlot.MORNING, 2: TimeSlot.AFTERNOON, 3: TimeSlot.EVENING}
        for arc in self.state.active_story_arcs:
            if arc.status != StoryStatus.ACTIVE:
                continue
            slot = stage_slot.get(arc.current_stage, TimeSlot.LATE_NIGHT)
            item = RoutineItem(
                id=f"story_{arc.id}_{self.state.day_index}_{slot.name.lower()}",
                title=f"{arc.title}: stage {arc.current_stage}",
                description=arc.next_possible_moments[(arc.current_stage - 1) % len(arc.next_possible_moments)],
                category=RoutineCategory.CASEWORK if arc.current_stage == 1 else RoutineCategory.LOCAL_MEDIA,
                time_slot=slot,
                urgency=Urgency.HIGH if arc.pressure_level >= 60 else Urgency.MEDIUM,
                workload_cost=1,
                stamina_cost=5,
                influence_cost=1,
                expires_after_slots=1,
                involved_actor_ids=arc.involved_actor_ids,
                involved_relationships=arc.involved_relationships,
                linked_constituency_id=arc.linked_constituency_id,
                possible_decisions=self._story_decisions_for_arc(arc),
                ignored_effect={"player.rival_threat": 2, "player.resident_trust": -1},
                escalation=f"{arc.title} drifts without your intervention.",
                slots_remaining=1,
                story_arc_id=arc.id,
            )
            self.state.routine_items.append(item)
            self.state.daily_agenda.items_by_slot.setdefault(slot, []).append(item.id)

    def _story_decisions_for_arc(self, arc: StoryArc):
        from .data import _d
        from .models import HandlingStyle

        return [
            _d(
                f"visit_{arc.id}",
                "Visit the site personally",
                HandlingStyle.PERSONAL_WARD_WORK,
                {"player.resident_trust": 3, "player.ward_visibility": 2},
                {"residents_association": 1},
                7,
                False,
                "You meet residents and gather details for follow-up.",
            ),
            _d(
                f"forward_{arc.id}",
                "Forward quietly to officers",
                HandlingStyle.QUIET_ADMIN,
                {"player.officer_relationship": 1, "player.casework_backlog": -1},
                {"council_officers": 1},
                3,
                True,
                "You send a tidy brief and request formal action.",
            ),
            _d(
                f"public_{arc.id}",
                "Post publicly and demand action",
                HandlingStyle.PUBLIC_CAMPAIGNING,
                {"player.local_media_profile": 2, "player.social_media_volatility": 2},
                {"council_officers": -1, "main_rival": -1},
                4,
                True,
                "The issue becomes visible quickly and responses polarise.",
            ),
        ]

    def _build_story_arcs(self, constituency_id: str) -> List[StoryArc]:
        return [
            StoryArc("school_parking_chaos", "School parking chaos", "school parking", StoryStatus.ACTIVE, 1, constituency_id, ["main_rival", "council_officer"], ["residents_association", "council_officers"], 58, 47, 40, 38, ["Parents report dangerous parking at school gates.", "Roads officer proposes weak temporary signage.", "Residents group requests evening accountability meeting."], []),
            StoryArc("planning_objection_row", "Planning objection row", "planning dispute", StoryStatus.ACTIVE, 1, constituency_id, ["main_rival"], ["community_group", "party_group"], 54, 42, 35, 36, ["Neighbours object to a late planning variation.", "Rival accuses you of sitting on the file.", "Committee asks for a public explanation."], []),
            StoryArc("missed_bins_backlash", "Missed bins backlash", "bins and missed collections", StoryStatus.ACTIVE, 1, constituency_id, ["council_officer"], ["residents_association", "council_officers"], 61, 45, 44, 34, ["Residents share photos of uncollected bins.", "Service manager sends a defensive update.", "Local press asks why the ward is still waiting."], []),
            StoryArc("town_centre_decline", "Town centre decline", "town centre decline", StoryStatus.ACTIVE, 1, constituency_id, ["main_rival", "journalist"], ["business_group", "local_journalist"], 56, 55, 39, 41, ["Shop owners warn footfall is collapsing.", "Rival announces a photo-op walkabout.", "Business group demands a concrete recovery motion."], []),
        ]

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

    def _arc(self, arc_id: str) -> StoryArc:
        assert self.state
        for arc in self.state.active_story_arcs:
            if arc.id == arc_id:
                return arc
        raise ValueError("Unknown arc")
