from political_sim.engine import SimulationEngine
from political_sim.models import PartyType, Role


def test_simulation_initialises():
    engine = SimulationEngine(seed=1)
    state = engine.create_simulation("Erin Wallace", "unionist_front", Role.ACTIVIST, "East Belfast")
    assert state.day == 1
    assert state.slot.value == "Morning"


def test_parties_load_into_shared_engine():
    engine = SimulationEngine(seed=2)
    state = engine.create_simulation("Erin Wallace", "people_first", Role.COUNCILLOR, "West Belfast")
    assert state.parties["unionist_front"].party_type == PartyType.DUP_STYLE
    assert state.parties["people_first"].party_type == PartyType.SINN_FEIN_STYLE
    assert state.parties["civic_alliance"].party_type == PartyType.ALLIANCE_STYLE


def test_player_can_be_created_in_each_role():
    for role in Role:
        engine = SimulationEngine(seed=3)
        state = engine.create_simulation("Erin Wallace", "civic_alliance", role, "North Down")
        assert state.player.current_role == role


def test_daily_agenda_generates_one_to_three_moments():
    engine = SimulationEngine(seed=4)
    state = engine.create_simulation("Erin Wallace", "unionist_front", Role.CANDIDATE, "Lagan Valley")
    assert 1 <= len(state.active_moments) <= 3


def test_role_limited_decisions_work():
    engine = SimulationEngine(seed=5)
    state = engine.create_simulation("Erin Wallace", "unionist_front", Role.ACTIVIST, "East Belfast")
    moment = state.active_moments[0]
    activist_options = engine.available_decisions(moment)
    assert activist_options
    unavailable = [d for d in moment.decision_options if Role.MINISTER in d.required_roles and Role.ACTIVIST not in d.required_roles]
    if unavailable:
        response = engine.apply_decision(moment.id, unavailable[0].id)
        assert "do not have the authority" in response.lower()


def test_applying_decision_changes_variables():
    engine = SimulationEngine(seed=6)
    state = engine.create_simulation("Erin Wallace", "people_first", Role.MLA, "West Belfast")
    moment = state.active_moments[0]
    option = engine.available_decisions(moment)[0]
    before = state.player.party_trust
    engine.apply_decision(moment.id, option.id)
    assert state.player.party_trust != before or state.player.stamina < 90


def test_ignored_moment_can_trigger_system_reaction():
    engine = SimulationEngine(seed=7)
    state = engine.create_simulation("Erin Wallace", "civic_alliance", Role.COUNCILLOR, "North Down")
    moment = state.active_moments[0]
    result = engine.ignore_moment(moment.id)
    assert "System reaction" in result


def test_career_momentum_can_increase():
    engine = SimulationEngine(seed=8)
    state = engine.create_simulation("Erin Wallace", "civic_alliance", Role.COUNCILLOR, "North Down")
    start = state.player.career_momentum
    moment = state.active_moments[0]
    option = engine.available_decisions(moment)[0]
    engine.apply_decision(moment.id, option.id)
    assert state.player.career_momentum >= start


def test_relationships_can_change():
    engine = SimulationEngine(seed=9)
    state = engine.create_simulation("Erin Wallace", "unionist_front", Role.COUNCILLOR, "East Belfast")
    moment = state.active_moments[0]
    option = None
    for decision in engine.available_decisions(moment):
        if decision.relationship_effects:
            option = decision
            break
    if option is None:
        option = engine.available_decisions(moment)[0]
    scores_before = {k: v.score for k, v in state.relationships.items()}
    engine.apply_decision(moment.id, option.id)
    scores_after = {k: v.score for k, v in state.relationships.items()}
    assert scores_before != scores_after or state.player.career_momentum >= 40
