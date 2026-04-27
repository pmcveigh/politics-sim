from __future__ import annotations

from dataclasses import replace
from typing import Dict, List

from .models import (
    Actor,
    Constituency,
    Decision,
    DecisionType,
    Faction,
    HandlingStyle,
    Institution,
    InstitutionType,
    Party,
    PartyType,
    Relationship,
    Role,
    RoutineCategory,
    TimeSlot,
    Urgency,
)


def build_parties() -> Dict[str, Party]:
    return {
        "cap": Party("cap", "Civic Alliance Party", PartyType.CROSS_COMMUNITY),
        "udp": Party("udp", "Union Democratic Party", PartyType.UNIONIST),
    }


def build_factions() -> Dict[str, Faction]:
    return {
        "cap_local": Faction("cap_local", "cap", "Local Government Builders", 55),
        "cap_tactical": Faction("cap_tactical", "cap", "Tactical Pragmatists", 50),
    }


def build_actors() -> Dict[str, Actor]:
    return {
        "main_rival": Actor("main_rival", "Jordan Keenan", Role.COUNCILLOR, "udp"),
        "party_leader": Actor("party_leader", "Riley Porter", Role.MLA, "cap"),
        "council_officer": Actor("council_officer", "Sam O'Neill", Role.COUNCILLOR, "cap"),
        "journalist": Actor("journalist", "Aisling Ward", Role.COUNCILLOR, "cap"),
    }


def build_constituencies() -> Dict[str, Constituency]:
    return {
        "north_down": Constituency(
            id="north_down",
            name="North Down",
            local_issue_pressure=52,
            local_media_heat=46,
            turnout_energy=50,
            working_class_pressure=42,
            middle_class_pressure=62,
            rural_pressure=28,
            urban_pressure=70,
            current_flashpoint="School parking and town centre decline",
            resident_satisfaction=49,
            council_service_pressure=54,
            party_machine_strength={"cap": 58, "udp": 51},
        )
    }


def build_institutions() -> Dict[str, Institution]:
    return {
        "council": Institution("council", "Borough Council", InstitutionType.LOCAL_COUNCIL),
        "party_group": Institution("party_group", "Party Group", InstitutionType.PARTY),
        "media": Institution("media", "Local Press", InstitutionType.MEDIA),
    }


def build_relationships() -> Dict[str, Relationship]:
    return {
        "local_branch": Relationship("local_branch", "Local Branch", 52),
        "party_group": Relationship("party_group", "Party Group", 51),
        "party_leader": Relationship("party_leader", "Party Leader", 50),
        "key_faction": Relationship("key_faction", "Key Faction", 49),
        "council_officers": Relationship("council_officers", "Council Officers", 47),
        "local_journalist": Relationship("local_journalist", "Local Journalist", 50),
        "residents_association": Relationship("residents_association", "Residents’ Association", 53),
        "business_group": Relationship("business_group", "Business Group", 49),
        "community_group": Relationship("community_group", "Community Group", 52),
        "main_rival": Relationship("main_rival", "Main Rival Councillor", 38),
    }


def _d(
    id_: str,
    label: str,
    style: HandlingStyle,
    effects: Dict[str, int],
    relationship_effects: Dict[str, int],
    stamina_cost: int,
    is_minor: bool,
    text: str,
) -> Decision:
    return Decision(
        id=id_,
        label=label,
        decision_type=DecisionType.HANDLE,
        handling_style=style,
        allowed_roles=[Role.COUNCILLOR, Role.CANDIDATE, Role.MLA],
        stamina_cost=stamina_cost,
        is_minor=is_minor,
        effects=effects,
        relationship_effects=relationship_effects,
        result_text=text,
    )


def routine_templates() -> List[dict]:
    return [
        {
            "id": "casework_school_parking",
            "title": "School parking complaints",
            "description": "Residents report daily chaos near the primary school.",
            "category": RoutineCategory.CASEWORK,
            "decisions": [
                _d("forward_officer", "Forward quietly to officers", HandlingStyle.QUIET_ADMIN, {"player.casework_backlog": -1, "player.officer_relationship": 1, "player.resident_trust": 1}, {"council_officers": 1}, 3, True, "Officers receive a structured request."),
                _d("visit_site", "Visit site personally", HandlingStyle.PERSONAL_WARD_WORK, {"player.casework_backlog": -1, "player.resident_trust": 3, "player.ward_visibility": 2}, {"residents_association": 2}, 8, False, "Parents appreciate you showing up in person."),
                _d("public_post", "Post publicly demanding action", HandlingStyle.PUBLIC_CAMPAIGNING, {"player.local_media_profile": 2, "player.social_media_volatility": 3, "constituency.local_media_heat": 2}, {"council_officers": -2}, 5, True, "The post gains attention but draws hostile replies."),
                _d("honest_limits", "Tell residents legal limits", HandlingStyle.HONEST_REFUSAL, {"player.committee_credibility": 2, "player.resident_trust": -1}, {"council_officers": 1}, 4, True, "Some residents dislike the answer, but officers trust your honesty."),
            ],
            "ignored": {"player.resident_trust": -2, "player.casework_backlog": 1, "player.rival_threat": 2, "constituency.local_issue_pressure": 2},
            "escalation": "Angry parent posts that you ignored school parking chaos.",
        },
        {
            "id": "officer_followup_bins",
            "title": "Officer follow-up on missed bin collections",
            "description": "Service managers await your response to a ward-wide complaint thread.",
            "category": RoutineCategory.OFFICER_FOLLOW_UP,
            "decisions": [
                _d("polite_chase", "Polite chase and update residents", HandlingStyle.QUIET_ADMIN, {"player.casework_backlog": -1, "player.officer_relationship": 2, "player.resident_trust": 1}, {"council_officers": 2}, 3, True, "Officer response is faster because of your working relationship."),
                _d("formal_complaint", "File formal complaint", HandlingStyle.PARTY_ESCALATION, {"player.resident_trust": 2, "player.officer_relationship": -2, "constituency.council_service_pressure": -1}, {"council_officers": -2}, 6, False, "Service managers escalate the issue but resent the approach."),
            ],
            "ignored": {"player.casework_backlog": 1, "player.resident_trust": -1, "player.rival_threat": 1},
            "escalation": "Rival posts photos of uncollected bins before your update goes out.",
        },
        {
            "id": "committee_vote_rates",
            "title": "Committee vote on town-centre rates",
            "description": "A paper contains bad news for small businesses.",
            "category": RoutineCategory.COMMITTEE_WORK,
            "decisions": [
                _d("follow_line", "Follow party group line", HandlingStyle.PARTY_ESCALATION, {"player.party_group_trust": 2, "player.resident_trust": -1}, {"party_group": 2}, 5, False, "Party group appreciates discipline, local traders do not."),
                _d("speak_local", "Speak for local concern", HandlingStyle.PERSONAL_WARD_WORK, {"player.resident_trust": 2, "player.party_group_trust": -2, "player.committee_credibility": 1}, {"party_group": -2}, 6, False, "You win local praise but irritate group managers."),
                _d("compromise", "Propose compromise amendment", HandlingStyle.CROSS_PARTY_DEAL, {"player.committee_credibility": 3, "player.influence": -1}, {"party_group": 1, "business_group": 1}, 7, False, "Your amendment partially passes after negotiation."),
            ],
            "ignored": {"player.committee_credibility": -2, "player.rival_threat": 1},
            "escalation": "A hostile paper says you were missing when traders needed representation.",
        },
        {
            "id": "media_quote",
            "title": "Local paper asks for quote",
            "description": "Reporter asks about town centre decline.",
            "category": RoutineCategory.LOCAL_MEDIA,
            "decisions": [
                _d("dry_update", "Dry factual update", HandlingStyle.QUIET_ADMIN, {"player.local_media_profile": 1}, {"local_journalist": 1}, 2, True, "The quote is reported fairly and without drama."),
                _d("campaigning_quote", "Strong campaigning line", HandlingStyle.MEDIA_PLAY, {"player.local_media_profile": 3, "player.social_media_volatility": 2}, {"local_journalist": -1}, 4, True, "Headline coverage rises, but tone is sharper."),
            ],
            "ignored": {"player.local_media_profile": -1, "player.rival_threat": 1},
            "escalation": "Your rival fills the media gap and claims local leadership.",
        },
        {
            "id": "residents_association_meeting",
            "title": "Residents’ association meeting",
            "description": "Association wants progress updates and realistic timelines.",
            "category": RoutineCategory.COMMUNITY_EVENT,
            "decisions": [
                _d("attend_visible", "Attend visibly", HandlingStyle.PERSONAL_WARD_WORK, {"player.ward_visibility": 3, "player.stamina": -2}, {"residents_association": 1}, 8, False, "You are seen putting in the hours."),
                _d("attend_listen", "Attend quietly and listen", HandlingStyle.QUIET_ADMIN, {"player.resident_trust": 2, "player.ward_visibility": 1}, {"residents_association": 2}, 6, False, "Residents feel listened to even without headline promises."),
                _d("send_apology", "Send apology and update", HandlingStyle.HONEST_REFUSAL, {"player.stamina": 2, "player.resident_trust": -1}, {"residents_association": -1}, 1, True, "Attendance drops your visibility this evening."),
            ],
            "ignored": {"player.resident_trust": -2, "player.rival_threat": 2, "player.casework_backlog": 1},
            "escalation": "Residents publicly thank your rival for attending when you did not.",
        },
    ]


def clone_decisions(decisions: List[Decision]) -> List[Decision]:
    return [replace(d) for d in decisions]
