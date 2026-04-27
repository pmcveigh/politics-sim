from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from .data import (
    beat_type_from_id,
    build_actors,
    build_constituency,
    build_content_packs,
    build_day_templates,
    build_factions,
    build_institutions,
    build_party,
    build_relationships,
    decision_library,
)
from .models import (
    ActorReaction,
    BeatStatus,
    CareerState,
    DailyAgenda,
    DailyBeat,
    FollowUp,
    GameDate,
    Player,
    Role,
    SimulationState,
    StoryArc,
    StoryStatus,
    TimeSlot,
)

SLOTS = [TimeSlot.MORNING, TimeSlot.AFTERNOON, TimeSlot.EVENING, TimeSlot.LATE_NIGHT]
TEMPLATE_ROTATION = ["admin", "crisis", "campaign", "council", "community"]


class SimulationEngine:
    def __init__(self) -> None:
        self.state: Optional[SimulationState] = None

    def create_simulation(self) -> SimulationState:
        player = Player(id="player", name="Alex Mercer", party_id="civic", constituency_id="harbour")
        stories = self._initial_story_arcs(player.constituency_id)
        self.state = SimulationState(
            game_date=GameDate(date(2026, 4, 27)),
            current_slot=TimeSlot.MORNING,
            day_index=0,
            player=player,
            party=build_party(),
            factions=build_factions(),
            constituency=build_constituency(),
            institutions=build_institutions(),
            actors=build_actors(),
            relationships=build_relationships(),
            active_story_arcs=stories,
            content_packs=build_content_packs(),
            day_templates=build_day_templates(),
            career=CareerState(current_role=Role.COUNCILLOR),
            daily_agenda=DailyAgenda(date(2026, 4, 27), "admin", {}),
            daily_beats={},
            event_log=["You begin as a councillor with casework, party pressure and local stories already in motion."],
            recent_consequence="Day opened: inbox and routine loaded.",
        )
        self._build_day()
        return self.state

    def beats_for_slot(self, slot: Optional[TimeSlot] = None) -> List[DailyBeat]:
        assert self.state
        slot = slot or self.state.current_slot
        ids = self.state.daily_agenda.beats_by_slot.get(slot, [])
        return [self.state.daily_beats[i] for i in ids if self.state.daily_beats[i].status == BeatStatus.OPEN]

    def choose_beat(self, beat_id: str, option_id: str) -> str:
        assert self.state
        beat = self.state.daily_beats[beat_id]
        if beat.status != BeatStatus.OPEN or beat.time_slot != self.state.current_slot or self.state.main_action_taken:
            return "That beat is not available right now."
        option = next((o for o in beat.decision_options if o.id == option_id), None)
        if not option:
            return "Decision option not available."

        self.state.main_action_taken = True
        self._apply_effects(option.effects)
        self.state.player.stamina = max(0, min(100, self.state.player.stamina - option.stamina_cost))
        self.state.player.influence = max(0, min(100, self.state.player.influence - option.influence_cost))
        beat.status = BeatStatus.RESOLVED
        reaction = self._actor_reaction(beat, option)
        story_text = self._progress_story(beat, option.flags_set)
        follow = self._schedule_followup(beat, option.next_beats)
        self._check_career_eligibility()

        result = (
            f"Headline: {beat.title}\n"
            f"Narrative: {option.consequence_text}\n"
            f"Key changes: Stamina -{option.stamina_cost}, Influence -{option.influence_cost}.\n"
            f"Actor reaction: {reaction.text}\n"
            f"Story progression: {story_text}\n"
            f"Scheduled follow-up: {follow if follow else 'No immediate follow-up scheduled.'}\n"
            f"Next suggested action: Review remaining beats in this time slot."
        )
        self.state.current_result = result
        self.state.recent_consequence = f"{beat.title}: {option.label}"
        self.state.event_log.append(result)
        return result

    def ignore_beat(self, beat_id: str) -> str:
        assert self.state
        beat = self.state.daily_beats[beat_id]
        if beat.status != BeatStatus.OPEN:
            return "Beat already closed."
        beat.status = BeatStatus.IGNORED
        self._apply_effects(beat.ignored_effect)
        txt = self._system_independence_response(beat)
        self.state.current_result = txt
        self.state.recent_consequence = f"Ignored: {beat.title}"
        self.state.event_log.append(txt)
        return txt

    def advance_time(self) -> None:
        assert self.state
        self._expire_slot_beats()
        i = SLOTS.index(self.state.current_slot)
        if i == len(SLOTS) - 1:
            self.state.game_date = self.state.game_date.add_days(1)
            self.state.day_index += 1
            self.state.current_slot = TimeSlot.MORNING
            self.state.main_action_taken = False
            self._build_day()
            return
        self.state.current_slot = SLOTS[i + 1]
        self.state.main_action_taken = False

    def _build_day(self) -> None:
        assert self.state
        template_id = TEMPLATE_ROTATION[self.state.day_index % len(TEMPLATE_ROTATION)]
        template = self.state.day_templates[template_id]
        beats_by_slot: Dict[TimeSlot, List[str]] = {s: [] for s in SLOTS}
        self.state.daily_beats = {}

        for slot in SLOTS:
            for idx, beat_key in enumerate(template.slot_beats.get(slot, [])):
                beat = self._make_beat(beat_key, slot, idx)
                beats_by_slot[slot].append(beat.id)
                self.state.daily_beats[beat.id] = beat

        self._inject_story_beats(beats_by_slot)
        self._inject_due_followups(beats_by_slot)
        self.state.daily_agenda = DailyAgenda(self.state.game_date.value, template_id, beats_by_slot)

    def _make_beat(self, beat_key: str, slot: TimeSlot, idx: int) -> DailyBeat:
        assert self.state
        lib = decision_library()
        decisions = []
        story_id = None
        involved = []
        if beat_key == "phone_call":
            decisions = lib["car_phone_call"]
            story_id = "car_accident_hotspot"
            involved = ["officer", "journalist", "residents_contact", "rival"]
        elif beat_key == "resident_meeting" and self.state.day_index % 2 == 0:
            decisions = lib["noise_meeting"]
            story_id = "noise_complaint"
            involved = ["residents_contact", "officer", "rival"]
        elif beat_key == "party_strategy_meeting":
            decisions = lib["campaign_request"]
            story_id = "campaign_help_request"
            involved = ["party_figure", "rival"]
        else:
            decisions = [
                decision_library()["campaign_request"][1],
            ]

        return DailyBeat(
            id=f"{beat_key}_{self.state.day_index}_{slot.name.lower()}_{idx}",
            title=beat_key.replace("_", " ").title(),
            description="Routine councillor work with linked local pressure and competing demands.",
            time_slot=slot,
            beat_type=beat_type_from_id(beat_key),
            linked_story_arc_id=story_id,
            involved_actor_ids=involved,
            decision_options=decisions,
            ignored_effect={"player.rival_threat": 2, "player.resident_trust": -1},
            status=BeatStatus.OPEN,
            urgency="High" if story_id else "Medium",
            expiry=1,
            short_risk_preview="Ignoring this may allow rivals, media or officers to move first.",
        )

    def _inject_story_beats(self, beats_by_slot: Dict[TimeSlot, List[str]]) -> None:
        assert self.state
        for arc in self.state.active_story_arcs.values():
            if arc.status != StoryStatus.ACTIVE:
                continue
            slot = TimeSlot.AFTERNOON if arc.current_stage == 1 else TimeSlot.EVENING
            beat = DailyBeat(
                id=f"story_{arc.id}_{self.state.day_index}",
                title=f"{arc.title} - Stage {arc.current_stage}",
                description=f"{arc.theme} is active. Pressure {arc.pressure_level}, visibility {arc.public_visibility}.",
                time_slot=slot,
                beat_type=beat_type_from_id("officer_meeting" if arc.id != "campaign_help_request" else "campaign_session"),
                linked_story_arc_id=arc.id,
                involved_actor_ids=arc.involved_actor_ids,
                decision_options=self._story_decisions(arc.id),
                ignored_effect={"player.rival_threat": 3, "player.resident_trust": -2},
                status=BeatStatus.OPEN,
                urgency="High",
                expiry=1,
                short_risk_preview="Story ownership may drift to your rival.",
            )
            self.state.daily_beats[beat.id] = beat
            beats_by_slot[slot].append(beat.id)

    def _inject_due_followups(self, beats_by_slot: Dict[TimeSlot, List[str]]) -> None:
        assert self.state
        pending: List[FollowUp] = []
        for follow in self.state.followups:
            if follow.due_date == self.state.game_date.value:
                beat = self._make_beat(follow.beat_id, follow.time_slot, 99)
                beat.id = f"follow_{follow.id}"
                beat.linked_story_arc_id = follow.story_arc_id
                self.state.daily_beats[beat.id] = beat
                beats_by_slot[follow.time_slot].append(beat.id)
            else:
                pending.append(follow)
        self.state.followups = pending

    def _story_decisions(self, arc_id: str):
        lib = decision_library()
        if arc_id == "car_accident_hotspot":
            return lib["car_phone_call"]
        if arc_id == "noise_complaint":
            return lib["noise_meeting"]
        return lib["campaign_request"]

    def _progress_story(self, beat: DailyBeat, flags: List[str]) -> str:
        assert self.state
        if not beat.linked_story_arc_id:
            return "Routine progression only."
        arc = self.state.active_story_arcs[beat.linked_story_arc_id]
        for f in flags:
            arc.flags[f] = True
        arc.player_ownership = min(100, arc.player_ownership + 6)
        arc.rival_ownership = max(0, arc.rival_ownership - 2)
        arc.pressure_level = max(0, arc.pressure_level - 1)
        arc.public_visibility = min(100, arc.public_visibility + 2)
        arc.current_stage += 1
        if arc.current_stage >= 4:
            arc.status = StoryStatus.RESOLVED if arc.player_ownership >= arc.rival_ownership else StoryStatus.FALLOUT
            arc.outcome_tags.append("resolved" if arc.status == StoryStatus.RESOLVED else "rival_credit")
        return f"{arc.title} moved to stage {arc.current_stage} with updated memory flags."

    def _schedule_followup(self, beat: DailyBeat, next_beats: List[str]) -> Optional[str]:
        assert self.state
        if not beat.linked_story_arc_id or not next_beats:
            return None
        new = FollowUp(
            id=f"{beat.id}_f",
            story_arc_id=beat.linked_story_arc_id,
            due_date=self.state.game_date.add_days(1).value,
            time_slot=TimeSlot.AFTERNOON,
            beat_id=next_beats[0],
        )
        self.state.followups.append(new)
        self.state.active_story_arcs[beat.linked_story_arc_id].scheduled_followups.append(new)
        return f"{next_beats[0].replace('_', ' ').title()} tomorrow afternoon"

    def _system_independence_response(self, beat: DailyBeat) -> str:
        assert self.state
        txt = f"Ignored: {beat.title}. "
        if beat.linked_story_arc_id:
            arc = self.state.active_story_arcs[beat.linked_story_arc_id]
            arc.rival_ownership = min(100, arc.rival_ownership + 8)
            arc.player_ownership = max(0, arc.player_ownership - 4)
            arc.flags["rival_intervened"] = True
            txt += "Your rival attends first and gains ownership."
        else:
            txt += "Media and residents proceed without your input."
        return txt

    def _actor_reaction(self, beat: DailyBeat, option) -> ActorReaction:
        assert self.state
        actor_id = option.possible_actor_reactions[0] if option.possible_actor_reactions else "journalist"
        line = {
            "officer": "The roads officer is irritated that you went public before the collision history was checked.",
            "residents_contact": "The residents' contact thanks you for turning up without cameras.",
            "rival": "Your rival posts a photograph at the junction and claims residents need action, not speeches.",
            "journalist": "The local journalist asks whether you are promising powers the council does not have.",
            "party_figure": "The party organiser notes that you kept your evening available for campaigning.",
        }.get(actor_id, "Local actors note your decision and adjust their approach.")
        rel_key = actor_id if actor_id in self.state.relationships else "journalist"
        self.state.relationships[rel_key].score = max(0, min(100, self.state.relationships[rel_key].score + 1))
        return ActorReaction(actor_id=actor_id, text=line, relationship_effects={rel_key: 1})

    def _apply_effects(self, effects: Dict[str, int]) -> None:
        assert self.state
        for k, v in effects.items():
            scope, attr = k.split(".", 1)
            if scope == "player" and hasattr(self.state.player, attr):
                current = getattr(self.state.player, attr)
                setattr(self.state.player, attr, max(0, min(100, current + v)))
            if scope == "relationship" and attr in self.state.relationships:
                rel = self.state.relationships[attr]
                rel.score = max(0, min(100, rel.score + v))

    def _expire_slot_beats(self) -> None:
        assert self.state
        for beat in self.beats_for_slot(self.state.current_slot):
            if beat.status == BeatStatus.OPEN:
                beat.status = BeatStatus.TAKEN_BY_RIVAL if beat.linked_story_arc_id else BeatStatus.IGNORED
                self._apply_effects(beat.ignored_effect)

    def _check_career_eligibility(self) -> None:
        assert self.state
        p = self.state.player
        if self.state.career.assembly_selection_open:
            return
        eligible = all([
            p.reputation >= 55,
            p.local_base >= 50,
            p.branch_support >= 50,
            p.career_momentum >= 5,
            p.rival_threat <= 65,
        ])
        if eligible:
            self.state.career.assembly_selection_open = True
            self.state.event_log.append("Career beat unlocked: Assembly selection conversation can now appear.")

    def _initial_story_arcs(self, constituency_id: str) -> Dict[str, StoryArc]:
        return {
            "car_accident_hotspot": StoryArc(
                id="car_accident_hotspot",
                title="Car accident hotspot",
                theme="Repeated crashes at a dangerous junction",
                status=StoryStatus.ACTIVE,
                current_stage=1,
                linked_constituency_id=constituency_id,
                involved_actor_ids=["officer", "journalist", "residents_contact", "rival"],
                pressure_level=62,
                public_visibility=48,
                player_ownership=45,
                rival_ownership=38,
            ),
            "noise_complaint": StoryArc(
                id="noise_complaint",
                title="Noise complaint between resident and business",
                theme="Late-night music row on the high street",
                status=StoryStatus.ACTIVE,
                current_stage=1,
                linked_constituency_id=constituency_id,
                involved_actor_ids=["residents_contact", "officer", "rival"],
                pressure_level=55,
                public_visibility=37,
                player_ownership=42,
                rival_ownership=40,
            ),
            "campaign_help_request": StoryArc(
                id="campaign_help_request",
                title="Stormont campaign help request",
                theme="Party asks for evening canvassing help",
                status=StoryStatus.ACTIVE,
                current_stage=1,
                linked_constituency_id=constituency_id,
                involved_actor_ids=["party_figure", "rival", "residents_contact"],
                pressure_level=50,
                public_visibility=33,
                player_ownership=41,
                rival_ownership=39,
            ),
        }
