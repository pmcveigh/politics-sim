from political_sim.engine import SimulationEngine
from political_sim.models import Role


def test_create_simulation():
    e = SimulationEngine(seed=1)
    state = e.create_simulation("Casey", "unionist_front", Role.ACTIVIST, "East Belfast", "Local network")
    assert state.player.name == "Casey"
    assert state.player.career.current_role == Role.ACTIVIST


def test_draw_valid_moment():
    e = SimulationEngine(seed=2)
    e.create_simulation("Casey", "people_first", Role.COUNCILLOR, "West Belfast", "Local network")
    m = e.draw_moment()
    assert m.target_party_id == "people_first"


def test_apply_decision_changes_party_variable():
    e = SimulationEngine(seed=3)
    state = e.create_simulation("Casey", "civic_alliance", Role.MLA, "North Down", "Local network")
    m = e.draw_moment()
    option = e.get_available_options(m)[0]
    before = state.parties["civic_alliance"].variables["party_unity"]
    e.apply_decision(option.id)
    after = state.parties["civic_alliance"].variables["party_unity"]
    assert before != after


def test_role_limited_decisions_enforced():
    e = SimulationEngine(seed=4)
    e.create_simulation("Casey", "unionist_front", Role.ACTIVIST, "Lagan Valley", "Local network")
    m = e.draw_moment()
    options = e.get_available_options(m)
    assert all(Role.ACTIVIST in o.required_roles for o in options)


def test_career_eligibility_updates():
    e = SimulationEngine(seed=5)
    state = e.create_simulation("Casey", "people_first", Role.COUNCILLOR, "Fermanagh and South Tyrone", "Local network")
    state.player.reputation = 72
    state.player.influence = 67
    state.player.leader_trust = 60
    state.player.party_trust = 58
    e._update_career_opportunities()
    assert Role.MINISTER in state.player.career.opportunities
