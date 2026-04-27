from political_sim.engine import SimulationEngine
from political_sim.models import BeatStatus, TimeSlot


def _first_story_beat(engine: SimulationEngine):
    return next(b for b in engine.state.daily_beats.values() if b.linked_story_arc_id and b.status == BeatStatus.OPEN)


def test_day_template_generates_plausible_day():
    engine = SimulationEngine()
    state = engine.create_simulation()
    assert state.daily_agenda.template_id in {"admin", "crisis", "campaign", "council", "community"}
    assert all(slot in state.daily_agenda.beats_by_slot for slot in [TimeSlot.MORNING, TimeSlot.AFTERNOON, TimeSlot.EVENING, TimeSlot.LATE_NIGHT])


def test_beats_appear_in_time_slots():
    engine = SimulationEngine()
    state = engine.create_simulation()
    assert state.daily_agenda.beats_by_slot[TimeSlot.MORNING]
    assert engine.beats_for_slot(TimeSlot.MORNING)


def test_decision_sets_story_flags():
    engine = SimulationEngine()
    state = engine.create_simulation()
    beat = _first_story_beat(engine)
    option = beat.decision_options[0]
    while engine.state.current_slot != beat.time_slot:
        engine.advance_time()
    engine.choose_beat(beat.id, option.id)
    arc = state.active_story_arcs[beat.linked_story_arc_id]
    assert any(arc.flags.get(flag) for flag in option.flags_set)


def test_decision_schedules_followup():
    engine = SimulationEngine()
    state = engine.create_simulation()
    beat = _first_story_beat(engine)
    option = next(o for o in beat.decision_options if o.next_beats)
    while engine.state.current_slot != beat.time_slot:
        engine.advance_time()
    engine.choose_beat(beat.id, option.id)
    assert state.followups


def test_ignored_beat_can_trigger_rival_action():
    engine = SimulationEngine()
    state = engine.create_simulation()
    beat = _first_story_beat(engine)
    while engine.state.current_slot != beat.time_slot:
        engine.advance_time()
    engine.ignore_beat(beat.id)
    arc = state.active_story_arcs[beat.linked_story_arc_id]
    assert arc.flags.get("rival_intervened") is True


def test_actor_reaction_modifies_relationship():
    engine = SimulationEngine()
    state = engine.create_simulation()
    beat = next(b for b in engine.state.daily_beats.values() if b.linked_story_arc_id and any(o.possible_actor_reactions for o in b.decision_options))
    option = next(o for o in beat.decision_options if o.possible_actor_reactions)
    reaction_id = option.possible_actor_reactions[0]
    before = state.relationships[reaction_id].score
    while engine.state.current_slot != beat.time_slot:
        engine.advance_time()
    engine.choose_beat(beat.id, option.id)
    after = state.relationships[reaction_id].score
    assert after != before


def test_dashboard_data_model_has_todays_flow():
    engine = SimulationEngine()
    state = engine.create_simulation()
    assert state.daily_agenda.beats_by_slot
    assert sum(len(v) for v in state.daily_agenda.beats_by_slot.values()) > 0


def test_story_arc_advances_after_decision():
    engine = SimulationEngine()
    state = engine.create_simulation()
    beat = _first_story_beat(engine)
    arc = state.active_story_arcs[beat.linked_story_arc_id]
    before = arc.current_stage
    while engine.state.current_slot != beat.time_slot:
        engine.advance_time()
    engine.choose_beat(beat.id, beat.decision_options[0].id)
    assert arc.current_stage > before


def test_no_passive_weekly_drift_exists():
    engine = SimulationEngine()
    state = engine.create_simulation()
    before = (state.player.reputation, state.player.local_base)
    for _ in range(8):
        engine.advance_time()
    after = (state.player.reputation, state.player.local_base)
    assert before == after


def test_career_eligibility_reachable_via_story_and_routine_success():
    engine = SimulationEngine()
    state = engine.create_simulation()
    state.player.reputation = 56
    state.player.local_base = 52
    state.player.branch_support = 52
    state.player.career_momentum = 5
    state.player.rival_threat = 40
    beat = _first_story_beat(engine)
    while engine.state.current_slot != beat.time_slot:
        engine.advance_time()
    engine.choose_beat(beat.id, beat.decision_options[0].id)
    assert state.career.assembly_selection_open is True


def test_ignored_slot_items_get_closed_when_advancing():
    engine = SimulationEngine()
    state = engine.create_simulation()
    open_ids = list(state.daily_agenda.beats_by_slot[state.current_slot])
    engine.advance_time()
    assert all(state.daily_beats[i].status in {BeatStatus.IGNORED, BeatStatus.TAKEN_BY_RIVAL, BeatStatus.RESOLVED} for i in open_ids)
