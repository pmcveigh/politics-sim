from __future__ import annotations

from typing import Dict

from .models import (
    Actor,
    Constituency,
    Faction,
    Institution,
    InstitutionType,
    Party,
    PartyType,
    Role,
)


def create_parties() -> Dict[str, Party]:
    unionist_factions = [
        Faction("Hardline Constitutionalists", "unionist_front", 62, 70, 55),
        Faction("Pragmatic Governors", "unionist_front", 58, 65, 60),
        Faction("Social Conservatives", "unionist_front", 55, 68, 57),
        Faction("Westminster Operators", "unionist_front", 52, 60, 61),
        Faction("Local Bosses", "unionist_front", 64, 66, 48),
        Faction("Modernisers", "unionist_front", 40, 45, 50),
    ]
    republican_factions = [
        Faction("Republican Old Guard", "people_first", 60, 72, 58),
        Faction("Governing Pragmatists", "people_first", 57, 62, 65),
        Faction("Left Social Republicans", "people_first", 49, 56, 52),
        Faction("Southern Electoral Machine", "people_first", 51, 58, 66),
        Faction("Northern Community Organisers", "people_first", 63, 67, 54),
        Faction("Modernising Professionals", "people_first", 44, 52, 59),
    ]
    alliance_factions = [
        Faction("Liberal Professionals", "civic_alliance", 56, 55, 57),
        Faction("Local Government Builders", "civic_alliance", 52, 61, 62),
        Faction("Cross-Community Idealists", "civic_alliance", 58, 59, 54),
        Faction("Tactical Pragmatists", "civic_alliance", 54, 50, 63),
        Faction("Young Urban Wing", "civic_alliance", 48, 44, 46),
        Faction("Cautious Moderates", "civic_alliance", 50, 64, 60),
    ]

    return {
        "unionist_front": Party(
            id="unionist_front",
            name="Unionist Front",
            party_type=PartyType.UNIONIST,
            leader="Gareth McBride",
            factions=unionist_factions,
            variables={
                "party_unity": 58,
                "leader_authority": 63,
                "activist_morale": 55,
                "public_trust": 44,
                "media_pressure": 60,
                "scandal_risk": 45,
                "election_readiness": 50,
                "faction_pressure": 64,
                "government_credibility": 48,
                "local_machine_strength": 65,
                "unionist_credibility": 66,
                "hardline_pressure": 62,
                "moderate_leakage": 47,
                "westminster_leverage": 53,
                "executive_stability": 42,
                "business_confidence": 49,
                "constitutional_pressure": 70,
            },
        ),
        "people_first": Party(
            id="people_first",
            name="People First Movement",
            party_type=PartyType.REPUBLICAN,
            leader="Niamh O'Hare",
            factions=republican_factions,
            variables={
                "party_unity": 61,
                "leader_authority": 64,
                "activist_morale": 62,
                "public_trust": 52,
                "media_pressure": 55,
                "scandal_risk": 39,
                "election_readiness": 58,
                "faction_pressure": 53,
                "government_credibility": 50,
                "local_machine_strength": 67,
                "republican_credibility": 65,
                "unity_momentum": 57,
                "northern_machine_strength": 66,
                "southern_growth": 54,
                "dublin_viability": 49,
                "legacy_pressure": 51,
                "stormont_stability": 45,
            },
        ),
        "civic_alliance": Party(
            id="civic_alliance",
            name="Civic Alliance",
            party_type=PartyType.CROSS_COMMUNITY,
            leader="Elliot Kerr",
            factions=alliance_factions,
            variables={
                "party_unity": 60,
                "leader_authority": 54,
                "activist_morale": 59,
                "public_trust": 56,
                "media_pressure": 52,
                "scandal_risk": 30,
                "election_readiness": 55,
                "faction_pressure": 49,
                "government_credibility": 51,
                "local_machine_strength": 46,
                "cross_community_credibility": 67,
                "moderate_appeal": 63,
                "liberal_voter_energy": 58,
                "tactical_vote_pressure": 55,
                "both_sides_pressure": 62,
                "respectability": 64,
                "overextension_risk": 43,
            },
        ),
    }


def create_constituencies() -> Dict[str, Constituency]:
    return {
        "East Belfast": Constituency("East Belfast", 64, 19, 45, 50, 58, 22, 75, 44, 56, {"unionist_front": 68, "people_first": 20, "civic_alliance": 47}),
        "North Down": Constituency("North Down", 51, 14, 60, 32, 70, 28, 71, 38, 52, {"unionist_front": 49, "people_first": 16, "civic_alliance": 61}),
        "Fermanagh and South Tyrone": Constituency("Fermanagh and South Tyrone", 42, 52, 31, 57, 40, 72, 37, 50, 60, {"unionist_front": 45, "people_first": 63, "civic_alliance": 25}),
        "West Belfast": Constituency("West Belfast", 10, 74, 24, 69, 28, 18, 82, 55, 66, {"unionist_front": 9, "people_first": 72, "civic_alliance": 22}),
        "Lagan Valley": Constituency("Lagan Valley", 59, 22, 44, 46, 59, 43, 52, 47, 54, {"unionist_front": 62, "people_first": 25, "civic_alliance": 42}),
    }


def create_institutions() -> Dict[str, Institution]:
    return {
        "Local Council": Institution("Local Council", InstitutionType.LOCAL_COUNCIL, 57, 49, ["bins", "planning", "flags"]),
        "Northern Ireland Assembly": Institution("Northern Ireland Assembly", InstitutionType.ASSEMBLY, 54, 65, ["budget", "health", "schools"]),
        "Executive Department": Institution("Executive Department", InstitutionType.EXECUTIVE_DEPARTMENT, 50, 61, ["delivery", "crisis management"]),
        "Party Executive": Institution("Party Executive", InstitutionType.PARTY_EXECUTIVE, 60, 58, ["candidate lists", "discipline"]),
        "Media": Institution("Media", InstitutionType.MEDIA, 49, 63, ["scandals", "headlines"]),
        "Civil Service": Institution("Civil Service", InstitutionType.CIVIL_SERVICE, 62, 52, ["implementation", "briefings"]),
    }


def create_actors() -> Dict[str, Actor]:
    base_stats = {
        "reputation": 55,
        "competence": 60,
        "ambition": 62,
        "loyalty_to_party": 58,
        "loyalty_to_leader": 50,
        "faction_loyalty": 57,
        "media_skill": 54,
        "local_machine_strength": 53,
        "ideological_intensity": 56,
        "scandal_risk": 41,
        "stamina": 59,
        "career_momentum": 52,
        "influence": 54,
    }
    return {
        "Gareth McBride": Actor("Gareth McBride", "unionist_front", "Pragmatic Governors", Role.MLA, base_stats.copy()),
        "Niamh O'Hare": Actor("Niamh O'Hare", "people_first", "Governing Pragmatists", Role.MLA, base_stats.copy()),
        "Elliot Kerr": Actor("Elliot Kerr", "civic_alliance", "Tactical Pragmatists", Role.MLA, base_stats.copy()),
        "Aoife Nolan": Actor("Aoife Nolan", "people_first", "Northern Community Organisers", Role.COUNCILLOR, base_stats.copy()),
        "David Sterling": Actor("David Sterling", "unionist_front", "Westminster Operators", Role.ADVISER, base_stats.copy()),
        "Maya Reid": Actor("Maya Reid", "civic_alliance", "Young Urban Wing", Role.CANDIDATE, base_stats.copy()),
    }
