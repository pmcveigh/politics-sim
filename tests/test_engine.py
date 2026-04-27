from political_sim.engine import SimulationEngine
from political_sim.models import Role


def test_simulation_initialises():
    engine = SimulationEngine()
    state = engine.create_simulation()
    assert state.player.role == Role.COUNCILLOR
    assert state.player.party_id == "cap"


def test_agenda_generates_moments():
    engine = SimulationEngine()
    state = engine.create_simulation()
    assert len(state.active_moments) >= 1


def test_applying_decision_changes_variables():
    engine = SimulationEngine()
    state = engine.create_simulation()
    moment = state.active_moments[0]
    decision = engine.available_decisions(moment)[0]
    before = state.player.reputation
    engine.apply_decision(moment.id, decision.id)
    assert state.player.reputation != before or state.player.career_momentum >= 5


def test_ignoring_moment_triggers_consequences():
    engine = SimulationEngine()
    state = engine.create_simulation()
    moment = state.active_moments[0]
    before = state.actors[f"{state.player.party_id}_rival"].reputation
    result = engine.ignore_moment(moment.id)
    after = state.actors[f"{state.player.party_id}_rival"].reputation
    assert "System reaction" in result
    assert after >= before


def test_candidate_selection_eligibility():
    engine = SimulationEngine()
    state = engine.create_simulation()
    state.player.reputation = 56
    state.player.local_base = 52
    state.player.career_momentum = 7
    state.relationships["local_branch"].score = 55
    assert engine._eligible_for_candidate_selection()


def test_junior_minister_eligibility():
    engine = SimulationEngine()
    state = engine.create_simulation()
    state.player.role = Role.MLA
    state.player.reputation = 62
    state.player.party_trust = 57
    state.player.leader_trust = 58
    state.career.survived_party_crisis = True
    state.parties[state.player.party_id].government_credibility = 50
    assert engine._eligible_for_junior_minister()


def test_role_limited_decisions_filtered():
    engine = SimulationEngine()
    state = engine.create_simulation()
    for m in state.active_moments:
        for d in engine.available_decisions(m):
            assert state.player.role in d.allowed_roles


def test_system_reaction_can_benefit_rival():
    engine = SimulationEngine()
    state = engine.create_simulation()
    target = [m for m in state.active_moments if m.id == "local_planning_row"][0]
    before = state.actors[f"{state.player.party_id}_rival"].reputation
    engine.ignore_moment(target.id)
    after = state.actors[f"{state.player.party_id}_rival"].reputation
    assert after > before
