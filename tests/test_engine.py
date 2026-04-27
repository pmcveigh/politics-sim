from political_sim.engine import SimulationEngine
from political_sim.models import Role, TimeSlot


def test_create_simulation_sets_start_date_and_agenda():
    e = SimulationEngine(seed=1)
    state = e.create_simulation("Casey", "unionist_front", Role.ACTIVIST, "East Belfast", "Local network")
    assert state.game_date.day == 1
    assert state.game_date.month == 5
    assert state.game_date.year == 2027
    assert state.game_date.time_slot == TimeSlot.MORNING
    assert 1 <= len(state.daily_agenda.moments) <= 3


def test_daily_agenda_moments_are_role_limited():
    e = SimulationEngine(seed=2)
    state = e.create_simulation("Casey", "people_first", Role.COUNCILLOR, "West Belfast", "Local network")
    assert all(Role.COUNCILLOR in m.eligible_roles for m in state.daily_agenda.moments)


def test_apply_decision_changes_party_variable_and_stamina():
    e = SimulationEngine(seed=3)
    state = e.create_simulation("Casey", "civic_alliance", Role.MLA, "North Down", "Local network")
    moment = state.daily_agenda.moments[0]
    option = e.get_available_options(moment)[0]
    before_unity = state.parties["civic_alliance"].variables["party_unity"]
    before_stamina = state.player.stamina
    e.apply_decision(moment.id, option.id)
    assert state.parties["civic_alliance"].variables["party_unity"] != before_unity
    assert state.player.stamina < before_stamina


def test_advance_time_slot_moves_at_most_one_day():
    e = SimulationEngine(seed=4)
    state = e.create_simulation("Casey", "unionist_front", Role.ACTIVIST, "Lagan Valley", "Local network")
    day_before = state.day_index
    for _ in range(4):
        e.advance_time_slot()
    assert state.day_index in [day_before, day_before + 1]


def test_ignore_moment_removes_from_agenda():
    e = SimulationEngine(seed=5)
    state = e.create_simulation("Casey", "people_first", Role.COUNCILLOR, "Fermanagh and South Tyrone", "Local network")
    moment = state.daily_agenda.moments[0]
    e.ignore_moment(moment.id)
    assert all(m.id != moment.id for m in state.daily_agenda.moments)
