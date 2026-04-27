from political_sim.engine import SimulationEngine
from political_sim.models import ItemStatus, Role, RoutineCategory


def test_daily_agenda_has_structure():
    engine = SimulationEngine()
    state = engine.create_simulation()
    assert state.daily_agenda.routine_obligation_id
    assert state.daily_agenda.opportunity_id
    assert state.daily_agenda.complication_id


def test_agenda_includes_obligation_opportunity_complication():
    engine = SimulationEngine()
    state = engine.create_simulation()
    ids = {state.daily_agenda.routine_obligation_id, state.daily_agenda.opportunity_id, state.daily_agenda.complication_id}
    assert len(ids) == 3


def test_role_limited_decisions_are_filtered():
    engine = SimulationEngine()
    state = engine.create_simulation(role=Role.COUNCILLOR)
    item = engine.items_for_current_slot()[0]
    assert all(state.player.role in d.allowed_roles for d in engine.available_decisions(item))


def test_casework_backlog_changes_after_decision():
    engine = SimulationEngine()
    state = engine.create_simulation()
    item = engine.items_for_current_slot()[0]
    before = state.player.casework_backlog
    decision = next(d for d in engine.available_decisions(item) if "backlog" in str(d.effects))
    engine.apply_decision(item.id, decision.id)
    assert state.player.casework_backlog != before


def test_ignored_item_can_benefit_rival():
    engine = SimulationEngine()
    state = engine.create_simulation()
    item = engine.items_for_current_slot()[0]
    before = state.player.rival_threat
    engine.ignore_item(item.id)
    assert state.player.rival_threat > before


def test_officer_relationship_affects_outcome():
    engine = SimulationEngine()
    state = engine.create_simulation()
    state.player.officer_relationship = 60
    # find officer follow-up day
    found = None
    for _ in range(8):
        for item in engine.items_for_current_slot():
            if item.category == RoutineCategory.OFFICER_FOLLOW_UP:
                found = item
                break
        if found:
            break
        engine.advance_time()
    assert found is not None
    decision = engine.available_decisions(found)[0]
    result = engine.apply_decision(found.id, decision.id)
    assert "officer replies quickly" in result


def test_social_media_choice_affects_volatility():
    engine = SimulationEngine()
    state = engine.create_simulation()
    item = engine.items_for_current_slot()[0]
    before = state.player.social_media_volatility
    decision = next((d for d in engine.available_decisions(item) if d.handling_style.value == "Public Campaigning"), None)
    if decision:
        engine.apply_decision(item.id, decision.id)
        assert state.player.social_media_volatility != before


def test_career_selection_opportunity_appears_after_thresholds():
    engine = SimulationEngine()
    state = engine.create_simulation()
    state.player.reputation = 56
    state.player.local_base = 55
    state.player.branch_support = 55
    state.player.career_momentum = 5
    state.player.rival_threat = 40
    engine._inject_career_opportunity_if_ready()
    assert any("Assembly selection opening" == i.title for i in state.routine_items)


def test_variables_change_only_from_decisions_or_ignored_items():
    engine = SimulationEngine()
    state = engine.create_simulation()
    before = state.player.reputation
    engine.advance_time()
    assert state.player.reputation == before
    item = engine.items_for_current_slot()[0]
    engine.ignore_item(item.id)
    assert any(i.status in {ItemStatus.EXPIRED, ItemStatus.HANDLED, ItemStatus.TAKEN_BY_OTHERS} for i in state.routine_items)
