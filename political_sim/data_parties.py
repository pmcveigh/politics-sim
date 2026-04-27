from __future__ import annotations

from typing import Dict, List

from .models import Actor, Constituency, Faction, Institution, InstitutionType, Party, PartyType, Role


def build_parties() -> Dict[str, Party]:
    return {
        "unionist_front": Party(
            id="unionist_front",
            name="Unionist Democratic Front",
            party_type=PartyType.DUP_STYLE,
            leader_actor_id="udf_leader",
            in_government=True,
            party_unity=58,
            leader_authority=61,
            activist_morale=55,
            public_trust=43,
            media_pressure=62,
            scandal_risk=45,
            election_readiness=54,
            faction_pressure=64,
            government_credibility=47,
            local_machine_strength=68,
            custom_variables={
                "unionist_credibility": 66,
                "hardline_pressure": 64,
                "moderate_leakage": 48,
                "westminster_leverage": 57,
                "executive_stability": 42,
                "business_confidence": 49,
                "constitutional_pressure": 69,
            },
        ),
        "people_first": Party(
            id="people_first",
            name="People First Republican Movement",
            party_type=PartyType.SINN_FEIN_STYLE,
            leader_actor_id="pfr_leader",
            in_government=True,
            party_unity=62,
            leader_authority=63,
            activist_morale=64,
            public_trust=52,
            media_pressure=56,
            scandal_risk=39,
            election_readiness=57,
            faction_pressure=54,
            government_credibility=51,
            local_machine_strength=66,
            custom_variables={
                "republican_credibility": 67,
                "unity_momentum": 59,
                "northern_machine_strength": 65,
                "southern_growth": 53,
                "dublin_viability": 49,
                "legacy_pressure": 52,
                "stormont_stability": 46,
            },
        ),
        "civic_alliance": Party(
            id="civic_alliance",
            name="Civic Alliance Party",
            party_type=PartyType.ALLIANCE_STYLE,
            leader_actor_id="cap_leader",
            in_government=False,
            party_unity=59,
            leader_authority=55,
            activist_morale=58,
            public_trust=57,
            media_pressure=52,
            scandal_risk=31,
            election_readiness=56,
            faction_pressure=50,
            government_credibility=50,
            local_machine_strength=47,
            custom_variables={
                "cross_community_credibility": 67,
                "moderate_appeal": 64,
                "liberal_voter_energy": 58,
                "tactical_vote_pressure": 54,
                "both_sides_pressure": 61,
                "respectability": 63,
                "overextension_risk": 44,
            },
        ),
    }


def build_factions() -> Dict[str, Faction]:
    factions: List[Faction] = [
        Faction("udf_hardline", "Hardline Constitutionalists", "unionist_front", 64, 52, 62, ["identity", "sovereignty"], [], []),
        Faction("udf_pragmatic", "Pragmatic Governors", "unionist_front", 58, 63, 46, ["delivery", "stability"], [], []),
        Faction("udf_social", "Social Conservatives", "unionist_front", 56, 57, 55, ["social values"], [], []),
        Faction("udf_westminster", "Westminster Operators", "unionist_front", 53, 60, 44, ["uk leverage"], [], []),
        Faction("udf_local", "Local Bosses", "unionist_front", 63, 49, 59, ["branches", "selection"], [], []),
        Faction("udf_modern", "Modernisers", "unionist_front", 41, 56, 38, ["electability"], [], []),
        Faction("pfr_old_guard", "Republican Old Guard", "people_first", 61, 56, 60, ["legacy", "unity"], [], []),
        Faction("pfr_pragmatic", "Governing Pragmatists", "people_first", 58, 65, 44, ["delivery", "government"], [], []),
        Faction("pfr_left", "Left Social Republicans", "people_first", 51, 54, 57, ["housing", "workers"], [], []),
        Faction("pfr_south", "Southern Electoral Machine", "people_first", 54, 62, 40, ["southern growth"], [], []),
        Faction("pfr_north", "Northern Community Organisers", "people_first", 62, 57, 53, ["community"], [], []),
        Faction("pfr_modern", "Modernising Professionals", "people_first", 45, 61, 39, ["credibility"], [], []),
        Faction("cap_liberal", "Liberal Professionals", "civic_alliance", 57, 58, 44, ["rights", "reform"], [], []),
        Faction("cap_local", "Local Government Builders", "civic_alliance", 53, 62, 40, ["delivery", "council"], [], []),
        Faction("cap_idealists", "Cross-Community Idealists", "civic_alliance", 58, 56, 48, ["shared future"], [], []),
        Faction("cap_tactical", "Tactical Pragmatists", "civic_alliance", 55, 64, 43, ["winnability"], [], []),
        Faction("cap_young", "Young Urban Wing", "civic_alliance", 49, 48, 59, ["activism", "social media"], [], []),
        Faction("cap_cautious", "Cautious Moderates", "civic_alliance", 52, 66, 45, ["reassurance"], [], []),
    ]
    for faction in factions:
        faction.preferred_decision_types = []
        faction.disliked_decision_types = []
    return {f.id: f for f in factions}


def build_constituencies() -> Dict[str, Constituency]:
    return {
        "East Belfast": Constituency("east_belfast", "East Belfast", 64, 18, 45, 49, 60, 20, 80, 43, 55, {"unionist_front": 69, "people_first": 22, "civic_alliance": 48}, 56, "Planning dispute near city centre"),
        "North Down": Constituency("north_down", "North Down", 51, 13, 61, 33, 72, 25, 74, 39, 53, {"unionist_front": 50, "people_first": 15, "civic_alliance": 62}, 51, "Rates rise complaint"),
        "Fermanagh and South Tyrone": Constituency("fermanagh_south_tyrone", "Fermanagh and South Tyrone", 42, 53, 31, 58, 39, 74, 35, 50, 60, {"unionist_front": 45, "people_first": 64, "civic_alliance": 24}, 48, "Rural health transport row"),
        "West Belfast": Constituency("west_belfast", "West Belfast", 11, 75, 24, 68, 27, 19, 83, 56, 67, {"unionist_front": 8, "people_first": 73, "civic_alliance": 23}, 58, "Housing waiting list anger"),
        "Lagan Valley": Constituency("lagan_valley", "Lagan Valley", 58, 23, 45, 45, 58, 45, 51, 47, 54, {"unionist_front": 63, "people_first": 24, "civic_alliance": 43}, 49, "School places pressure"),
    }


def build_institutions() -> Dict[str, Institution]:
    return {
        "local_council": Institution("local_council", "Local Council", InstitutionType.LOCAL_COUNCIL, 58, 50, ["planning", "waste", "flags"]),
        "assembly": Institution("assembly", "Northern Ireland Assembly", InstitutionType.ASSEMBLY, 54, 66, ["questions", "votes", "committees"]),
        "executive_department": Institution("executive_department", "Executive Department", InstitutionType.EXECUTIVE_DEPARTMENT, 50, 62, ["service delivery", "crises"]),
        "party_executive": Institution("party_executive", "Party Executive", InstitutionType.PARTY_EXECUTIVE, 61, 59, ["discipline", "selection"]),
        "media": Institution("media", "Media", InstitutionType.MEDIA, 49, 64, ["headlines", "briefings"]),
        "civil_service": Institution("civil_service", "Civil Service", InstitutionType.CIVIL_SERVICE, 63, 53, ["advice", "implementation"]),
    }


def _actor(actor_id: str, name: str, role: Role, party_id: str, constituency: str, faction_id: str, rep: int, comp: int, amb: int, media: int, local: int) -> Actor:
    return Actor(
        id=actor_id,
        name=name,
        role=role,
        party_id=party_id,
        constituency_id=constituency,
        faction_id=faction_id,
        reputation=rep,
        competence=comp,
        ambition=amb,
        loyalty_to_party=58,
        loyalty_to_leader=54,
        faction_loyalty=56,
        media_skill=media,
        local_machine_strength=local,
        ideological_intensity=57,
        scandal_risk=39,
        stamina=65,
        career_momentum=52,
        influence=0,
    )


def build_actors() -> Dict[str, Actor]:
    actors = [
        _actor("udf_leader", "Calum Boyd", Role.MLA, "unionist_front", "East Belfast", "udf_pragmatic", 66, 61, 58, 62, 60),
        _actor("udf_senior_min", "Fiona McKeown", Role.MINISTER, "unionist_front", "Lagan Valley", "udf_pragmatic", 63, 65, 60, 55, 58),
        _actor("udf_mla", "Ronan Kells", Role.MLA, "unionist_front", "North Down", "udf_hardline", 57, 56, 67, 60, 51),
        _actor("udf_councillor", "Iain Donnelly", Role.COUNCILLOR, "unionist_front", "East Belfast", "udf_local", 55, 54, 64, 47, 68),
        _actor("udf_adviser", "Martha Kerrigan", Role.ADVISER, "unionist_front", "Lagan Valley", "udf_westminster", 52, 62, 63, 66, 44),
        _actor("udf_officer", "Declan Beattie", Role.CANDIDATE, "unionist_front", "East Belfast", "udf_local", 50, 51, 59, 45, 64),
        _actor("udf_rival", "Graham Taggart", Role.CANDIDATE, "unionist_front", "North Down", "udf_hardline", 54, 52, 72, 59, 57),
        _actor("pfr_leader", "Siobhán Devlin", Role.MLA, "people_first", "West Belfast", "pfr_pragmatic", 67, 62, 59, 61, 62),
        _actor("pfr_senior_min", "Pádraig Mullan", Role.MINISTER, "people_first", "Fermanagh and South Tyrone", "pfr_pragmatic", 64, 64, 57, 54, 61),
        _actor("pfr_mla", "Eoin Lavery", Role.MLA, "people_first", "West Belfast", "pfr_old_guard", 59, 57, 66, 53, 55),
        _actor("pfr_councillor", "Máire Keenan", Role.COUNCILLOR, "people_first", "Fermanagh and South Tyrone", "pfr_north", 56, 55, 63, 49, 66),
        _actor("pfr_adviser", "Aisling Carney", Role.ADVISER, "people_first", "West Belfast", "pfr_south", 53, 63, 61, 67, 46),
        _actor("pfr_officer", "Conor McIlroy", Role.CANDIDATE, "people_first", "West Belfast", "pfr_north", 51, 53, 60, 48, 63),
        _actor("pfr_rival", "Orla Fitzsimons", Role.CANDIDATE, "people_first", "Fermanagh and South Tyrone", "pfr_left", 55, 54, 71, 58, 56),
        _actor("cap_leader", "Naomi Calder", Role.MLA, "civic_alliance", "North Down", "cap_tactical", 65, 63, 56, 64, 52),
        _actor("cap_senior_min", "Ryan Whitla", Role.JUNIOR_MINISTER, "civic_alliance", "East Belfast", "cap_local", 60, 61, 58, 58, 54),
        _actor("cap_mla", "Grace Healy", Role.MLA, "civic_alliance", "Lagan Valley", "cap_idealists", 58, 58, 62, 61, 49),
        _actor("cap_councillor", "Peter Lennox", Role.COUNCILLOR, "civic_alliance", "North Down", "cap_local", 57, 56, 63, 52, 60),
        _actor("cap_adviser", "Leah McNabb", Role.ADVISER, "civic_alliance", "East Belfast", "cap_liberal", 54, 62, 65, 69, 40),
        _actor("cap_officer", "Niall Dunbar", Role.CANDIDATE, "civic_alliance", "Lagan Valley", "cap_cautious", 52, 55, 59, 50, 57),
        _actor("cap_rival", "Bethany Crozier", Role.CANDIDATE, "civic_alliance", "North Down", "cap_young", 55, 54, 73, 65, 48),
    ]
    return {a.id: a for a in actors}
